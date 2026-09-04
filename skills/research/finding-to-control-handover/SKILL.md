---
name: finding-to-control-handover
description: >-
  Convert a research finding into the three artefacts that outlive it — an eval
  case, a control and a detection — and verify the eval fails on the old build
  and passes on the new one. Use when closing a finding, or when research output
  is not reaching the teams that own the fix.
allowed-tools: Read, Grep, Glob
---

# Three artefacts, three owners, or the finding is a memory

The handover is the whole value of a research function. A finding produces an
**eval case** (so the class is measured from now on), a **control** (so it stops
happening), and a **detection** (so you see it when the control is off). Each
has a different owner, and a handover missing one of them silently reopens.

## When to use this

At the close of every finding worth having found, and when planning what a
research team's output should be.

## Procedure

**1 — Write the eval case first.** It is the artefact that keeps the class
measured after everyone has moved on. Verify it fails on the current build —
that is what makes it a test rather than a hope.

**2 — Specify the control at the enforcement point.** Which mechanism, where it
binds. Then check the case passes with it in place, and check the principal's
own path still works, because a control that also blocks legitimate use is an
outage with a security justification.

**3 — Write the detection for the control being off.** Not for the payload — the
payload changes. The detection fires when the condition the control prevents
occurs, which is what you need when somebody disables it for a demo.

**4 — Name an owner per artefact.** Eval to whoever runs the suite, control to
the platform team, detection to the SOC. An artefact with no owner is the one
that will not exist in six months.

**5 — Record coverage.** How many source-and-privilege combinations the control
covers, and which it does not. Partial coverage is fine; unstated partial
coverage is how the next finding is a surprise.

## Output contract

```json
{
  "finding": {"class": "str"},
  "eval_case": {"description": "str", "old_build": false, "new_build": true, "owner": "str"},
  "control": {"mechanism": "str", "point": "str", "principal_path_ok": true, "owner": "str"},
  "detection": {"fires_on": "str", "severity": "str", "owner": "str"},
  "coverage": {"combinations": 0, "covered": 0, "gaps": ["str"]}
}
```

## Failure modes

- **A detection for the payload.** It will be the next payload.
- **No owner.** The artefact does not survive the quarter.
- **Not checking the principal path.** The control gets rolled back and the
  finding reopens.
