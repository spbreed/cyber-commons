---
name: guardrail-specification
description: >-
  Separate operating guardrails, which are enforceable today, from outcome
  guardrails, which need a measurement before they mean anything — and specify
  that measurement. Use when a policy contains a rule nobody can enforce.
allowed-tools: Read, Grep, Glob
---

# An outcome guardrail with no measurement is a wish

Operating guardrails constrain what the system may do: which tools, which data,
which actions need approval. They are enforceable today. Outcome guardrails
constrain what the system may cause — no discriminatory decisions, no
misleading advice — and they are enforceable only where somebody has specified
the measurement.

## When to use this

Writing an AI policy, reviewing one, or explaining why a coverage figure of 100%
is counting only the rules that shipped.

## Procedure

**1 — Classify every rule.** Does it constrain the system's behaviour, or the
outcome of that behaviour? The test is whether it can be checked at the moment
of action.

**2 — For each operating guardrail, name the enforcement point.** The gateway,
the tool policy, the approval gate. If there is not one, it is aspirational and
should be reported that way.

**3 — For each outcome guardrail, specify the measurement.** The metric, the
population, the threshold, the cadence, and who reviews it. Four of those five
being present is still not a guardrail.

**4 — Count coverage both ways.** Against the rules that shipped, and against
all the rules that were agreed. The first is usually 100% and the second is
usually about half, and the gap is the honest programme statement.

**5 — Report the unmeasurable ones as open commitments** with an owner and a
date. Leaving them in the policy unmarked is how a policy stops being read.

## Example

**Input** — the fixture committed at the top of [`scripts/guardrail_specification.py`](scripts/guardrail_specification.py). Edit it and re-run: the buckets, counts and verdicts below are derived from it, not hard-coded.

**Output** — the opening lines of a real run:

```
rule                                                        kind        enforceable
--------------------------------------------------------------------------------------
all agent egress goes through the gateway                   operating          True
privileged tools require approval below L3                  operating          True
every action is logged with the acting identity             operating          True
agent identities are separately revocable                   operating          True
no agent action causes unrecoverable customer data loss     outcome           False
automated remediation does not increase customer-facing incidentsoutcome            True
```

The run continues past this. The script is the example: `test_skills.py` executes it on every build, so this block cannot drift from what the skill actually prints.

## Output contract

```json
{
  "rules": [{"text": "str", "kind": "operating|outcome",
             "enforcement_point": "str|null",
             "measurement": {"metric": "str", "population": "str", "threshold": 0.0,
                             "cadence": "str", "reviewer": "str"}}],
  "coverage": {"of_shipped": 1.0, "of_agreed": 0.0},
  "open_commitments": [{"rule": "str", "owner": "str", "due": "str"}]
}
```

## Failure modes

- **Counting only what shipped.** The number is 100% by construction.
- **An outcome guardrail with a metric and no threshold.** Nothing fails.
- **Leaving unmeasurable rules unmarked.** The policy loses credibility as a
  whole.
