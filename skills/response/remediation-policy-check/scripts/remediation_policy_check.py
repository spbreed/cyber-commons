#!/usr/bin/env python3
"""Classify remediation actions against one policy, on blast radius and reversibility.

This is the executable half of `remediation-policy-check`. The tier a runbook
runs at is derived here, once, from two properties of the action — not chosen
per runbook by whoever wrote it.

Standard library only, and deterministic.
"""

# The policy. Two axes, and the tier falls out of them.
#   reversible : can this be undone without a human decision?
#   radius     : one agent, one tenant, or the estate
def tier(reversible, radius):
    if not reversible:
        return "manual"                      # never automated, whatever the radius
    if radius in ("tenant", "estate"):
        return "human-in-the-loop"           # reversible, but somebody else feels it
    return "automated"                       # one agent, and undoable

ACTIONS = [
    ("throttle one agent",          True,  "agent"),
    ("reduce one agent's scope",    True,  "agent"),
    ("revoke one agent's token",    True,  "agent"),
    ("reroute a tenant's traffic",  True,  "tenant"),
    ("force HITL on every agent",   True,  "estate"),
    ("fleet kill switch",           True,  "estate"),
    ("delete the agent's workdir",  False, "agent"),
    ("roll back the tenant's data", False, "tenant"),
    ("rotate the estate's root CA", False, "estate"),
]

print(f"{'action':<30}{'reversible':>11}{'radius':>9}   tier")
report = {"actions": [], "by_tier": {}}
for name, rev, radius in ACTIONS:
    t = tier(rev, radius)
    print(f"{name:<30}{str(rev):>11}{radius:>9}   {t}")
    report["actions"].append({"action": name, "reversible": rev,
                              "radius": radius, "tier": t})
    report["by_tier"][t] = report["by_tier"].get(t, 0) + 1
print()
for t in ("automated", "human-in-the-loop", "manual"):
    print(f"   {t:<20}{report['by_tier'].get(t, 0)}")
print()
print("Reversibility dominates radius, and that ordering is the policy's whole")
print("content. 'delete the agent's workdir' touches one agent and is still")
print("manual, because there is no undo - while 'force HITL on every agent'")
print("touches the entire estate and is only human-in-the-loop, because it is")
print("one flag and it can be turned back off.")
print()
print("Write this down once and every runbook inherits its tier. Decide it per")
print("runbook and the blast radius of your response is unknown until it fires.")

assert report["by_tier"] == {"automated": 3, "human-in-the-loop": 3, "manual": 3}
assert all(a["tier"] == "manual" for a in report["actions"] if not a["reversible"])
assert tier(True, "agent") == "automated" and tier(True, "tenant") == "human-in-the-loop"
assert tier(False, "agent") == "manual", "irreversibility outranks a small radius"
