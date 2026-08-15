# Lab B2.10 / E1.5 — evaluating a security harness

**Chapters:** [B2.10](../../curriculum/track-b2.md) (build the eval) ·
[E1.5](../../curriculum/track-e1.md) (read it as audit evidence) ·
[C1.6](../../curriculum/track-c1.md) (attack it)

This is the most complete lab in the commons: a working benchmark that scores an
AI security harness against real vulnerability ground truth, with committed
evidence for every number.

> **Where the code lives.** This lab's implementation sits at the repository
> root (`bench/`, `ingest/`, `questions/`, `ground-truth/`, `work_mantis/`,
> `scripts/vulnbench.sh`) rather than inside this folder, because it predates the
> curriculum reorganisation and is a tested, evidenced pipeline — moving it would
> have meant re-validating every path for no learner benefit. Run the commands
> below **from the repository root**.

## Run it

```bash
scripts/vulnbench.sh doctor        # prerequisites
scripts/vulnbench.sh setup         # .venv + deps
scripts/vulnbench.sh build         # 552-row ground truth (SecLLMHolmes + TerraGoat/Checkov)
scripts/vulnbench.sh verify        # regression fingerprint — expect Expert Accuracy 0.9479
scripts/vulnbench.sh compare       # blind model comparison (code + IaC)
scripts/vulnbench.sh cybergym-preflight   # can this host run execution benchmarks?
```

It is also wired as an **agent skill** — ask Claude Code or Copilot to "run the
vulnbench benchmark" and it drives the same entrypoint
(`.claude/skills/`, `.github/prompts/`, `AGENTS.md`).

## What it teaches

1. **Ground truth is the prerequisite.** No answer key, no score.
2. **Blind protocol.** Opaque filenames + held-out labels, or you are measuring
   the model's ability to read a path.
3. **Conformance ≠ accuracy.** Schema validity is ~100% *by construction* and
   says nothing about correctness. Never quote it as quality.
4. **Reliability, not capability.** Report across all attempts, not best-of-*k*.
5. **The model is the biggest lever.** Same harness, same prompt — Expert
   Accuracy swings from 0.47 to 0.95 depending on the backbone.

## Recorded results (committed evidence)

Three model backbones, same blind audit, three corpora:

| Task | Metric | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| SAST — synthetic code (48 files) | Expert Acc | **0.90** | 0.75 | 0.61 |
| CVE — real-world code (30 files) | Expert Acc | 0.87 | **0.95** | 0.47 |
| IaC — TerraGoat vs Checkov (34 files) | micro-F1 | **0.76** | 0.66 | 0.58 |

Ranking is **non-monotonic** — no backbone wins everywhere, which is precisely
why you benchmark on *your* task rather than trusting a leaderboard.

Evidence: [`docs/MODEL_COMPARISON.md`](../../docs/MODEL_COMPARISON.md),
[`docs/REAL_MANTIS_RUN.md`](../../docs/REAL_MANTIS_RUN.md),
[`work_mantis/failing_questions.md`](../../work_mantis/failing_questions.md)
(every wrong answer), blinded corpora and held-out answer keys in
[`work_mantis/`](../../work_mantis/README.md).

## Open-weight backbones

The recorded comparison used Claude models because that was the available
subscription. The harness is **model-agnostic** — point it at any
OpenAI-compatible endpoint to compare Llama / GLM / Kimi instead:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama
for M in llama3.3 glm-4.6 kimi-k2; do MODEL=$M scripts/vulnbench.sh compare; done
```

That reproduction — the same harness across three open-weight families — is the
[C2.6](../../curriculum/track-c2.md) deliverable.

## Execution-based benchmarks

CyberGym / ExploitGym / CyberGym-E2E are integrated via
[`bench/cybergym_adapter.py`](../../bench/cybergym_adapter.py) and scored on the
same Expert-Accuracy scale. They need Docker + ~130GB of task data + Python ≥3.12;
`cybergym-preflight` tells you honestly whether a host can run them. See
[`docs/CYBERGYM_INTEGRATION.md`](../../docs/CYBERGYM_INTEGRATION.md).
