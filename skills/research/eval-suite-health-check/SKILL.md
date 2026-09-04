---
name: eval-suite-health-check
description: >-
  Run an evaluation suite with confidence intervals, confirm a control moves one
  surface and not the others, and detect the suite being diluted by cases
  everything blocks. Use when an eval score improves and you need to know
  whether the system did.
allowed-tools: Read, Grep, Glob
---

# A suite that gets easier reports that you got better

An evaluation suite is an instrument, and instruments drift. Two properties keep
it honest: a control should move the surface it addresses and leave the others
alone, and the aggregate should not improve because somebody added cases
everything already blocks.

## When to use this

Whenever an eval number moves, before adding cases to a suite, and at any
regular review of a safety benchmark you rely on.

## Procedure

**1 — Run the baseline with intervals.** Per case and per surface. A point
estimate cannot support the comparison you are about to make.

**2 — Apply one control and re-run.** The prediction is specific: the surface it
addresses drops, with non-overlapping intervals, and the other surfaces do not
move. Both halves are the test — a control that moves everything is measuring
something other than the control.

**3 — Report per surface, never only in aggregate.** The aggregate hides both a
control that works and a control that broke something else.

**4 — Dilute the suite deliberately.** Add cases the target trivially blocks and
re-compute. Watch the aggregate improve while nothing about the system changed.
That demonstration is what justifies the next step.

**5 — Add a suite-health check.** Difficulty distribution, share of cases no
target has ever failed, and the date each case was added. A suite with a growing
share of trivial cases is reporting improvement it has not earned.

## Output contract

```json
{
  "baseline": [{"case": "str", "surface": "str", "rate": 0.0, "interval": [0.0, 0.0]}],
  "with_control": [{"surface": "str", "rate": 0.0, "interval": [0.0, 0.0], "moved": true}],
  "expected_unchanged": ["str"],
  "dilution": {"added_trivial": 0, "aggregate_before": 0.0, "aggregate_after": 0.0},
  "health": {"trivial_share": 0.0, "never_failed": 0, "oldest_case": "str"}
}
```

## Failure modes

- **Aggregate-only reporting.** It hides the two things you are looking for.
- **A control that moves every surface.** Investigate before celebrating.
- **Adding cases without recording difficulty.** The suite drifts easier and the
  score drifts up.
