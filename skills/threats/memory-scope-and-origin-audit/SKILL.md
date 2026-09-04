---
name: memory-scope-and-origin-audit
description: >-
  Audit what an agent's persisted memory is keyed by and whether the origin of
  each record survives the write, then show what a poisoned record does to a
  later request from a different user. Use when reviewing memory, RAG stores or
  any state that outlives one session.
allowed-tools: Read, Grep, Glob
---

# A memory write is a durable authorisation decision

Poisoning a session lasts a session. Poisoning memory lasts until somebody
notices, and the damage lands on **a different user's** request — which is why
the key and the origin field matter more than the content filter.

## When to use this

Reviewing any store the agent writes to and later reads back: conversation
memory, a vector index it maintains, a summaries table, a "learned preferences"
record.

## Procedure

**1 — Read the write path, not the read path.** Find every call that persists.
Record the key it writes under and every field it stores.

**2 — Answer the two questions about the key.** Is it scoped to the *writer* —
the user whose content produced it — or to something wider, a workspace, a
tenant, the agent itself? A key wider than the writer is the mechanism by which
one user's content reaches another's session.

**3 — Check whether origin survives the write.** A record derived from an
untrusted document is itself untrusted. If the write drops the origin, the
poison is indistinguishable from a fact on read, and no later control can
recover the distinction.

**4 — Age the payload.** Write from one user's untrusted content, then read
back from a different identity and a later request. The gap is the point: a
memory finding that only reproduces inside one session is a session finding.

**5 — Check expiry and revocation.** Ask what removes a record, and who can
trigger it. "Nothing" is a common and reportable answer.

## Output contract

```json
{
  "writes": [{"site": "str", "key_scope": "writer|workspace|tenant|agent", "origin_stored": false}],
  "cross_user_reachable": true,
  "aged_probe": {"written_by": "str", "read_by": "str", "steered": true},
  "expiry": {"mechanism": "none|ttl|manual", "revocable_by": "str"}
}
```

## Failure modes

- **Auditing the read path.** Reads are where the damage shows; writes are
  where it is decided.
- **Testing inside one session.** The property that matters is survival across
  identities and time.
- **Accepting a content filter as the control.** The record was written by your
  own summariser; it will not look like an attack.
