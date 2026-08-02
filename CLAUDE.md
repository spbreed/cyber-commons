# vulnbench

Benchmark harness for LLM-driven SAST/pentest tooling against OSS vulnerability
ground truth.

## Purpose

Build a SQLite datasource of vulnerability ground truth, load benchmark
question sets, and score a harness's findings using the Sola four-stage
evaluation: expert-proxy scoring ({0, 0.5, 1}) plus LLM-as-judge metrics
(faithfulness, hallucination_free, correctness, retrieval_use, example_adapt)
from two judges with MIN aggregation.

## Ground-truth sources

- **SecLLMHolmes** (ai4cloudops/SecLLMHolmes): labeled code vulnerabilities —
  hand-crafted per-CWE samples (`N.ext` = vulnerable, `p_N.ext` = safe, with
  rationale text under `ground-truth/`) and real-world CVEs
  (`vuln.*`/`patch.*` pairs plus `cve_details.json`).
- **TerraGoat** (bridgecrewio/terragoat) scanned with **Checkov** as an IaC
  misconfiguration oracle: every failed check becomes a vulnerable row.
- Extensible via `ingest/sources.yaml` — CloudGoat, AWSGoat, IAM-Vulnerable,
  GOAD, NYU-CTF and Cybench are registered as deploy-gated stubs.

## Invariants the build must preserve

- **File-path matching between findings and ground truth must use the
  parent-dir + filename tail, NOT the bare basename.** SecLLMHolmes reuses
  filenames like `3.c` / `p_1.py` across CWE directories, so basename-only
  matching silently mis-scores. Exact path match first; otherwise the tail
  (`CWE-89/1.py`) is used only when it is unique across the ground truth in
  scope (ambiguous tails are refused).
- Question text for the Sola suites is loaded verbatim from
  `questions/sola_ispm.json` / `questions/sola_crossvendor.json` — never
  invented. The loader warns until the expected counts (77 / 50) are met.
- Reruns are idempotent per (run_id, harness): findings and scores for the
  run are replaced, and ground-truth rows are replaced per source.

## Commands

```bash
python ingest/build_datasource.py            # build data/vulnbench.db (~552 rows)
python questions/loader.py                   # load question suites (77+50+78 = 205)
python bench/run_benchmark.py --findings <jsonl>   # score a findings file
```

Useful flags for `run_benchmark.py`: `--gt-source <source>` to scope scoring,
`--run-id <id>` for named (idempotent) runs, `--judges` to use real Anthropic
judges (needs `ANTHROPIC_API_KEY`; a deterministic offline heuristic is used
otherwise), `--min-acc <t>` to exit non-zero on a regression.

Findings input uses Mantis's `historical_learnings.jsonl` schema:
`{revision_id, title, description, code_paths: ["file:line"], vuln_type,
mitigation_diff, cve}`.

## Environment

Local venv at `.venv/` with `pyyaml`, `checkov`, `anthropic` installed
(`python3 -m venv .venv && .venv/bin/pip install pyyaml checkov anthropic`).
Cloned ground-truth repos live in `_repos/` (gitignored), the database in
`data/vulnbench.db` (gitignored).

## Scheduling

`scripts/run_vulnbench.sh` is the cron entrypoint (refreshes ground truth,
runs the benchmark, fails loudly below `MIN_ACC`, logs to `logs/`).
`make schedule` prints/installs the crontab line idempotently — review before
installing. Point it at real Mantis output with
`FINDINGS=/path/to/historical_learnings.jsonl`.
