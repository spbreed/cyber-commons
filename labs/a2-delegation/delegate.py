#!/usr/bin/env python3
"""Lab A2.5 — a three-hop delegation chain that survives audit.

Implements the shape of RFC 8693 token exchange with the `act` (actor) claim, so
you can see *in the token* who is acting on whose behalf, and prove that each hop
is strictly attenuated. No Keycloak, no Docker, no network: stdlib only, so the
lesson is reachable on any laptop.

The chapter's full lab runs this against real Keycloak; this file is the same
mechanics with the infrastructure removed, and it is what the tests exercise.

    python3 delegate.py chain          # build + print a 3-hop chain
    python3 delegate.py verify         # prove attenuation holds at every hop
    python3 delegate.py escalate       # try to widen scope mid-chain (must fail)
    python3 delegate.py impersonate    # the anti-pattern, and why audit dies
    python3 delegate.py revoke reviewer-agent   # revoke one actor, not the chain
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sys
import time

SECRET = b"lab-signing-key-not-for-production"

# The authorization server's view of what each principal may ever hold. A hop can
# only ever *narrow* from here — this is the "attenuation by construction" idea
# from A1.3, expressed as data.
GRANTS = {
    "user:alice":      {"repo:read", "repo:write", "deploy:prod", "secrets:read"},
    "reviewer-agent":  {"repo:read", "repo:write"},
    "patch-agent":     {"repo:read"},
}

REVOKED: set[str] = set()


# ------------------------------------------------------------------ JWT (mini)
def _b64(d: bytes) -> str:
    return base64.urlsafe_b64encode(d).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign(payload: dict) -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    body = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    sig = _b64(hmac.new(SECRET, f"{header}.{body}".encode(), hashlib.sha256).digest())
    return f"{header}.{body}.{sig}"


def verify_signature(token: str) -> dict:
    header, body, sig = token.split(".")
    expect = _b64(hmac.new(SECRET, f"{header}.{body}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, expect):
        raise ValueError("signature invalid")
    return json.loads(_unb64(body))


# ------------------------------------------------------------- token exchange
def issue_root(subject: str, scope: set[str], ttl: int = 900) -> str:
    """The human's own token. No `act` claim: nobody is acting for anyone yet."""
    if not scope <= GRANTS[subject]:
        raise ValueError(f"{subject} was never granted {scope - GRANTS[subject]}")
    now = int(time.time())
    return sign({"sub": subject, "scope": sorted(scope), "iat": now, "exp": now + ttl})


def exchange(token: str, actor: str, requested: set[str], ttl: int = 300) -> str:
    """RFC 8693-style exchange: `actor` asks to act on behalf of the token's subject.

    Two rules make the result auditable and safe:
      1. the new scope must be a SUBSET of the presented token's scope (attenuation)
      2. it must also be within what `actor` may ever hold (the actor's own ceiling)
    and the presented token's identity is preserved as a nested `act` claim, so the
    whole chain is readable afterwards.
    """
    claims = verify_signature(token)
    if claims["exp"] < time.time():
        raise ValueError("presented token expired")
    for principal in actors_in(claims) + [claims["sub"]]:
        if principal in REVOKED:
            raise ValueError(f"principal '{principal}' is revoked")

    presented = set(claims["scope"])
    if not requested <= presented:
        raise ValueError(f"escalation refused: {sorted(requested - presented)} not in presented scope")
    ceiling = GRANTS.get(actor, set())
    if not requested <= ceiling:
        raise ValueError(f"actor ceiling refused: {sorted(requested - ceiling)} beyond {actor}'s grant")

    now = int(time.time())
    return sign({
        "sub": claims["sub"],                 # the chain still names the human
        "scope": sorted(requested),
        "iat": now, "exp": now + ttl,
        # nested actor chain — the innermost `act` is the most recent delegate
        "act": {"sub": actor, **({"act": claims["act"]} if "act" in claims else {})},
    })


def actors_in(claims: dict) -> list[str]:
    out, act = [], claims.get("act")
    while act:
        out.append(act["sub"])
        act = act.get("act")
    return out


def revoke(principal: str) -> None:
    REVOKED.add(principal)


# ------------------------------------------------------------------ scenarios
def describe(token: str) -> str:
    c = verify_signature(token)
    # actors_in() returns most-recent-first (innermost act is the latest hop);
    # reverse it so the arrows read in delegation order: who handed to whom.
    chain = " → ".join([c["sub"]] + list(reversed(actors_in(c))))
    return f"  scope={sorted(c['scope'])}\n  chain: {chain}"


def cmd_chain() -> int:
    t0 = issue_root("user:alice", {"repo:read", "repo:write", "deploy:prod"})
    print("hop 0 — alice's own token"); print(describe(t0))
    t1 = exchange(t0, "reviewer-agent", {"repo:read", "repo:write"})
    print("\nhop 1 — reviewer-agent acting for alice"); print(describe(t1))
    t2 = exchange(t1, "patch-agent", {"repo:read"})
    print("\nhop 2 — patch-agent acting for reviewer-agent acting for alice"); print(describe(t2))
    print("\nfull claims of the final token:")
    print(json.dumps(verify_signature(t2), indent=1))
    return 0


def cmd_verify() -> int:
    t0 = issue_root("user:alice", {"repo:read", "repo:write", "deploy:prod"})
    t1 = exchange(t0, "reviewer-agent", {"repo:read", "repo:write"})
    t2 = exchange(t1, "patch-agent", {"repo:read"})
    scopes = [set(verify_signature(t)["scope"]) for t in (t0, t1, t2)]
    ok = all(scopes[i + 1] < scopes[i] for i in range(len(scopes) - 1))
    for i, s in enumerate(scopes):
        print(f"  hop {i}: {sorted(s)}")
    print(f"\nstrictly attenuating at every hop: {ok}")
    print("deploy:prod reachable by patch-agent:",
          "deploy:prod" in scopes[-1], "(must be False)")
    return 0 if ok and "deploy:prod" not in scopes[-1] else 1


def cmd_escalate() -> int:
    t0 = issue_root("user:alice", {"repo:read"})
    t1 = exchange(t0, "reviewer-agent", {"repo:read"})
    print("reviewer-agent holds:", verify_signature(t1)["scope"])
    try:
        exchange(t1, "patch-agent", {"repo:read", "repo:write"})
        print("ESCALATION SUCCEEDED — the chain is broken"); return 1
    except ValueError as e:
        print(f"escalation refused: {e}")
        print("\nNote it was refused by the *token*, not by an application check\n"
              "that an injected instruction could talk its way past.")
        return 0


def cmd_impersonate() -> int:
    """The anti-pattern: hand the agent the human's token unchanged."""
    t0 = issue_root("user:alice", {"repo:read", "repo:write", "deploy:prod"})
    c = verify_signature(t0)
    print("agent presents alice's token verbatim:")
    print(f"  sub={c['sub']}  act={c.get('act', 'NONE')}  scope={sorted(c['scope'])}")
    print("\nWhat the audit log will say : 'alice deployed to prod'")
    print("What actually happened      : an agent did, and you cannot tell which one")
    print("Blast radius                : alice's entire grant, including deploy:prod")
    print("\nThis is Shadow Autonomy (A2.3). Nothing here is technically broken —\n"
          "which is exactly why it survives in production for years.")
    return 0


def cmd_revoke(target: str) -> int:
    t0 = issue_root("user:alice", {"repo:read", "repo:write"})
    t1 = exchange(t0, "reviewer-agent", {"repo:read", "repo:write"})
    t_other = exchange(t0, "patch-agent", {"repo:read"})
    revoke(target)
    print(f"revoked: {target}\n")
    for name, tok in (("reviewer-agent chain", t1), ("patch-agent chain", t_other)):
        try:
            exchange(tok, "patch-agent", {"repo:read"})
            print(f"  {name}: still usable")
        except ValueError as e:
            print(f"  {name}: dead — {e}")
    print("\nOne actor revoked, the other unaffected: the A2.4 deliverable.")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    return {
        "chain": cmd_chain, "verify": cmd_verify, "escalate": cmd_escalate,
        "impersonate": cmd_impersonate,
    }.get(cmd, lambda: cmd_revoke(sys.argv[2] if len(sys.argv) > 2 else "reviewer-agent"))() \
        if cmd != "revoke" else cmd_revoke(sys.argv[2] if len(sys.argv) > 2 else "reviewer-agent")


if __name__ == "__main__":
    sys.exit(main())
