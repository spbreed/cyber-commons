#!/usr/bin/env python3
"""Map which function operates which controls, and find the seams where two reasonable assumptions leave a use case ungoverned.

This is the executable half of the `stakeholder-seam-map` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# The five control functions from the table above, with the count of
# controls each one operates. Everything here is true, and self-reported.
OPERATES = {"legal": 4, "compliance": 4, "privacy": 4, "cyber": 6, "model_risk": 4}
OPEN_SEAMS = 4                      # the four from the previous section

def self_report(function):
    """Each function reports on the controls it operates. All of it is true."""
    return {"function": function, "controls_operating": OPERATES[function],
            "status": "green"}

for f in sorted(OPERATES):
    r = self_report(f)
    print(f"   {r['function']:12s}{r['controls_operating']} controls  {r['status']}")
print()
print(f"functions reporting green : {len(OPERATES)}/{len(OPERATES)}")
print(f"open seams                : {OPEN_SEAMS}")
print()
print("A dashboard assembled from function self-reports is all green, and four")
print("material gaps are open. The dashboard is not lying - it is asking each")
print("function about the inside of its own box, and every failure here is")
print("between boxes.")
assert OPEN_SEAMS == 4 and len(OPERATES) == 5

HANDOFFS = {
 "trace retention schedule":      {"owner": "privacy",  "consumers": ["cyber", "legal"]},
 "tool scope in validation":      {"owner": "model_risk","consumers": ["cyber", "business_owner"]},
 "vendor no-train verification":  {"owner": "cyber",    "consumers": ["legal", "compliance"]},
 "re-tier on capability change":  {"owner": "compliance","consumers": ["business_owner", "cyber"]},
}
print(f"{'handoff artefact':32s}{'accountable':13s}consumers")
for h in sorted(HANDOFFS):
    v = HANDOFFS[h]
    print(f"{h:32s}{v['owner']:13s}{', '.join(v['consumers'])}")

covered = len(HANDOFFS)
print(f"\nseams: {OPEN_SEAMS}   handoffs with an accountable owner: {covered}")
print()
print("One artefact, many consumers, exactly one owner. The consumers matter as")
print("much as the owner: a handoff nobody consumes was never a handoff, and a")
print("handoff with two owners is the contested case from E1.0 again.")
assert covered == OPEN_SEAMS

def governed(use_case):
    missing = [seat for seat in ("business_owner", "internal_audit")
               if seat not in use_case["seats"]]
    five = [f for f in OPERATES if f in use_case["seats"]]
    return {"control_functions_present": len(five),
            "missing_seats": missing,
            "is_governed": not missing and len(five) == len(OPERATES)}

CASES = [
 {"name": "customer support agent",
  "seats": list(OPERATES) + ["business_owner", "internal_audit"]},
 {"name": "internal code assistant", "seats": list(OPERATES)},
]
for c in CASES:
    g = governed(c)
    print(f"   {c['name']:26s}five functions: {g['control_functions_present']}/5   "
          f"missing: {g['missing_seats'] or 'none'}   governed: {g['is_governed']}")
print()
print("The second one has every control function at the table and no accountable")
print("owner. Five functions are governing something nobody has agreed to own,")
print("which is how a use case survives a review and still has no one to fund")
print("the remediation it was told to do.")
assert not governed(CASES[1])["is_governed"]
