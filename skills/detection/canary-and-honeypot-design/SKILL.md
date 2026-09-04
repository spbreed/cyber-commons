---
name: canary-and-honeypot-design
description: >-
  Place credential canaries and honeypot tasks in an agent's environment so that
  an alert has no structurally possible false positive, and measure how fast the
  signal decays as agents learn. Use when deception is being added, or when a
  detection needs to be one nobody has to triage.
allowed-tools: Read, Grep, Glob
---

# An alert with no possible false positive

A canary credential that nothing legitimate uses produces an alert that needs no
triage: the only way it authenticates is that somebody read it and tried it.
That property is structural, not statistical, and it is why deception belongs in
an agent environment where every other signal is ambiguous.

## When to use this

Designing detection for agent environments, and whenever an existing detection's
false-positive rate is the reason it is ignored.

## Procedure

**1 — Place canaries where only reading them is unusual.** Environment
variables, config files, the fixtures a code agent walks. They must be
indistinguishable from real ones — a canary named `canary_key` is a filter, not
a trap.

**2 — Ensure nothing legitimate uses them.** This is the whole property. Check
the code, the tests and the deployment. One legitimate reference and the alert
becomes triage.

**3 — Instrument the authentication path** to capture source address and user
agent on use. A canary alert with no context tells you that it happened and
nothing about who.

**4 — Add honeypot tasks for behaviour rather than credentials.** A task with an
available shortcut that nothing legitimate would take. Log the attempt and score
it; this measures inclination, which no credential can.

**5 — Measure decay.** Agents and operators learn. Model the hit rate over days
since placement, with and without rotation, and set the rotation interval from
the curve rather than from a calendar.

## Output contract

```json
{
  "canaries": [{"id": "str", "placed_in": "str", "indistinguishable": true, "legitimate_refs": 0}],
  "alerts": [{"canary": "str", "source_ip": "str", "user_agent": "str", "false_positive_possible": false}],
  "honeypot_tasks": [{"task": "str", "shortcut": "str", "attempts": 0}],
  "decay": {"days": [0], "hit_rate": [0.0], "rotation_days": 0}
}
```

## Failure modes

- **A canary anything legitimate touches.** The property is gone and the alert
  becomes noise.
- **Naming it as a canary.** It becomes a filter for the competent attacker.
- **Never rotating.** The signal decays and the absence of alerts reads as
  safety.
