#!/usr/bin/env python3
"""Build a root cause record from a reconstructed incident, and reject one that names a person.

This is the executable half of `root-cause-record`. A postmortem narrative is
not a root cause: the test is whether the record names a CONTROL that should
have caught the incident and did not, in a form the next change can act on.

Standard library only, and deterministic.
"""

INCIDENT = {
    "id": "INC-2026-114",
    "summary": "vendor MCP tool description was altered; the workflow agent "
               "issued a refund it was never asked for",
    "detected_by": "customer complaint",
    "detected_after_minutes": 194,
}

# Every control that could have caught this, and whether it did.
CHAIN = [
    ("A2.6", "provenance marking at ingress",            "absent"),
    ("A3.1", "default-deny on the tool call",            "present-but-scoped-wrong"),
    ("D2.4", "detection on refund without approval",     "absent"),
    ("D1.2", "drift monitor on vendor tool descriptions", "absent"),
    ("D4.4", "stop authority within the refund window",  "present"),
]

CANDIDATES = [
    "the on-call engineer missed the alert",                    # names a person
    "we should have been more careful with vendor MCP servers",  # names a mood
    "no control compared the vendor tool description against "
    "the version approved at onboarding",                        # names a control
]

print(f"{INCIDENT['id']} · detected by {INCIDENT['detected_by']} after "
      f"{INCIDENT['detected_after_minutes']} minutes")
print()
print(f"{'control':<8}{'what it would have caught':<42}status")
for cid, what, status in CHAIN:
    print(f"{cid:<8}{what:<42}{status}")
print()

# Step 2 — the first control in the chain that was absent is the root cause
# candidate. Later absent controls are contributing, not root.
absent = [c for c in CHAIN if c[2] == "absent"]
root = absent[0]
print(f"first absent control in the chain: {root[0]} — {root[1]}")
print(f"contributing: {', '.join(c[0] for c in absent[1:])}")
print()

# Step 4 — the record has to name a control, not a person or an intention.
PERSON = ("engineer", "analyst", "developer", "team", "on-call", "we", "someone")
report = {"incident": INCIDENT["id"], "root_control": root[0],
          "contributing": [c[0] for c in absent[1:]], "statements": []}
print("candidate root cause statements")
for text in CANDIDATES:
    words = set(text.lower().replace(",", " ").split())
    names_person = bool(words & set(PERSON))
    names_control = any(k in text for k in ("control", "no ", "compared", "check"))
    ok = names_control and not names_person
    print(f"   {'ACCEPT' if ok else 'REJECT'}  {text}")
    if not ok:
        why = "names no control" if not names_control else "names a person"
        print(f"           -> {why}")
    report["statements"].append({"text": text, "accepted": ok})
print()
accepted = [s for s in report["statements"] if s["accepted"]]
print(f"{len(accepted)} of {len(CANDIDATES)} statements are usable as a root cause")
print()
print("The first two are true and useless. An engineer missing an alert is a")
print("thing that will happen again next quarter to a different engineer, and")
print("'be more careful' is not a change anybody can make. Only the third names")
print("something that can be built, tested, and checked in D5.4.")
print()
print("Note that stop authority was PRESENT and the incident still ran 194")
print("minutes. A control that exists but is never reached is not a mitigating")
print("factor - it is evidence that the detection in front of it was the gap.")

assert len(accepted) == 1
assert report["root_control"] == "A2.6"
assert "D2.4" in report["contributing"]
