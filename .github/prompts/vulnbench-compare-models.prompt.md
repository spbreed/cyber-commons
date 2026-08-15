---
mode: agent
description: Reproduce the Cyber Harness Eval model comparison (Opus/Sonnet/Haiku) and report metrics.
---

Reproduce the blind model comparison in Cyber Harness Eval.

Steps:
1. `labs/b2.10-eval-harness/scripts/vulnbench.sh doctor` (setup/build if needed).
2. `labs/b2.10-eval-harness/scripts/vulnbench.sh compare` — runs `labs/b2.10-eval-harness/work_mantis/compare_models.py` (code
   SAST + real-world CVE) and `labs/b2.10-eval-harness/work_mantis/compare_iac.py` (Terraform vs Checkov).

Report a table of precision / recall / F1 / CWE-accuracy / Expert Accuracy per
model, and the per-model failure themes from `labs/b2.10-eval-harness/work_mantis/failing_questions.md`.
Note the ranking is non-monotonic across corpora — recommend a model **per task**
(SAST → Opus, real-CVE/pentest → Sonnet, IaC → Opus), not one overall winner.

To run a *fresh* blind audit with a specific model rather than re-scoring the
committed verdicts, follow `.claude/skills/vulnbench-blind-audit/SKILL.md`.
