# Lab M0.2 — the loop, and why the verifier is the security control

**Chapter:** [Module 0](../../curriculum/module-0.md) · sessions M0.1–M0.3, reused by B2.1 and B2.4

The smallest possible security harness: **plan → act → verify → stop**. The lab
exists to make one idea physical — *the verifier is the security control and
everything else is plumbing.*

## Run it

```bash
# Option A — with a real open-weight model (see ../../MODELS.md)
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6

# Option B — no model at all; a deterministic stub drives the loop
#            (a test fixture for the mechanics, never quote it as a result)
export MODEL=stub

pip install pytest

python3 loop.py --verifier pytest      # deterministic oracle
python3 loop.py --verifier llm-judge   # self-grading, same family as generator
python3 loop.py --verifier none        # no stop signal at all
```

## What you should see

Recorded output from this repo (`--model stub`, so it is reproducible):

| Verifier | stop reason | verifier said OK | **actually correct** |
|---|---|---|---|
| `pytest` (oracle) | `verified` | true | **true** |
| `llm-judge` (same family) | `verified` | true | **false** ⚠ |
| `none` | `max_steps` | false | true |

The middle row is the whole lab. The judge approved `return a - b` — the loop
reported success on broken code, confidently, with a clean trace. That is the
**self-grading failure mode** ([B2.2](../../curriculum/track-b2.md)) and it is
why deterministic oracles — compilers, tests, scanners — outrank LLM judges
wherever an oracle exists.

The third row matters too: with no verifier the loop cannot *succeed*, only run
out of budget. "It finished" is not a stop condition
([B2.4](../../curriculum/track-b2.md)).

## Things worth breaking

- `--max-steps`, `--timeout`, `--token-ceiling` — four different stop reasons,
  all recorded in the trace (`--json`).
- Swap `MODEL` between `llama3.3`, `glm-4.6`, `kimi-k2` with the loop unchanged.
  That invariance is the prerequisite for multi-backbone benchmarking in
  [C2.6](../../curriculum/track-c2.md).
- Note there is **no shell tool**. The only action is a narrow `apply_patch`.
  Designing the dangerous call out of existence is
  [B2.3](../../curriculum/track-b2.md), not a policy you bolt on later.

## Implementation notes

`verify_pytest` deletes `__pycache__` and disables bytecode before each run.
Without that, the oracle reads a stale `.pyc` and reports on code that is no
longer on disk — a *lying oracle*, which is worse than no oracle. It was a real
bug in the first version of this lab; it is left documented rather than quietly
fixed, because it is exactly the class of failure the chapter is about.
