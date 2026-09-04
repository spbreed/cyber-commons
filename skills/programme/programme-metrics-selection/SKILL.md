---
name: programme-metrics-selection
description: >-
  Pick programme metrics that degrade when the programme is neglected, and
  separate them from the comfortable ones that stay green regardless. Use when
  choosing what to report, or when every metric is green and the estate is not.
allowed-tools: Read, Grep, Glob
---

# A metric that cannot go red is a decoration

The test for a programme metric is simple and rarely applied: if the programme
were neglected for a quarter, would this number move? Counts of policies
published, training completed and tools deployed would not. Exposure,
containment effectiveness, evidence freshness and measured time-to-stop all
would.

## When to use this

Choosing what to report to an executive committee, and auditing an existing
dashboard that is entirely green.

## Procedure

**1 — List the candidate metrics** and, for each, what it is computed from.
Anything computed from a plan rather than from the estate is a decoration
already.

**2 — Apply the neglect test.** Simulate a quarter with nothing done: no
attestations refreshed, no evals run, no drift reviewed. Which numbers move?

**3 — Keep the ones that move and say what each one costs to compute.** A
metric nobody can produce monthly will be produced annually and stop being a
control.

**4 — Report the comfortable ones you are dropping,** with the reason. They have
constituencies, and removing them silently gets them reinstated.

**5 — Set a target and a direction per surviving metric.** A number with no
target is a chart; a number with a target is a commitment somebody is
accountable for.

## Output contract

```json
{
  "candidates": [{"name": "str", "computed_from": "estate|plan", "moves_under_neglect": false}],
  "kept": [{"name": "str", "value": 0.0, "target": 0.0, "cadence": "str", "cost": "str"}],
  "dropped": [{"name": "str", "why": "str"}],
  "neglect_simulation": {"quarter": "str", "moved": ["str"], "unmoved": ["str"]}
}
```

## Failure modes

- **Metrics computed from the plan.** They measure the plan.
- **Dropping comfortable metrics silently.** They come back.
- **No target.** Nobody is accountable for a direction.
