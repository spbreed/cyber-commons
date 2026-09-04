#!/usr/bin/env python3
"""Break the disclosure clock into phases and find the one that consumes most of it.

This is the executable half of the `disclosure-phase-breakdown` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
t0 = time.time(); H = 3600

def clock(awareness, containment, report, deadline_hours):
    to_contain = (containment - awareness)/H
    to_report  = (report - awareness)/H
    return {"contain_h": round(to_contain,1), "report_h": round(to_report,1),
            "deadline": deadline_hours, "met": to_report <= deadline_hours,
            "margin_h": round(deadline_hours - to_report, 1)}

SCENARIOS = {
 "attribution sound":            (t0 + 2*H,  t0 + 20*H),
 "attribution broken, 3d scope": (t0 + 6*H,  t0 + 92*H),
 "fast containment, slow scope": (t0 + 1*H,  t0 + 80*H),
}
print(f"{'scenario':32s}{'contain':>9}{'report':>9}{'met':>6}{'margin':>9}")
print("-" * 66)
for name, (c, r) in SCENARIOS.items():
    k = clock(t0, c, r, 72)
    print(f"{name:32s}{k['contain_h']:>9.1f}{k['report_h']:>9.1f}"
          f"{str(k['met']):>6}{k['margin_h']:>9.1f}")
print("\nThe third row contained in ONE HOUR and missed by 8 hours.")

# Where the time actually goes when attribution is broken.
PHASES = [
 ("alert fires → analyst picks it up",        3,  "queue depth"),
 ("confirm an incident",                      6,  "is this real?"),
 ("establish WHO acted",                     48,  "logs name the human; agents hidden"),
 ("scope what was touched",                  24,  "must walk the delegation chain (D2.3)"),
 ("legal determines reportability",            8,  "needs the scope"),
 ("draft and send",                            3,  ""),
]
elapsed = 0
print(f"{'phase':38s}{'hours':>7}{'cumulative':>12}  note")
print("-" * 82)
for name, h, note in PHASES:
    elapsed += h
    flag = "  ← DEADLINE PASSED" if elapsed > 72 else ""
    print(f"{name:38s}{h:>7}{elapsed:>12}{flag}  {note}")
print(f"\ntotal {elapsed}h against a 72h deadline")
attribution_cost = PHASES[2][1]
print(f"the attribution phase alone is {attribution_cost}h — "
      f"{attribution_cost/72:.0%} of the entire deadline")
assert elapsed > 72

def with_act_chains(phases):
    """With an acting-identity field, 'who acted' is a query, not an investigation."""
    return [(n, (0.5 if n.startswith("establish WHO") else h), note)
            for n, h, note in phases]

fixed = with_act_chains(PHASES)
total_fixed = sum(h for _, h, _ in fixed)
print(f"with act chains recorded (A2.5 + EV-1): {total_fixed}h vs {elapsed}h")
print(f"deadline met: {total_fixed <= 72}")
assert total_fixed <= 72

PRE_DRAFTED = """
We are notifying you of an incident under [instrument], first identified at
[awareness timestamp].

An automated system operating within our environment performed actions that may
have affected [scope]. Our logging currently attributes these actions to the
authenticated principal on whose behalf the system was acting; we are working to
establish which specific automated component performed them.

Containment: [action] completed at [time].
We will provide an update within [period], including the completed attribution.
"""
print("\nPRE-DRAFTED DISCLOSURE (write this now, not during the incident):")
print(PRE_DRAFTED)
print("It is honest, it starts the notification, and it does not claim an")
print("attribution you cannot yet support.")

# Verify: the runbook needs two owners, not one.
def runbook_check(containment_owner, disclosure_owner, clock_starts_at,
                  has_predrafted):
    problems = []
    if containment_owner == disclosure_owner:
        problems.append("one owner for both workstreams — they compete under time pressure")
    if clock_starts_at != "awareness":
        problems.append(f"clock starts at {clock_starts_at!r}; a regulator will use awareness")
    if not has_predrafted:
        problems.append("no pre-drafted disclosure for incomplete attribution")
    return (not problems), problems

for label, args in (("as usually written", ("IR lead", "IR lead", "confirmation", False)),
                    ("corrected", ("IR lead", "legal/compliance lead", "awareness", True))):
    ok, problems = runbook_check(*args)
    print(f"{label:22s} sound={ok}")
    for p in problems: print(f"   ⚠ {p}")
assert runbook_check("IR lead", "legal/compliance lead", "awareness", True)[0]
