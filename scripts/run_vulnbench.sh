#!/usr/bin/env bash
# vulnbench nightly runner — cron entrypoint.
#   FINDINGS=/path/to/historical_learnings.jsonl  findings file to score
#   MIN_ACC=0.80                                  regression threshold
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

mkdir -p logs
LOG="logs/vulnbench-$(date +%F).log"
exec >>"$LOG" 2>&1

echo "=== vulnbench run $(date -Is) ==="

# shellcheck disable=SC1091
source .venv/bin/activate

# refresh ground truth (re-clones missing repos, re-runs the checkov oracle)
python ingest/build_datasource.py --only secllmholmes terragoat

# reload question suites: the refresh replaces ground-truth rows, so the
# derived code_vuln questions must be re-derived (idempotent, also covers a
# missing/fresh DB)
python questions/loader.py

FINDINGS="${FINDINGS:-data/mantis_findings.sample.jsonl}"
MIN_ACC="${MIN_ACC:-0.80}"

# --min-acc makes the run exit non-zero on a regression, so cron fails loudly
python bench/run_benchmark.py \
    --findings "$FINDINGS" \
    --harness mantis \
    --run-id "nightly-$(date +%F)" \
    --gt-source secllmholmes-handcrafted \
    --min-acc "$MIN_ACC"

echo "=== vulnbench run OK $(date -Is) ==="
