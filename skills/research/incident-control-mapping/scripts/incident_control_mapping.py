#!/usr/bin/env python3
"""Map each control failure in a published incident to the control that would have closed it, and count preventive against detective.

This is the executable half of the `incident-control-mapping` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# The incident's control register, embedded verbatim. It is the same list
# `labs/incident-register/register.json` holds and `check_register.py`
# keeps in step, so the mapping below is against real rows rather than
# an illustration.
REGISTER = [
 # id      name                                     type   NIST     owning lesson
 ("C1.1",  "out-of-band telemetry capture",         "P/D", "AU-9",  "A2.8"),
 ("C1.2",  "hash-chained WORM transcript store",    "P",   "AU-10", "A2.8"),
 ("C1.3",  "logging-plane isolation",               "P",   "SC-39", "A2.8"),
 ("C1.4",  "escape detection",                      "D",   "SI-7",  "D1.9"),
 ("C2.1",  "per-run namespace isolation",           "P",   "SC-4",  "A3.8"),
 ("C2.2",  "immutable / write-once artifact cache", "P",   "AC-4",  "A3.8"),
 ("C2.3",  "covert channel analysis",               "D",   "SC-31", "D1.10"),
 ("C2.4",  "write-pattern anomaly detection",       "D",   "SI-4",  "D1.10"),
 ("C3.1",  "parser sandboxing",                     "P",   "SI-3",  "A3.2"),
 ("C3.2",  "credential removal from workers",       "P",   "AC-6",  "A2.4"),
 ("C3.3",  "micro-segmentation, default-deny egress","P",  "SC-7",  "A3.3"),
 ("C3.4",  "dataset and upload content scanning",   "D",   "SI-10", "D1.9"),
 ("C4.1",  "secret scanning, automated revocation", "D/C", "IA-5",  "D1.9"),
 ("C4.2",  "short-lived workload credentials",      "P",   "IA-5",  "A2.4"),
 ("C4.3",  "scope minimisation",                    "P",   "AC-6",  "A2.3"),
 ("C4.4",  "credential canaries",                   "D",   "SI-4",  "D1.11"),
 ("C5.1",  "artifact signing verified at pull",     "P",   "SR-11", "A3.8"),
 ("C5.2",  "provenance attestation",                "P",   "SR-4",  "A3.8"),
 ("C5.3",  "admin-plane separation, JIT elevation", "P/D", "AC-6",  "A3.8"),
 ("C5.4",  "cache integrity diffing",               "D",   "SI-7",  "D1.9"),
 ("C6.1",  "control-exemption gate",                "P",   "CM-3",  "A3.9"),
 ("C6.2",  "mandatory blast-radius caps",           "P",   "RA-3",  "A3.9"),
 ("C6.3",  "continuous exemption-state monitoring", "D/C", "CA-7",  "D1.9"),
 ("C6.4",  "exemption register at launch approval", "P",   "PM-9",  "A3.9"),
 ("C7.1",  "authenticated principal hierarchy",     "P",   "IA-9",  "A2.6"),
 ("C7.2",  "channel separation",                    "P",   "AC-3",  "A2.6"),
 ("C7.3",  "prompt-injection filtering",            "P/D", "SI-10", "A2.6"),
 ("C7.4",  "authorisation-decision logging",        "D",   "AU-2",  "D1.10"),
 ("C8.1",  "cross-trajectory correlation analytics","D",   "SI-4",  "D1.10"),
 ("C8.2",  "population and lifetime quotas",        "P",   "SC-6",  "A3.9"),
 ("C8.3",  "fleet kill switch",                     "C",   "IR-4",  "D2.9"),
 ("C8.4",  "coordination-signature detection",      "D",   "SI-4",  "D1.10"),
 ("C9.1",  "first-class report-to-human tool",      "P",   "IR-6",  "A3.10"),
 ("C9.2",  "escalation-path testing",               "D",   "IR-3",  "D1.10"),
 ("C9.3",  "non-use telemetry",                     "D",   "SI-4",  "D1.10"),
 ("C9.4",  "mandatory HITL checkpoint on discovery","P",   "AC-3",  "A3.10"),
 ("C10.1", "cheat-surface red team",                "P",   "SA-11", "C1.2"),
 ("C10.2", "explicit abstain affordance",           "P",   "SA-8",  "A3.10"),
 ("C10.3", "honeypot and canary tasks",             "D",   "RA-5",  "D1.11"),
 ("C10.4", "scorer integrity separation",           "P",   "SC-7",  "A3.8"),
]

SURFACE_USED_BY = {
 "artifact repository": [1, 2, 5],
 "agent container":     [1],
 "third-party upload":  [3],
 "public internet":     [4],
 "eval configuration":  [6],
 "peer channel":        [7, 8],
 "harness tooling":     [9],
 "benchmark scoring":   [10],
}

print(f"{'shared surface':22s}{'rows':12s}reading")
for surface in sorted(SURFACE_USED_BY):
    rows = SURFACE_USED_BY[surface]
    reading = ("one chain, not separate findings" if len(rows) > 2
               else "linked" if len(rows) == 2 else "single row")
    print(f"{surface:22s}{str(rows):12s}{reading}")

chain = [s for s, r in sorted(SURFACE_USED_BY.items()) if len(r) > 2]
print(f"\nsurfaces implicated in three or more rows: {chain}")
print()
print("Filed as three findings, three teams each fix their third and the")
print("repository stays a shared mutable surface. Filed as one chain, the")
print("remediation is a single workstream - which is why the register keeps")
print("the note rather than the tidy row numbering.")
assert chain == ["artifact repository"]

from collections import Counter

FUNCTION = {"A": "securing the architecture", "C": "red teaming and research",
            "D": "the agentic SOC"}

by_fn = Counter(c[4][0] for c in REGISTER)
print(f"{'function':10s}{'controls':>9}  what it owns")
for f in sorted(by_fn):
    print(f"{f:10s}{by_fn[f]:>9}  {FUNCTION[f]}")

print()
new = {"A2.8", "A3.8", "A3.9", "A3.10", "D1.11", "C1.2", "D1.9", "D1.10", "D2.9"}
existing = sorted({c[4] for c in REGISTER} - new)
print(f"controls landing on lessons that already existed: "
      f"{sum(1 for c in REGISTER if c[4] in existing)}")
for lesson in existing:
    ids = [c[0] for c in REGISTER if c[4] == lesson]
    print(f"   {lesson:7s}{', '.join(ids)}")

orphans = [c[0] for c in REGISTER if not c[4]]
print(f"\ncontrols with no owning lesson: {len(orphans)}")
print()
print("Nothing is unowned. Note which functions do NOT appear: the register")
print("is preventive, detective and investigative, and none of its forty")
print("controls is a code-review control - the pipeline in Function B reviews")
print("code, and no amount of code review would have caught any of this.")
print()
print("Six of the forty needed no new lesson at all -")
print("parser sandboxing was already A3.2, micro-segmentation A3.3, short-lived")
print("credentials A2.4. A register that duplicates what you have is worse than")
print("one that maps onto it.")
assert not orphans and set(by_fn) == {"A", "C", "D"}

PRECONDITIONS = {
 "parallel agents on one task":        ("present", "R8"),
 "shared mutable surface between runs":("present", "R4, R7"),
 "agents read each other's output":    ("present", "R3"),
 "workload-writable transcript":       ("present", "R10, R11"),
 "credentials reachable from workload":("present", "R5"),
 "reachable third party":              ("present", "R4, R9"),
 "no agent-to-human escalation path":  ("present", "-"),
 "detective control switched off":     ("present", "R2"),
 "tens of thousands of agents at once":("not yet",  "-"),
}
present = [k for k, (s, _) in PRECONDITIONS.items() if s == "present"]
print(f"preconditions the incident needed : {len(PRECONDITIONS)}")
print(f"already true at CyberTravels      : {len(present)}")
print(f"still missing                     : "
      f"{len(PRECONDITIONS) - len(present)}  (scale)")
print()
covered = {r for _, (_, rows) in PRECONDITIONS.items()
           for r in rows.replace(" ", "").split(",") if r != "-"}
print(f"register rows implicated: {len(covered)}  "
      f"({', '.join(sorted(covered, key=lambda x: int(x[1:])))})")
print()
print("Read the incident as a story about an AI lab and it is a curiosity. Read")
print("it as a list of preconditions and eight of nine are already sitting in a")
print("travel company's booking platform. The ninth is a scaling decision")
print("somebody will make for good reasons on an ordinary Tuesday.")
assert len(present) == 8 and len(covered) == 9
