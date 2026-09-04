---
name: control-to-framework-mapping
description: >-
  Map a control catalogue outward to framework clauses — never the reverse — and
  assemble the evidence pack a given risk tier requires. Use when a framework
  checklist is being turned into a programme, or when coverage is claimed
  without artefacts.
allowed-tools: Read, Grep, Glob
---

# Control to framework, never framework to control

Starting from the framework produces a checklist that is complete, satisfies an
assessor, and defends nothing: it enumerates clauses rather than capabilities,
and a clause with no operating control behind it evidences nothing. Starting
from controls produces a smaller list of things you actually do, each of which
happens to satisfy several clauses.

## When to use this

Building a control catalogue, responding to a framework mapping request, or
auditing a coverage claim.

## Procedure

**1 — Write the catalogue first, as operating controls.** Each one a mechanism
somebody runs, with an owner. If a row cannot be described as something that
runs, it is a policy statement and belongs elsewhere.

**2 — Map each control outward.** One control to many clauses across every
framework you report against. The one-to-many direction is what makes this
cheaper than it looks.

**3 — Attach the evidence artefact per control.** A log, an export, a test
result, a signed attestation — the thing an assessor would be handed. A control
with no artefact is unevidenced whatever its status says.

**4 — Derive requirements per tier.** Which controls a critical-tier system must
have, which a medium one. Then count the clauses that follow, rather than
promising clause coverage directly.

**5 — Report coverage as an output.** "These 8 controls satisfy 12 clauses" is
defensible; "we cover 12 clauses" invites the follow-up you cannot answer.

## Output contract

```json
{
  "catalogue": [{"id": "str", "control": "str", "owner": "str", "artefact": "str"}],
  "mapping": [{"control": "str", "framework": "str", "clauses": ["str"]}],
  "tiers": [{"tier": "str", "requires": ["str"], "clauses_satisfied": 0}],
  "coverage": {"controls": 0, "clauses": 0, "unevidenced": ["str"]}
}
```

## Failure modes

- **Starting from the framework.** You get a checklist, not a programme.
- **A control with no artefact.** It cannot be shown.
- **Claiming clause coverage directly.** The assessor asks which control, and
  there is no answer.
