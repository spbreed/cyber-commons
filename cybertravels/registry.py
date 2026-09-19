# step:file B2.1
"""The workload identity registry — who the agents are, and how they prove it.

Function G gave each agent a SPIFFE-style name and put the four of them in a
`set` in `config.py`. That was enough to make an audit row name which agent
acted, which was A1.3's point. It is not enough for anything B2 asks:

* the set is edited by hand, so nothing records **when** an identity started
  existing or who approved it;
* membership is the only check, so any process that can read `IDP_SECRET` can
  mint a token for any of the four;
* there is no way to **stop** an identity, so a decommissioned agent's
  credentials keep working until somebody remembers.

This module replaces the set with a registry, and it arrives in three stages —
one per lesson, so the checkpoint at each one contains exactly what that lesson
built:

    B2.1  the registry itself: identities as records rather than strings
    B2.2  issuance against attestation, so there is no first secret to steal
    B2.5  the lifecycle: rotation, revocation, and finding the orphans
"""
import hashlib
import time

from . import config


class RegistryError(Exception):
    """An identity was refused, or asked for that does not exist."""


# One record per workload. `selectors` is the part that matters in B2.2: the
# properties a workload can *demonstrate* rather than assert.
class Workload:
    __slots__ = ("spiffe_id", "selectors", "registered_at", "approved_by",
                 "state", "generation", "retired_at")

    def __init__(self, spiffe_id, selectors, approved_by="alex"):
        self.spiffe_id = spiffe_id
        self.selectors = dict(selectors)
        self.registered_at = time.time()
        self.approved_by = approved_by
        self.state = "active"
        self.generation = 1
        self.retired_at = None

    def as_dict(self):
        return {"spiffe_id": self.spiffe_id, "selectors": self.selectors,
                "state": self.state, "generation": self.generation,
                "approved_by": self.approved_by,
                "registered_at": self.registered_at,
                "retired_at": self.retired_at}

    def __repr__(self):
        return f"<Workload {self.spiffe_id} {self.state} g{self.generation}>"


# The four agents CyberTravels runs, as records. The selectors describe how
# each one can be recognised at issuance time — in production these come from
# the platform (a Kubernetes service account, a process UID, an image digest),
# which is why they are properties of the running thing rather than a name it
# chose for itself.
_WORKLOADS: dict[str, Workload] = {
    sid: Workload(sid, {"module": f"cybertravels.agents.{name}",
                        "image": f"cybertravels/{name}:1"})
    for name, sid in config.AGENT_IDS.items()
}


def get(spiffe_id) -> Workload:
    w = _WORKLOADS.get(spiffe_id)
    if w is None:
        raise RegistryError(f"no such workload: {spiffe_id}")
    return w


def active(spiffe_id) -> bool:
    """Registered **and** not retired. `config.REGISTERED_AGENTS` only answered
    the first half, which is why a decommissioned agent kept working."""
    w = _WORKLOADS.get(spiffe_id)
    return bool(w and w.state == "active")


def all_workloads():
    return [w.as_dict() for w in sorted(_WORKLOADS.values(),
                                        key=lambda w: w.spiffe_id)]


# step:B2.2 add
# --------------------------------------------------------------------------- #
# B2.2 — issuance against attestation
# --------------------------------------------------------------------------- #
# The bootstrap problem: a workload needs a credential to prove who it is, and
# it has to prove who it is to get a credential. Handing every agent the same
# long-lived secret at deploy time answers it by giving up — that secret is on
# disk, in the image, and in whatever read it last.
#
# The way out is that a workload does not have to *assert* anything. The
# platform can already observe properties of the running process, and those
# properties are what it presents. Nothing secret is issued to bootstrap;
# evidence is checked and a short-lived identity document comes back.
#
# This models the shape rather than the cryptography: real SVIDs are X.509 or
# JWT documents signed by an authority the workload cannot reach. The property
# being taught is the one that survives the simplification — **the workload
# never holds a credential that would let it impersonate a different one.**
SVID_TTL = 300


def attest(spiffe_id, evidence: dict):
    """Issue a short-lived identity document, if the evidence matches.

    `evidence` is what the platform observed about the process. Every selector
    on the record must match; extra evidence is ignored, missing or mismatched
    evidence is a refusal.
    """
    w = get(spiffe_id)
    if w.state != "active":
        raise RegistryError(f"{spiffe_id} is {w.state} — no SVID is issued to "
                            f"a workload that has been retired")
    for key, want in w.selectors.items():
        got = evidence.get(key)
        if got != want:
            raise RegistryError(
                f"attestation failed for {spiffe_id}: selector {key!r} "
                f"expected {want!r}, the process presented {got!r}")
    now = int(time.time())
    return {
        "spiffe_id": spiffe_id,
        "generation": w.generation,
        "issued_at": now,
        "expires_at": now + SVID_TTL,
        # A handle over the evidence, so an audit row can say which running
        # thing was attested without the record carrying the evidence itself.
        "attested": hashlib.sha256(
            repr(sorted(w.selectors.items())).encode()).hexdigest()[:16],
    }
# step:B2.2 end


# step:B2.5 add
# --------------------------------------------------------------------------- #
# B2.5 — the lifecycle
# --------------------------------------------------------------------------- #
# An identity that can be created and never stopped is half a control. These
# three are the operations an NHI register has to support before anybody can
# answer "what is still able to act, and should it be".
def rotate(spiffe_id):
    """New generation, same identity. Tokens minted under the old generation
    are still valid until they expire — which is why the TTL is short, and why
    rotation is not a substitute for revocation."""
    w = get(spiffe_id)
    if w.state != "active":
        raise RegistryError(f"cannot rotate {spiffe_id}: it is {w.state}")
    w.generation += 1
    return w.as_dict()


def revoke(spiffe_id, reason=""):
    """Stop it. `active()` is false from here, so `attest` refuses and
    `identity.verify_delegated` refuses anything it signed."""
    w = get(spiffe_id)
    w.state = "revoked"
    w.retired_at = time.time()
    return {"spiffe_id": spiffe_id, "state": "revoked", "reason": reason}


def register(spiffe_id, selectors, approved_by):
    """Add one. `approved_by` is not optional: an identity nobody approved is
    the row an auditor stops on, and B2.5's Day 2 counts exactly those."""
    if not approved_by:
        raise RegistryError("an identity needs a named approver")
    if spiffe_id in _WORKLOADS:
        raise RegistryError(f"{spiffe_id} is already registered")
    _WORKLOADS[spiffe_id] = Workload(spiffe_id, selectors, approved_by)
    return _WORKLOADS[spiffe_id].as_dict()


def orphans(live_ids):
    """Registered identities no running workload claims, and running workloads
    nobody registered. Both directions matter and teams usually check one."""
    known = set(_WORKLOADS)
    live = set(live_ids)
    return {
        "registered_but_absent": sorted(
            i for i in known - live if active(i)),
        "running_but_unregistered": sorted(live - known),
    }
# step:B2.5 end
