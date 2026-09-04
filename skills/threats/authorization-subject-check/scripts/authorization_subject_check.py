#!/usr/bin/env python3
"""Show which principal authorisation is actually evaluated against, and what the audit trail can name afterwards.

This is the executable half of the `authorization-subject-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

USERS = {"dana":  {"scopes": {"reports:read"}},
         "priya": {"scopes": {"reports:read", "reports:write", "db:admin"}}}

# the agent authenticates as itself, and needs the union of what any user needs
AGENT_SVC = {"name": "agent-svc", "scopes": {"reports:read", "reports:write", "db:admin"}}

AUDIT = []

def call_tool(caller_identity, on_behalf_of, tool, required_scope):
    """Authorization is checked against the CALLER - which is the agent."""
    allowed = required_scope in caller_identity["scopes"]
    AUDIT.append({"actor": caller_identity["name"], "tool": tool,
                  "allowed": allowed})          # note: no human principal
    return allowed

print(f"{'requester':8s}{'their scopes':44s}{'asked for':16s}allowed?")
for user in sorted(USERS):
    ok = call_tool(AGENT_SVC, user, "drop_table", "db:admin")
    print(f"{user:8s}{str(sorted(USERS[user]['scopes'])):44s}{'db:admin':16s}{ok}")

print("\nAUDIT TRAIL")
for a in AUDIT:
    print(f"   actor={a['actor']:10s} tool={a['tool']:12s} allowed={a['allowed']}")

print("\ndana holds reports:read only, and her request reached db:admin.")
print("The authorization decision was made about the agent, not about her.")
print()
print("Now answer 'which user caused the table to be dropped' from that trail.")
print("You cannot: every row says agent-svc. Privilege and attribution failed")
print("in the same step, which is what makes this different from a human with")
print("too much access.")
assert all(a["allowed"] for a in AUDIT)
assert all("dana" not in str(a) for a in AUDIT)
