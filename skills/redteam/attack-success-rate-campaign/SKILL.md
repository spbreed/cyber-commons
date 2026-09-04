---
name: attack-success-rate-campaign
description: >-
  Measure attack success rate for a defence across a case suite, with false
  alarms on benign cases and a bypass delivered through the channel the defence
  trusts. Use when comparing defences, or when a filter's block rate is being
  reported as its effectiveness.
allowed-tools: Read, Grep, Glob
---

# A block rate with no false-alarm rate is half a measurement

Attack success rate is comparable only when the suite is fixed and the benign
cases are run too. A keyword filter looks respectable on ASR and blocks people
writing about security; a provenance control takes ASR to zero and has no false
alarms — until the payload arrives through the channel it trusts.

## When to use this

Comparing defences, accepting a vendor's block rate, or before a control goes in
front of users who write about security for a living.

## Procedure

**1 — Fix the suite before you measure anything.** Attack cases by surface, and
benign cases that look like attacks — a security engineer's own writing, an
incident report quoting a payload. Changing the suite between defences makes the
numbers incomparable, and it is the most common way this is done wrong.

**2 — Run each defence over the whole suite.** Record ASR per surface, not just
overall: a defence that closes injection and does nothing for identity has an
overall number that hides both facts.

**3 — Record false alarms separately.** They are the cost side. A defence with
ASR 0.67 and 2 false alarms in 4 benign cases is not a trade-off anyone would
take if the second number were reported.

**4 — Attack the assumption, not just the defence.** For provenance, deliver the
payload through the principal channel — the one the control trusts by
construction. Every defence has one, and finding it is the point of the
campaign.

**5 — Report the bypass as a property of the design.** "Provenance holds unless
the payload comes from the principal" is the honest claim, and it tells you the
next control rather than discrediting this one.

## Output contract

```json
{
  "suite": {"attack_cases": 0, "benign_cases": 0, "surfaces": ["str"], "frozen": true},
  "defences": [{"name": "str", "asr_overall": 0.0, "asr_by_surface": {"str": 0.0},
                "false_alarms": 0}],
  "bypass": {"defence": "str", "channel": "str", "asr_after": 0.0},
  "claim": "str"
}
```

## Failure modes

- **Changing the suite per defence.** The numbers stop being comparable.
- **Reporting ASR without false alarms.** The cost side is missing.
- **Treating a bypass as a refutation.** It is the boundary of the claim.
