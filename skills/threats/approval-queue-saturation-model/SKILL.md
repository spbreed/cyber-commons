---
name: approval-queue-saturation-model
description: >-
  Model what happens to an approval gate as volume rises — coverage staying at
  100% while actual review collapses — and find the volume at which the control
  stops working. Use when reviewing human-in-the-loop design, approval fatigue,
  or a gate that has never been measured.
allowed-tools: Read, Grep, Glob
---

# Coverage stays at 100%; reading does not

An approval gate reports the same number at every volume, because coverage
measures whether a human was *asked*. What degrades is whether they read it,
and an attacker who can choose position only has to generate enough requests to
sit behind.

## When to use this

Any control whose enforcement is a person: approvals, exception reviews, alert
triage sign-off, change advisory.

## Procedure

**1 — Measure current volume,** per reviewer per day. Not the design volume —
the observed one, at peak rather than mean.

**2 — Establish the reading budget.** How many items can one reviewer consider
properly in a shift? Ask them; the number is usually between 20 and 30 and it
is always far below the queue.

**3 — Model detection against position.** Place a malicious item at various
depths and compute the probability it is actually read. The curve falls off a
cliff at the reading budget, not gradually.

**4 — Note who controls position.** If a requester can generate the items in
front of theirs, depth is attacker-chosen and the average case is irrelevant.

**5 — Report the two numbers that change the design.** Items per reviewer per
day, and the reading budget. The gap between them is the finding, and it points
at routing by reversibility rather than at hiring.

## Output contract

```json
{
  "volume": {"per_reviewer_per_day": 0, "measured_at": "peak|mean"},
  "reading_budget": 0,
  "coverage_reported": 1.0,
  "detection_by_depth": [{"depth": 0, "read_probability": 0.0}],
  "position_attacker_controlled": true,
  "gap": 0
}
```

## Failure modes

- **Reporting coverage.** It is 100% by construction and means nothing.
- **Using mean volume.** The gate fails at peak.
- **Recommending more reviewers.** The fix is fewer items, chosen by
  reversibility.
