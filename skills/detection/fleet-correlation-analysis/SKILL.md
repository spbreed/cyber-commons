---
name: fleet-correlation-analysis
description: >-
  Correlate across agent runs that each pass every per-run check, and find the
  shared artefacts, novel tokens and repeated trajectories that are only visible
  at fleet level. Use when every run looks clean and something is still wrong.
allowed-tools: Read, Grep, Glob
---

# Every run is clean; the fleet is not

Per-run checks are the wrong altitude for a coordinated problem. Five runs each
pass everything, and the object one of them wrote is read by three unrelated
others; three of them coin the same novel token; four of five converge on the
same trajectory nobody designed. None of that is visible from inside a run.

## When to use this

Any estate running many agents, and specifically when per-run monitoring reports
nothing and behaviour is still surprising.

## Procedure

**1 — Confirm the per-run checks pass.** Establish the baseline explicitly:
these runs individually have nothing to report. Otherwise the fleet finding
looks like a per-run finding that was missed.

**2 — Build the shared-artefact graph.** Objects written by one run and read by
another, keyed by object rather than by run. An object with one writer and
several unrelated readers is the shape to look for.

**3 — Find novel tokens shared across runs.** Strings that appear in several
runs and in no baseline corpus. Independent runs do not coin the same identifier
by accident.

**4 — Cluster trajectories.** Sequences of tool calls, compared across runs. A
cluster nobody designed is either an emergent shortcut or a shared influence,
and both need explaining.

**5 — Report at fleet level with the runs attached.** The finding is the
pattern; the runs are the evidence. A report that lists runs without the pattern
is the per-run view again.

## Output contract

```json
{
  "per_run": [{"run": "str", "checks_passed": true, "findings": 0}],
  "shared_artefacts": [{"object": "str", "written_by": "str", "read_by": ["str"], "unrelated": true}],
  "novel_tokens": [{"token": "str", "runs": ["str"], "in_baseline": false}],
  "trajectory_clusters": [{"pattern": ["str"], "runs": ["str"], "designed": false}],
  "fleet_findings": [{"pattern": "str", "evidence_runs": ["str"]}]
}
```

## Failure modes

- **Aggregating per-run alerts.** Zero plus zero is still zero.
- **Keying the graph by run.** Key it by object or the sharing is invisible.
- **Explaining a shared token as coincidence.** Check the corpus before
  accepting that.
