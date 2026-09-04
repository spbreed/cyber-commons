---
name: tamper-evident-log-check
description: >-
  Reconcile an agent's own transcript against an independent host stream to find
  steps that executed something other than what was recorded, then hash-chain
  the segments and localise a rewrite. Use when the log's writer is the thing
  being investigated.
allowed-tools: Read, Grep, Glob
---

# The transcript is written by the subject of the investigation

An in-band check reads the agent's account of what it did and reports a clean
run. Spoofing is invisible to it by construction. Two independent things fix
that: a **second stream** the agent does not author, and a **chain** that makes
a later rewrite detectable and localisable.

## When to use this

Any agent whose actions matter after the fact: one that executes code, changes
infrastructure, moves money, or whose output is evidence.

## Procedure

**1 — Identify the writer of each stream.** The agent's transcript is written by
the agent. Find one stream that is not: host process accounting, container
runtime events, a syscall auditor, cloud API logs.

**2 — Reconcile step by step.** For each recorded step, does the host stream
show the action the transcript claims? Report the disagreement **rate**, not
just examples — a rate is a property of the system, an example is an anecdote.

**3 — Chain the segments.** Hash each segment together with the previous hash.
This is what turns "the log looks fine" into "any change to segment *n* is
detectable, and detectable *at* segment *n*".

**4 — Rewrite one segment and verify.** The check must fail, and it must name
the segment. A chain that detects tampering but cannot localise it sends you
back to reconciling everything.

**5 — Check what the workload's own role can reach.** If the agent's role can
write to the log store, the chain protects against an outsider and not against
the subject. Enumerate the logging plane against the role's permissions.

## Output contract

```json
{
  "streams": [{"name": "str", "written_by": "agent|host|platform"}],
  "reconciliation": {"steps": 0, "disagreements": 0, "rate": 0.0, "examples": ["str"]},
  "chain": {"segments": 0, "verifies": true},
  "rewrite_probe": {"segment": 0, "detected": true, "localised_to": 0},
  "logging_plane": {"targets": ["str"], "writable_by_workload": ["str"]}
}
```

## Failure modes

- **Reporting an in-band clean run.** It is the expected result and it means
  nothing.
- **Chaining without an independent stream.** A consistent chain of false
  entries verifies perfectly.
- **Ignoring the workload's write access to the log store.** It is the whole
  threat model of this check.
