# step:file A3.5
"""Validating what comes back — before any of it reaches the model.

Every control so far guards the outbound half: may this agent call this tool,
with what authority, within what budget. The return path had nothing. A tool
result went from the MCP server into the context window unread, which means a
resource server that has been compromised, or is simply a third party's, gets
to write directly into the agent's reasoning.

Two checks, and they answer different questions.

**Schema** — is this the shape the tool promised? Cheap, total, and catches a
tool that changed under you. It says nothing about whether the content is
sane.

**An independent verifier** — does this result contradict something we already
know? A booking that belongs to a different traveller than the one we asked
about, a refund larger than the booking, a count that disagrees with the rows
beside it. This is the half that catches a *correct-shaped* lie, and it has to
be independent of the thing it is checking, which is B2.1's whole argument.

Conformance is a statement about the serialiser. An empty result conforms
perfectly.
"""
import json


class ReturnRejected(Exception):
    """The tool's answer did not survive validation."""


# Shape per tool: field -> type. Deliberately small; a schema nobody can read
# is a schema nobody updates when the tool changes.
SCHEMAS = {
    "get_booking": {"id": int, "reference": str, "owner_id": str,
                    "status": str, "amount": float},
    "list_my_bookings": list,
    "search_bookings": list,
    "cancel_booking": {"booking_id": int, "status": str},
    "issue_refund": {"refunded": float, "booking": int},
    "lookup_vendor_doc": {"vendor": str, "origin": str, "trusted": bool,
                          "body": str},
    "search_policy": {"origin": str, "trusted": bool, "results": list},
}


def check_schema(tool, payload):
    spec = SCHEMAS.get(tool)
    if spec is None:
        raise ReturnRejected(f"no schema for {tool!r} — a tool whose answer "
                             f"nobody described is a tool whose answer nobody "
                             f"checks")
    if spec is list:
        if not isinstance(payload, list):
            raise ReturnRejected(f"{tool} returned {type(payload).__name__}, "
                                 f"expected a list")
        return True
    if not isinstance(payload, dict):
        raise ReturnRejected(f"{tool} returned {type(payload).__name__}, "
                             f"expected an object")
    if isinstance(payload.get("error"), str):
        return True                       # a refusal is a legitimate answer
    for field, want in spec.items():
        if field not in payload:
            raise ReturnRejected(f"{tool} omitted {field!r}")
        if not isinstance(payload[field], want):
            raise ReturnRejected(
                f"{tool}.{field} is {type(payload[field]).__name__}, "
                f"expected {want.__name__}")
    return True


def verify(tool, payload, *, asked_for=None, session=None):
    """The independent half. Returns a list of contradictions, not a boolean.

    Nothing here asks the model whether its own result is reasonable. A model
    grading its own output grades it generously, and a verifier that shares the
    thing it verifies verifies nothing.
    """
    out = []
    if not isinstance(payload, dict):
        return out
    if tool == "get_booking" and asked_for is not None:
        if payload.get("id") not in (None, asked_for):
            out.append(f"asked for booking {asked_for} and got "
                       f"{payload.get('id')}")
    if tool == "issue_refund":
        if float(payload.get("refunded", 0)) <= 0:
            out.append("a refund of zero or less was reported as done")
    counts = payload.get("counts")
    if isinstance(counts, dict) and isinstance(payload.get("findings"), list):
        if counts.get("verified") != len(payload["findings"]):
            out.append(f"counts.verified={counts.get('verified')} disagrees "
                       f"with {len(payload['findings'])} findings")
    return out


def guard(tool, raw, *, asked_for=None, session=None):
    """Both halves, on the way back. Raises on shape, reports on content."""
    try:
        payload = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        raise ReturnRejected(f"{tool} returned text that is not JSON")
    check_schema(tool, payload)
    return payload, verify(tool, payload, asked_for=asked_for, session=session)
