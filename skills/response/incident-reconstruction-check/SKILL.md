---
name: incident-reconstruction-check
description: >-
  Reconstruct an incident from logs that attribute every action to a human,
  check what the evidence actually supports, and refuse to publish a narrative
  it does not carry. Use during response, when the timeline names a person and
  an agent did the work.
allowed-tools: Read, Grep, Glob
---

# The fluent narrative recommends suspending the wrong person

Agent logs that record only the delegated principal produce a timeline in which
a human did everything. A model asked to summarise it writes something fluent
and confident that recommends suspending her. The reconstruction is not wrong
about the events; it is wrong about the actor, and nothing in the log says so.

## When to use this

Every incident involving an agent, and before any narrative reaches a person who
will act on it.

## Procedure

**1 — Render the timeline as the logs have it.** Do not correct it yet. This is
what an investigator would see, and seeing it is the point.

**2 — Ask which field carries the acting identity.** Not the delegated
principal — the identity that performed the action. If no field carries it, stop:
every attribution below is inherited from the request, not observed.

**3 — Produce the truth view from an independent source** where one exists — host
accounting, the gateway, the downstream's own log. Diff it against the timeline
and record what changes. Usually one or two actions move from the human to the
agent, and they are the important ones.

**4 — Gate the narrative on evidence.** A summary may assert only what a field
supports. Attach the field to each claim; a claim with no field is removed, not
softened.

**5 — Publish the safe version and the gap.** State plainly which questions the
record cannot answer. An investigation that says so is more useful than one that
fills the gap fluently.

## Output contract

```json
{
  "timeline": [{"at": "str", "attributed_to": "str", "action": "str"}],
  "acting_identity_field": "str|null",
  "truth_view": [{"at": "str", "actual_actor": "str", "action": "str", "source": "str"}],
  "narrative": {"claims": [{"text": "str", "supported_by": "str|null"}], "removed": 0},
  "gaps": ["str"]
}
```

## Failure modes

- **Publishing the fluent version.** It is confident and it names a person.
- **Correcting the timeline before showing it.** The uncorrected view is what
  everyone else is looking at.
- **Softening unsupported claims.** Remove them.
