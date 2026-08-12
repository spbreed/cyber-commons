#!/usr/bin/env bash
# vulnbench — single entrypoint used by the agent skills (Claude Code, Copilot,
# and any AGENTS.md-aware agent) and by humans. Thin wrapper over the Python
# tools so every surface runs the exact same thing.
#
# Usage:
#   scripts/vulnbench.sh doctor                     # check prerequisites
#   scripts/vulnbench.sh setup                      # create .venv + install deps
#   scripts/vulnbench.sh build                      # build datasource + load questions
#   scripts/vulnbench.sh score --findings <f.jsonl> [--gt-source <s>] [--min-acc <t>] [passthrough flags]
#   scripts/vulnbench.sh verify                     # regression fingerprint (expects 0.9479)
#   scripts/vulnbench.sh compare                    # model comparison scorers (code + IaC)
#   scripts/vulnbench.sh all --findings <f.jsonl>   # build + score in one go
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"
VENV="$REPO_DIR/.venv"
PY="$VENV/bin/python"
DEPS="pyyaml checkov anthropic jsonschema"

log() { printf '\033[1;36m[vulnbench]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[vulnbench] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

need_venv() { [ -x "$PY" ] || die "no .venv — run: scripts/vulnbench.sh setup"; }

cmd_doctor() {
  local ok=0
  for b in git python3; do
    if command -v "$b" >/dev/null 2>&1; then log "found $b: $($b --version 2>&1 | head -1)"; else log "MISSING $b"; ok=1; fi
  done
  if [ -x "$VENV/bin/checkov" ]; then log "found checkov (venv): $("$VENV/bin/checkov" --version 2>&1 | head -1)";
  elif command -v checkov >/dev/null 2>&1; then log "found checkov: $(checkov --version 2>&1 | head -1)";
  else log "checkov not installed (run setup; IaC oracle will be skipped without it)"; fi
  if [ -x "$PY" ]; then log "venv present: $("$PY" --version)"; else log "venv missing (run setup)"; fi
  [ -f data/vulnbench.db ] && log "datasource present: data/vulnbench.db" || log "datasource NOT built (run build)"
  return $ok
}

cmd_setup() {
  [ -x "$PY" ] || { log "creating .venv"; python3 -m venv "$VENV"; }
  log "installing deps: $DEPS"
  "$VENV/bin/pip" install -q --upgrade pip >/dev/null 2>&1 || true
  "$VENV/bin/pip" install -q $DEPS
  log "setup complete"
}

cmd_build() {
  need_venv
  log "building ground-truth datasource (clones repos on first run)"
  "$PY" ingest/build_datasource.py --only secllmholmes terragoat
  log "loading question suites"
  "$PY" questions/loader.py
}

cmd_score() {
  need_venv
  [ -f data/vulnbench.db ] || die "datasource missing — run: scripts/vulnbench.sh build"
  [ "$#" -ge 1 ] || die "score needs --findings <file.jsonl> [flags]"
  log "scoring findings"
  "$PY" bench/run_benchmark.py "$@"
}

cmd_verify() {
  need_venv
  [ -f data/vulnbench.db ] || cmd_build
  log "regression fingerprint (expect Expert Accuracy 0.9479)"
  "$PY" bench/run_benchmark.py \
    --findings data/mantis_findings.sample.jsonl \
    --harness mantis --run-id verify \
    --gt-source secllmholmes-handcrafted --min-acc 0.80
}

cmd_compare() {
  need_venv
  log "code model comparison"
  "$PY" work_mantis/compare_models.py || true
  log "IaC model comparison"
  "$PY" work_mantis/compare_iac.py || true
}

cmd_all() {
  cmd_build
  cmd_score "$@"
}

# --- CyberGym / ExploitGym / CyberGym-E2E (execution-based, Docker + task data) ---

cmd_cybergym_preflight() {
  # Honest capability check. CyberGym RUNS PoCs in Docker against per-task
  # vulnerable/patched build images; it needs the daemon, Python>=3.12, big disk,
  # and network to HuggingFace (task data) + the image registry. Reports what's
  # missing instead of pretending.
  local cap=0
  log "CyberGym preflight — checking whether this host can RUN the benchmark"
  if command -v docker >/dev/null 2>&1 && timeout 20 docker info >/dev/null 2>&1; then
    log "  [ok]   docker daemon up ($(docker --version))"
  else log "  [MISS] docker daemon not usable"; cap=1; fi
  local pyv; pyv="$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null || echo 0.0)"
  if python3 -c 'import sys;sys.exit(0 if sys.version_info>=(3,12) else 1)' 2>/dev/null; then
    log "  [ok]   python $pyv (cybergym needs >=3.12)"
  else log "  [MISS] python $pyv < 3.12 — cybergym package won't install"; cap=1; fi
  local free_gb; free_gb="$(df -PBG . | awk 'NR==2{gsub("G","",$4);print $4}')"
  if [ "${free_gb:-0}" -ge 150 ]; then log "  [ok]   disk free ${free_gb}G (need ~130G+)";
  else log "  [MISS] disk free ${free_gb}G < ~130G needed for task data/images"; cap=1; fi
  if curl -sS -m 15 -o /dev/null -w '%{http_code}' https://huggingface.co/datasets 2>/dev/null | grep -qE '^[23]'; then
    log "  [ok]   huggingface.co reachable (task data source)"
  else log "  [MISS] huggingface.co unreachable — cannot download the 240GB task data"; cap=1; fi
  if timeout 30 docker pull --quiet hello-world >/dev/null 2>&1; then
    log "  [ok]   docker registry reachable (can pull runner images)"; docker rmi hello-world >/dev/null 2>&1 || true
  else log "  [MISS] docker registry unreachable — cannot pull OSS-Fuzz runner images"; cap=1; fi
  echo
  if [ "$cap" -eq 0 ]; then
    log "RESULT: this host CAN run CyberGym. Next: clone github.com/sunblaze-ucb/cybergym,"
    log "        download task data, start the server, run an agent, then:"
    log "        scripts/vulnbench.sh cybergym-score --results <verify.jsonl> --benchmark cybergym"
  else
    log "RESULT: this host CANNOT run the real CyberGym execution benchmark (see [MISS] above)."
    log "        The scoring ADAPTER still works on results produced elsewhere:"
    log "        scripts/vulnbench.sh cybergym-score --results <verify.jsonl> --benchmark cybergym"
  fi
  return $cap
}

cmd_cybergym_score() {
  need_venv
  [ "$#" -ge 1 ] || die "cybergym-score needs --results <verify.jsonl> [--benchmark cybergym|exploitgym|cybergym-e2e]"
  log "scoring CyberGym-family results via the adapter"
  "$PY" bench/cybergym_adapter.py "$@"
}

main() {
  local sub="${1:-doctor}"; shift || true
  case "$sub" in
    doctor)  cmd_doctor "$@" ;;
    setup)   cmd_setup "$@" ;;
    build)   cmd_build "$@" ;;
    score)   cmd_score "$@" ;;
    verify)  cmd_verify "$@" ;;
    compare) cmd_compare "$@" ;;
    all)     cmd_all "$@" ;;
    cybergym-preflight) cmd_cybergym_preflight "$@" ;;
    cybergym-score)     cmd_cybergym_score "$@" ;;
    -h|--help|help) sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' ;;
    *) die "unknown command '$sub' (try: doctor setup build score verify compare all)" ;;
  esac
}
main "$@"
