---
name: run-replayability-audit
description: >-
  Check whether an incident run can be replayed at all — model version, seed,
  prompt, tool results, retrieved context — and what a later model version does
  to the replay. Use when forensics needs to know why the agent did what it did.
allowed-tools: Read, Grep, Glob
---

# Replay needs five things and production records three

"Why did the agent do that" is answerable only if the run can be re-run under the
conditions it ran in. That needs the model version, the sampling parameters and
seed, the exact prompt, every tool result and the retrieved context. A typical
production run records enough to see what happened and not enough to reproduce
it.

## When to use this

Before an incident, as a readiness check, and during one, to establish honestly
whether the reconstruction is possible.

## Procedure

**1 — List the five inputs and check each against a real run record.** Model
version and seed are the two usually missing, and their absence is decisive
rather than inconvenient.

**2 — Attempt the replay.** If any input is missing, say what the replay can and
cannot establish. A partial replay is still useful for the tool path and useless
for the reasoning.

**3 — Replay under later model versions.** The provider has probably upgraded.
Record whether the action changes: if it does, the original decision cannot be
reproduced at all, and that is a finding about the estate rather than about the
incident.

**4 — Cost full instrumentation.** Storage and latency for recording everything,
against the incidents where you needed it. Present both; the answer is usually to
instrument the high-tier agents only, and that is a defensible decision when the
numbers are attached.

**5 — Record what the estate has chosen.** Which agents are replayable and which
are not, so nobody assumes during an incident.

## Output contract

```json
{
  "inputs": [{"name": "str", "recorded": false}],
  "replay": {"possible": false, "establishes": ["str"], "cannot_establish": ["str"]},
  "version_drift": [{"version": "str", "action": "str", "same_as_original": false}],
  "cost": {"storage_per_run": "str", "latency_ms": 0},
  "policy": [{"tier": "str", "fully_instrumented": true}]
}
```

## Failure modes

- **Assuming replay is possible.** Check the record before promising it.
- **Replaying on the current model.** It is not the one that acted.
- **Instrumenting everything or nothing.** Tier it and write the choice down.
