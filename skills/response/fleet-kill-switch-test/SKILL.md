---
name: fleet-kill-switch-test
description: >-
  Test a fleet-wide stop for what it leaves behind — valid tokens, destroyed
  evidence, and the runs that should have been preserved — and measure how long
  the whole thing takes. Use before relying on a kill switch, and after
  designing one.
allowed-tools: Read, Grep, Glob
---

# Terminating the agents leaves every token valid

A fleet kill switch usually terminates workloads. Termination does not revoke
credentials, so every token the fleet held stays valid until it expires — up to
seventy-two hours of an attacker being able to act as agents that no longer
exist. And a kill that does not preserve first destroys the evidence for the
incident that triggered it.

## When to use this

Before a kill switch is relied on, after it is built, and once a year as a
rehearsal.

## Procedure

**1 — Terminate only, and count what stays valid.** Tokens, sessions,
outstanding delegated grants. This is the baseline failure and it is invisible
in a design review.

**2 — Terminate and revoke together, and re-count.** Zero is the target. If
revocation is a separate runbook step performed by a different team, it will not
happen at speed.

**3 — Check evidence preservation.** Kill with and without preservation, then
attempt the reconstruction. A kill switch that destroys the run records is a
containment that ends the investigation.

**4 — Test selectivity.** Stop one agent, one class, the whole fleet. A switch
with only the last setting will not be used until it is far too late, which is
the same as not having one.

**5 — Measure the time.** Decision to last agent stopped and last token revoked.
Set a target and report against it; an untimed rehearsal is a demonstration.

## Output contract

```json
{
  "fleet": {"agents": 0, "tokens": 0},
  "terminate_only": {"tokens_valid_after": 0, "max_validity_hours": 0},
  "terminate_and_revoke": {"tokens_valid_after": 0},
  "preservation": {"preserved": true, "reconstructable": true},
  "selectivity": [{"scope": "one|class|fleet", "supported": true}],
  "timing": {"target_minutes": 0.0, "measured_minutes": 0.0}
}
```

## Failure modes

- **Terminating without revoking.** The credentials outlive the workloads.
- **Killing before preserving.** The incident becomes unreconstructable.
- **A fleet-only switch.** Nobody uses it until the whole estate is on fire.
