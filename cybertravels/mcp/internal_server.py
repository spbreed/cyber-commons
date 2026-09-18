"""Internal MCP server — bookings and payments. Ours, and a boundary anyway.

A genuine MCP stdio server. Every tool enforces the delegated token before it
does anything: signature, audience `mcp:internal`, the required scope, a
registered actor, and expiry. Then it audits — allowed or denied.

**The boundary is the point.** This server is written by the same team as the
orchestrator and runs on the same host, and it still refuses to act on the
orchestrator's word. A resource server that trusts its caller because the
caller is "internal" has no boundary, it has a naming convention.

What it does *not* do is fix the tools it calls. `get_booking` and
`issue_refund` are reached with a valid, correctly-scoped token and still
return another traveller's record, because scope authorises the *action* and
nothing here authorises the *object*. That gap is the whole of A2.5, and
LABELS.md records it as rows 1 and 4.

Run standalone against an MCP inspector:

    python -m cybertravels.mcp.internal_server
"""
# step:file G1.2
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from cybertravels import config, db, identity           # noqa: E402
from cybertravels.tools import bookings_api, payments_api  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:  # scanning, not running
    FastMCP = None

AUD = config.AUD_INTERNAL_MCP
mcp = FastMCP("cybertravels-internal") if FastMCP else None


def _guard(auth_token, scope, tool):
    """Verify the delegated token or refuse. Returns the session it implies."""
    try:
        claims = identity.verify_delegated(auth_token, AUD, scope)
    except identity.IdentityError as e:
        db.audit("unverified", tool, AUD, scope, "denied", str(e))
        raise
    return claims, identity.Session.from_claims(claims)


def _tool(fn):
    return mcp.tool()(fn) if mcp else fn


@_tool
def list_my_bookings(auth_token: str) -> str:
    """List the bookings belonging to the traveller this call is on behalf of."""
    claims, session = _guard(auth_token, "bookings:read", "list_my_bookings")
    out = db.rows(bookings_api.list_my_bookings(session))
    db.audit(identity.actor_chain(claims), "list_my_bookings", AUD,
             "bookings:read", "ok", {"count": len(out)})
    return json.dumps(out)


@_tool
def get_booking(auth_token: str, booking_id: int) -> str:
    """Fetch one booking by id."""
    claims, session = _guard(auth_token, "bookings:read", "get_booking")
    row = bookings_api.get_booking(session, booking_id)
    out = dict(row) if row else {"error": "not found"}
    db.audit(identity.actor_chain(claims), "get_booking", AUD, "bookings:read",
             "ok", {"booking_id": booking_id, "owner": out.get("owner_id")})
    return json.dumps(out)


@_tool
def search_bookings(auth_token: str, reference: str) -> str:
    """Search bookings by partial reference."""
    claims, session = _guard(auth_token, "bookings:read", "search_bookings")
    out = db.rows(bookings_api.search_bookings(session, reference))
    db.audit(identity.actor_chain(claims), "search_bookings", AUD,
             "bookings:read", "ok", {"reference": reference, "count": len(out)})
    return json.dumps(out)


@_tool
def cancel_booking(auth_token: str, booking_id: int) -> str:
    """Cancel a booking. High risk — the orchestrator gates this on a human."""
    claims, session = _guard(auth_token, "bookings:write", "cancel_booking")
    bookings_api.cancel_booking(session, booking_id)
    db.conn().commit()
    db.audit(identity.actor_chain(claims), "cancel_booking", AUD,
             "bookings:write", "ok", {"booking_id": booking_id})
    return json.dumps({"booking_id": booking_id, "status": "cancelled"})


@_tool
def issue_refund(auth_token: str, booking_id: int, amount: float) -> str:
    """Refund against a booking. High risk, and on the money path."""
    claims, session = _guard(auth_token, "payments:refund", "issue_refund")
    out = payments_api.issue_refund(session, booking_id, amount)
    db.conn().commit()
    db.audit(identity.actor_chain(claims), "issue_refund", AUD,
             "payments:refund", "ok", out)
    return json.dumps(out)


if __name__ == "__main__":
    if mcp is None:
        sys.exit("the `mcp` package is not installed; see "
                 "cybertravels/requirements.txt")
    mcp.run()
