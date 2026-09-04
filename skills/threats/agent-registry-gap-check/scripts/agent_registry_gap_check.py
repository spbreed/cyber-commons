#!/usr/bin/env python3
"""Compare the agents that exist with the agents anybody registered, and show what the unregistered ones are handed.

This is the executable half of the `agent-registry-gap-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

REGISTRY = {"pricing-agent":  {"owner": "payments-team", "approved": True},
            "billing-agent":  {"owner": "payments-team", "approved": True}}

DISCOVERED = ["pricing-agent", "billing-agent", "reporting-agent-v2"]

DELEGATED = []

def delegate(agent_name, task, user_token):
    """The orchestrator hands work - and the caller's narrowed token - onward."""
    DELEGATED.append({"agent": agent_name, "task": task, "token": user_token})
    return f"{agent_name} accepted"

USER_TOKEN = "obo:dana@corp:reports:read,reports:write"

print(f"{'agent':22s}{'in registry?':14s}{'approved?':11s}received work?")
for name in DISCOVERED:
    entry = REGISTRY.get(name)
    delegate(name, "summarise Q3 revenue", USER_TOKEN)      # admitted by discovery
    print(f"{name:22s}{str(bool(entry)):14s}"
          f"{str(bool(entry and entry['approved'])):11s}yes")

rogue = [d for d in DELEGATED if d["agent"] not in REGISTRY]
print(f"\nagents that received delegated work : {len(DELEGATED)}")
print(f"of which unregistered               : {len(rogue)}")
for r in rogue:
    print(f"   {r['agent']} now holds {r['token']}")
print()
print("It was admitted because it answered the protocol in the right place.")
print("It received the task AND the narrowed user token, so it can act as dana")
print("against every downstream that honours that token.")
assert rogue and all(r["token"] == USER_TOKEN for r in rogue)
