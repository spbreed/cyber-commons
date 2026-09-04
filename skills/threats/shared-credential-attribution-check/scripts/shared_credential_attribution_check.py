#!/usr/bin/env python3
"""Show what a shared credential does to attribution and to containment when one holder misbehaves.

This is the executable half of the `shared-credential-attribution-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SHARED_KEY = "svc-agent-7f3a1c"

AGENTS = {"triage-agent":  {"key": SHARED_KEY},
          "patch-agent":   {"key": SHARED_KEY},
          "deploy-agent":  {"key": SHARED_KEY}}

CALLS = []

def downstream(api_key, action, resource):
    """A downstream service sees only the credential presented."""
    CALLS.append({"presented": api_key, "action": action, "resource": resource})
    return {"ok": True, "caller": api_key}

for name in sorted(AGENTS):
    downstream(AGENTS[name]["key"], "read", "reports")
downstream(SHARED_KEY, "delete", "prod.customers")     # one of them did this

print("what the downstream service recorded:")
for c in CALLS:
    print(f"   caller={c['presented']}  {c['action']:7s} {c['resource']}")

incident = [c for c in CALLS if c["action"] == "delete"]
candidates = sorted(AGENTS)
print(f"\nincident: {incident[0]['action']} on {incident[0]['resource']}")
print(f"which agent did it? candidates: {candidates}")
print(f"distinguishable from the record? {len({c['presented'] for c in CALLS}) > 1}")

print("\ncontainment options:")
print(f"   rotate {SHARED_KEY} -> stops the incident, and stops "
      f"{len(AGENTS)} agents including {len(AGENTS)-1} innocent ones")
print("   rotate only the culprit -> not available; there is no 'only'")
print()
print("No attacker forged anything. Impersonation is the resting state of a")
print("system where identity was never per-workload.")
assert len({c["presented"] for c in CALLS}) == 1
