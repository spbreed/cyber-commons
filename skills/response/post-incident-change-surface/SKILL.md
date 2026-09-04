---
name: post-incident-change-surface
description: >-
  Count the surfaces that change an agent's behaviour without passing change
  management, and check weeks later which post-incident actions are still
  verifiable rather than guidance. Use at post-incident review, or before
  closing actions from the last one.
allowed-tools: Read, Grep, Glob
---

# A prompt edit is guidance, and it closed an action item

Post-incident actions for agentic systems fail in a specific way: several of them
are changes to surfaces that generate no record, and one or two are prompt edits
recorded as controls. Six weeks later nobody can demonstrate that any of it is
still in place, and the review declares the incident closed.

## When to use this

At post-incident review, and again several weeks afterwards — the second pass is
the one that finds this.

## Procedure

**1 — Enumerate the change surfaces and mark which bypass change management.**
Code and infrastructure usually do not; model version, prompt, manifest and
approval settings usually do.

**2 — Classify every action from the review.** Control, detection, guidance, or
documentation. A prompt edit is guidance: it changes behaviour on average and
enforces nothing.

**3 — Test verifiability now.** For each action, is there a check that would fail
if it were reverted? If not, the action cannot be audited and will silently
regress.

**4 — Re-test weeks later.** Run the same check. The count that survives is the
honest measure of the review, and it is usually a third of what was agreed.

**5 — Measure the blast radius before and after.** The reduction is what the
incident actually bought. If it is unchanged, the actions were process rather
than containment, and that belongs in the report.

## Output contract

```json
{
  "surfaces": [{"name": "str", "bypasses_change_management": true}],
  "actions": [{"action": "str", "kind": "control|detection|guidance|documentation",
               "verifiable": false, "check": "str|null"}],
  "recheck": {"weeks_later": 0, "still_verifiable": 0, "of": 0},
  "blast_radius": {"before": 0, "after": 0}
}
```

## Failure modes

- **Recording a prompt edit as a control.** It is guidance under a different
  name.
- **Closing actions at the review.** Re-check weeks later or the number is
  aspirational.
- **No before-and-after blast radius.** Nothing shows whether it helped.
