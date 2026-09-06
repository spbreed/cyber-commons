#!/usr/bin/env python3
"""Turn a root cause record into a reviewable policy diff, with the incident attached as evidence.

This is the executable half of `policy-change-proposal`. The last step of an
incident is a change to what is ALLOWED, not only to what is deployed. Stated
as a diff, it can be argued with; stated as a postmortem paragraph, it cannot.

Standard library only, and deterministic.
"""

POLICY = {
    "mcp.vendor.tool_descriptions": "trusted on fetch",
    "tool.call.provenance":         "recorded when present",
    "payments.refund.approval":     "required for amounts over 500",
    "detection.scope_breach.sla":   "15 minutes",
}

ROOT_CAUSE = {
    "incident": "INC-2026-114",
    "control": "no control compared the vendor tool description against the "
               "version approved at onboarding",
    "kci_not_restored": ["KCI-03", "KCI-04"],
}

# Each proposed change names the clause, the new value, and why — the "why" is
# the incident, not an opinion.
PROPOSED = [
    ("mcp.vendor.tool_descriptions", "pinned at onboarding; a change requires review",
     "the altered description is what issued the refund"),
    ("tool.call.provenance", "required; a call without it is refused",
     "41% of calls carried provenance during the incident, so it was optional"),
    ("payments.refund.approval", "required for every amount",
     "KCI-03 did not return to target after the fix"),
]

print(f"policy change proposal · evidence: {ROOT_CAUSE['incident']}")
print(f"root cause: {ROOT_CAUSE['control']}")
print()
report = {"incident": ROOT_CAUSE["incident"], "changes": [], "unaddressed": []}
for clause, new, why in PROPOSED:
    old = POLICY[clause]
    print(f"  {clause}")
    print(f"  - {old}")
    print(f"  + {new}")
    print(f"    why: {why}")
    print()
    report["changes"].append({"clause": clause, "from": old, "to": new, "why": why})

# Step 5 — anything the root cause raised that the diff does NOT change.
covered = {"KCI-03"}
report["unaddressed"] = [k for k in ROOT_CAUSE["kci_not_restored"] if k not in covered]
print(f"{len(report['changes'])} clause(s) changed")
if report["unaddressed"]:
    print(f"NOT addressed by this proposal: {', '.join(report['unaddressed'])}")
    print("   KCI-04 is the detection SLA. No policy change fixes it, because the")
    print("   policy already says 15 minutes — the control was never built to meet")
    print("   what the policy already required. That is an engineering item, and")
    print("   saying so here stops it being lost between the two.")
print()
print("Every line has an incident behind it. A policy diff whose 'why' column is")
print("an opinion gets argued on opinions; one whose 'why' column is a measured")
print("number from last week's incident gets argued on the number.")
print()
print("The refusal in the second change is the expensive one and is stated as a")
print("diff on purpose: 'provenance required, calls without it refused' will")
print("break integrations, and the review that follows is exactly the review")
print("that should happen before it ships rather than after.")

assert len(report["changes"]) == 3
assert report["unaddressed"] == ["KCI-04"]
assert all(c["from"] != c["to"] for c in report["changes"])
