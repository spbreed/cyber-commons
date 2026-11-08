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




