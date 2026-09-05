---
name: attribution-ledger-check
description: >-
  Check that one record answers all four investigation questions — human
  principal, attested workload and run, delegation chain, and the motivating
  input with its origin — and that the agent cannot amend it. Use when
  designing agent audit records rather than reading them.
allowed-tools: Read, Grep, Glob
---

# One entry, four questions

An audit trail is not "we log tool calls". It is a record that answers, from a
single entry, the four questions an investigation asks — and that the subject of
the record cannot edit. Both halves are required: a complete record the agent
can rewrite is a record of what the agent wanted you to see.

## When to use this

While designing the record. Retrofitting attribution after an incident means
reconstructing it from four services' timestamps, which does not happen at 2am.

## Procedure

**1 — Write the four questions down first.** Which human. Which workload and
which run. Through what delegation chain. On what motivating input, from what
origin. Design the entry to answer them; do not collect fields and hope.

**2 — Map each question to a field.** Principal from the delegated token, not
from a header the agent set. Workload and instance from the attestation. Chain
from the token's `act` nesting. Motivating input from the ingress record that
caused this step, with its origin tag.

**3 — Test each question against one entry.** Alone. If answering needs a join
across services, that question is unanswered for practical purposes and should
be recorded as such.

**4 — Attempt the amendment as the agent.** Append, overwrite, delete, reorder.
Every one must be refused by something the agent does not control — an
append-only store, a separate writer identity, a downstream sink it cannot
reach.

**5 — Check the write path's own identity.** If the agent's role can write to
the log destination, the ledger is advisory whatever the API says.

## Example

**Input** — the fixture committed at the top of [`scripts/attribution_ledger_check.py`](scripts/attribution_ledger_check.py). Edit it and re-run: the buckets, counts and verdicts below are derived from it, not hard-coded.

**Output** — the opening lines of a real run:

```
   which user caused the deletion?     dana@corp
   what performed it?                  spiffe://corp/reports-agent (run-8812)
   how did authority reach it?         dana@corp -> orchestrator -> reports-agent
   what made the agent decide?         'wiki/473: retire invoice 8812 when the custo' from knowledge

questions answerable: 4/4

input origin was 'knowledge' - a trust-0 component. That single
```

The run continues past this. The script is the example: `test_skills.py` executes it on every build, so this block cannot drift from what the skill actually prints.

## Output contract

```json
{
  "entry": {"principal": "str", "workload": "str", "instance": "str",
            "chain": ["str"], "motivating_input": {"ref": "str", "origin": "str"}},
  "questions": [{"question": "str", "answered_from_single_entry": true}],
  "amendment_attempts": [{"operation": "append|overwrite|delete|reorder", "refused_by": "str"}],
  "writer_identity": {"agent_can_write_destination": false}
}
```

## Failure modes

- **A principal field the agent populates.** It is a claim, not attribution.
- **Answering a question by correlation.** Correlation is a plan, not a record.
- **Testing amendment through the API only.** Try the storage layer the agent's
  role can reach.
