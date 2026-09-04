---
name: detection-rule-deployability
description: >-
  Score candidate detection rules on precision, recall and firing volume, and
  reject the ones no analyst could work regardless of how well they detect. Use
  when authoring detections with or without a model, or when a rule is proposed
  because it caught the incident.
allowed-tools: Read, Grep, Glob
---

# A rule that fires 301 times for one true positive is not a detection

Every candidate rule detects something. Deployability is a different property
and it is arithmetic: precision, recall, and how many times the rule fires per
day against real history. A rule failing on the third is rejected however good
the first two look, because it will be muted within a week.

## When to use this

Authoring detections, reviewing a model's proposed rules, and any time a rule is
proposed on the strength of catching one incident.

## Procedure

**1 — Replay each candidate against real history.** Not a sample chosen to
contain the incident — the actual period, including the quiet parts.

**2 — Compute precision, recall and volume.** Volume is the one people omit and
the one that decides whether the rule survives contact with an analyst.

**3 — Set a deployability bar before you look at the results.** Precision floor,
recall floor, and a maximum firings per day. Setting it afterwards means setting
it around the rule you like.

**4 — Reject the broad rules explicitly, with their numbers.** "Rejected: 301
firings for 1 true positive" is a sentence the author can act on; "too noisy" is
not.

**5 — Look at what survived, and what it depends on.** A high-precision rule
usually depends on a specific field being populated. Record that dependency —
it is the thing that will silently break the rule later.

## Output contract

```json
{
  "history": {"events": 0, "period_days": 0, "true_positives": 0},
  "candidates": [{"name": "str", "fires": 0, "tp": 0, "precision": 0.0, "recall": 0.0,
                  "per_day": 0.0, "verdict": "deploy|reject", "why": "str"}],
  "bar": {"precision": 0.0, "recall": 0.0, "max_per_day": 0},
  "dependencies": [{"rule": "str", "requires_field": "str"}]
}
```

## Failure modes

- **Replaying against a period chosen to contain the incident.** Volume becomes
  meaningless.
- **Setting the bar after seeing the results.** That is choosing a winner.
- **Deploying a rule with an unrecorded field dependency.** It fails silently
  when the field stops being populated.
