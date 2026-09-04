#!/usr/bin/env python3
"""Provision an agent as a SCIM resource whose owner is a reference, then run a leaver event and see which agents survive it.

This is the executable half of the `nhi-lifecycle-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import json

# A SCIM resource for an agent. The protocol is RFC 7644; the schema URN is
# your own extension, in exactly the way the enterprise extension declares
# "manager" for users. Note what "owner" is: a REFERENCE, not a name.
AGENT_SCHEMA = "urn:cybertravels:params:scim:schemas:extension:agent:2.0:Agent"

agent = {
 "schemas": [AGENT_SCHEMA],
 "id": "b7f3a1c2",
 "externalId": "spiffe://cybertravels.com/ns/prod/sa/pricing-agent",
 "displayName": "pricing-agent",
 "active": True,
 "owner": {"value": "sam-2291",
           "$ref": "https://idp.cybertravels.com/scim/v2/Users/sam-2291",
           "display": "sam@cybertravels.com"},
 "registrationExpires": 9000,
 "meta": {"resourceType": "Agent", "created": "2026-01-14T09:02:00Z",
          "lastModified": "2026-01-14T09:02:00Z", "version": 'W/"1"'},
}
print("POST /scim/v2/Agents")
print(json.dumps(agent, indent=1, sort_keys=True))

NOW = 5000

USERS = {                       # what SCIM /Users says about the humans
 "sam-2291":  {"userName": "sam@cybertravels.com",  "active": True},
 "dana-4417": {"userName": "dana@cybertravels.com", "active": True},
}
REGISTRY = {                    # what SCIM /Agents says about the agents
 "spiffe://cybertravels.com/ns/prod/sa/pricing-agent":
    {"active": True, "owner": "sam-2291",  "expires": 9000},
 "spiffe://cybertravels.com/ns/prod/sa/billing-agent":
    {"active": True, "owner": "dana-4417", "expires": 4000},   # lapsed
 "spiffe://cybertravels.com/ns/prod/sa/legacy-agent":
    {"active": True, "owner": None,        "expires": 9000},   # orphan
}

def admit(presented, now=NOW):
    """Checks the ATTESTED identity, then resolves the owner reference."""
    e = REGISTRY.get(presented)
    if e is None:                 return False, "not registered"
    if not e["active"]:           return False, "deprovisioned (active: false)"
    if e["owner"] is None:        return False, "no accountable owner"
    owner = USERS.get(e["owner"])
    if owner is None:             return False, "owner ref dangles"
    if not owner["active"]:       return False, f"owner {owner['userName']} has left"
    if e["expires"] < now:        return False, "registration lapsed"
    return True, f"owner {owner['userName']}"

PRESENTING = [
 "spiffe://cybertravels.com/ns/prod/sa/pricing-agent",
 "spiffe://cybertravels.com/ns/prod/sa/billing-agent",
 "spiffe://cybertravels.com/ns/prod/sa/legacy-agent",
 "spiffe://cybertravels.com/ns/prod/sa/reporting-agent-v2",
]

def sweep(label):
    print(label)
    ok_n = 0
    for ident in PRESENTING:
        ok, why = admit(ident)
        ok_n += ok
        print(f"   {ident.rsplit('/', 1)[-1]:22s}{'admitted' if ok else 'REFUSED':10s}{why}")
    print(f"   -> {ok_n} of {len(PRESENTING)} admitted\n")
    return ok_n

sweep("presenting at the orchestrator:")
print("reporting-agent-v2 is A1.11's rogue: a real process, answering the")
print("protocol correctly, refused because nothing registered it. legacy-agent")
print("is the more common case - registered, running, owned by nobody.")

def scim_patch(collection, rid, ops):
    """RFC 7644 PATCH. Deprovisioning is active:false, not DELETE - the record
    has to survive so that an investigation six months later can still read it."""
    target = collection[rid]
    target.update(ops)
    return {"status": 200, "id": rid, **ops}

print("PATCH /scim/v2/Users/sam-2291")
print(f"   {scim_patch(USERS, 'sam-2291', {'active': False})}\n")

# First, the control absent. This is what a registry that stores the owner as a
# STRING does: nothing joins Sam's leaver event to his agent, so admission has
# no way to learn about it and the agent keeps working indefinitely.
def admit_by_name(presented, now=NOW):
    e = REGISTRY.get(presented)
    if e is None or not e["active"] or e["owner"] is None: return False
    return e["expires"] >= now

still_in = [i.rsplit("/", 1)[-1] for i in PRESENTING if admit_by_name(i)]
print(f"owner stored as a string  -> still admitted: {still_in}")
print("   Sam left this afternoon. His agent holds bookings scope tomorrow,")
print("   next quarter, and until somebody runs an access review.\n")

# Now the same sweep with the owner stored as a $ref, which admit() resolves.
after_leaver = sweep("owner stored as a $ref -> resolved at admission:")
print("pricing-agent was admitted an hour ago and is refused now, on the")
print("strength of an HR event nobody forwarded to the agent platform.\n")

# The orphan query, which is the whole reason for using a protocol rather than
# a wiki page: RFC 7644 filter syntax, one request, no quarterly review.
print('GET /scim/v2/Agents?filter=active eq true and owner pr false')
orphans = sorted(k for k, v in REGISTRY.items()
                 if v["active"] and v["owner"] is None)
print(f'   {len(orphans)} result(s): {[o.rsplit("/", 1)[-1] for o in orphans]}\n')

# Retiring one agent is now one call, and it does not touch the others - the
# thing A1.7's shared service account made impossible.
print("PATCH /scim/v2/Agents/billing-agent")
scim_patch(REGISTRY, "spiffe://cybertravels.com/ns/prod/sa/billing-agent",
           {"active": False})
after = sweep("after retiring exactly one agent:")

assert still_in == ["pricing-agent"], "the string owner should miss the leaver"
assert after_leaver == 0, "the $ref owner should cascade Sam's leaver event"
assert not admit(PRESENTING[0])[0] and "left" in admit(PRESENTING[0])[1]
assert len(orphans) == 1
