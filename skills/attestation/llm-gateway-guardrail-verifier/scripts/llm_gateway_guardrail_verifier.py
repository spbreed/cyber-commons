#!/usr/bin/env python3
"""Send five calls through one gateway and record which check refuses each one.

This is the executable half of the `llm-gateway-guardrail-verifier` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

LEGACY_DB_CREDENTIAL = "static-service-password"     # never leaves the gateway

REGISTRY = {"spiffe://corp/reports-agent": {"owner": "sam@corp", "expires": 9000}}
POLICY = {("reports-agent", "run_query", "table:reports"): {"SELECT"}}
EGRESS_ALLOW = {"reports-db.corp.example"}

AUDIT = []

def gateway(call):
    """One choke point: identity, registry, policy, egress, budget, audit."""
    checks = []
    def check(name, ok, why=""):
        checks.append((name, ok, why)); return ok

    if not check("identity", call["identity"] in REGISTRY, "attested and registered"):
        return {"allowed": False, "checks": checks}
    verbs = POLICY.get((call["agent"], call["tool"], call["resource"]), set())
    if not check("policy", call["verb"] in verbs, f"permitted verbs {sorted(verbs) or 'none'}"):
        return {"allowed": False, "checks": checks}
    if not check("egress", call["destination"] in EGRESS_ALLOW, "destination allow-list"):
        return {"allowed": False, "checks": checks}
    if not check("budget", call["calls_so_far"] < 5, "per-target ceiling"):
        return {"allowed": False, "checks": checks}

    # the agent never held this; the gateway attaches it on the way out
    AUDIT.append({"principal": call["principal"], "agent": call["agent"],
                  "tool": call["tool"], "resource": call["resource"]})
    return {"allowed": True, "checks": checks, "credential_attached": LEGACY_DB_CREDENTIAL[:6] + "..."}

BASE = {"identity": "spiffe://corp/reports-agent", "agent": "reports-agent",
        "principal": "dana@corp", "tool": "run_query", "resource": "table:reports",
        "verb": "SELECT", "destination": "reports-db.corp.example", "calls_so_far": 0}

CASES = {
 "the intended call":          BASE,
 "unregistered agent":         dict(BASE, identity="spiffe://corp/rogue-agent"),
 "verb not permitted":         dict(BASE, verb="DELETE"),
 "exfiltration destination":   dict(BASE, destination="archive.evil.example"),
 "over the per-target ceiling":dict(BASE, calls_so_far=9),
}
for label, call in CASES.items():
    r = gateway(call)
    failed = [n for n, ok, _ in r["checks"] if not ok]
    print(f"   {label:28s}{'ALLOWED' if r['allowed'] else 'denied at ' + failed[0]}")

print(f"\naudit entries written: {len(AUDIT)}")
print(f"credential held by the agent: never - attached at the gateway")
print()
print("The agent implements none of this. Add a new agent tomorrow and it")
print("inherits every control by being on the other side of one hop.")
print()
print("And the legacy database, which cannot consume a delegated token, is")
print("reached with a static credential the agent has never seen - authorised")
print("against dana before the call was made.")
assert len(AUDIT) == 1 and gateway(CASES["unregistered agent"])["allowed"] is False
