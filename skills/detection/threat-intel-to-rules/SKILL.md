---
name: threat-intel-to-rules
description: >-
  Convert a threat-intel feed into detection rules, drop the indicators that
  cannot be matched or scored, and report the three numbers that say whether the
  feed earns its price. Use when subscribing to intel, or when a feed produces
  alerts nobody actions.
allowed-tools: Read, Grep, Glob
---

# Most of a feed is not matchable, and that is fine if you say so

An intel feed contains indicators, narratives and low-confidence guesses. Only
some of it converts into something a detection can match on. The useful output
is a small number of rules plus an explicit list of what was dropped and why —
and three numbers that tell you whether to renew.

## When to use this

On any intel feed, at subscription and at renewal, and when an intel-derived
rule fires and nobody knows what to do.

## Procedure

**1 — Set a confidence floor and a matchable-type list.** Hosts, hashes,
techniques. Narratives are context, not indicators; write the floor down before
reading the feed.

**2 — Convert what qualifies.** One rule per indicator, with the response
attached. An indicator with no response is not ready — the analyst will get the
alert and ask what to do.

**3 — Drop the rest with reasons.** "Narrative, not matchable" and "confidence
0.4, below floor" are both fine. An undocumented drop is indistinguishable from
an oversight.

**4 — Run the rules against real events.** Record which fired and what the
response was. A rule that has never fired is not automatically bad; a rule that
fires and produces no action is.

**5 — Report the three numbers.** Indicators converted, alerts produced, alerts
actioned. The ratio of the third to the second is what the feed is worth, and it
is the number to take to a renewal conversation.

## Example

**Input** — the fixture committed at the top of [`scripts/threat_intel_to_rules.py`](scripts/threat_intel_to_rules.py). Edit it and re-run: the buckets, counts and verdicts below are derived from it, not hard-coded.

**Output** — the opening lines of a real run:

```
indicator                                     kind         conf  verdict
----------------------------------------------------------------------------------------
collect.example.com                           host         0.95  RULE — convertible to a rule
169.254.169.254                               host         0.99  RULE — convertible to a rule
a1b2c3d4e5f6                                  hash         0.72  RULE — convertible to a rule
pastebin.example                              host         0.55  drop — confidence 0.55 below floor 0.7
adversaries increasingly use agentic tooling  narrative    0.40  drop — narrative is not matchable in telemetry
agents reading ~/.aws/credentials             technique    0.88  RULE — convertible to a rule
```

The run continues past this. The script is the example: `test_skills.py` executes it on every build, so this block cannot drift from what the skill actually prints.

## Output contract

```json
{
  "feed": {"indicators": 0, "confidence_floor": 0.0, "matchable_types": ["str"]},
  "rules": [{"indicator": "str", "type": "str", "response": "str"}],
  "dropped": [{"indicator": "str", "reason": "str"}],
  "firings": [{"rule": "str", "events": 0}],
  "value": {"converted": 0, "alerts": 0, "actioned": 0}
}
```

## Failure modes

- **Converting narratives.** They do not match on anything.
- **Rules with no response.** The alert lands and stops.
- **Reporting alerts rather than actions.** Alerts are cheap to produce.
