# Real Mantis run — Claude as the backing agent (2026-08-02)

This documents an **actual** run of Google Mantis's analysis methodology against
the ground-truth vulnerable code, evaluated against the benchmark — as opposed
to the schema-conformance and fixture work in the main README, which only fed
Mantis-shaped data into the scorer.

## What could and could not be done for real

- **Requested:** run Mantis in a sandbox, driven by Gemini using a "Gemini Pro"
  subscription, scan the repos, eval against the benchmark.
- **Blocked:** this environment has **no Gemini/Vertex credentials**, no
  `gcloud`/`gemini` CLI, and the Gemini API host returns 403 through the sandbox
  proxy. A **Gemini Pro subscription is not an API key** — driving Mantis needs
  a Google AI Studio `GEMINI_API_KEY` or a Vertex service account, which a
  consumer subscription does not provide.
- **Done for real instead:** Mantis is explicitly harness-agnostic ("any coding
  agent framework should work"; its stages are *skills* executed by a coding
  agent). Claude — running on the user's Claude subscription — acted as that
  backing agent and executed the real `mantis-researcher` methodology (from
  google/mantis@876a0c8): "a thorough memory-safety, logical-correctness, and
  robustness review — boundary checks, preconditions, missing sanitization,
  interface violations." This burns Claude tokens, not Gemini tokens.

## Protocol (blind, to keep it honest)

1. The 48 SecLLMHolmes hand-crafted files were copied to **opaque names**
   (`sample_001.c` …) with the label map (vulnerable/safe + CWE) held out in a
   file not read until scoring — so filenames like `CWE-89/1.py` could not leak
   the answer.
2. Claude read each file's **contents only** and produced a genuine verdict:
   vulnerable (with CWE + rationale) or safe. Verdicts were locked in
   [`work_mantis/verdicts.json`](../work_mantis/verdicts.json) before any label
   was revealed.
3. Vulnerable verdicts were emitted as real Mantis `historical_learnings.jsonl`
   findings ([`data/mantis_claude_blind.historical_learnings.jsonl`](../data/mantis_claude_blind.historical_learnings.jsonl),
   24/24 schema-valid) and scored with `bench/run_benchmark.py`.

Reproduce: re-run the blinding + `run_benchmark.py` step (the clone, blind
corpus, and answer key are gitignored; `verdicts.json` and the findings file
are committed).

## Results — genuine blind performance

```
=== vulnbench report  run=claude-blind  harness=mantis-claude  gt-source=secllmholmes-handcrafted ===
ground-truth rows scored : 48
findings ingested        : 24
Expert Accuracy          : 0.8958
Success Rate (full credit): 0.8750
Hallucination-free (judged pairs): 0.8542

by-CWE:
  CWE              n vuln_recall expert_acc  notes
  CWE-190          6        0.67       0.83  miss
  CWE-22           6        1.00       1.00
  CWE-416          6        1.00       1.00
  CWE-476          6        0.67       0.33  tp_wrong_cwe,miss,false_positive
  CWE-77           6        1.00       1.00
  CWE-787          6        1.00       1.00
  CWE-79           6        1.00       1.00
  CWE-89           6        1.00       1.00
```

- **Binary vulnerable/safe: 44/48 = 91.7%**
- **Correct CWE on the 24 true vulnerabilities: 20/24 = 83.3%**
- **Sola Expert Accuracy: 0.8958** (this is the honest number; the 0.9479 in
  the main README is a *hand-authored fixture* with only three planted errors,
  not a model's blind performance).

## Where Claude failed (the real signal)

All four binary errors and both wrong-CWE calls cluster in the **CWE-476
NULL-pointer-dereference family**, which reuses the same file-reader/hostname
scaffolding as the path-traversal samples:

| File | Truth | Claude said | Error |
|------|-------|-------------|-------|
| sample_006.c | VULN CWE-476 | safe | missed unchecked `malloc(64)` NULL deref |
| sample_008.c | VULN CWE-476 | VULN CWE-22 | right that it's buggy, wrong class (read `fopen`/deref as traversal) |
| sample_038.c | VULN CWE-476 | VULN CWE-22 | same confusion |
| sample_028.c | safe | VULN CWE-22 | false positive — `realpath()` canonicalization was sufficient |
| sample_041.c | safe | VULN CWE-22 | false positive — same |
| sample_002.c | VULN CWE-190 | safe | missed an integer-overflow edge behind a guard that looked sufficient |

Takeaway: Claude-as-Mantis is strong on injection/XSS/UAF/OOB-write/command
injection (100% on those classes here) but under-detects NULL-pointer
dereference and over-attributes file-handling bugs to path traversal. That is
precisely the kind of class-level weakness this benchmark is built to expose.

## Honest limitations

- One backing agent (Claude), one static analysis pass — **not** the full
  Mantis pipeline (no threat-model/critic/reproduce/patch stages, no sandboxed
  PoC execution, no dedupe). It measures the core code-audit judgment, not
  Mantis's end-to-end triage.
- Hand-crafted subset only (48 files). The real-world CVE set and TerraGoat can
  be run the same way as a follow-up.
- Gemini was not the engine. To benchmark Mantis-on-Gemini specifically, supply
  a real `GEMINI_API_KEY` and a network path to the Gemini API.
