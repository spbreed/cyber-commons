"""Identity and delegation — RFC 8693 token exchange, enforced.

Three jobs:

1. Mint traveller tokens and each agent's workload-identity token.
2. Exchange (user token + agent token) for a short-lived, down-scoped token
   carrying an `act` claim — the agent acting on behalf of the human.
3. Let a resource server **enforce** that token: signature, audience, scope,
   registered actor, expiry.

Step 3 is the one most systems skip. They log the actor claim and act anyway,
which makes the delegation chain a description of what happened rather than a
control over it. A2.3 is the lesson; this is the code it reads.

PyJWT is the only non-stdlib import here, and it is only used to sign and
verify. If it is missing the module still imports, so the tree can be scanned
on a machine with nothing installed.
"""
# step:file G1.3
import hashlib
import json
import time
import uuid

from . import config
# step:A2.1 add
from . import registry
# step:A2.1 end

# Broad on purpose. PyJWT is optional here — the tree must scan on a machine
# with nothing installed — and "not installed" is not the only way this import
# fails. A PyJWT whose `cryptography` wheel does not match the interpreter
# raises from the Rust extension, not ModuleNotFoundError, and catching only
# the tidy case turns a broken wheel on somebody's laptop into a stack trace
# they read as a broken repository.
try:
    import jwt                       # PyJWT
    from jwt import InvalidTokenError
except Exception:                    # noqa: BLE001 — scanning, not running
    jwt = None

    class InvalidTokenError(Exception):
        pass


class IdentityError(Exception):
    """Authentication or delegation policy was violated."""


def _require_jwt():
    if jwt is None:
        raise IdentityError(
            "PyJWT is not installed. The tree scans without it; running the "
            "system needs `pip install -r cybertravels/requirements.txt`.")


# --------------------------------------------------------------------------- #
# Minting
# --------------------------------------------------------------------------- #
def mint_user_token(username: str) -> str:
    """A session token for a person. Audience is the orchestrator and nothing
    downstream: it grants the right to *invoke an agent*, not to touch a
    booking."""
    _require_jwt()
    user = config.USERS.get(username)
    if not user:
        raise IdentityError(f"unknown user: {username}")
    now = int(time.time())
    return jwt.encode({
        "iss": config.IDP_ISSUER,
        "sub": username,
        "aud": config.AUD_BFF,
        "role": user["role"],
        "scope": "agent:invoke",
        "iat": now,
        "exp": now + config.USER_TOKEN_TTL,
        "jti": uuid.uuid4().hex,
    }, config.IDP_SECRET, algorithm=config.JWT_ALG)


def mint_agent_token(agent: str) -> str:
    """The agent's own workload identity — the actor token. Never tied to a
    person, obtained at startup, and the reason an audit row can say *which*
    agent acted rather than "the platform"."""
    _require_jwt()
    spiffe_id = config.AGENT_IDS.get(agent)
    if not spiffe_id:
        raise IdentityError(f"unknown agent: {agent}")
    now = int(time.time())
    return jwt.encode({
        "iss": config.IDP_ISSUER,
        "sub": spiffe_id,
        "aud": "token-exchange",
        "typ": "agent-workload",
        "iat": now,
        "exp": now + config.AGENT_TOKEN_TTL,
    }, config.IDP_SECRET, algorithm=config.JWT_ALG)


# --------------------------------------------------------------------------- #
# RFC 8693 exchange
# --------------------------------------------------------------------------- #
# step:A2.4 add
def bind_call(tool: str, args: dict) -> str:
    """A handle over the exact call this token is for.

    Canonical and sorted, so two honest machines agree. It closes **replay**,
    not authorisation: a token minted for `get_booking(2)` cannot be reused for
    `get_booking(3)`, and it says nothing about whether booking 2 is yours.
    That gap is real, it is rows 1 and 4 of `LABELS.md`, and B2.3 is where it
    gets found. A control that looks like it closes something it does not is
    worse than an absent one.
    """
    payload = json.dumps([tool, {k: args[k] for k in sorted(args)
                                 if k != "auth_token"}],
                         sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]
# step:A2.4 end


def token_exchange(subject_token: str, actor_token: str,
                   audience: str, scope: str,
                   # step:A2.4 add
                   call_binding: str | None = None,
                   # step:A2.4 end
                   ) -> dict:
    """User token + agent token -> one delegated token, for one call.

    Enforced here, in order:
      * the subject token is valid and authorised to invoke an agent
      * the actor token is valid and names a *registered* workload identity
      * the requested scope is inside what the subject's role may delegate

    The result keeps `sub` as the human and records the agent in `act`. It is
    addressed to exactly one audience, carries exactly one scope, and expires
    in two minutes.
    """
    _require_jwt()
    try:
        subj = jwt.decode(subject_token, config.IDP_SECRET,
                          algorithms=[config.JWT_ALG], audience=config.AUD_BFF)
    except InvalidTokenError as e:
        raise IdentityError(f"invalid subject token: {e}")
    if subj.get("scope") != "agent:invoke":
        raise IdentityError("this user may not invoke an agent")

    try:
        act = jwt.decode(actor_token, config.IDP_SECRET,
                         algorithms=[config.JWT_ALG], audience="token-exchange")
    except InvalidTokenError as e:
        raise IdentityError(f"invalid actor token: {e}")
    # step:A2.1 was
    #~ # Membership in a hand-edited set. It answers "is this one of ours" and
    #~ # nothing else — not when it was approved, and not whether it still is.
    #~ if act.get("sub") not in config.REGISTERED_AGENTS:
    #~     raise IdentityError(
    #~         f"actor is not a registered agent: {act.get('sub')}")
    # step:A2.1 now
    if not registry.active(act.get("sub")):
        raise IdentityError(
            f"actor is not an active registered workload: {act.get('sub')}")
    # step:A2.1 end

    role = subj.get("role")
    allowed = config.ROLE_ALLOWED_SCOPES.get(role, set())
    if scope not in allowed:
        raise IdentityError(
            f"role '{role}' may not delegate '{scope}' "
            f"(allowed: {sorted(allowed)})")

    # step:A2.3 add
    # A chain has to NARROW. If the subject token is itself a delegated token —
    # one agent handing work to another — the new scope must be inside what the
    # parent already held. Without this, hop two can ask for anything the human
    # may delegate, and a chain that widens is a chain that launders authority
    # through an agent rather than passing it on.
    parent_scope = subj.get("scope", "")
    if parent_scope not in ("agent:invoke", "") and scope != parent_scope:
        raise IdentityError(
            f"delegation must narrow: the parent held '{parent_scope}' and "
            f"this asks for '{scope}'")
    # step:A2.3 end

    now = int(time.time())
    claims = {
        "iss": config.IDP_ISSUER,
        "sub": subj["sub"],              # still the human
        # step:A2.3 was
        #~ "act": {"sub": act["sub"]},  # the agent acting for them
        # step:A2.3 now
        # The FULL chain, not just the last hop. `act.act` is RFC 8693's own
        # nesting, and it is what lets an investigator say "the advisor asked
        # the workflow agent, on Dana's behalf" rather than seeing one name.
        "act": ({"sub": act["sub"], "act": subj["act"]} if subj.get("act")
                else {"sub": act["sub"]}),
        # step:A2.3 end
        "aud": audience,                 # one resource server
        "scope": scope,                  # one scope
        "iat": now,
        "exp": now + config.DELEGATED_TOKEN_TTL,
        "jti": uuid.uuid4().hex,
    }
    # step:A2.4 add
    if call_binding is not None:
        claims["cnf"] = call_binding
    # step:A2.4 end
    return {"access_token": jwt.encode(claims, config.IDP_SECRET,
                                       algorithm=config.JWT_ALG),
            "claims": claims}


# --------------------------------------------------------------------------- #
# Enforcement, inside the resource server
# --------------------------------------------------------------------------- #
def verify_delegated(token: str, expected_audience: str,
                     required_scope: str,
                     # step:A2.4 add
                     call_binding: str | None = None,
                     # step:A2.4 end
                     ) -> dict:
    """Refuse to act unless the token is signed, addressed to *this* server,
    carries the required scope, names a registered actor and has not expired.

    Called at the top of every MCP tool. A resource server that trusts the
    orchestrator's word is a resource server with no boundary.
    """
    _require_jwt()
    try:
        claims = jwt.decode(token, config.IDP_SECRET,
                            algorithms=[config.JWT_ALG],
                            audience=expected_audience)
    except InvalidTokenError as e:
        raise IdentityError(f"token rejected: {e}")

    granted = set(str(claims.get("scope", "")).split())
    if required_scope not in granted:
        raise IdentityError(
            f"insufficient scope: need '{required_scope}', have {sorted(granted)}")

    actor = (claims.get("act") or {}).get("sub")
    # step:A2.1 was
    #~ if actor not in config.REGISTERED_AGENTS:
    #~     raise IdentityError(f"unrecognised actor in the chain: {actor}")
    # step:A2.1 now
    # A revoked workload's tokens stop working here rather than at expiry,
    # which is the difference A2.5 builds the lifecycle for.
    if not registry.active(actor):
        raise IdentityError(
            f"actor is not an active registered workload: {actor}")
    # step:A2.1 end
    # step:A2.4 add
    # Bound to one call. A token captured from one tool invocation cannot be
    # replayed against a different one — the resource server recomputes the
    # binding from the arguments it was actually given.
    if call_binding is not None and claims.get("cnf") != call_binding:
        raise IdentityError(
            "token is bound to a different call — replayed, or the arguments "
            "changed between the exchange and the call")
    # step:A2.4 end
    return claims


def actor_chain(claims: dict) -> str:
    """`human => agent`, for an audit row that answers "who did this"."""
    # step:A2.3 was
    #~ actor = (claims.get("act") or {}).get("sub", "?")
    #~ return f"{claims.get('sub', '?')} => {actor}"
    # step:A2.3 now
    # Walks the whole nest, so a two-hop delegation reads as two hops.
    hops, node = [], claims.get("act")
    while node:
        hops.append(node.get("sub", "?"))
        node = node.get("act")
    return " => ".join([claims.get("sub", "?"), *reversed(hops)])
    # step:A2.3 end


# step:A3.1 add
def session_for(user_token: str) -> "Session":
    """The human behind a run, as a Session, for the decision point.

    A3.1's `policy.decide()` needs to know who is asking, and the runtime holds
    a token rather than a session. Decoding it here rather than trusting a
    username passed alongside is the point: the role that policy reads is the
    one the IdP signed, not the one the caller says it has.
    """
    _require_jwt()
    try:
        claims = jwt.decode(user_token, config.IDP_SECRET,
                            algorithms=[config.JWT_ALG],
                            audience=config.AUD_BFF)
    except InvalidTokenError as e:
        raise IdentityError(f"invalid subject token: {e}")
    return Session.from_claims(claims)
# step:A3.1 end


class Session:
    """What a tool sees: the human, their role, and the agent acting for them.

    The tools in `tools/` take this as their first argument. Whether they then
    *use* it is the entire IDOR question, and `LABELS.md` records which ones do.
    """

    __slots__ = ("user_id", "role", "agent", "claims")

    def __init__(self, user_id, role, agent=None, claims=None):
        self.user_id = user_id
        self.role = role
        self.agent = agent
        self.claims = claims or {}

    @classmethod
    def from_claims(cls, claims: dict) -> "Session":
        user = config.USERS.get(claims.get("sub"), {})
        return cls(user_id=claims.get("sub"), role=user.get("role"),
                   agent=(claims.get("act") or {}).get("sub"), claims=claims)

    def __repr__(self):
        return f"<Session {self.user_id} via {self.agent}>"
