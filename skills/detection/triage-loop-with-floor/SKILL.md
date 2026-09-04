---
name: triage-loop-with-floor
description: >-
  Run an alert triage loop against ground truth, measure the confusion matrix,
  and bound it with a confidence bar and a severity floor no automatic closure
  may cross. Use when automating triage, or when deciding what an agent may
  close on its own.
allowed-tools: Read, Grep, Glob
---

# The floor is the part that makes the loop deployable

A triage loop that matches ground truth on a sample is a promising loop. What
makes it something you can run is the pair of bounds around it: a confidence bar
that decides when it defers, and a severity floor it may never close through,
whatever its confidence.

## When to use this

Before an agent closes anything, and when tuning how much of a queue is
automated.

## Procedure

**1 — Score against ground truth, as a confusion matrix.** Escalated and closed,
against true and false. Accuracy alone hides the direction of the errors, and
only one direction matters here.

**2 — Sweep the confidence bar.** For each setting, record analyst minutes saved
and incidents missed. This is the trade being made, and it should be made
explicitly by whoever owns the queue rather than implicitly by a default.

**3 — Set the severity floor separately.** Any alert above it is escalated
regardless of confidence. A confident wrong closure on a critical alert is the
failure this exists to prevent, and no confidence threshold protects against it.

**4 — Check what the floor costs.** How many alerts it forces to a human per
day. If that number is above the reading budget, the floor is theatre and the
queue needs a different cut.

**5 — Record every automatic closure with its reason and confidence.** The loop
will be wrong sometimes; the question at review is whether you can find out how.

## Output contract

```json
{
  "confusion": {"tp": 0, "fp": 0, "tn": 0, "fn": 0},
  "confidence_sweep": [{"bar": 0.0, "analyst_minutes_saved": 0, "incidents_missed": 0}],
  "floor": {"severity": "str", "escalated_regardless": 0, "per_day": 0},
  "audit": {"closures_logged": true, "fields": ["reason", "confidence", "rule"]}
}
```

## Failure modes

- **Reporting accuracy.** The direction of the error is the whole question.
- **A floor set above the reading budget.** It routes to a person who will not
  read it.
- **Unlogged closures.** You cannot review what the loop decided.
