#!/usr/bin/env python3
"""Trace each joint runbook from owner to consumer and find the handoffs that were never actually delivered.

This is the executable half of the `handoff-delivery-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

RUNBOOKS = {
 "privacy assessment -> control design": {
   "artefact": "DPIA with a control annex",
   "owner": "privacy",
   "consumers": ["cyber", "model_risk"],
   "consumer_entitled_to_assume": "the data classes and retention limits are settled",
   "delivered_to": ["cyber"]},                       # model_risk never receives it
 "legal position -> system prompt": {
   "artefact": "approved language and refusal set",
   "owner": "legal",
   "consumers": ["cyber", "business_owner"],
   "consumer_entitled_to_assume": "these refusals are contractually required",
   "delivered_to": ["cyber", "business_owner"]},
 "MRM validation -> security evidence": {
   "artefact": "validation report with tool surface and autonomy",
   "owner": "model_risk",
   "consumers": ["cyber", "compliance", "internal_audit"],
   "consumer_entitled_to_assume": "the validated unit matches what is deployed",
   "delivered_to": ["compliance"]},                  # cyber and audit never receive it
}
for name in sorted(RUNBOOKS):
    r = RUNBOOKS[name]
    print(f"{name}")
    print(f"   artefact  : {r['artefact']}")
    print(f"   owner     : {r['owner']}")
    print(f"   consumers : {', '.join(r['consumers'])}")
    print()

gaps = []
for name in sorted(RUNBOOKS):
    r = RUNBOOKS[name]
    missing = sorted(set(r["consumers"]) - set(r["delivered_to"]))
    status = "complete" if not missing else f"NOT DELIVERED to {', '.join(missing)}"
    print(f"{name[:44]:46s}{status}")
    for m in missing:
        gaps.append((name, m, r["consumer_entitled_to_assume"]))
print()
print(f"undelivered handoffs: {len(gaps)}")
for name, who, assumption in gaps:
    print(f"   {who:14s} is assuming: {assumption}")
    print(f"   {'':14s} and has not received: {RUNBOOKS[name]['artefact']}")
assert gaps

CONSEQUENCE = {
 ("privacy assessment -> control design", "model_risk"):
   "validation runs on data the DPIA restricted; the restriction is invisible to it",
 ("MRM validation -> security evidence", "cyber"):
   "security cannot see the validated tool surface, so scope creep is undetectable",
 ("MRM validation -> security evidence", "internal_audit"):
   "third line cannot test the second line's assurance; it audits the artefact it has",
}
for name, who, _ in gaps:
    print(f"   {who:16s}{CONSEQUENCE.get((name, who), 'unknown')}")
print()
print("None of these is a control failing. Each is a control that was built,")
print("works, and is invisible to the function whose decision depends on it.")

def close(runbooks):
    out = {}
    for name, r in runbooks.items():
        out[name] = dict(r, delivered_to=sorted(r["consumers"]))
    return out

CLOSED = close(RUNBOOKS)
remaining = [(n, c) for n, r in sorted(CLOSED.items())
             for c in r["consumers"] if c not in r["delivered_to"]]
print(f"{'seam':46s}{'owner':13s}delivered to")
for n in sorted(CLOSED):
    r = CLOSED[n]
    print(f"{n[:44]:46s}{r['owner']:13s}{', '.join(r['delivered_to'])}")
print(f"\nundelivered handoffs remaining: {len(remaining)}")
print()
print("One owner per artefact, every consumer named, and delivery recorded")
print("rather than assumed. The delivery record is the part people skip, and it")
print("is the only part that makes the seam auditable a year later.")
assert not remaining

def check(runbooks):
    problems = []
    for name, r in sorted(runbooks.items()):
        if not r["artefact"]:                     problems.append(f"{name}: no artefact")
        if not r["owner"]:                        problems.append(f"{name}: no owner")
        if isinstance(r["owner"], list):          problems.append(f"{name}: {len(r['owner'])} owners")
        if not r["consumers"]:                    problems.append(f"{name}: no consumers")
        undel = set(r["consumers"]) - set(r["delivered_to"])
        if undel:                                 problems.append(f"{name}: undelivered to {sorted(undel)}")
    return problems

print("before:", len(check(RUNBOOKS)), "problem(s)")
for p in check(RUNBOOKS): print("   ", p)
print("after :", len(check(CLOSED)), "problem(s)")
print()
print("Four properties, checked mechanically: an artefact exists, one owner is")
print("accountable, consumers are named, delivery is recorded. A governance")
print("programme that can run this check on its own seams is doing something")
print("more useful than another policy document.")
assert check(RUNBOOKS) and not check(CLOSED)
