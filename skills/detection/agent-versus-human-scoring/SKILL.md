---
name: agent-versus-human-scoring
description: >-
  Score actors on behavioural signals to separate agents from people, sweep the
  threshold, and pick it by expected cost rather than by accuracy. Use when
  deciding whether a session is automated, or when unregistered automation needs
  finding.
allowed-tools: Read, Grep, Glob
---

# Pick the threshold by what each mistake costs

Separating agent from human is a scoring problem with two asymmetric errors: a
flagged human costs an analyst half an hour, and a missed agent costs whatever
an unmonitored automation does. Choosing the threshold by accuracy weights those
equally, which is the one thing you know is wrong.

## When to use this

Finding unregistered automation, deciding whether a session is a person, and
before any control that treats agents differently from users.

## Procedure

**1 — Score on behaviour, not on the user agent string.** Inter-action variance,
rate, breadth, and the share of actions with no preceding read. Anything
self-declared is a claim.

**2 — Score a spread of real actors.** A service indexer, an unknown token, a
person, a person driving an IDE assistant, and an agent deliberately jittered to
look human. The last two are the interesting middle.

**3 — Sweep the threshold and record both errors.** Humans flagged and agents
missed, at each setting. They move in opposite directions and the crossing point
is not the answer.

**4 — Attach a cost to each error and minimise the total.** Analyst hours for a
false positive, expected hours of an unmonitored agent for a false negative. The
chosen threshold now has a justification somebody can argue with.

**5 — Join to the registry.** An actor scoring as an agent and absent from the
registry is the finding worth routing; a registered agent scoring as an agent is
working correctly.

## Output contract

```json
{
  "actors": [{"name": "str", "score": 0.0, "truth": "agent|human|unknown"}],
  "sweep": [{"threshold": 0.0, "humans_flagged": 0, "agents_missed": 0, "expected_cost": 0.0}],
  "costs": {"false_positive_hours": 0.0, "false_negative_hours": 0.0},
  "chosen": {"threshold": 0.0, "why": "str"},
  "registry": {"scored_agent_unregistered": ["str"]}
}
```

## Failure modes

- **Scoring the user agent string.** It is self-declared.
- **Optimising accuracy.** It assumes the two errors cost the same.
- **Flagging registered agents.** They are supposed to look like agents.
