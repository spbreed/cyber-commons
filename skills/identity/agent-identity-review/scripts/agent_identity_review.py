#!/usr/bin/env python3
"""Separate the user, the workload and the agent instance, and use each for what only it can answer.

This is the executable half of the `agent-identity-review` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Principal:
    user: str            # the human who asked
    workload: str        # the process, from platform attestation
    instance: str        # this run of this agent
    scopes: frozenset    # the workload's ceiling

def authorize(p, required):
    """Authorization is about the WORKLOAD: what may this agent ever do."""
    return required in p.scopes

def attribute(p, action):
    """Attribution is about the USER: who caused this."""
    return {"action": action, "caused_by": p.user,
            "performed_by": p.workload, "run": p.instance}

def memory_key(p, workspace):
    """Memory is scoped to the USER, not the workspace - this is the write that
    let A1.4 leak a poisoned note between people."""
    return f"{workspace}:{p.user}"

dana = Principal("dana@corp", "reports-agent", "run-8812",
                 frozenset({"reports:read"}))
priya = Principal("priya@corp", "reports-agent", "run-8813",
                  frozenset({"reports:read"}))

print(f"{'request':28s}{'authorized?':13s}attributed to")
for p, need in ((dana, "reports:read"), (dana, "db:admin")):
    ok = authorize(p, need)
    rec = attribute(p, need)
    print(f"{p.user + ' -> ' + need:28s}{str(ok):13s}{rec['caused_by']} via {rec['performed_by']}")

print("\nmemory keys - the same workspace, two users:")
print(f"   dana  -> {memory_key(dana, 'acme')}")
print(f"   priya -> {memory_key(priya, 'acme')}")
print(f"   shared? {memory_key(dana, 'acme') == memory_key(priya, 'acme')}")
print()
print("db:admin is refused because the WORKLOAD never held it - so no user can")
print("borrow it through the agent, which is A1.6 closed. The audit line names")
print("dana, which is A1.14 closed. And a note written in dana's session cannot")
print("be read back in priya's, which is A1.4 closed.")
assert not authorize(dana, "db:admin")
assert memory_key(dana, "acme") != memory_key(priya, "acme")
