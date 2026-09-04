#!/usr/bin/env python3
"""Print an entitlement at full resolution and evaluate the same tool calls under allow-by-default and under default-deny.

This is the executable half of the `iam-least-privilege-verifier` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# One agent's entire entitlement. Not "the Workflow Agent may query" - this
# SPIFFE ID, these tools, these resources, these verbs. Anything not written
# here is refused, so the file is also the complete answer to "what can this
# agent do", which no amount of reading the code will give you.
ENTITLEMENTS = {
 "spiffe://cybertravels.com/ns/prod/sa/workflow-agent": {
   "run_query":   {"table:bookings":        {"SELECT", "UPDATE"}},
   "charge_card": {"payments:booking":      {"CHARGE"}},   # CHARGE, not REFUND
   "send_email":  {"domain:cybertravels.com": {"*"}},
 },
 "spiffe://cybertravels.com/ns/prod/sa/advisor-agent": {
   "run_query":   {"table:itineraries":     {"SELECT"}},
 },
}

WF = "spiffe://cybertravels.com/ns/prod/sa/workflow-agent"

def decide(identity, tool, resource, verb, default_deny=True):
    """Four inputs. No matching rule means refuse."""
    resources = ENTITLEMENTS.get(identity, {}).get(tool)
    if resources is None:
        return (False, "no entitlement for this identity+tool") if default_deny \
               else (True, "allowed by default")
    for res_prefix in sorted(resources):
        if resource.startswith(res_prefix):
            verbs = resources[res_prefix]
            if "*" in verbs or verb in verbs:
                return True, f"{tool} on {res_prefix} permits {verb}"
            return False, f"{verb} not permitted on {res_prefix} (only {sorted(verbs)})"
    return (False, "resource outside the entitlement") if default_deny \
           else (True, "allowed by default")

for tool, res in sorted((t, r) for t, rs in ENTITLEMENTS[WF].items() for r in rs):
    print(f"   {tool:12s}{res:26s}{sorted(ENTITLEMENTS[WF][tool][res])}")

CALLS = [
 (WF, "run_query",   "table:bookings",           "SELECT"),  # intended
 (WF, "run_query",   "table:customer_pii",       "SELECT"),  # A1.5, resource
 (WF, "charge_card", "payments:booking",         "REFUND"),  # R1, verb
 (WF, "send_email",  "domain:archive.evil.example", "*"),    # A1.3, exfiltration
 (WF, "drop_table",  "table:bookings",           "*"),       # tool never granted
]

for mode in (False, True):
    label = "DEFAULT-DENY" if mode else "allow-by-default"
    allowed = 0
    print(f"{label}:")
    for identity, tool, resource, verb in CALLS:
        ok, why = decide(identity, tool, resource, verb, default_deny=mode)
        allowed += ok
        print(f"   {tool:12s}{resource:30s}{verb:7s}"
              f"{'ALLOW' if ok else 'deny ':6s}{why}")
    print(f"   -> {allowed}/{len(CALLS)} permitted\n")

print("Only the first call should succeed. Under allow-by-default four do, and")
print("each one is a real risk from Chapter 1 walking through.")
print()
print("Row three is the one to sit with: same identity, same tool, same")
print("resource, refused on the VERB. An entitlement attached to the tool")
print("instead of the call cannot express that distinction at all - and the")
print("distance between CHARGE and REFUND is the whole of R1.")
assert sum(decide(*c, default_deny=True)[0] for c in CALLS) == 1
assert not decide(WF, "charge_card", "payments:booking", "REFUND")[0]
