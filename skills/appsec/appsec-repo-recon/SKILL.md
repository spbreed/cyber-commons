---
name: appsec-repo-recon
description: >-
  Build the structural and historical map of a codebase before any security
  analysis. Use at the start of an application security review, when asked to
  find entry points, sinks, trust boundaries or attack surface, when triaging
  which files deserve attention, or when a later stage needs an architecture
  map it does not have.
allowed-tools: Read, Grep, Glob, Bash
---

# AppSec pipeline · Phase 1 — Ingestion and structural mapping

Covers **stages 1–4**. Produces the map every later stage reads. Nothing in
this phase decides whether the code is vulnerable — it decides *where to look*.

Most review starts at the diff, which is the smallest context available and
discards the best predictor there is: the repository has already recorded where
it breaks.

## When to use this

Load this skill first in any review of a codebase you have not mapped. If a
threat model, audit or report is requested and no `architecture_map` exists,
build one here rather than guessing from file names.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Repository worktree | yes | read-only is sufficient |
| Commit history | preferred | degraded mode without it; say so in `caveats` |
| Issue/PR history | optional | improves stage 1 only |

## Procedure

**Stage 1 — Historical parsing.** Extract prior vulnerabilities, the commits
that fixed them, and their files. Security fixes cluster: a file patched for a
vulnerability once is materially more likely to hold another. Record a
`fix_count` per file. Never treat absence of history as evidence of safety —
it is usually evidence of a young file or a squashed import.

**Stage 2 — Structural indexing.** Enumerate units (functions, methods,
handlers) with file, line, parameters, and the calls each one makes. This is
the index every later stage joins against, so record identity as
`(file, unit)` — never a bare basename. Two `handler.py` files in different
directories are two different units, and collapsing them silently merges their
findings.

**Stage 3 — Component summarisation.** For each unit, record what it *touches*:
network, filesystem, database, subprocess, credentials, deserialisation. A unit
that touches none of these cannot be a sink, and excluding it early is the
cheapest correct filter in the pipeline.

**Stage 4 — Architecture synthesis.** Join the above into:
- **entry points** — units reachable from outside the trust boundary
- **sinks** — units that touch a dangerous resource
- **flows** — the call edges connecting them
- **trust boundaries** — the edges where the caller's trust level drops

Then compute reachability: for every entry point, which sinks can it reach.
An unreachable sink is not an attack surface, and a reachable one is the whole
list for Phase 2.

## Output contract

Emit exactly this shape. Later phases join on these keys.

```json
{
  "architecture_map": {
    "entry_points": [{"unit": "str", "file": "str", "line": 0, "exposure": "public|authenticated|internal"}],
    "sinks":        [{"unit": "str", "file": "str", "resource": "network|filesystem|database|subprocess|credential|deserialisation"}],
    "flows":        [["caller_unit", "callee_unit"]],
    "boundaries":   [{"edge": "a → b", "from_trust": 0, "to_trust": 0}],
    "reachable":    [{"entry": "str", "sink": "str", "path": ["unit", "..."]}],
    "hotspots":     [{"file": "str", "fix_count": 0}],
    "caveats":      ["str"]
  }
}
```

Order every list deterministically — sort by a full key, never rely on set or
dict iteration order. Two runs of this skill over the same commit must produce
byte-identical output, or the diff between two scans is meaningless.

## Failure modes

- **Reporting a sink with no path from an entry point.** That is a code smell,
  not an attack surface. Keep it out of `reachable`.
- **Matching paths by basename.** Match on parent directory plus filename tail.
- **Claiming completeness.** If the index skipped a language, generated code,
  or a vendored tree, list it in `caveats`. A silently partial map is worse
  than a small one, because the next stage cannot tell.

## Handoff

Pass `architecture_map` to **appsec-threat-model**. If `reachable` is empty,
stop and report that — do not proceed to threat modelling on an empty surface.
