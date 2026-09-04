#!/usr/bin/env python3
"""Route actions by reversibility and count how many reach a human per day.

This is the executable half of the `blast-radius-review` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

ACTIONS = {
 "read_report":      {"reversible": True,  "external": False},
 "write_draft":      {"reversible": True,  "external": False},
 "update_ticket":    {"reversible": True,  "external": False},
 "delete_row":       {"reversible": False, "external": False},
 "send_email":       {"reversible": False, "external": True},
 "issue_refund":     {"reversible": False, "external": True},
 "rotate_credential":{"reversible": False, "external": False},
}
DAILY_VOLUME = {"read_report": 400, "write_draft": 120, "update_ticket": 260,
                "delete_row": 6, "send_email": 3, "issue_refund": 2,
                "rotate_credential": 1}

def route(action):
    a = ACTIONS[action]
    if not a["reversible"] or a["external"]:
        return "human approval"
    return "policy only"

CAREFUL_CAPACITY = 25
print(f"{'action':20s}{'reversible':12s}{'external':10s}{'routing':16s}per day")
to_human = 0
for name in sorted(ACTIONS):
    a, r = ACTIONS[name], route(name)
    if r == "human approval": to_human += DAILY_VOLUME[name]
    print(f"{name:20s}{str(a['reversible']):12s}{str(a['external']):10s}"
          f"{r:16s}{DAILY_VOLUME[name]}")

total = sum(DAILY_VOLUME.values())
print(f"\nactions per day            : {total}")
print(f"reaching a human           : {to_human}")
print(f"a reviewer considers ~{CAREFUL_CAPACITY}/day properly")
print(f"gate holds?                : {to_human <= CAREFUL_CAPACITY}")
print()
print(f"Approving everything would send {total} a day to someone who can read")
print(f"{CAREFUL_CAPACITY}. Routing by reversibility sends {to_human}, and every one gets read.")

# the T15 half
FINDING = "libfoo has no known vulnerabilities"
print(f"\nunlabelled : {FINDING}")
print(f"labelled   : [machine-generated, unverified] {FINDING}")
print("\nThe label does not stop anyone acting on it. It restores the scepticism")
print("they would give a colleague saying the same sentence.")
assert to_human <= CAREFUL_CAPACITY
