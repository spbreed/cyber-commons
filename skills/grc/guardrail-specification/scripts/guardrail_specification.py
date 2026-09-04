#!/usr/bin/env python3
"""Separate operating guardrails from outcome guardrails and specify the measurement each outcome one needs before it can be enforced.

This is the executable half of the `guardrail-specification` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

def classify(rule, constrains_outcome, measurement_exists):
    kind = "outcome" if constrains_outcome else "operating"
    if kind == "operating":
        return {"rule": rule, "kind": kind, "enforceable_today": True,
                "risk": "may satisfy audit while missing real harm"}
    return {"rule": rule, "kind": kind, "enforceable_today": measurement_exists,
            "risk": ("enforceable" if measurement_exists
                     else "needs an agreed measurement before it can be enforced")}

RULES = [
 ("all agent egress goes through the gateway", False, True),
 ("privileged tools require approval below L3", False, True),
 ("every action is logged with the acting identity", False, True),
 ("agent identities are separately revocable", False, True),
 ("no agent action causes unrecoverable customer data loss", True, False),
 ("automated remediation does not increase customer-facing incidents", True, True),
 ("model outputs do not produce disparate outcomes across segments", True, False),
]
print(f"{'rule':60s}{'kind':11s}{'enforceable':>12}")
print("-" * 86)
for rule, outcome, measurable in RULES:
    c = classify(rule, outcome, measurable)
    print(f"{c['rule']:60s}{c['kind']:11s}{str(c['enforceable_today']):>12}")

operating = [r for r in RULES if not r[1]]
outcome   = [r for r in RULES if r[1]]
enforceable_outcome = [r for r in outcome if r[2]]

print(f"operating guardrails : {len(operating)}  all enforceable today")
print(f"outcome guardrails   : {len(outcome)}  of which enforceable: "
      f"{len(enforceable_outcome)}")

naive = len(operating) / len(RULES)
honest = (len(operating) + len(enforceable_outcome)) / len(RULES)
print(f"\n'guardrail coverage' if you count only what you shipped: "
      f"{len(operating)}/{len(operating)} = 100%")
print(f"coverage across ALL agreed guardrails: "
      f"{len(operating)+len(enforceable_outcome)}/{len(RULES)} = {honest:.0%}")
print("\nThe first number is what usually reaches a steering committee.")

def specify_outcome_guardrail(rule, metric, threshold, source, cadence):
    complete = all([metric, threshold is not None, source, cadence])
    return {"rule": rule, "metric": metric, "threshold": threshold,
            "source": source, "cadence": cadence,
            "status": "enforceable" if complete else "ASPIRATION — label it as such"}

SPECS = [
 specify_outcome_guardrail(
   "automated remediation does not increase customer-facing incidents",
   metric="customer-facing SEV1+SEV2 per 1000 remediations",
   threshold=1.2, source="incident management system", cadence="monthly"),
 specify_outcome_guardrail(
   "no agent action causes unrecoverable customer data loss",
   metric="", threshold=None, source="", cadence=""),
]
for s in SPECS:
    print(f"{s['rule']}")
    print(f"   metric   {s['metric'] or '—'}")
    print(f"   threshold {s['threshold'] if s['threshold'] is not None else '—'}")
    print(f"   source   {s['source'] or '—'}")
    print(f"   status   {s['status']}\n")

def programme_statement(rules, specs):
    enforceable = len([r for r in rules if not r[1]]) + \
                  len([s for s in specs if s["status"] == "enforceable"])
    aspirations = [s["rule"] for s in specs if s["status"] != "enforceable"]
    return (f"{enforceable}/{len(rules)} guardrails are enforceable today.\n"
            f"The following are agreed but UNMEASURED, and are not counted as "
            f"coverage:\n" + "\n".join(f"   - {a}" for a in aspirations))
print(programme_statement(RULES, SPECS))
assert any(s["status"] != "enforceable" for s in SPECS)
