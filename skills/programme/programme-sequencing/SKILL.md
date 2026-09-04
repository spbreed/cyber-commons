---
name: programme-sequencing
description: >-
  Simulate a programme's build order against its prerequisites and find the
  steps that block on something not yet done. Use when planning an AI security
  programme, or when a plan starts with evaluation.
allowed-tools: Read, Grep, Glob
---

# Only one step is doable from a standing start

Programme plans are usually ordered by what is interesting or visible.
Simulating the order against prerequisites shows which steps block: the popular
evaluation-first sequence completes four of six on the first pass and stalls
twice, because you cannot evaluate what you have not inventoried or tier what
you cannot list.

## When to use this

Planning a programme, reviewing somebody else's plan, and when a quarter ended
with several things "in progress".

## Procedure

**1 — Write the steps and their prerequisites.** Explicitly, as a dependency
list. Most disagreements about order dissolve here, because the dependency is
not a matter of opinion.

**2 — Identify what is doable from a standing start.** Steps with no
prerequisites. There is usually exactly one, and it is the inventory.

**3 — Simulate the proposed order.** Walk it, marking each step done or blocked.
Report completions on the first pass and the steps that blocked, with what they
were waiting on.

**4 — Simulate the dependency-respecting order** and compare. Same steps, same
effort, different completion — that comparison is the argument, and it does not
require anybody to concede a preference.

**5 — Say what each order produces at the end of each period.** The correct
order usually produces nothing demoable for two quarters, and saying so in
advance is what stops it being abandoned in the second.

## Output contract

```json
{
  "steps": [{"id": 0, "name": "str", "requires": [0]}],
  "doable_from_start": [0],
  "orders": [{"name": "str", "sequence": [0], "completed_first_pass": 0,
              "blocked": [{"step": 0, "waiting_on": [0]}]}],
  "per_period_output": [{"order": "str", "period": "str", "demoable": false}]
}
```

## Failure modes

- **Starting with evaluation.** It depends on nearly everything else.
- **Arguing about order without the dependency list.** It becomes preference.
- **Not warning about the quiet quarters.** The plan gets abandoned mid-way.
