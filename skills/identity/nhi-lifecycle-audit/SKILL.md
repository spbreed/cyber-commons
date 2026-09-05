---
name: nhi-lifecycle-audit
description: >-
  Audit non-human identities as provisioned resources with a human owner
  reference — checking admission, orphaning, lapse, and whether a leaver event
  on the owner actually removes the agent's access. Use when agents outlive the
  people who created them, or when asked who owns a service account.
allowed-tools: Read, Grep, Glob
---

# An agent identity with no owner is a permanent one

Non-human identities are created for a proof of concept and are still
authenticating two years later. The lifecycle question is not "does it exist"
but "what event removes it", and the answer that works is an **owner reference**
resolved at admission — so the leaver process you already run does the work.

## When to use this

Any estate with service accounts, agent identities or machine credentials —
particularly where agents are created programmatically, or where a
proof-of-concept identity was never retired.

## Procedure

**1 — Enumerate the identities as resources.** Name, created-at, last-used, and
the schema they are provisioned under. SCIM (RFC 7643/7644) is the interface
most estates already have; use it rather than inventing a registry.

**2 — Require an owner reference, not an owner string.** `owner.$ref` pointing
at a `User` resource resolves; a name in a text field does not. The difference
is whether a leaver event can be followed.

**3 — Classify every identity against admission.** Four outcomes and all four
must be exercised: admitted, **unregistered** (exists, nobody provisioned it),
**orphaned** (owner reference does not resolve), **lapsed** (unused past its
window).

**4 — Run a leaver event.** A single `PATCH {active: false}` on the owner. Then
re-run admission. Any agent whose owner is now inactive must be refused on the
next presentation — not swept overnight, refused.

**5 — Report the sweep as a control, not a report.** A list of orphaned
identities that nobody acts on is a recurring finding. Name the automatic
consequence.

## Example

**Input** — the fixture committed at the top of [`scripts/nhi_lifecycle_audit.py`](scripts/nhi_lifecycle_audit.py). Edit it and re-run: the buckets, counts and verdicts below are derived from it, not hard-coded.

**Output** — the opening lines of a real run:

```
POST /scim/v2/Agents
{
 "active": true,
 "displayName": "pricing-agent",
 "externalId": "spiffe://cybertravels.com/ns/prod/sa/pricing-agent",
 "id": "b7f3a1c2",
 "meta": {
  "created": "2026-01-14T09:02:00Z",
```

The run continues past this. The script is the example: `test_skills.py` executes it on every build, so this block cannot drift from what the skill actually prints.

## Output contract

```json
{
  "identities": [{"name": "str", "owner_ref": "str|null", "last_used": 0,
                  "verdict": "admitted|unregistered|orphaned|lapsed"}],
  "owner_resolution": {"kind": "reference|string", "resolvable": false},
  "leaver": {"event": "str", "agents_refused_after": ["str"], "on_next_presentation": true},
  "sweep": {"window_days": 0, "automatic_consequence": "str"}
}
```

## Failure modes

- **An owner recorded as text.** It cannot be joined to the leaver process, so
  it is documentation.
- **Sweeping instead of refusing.** A nightly job leaves a window; admission
  does not.
- **Counting unregistered as orphaned.** They have different owners and
  different fixes.
