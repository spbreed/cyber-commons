# Model comparison — Claude Opus / Sonnet / Haiku as the Mantis agent

Google Mantis is model-agnostic (its skills are executed by a coding agent).
Using the user's Claude subscription, three Claude models each ran the **same
blind `mantis-researcher` audit** over the same corpora, then were scored
against the held-out labels. This isolates the one variable that matters for a
Mantis deployment: **which backing model finds the bugs.**

## Method

- **Corpora (blinded):** 48 SecLLMHolmes hand-crafted files (24 vuln / 24 safe)
  and 30 real-world CVE files (15 vulnerable pre-fix + 15 patched, from libtiff,
  gpac, Linux kernel, pjsip). Files were copied to opaque names with the answer
  key held out; models saw **contents only**.
- **Agent:** each model ran as a subagent with the identical brief
  ([`work_mantis/AGENT_INSTRUCTIONS.md`](../work_mantis/AGENT_INSTRUCTIONS.md)) —
  the real Mantis researcher methodology, constrained to the 8-CWE SecLLMHolmes
  taxonomy for comparability.
- **Scoring:** [`work_mantis/compare_models.py`](../work_mantis/compare_models.py)
  computes vuln-detection precision/recall/F1, CWE accuracy on true vulns, and
  the Sola expert-proxy accuracy ({0,0.5,1}). Cross-checked against the official
  `bench/run_benchmark.py` (Sonnet hand-crafted = 0.7500 both ways).

## Results

| Model  | Corpus       | n  | TP | FP | FN | TN | Precision | Recall | F1   | CWE acc | **Expert Acc** |
|--------|--------------|----|----|----|----|----|-----------|--------|------|---------|----------------|
| Opus   | hand-crafted | 48 | 22 |  2 |  2 | 22 | 0.92      | 0.92   | 0.92 | 0.83    | **0.90**       |
| Sonnet | hand-crafted | 48 | 23 |  9 |  1 | 15 | 0.72      | 0.96   | 0.82 | 0.79    | **0.75**       |
| Haiku  | hand-crafted | 48 | 18 | 10 |  6 | 14 | 0.64      | 0.75   | 0.69 | 0.54    | **0.61**       |
| Opus   | real-world   | 30 | 13 |  1 |  2 | 14 | 0.93      | 0.87   | 0.90 | 0.73    | **0.87**       |
| Sonnet | real-world   | 30 | — blocked by real-time cyber safeguards (see below) — |||||||| |
| Haiku  | real-world   | 30 |  3 |  3 | 12 | 12 | 0.50      | 0.20   | 0.29 | 0.07    | **0.47**       |

(TP = true vuln correctly flagged; FP = safe file flagged; FN = vuln missed;
TN = safe correctly cleared. Expert Acc is the Sola {0,0.5,1} score.)

## What the numbers say

- **Clear, consistent model ordering: Opus > Sonnet > Haiku**, on both corpora.
- **Opus is robust and well-calibrated** — 0.90 on synthetic, 0.87 on the much
  harder real-world CVEs, with very few false positives (2 and 1). On the
  real-world pairs it correctly reasoned "is the guard present or absent?"
- **Sonnet over-reports.** Highest recall on hand-crafted (0.96 — misses almost
  nothing) but precision only 0.72: it flagged 9 safe files as vulnerable. In a
  real pipeline that is triage load; Mantis's critic/review stages exist partly
  to absorb exactly this.
- **Haiku degrades sharply on real code.** Passable on toy samples (0.61) but on
  real-world CVEs it flagged only 3 of 15 true vulns (recall 0.20, CWE acc
  0.07) — it defaults to "safe" when the code is large and unfamiliar. Not
  suitable as the audit model for real targets.
- **Sonnet's real-world audit was blocked by Anthropic's real-time cyber
  safeguards** — reading the real CVE code (libtiff/Linux/gpac/pjsip) tripped
  the filter twice, even though Sonnet handled the synthetic set fine. This is a
  genuine operational constraint for running cyber evals on the consumer tier:
  the Cyber Verification Program exists to lift it
  (https://support.claude.com/en/articles/14604842).

## Caveats

- One static-analysis pass per model — **not** the full Mantis pipeline (no
  threat-model / critic / reproduce / patch / dedupe stages, no sandboxed PoC).
  This measures the backing model's raw code-audit judgment, which is the single
  biggest driver of Mantis quality but not the whole system.
- Small corpora (48 + 30). Treat gaps of a few points as noise; the
  cross-corpus ordering and the Haiku real-world collapse are the robust signals.
- Opus hand-crafted was run interactively (documented in REAL_MANTIS_RUN.md);
  the other five runs were subagents. All used the identical brief and scorer.
