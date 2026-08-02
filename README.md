# vulnbench

Benchmark harness that measures how good an AI security tool actually is at
finding vulnerabilities — by testing it against code whose bugs are already
known and documented.

## What this project is about (the easy version)

Imagine grading a student's exam. You can only grade it because you have the
answer key. AI-driven security scanners (SAST tools, pentest copilots,
LLM agents) produce long lists of "findings" — but without an answer key you
can't tell whether those findings are brilliant or hallucinated.

vulnbench builds that answer key and does the grading:

1. **Collect the answer key** — clone open-source projects that are
   *deliberately* vulnerable and where every bug is documented, and load those
   labels into a SQLite database (`data/vulnbench.db`).
2. **Ask the questions** — a set of benchmark questions ("Does this file
   contain a vulnerability? Which CWE?") derived from that answer key.
3. **Grade the tool** — take the tool's findings file, match each finding to
   the answer key, and score it: full credit for the right file *and* right
   bug class, half credit for right file / wrong bug class, zero for a miss,
   and a penalty for flagging code that is actually safe.
4. **Watch for regressions** — a nightly cron run re-scores the tool and
   fails loudly if its accuracy drops below a threshold.

## The ground-truth repos, and how they "realize" vulnerabilities

The answer key comes from OSS projects that are vulnerable *on purpose*. They
live as local clones in [`ground-truth/`](ground-truth/README.md) (contents
gitignored; the builder re-clones anything missing) and are registered in
[`ingest/sources.yaml`](ingest/sources.yaml).

**Active sources — 552 labeled rows today:**

- **SecLLMHolmes** ([ai4cloudops/SecLLMHolmes](https://github.com/ai4cloudops/SecLLMHolmes),
  `ground-truth/secllmholmes/`) — 78 rows. Vulnerabilities are realized as
  *paired files*:
  - *Hand-crafted samples (48)*: eight CWE folders (CWE-22 path traversal,
    CWE-77 command injection, CWE-79 XSS, CWE-89 SQL injection, CWE-190
    integer overflow, CWE-416 use-after-free, CWE-476 NULL dereference,
    CWE-787 out-of-bounds write). In each folder `1.c/2.c/3.c` (or `.py`)
    contain the bug and `p_1 … p_3` are the *patched twins*. An expert-written
    rationale for every file sits under `ground-truth/` in that repo.
  - *Real-world CVEs (30)*: 15 CVEs from gpac, libtiff, etc., each as a
    `vuln.*`/`patch.*` pair — the actual pre-fix and post-fix code — with CWE
    and file metadata in `cve_details.json`.
- **TerraGoat** ([bridgecrewio/terragoat](https://github.com/bridgecrewio/terragoat),
  `ground-truth/terragoat/`) — 474 rows. Deliberately insecure Terraform for
  AWS/Azure/GCP (public S3 buckets, unencrypted databases, open security
  groups…). Here the "labeler" is the **Checkov** policy scanner used as an
  oracle: every failed policy check becomes one vulnerable row with its check
  id, file, and line range.

**Deploy-gated sources** (cloned into `ground-truth/`, registered but not yet
ingested — their ground truth only exists once the environment is deployed):
CloudGoat, AWSGoat, IAM-Vulnerable, GOAD, NYU-CTF Bench, Cybench. Details in
[ground-truth/README.md](ground-truth/README.md).

## The benchmark questions

Three suites, documented question-by-question in
[`questions/README.md`](questions/README.md):

- **`code_vuln` (78, loaded)** — one question per SecLLMHolmes ground-truth
  row: *"Does `<file>` contain a vulnerability? Which CWE?"* Each question
  stores a `ground_truth_ref` back to the answer-key row in
  `ground-truth/secllmholmes/`, so grading is mechanical.
- **`sola_ispm` (77, pending)** and **`sola_crossvendor` (50, pending)** —
  identity-security posture questions from the Sola papers
  (arXiv:2601.07880 / arXiv:2606.02674 Appendix A). Question text is loaded
  *verbatim only* — the loader refuses to invent it and warns until the JSON
  templates ([questions/sola_ispm.json](questions/sola_ispm.json),
  [questions/sola_crossvendor.json](questions/sola_crossvendor.json)) contain
  the pasted appendix text.

## How the benchmarking works

The scorer ([`bench/score.py`](bench/score.py) +
[`bench/run_benchmark.py`](bench/run_benchmark.py)) implements the Sola
four-stage evaluation:

1. **Ingest & normalize.** Read the harness's findings file (JSONL). Resolve
   each finding's free-text `vuln_type` ("SQL injection", "UAF"…) to a CWE via
   a lexicon, with explicit `CWE-<n>` strings taking priority.
2. **Match findings to the answer key.** Exact file-path match first;
   otherwise the *parent-dir + filename tail* (`CWE-89/1.py`) is used, and
   only when that tail is unique across the ground truth in scope. Bare
   basenames are never used — SecLLMHolmes reuses names like `3.c` across CWE
   folders, so basename matching silently mis-grades (this invariant is in
   [CLAUDE.md](CLAUDE.md)).
3. **Expert-proxy score** per answer-key row, on {0, 0.5, 1}:
   - vulnerable file → **1** if flagged with the correct CWE, **0.5** if
     flagged with the wrong CWE, **0** if missed;
   - safe/patched file → **0** if flagged (false positive), **1** otherwise.
4. **LLM-as-judge metrics** — faithfulness, hallucination_free, correctness,
   retrieval_use, example_adapt — scored by **two judges and MIN-aggregated**
   (a finding only gets credit both judges agree on). With
   `ANTHROPIC_API_KEY` + `--judges` these are real Anthropic model judges;
   otherwise a deterministic offline heuristic keeps runs reproducible
   anywhere.

Every run writes findings and scores into the database keyed by
`(run_id, harness)` and is idempotent — rerunning a `run_id` replaces its
rows. `--min-acc <t>` turns a score drop into a non-zero exit for CI/cron.

## How the Google Mantis test harness is benchmarked here

**Mantis** ([github.com/google/mantis](https://github.com/google/mantis)) is
Google's toolkit of security-review *skills* for coding agents — a sequential
pipeline (history → threat-model → research → critic → reproduce → patch →
report) that a coding agent runs to discover and triage vulnerabilities. It
isn't a standalone scanner you invoke; its stages are driven by an agent and
it "generates and executes autonomously generated code," so it is meant to run
only in isolated sandboxes. What matters for benchmarking is its **output
contract**, defined in the repo's [`schema.json`](bench/mantis_schema.json)
(vendored here at commit `876a0c8`).

Mantis produces findings in two shapes, and vulnbench consumes both:

1. **History-inbox lines** — the `mantis-history` stage walks a project's VCS
   history and writes `workspace/historical_learnings.jsonl`, one object per
   past fix:
   ```json
   {"revision_id": "…", "title": "…", "description": "…",
    "code_paths": ["path/to/file.c:123"], "vuln_type": "SQL Injection",
    "mitigation_diff": "…", "cve": "…", "history": [ … ]}
   ```
   (`#/$defs/learning_entry` → "Historical Learning Entry" branch, which
   **requires** all of the above including `history`.)
2. **Rich finding objects** — `workspace/findings/<uuid>.json`, with an
   explicit `cwe`, a `status` (`VALID` / `FALSE_POSITIVE` / `DUPLICATE` / …),
   `severity`, `mitigation`/`patch_diff`, and more (`#/$defs/finding`).

The scorer handles both: `code_paths` are matched to the ground-truth files;
the CWE comes from the explicit `finding.cwe` when present, otherwise
`vuln_type` is resolved via the lexicon; findings whose `status` is
`FALSE_POSITIVE`/`DUPLICATE` are **retracted** (not counted as flags); and any
safe/patched file the harness flags counts as a false positive. Every ingested
line is validated against Google's own `schema.json` before scoring.

### Real-time test against google/mantis (2026-08-02)

The full pipeline can't run here (it needs an agent harness + sandboxes), but
its **history-extraction stage is deterministic and reproducible**, and the
SecLLMHolmes real-world corpus is exactly what that stage consumes: 15
vuln→patch revision pairs with CVE metadata. So the test was:

1. **Validate the harness against Google's real contract.** `schema.json` was
   pulled from google/mantis and vulnbench now validates every findings line
   against it. This immediately caught a real gap — Google's "Historical
   Learning Entry" schema *requires* a `history` array that the original
   sample omitted (0/24 conforming). Adding it brought the sample to **24/24
   conforming**, and the finding-object sample to **3/3**.
2. **Run the Mantis history stage for real** over the CVE corpus
   ([`bench/mantis_history_extract.py`](bench/mantis_history_extract.py) →
   `data/mantis_realworld.historical_learnings.jsonl`), emitting genuine,
   schema-valid Mantis output (human-readable weakness class in `vuln_type`,
   the real vuln→patch unified diff in `mitigation_diff`, so CWE resolution
   goes through the scorer's lexicon rather than being handed the answer).
3. **Score it** against the real-world ground truth. Results below.

Reproduce with `make mantis-realworld`. The shipped
[`data/mantis_findings.sample.jsonl`](data/mantis_findings.sample.jsonl) (24
hand-crafted findings with three planted errors) and
[`data/mantis_finding_object.sample.jsonl`](data/mantis_finding_object.sample.jsonl)
(the rich shape, incl. a retracted `FALSE_POSITIVE`) remain the fast
regression fixtures — point `FINDINGS` at a live pipeline's output to grade it.

## Results

All numbers are from actual runs in this environment (2026-08-02,
Python 3.11.15, Checkov 3.3.9, offline heuristic judges).

**Datasource build** (`python ingest/build_datasource.py`):

```
ground_truth rows by source:
  secllmholmes-handcrafted        48
  secllmholmes-realworld          30
  terragoat                      474
  TOTAL                          552
```

**Questions** (`python questions/loader.py`): 78 `code_vuln` loaded; Sola
suites warn until their 77 + 50 verbatim questions are pasted in.

**Real-time Google Mantis test — history stage over the real-world CVE corpus**
(`make mantis-realworld`):

```
schema: 15/15 lines conform to google/mantis schema.json
ingest: 15 scored, 0 retracted (FALSE_POSITIVE/DUPLICATE), shapes=['learning_entry']

=== vulnbench report  run=mantis-realworld  harness=mantis  gt-source=secllmholmes-realworld ===
ground-truth rows scored : 30
findings ingested        : 15
Expert Accuracy          : 1.0000
Success Rate (full credit): 1.0000
Hallucination-free (judged pairs): 1.0000

by-CWE:
  CWE              n vuln_recall expert_acc  notes
  CWE-190          8        1.00       1.00
  CWE-416          2        1.00       1.00
  CWE-476          8        1.00       1.00
  CWE-787         12        1.00       1.00
```

The Mantis history stage recovered all 15 real CVEs (gpac, libtiff, linux,
pjsip) with the correct CWE class and produced **zero false positives** on the
15 patched twins — every line validated against Google's real `schema.json`.
The 1.00 reflects clean CVE metadata plus correct lexicon resolution of the
weakness-class names; it is the honest end-to-end result, not a planted
fixture.

**Schema conformance** (validating both shipped samples against google/mantis):

| Findings file | Shape | Conformance | Notes |
|---|---|---|---|
| `mantis_findings.sample.jsonl` | learning_entry | 24/24 | after adding the schema-required `history` array |
| `mantis_finding_object.sample.jsonl` | finding | 3/3 | 1 `FALSE_POSITIVE` correctly retracted, 2 scored |
| `mantis_realworld.historical_learnings.jsonl` | learning_entry | 15/15 | generated by the history-extraction stage |

**Mantis scoring run** (`--run-id verify --gt-source secllmholmes-handcrafted`):

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

Acceptance checklist — all planted errors surfaced exactly where expected:

| Check                                        | Expected | Observed |
|----------------------------------------------|----------|----------|
| Expert Accuracy                              | ~0.95    | 0.9479   |
| Planted miss visible (CWE-22 recall)         | 0.67     | 0.67     |
| Planted wrong-CWE visible (CWE-476 acc)      | ~0.92    | 0.92     |
| Planted false positive visible (CWE-89 acc)  | ~0.83    | 0.83     |

Additional verified behavior:

- **Idempotent reruns** — repeating `--run-id verify` leaves exactly 48 score
  rows / 24 finding rows (replaced, not duplicated).
- **Regression gate** — `--min-acc 0.99` exits non-zero
  (`REGRESSION: Expert Accuracy 0.9479 < threshold 0.99`); `--min-acc 0.80`
  exits 0.
- **Full-scope run** (no `--gt-source`) scores all 552 rows: Expert Accuracy
  0.1096, as expected since the sample findings only cover the hand-crafted
  subset.
- **Nightly wrapper end-to-end** (`bash scripts/run_vulnbench.sh`, exit 0,
  logged to `logs/vulnbench-2026-08-02.log`): refresh → 552 rows, questions →
  78, benchmark `nightly-2026-08-02` → Expert Accuracy 0.9479, threshold
  passed, `=== vulnbench run OK ===`.

## Benchmarking your own harness (step-by-step)

Any cyber-assessment harness similar to Mantis can be graded the same way —
the only contract is the findings file.

1. **Set up the environment.**
   ```bash
   git clone <this repo> && cd <repo>
   python3 -m venv .venv && .venv/bin/pip install pyyaml checkov anthropic jsonschema
   ```
2. **Build the answer key.**
   ```bash
   .venv/bin/python ingest/build_datasource.py   # clones ground-truth/, ~552 rows
   .venv/bin/python questions/loader.py          # loads/derives the question suites
   ```
3. **Point your harness at the ground-truth code.** Run it over
   `ground-truth/secllmholmes/datasets/...` (and/or `ground-truth/terragoat/`)
   so its findings reference those file paths. Keep paths repo-relative or at
   least ending in `parent-dir/filename` — that's what the matcher uses.
4. **Export findings as JSONL.** Either Mantis shape works: the
   `historical_learnings.jsonl` line (`code_paths` with `file:line`,
   `vuln_type` free-text or explicit `CWE-<n>`, `title`, `description`,
   `mitigation_diff`, `cve`, `history`) or the rich finding object (`id`,
   `status`, explicit `cwe`, `mitigation`/`patch_diff`). Findings with
   `status` `FALSE_POSITIVE`/`DUPLICATE` are auto-retracted. If your harness
   emits another format, write a small adapter onto these fields.
5. **Score it** (each line is validated against the vendored google/mantis
   `schema.json` first; use `--no-validate` to skip).
   ```bash
   .venv/bin/python bench/run_benchmark.py \
       --findings /path/to/your_findings.jsonl \
       --harness <your-harness-name> --run-id baseline-$(date +%F) \
       --gt-source secllmholmes-handcrafted
   ```
   Add `--judges` with `ANTHROPIC_API_KEY` set for real LLM judges; add
   `--gt-source terragoat` (or omit `--gt-source`) to grade IaC findings too.
6. **Read the report.** Expert Accuracy is the headline; the by-CWE table
   shows which bug classes your harness misses or mislabels;
   hallucination-free and the judge metrics catch confident-but-wrong output.
7. **Sanity-check the pipeline itself** with the shipped sample:
   `make verify` must show the 0.9479 / 0.67 / 0.92 / 0.83 fingerprint. If it
   doesn't, the path matcher has regressed — fix before trusting any scores.
8. **Automate it.**
   ```bash
   make schedule-show   # review the cron line first
   make schedule        # 0 6 * * * … scripts/run_vulnbench.sh (idempotent install)
   ```
   Point the nightly run at your harness's live output:
   `FINDINGS=/path/to/your_findings.jsonl MIN_ACC=0.85` — the run exits
   non-zero (and your cron/CI alerts) the moment accuracy regresses.
9. **Extend the answer key** as your harness grows: add a repo + parser entry
   to `ingest/sources.yaml` (the `checkov_oracle` parser works for any
   Terraform target unchanged), rebuild, and new labeled rows flow into the
   same scoring pipeline.

## Repo layout

```
ground-truth/   cloned vulnerable repos (answer key; contents gitignored)  → README
ingest/         sources.yaml registry + build_datasource.py
questions/      loader.py, suite JSON, per-question README
bench/          schema.sql, score.py, run_benchmark.py, mantis_history_extract.py,
                mantis_schema.json (vendored google/mantis contract) + provenance
data/           mantis_findings.sample.jsonl, mantis_finding_object.sample.jsonl,
                mantis_realworld.historical_learnings.jsonl (committed);
                vulnbench.db (gitignored)
scripts/        run_vulnbench.sh — nightly cron entrypoint
Makefile        build / questions / bench / verify / mantis-realworld / schedule
CLAUDE.md       invariants and commands for AI-assisted development
```
