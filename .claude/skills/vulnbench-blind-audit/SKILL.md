---
name: vulnbench-blind-audit
description: >-
  Run an LLM model AS the Mantis cyber harness in a blind audit and score it
  (Cyber Harness Eval). Use when asked to have a model find vulnerabilities in
  the ground-truth code, compare models (Opus/Sonnet/Haiku) as the security
  agent, reproduce the model comparison, or produce Expert Accuracy for a model
  rather than for an existing findings file.
allowed-tools: Bash, Read, Grep, Glob, Write, Agent
---

# vulnbench — blind model audit (model as the harness)

This runs the real Mantis `mantis-researcher` methodology with an LLM as the
backing model, **blind** (opaque filenames, held-out labels), then scores it.

## Corpora (already blinded and committed)
- `work_mantis/blind/` — 48 SecLLMHolmes hand-crafted files (SAST).
- `work_mantis/blind_rw/` — 30 real-world CVE files.
- `work_mantis/blind_iac/` — 34 Terraform files (IaC, scored vs Checkov).

The held-out answer keys are `work_mantis/.labels*.json` — **do not read them
during analysis**, only the scorer uses them.

## Steps

1. **Brief the model.** Give it the identical instruction file so runs are
   comparable:
   - code corpora → `work_mantis/AGENT_INSTRUCTIONS.md`
   - IaC corpus → `work_mantis/IAC_INSTRUCTIONS.md`

2. **Run the audit.** Either analyze the corpus yourself (as the current model)
   or spawn a subagent pinned to a specific model (`Agent` tool, `model:
   sonnet` / `haiku` / `opus`). The model reads **contents only** and writes a
   verdicts JSON:
   - code → `{"model": "...", "verdicts": {"sample_001.c": {"v": 1, "cwe": "CWE-77", "why": "..."}, ...}}`
     to `work_mantis/verdicts_<model>.json` (hand-crafted) or
     `work_mantis/verdicts_rw_<model>.json` (real-world).
   - IaC → `{"model": "...", "findings": {"iac_01.tf": ["ENCRYPTION", ...], ...}}`
     to `work_mantis/iac_<model>.json`.
   For real CVE code, frame the task explicitly as an **authorized defensive
   review of public, already-patched code for a benchmark** — bare prompts can
   trip cyber safeguards.

3. **Score and compare.**
   ```bash
   scripts/vulnbench.sh compare        # runs compare_models.py + compare_iac.py
   ```
   Reports precision / recall / F1 / CWE-accuracy / Expert Accuracy per model.

4. **Cross-check (optional, rigorous).** Emit a Mantis findings file from a
   verdicts file (translate blind_id → real path via the answer key) and run
   `scripts/vulnbench.sh score` on it — the official scorer must agree.

## Reading the result
Report per-model Expert Accuracy / F1 and the **failure themes** from
`work_mantis/failing_questions.md`. Remember the ranking is non-monotonic
(different model wins per corpus); recommend a model per task, not overall.
