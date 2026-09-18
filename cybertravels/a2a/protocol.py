"""Agent-to-agent messaging, with the envelope that makes it reviewable.

CyberTravels has four agents and they talk to each other. The naive version of
that is `messaging/bus.py`, which is still in this tree and still used: a dict
of lists, text in and text out, no sender identity that survives the hop. It is
there because it is what almost every A2A layer looks like at first, and
because A1.7 needs something to fix.

This module is the fix. Three properties, and each one closes a specific way a
peer message goes wrong:

**The sender is named and the naming is signed.** A message carries the
sending agent's workload identity, and the envelope is signed with it. Without
that, "the coding agent asked me to" is a claim the receiving agent cannot
check and an investigator cannot either.

**The human is carried through.** An envelope holds the `on_behalf_of` subject
from the originating request. An agent that hands work to a peer does not get
to launder whose authority it is acting under — that is the hop where a
delegation chain usually breaks, and A2.6 is the lesson.

**A peer's text is data, not instruction.** `content` is always labelled with
its origin when it reaches a model. A message from a peer agent is exactly as
trustworthy as whatever that peer last read, which may have been a vendor
document. Treating a peer as a colleague is how one injected document becomes
four compromised agents.

The envelope is a plain dict so it can be logged, diffed and asserted on. The
signature is an HMAC over the canonical JSON: enough to detect a forged sender
inside one deployment, and explicitly not a substitute for real workload
identity, which A2.1 builds.
"""
# step:file G1.6
import hashlib
import hmac
import json
import time
import uuid

from .. import config

MAX_HOPS = 4          # a cycle between four agents is a cost incident
_INBOX: dict[str, list[dict]] = {}


def _canonical(env: dict) -> bytes:
    body = {k: env[k] for k in sorted(env) if k != "sig"}
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()


def _sign(env: dict) -> str:
    return hmac.new(config.IDP_SECRET.encode(), _canonical(env),
                    hashlib.sha256).hexdigest()


def envelope(from_agent, to_agent, content, *, on_behalf_of,
             origin="agent-conclusion", trace_id="", hops=0):
    """Build a signed A2A envelope. `on_behalf_of` is not optional."""
    if from_agent not in config.AGENT_IDS:
        raise ValueError(f"unknown sending agent: {from_agent}")
    if to_agent not in config.AGENT_IDS:
        raise ValueError(f"unknown receiving agent: {to_agent}")
    env = {
        "id": uuid.uuid4().hex,
        "at": time.time(),
        "from": config.AGENT_IDS[from_agent],
        "to": config.AGENT_IDS[to_agent],
        "on_behalf_of": on_behalf_of,
        "origin": origin,
        "trusted": origin in ("operator", "policy", "agent-conclusion"),
        "content": content,
        "trace_id": trace_id,
        "hops": hops,
    }
    env["sig"] = _sign(env)
    return env


class A2AError(Exception):
    """The envelope did not survive verification."""


def verify(env: dict) -> dict:
    """Check the signature, the registration and the hop ceiling.

    A receiving agent calls this before reading `content`. The hop ceiling is
    not a nicety: four agents that can each call each other will, given one
    ambiguous instruction, and the bill arrives before the loop does.
    """
    if not isinstance(env, dict) or "sig" not in env:
        raise A2AError("not an envelope")
    if not hmac.compare_digest(env["sig"], _sign(env)):
        raise A2AError("signature does not match — sender is not who it says")
    if env.get("from") not in config.REGISTERED_AGENTS:
        raise A2AError(f"unregistered sender: {env.get('from')}")
    if env.get("to") not in config.REGISTERED_AGENTS:
        raise A2AError(f"unregistered recipient: {env.get('to')}")
    if not env.get("on_behalf_of"):
        raise A2AError("no human in the delegation chain")
    if int(env.get("hops", 0)) >= MAX_HOPS:
        raise A2AError(f"hop ceiling reached ({MAX_HOPS})")
    return env


def send(env: dict) -> dict:
    verify(env)
    _INBOX.setdefault(env["to"], []).append(env)
    return env


def receive(agent: str) -> list[dict]:
    """Drain one agent's inbox, verifying every envelope on the way out."""
    spiffe_id = config.AGENT_IDS[agent]
    out, bad = [], []
    for env in _INBOX.pop(spiffe_id, []):
        try:
            out.append(verify(env))
        except A2AError as e:
            bad.append({"envelope": env.get("id"), "reason": str(e)})
    return out + ([{"rejected": bad}] if bad else [])


def as_prompt_block(envelopes) -> str:
    """Render peer messages for a model, labelled. See the module docstring:
    the label is the control."""
    lines = []
    for env in envelopes:
        if "content" not in env:
            continue
        tag = "trusted" if env.get("trusted") else "UNTRUSTED"
        lines.append(f"  [peer {env['from']}, {tag}, origin={env['origin']}] "
                     f"{env['content']}")
    return ("Messages from peer agents:\n" + "\n".join(lines)) if lines else ""
