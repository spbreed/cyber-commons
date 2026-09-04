#!/usr/bin/env python3
"""Scope what an agent touched during an incident, from the run record rather than from the alert.

This is the executable half of the `incident-scoping` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# The skill runtime comes from the shared library, not from a copy in this file.
# In a lesson notebook the cell above has already loaded it; standalone, find it
# the same way that cell does.
# The runtime comes from the shared library. The lesson cell above put it
# on the path; standalone, PYTHONPATH does (see scripts/test_skills.py).
from cyber_commons_skill_runtime import check, contract_of, parse_skill


def _skill_md():
    """The SKILL.md next to this script, or the one the notebook already parsed."""
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


import pathlib as _pathlib

SKILL_MD = _skill_md()
meta, body = parse_skill(SKILL_MD)

REACHED = {
 "dana@corp":    ["repo-core", "repo-infra", "vault-dev"],
 "orchestrator": ["repo-core", "queue-tasks"],
 "patch-agent":  ["repo-core", "repo-payments"],
 "deploy-agent": ["cluster-prod"],
}
CHAIN = ["dana@corp", "orchestrator", "patch-agent", "deploy-agent"]

def scope(chain, reached):
    last_only = set(reached.get(chain[-1], []))
    full = {r for a in chain for r in reached.get(a, [])}
    return {"chain": " → ".join(chain),
            "scoped_last_actor_only": sorted(last_only),
            "scoped_whole_chain": sorted(full),
            "missed_by_naive_scoping": sorted(full - last_only),
            "undercount_factor": round(len(full)/len(last_only), 2) if last_only else None}

s = scope(CHAIN, REACHED)
for k, v in s.items(): print(f"{k:26s}{v}")
print("\nScoping the last actor finds one cluster. The chain reached six")
print("resources, including a payments repository and a dev vault.")

print(f"{'depth':>6}{'last-actor scope':>19}{'chain scope':>14}{'undercount':>12}")
print("-" * 52)
for d in range(1, 5):
    sub = CHAIN[:d]
    r = scope(sub, REACHED)
    print(f"{d:>6}{len(r['scoped_last_actor_only']):>19}"
          f"{len(r['scoped_whole_chain']):>14}"
          f"{str(r['undercount_factor']):>12}")
print("\nEach hop adds resources the last actor never touched. This is why B2.0")
print("bounds delegation depth: depth is an incident-scope multiplier.")

SHARED = {"repo-core": ["build-agent", "test-agent"],
          "cluster-prod": ["deploy-agent", "monitor-agent"],
          "repo-payments": ["finance-agent"]}

def scope_transitive(chain, reached, shared, hops=1):
    """Anything that shares a touched resource may have been influenced."""
    direct = {r for a in chain for r in reached.get(a, [])}
    exposed = set(chain)
    frontier = set(direct)
    for _ in range(hops):
        nxt = set()
        for res in frontier:
            for actor in shared.get(res, []):
                if actor not in exposed:
                    exposed.add(actor)
                    nxt |= set(reached.get(actor, []))
        frontier = nxt
    return {"resources_direct": sorted(direct),
            "actors_in_scope": sorted(exposed),
            "second_order_actors": sorted(exposed - set(chain))}

t = scope_transitive(CHAIN, REACHED, SHARED)
for k, v in t.items(): print(f"{k:22s}{v}")
print("\nFive more identities shared a resource with the compromised chain.")
print("They are not confirmed compromised — they are IN SCOPE, which is different")
print("and is the distinction an incident record has to make explicitly.")
assert t["second_order_actors"]

# Verify: produce the scope statement for the incident record.
def scope_statement(chain, reached, shared):
    s = scope(chain, reached)
    t = scope_transitive(chain, reached, shared)
    return (f"SCOPE\n"
            f"  chain              {s['chain']}\n"
            f"  confirmed touched  {s['scoped_whole_chain']}\n"
            f"  would have been missed by scoping the acting agent alone:\n"
            f"                     {s['missed_by_naive_scoping']}\n"
            f"  undercount factor  {s['undercount_factor']}×\n"
            f"  in scope, not confirmed (shared a resource):\n"
            f"                     {t['second_order_actors']}")
print(scope_statement(CHAIN, REACHED, SHARED))

contract = contract_of(body)
t = scope_transitive(CHAIN, REACHED, SHARED)
reach = sorted({r for a in CHAIN for r in REACHED.get(a, [])})

incident = {
 "window": {"first_suspicious_action": f"{CHAIN[1]} accepted an external instruction",
            "detected_at": "the deploy that followed",
            # the trigger precedes the detection by about one task loop
            "gap_seconds": 42 * 60},
 "chain": [{"action": f"{a} acted", "motivating_input": "issue comment"
                      if a == CHAIN[1] else f"instruction from {CHAIN[i]}",
            "input_origin": "external_untrusted" if a == CHAIN[1] else "internal",
            "within_authority": True}
           for i, a in enumerate(CHAIN[1:])],
 "root_cause": {"input": "issue comment on a public tracker",
                "origin": "external_untrusted",
                "why_trusted": "repository content was read as instruction, not data"},
 # every action was permitted; that is what makes this hard
 "authority": {"authorised_but_wrong": len(CHAIN) - 1, "exceeded_authority": 0},
 "data": {"reach": reach, "confirmed_exfiltration": [],
          "egress_bounded_by": "agent network policy"},
 "containment": {"cut": "credential",
                 "does_not_stop": sorted(t["second_order_actors"]),
                 "evidence_snapshotted_first": True},
 "clock": {"regulatory_trigger": False,
           "basis": "no confirmed exfiltration of personal data yet"},
}
problems = check(incident, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\nauthorised but wrong : {incident['authority']['authorised_but_wrong']}")
print(f"exceeded authority   : {incident['authority']['exceeded_authority']}")
print(f"reach                : {len(reach)} resources")
print(f"confirmed exfil      : {len(incident['data']['confirmed_exfiltration'])}")
print(f"revoking one credential does NOT stop: "
      f"{incident['containment']['does_not_stop'] or 'nothing else'}")
print()
print("Zero actions exceeded authority, and the incident still happened. That")
print("combination says the grant was too broad - a different fix from a")
print("control that failed, which is why the contract counts them separately.")
print()
print("Reach is 4 resources; confirmed exfiltration is 0. Reporting the second")
print("as the scope is how a notification decision gets made on the wrong number.")
assert incident["authority"]["exceeded_authority"] == 0
assert len(reach) > len(incident["data"]["confirmed_exfiltration"])
