---
name: blast-radius-review
description: >-
  Compute what an agent can reach and damage in a single run, and decide the
  autonomy level its blast radius can support. Use when reviewing an agent
  design or deployment, deciding whether an action needs human approval, sizing
  a sandbox, or answering how bad it would be if an agent were fully
  compromised.
allowed-tools: Read, Grep, Glob
---

# Blast radius as a design metric

Blast radius is not an adjective. It is the set of resources an agent can
change before anyone can stop it, and it is **computed** from three inputs:

```
blast_radius = reachable_resources × action_irreversibility × time_to_human_stop
```

Treating it as a number is what lets it be a design constraint instead of a
discussion.

## When to use this

At design review, before raising an agent's autonomy, and after any change that
adds a tool, a credential, or a scheduled trigger.

## Procedure

**1 — Enumerate reachable resources.** For each tool the agent can call, list
what it can touch with attacker-chosen arguments — not what it touches in the
happy path. A `Bash` tool with unrestricted arguments reaches everything the
process can reach; record it that way rather than as one row.

**2 — Grade irreversibility.** Per action:

| Grade | Meaning | Example |
|---|---|---|
| 0 | read-only | query, list |
| 1 | reversible with effort | write a file, open a PR |
| 2 | reversible only with a backup | delete a row, force-push |
| 3 | irreversible or externally visible | send an email, pay, publish, rotate a key |

Grade 3 actions are the whole reason approval gates exist. An agent whose
worst action is grade 0 does not need one.

**3 — Measure time-to-human-stop.** How long between the agent deciding and a
human being able to intervene? Interactive with a prompt is seconds. A
scheduled run at 03:00 with notifications off is hours. This term dominates the
product more often than people expect, and it is usually the cheapest to fix.

**4 — Place it on the autonomy ladder.**

| Level | Meaning | Requires |
|---|---|---|
| L1 | suggests; human executes | nothing |
| L2 | acts within a bounded sandbox | reversible actions only |
| L2.5 | acts, but grade-3 actions need approval | a working approval path |
| L3 | acts unattended | demonstrated containment + audit + stop authority |

An agent at L3 whose grade-3 actions are unbounded is misclassified, not brave.

**5 — Find the cheapest reduction.** Usually one of: remove a credential from
the environment, split one broad tool into two narrow ones, add a choke point
in front of the irreversible action, or shorten time-to-stop with a
notification. Recommend the one with the best radius reduction per unit of
friction, and say what it costs.

## Example

**Input** — the fixture committed at the top of [`scripts/blast_radius_review.py`](scripts/blast_radius_review.py). Edit it and re-run: the buckets, counts and verdicts below are derived from it, not hard-coded.

**Output** — the opening lines of a real run:

```
action              reversible  external  routing         per day
delete_row          False       False     human approval  6
issue_refund        False       True      human approval  2
read_report         True        False     policy only     400
rotate_credential   False       False     human approval  1
send_email          False       True      human approval  3
update_ticket       True        False     policy only     260
write_draft         True        False     policy only     120
```

The run continues past this. The script is the example: `test_skills.py` executes it on every build, so this block cannot drift from what the skill actually prints.

## Output contract

```json
{
  "resources": [{"tool": "str", "reachable": ["str"], "unbounded": false}],
  "actions": [{"action": "str", "irreversibility": 0, "why": "str"}],
  "time_to_human_stop_seconds": 0,
  "blast_radius": {"score": 0, "inputs": {"resources": 0, "max_irreversibility": 0, "seconds": 0}},
  "autonomy": {"current": "L1|L2|L2.5|L3", "supported": "L1|L2|L2.5|L3", "mismatch": false},
  "reductions": [{"change": "str", "new_score": 0, "friction": "low|medium|high"}]
}
```

Show `inputs`. A blast-radius score without its terms cannot be challenged, and
an unchallengeable metric stops being used.

## Failure modes

- **Counting the happy path.** Enumerate with attacker-chosen arguments.
- **Ignoring time-to-stop** because it is not about permissions. It is the term
  that separates an incident from a near miss.
- **Raising autonomy because the agent has been reliable.** Reliability is not
  containment; it is the absence of an adversary so far.
