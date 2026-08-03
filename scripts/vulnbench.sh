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
    -h|--help|help) sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' ;;
    *) die "unknown command '$sub' (try: doctor setup build score verify compare all)" ;;
  esac
}
main "$@"
