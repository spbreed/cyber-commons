---
name: technique-reproducibility-test
description: >-
  Run a technique enough times to say whether it reproduces, and compute the
  sample size a before-and-after comparison actually needed before claiming a
  control worked. Use when a jailbreak "works", or when a fix is declared
  effective from a handful of trials.
allowed-tools: Read, Grep, Glob
---

# One success is an anecdote; the interval is the result

Model-layer research is statistical whether or not anybody does the statistics.
A technique that succeeds once may not reproduce; a control that appears to
help at n=20 has an interval overlapping the baseline. Both errors are avoided
by the same discipline — report a rate with an interval, and compute the sample
size before running the comparison.

## When to use this

Any claim about model behaviour: a technique that works, a control that helps, a
model that is safer than another.

## Procedure

**1 — Define success mechanically.** A string, a state, a check — something a
script decides. "The model complied" judged by reading is not reproducible
between two people.

**2 — Run enough trials to produce a rate, and hold the conditions fixed.**
Same model version, same temperature, same prompt. Record the version: a rate
without one is unrepeatable by construction.

**3 — Classify the technique honestly.** Not reproduced, flaky, or reproducible.
Flaky is a real and common answer and it deserves the word rather than a
rounded-up rate.

**4 — Compute the required sample size before comparing.** From the baseline
rate, the effect you would care about, and the power you want. Then run that
many. Doing this afterwards produces the number that makes the result you got
look significant.

**5 — Report intervals, and say when they overlap.** Show the same true effect
at n=20, n=100 and n=1000 if you need to make the point: the effect did not
change, the ability to see it did.

## Example

**Input** — the fixture committed at the top of [`scripts/technique_reproducibility_test.py`](scripts/technique_reproducibility_test.py). Edit it and re-run: the buckets, counts and verdicts below are derived from it, not hard-coded.

**Output** — the opening lines of a real run:

```
technique              rate              ci95  verdict
------------------------------------------------------------
direct override       0.055    (0.023, 0.087)  flaky
context reframe       0.395    (0.327, 0.463)  flaky
task nesting          0.660    (0.594, 0.726)  reproducible

'It worked' is true for all three. Only one is reproducible.
     n            before             after  conclusion
```

The run continues past this. The script is the example: `test_skills.py` executes it on every build, so this block cannot drift from what the skill actually prints.

## Output contract

```json
{
  "success_criterion": "str",
  "conditions": {"model": "str", "version": "str", "temperature": 0.0},
  "techniques": [{"name": "str", "trials": 0, "rate": 0.0, "interval": [0.0, 0.0],
                  "verdict": "not reproduced|flaky|reproducible"}],
  "comparison": {"before": 0.0, "after": 0.0, "n": 0, "required_n": 0, "separated": false}
}
```

## Failure modes

- **Reporting a rate with no model version.** Nobody can repeat it.
- **Computing the sample size afterwards.** That is choosing the number that
  fits.
- **Rounding flaky up to works.** It is the finding, not a rough edge.
