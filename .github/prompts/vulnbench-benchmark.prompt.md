---
mode: agent
description: Run the Cyber Harness Eval benchmark on a findings file and report accuracy.
---

Benchmark an AI security harness with Cyber Harness Eval.

Steps (use the `labs/b2.10-eval-harness/scripts/vulnbench.sh` entrypoint, run from repo root):
1. `labs/b2.10-eval-harness/scripts/vulnbench.sh doctor` — if venv or datasource is missing, run
   `labs/b2.10-eval-harness/scripts/vulnbench.sh setup` then `labs/b2.10-eval-harness/scripts/vulnbench.sh build`.
2. Score the findings file the user provides (Mantis `historical_learnings.jsonl`
   or `finding`-object JSONL):
   `labs/b2.10-eval-harness/scripts/vulnbench.sh score --findings ${input:findings} --gt-source ${input:gtSource:secllmholmes-handcrafted} --min-acc 0.80`
3. If no findings file exists yet, run `labs/b2.10-eval-harness/scripts/vulnbench.sh verify` to prove the
   pipeline (expect Expert Accuracy 0.9479).

Report the **Expert Accuracy**, the by-CWE breakdown (where it fails), and
whether it passed `--min-acc`. Do NOT report schema conformance as if it were
accuracy — conformance is structural (~100%), accuracy is correctness.
