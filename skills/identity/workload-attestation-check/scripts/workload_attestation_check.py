#!/usr/bin/env python3
"""Show what an identity service does with an unattested process, an unregistered image, and a credential presented from the wrong node or after expiry.

This is the executable half of the `workload-attestation-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import hashlib, time

PLATFORM_TRUTH = {          # only the platform can observe these
 "proc-1": {"image": "reports-agent@sha256:aa11", "namespace": "prod", "node": "n-7"},
 "proc-2": {"image": "billing-agent@sha256:bb22", "namespace": "prod", "node": "n-7"},
}

def platform_attest(pid):
    """The platform signs a statement about a process it actually started."""
    facts = PLATFORM_TRUTH.get(pid)
    if not facts:
        return None                       # cannot attest a process it did not start
    payload = f"{pid}|{facts['image']}|{facts['namespace']}"
    return {"claims": facts, "sig": hashlib.sha256(payload.encode()).hexdigest()[:16]}

REGISTERED = {"reports-agent@sha256:aa11": "spiffe://corp/reports-agent"}

def issue_credential(attestation, now=1000, ttl=300):
    """Exchange an attestation for a short-lived, workload-bound credential."""
    if not attestation:
        return None, "no attestation - unattested process"
    identity = REGISTERED.get(attestation["claims"]["image"])
    if not identity:
        return None, "image is not registered to any identity"
    return {"identity": identity, "expires": now + ttl,
            "bound_to": attestation["claims"]["node"]}, "issued"

for pid in ("proc-1", "proc-2", "proc-stolen"):
    cred, why = issue_credential(platform_attest(pid))
    print(f"   {pid:14s}{(cred['identity'] if cred else '-'):32s}{why}")

# a stolen credential presented from another node
stolen, _ = issue_credential(platform_attest("proc-1"))
def present(cred, from_node, now):
    if now > cred["expires"]:            return False, "expired"
    if from_node != cred["bound_to"]:    return False, f"bound to {cred['bound_to']}"
    return True, "accepted"

print()
for node, now in (("n-7", 1100), ("n-9", 1100), ("n-7", 2000)):
    ok, why = present(stolen, node, now)
    print(f"   presented from {node} at t={now}: {'ok' if ok else 'REFUSED'} ({why})")
print()
print("Copying the credential does not help: it is bound to a node and expires")
print("in five minutes. Copying the image does not help either - proc-2 is a")
print("real process and still gets nothing, because its image is not registered.")
assert issue_credential(platform_attest("proc-stolen"))[0] is None
assert not present(stolen, "n-9", 1100)[0]
