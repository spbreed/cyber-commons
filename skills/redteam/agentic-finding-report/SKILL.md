---
name: agentic-finding-report
description: >-
  Write up an agentic finding so it names the missing control, states explicitly
  what is not a fix, and carries a regression case that fails on the old build
  and passes on the new one. Use when a report will be read by the team that has
  to close it.
allowed-tools: Read, Grep, Glob
---

# A finding is closed by a control, not by a fix

A weak agentic report describes a payload and predicts its own outcome: the
prompt gets patched, the payload stops working, the class remains. A strong one
names the control that is missing, names the plausible fixes that are not fixes,
and hands over a case that fails today and passes when the control exists.

## When to use this

Every agentic finding you report, and especially the ones where the reproduction
is a prompt.

## Procedure

**1 — Separate the instance from the class.** The payload is an instance.
Name the class — no provenance on ingress, authorisation on the workload,
unbounded egress — because that is what a control closes.

**2 — Name the control.** Not "sanitise input": the specific mechanism, at the
specific point. A report whose remediation section could be pasted into another
report has not done this.

**3 — Write down what is not a fix**, explicitly, with a sentence each. Blocking
the phrase. Adding the instruction to the system prompt. Filtering the one host.
Every one of these will be proposed, and pre-empting them is the difference
between one round and four.

**4 — Write the regression case.** It must fail on the current build. A case
that passes today is a case that will pass forever without anything being fixed.

**5 — Verify it both ways.** Fails on the old build, passes with the control in
place. Hand over both results; the pair is what lets somebody else re-run it.

**6 — Record surface coverage.** How many surfaces you tested and how many you
did not. A report that implies completeness it does not have is the reason the
next one is not believed.

## Output contract

```json
{
  "finding": {"instance": "str", "class": "str"},
  "control": {"mechanism": "str", "point": "str"},
  "not_a_fix": [{"proposal": "str", "why_not": "str"}],
  "regression_case": {"description": "str", "old_build": false, "new_build": true},
  "coverage": {"surfaces_tested": ["str"], "surfaces_untested": ["str"]}
}
```

## Failure modes

- **Reporting the payload.** It will be blocked and the class will remain.
- **A regression case that passes today.** It tests nothing.
- **Implying full coverage.** State the untested surfaces or the next report
  starts from disbelief.
