"""Agent-to-agent messaging, with the envelope that makes it reviewable.

CyberTravels has four agents and they talk to each other. The naive version of
that is `messaging/bus.py`, which is still in this tree and still used: a dict
of lists, text in and text out, no sender identity that survives the hop. It is
there because it is what almost every A2A layer looks like at first, and
because B1.7 needs something to fix.

This module is the fix. Three properties, and each one closes a specific way a
peer message goes wrong:

**The sender is named and the naming is signed.** A message carries the
sending agent's workload identity, and the envelope is signed with it. Without
that, "the coding agent asked me to" is a claim the receiving agent cannot
check and an investigator cannot either.

**The human is carried through.** An envelope holds the `on_behalf_of` subject
from the originating request. An agent that hands work to a peer does not get
to launder whose authority it is acting under — that is the hop where a
delegation chain usually breaks, and B2.6 is the lesson.

**A peer's text is data, not instruction.** `content` is always labelled with
its origin when it reaches a model. A message from a peer agent is exactly as
trustworthy as whatever that peer last read, which may have been a vendor
document. Treating a peer as a colleague is how one injected document becomes
four compromised agents.

The envelope is a plain dict so it can be logged, diffed and asserted on. The
signature is an HMAC over the canonical JSON: enough to detect a forged sender
inside one deployment, and explicitly not a substitute for real workload
identity, which B2.1 builds.
"""
# step:file A1.6
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


def forward(received: dict, to_agent: str, content, *, origin=None) -> dict:
    """Hand work onward, carrying the chain and spending one hop.

    This is the function the ceiling in `verify` needs in order to mean
    anything. For one release there was no such function: every caller built a
    fresh `envelope()`, which defaults `hops=0`, and nothing anywhere ever
    incremented the counter. `MAX_HOPS` was therefore unreachable in normal
    operation — it could only fire if a caller hand-passed a high number, which
    is the one case an attacker will not do for you. A1.6 taught it as a
    control and the control could not trip.

    Three things travel and one is spent:

    * `on_behalf_of` is carried, never re-minted. An agent passing work to a
      peer does not get to launder whose authority it acts under.
    * `trace_id` is carried, so four hops are one investigation.
    * `origin` defaults to the origin of what was read, because a peer is
      exactly as trustworthy as whatever it last read. Pass it explicitly only
      to *downgrade*.
    * `hops` is spent — this is the increment that was missing.
    """
    verify(received)                     # never forward what you did not check
    sender = _agent_name(received["to"])  # we are the recipient, forwarding on
    out = envelope(sender, to_agent, content,
                   on_behalf_of=received["on_behalf_of"],
                   origin=origin if origin is not None else received["origin"],
                   trace_id=received.get("trace_id", ""),
                   hops=int(received.get("hops", 0)) + 1)
    # Verify what we are about to hand back, not only what we were given.
    # Without this the fourth forward returns an envelope at hops == MAX_HOPS
    # that `send` then refuses — a ceiling that fires one hop late, in the
    # caller, on an object that should never have been built. MAX_HOPS is the
    # number of agents a chain may touch, so the refusal belongs here.
    return verify(out)


def _agent_name(spiffe_id: str) -> str:
    """The short name for a spiffe id, which is what `envelope` takes."""
    for name, sid in config.AGENT_IDS.items():
        if sid == spiffe_id:
            return name
    raise A2AError(f"not one of ours: {spiffe_id}")


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
