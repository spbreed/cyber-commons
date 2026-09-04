---
name: conditional-approval-design
description: >-
  Tier a risky request, show what a flat refusal costs in visibility, and write
  the conditions that make a yes safe, testable and time-bound. Use when the
  answer is no and the capability will ship anyway.
allowed-tools: Read, Grep, Glob
---

# The flat no loses the visibility and the capability ships

A refusal without conditions has a predictable outcome: the capability appears
somewhere you cannot see, on somebody's personal account or inside a product
already bought. A conditional yes keeps it inside the estate, and the conditions
are the control — provided each one is testable and has a date.

## When to use this

Any request whose straightforward answer is no, and any exception that is about
to be granted informally.

## Procedure

**1 — Tier the request and compute its blast radius.** An irreversible
tenant-wide tool is what usually makes it critical, and naming that is more
useful than the tier.

**2 — Model the flat refusal.** Where the capability goes instead, and what
visibility you lose. Write it down — the point is not to argue against refusing
but to price it.

**3 — Write conditions that each remove a term of the risk.** Gate the
irreversible action, narrow the scope, cap the population, add the detection.
Vague conditions — "with appropriate oversight" — are a yes with extra words.

**4 — Make each condition testable.** A check that would fail if the condition
were not met, and who runs it. A condition nobody tests is a condition nobody
keeps.

**5 — Put an expiry on the approval.** Conditional approvals that do not expire
become permanent policy set by whoever asked first.

## Output contract

```json
{
  "request": {"name": "str", "tools": ["str"], "blast": 0, "tier": "str", "irreversible": ["str"]},
  "flat_refusal": {"capability_ships_anyway": true, "visibility_lost": ["str"]},
  "conditions": [{"condition": "str", "removes": "str", "test": "str", "owner": "str"}],
  "approval": {"granted": true, "expires": "str", "review_trigger": ["str"]}
}
```

## Failure modes

- **Refusing without pricing it.** The capability ships out of sight.
- **Untestable conditions.** They are a yes in a longer sentence.
- **No expiry.** The exception becomes the policy.
