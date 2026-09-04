#!/usr/bin/env python3
"""Run the disclosure clock from each candidate awareness point and find which scoping delays miss the deadline.

This is the executable half of the `regulatory-clock-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time

def clock(awareness, containment, report, deadline_hours=72):
    to_contain = (containment - awareness) / 3600
    to_report  = (report - awareness) / 3600
    return {"hours_to_containment": round(to_contain, 1),
            "hours_to_report": round(to_report, 1),
            "deadline": deadline_hours,
            "met": to_report <= deadline_hours,
            "margin": round(deadline_hours - to_report, 1)}

t0 = time.time()
H = 3600
SCENARIOS = {
 "fast containment, slow scoping": (t0 + 1*H,  t0 + 80*H),
 "slow containment, fast reporting": (t0 + 40*H, t0 + 60*H),
 "both fast":                      (t0 + 2*H,  t0 + 20*H),
 "attribution broken (D2.1)":      (t0 + 6*H,  t0 + 92*H),
}
print(f"{'scenario':34s}{'contain':>9}{'report':>9}{'met':>6}{'margin':>9}")
print("-" * 68)
for name, (c, r) in SCENARIOS.items():
    k = clock(t0, c, r)
    print(f"{name:34s}{k['hours_to_containment']:>9.1f}{k['hours_to_report']:>9.1f}"
          f"{str(k['met']):>6}{k['margin']:>9.1f}")
print("\nThe first row contained in ONE HOUR and still missed the deadline.")

TIMELINE = [
 ("alert fires",                          0,  False),
 ("analyst triages, suspects an incident", 3, True),   # ← awareness, arguably
 ("IR lead confirms an incident",         9,  True),
 ("scope established",                    40, True),
 ("legal confirms it is reportable",      55, True),
]
print(f"{'event':40s}{'t+h':>6}  could a regulator call this awareness?")
print("-" * 84)
for name, h, aware in TIMELINE:
    print(f"{name:40s}{h:>6}  {aware}")

report_at = 76
for label, start_h in (("clock from analyst suspicion", 3),
                       ("clock from IR confirmation", 9),
                       ("clock from legal determination", 55)):
    hours = report_at - start_h
    print(f"\n{label:34s} elapsed {hours:>3}h  "
          f"{'MET' if hours <= 72 else 'MISSED'} (72h deadline)")
print("\nThe same incident, the same report time, three different answers.")
print("Pick the earliest defensible start. A regulator will.")

OBLIGATIONS = {
 "GDPR (personal data breach)":     (72,  "supervisory authority"),
 "DORA (major ICT incident)":       (4,   "initial notification"),
 "NIS2 (early warning)":            (24,  "CSIRT"),
 "PCI DSS (card data)":             (24,  "acquirer/brands"),
 "contractual (major client)":      (12,  "client security contact"),
}
print(f"{'obligation':36s}{'deadline (h)':>14}  notify")
print("-" * 76)
for name, (hours, who) in sorted(OBLIGATIONS.items(), key=lambda kv: kv[1][0]):
    print(f"{name:36s}{hours:>14}  {who}")
shortest = min(OBLIGATIONS.items(), key=lambda kv: kv[1][0])
print(f"\nyour real deadline is the shortest: {shortest[0]} at {shortest[1][0]}h")

def runbook_check(containment_owner, disclosure_owner, clock_starts_at):
    problems = []
    if containment_owner == disclosure_owner:
        problems.append("one owner for both workstreams — they compete for the "
                        "same person under time pressure")
    if clock_starts_at != "awareness":
        problems.append(f"clock starts at {clock_starts_at!r}, not at awareness — "
                        f"a regulator will use the earlier point")
    return (not problems), problems

for label, args in (("as usually written", ("IR lead", "IR lead", "confirmation")),
                    ("corrected", ("IR lead", "legal/compliance lead", "awareness"))):
    ok, problems = runbook_check(*args)
    print(f"\n{label}: sound={ok}")
    for p in problems: print(f"   ⚠ {p}")
assert runbook_check("IR lead", "legal/compliance lead", "awareness")[0]
