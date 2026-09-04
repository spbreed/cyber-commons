---
name: generated-code-reach-enumerator
description: >-
  Enumerate what model-authored code can read, write and connect to when it
  executes — on an ordinary task and on a steered one — including process
  environment, filesystem and cloud metadata. Use when an agent runs code it
  wrote, or when sizing the runtime that code should execute in.
allowed-tools: Read, Grep, Glob, Bash
---

# The reach is the same whether the code was steered or not

An agent that executes its own code has the process's reach, not the task's.
The interesting measurement is that an **ordinary, unattacked** task already
touches everything the process can see; steering only changes what it does with
that reach, not how much of it there is.

## When to use this

Any agent with a code-execution tool, a notebook runner, a build step it
authors, or a shell. Run it before choosing a sandbox, because the output is
the requirement list for one.

## Procedure

**1 — Inventory the process environment.** Every variable visible to the
executing process. Credentials in the environment are reachable by any line of
code, and the agent did not have to look for them.

**2 — Inventory filesystem reach.** What the process can open, not what the
task needs. Include the agent's own configuration, adjacent workspaces, and any
key material mounted for another purpose.

**3 — Inventory network reach.** Resolve and attempt each destination the
process can open. The cloud metadata address is the one that turns a code
execution into a credential theft; test it explicitly.

**4 — Run the benign task and record what it touched.** This is the number that
changes the conversation: an ordinary task with no adversary reaching a private
key is a design fact, not an incident.

**5 — Run the steered task and diff.** The difference between the two is what
an attacker gains. It is usually smaller than people expect, because the
ordinary run already had everything.

## Output contract

```json
{
  "environment": {"variables": ["str"], "credential_shaped": ["str"]},
  "filesystem": {"readable": ["str"], "sensitive": ["str"]},
  "network": {"reachable": ["str"], "metadata_endpoint": true},
  "benign_run": {"touched": ["str"]},
  "steered_run": {"touched": ["str"], "gain_over_benign": ["str"]},
  "sandbox_requirements": ["str"]
}
```

## Failure modes

- **Measuring the task instead of the process.** The task is a suggestion; the
  process boundary is the control.
- **Skipping the metadata endpoint** because it is not in the code. It does not
  need to be.
- **Reporting only the steered run.** The benign run is the more persuasive
  half of the finding.
