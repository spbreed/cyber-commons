---
name: model-risk-validation-scope
description: >-
  Check whether a model validated under one autonomy level and tool set is still
  covered by that validation as deployed, and find the monitoring that stops at
  the model's output. Use when applying model risk management to an agentic
  system.
allowed-tools: Read, Grep, Glob
---

# The validation was of a system that had no tools

Model risk management carries three pillars — validation, monitoring,
governance — and each makes an assumption that agentic deployment breaks.
Validation assumes the thing validated is the thing deployed; a model validated
with no tools at L1 and deployed with three tools at L3 is the same model and a
different system, and the validation does not cover it.

## When to use this

Applying an existing model risk framework to agents, and at every autonomy or
tool-manifest change afterwards.

## Procedure

**1 — Write down what was validated.** Model, version, tool set, autonomy level,
data scope. Validation scope is usually recorded as the model alone, which is
the defect.

**2 — Write down what is deployed,** in the same fields. Then diff. Any
difference in tools or autonomy means the validation does not cover the
deployment, and that sentence is the finding.

**3 — Check what monitoring observes.** Most monitors the model's output
distribution. List what it does not observe — rows written to production, actions
taken, resources reached — because that is where agentic risk lives.

**4 — Name the re-validation triggers.** Tool added, autonomy raised, model
version changed, data scope widened. Without triggers, re-validation happens on
the audit calendar, which is the assumption that failed in the first place.

**5 — Report per pillar.** Validation coverage, monitoring blind spots,
governance triggers. Three findings with three owners rather than one finding
about the framework.

## Output contract

```json
{
  "validated": {"model": "str", "version": "str", "tools": ["str"], "autonomy": "str", "data": ["str"]},
  "deployed": {"model": "str", "version": "str", "tools": ["str"], "autonomy": "str", "data": ["str"]},
  "covers": false,
  "differences": ["str"],
  "monitoring": {"observes": ["str"], "does_not_observe": ["str"]},
  "revalidation_triggers": ["str"]
}
```

## Failure modes

- **Recording validation scope as the model.** It is the system.
- **Monitoring output distribution only.** The actions are the risk.
- **Calendar re-validation.** The triggers are events, not dates.
