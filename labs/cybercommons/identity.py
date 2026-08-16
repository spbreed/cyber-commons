"""Agent identity: delegation that survives audit, and the ways it usually doesn't.

Modelled on RFC 8693 token exchange, in the standard library, so the lesson runs
without a Keycloak. The two rules that make a chain auditable are enforced in
`exchange()` and nowhere else:

  1. **Subset of what was presented.** You cannot hand on authority you were not
     given.
  2. **Within the actor's own ceiling.** You cannot hand on authority you are
     not permitted to hold, even if the caller offered it.

Drop either rule and the chain still *looks* fine — which is exactly why the
anti-patterns below (`impersonate`) are the default in real deployments.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

# What each actor is allowed to hold at most, regardless of who asks.
GRANTS: dict[str, set[str]] = {
    "alice":          {"repo:read", "repo:write", "deploy:prod", "secrets:read"},
    "reviewer-agent": {"repo:read", "repo:comment"},
    "patch-agent":    {"repo:read", "repo:write"},
    "deploy-agent":   {"repo:read", "deploy:staging"},
}


class DelegationError(Exception):
    """Raised when a hop would widen authority. Refusing is the feature."""


@dataclass
class Token:
    """A bearer token whose `act` chain records *who acted through whom*."""
    sub: str                                  # the principal the action is for
    actor: str                                # who is actually holding it now
    scopes: set[str]
    act: dict | None = None                   # nested chain of prior actors
    issued: float = field(default_factory=time.time)
    ttl: float = 300.0

    @property
    def expired(self) -> bool:
        return time.time() - self.issued > self.ttl

    def chain(self) -> list[str]:
        """Actors from the original principal outward: alice → reviewer → patch.

        The nested `act` claim is stored most-recent-first, so it is reversed
        here — getting that backwards is one of the two ways an audit trail
        misleads. The other is double-counting the principal: on the first hop
        the innermost `act.actor` *is* the principal, so prepending `sub`
        unconditionally renders `alice → alice → patch-agent`. The head check
        below is what keeps a minted token reading as plain `alice`.
        """
        out, node = [], self.act
        while node:
            out.append(node["actor"])
            node = node.get("act")
        chain = list(reversed(out)) + [self.actor]
        if chain[0] != self.sub:
            chain.insert(0, self.sub)
        return chain

    def fingerprint(self) -> str:
        blob = json.dumps({"sub": self.sub, "actor": self.actor,
                           "scopes": sorted(self.scopes), "act": self.act},
                          sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:12]

    def describe(self) -> str:
        return (f"{' → '.join(self.chain())}\n"
                f"    scopes {sorted(self.scopes)}  fp={self.fingerprint()}")


def mint(principal: str, scopes: set[str] | None = None) -> Token:
    """The first token. A human principal, no actor chain yet."""
    allowed = GRANTS.get(principal, set())
    want = scopes if scopes is not None else set(allowed)
    if not want <= allowed:
        raise DelegationError(f"{principal} cannot hold {sorted(want - allowed)}")
    return Token(sub=principal, actor=principal, scopes=set(want))


def exchange(presented: Token, new_actor: str, scopes: set[str]) -> Token:
    """One delegation hop. Both narrowing rules are enforced here.

    Returns a token whose `act` claim nests the presenting actor, so the audit
    trail can name every hop rather than just the last one.
    """
    if presented.expired:
        raise DelegationError(f"presented token expired ({presented.ttl}s ttl)")
    if not scopes <= presented.scopes:
        raise DelegationError(
            f"widening refused: {sorted(scopes - presented.scopes)} not in the "
            f"presented token {sorted(presented.scopes)}")
    ceiling = GRANTS.get(new_actor, set())
    if not scopes <= ceiling:
        raise DelegationError(
            f"widening refused: {new_actor} may never hold "
            f"{sorted(scopes - ceiling)} (its ceiling is {sorted(ceiling)})")
    return Token(sub=presented.sub, actor=new_actor, scopes=set(scopes),
                 act={"actor": presented.actor, "act": presented.act},
                 ttl=min(presented.ttl, 300.0))


def impersonate(principal: str, actor: str, scopes: set[str]) -> Token:
    """The anti-pattern: the agent simply *becomes* the human.

    No `act` claim, so every log line says the human did it. This is A2.3
    (Shadow Autonomy) and it is not a bug in anyone's code — it is what you get
    when an agent is handed a service account and told to get on with it.
    """
    return Token(sub=principal, actor=principal, scopes=set(scopes), act=None)


# ------------------------------------------------------------------ revocation
class Registry:
    """A non-human identity registry with per-actor revocation.

    Revoking one agent must not take down the others. If your only lever is
    rotating a shared secret, you do not have identities, you have a password.
    """

    def __init__(self) -> None:
        self.revoked: set[str] = set()
        self.issued: list[Token] = []

    def record(self, t: Token) -> Token:
        self.issued.append(t)
        return t

    def revoke(self, actor: str) -> int:
        self.revoked.add(actor)
        return sum(1 for t in self.issued if actor in t.chain())

    def valid(self, t: Token) -> tuple[bool, str]:
        if t.expired:
            return False, "expired"
        for a in t.chain():
            if a in self.revoked:
                return False, f"actor '{a}' revoked — whole chain invalid"
        return True, "ok"

    def inventory(self) -> list[dict]:
        """The NHI inventory question: what identities exist, holding what?"""
        seen: dict[str, dict] = {}
        for t in self.issued:
            row = seen.setdefault(t.actor, {"actor": t.actor, "tokens": 0,
                                            "scopes": set(), "revoked": False})
            row["tokens"] += 1
            row["scopes"] |= t.scopes
            row["revoked"] = t.actor in self.revoked
        return [{**r, "scopes": sorted(r["scopes"])} for r in seen.values()]


# ------------------------------------------------------- just-in-time authority
@dataclass
class JITGrant:
    """Authority that exists only for the duration of one justified task.

    Standing privilege is the thing being replaced. The audit question shifts
    from "who has deploy:prod?" (always the same dull list) to "who held it, for
    what, for how long?" — which is answerable and actually interesting.
    """
    actor: str
    scope: str
    reason: str
    seconds: float = 60.0
    granted: float = field(default_factory=time.time)

    @property
    def active(self) -> bool:
        return time.time() - self.granted < self.seconds

    def audit_line(self) -> str:
        state = "ACTIVE" if self.active else "expired"
        return (f"{self.actor:16s} {self.scope:16s} {state:8s} "
                f"{self.seconds:5.0f}s  reason={self.reason!r}")
