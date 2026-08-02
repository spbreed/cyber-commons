# vulnbench

**A benchmark that measures — with evidence — how good an AI security harness
actually is at finding vulnerabilities, and which model to run it on.**

vulnbench takes an LLM-driven security tool (built around Google's
[Mantis](https://github.com/google/mantis) contract), runs it blind against
open-source code and cloud config whose bugs are already documented, and scores
the findings against that ground truth — across code SAST, real CVEs, and
Infrastructure-as-Code.

---

## Before → After (the value add)

| | **Before vulnbench** | **After vulnbench** |
|---|---|---|
| Trust in findings | An AI harness emits a list of "findings" — no way to know how many are real | Every finding scored against a 552-row ground-truth datasource; honest Expert Accuracy per run |
| Correctness of scoring | Naïve file matching (basename) silently mis-scores — SecLLMHolmes reuses `3.c`, `p_1.py` across CWE dirs | Collision-safe **parent-dir+filename-tail** matcher (invariant, guarded) — no silent mis-scores |
| Format trust | "Is this even valid Mantis output?" unknown | Every line **schema-validated** against the real `google/mantis` contract |
| Model choice | "Which model should back the harness?" a guess | **Evidence-based** Opus/Sonnet/Haiku comparison across SAST / CVE / IaC |
| Honesty | Easy to fool yourself with a hand-authored demo | **Blind protocol** (opaque filenames, held-out keys) — the committed 0.90 is real, not a 0.95 fixture |
| Cost | Run the biggest model on everything | Measured **token-vs-accuracy** guidance per task |

Everything below is reproducible: blinded corpora, answer keys, per-model locked
outputs, deterministic scorers, and Mantis-schema findings are all committed
under [`work_mantis/`](work_mantis/README.md), [`data/`](data), and
[`docs/`](docs).

---

## Summary of findings

Three Claude models ran the **same blind audit** on the user's Claude
subscription, across three real tasks. Headline scores (full detail in
[docs/MODEL_COMPARISON.md](docs/MODEL_COMPARISON.md)):

| Task | Metric | **Opus** | **Sonnet** | **Haiku** |
|------|--------|----------|------------|-----------|
| **SAST** — synthetic code (48 SecLLMHolmes) | Expert Acc | **0.90** | 0.75 | 0.61 |
| **CVE** — real-world code (30 CVE files) | Expert Acc | 0.87 | **0.95** | 0.47 |
| **IaC** — TerraGoat vs Checkov (34 `.tf`) | micro-F1 | **0.76** | 0.66 | 0.58 |

1. **Model quality dominates harness quality.** The single biggest lever on a
   Mantis deployment is the backing model: Expert Accuracy spans 0.47→0.95 on
   the *same* code with the *same* prompt.
2. **Ranking is not monotonic.** Opus is the most consistent, but **Sonnet is
   the best on real CVE code (0.95, zero false positives, 14/15 caught)** while
   over-flagging synthetic toys (0.75). Real patched code has a concrete fix to
   detect; the synthetic "safe" traps bait Sonnet into false positives.
3. **Haiku collapses on real code** — it flags only 3 of 15 real CVEs
   (recall 0.20). Fine-ish on toys, unsafe as the audit model for real targets.
4. **All models are high-precision on IaC** (~0.88–0.90 vs Checkov) but lose the
   long tail (backup/DR, misc hardening).
5. **Cyber safeguards are real and content-triggered.** Sonnet's CVE run was
   blocked twice under a bare prompt; it completed only with explicit
   authorized-defensive-review framing. IaC review never tripped it.

---

## Conformance vs. Accuracy (read this before quoting a number)

These are two different measurements and it is easy to confuse them:

| | **Conformance** | **Accuracy** |
|---|---|---|
| Question | *Is the finding valid Mantis output?* | *Is the finding correct?* |
| Checks | JSON shape vs `google/mantis` schema (`revision_id, title, description, code_paths, vuln_type, mitigation_diff, cve, history` present, right types) | Does the vuln/safe + CWE call match ground truth? |
| Typical value | **100%** | Opus 0.90 / Sonnet 0.75 / Haiku 0.61 (SAST) |
| Why | **Structural, and true by construction** — the emitter fills every required field | **Semantic** — the model actually has to find the bug |

**Why conformance is 100%:** it is a plumbing check that the harness *speaks
Mantis's format*, and we build each line to that shape. It says **nothing** about
whether the vulnerability call is right. A "SQL injection in a safe file" finding
still conforms — it's well-formed and wrong.

It is a *real* check, not a rubber stamp — it has failed and been fixed:
`0/24` when the sample omitted the schema-required `history` array → `23/24`
with one `mitigation_diff: null` → `24/24` once fixed. **The number you should
quote for "how good is the harness" is Accuracy, never conformance.**

---

## Per-model failure themes (evidence: [`work_mantis/failing_questions.md`](work_mantis/failing_questions.md))

### Opus — precise, one systematic blind spot
- **Theme: NULL-pointer-dereference (CWE-476).** Every code miss/mislabel on
  both corpora clusters here (3 of 6 hand-crafted, 2 of 5 real-world). It reads
  NULL-deref file-readers as **path traversal** — e.g. `CWE-476/1.c` has both a
  discarded-`realpath` smell *and* an unchecked `fopen`→`fgets`; Opus flags the
  traversal, ground truth labels the NULL deref.
- Minor: a couple of guarded **integer-overflow** edges (CWE-190) read as safe.
- Very few false positives (2 and 1). **Well-calibrated; trust its "safe."**
- IaC: strongest recall (0.66); perfect on SECRETS (1.00), strong PUBLIC_ACCESS.

### Sonnet — over-eager on toys, excellent on real code
- **Theme: false positives on synthetic patched code.** 9 of its 14
  hand-crafted failures are safe files it flagged (recall 0.96, precision 0.72)
  — residual hygiene smells in the "safe" twins bait it.
- **On real CVE code the trait inverts:** only 2 failures out of 30, **zero
  false positives** — the best real-world run of any model.
- Shares the CWE-476/CWE-416 mislabel confusion on a few files.
- IaC: weakest on NETWORK_CONTROLS (0.33). **Trust its real-world "vuln"
  findings; discount its synthetic false positives.**

### Haiku — over- and under-flags toys, misses real bugs
- **Theme (toys): scattered noise** — 10 false positives + 6 misses + 5 wrong
  CWEs on 48 files; no reliable direction.
- **Theme (real code): systematic misses.** 12 of 17 real-world failures are
  **missed vulnerabilities** (CWE-787 ×5, CWE-476 ×4, CWE-190 ×4) — it defaults
  to "safe" on large unfamiliar code (recall 0.20).
- IaC: weak ENCRYPTION (0.38) and LOGGING (0.41) recall. **Not safe as the sole
  audit model for real targets.**

---

## Which model, where

| Use case | Recommended | Why (evidence) |
|----------|-------------|----------------|
| **SAST triage on your own code** (synthetic-like, many files) | **Opus** | Highest Expert Acc (0.90), few false positives — least human triage load |
| **Pentest / real-CVE reasoning** (large real code, exploit-relevant) | **Sonnet** | Best real-world run (0.95, precision 1.00); Opus close behind (0.87) |
| **IaC / threat-model reasoning** (Terraform, cloud posture) | **Opus** | Best IaC recall/F1 (0.66/0.76); no safeguard friction on config review |
| **Cheap first-pass filter** | **not Haiku on real code** | Haiku real-world recall 0.20 → a Haiku filter would drop ~80% of real bugs |
| **Second opinion / FP control** | **Opus reviews Sonnet** | Sonnet finds aggressively; Opus is calibrated on "safe" — pair them |

---

## How the harness's accuracy is improved (what makes the scores trustworthy)

1. **Collision-safe path matching (the core invariant).** Findings match ground
   truth by exact path, else the **unique parent-dir+filename tail**
   (`CWE-89/1.py`), **never bare basename** — SecLLMHolmes reuses `3.c`/`p_1.py`
   across CWE dirs, so basename matching silently mis-scores. Ambiguous tails
   are refused. Regression-guarded by the `make verify` fingerprint.
2. **Real-contract schema validation.** Every line is validated against the
   vendored `google/mantis` `schema.json` — this caught the missing `history`
   field that made the first sample 0/24.
3. **Blind protocol.** Opaque filenames + held-out answer keys give honest
   numbers: the committed **0.8958** is blind model performance, distinct from
   the **0.9479** hand-authored fixture (three planted errors) used only as a
   pipeline regression check.
4. **Status retraction + dual-judge MIN aggregation.** `FALSE_POSITIVE`/
   `DUPLICATE` findings are auto-retracted (matching real Mantis triage); two
   judges are MIN-aggregated so a finding only earns credit both agree on.

---

## Token-maxxing (cost vs accuracy, measured)

Real subagent usage from these runs (tokens per 30–48-file audit):

| Model | Real-world audit tokens | Accuracy | Verdict |
|-------|------------------------|----------|---------|
| Haiku | ~105k (fastest/cheapest) | 0.47 | cheap but misses most real bugs |
| Sonnet | ~289k | **0.95** | best accuracy-for-cost on real code |
| Opus | ~278k | 0.87 | strong, consistent |

Evidence-based ways to cut tokens **without** losing the accuracy that matters:

- **Route by task, don't max-model everything.** IaC audits cost ~72–93k for all
  three models but Opus wins on quality → use Opus there; on real code Sonnet
  matches Opus tokens at higher accuracy → use Sonnet.
- **Batch files per call.** One subagent audited 30–48 files in a single
  context (amortized system prompt) instead of one request per file.
- **Constrain the output.** The brief asks for verdict JSON + a one-line reason,
  not a verbose report — output tokens dominate cost.
- **Do *not* use Haiku as a cheap pre-filter on real code.** Its 0.20 real-world
  recall means a "Haiku says safe → skip" gate would silently drop ~80% of real
  vulnerabilities. The cheap-filter pattern only holds where recall is high.

---

## What's in the box

- **Ground truth** — SQLite datasource of 552 labeled rows: SecLLMHolmes code
  vulns (78) + TerraGoat misconfigs via Checkov (474). See
  [`ground-truth/README.md`](ground-truth/README.md).
- **Questions** — 78 derived code-vuln questions + the Sola ISPM/cross-vendor
  suites (pending verbatim appendix text). See
  [`questions/README.md`](questions/README.md).
- **Scorer** — the four-stage Sola evaluator (`bench/`), schema validation, and
  the IaC multi-label scorer.
- **Real runs & evidence** — [`work_mantis/`](work_mantis/README.md): blind
  corpora, answer keys, per-model verdicts, comparison scorers, failing-question
  dumps. Write-ups in [docs/](docs).

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install pyyaml checkov anthropic jsonschema

.venv/bin/python ingest/build_datasource.py        # build ground truth (~552 rows)
.venv/bin/python questions/loader.py               # load question suites
.venv/bin/python bench/run_benchmark.py --findings <jsonl> --gt-source <source>  # score
make verify                                        # pipeline regression fingerprint
make mantis-realworld                              # Mantis history stage over real CVEs
python work_mantis/compare_models.py               # code model comparison
python work_mantis/compare_iac.py                  # IaC model comparison
```

## How the benchmarking works (four-stage Sola evaluation)

1. **Ingest & normalize** — read the harness findings (Mantis
   `historical_learnings.jsonl` or the rich `finding` object); resolve free-text
   `vuln_type` to a CWE (explicit `finding.cwe` wins); retract
   `FALSE_POSITIVE`/`DUPLICATE`.
2. **Match** — exact path, else unique parent+filename tail (never basename).
3. **Expert-proxy {0, 0.5, 1}** — vuln file → 1 right CWE / 0.5 wrong CWE / 0
   miss; safe file → 0 if flagged (false positive) else 1.
4. **LLM-as-judge** — faithfulness, hallucination_free, correctness,
   retrieval_use, example_adapt; two judges, MIN-aggregated (real Anthropic
   judges with `--judges` + key, deterministic offline heuristic otherwise).

Idempotent per `(run_id, harness)`; `--min-acc <t>` exits non-zero on regression
for CI/cron. Scheduling entrypoint: `scripts/run_vulnbench.sh` +
`make schedule` (see [CLAUDE.md](CLAUDE.md)).

## Repo layout

```
ground-truth/  cloned vulnerable repos (answer key; contents gitignored)  → README
ingest/        sources.yaml registry + build_datasource.py
questions/     loader.py, suite JSON, per-question README
bench/         schema.sql, score.py, run_benchmark.py, mantis_history_extract.py,
               iac_categorize.py, mantis_schema.json (vendored google/mantis)
data/          Mantis findings samples + blind-run findings (committed); vulnbench.db (gitignored)
work_mantis/   blind corpora, answer keys, per-model verdicts, scorers, evidence  → README
docs/          REAL_MANTIS_RUN.md, MODEL_COMPARISON.md
scripts/       run_vulnbench.sh — nightly cron entrypoint
```
