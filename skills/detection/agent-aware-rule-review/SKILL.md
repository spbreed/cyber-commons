---
name: agent-aware-rule-review
description: >-
  Run existing detection rules against an agent doing its job to find which fire
  on legitimate work, and measure behavioural drift from a signed-off baseline
  week by week. Use when agents enter an estate whose detection content predates
  them.
allowed-tools: Read, Grep, Glob
---

# Every classic rule fires on an agent working normally

Detection content written for humans classifies agent behaviour as an incident:
the volume rule, the off-hours rule, the breadth-of-access rule. Turning them
off loses coverage; leaving them on trains the analyst to ignore them. The
answer is a per-population baseline and a drift measure against it.

## When to use this

Whenever agents are introduced into an estate with existing detection content,
and at each model or manifest upgrade afterwards.

## Procedure

**1 — Run each classic rule against a clean agent run** and against a human's
day. Record which fire on which. Rules that fire on the agent and not the human
are the ones needing a population.

**2 — Sign off a baseline for each agent.** Tools used, resources touched, rate,
hours. Signed off means somebody agreed it — a baseline nobody approved is a
measurement, not a control.

**3 — Compare each subsequent week against the baseline.** Report a drift figure
and, more usefully, the *new* items: a tool that was not in the baseline is the
signal, and it is legible in a way a distance number is not.

**4 — Set a tolerance and say what crossing it does.** Drift within tolerance is
noise; beyond it is a review, and the review is of the change that caused it —
usually a model upgrade or a manifest edit.

**5 — Write the alert text for a human.** "patch-agent drift 0.35, new tools:
run_shell" is actionable. A distance metric on its own gets closed.

## Output contract

```json
{
  "classic_rules": [{"name": "str", "fires_on_agent": true, "fires_on_human": false}],
  "baseline": {"agent": "str", "tools": ["str"], "resources": ["str"], "signed_off": true},
  "weeks": [{"week": 0, "drift": 0.0, "new_tools": ["str"], "within_tolerance": true}],
  "tolerance": 0.0,
  "alert_text": "str"
}
```

## Failure modes

- **Muting the classic rules.** You lose them for humans too.
- **A baseline nobody signed off.** Nothing to appeal to when it drifts.
- **Alerting on the distance only.** Name the new tool.
