# Cyber Harness Eval

**Measure — with evidence — how good an AI security harness actually is at
finding vulnerabilities, and decide which model to run it on.**

Cyber Harness Eval takes an LLM-driven security tool (built around Google
[Mantis](https://github.com/google/mantis)'s findings contract), runs it **blind**
against open-source code and cloud config whose bugs are already documented, and
**scores** the findings against that ground truth — across code SAST, real CVEs,
and Infrastructure-as-Code.

---

## Why this project

AI security harnesses are **probabilistic**. They emit confident "findings," but
some are real, some are hallucinated, and some are right-bug/wrong-reason. Ship
one into a security pipeline without measuring it and you are trusting a black
box with your risk decisions.

There was no easy way to answer three questions that decide whether such a tool
is safe to deploy:

1. **Is it correct?** How many findings are true vs. false, and does it get the
   vulnerability class right?
2. **Is it valid?** Does it even emit well-formed output your pipeline can consume?
3. **Which model should back it?** Opus, Sonnet, Haiku — the same harness scores
   very differently depending on the model inside it.

Cyber Harness Eval answers all three with reproducible, committed evidence. It is
the **Evaluation & Risk Gate** for "AI for Security" tooling: you do not let a
probabilistic vulnerability finder into production ungraded.

---

## Example cyber harnesses (Mantis and its cousins)

A "cyber harness" is an LLM/agent-driven tool that autonomously reviews code or
systems for security issues. This eval framework scores any of them — natively
for anything that emits the Mantis `historical_learnings.jsonl` / `finding`
schema, or via a thin adapter for the rest.

| Harness | What it is |
|---------|-----------|
| **Google Mantis** ([google/mantis](https://github.com/google/mantis)) | Model-agnostic *skills* pipeline (history → threat-model → research → critic → reproduce → patch → report) run by a coding agent. The reference contract for this repo. |
| **Google Big Sleep** | DeepMind/Project-Zero agent that finds real memory-safety bugs in production software. |
| **OpenAI Aardvark** | Agentic "security researcher" that scans repos, validates exploitability, proposes patches. |
| **XBOW** | Autonomous offensive-security (pentest) agent that solves web-app benchmarks. |
| **PentestGPT / CAI** | Open-source LLM-driven penetration-testing assistants. |
| **ZeroPath / Corgea / Almanax** | Commercial LLM-based SAST that triages and fixes findings. |

They differ in surface (SAST vs. pentest vs. IaC) but share one problem: **their
output is only as trustworthy as its measured accuracy.** That is what this repo
provides.

---

## Strategy to eval your cyber harness

Five moves, each of which this repo implements and evidences:

1. **Build an answer key.** Collect code/config whose vulnerabilities are already
   labeled — SecLLMHolmes (hand-labeled CWEs + real CVEs) and TerraGoat scanned
   by Checkov — into a 552-row SQLite ground truth.
2. **Run the harness blind.** Feed it the targets under **opaque filenames** with
   the labels **held out**, so it cannot pattern-match the answer. Honest numbers,
   not a demo.
3. **Validate the format (conformance).** Check every finding against the real
   `google/mantis` JSON schema — separately from whether it's *correct*.
4. **Score correctness (accuracy).** Match findings to ground truth with a
   **collision-safe path matcher**, then apply the Sola four-stage score
   (expert-proxy {0, 0.5, 1} + dual LLM judges, MIN-aggregated).
5. **Compare models & decide.** Run the same blind audit on Opus/Sonnet/Haiku,
   read per-model failure themes, and route each task to the right model.

> **Conformance ≠ Accuracy.** Conformance asks *"is it valid Mantis output?"* —
> ~100%, true by construction, says nothing about correctness. Accuracy asks
> *"is it right?"* — the real score (0.47–0.95 here). **Always quote accuracy.**

---

## Before & After

| | **Before** | **After (Cyber Harness Eval)** |
|---|---|---|
| Trust in findings | a list, no idea how many are real | every finding scored vs. 552-row ground truth |
| Scoring correctness | naïve basename matching silently mis-scores | collision-safe parent-dir+filename-tail matcher |
| Format trust | "is this valid Mantis output?" unknown | schema-validated against the real google/mantis contract |
| Model choice | a guess | evidence-based Opus/Sonnet/Haiku comparison (SAST/CVE/IaC) |
| Honesty | fooled by a hand-authored demo | blind protocol — committed 0.90 is real, not a 0.95 fixture |
| Cost | biggest model on everything | measured token-vs-accuracy routing |

---

## What is in the box

- **Ground truth** — SQLite datasource, 552 labeled rows: SecLLMHolmes code vulns
  (78) + TerraGoat IaC misconfigs via Checkov (474). → [`ground-truth/`](ground-truth/README.md)
- **Questions** — 78 derived code-vuln questions + Sola ISPM/cross-vendor suites.
  → [`questions/`](questions/README.md)
- **Scorer** — four-stage Sola evaluator, `google/mantis` schema validation, IaC
  multi-label scorer. → [`bench/`](bench)
- **Real runs & evidence** — blind corpora, held-out answer keys, per-model locked
  verdicts, deterministic scorers, failing-question dumps. → [`work_mantis/`](work_mantis/README.md)
- **Write-ups** — [`docs/REAL_MANTIS_RUN.md`](docs/REAL_MANTIS_RUN.md),
  [`docs/MODEL_COMPARISON.md`](docs/MODEL_COMPARISON.md)
- **Training** — a lightboard course for newcomers to cyber + AI.
  → [`training/`](training/README.md)

---

## How to set it up

```bash
git clone <this repo> && cd Cyber-harness-eval
python3 -m venv .venv
.venv/bin/pip install pyyaml checkov anthropic jsonschema

.venv/bin/python ingest/build_datasource.py     # clones ground-truth/, builds ~552 rows
.venv/bin/python questions/loader.py             # loads/derives the question suites
```

Requires `git`, `python3`, and `checkov` (installed above). Cloned vulnerable
repos land in `ground-truth/` (contents gitignored); the DB is `data/vulnbench.db`.

---

## Commands

One entrypoint drives everything (this is what the agent skills call):

```bash
scripts/vulnbench.sh doctor              # check prerequisites
scripts/vulnbench.sh setup               # create .venv + install deps
scripts/vulnbench.sh build               # build datasource (~552 rows) + load questions
scripts/vulnbench.sh score --findings <jsonl> --gt-source <source> --min-acc 0.80
scripts/vulnbench.sh verify              # regression fingerprint (0.9479)
scripts/vulnbench.sh compare            # model comparison (code + IaC)
```

Underlying tools (called by the entrypoint; usable directly too):
`ingest/build_datasource.py`, `questions/loader.py`, `bench/run_benchmark.py`,
`work_mantis/compare_models.py`, `work_mantis/compare_iac.py`,
`make mantis-realworld`, `make schedule-show`.

`score` flags: `--gt-source` (scope), `--run-id` (idempotent named run),
`--judges` (real Anthropic judges; needs `ANTHROPIC_API_KEY`), `--min-acc <t>`
(non-zero exit on regression), `--no-validate` (skip schema check).

---

## How to run benchmarks

The benchmark runs **as an agent skill** — one entrypoint,
[`scripts/vulnbench.sh`](scripts/vulnbench.sh), wrapped for every agent surface
so you can just *ask* your coding agent to "run the vulnbench benchmark" and it
executes the same steps a human would.

### As an agent skill

| Agent | How it's wired | To invoke |
|-------|----------------|-----------|
| **Claude Code** | [`.claude/skills/vulnbench-benchmark/`](.claude/skills/vulnbench-benchmark/SKILL.md) and [`vulnbench-blind-audit`](.claude/skills/vulnbench-blind-audit/SKILL.md) (auto-trigger on description) | "run the vulnbench benchmark on `<findings.jsonl>`" or `/vulnbench-benchmark` |
| **GitHub Copilot** | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) + prompt files in [`.github/prompts/`](.github/prompts) | `/vulnbench-benchmark` in Copilot Chat |
| **Cursor / other** | [`AGENTS.md`](AGENTS.md) (cross-agent standard) | "benchmark the harness per AGENTS.md" |

All three call the same entrypoint, so results are identical regardless of agent.

### Directly (what the skills run)

```bash
scripts/vulnbench.sh doctor                    # check prerequisites
scripts/vulnbench.sh setup                     # create .venv + install deps (first time)
scripts/vulnbench.sh build                     # build ground truth (~552 rows) + questions

# 1. Score a harness's findings (Mantis historical_learnings.jsonl or finding-object JSONL)
scripts/vulnbench.sh score --findings <path.jsonl> \
    --harness mantis --run-id nightly-$(date +%F) \
    --gt-source secllmholmes-handcrafted --min-acc 0.80

# 2. Reproduce the model comparison (Opus/Sonnet/Haiku, code + IaC)
scripts/vulnbench.sh compare

# 3. Pipeline regression fingerprint — must print Expert Accuracy 0.9479
scripts/vulnbench.sh verify
```

`score` reports Expert Accuracy, by-CWE recall, and mean judge metrics, and exits
non-zero if accuracy drops below `--min-acc` (that non-zero is the CI/regression
signal). For a fresh **blind model audit** (running a model *as* the harness
rather than scoring an existing file), follow the `vulnbench-blind-audit` skill /
[`work_mantis/README.md`](work_mantis/README.md).

> **Verified run (through the entrypoint):** `scripts/vulnbench.sh verify` →
> `Expert Accuracy 0.9479`; `scripts/vulnbench.sh compare` reproduces the full
> Opus/Sonnet/Haiku table below.

---

## Repo layout

```
.claude/skills/ Claude Code agent skills (vulnbench-benchmark, vulnbench-blind-audit)
.github/        Copilot instructions + prompt files (.github/prompts/)
AGENTS.md       cross-agent instructions (Copilot/Cursor/… standard)
scripts/        vulnbench.sh (agent-skill entrypoint) + run_vulnbench.sh (cron)
ground-truth/  cloned vulnerable repos (answer key; contents gitignored)  → README
ingest/        sources.yaml registry + build_datasource.py
questions/     loader.py, suite JSON, per-question README
bench/         schema.sql, score.py, run_benchmark.py, mantis_history_extract.py,
               iac_categorize.py, mantis_schema.json (vendored google/mantis)
data/          Mantis findings samples + blind-run findings; vulnbench.db (gitignored)
work_mantis/   blind corpora, answer keys, per-model verdicts, scorers, evidence  → README
docs/          REAL_MANTIS_RUN.md, MODEL_COMPARISON.md
training/      lightboard course (cyber + AI for newcomers)  → README
Makefile       build / questions / bench / verify / mantis-realworld / schedule
```

---

## Summary of findings

Three Claude models ran the **same blind audit** across three real tasks
(full detail in [docs/MODEL_COMPARISON.md](docs/MODEL_COMPARISON.md)):

| Task | Metric | **Opus** | **Sonnet** | **Haiku** |
|------|--------|----------|------------|-----------|
| **SAST** — synthetic code (48 files) | Expert Acc | **0.90** | 0.75 | 0.61 |
| **CVE** — real-world code (30 files) | Expert Acc | 0.87 | **0.95** | 0.47 |
| **IaC** — TerraGoat vs Checkov (34 files) | micro-F1 | **0.76** | 0.66 | 0.58 |

- **Model quality is the biggest lever.** Same code, same prompt, Expert Accuracy
  spans 0.47 → 0.95 across models.
- **Ranking is not monotonic.** Opus is most consistent; **Sonnet is best on real
  CVE code (0.95, zero false positives, 14/15 caught)** but over-flags synthetic
  toys; **Haiku collapses on real code** (flags 3 of 15 real CVEs).
- **Failure themes** ([`work_mantis/failing_questions.md`](work_mantis/failing_questions.md)):
  Opus → misses/mislabels **NULL-pointer-deref (CWE-476)**; Sonnet → **false
  positives on patched synthetic code**; Haiku → **systematic misses on real bugs**.
- **Which model where:** SAST triage → **Opus**; pentest / real-CVE reasoning →
  **Sonnet**; IaC / threat-model reasoning → **Opus**. Do **not** use Haiku as a
  cheap pre-filter on real code (0.20 recall drops ~80% of real bugs).
- **Conformance was 100%; accuracy was not** — the harness always emits valid
  Mantis output, but correctness is where models pass or fail.
- **Cyber safeguards are real** — Sonnet's CVE run was blocked twice under a bare
  prompt; it completed only with explicit authorized-defensive-review framing.
