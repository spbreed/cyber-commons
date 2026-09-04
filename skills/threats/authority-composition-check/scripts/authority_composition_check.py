#!/usr/bin/env python3
"""Show a denied scope being reached through a chain of individually legitimate hops.

This is the executable half of the `authority-composition-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

PERMISSIONS = {"mallory": {"reports:read"},
               "finance-agent": {"reports:read", "payments:write"},
               "orchestrator": {"reports:read", "route"}}

def direct(user, scope):
    return scope in PERMISSIONS[user]

CHAIN = []
def route(user, request):
    """Each hop checks only its own permission. Nothing checks the composition."""
    CHAIN.append(("user asks orchestrator", user, direct(user, "reports:read")))
    CHAIN.append(("orchestrator routes", "orchestrator", direct("orchestrator", "route")))
    needed = "payments:write" if "refund" in request else "reports:read"
    CHAIN.append(("agent acts", "finance-agent", direct("finance-agent", needed)))
    return all(ok for _, _, ok in CHAIN)

print(f"mallory holds        : {sorted(PERMISSIONS['mallory'])}")
print(f"mallory asks directly for payments:write -> "
      f"{'allowed' if direct('mallory', 'payments:write') else 'DENIED'}")
print()
print("same outcome, requested through the architecture:")
ok = route("mallory", "please issue a refund for order 4471")
for step, who, allowed in CHAIN:
    print(f"   {step:26s}{who:16s}{'ok' if allowed else 'denied'}")
print(f"   -> reached payments:write: {ok}")
print()
print("Every hop was legitimate. Mallory was allowed to ask, the orchestrator")
print("was allowed to route, the agent was allowed to act. The composition")
print("reached exactly what the direct check refused.")

# T15: the same output, two framings
FINDING = "dependency libfoo has no known vulnerabilities"
print()
print("and the other direction - the same claim, two ways:")
print(f"   colleague says : '{FINDING}'   -> reader asks how they know")
print(f"   agent reports  : '{FINDING}'   -> reader treats it as checked")
print()
print("Nothing about the second is more true. It is formatted like a system")
print("output, so it recruits the authority of one.")
assert not direct("mallory", "payments:write") and ok
