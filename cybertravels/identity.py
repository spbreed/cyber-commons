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
import time
import uuid

from . import config

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
def token_exchange(subject_token: str, actor_token: str,
                   audience: str, scope: str) -> dict:
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
    if act.get("sub") not in config.REGISTERED_AGENTS:
        raise IdentityError(f"actor is not a registered agent: {act.get('sub')}")

    role = subj.get("role")
    allowed = config.ROLE_ALLOWED_SCOPES.get(role, set())
    if scope not in allowed:
        raise IdentityError(
            f"role '{role}' may not delegate '{scope}' "
            f"(allowed: {sorted(allowed)})")

    now = int(time.time())
    claims = {
        "iss": config.IDP_ISSUER,
        "sub": subj["sub"],              # still the human
        "act": {"sub": act["sub"]},      # the agent acting for them
        "aud": audience,                 # one resource server
        "scope": scope,                  # one scope
        "iat": now,
        "exp": now + config.DELEGATED_TOKEN_TTL,
        "jti": uuid.uuid4().hex,
    }
    return {"access_token": jwt.encode(claims, config.IDP_SECRET,
                                       algorithm=config.JWT_ALG),
            "claims": claims}


# --------------------------------------------------------------------------- #
# Enforcement, inside the resource server
# --------------------------------------------------------------------------- #
def verify_delegated(token: str, expected_audience: str,
                     required_scope: str) -> dict:
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
    if actor not in config.REGISTERED_AGENTS:
        raise IdentityError(f"unrecognised actor in the chain: {actor}")
    return claims


def actor_chain(claims: dict) -> str:
    """`human => agent`, for an audit row that answers "who did this"."""
    actor = (claims.get("act") or {}).get("sub", "?")
    return f"{claims.get('sub', '?')} => {actor}"


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
