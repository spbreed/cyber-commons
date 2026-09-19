# step:file B3.3
"""Egress control — an allow-list at the boundary the agent actually crosses.

Up to here CyberTravels has had no egress control at all. Nothing in the tree
constrains where the agent reaches: `_stubs.HTTP` will take any URL, and the
only reason nothing leaves is that the stub is inert. That absence is the
starting position this lesson fills in.

Two things make agent egress different from ordinary egress, and both are why
a network-level allow-list alone is not enough:

**The destination is chosen at run time by a model.** A firewall rule written
against a deployment is written against a set of destinations somebody decided
in advance. An agent picks one per call, from text it just read.

**Exfiltration does not need a new destination.** A vendor API the agent is
supposed to call is a perfectly good channel for sending data out — the
allow-list says yes, and the data leaves. So the check is on the destination
*and* on what is being sent, which is the second half teams skip.

Enforced here at the point the agent reaches out, because that is where the
decision is, and noted plainly: a control inside the process an attacker is
influencing is the weaker placement. B3.7 moves it to a gateway.
"""
import re
from urllib.parse import urlparse


class EgressDenied(Exception):
    """The destination, or what was being sent to it, was refused."""


# Everything CyberTravels legitimately talks to. Nothing else, and no wildcard
# for "internal" — the vendor MCP server runs on our host and is still a third
# party's process.
ALLOWED_HOSTS = {
    "api.skyline-air.example",
    "api.northwind-rail.example",
    "idp.cybertravels.local",
}

# Shapes that must not leave, whatever the destination. This is not a filter
# that catches a determined exfiltration — an agent that encodes a token is
# past it — and it is worth having anyway, because the common case is not
# determined, it is a summary that happened to include a credential.
NEVER_SEND = [
    (re.compile(r"\bnvapi-[A-Za-z0-9_\-]{8,}"), "an NVIDIA API key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{16,}"), "an API key"),
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\."), "a JWT"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "a private key"),
]


def check(url, body=""):
    """Allow or refuse one outbound call. Returns a record either way."""
    host = (urlparse(url).hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise EgressDenied(
            f"destination {host!r} is not on the egress allow-list. The agent "
            f"chose it at run time, which is exactly the case a deployment-time "
            f"firewall rule does not cover")
    for pattern, what in NEVER_SEND:
        if pattern.search(body or ""):
            raise EgressDenied(
                f"refused to send {what} to {host} — the destination is "
                f"allowed and the payload is not, which is the half of egress "
                f"control an allow-list alone does not do")
    return {"host": host, "allowed": True, "bytes": len(body or "")}


def would_allow(url):
    """Non-raising, for a report rather than a call."""
    return (urlparse(url).hostname or "").lower() in ALLOWED_HOSTS
