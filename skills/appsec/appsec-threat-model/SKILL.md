---
name: appsec-threat-model
description: >-
  Turn an architecture map into a ranked, testable threat model and an audit
  plan. Use after repository reconnaissance, when asked what could go wrong in
  a system, which CWEs apply, where to spend review effort, or how to allocate
  a fixed analysis budget across a codebase.
allowed-tools: Read, Grep, Glob
---

# AppSec pipeline · Phase 2 — Threat modelling and strategy

Covers **stages 5–6**. Consumes `architecture_map` from **appsec-repo-recon**
and produces a ranked threat list plus the plan that spends the audit budget.

A threat model that lists everything is a list, not a model. The output of this
phase is an *ordering*: what to look at first, and what to knowingly skip.

## When to use this

After Phase 1, before any auditing. If asked to "threat model" a system with no
architecture map, run **appsec-repo-recon** first — a threat model built from
file names is fiction.

## Inputs

| Input | Required | Notes |
|---|---|---|
| `architecture_map` | yes | from appsec-repo-recon |
| Audit budget | yes | units of analysis you can actually afford |
| Deployment context | optional | internet-facing vs internal changes exposure |

## Procedure

**Stage 5 — Threat modelling.** For every `reachable` entry→sink pair, ask what
an attacker controlling the entry can do to the sink. Record a threat with:

- the **CWE** it would be, concretely (CWE-89, CWE-22, CWE-78, CWE-502, …)
- the **entry** and **sink** identities, and the path between them
- whether the path crosses a **trust boundary**
- the **authentication** required to reach the entry
- a **score**, computed — never asserted

Score from properties you already have, so the number is reproducible:

```
score = exposure_weight(entry)      # public 3, authenticated 2, internal 1
      × resource_weight(sink)       # subprocess/deserialisation 3, db/fs 2, network 1
      × boundary_multiplier         # 2 if the path crosses a trust boundary
```

A model that outputs a severity without showing the inputs cannot be argued
with, and an unarguable severity is one nobody fixes.

**Stage 6 — Strategic planning.** Spend the budget. Rank threats by score, then
by a **full tiebreak** — `(-score, cwe, entry, sink)` — so equal scores order
identically on every machine. Then allocate:

- Cover the highest-scoring threats first.
- Prefer **breadth across distinct CWEs** over depth on one: three different
  weakness classes found beats three instances of the same one.
- Record what the budget did **not** cover, in `deferred`. An audit plan that
  hides its own gaps produces a report that overclaims.

## Output contract

```json
{
  "threat_model": [
    {"cwe": "CWE-89", "entry": "str", "sink": "str", "path": ["unit"],
     "crosses_boundary": true, "auth": "none|user|admin",
     "score": 0, "score_inputs": {"exposure": 0, "resource": 0, "boundary": 0}}
  ],
  "plan": {
    "budget": 0,
    "selected": [{"threat_index": 0, "cost": 0, "why": "str"}],
    "deferred": [{"threat_index": 0, "why": "str"}],
    "coverage": {"threat_weighted": 0.0, "distinct_cwes": 0}
  }
}
```

`score_inputs` is not optional. It is what makes the ranking reviewable.

## Failure modes

- **Scoring by vibes.** If you cannot show the multiplication, do not emit the
  score.
- **A budget that covers everything.** Then the plan proves nothing — the
  interesting behaviour of an allocator only appears under scarcity. If the
  budget genuinely covers all targets, say so rather than claiming a strategy
  worked.
- **Ranking instability.** Equal scores must not reorder between runs. Sort
  keys first; never iterate a set into a stable sort.
- **Treating "no auth" as the only risk.** An authenticated path to a
  subprocess sink usually outranks an anonymous path to a read-only one.

## Handoff

Pass `threat_model` and `plan.selected` to **appsec-vuln-audit**. Carry
`deferred` all the way to the report — it is the honest scope statement.
