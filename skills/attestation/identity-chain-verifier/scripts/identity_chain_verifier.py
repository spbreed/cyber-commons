#!/usr/bin/env python3
"""Exchange a token so the subject stays the user and the actor names the agent, then check the certificate binding downstream.

This is the executable half of the `identity-chain-verifier` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import base64, hashlib, hmac, json

def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

# --- layer 1: the SVID -----------------------------------------------------
# A real X.509-SVID is a certificate carrying the SPIFFE ID in its URI SAN.
# Here it is the DER bytes standing in for one. The only property the protocol
# needs is that the thumbprint is DERIVED from the certificate rather than
# asserted alongside it.
class SVID:
    def __init__(self, spiffe_id, der):
        self.spiffe_id, self.der = spiffe_id, der
    @property
    def thumbprint(self):                        # RFC 8705 x5t#S256
        return b64u(hashlib.sha256(self.der).digest())

AGENT = SVID("spiffe://cybertravels.com/ns/prod/sa/agent-alpha",
             b"cert-agent-alpha")

# --- layer 2: RFC 8693 token exchange --------------------------------------
CEILINGS = {                        # what each actor may EVER hold
 "alice@cybertravels.com":
    {"bookings:read", "bookings:write", "payments:refund"},
 "spiffe://cybertravels.com/ns/prod/sa/orchestrator":
    {"bookings:read", "bookings:write"},
 "spiffe://cybertravels.com/ns/prod/sa/agent-alpha":
    {"bookings:read"},
}
SIGNING_KEY = b"demo-key-not-a-secret"

class DelegationError(Exception): pass

def exchange(subject_token, actor, requested):
    """RFC 8693: subject_token is the user, actor_token is the agent's SVID."""
    requested = set(requested)
    presented = set(subject_token["scope"].split())
    if not requested <= presented:                                 # rule 1
        raise DelegationError(
            f"widening: {sorted(requested - presented)} was never presented")
    ceiling = CEILINGS[actor.spiffe_id]
    issued = requested & ceiling                                   # rule 2
    if issued != requested:
        print(f"   ceiling narrowed it: {actor.spiffe_id.rsplit('/', 1)[-1]} "
              f"may never hold {sorted(requested - ceiling)}")
    act = {"sub": actor.spiffe_id}
    if "act" in subject_token:                    # nest the previous hop
        act["act"] = subject_token["act"]
    return {
      "sub": subject_token["sub"],                # STILL the human
      "aud": "https://payments.cybertravels.internal",
      "scope": " ".join(sorted(issued)),
      "act": act,                                 # the agent, and the chain
      "cnf": {"x5t#S256": actor.thumbprint},      # layer 3, stamped here
    }

def sign(claims):
    head = b64u(json.dumps({"alg": "HS256", "typ": "JWT"}, sort_keys=True).encode())
    body = b64u(json.dumps(claims, sort_keys=True).encode())
    mac = hmac.new(SIGNING_KEY, f"{head}.{body}".encode(), hashlib.sha256)
    return f"{head}.{body}.{b64u(mac.digest())}"

user = {"sub": "alice@cybertravels.com",
        "scope": "bookings:read bookings:write payments:refund"}
tok = exchange(user, AGENT, {"bookings:read"})

print("the access token the payments API will actually see:\n")
print(json.dumps(tok, indent=2, sort_keys=True))
print(f"\nas a JWT: {sign(tok)[:78]}...")

# The token above leaked. A debug log, a crash dump, an LLM transcript - it
# does not matter which. Another pod picks it up and replays it.
THIEF = SVID("spiffe://cybertravels.com/ns/prod/sa/scraper", b"cert-scraper")

def serve_bearer(token, _tls_peer):
    """How most services check a token today: is it signed, does it say yes?"""
    return "bookings:read" in token["scope"].split()

def serve_bound(token, tls_peer):
    """RFC 8705: re-derive the thumbprint from THIS connection, first."""
    want = token.get("cnf", {}).get("x5t#S256")
    if want is None:
        raise PermissionError("token is not certificate-bound - refusing")
    if not hmac.compare_digest(want, tls_peer.thumbprint):
        raise PermissionError(
            f"cnf mismatch: issued to {want[:12]}..., presented on a "
            f"connection using {tls_peer.thumbprint[:12]}...")
    return "bookings:read" in token["scope"].split()

print("the legitimate agent, on its own connection:")
print(f"   bearer check : {serve_bearer(tok, AGENT)}")
print(f"   bound  check : {serve_bound(tok, AGENT)}")

print("\nthe same token, replayed by a different pod:")
print(f"   bearer check : {serve_bearer(tok, THIEF)}   <- accepted. a bearer "
      f"token is a password.")
try:
    serve_bound(tok, THIEF)
except PermissionError as e:
    print(f"   bound  check : refused - {e}")

# And the widening attempt: alice really does hold payments:refund, but
# agent-alpha may never hold it, no matter who asks.
print("\nalice asks agent-alpha to issue a refund on her behalf:")
subset_ok = {"payments:refund"} <= set(user["scope"].split())
refund = exchange(user, AGENT, {"payments:refund"})
print(f"   subset-of-presented alone would allow it : {subset_ok}")
print(f"   scope actually issued                    : {refund['scope'] or 'none'}")

assert serve_bearer(tok, THIEF) is True          # the hole
try:
    serve_bound(tok, THIEF)
    raise AssertionError("the binding did not hold")
except PermissionError:
    pass
assert subset_ok and refund["scope"] == ""
assert tok["act"]["sub"].endswith("/sa/agent-alpha")

ORCH = SVID("spiffe://cybertravels.com/ns/prod/sa/orchestrator",
            b"cert-orchestrator")

hop1 = exchange(user, ORCH, {"bookings:read", "bookings:write"})
hop2 = exchange(hop1, AGENT, {"bookings:read"})

def chain(claims):
    """sub is the human; act nests one entry per hop, most recent first."""
    hops, node = [], claims.get("act")
    while node:
        hops.append(node["sub"].rsplit("/", 1)[-1])
        node = node.get("act")
    return " -> ".join([claims["sub"], *reversed(hops)])

print(f"delegation chain : {chain(hop2)}")
print(f"final scope      : {hop2['scope']}")
print(f"bound to         : {hop2['cnf']['x5t#S256'][:16]}...  "
      f"(agent-alpha's certificate, not the orchestrator's)")
assert chain(hop2) == ("alice@cybertravels.com -> orchestrator -> agent-alpha")
assert hop2["cnf"]["x5t#S256"] == AGENT.thumbprint
