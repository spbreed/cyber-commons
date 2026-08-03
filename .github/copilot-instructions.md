# GitHub Copilot instructions — Cyber Harness Eval

This repo benchmarks an AI security harness (Mantis-style) against vulnerability
ground truth. When asked to run, benchmark, or evaluate the harness, drive
everything through the single entrypoint — do not hand-roll Python calls.

## Entrypoint

```bash
scripts/vulnbench.sh doctor        # check prerequisites
scripts/vulnbench.sh setup         # create .venv + install deps
scripts/vulnbench.sh build         # build ground-truth datasource (~552 rows)
scripts/vulnbench.sh score --findings <f.jsonl> --gt-source <source> --min-acc 0.80
scripts/vulnbench.sh verify        # regression fingerprint (Expert Accuracy 0.9479)
scripts/vulnbench.sh compare       # model comparison (code + IaC)
```

## Guidance
- Run `doctor` first; if venv/datasource missing → `setup` then `build`.
- Findings file: Mantis `historical_learnings.jsonl` or `finding` object (JSONL).
- `--gt-source` ∈ `secllmholmes-handcrafted` | `secllmholmes-realworld` | `terragoat`.
- **Report Expert Accuracy, not conformance.** Conformance is schema validity
  (~100%, structural); accuracy is correctness (the real number).
- A non-zero exit from `--min-acc` is a regression — surface it, don't hide it.
- Reusable prompt files live in [`.github/prompts/`](prompts). Full detail in
  [`../AGENTS.md`](../AGENTS.md) and [`../README.md`](../README.md).
