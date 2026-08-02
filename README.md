# vulnbench

Benchmark harness for LLM-driven SAST/pentest tooling against OSS vulnerability
ground truth. Builds a SQLite datasource of labeled vulnerabilities, loads
benchmark question suites, and scores a harness's findings with the Sola
four-stage evaluation (expert-proxy `{0, 0.5, 1}` + LLM-as-judge metrics from
two judges, MIN-aggregated).

See [CLAUDE.md](CLAUDE.md) for the invariants the build must preserve and
[Scheduling](#scheduling) for the nightly cron entrypoint.

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install pyyaml checkov anthropic

.venv/bin/python ingest/build_datasource.py    # build data/vulnbench.db
.venv/bin/python questions/loader.py           # load question suites
.venv/bin/python bench/run_benchmark.py \
    --findings data/mantis_findings.sample.jsonl \
    --harness mantis --run-id verify \
    --gt-source secllmholmes-handcrafted       # score a findings file
```

Findings input uses Mantis's `historical_learnings.jsonl` schema:
`{revision_id, title, description, code_paths: ["file:line"], vuln_type,
mitigation_diff, cve}`. Point the runner at real Mantis output with
`--findings /path/to/historical_learnings.jsonl`.

---

## Verified test results

All numbers below are from actual runs in this environment
(2026-08-02, Python 3.11.15, Checkov 3.3.9, offline heuristic judges).

### 1. Ground-truth datasource build

`python ingest/build_datasource.py --only secllmholmes terragoat`

```
ground_truth rows by source:
  secllmholmes-handcrafted        48
  secllmholmes-realworld          30
  terragoat                      474
  TOTAL                          552
```

Meets the ~552-row acceptance target exactly: 48 hand-crafted per-CWE samples
(8 CWEs x 6 files, `N.ext` vulnerable / `p_N.ext` safe), 30 real-world rows
(15 CVEs x vuln/patch pair), and 474 TerraGoat misconfigurations from the
Checkov oracle.

### 2. Question suites

`python questions/loader.py`

```
[sola_ispm] WARNING: loaded 0 questions, expected 77. Paste the paper's Appendix A questions into sola_ispm.json (verbatim).
[sola_crossvendor] WARNING: loaded 0 questions, expected 50. Paste the paper's Appendix A questions into sola_crossvendor.json (verbatim).

questions by suite:
  code_vuln              78
  TOTAL                  78
```

The 78 code-vuln-detection questions are derived from the SecLLMHolmes rows
(one per ground-truth row, with `ground_truth_ref`). The two Sola suites are
**pending**: arXiv is unreachable from this environment and the loader refuses
to fabricate question text, so `questions/sola_ispm.json` (77 expected:
Inventory 14, AWS Hygiene 39, GWS Hygiene 14, Okta Hygiene 10) and
`questions/sola_crossvendor.json` (50 expected) are paste-ready templates.
Total reaches 205 once the appendix text is pasted in verbatim.

### 3. Mantis scoring harness — verification run

`python bench/run_benchmark.py --findings data/mantis_findings.sample.jsonl
--harness mantis --run-id verify --gt-source secllmholmes-handcrafted`

The sample findings file contains 24 findings over the SecLLMHolmes
hand-crafted set with three deliberately planted errors (one missed CWE-22
file, one CWE-476 file labeled with the wrong CWE, one false positive on a
patched CWE-89 file), so the report has a known fingerprint:

```
=== vulnbench report  run=verify  harness=mantis  gt-source=secllmholmes-handcrafted ===
ground-truth rows scored : 48
findings ingested        : 24
Expert Accuracy          : 0.9479
Success Rate (full credit): 0.9375
Hallucination-free (judged pairs): 0.9271

by-CWE:
  CWE              n vuln_recall expert_acc  notes
  CWE-190          6        1.00       1.00
  CWE-22           6        0.67       0.83  miss
  CWE-416          6        1.00       1.00
  CWE-476          6        1.00       0.92  tp_wrong_cwe
  CWE-77           6        1.00       1.00
  CWE-787          6        1.00       1.00
  CWE-79           6        1.00       1.00
  CWE-89           6        1.00       0.83  false_positive

mean judge metrics (two judges, MIN-aggregated):
  faithfulness         0.9375
  hallucination_free   0.9271
  correctness          0.9375
  retrieval_use        0.9688
  example_adapt        1.0000
  judge mode: offline-heuristic
```

Acceptance checklist (all pass):

| Check                                        | Expected | Observed |
|----------------------------------------------|----------|----------|
| Expert Accuracy                              | ~0.95    | 0.9479   |
| Planted miss visible (CWE-22 recall)         | 0.67     | 0.67     |
| Planted wrong-CWE visible (CWE-476 acc)      | ~0.92    | 0.92     |
| Planted false positive visible (CWE-89 acc)  | ~0.83    | 0.83     |

Several sample findings intentionally use short `CWE-89/2.py`-style paths, so
this run also proves the path matcher resolves the unique parent-dir+filename
tail rather than regressing to bare basenames (which collide across CWE dirs).

Additional checks performed:

- **Idempotent rerun**: repeating the same `--run-id verify` command returns
  identical results and leaves exactly 48 score rows / 24 finding rows for the
  run (rows are replaced, not duplicated).
- **Regression gate**: the same run with `--min-acc 0.99` exits non-zero with
  `REGRESSION: Expert Accuracy 0.9479 < threshold 0.99`; with `--min-acc 0.80`
  it exits 0.
- **Full-scope run** (`--run-id verify-all`, no `--gt-source`): scores all 552
  ground-truth rows (Expert Accuracy 0.1096, as expected — the sample findings
  only cover the hand-crafted subset).

### 4. Nightly wrapper — end-to-end run

`bash scripts/run_vulnbench.sh` (exit code 0), logged to
`logs/vulnbench-2026-08-02.log`:

```
=== vulnbench run 2026-08-02T14:49:11+00:00 ===
ground_truth rows by source:
  secllmholmes-handcrafted        48
  secllmholmes-realworld          30
  terragoat                      474
  TOTAL                          552
questions by suite:
  code_vuln              78
  TOTAL                  78

=== vulnbench report  run=nightly-2026-08-02  harness=mantis  gt-source=secllmholmes-handcrafted ===
ground-truth rows scored : 48
findings ingested        : 24
Expert Accuracy          : 0.9479
Success Rate (full credit): 0.9375
Hallucination-free (judged pairs): 0.9271
=== vulnbench run OK 2026-08-02T14:49:47+00:00 ===
```

The wrapper refreshes ground truth, re-derives questions, scores
`${FINDINGS:-data/mantis_findings.sample.jsonl}` under `nightly-$(date +%F)`,
and fails loudly (non-zero exit) if Expert Accuracy drops below
`${MIN_ACC:-0.80}`.

---

## Scheduling

```bash
make schedule-show   # prints the crontab line for review
make schedule        # installs it idempotently (keeps other crontab entries)
make unschedule      # removes it
```

Crontab line installed by `make schedule`:

```
0 6 * * * /usr/bin/env bash /home/user/Cyber-harness-eval/scripts/run_vulnbench.sh
```

Point the nightly run at real Mantis output via environment variables:

```bash
FINDINGS=/path/to/historical_learnings.jsonl MIN_ACC=0.85 bash scripts/run_vulnbench.sh
```

## Layout

```
ingest/    sources.yaml registry + build_datasource.py (SecLLMHolmes parser,
           Checkov IaC oracle; CloudGoat/AWSGoat/IAM-Vulnerable/GOAD/NYU-CTF/
           Cybench registered as deploy-gated stubs)
questions/ loader.py + Sola suite JSON (verbatim question text only)
bench/     schema.sql, score.py (CWE lexicon, tail matcher, expert proxy,
           MIN-aggregated judges), run_benchmark.py (report + regression gate)
data/      mantis_findings.sample.jsonl (committed), vulnbench.db (gitignored)
scripts/   run_vulnbench.sh — cron entrypoint
```
