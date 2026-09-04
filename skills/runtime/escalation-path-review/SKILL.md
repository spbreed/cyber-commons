---
name: escalation-path-review
description: >-
  Check whether an agent that notices something outside its task has any way to
  say so, and price the reporting tool it is offered — terminality, budget cost
  and penalty — against the alternative of carrying on. Use when designing tool
  lists, or after an agent silently continued through something it should have
  raised.
allowed-tools: Read, Grep, Glob
---

# An agent with no way to report will not report

An agent that encounters a live third-party breach mid-task produces no report
if its tool list has no way to produce one. That is not a judgement failure; it
is a missing tool. And adding one is not enough: a reporting tool that ends the
run, spends the budget and carries a penalty is priced below carrying on, so it
will not be used.

## When to use this

When designing an agent's tool list, when raising autonomy, and after any
incident where an agent continued through something a person would have
escalated.

## Procedure

**1 — Take a trajectory with something worth raising in it.** Real or
constructed: a credential in output, a third-party compromise, a task that has
become something other than what was asked.

**2 — Run it against the tool list as shipped.** Record whether any report is
possible at all. "The agent did not raise it" is meaningless until this is
answered.

**3 — Add a reporting tool and re-run.** The difference is the baseline: the
capability, before any question of incentive.

**4 — Price the tool.** Three terms — does calling it end the run, does it
consume the task budget, does it carry a penalty in whatever the agent is
scored on. Compute its value against continuing. A tool priced below continuing
is a tool that exists for the design review.

**5 — Add a checkpoint that does not depend on the agent choosing.** A pattern
check on output — credential-shaped strings, hosts outside the allowlist — that
pauses regardless of the agent's judgement. This is the part that works when
the incentive analysis fails.

## Output contract

```json
{
  "trajectory": ["str"],
  "as_shipped": {"tools": ["str"], "report_produced": false},
  "with_tool": {"tools": ["str"], "report_produced": true},
  "pricing": {"terminal": true, "costs_budget": true, "penalised": true,
              "value_of_reporting": 0.0, "value_of_continuing": 0.0, "would_use": false},
  "checkpoint": {"patterns": ["str"], "paused_on": ["str"], "agent_choice_required": false}
}
```

## Failure modes

- **Concluding the agent chose not to report.** Check the tool list first.
- **Adding the tool and stopping.** An unpriced tool is not an escalation path.
- **Relying on the agent's judgement** for the case where its judgement is what
  failed. The checkpoint does not ask.
