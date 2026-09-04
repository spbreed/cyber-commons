#!/usr/bin/env python3
"""Compare a build order that produces coverage against one that produces demos, quarter by quarter.

This is the executable half of the `capability-build-order` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
now = time.time(); DAY = 86400
REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]

QUARTERS = {
 "Q1 · inventory + identity": ["AC-1","AC-2"],
 "Q2 · containment":          ["AC-1","AC-2","SB-1","SB-2"],
 "Q3 · evidence + evaluation":["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2"],
 "Q4 · continuous + stop":    REQUIRED,
}
DEMOABLE = {"AC-1": False, "AC-2": False, "SB-1": False, "SB-2": False,
            "EV-1": False, "EV-2": True, "DR-1": True, "ST-1": True}

print(f"{'quarter':30s}{'coverage':>10}{'demoable':>11}")
print("-" * 54)
for q, done in QUARTERS.items():
    cov = len(done)/len(REQUIRED)
    demo = sum(1 for c in done if DEMOABLE[c])
    print(f"{q:30s}{cov:>10.0%}{demo:>11}")
print("\nQ1 and Q2 produce nothing demoable. That is the political problem, and")
print("it is why the inverted order keeps getting chosen.")

INVERTED = {
 "Q1 · evaluation + dashboard": ["EV-2","DR-1"],
 "Q2 · more evaluation":        ["EV-2","DR-1"],
 "Q3 · identity (finally)":     ["EV-2","DR-1","AC-1","AC-2"],
 "Q4 · containment":            ["EV-2","DR-1","AC-1","AC-2","SB-1","SB-2"],
}
CAPABILITY_AT = {
 "can revoke one agent":            {"AC-1"},
 "can attribute an action":         {"AC-1","EV-1"},
 "can bound a compromised agent":   {"SB-1","SB-2"},
 "can halt the fleet":              {"ST-1"},
 "can defend an accuracy number":   {"EV-2"},
}
def capabilities(done):
    return [c for c, need in CAPABILITY_AT.items() if need <= set(done)]

print(f"{'quarter':30s}{'coverage':>10}  capabilities")
print("-" * 90)
for q, done in INVERTED.items():
    print(f"{q:30s}{len(done)/len(REQUIRED):>10.0%}  {capabilities(done) or '—'}")

end_inverted = capabilities(INVERTED["Q4 · containment"])
end_correct  = capabilities(QUARTERS["Q4 · continuous + stop"])
print(f"\nafter four quarters:")
print(f"   inverted order: {len(end_inverted)} capabilities  {end_inverted}")
print(f"   correct order : {len(end_correct)} capabilities")
print("\nThe inverted programme spent a year and still cannot halt the fleet.")
assert len(end_correct) > len(end_inverted)

ROLES = {
 "harness engineer":   ("B2", {"EV-2"},                 "loop, verifier, eval"),
 "identity engineer":  ("A2", {"AC-1","AC-2","EV-1"},   "identity, delegation, act chains"),
 "detection engineer": ("D1", {"DR-1"},                 "agent telemetry and drift"),
 "GRC practitioner":   ("E1", {"SB-2","ST-1"},          "tiering, evidence, verification"),
}
def unblocks(role):
    delivered = ROLES[role][1]
    return [c for c, need in CAPABILITY_AT.items() if need & delivered]

print(f"{'role':22s}{'track':7s}{'controls':28s}unblocks")
print("-" * 92)
for role, (track, controls, what) in sorted(
        ROLES.items(), key=lambda kv: -len(unblocks(kv[0]))):
    print(f"{role:22s}{track:7s}{str(sorted(controls)):28s}{unblocks(role)}")

first = max(ROLES, key=lambda r: len(unblocks(r)))
print(f"\nhire first (unblocks the most): {first}")
print(f"hired first most often        : harness engineer")
assert first == "identity engineer"

print("\nplan that survives contact:")
for q, hire, deliver in [
 ("Q1", "identity engineer", "inventory + agent identities (AC-1, AC-2)"),
 ("Q2", "GRC practitioner",  "containment + tiering (SB-1, SB-2)"),
 ("Q3", "harness engineer",  "evidence + held-out evaluation (EV-1, EV-2)"),
 ("Q4", "detection engineer","drift + tested stop (DR-1, ST-1)"),
]:
    print(f"   {q}  hire {hire:20s}deliver {deliver}")
