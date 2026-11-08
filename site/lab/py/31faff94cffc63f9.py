"""From a framework control to a number somebody can check this week.

An annual review certifies nothing about a system that changed the week after
it, and every system here changes weekly. So a control in this register is not
a paragraph with a date on it — it is a **key control indicator**: a named
measurement, a source in the tree, a threshold, and a cadence.

The rule that makes a KCI worth having is that it has to be computable without
asking anybody. If the measurement requires an engineer to go and look, it
will be taken once, at audit time, by somebody who knows what answer is
wanted.

Four lessons build this file:

    F1.1  the KCI itself — control -> measurement -> threshold
    F1.2  the inventory, derived from the tree rather than from a survey
    F1.3  tiering by what the thing can do, not by which model it uses
    F1.4  mapping outward to frameworks, never inward from them
"""
from .. import config


class KCI:
    """One control, as something measurable."""

    __slots__ = ("control_id", "name", "measure", "threshold", "direction",
                 "cadence_days", "source")

    def __init__(self, control_id, name, measure, threshold, direction,
                 cadence_days, source):
        if direction not in (">=", "<="):
            raise ValueError(f"{control_id}: a threshold needs a direction")
        if not callable(measure):
            raise ValueError(
                f"{control_id}: the measurement has to be computable. One that "
                f"needs an engineer to go and look is taken once, at audit "
                f"time, by somebody who knows what answer is wanted")
        self.control_id = control_id
        self.name = name
        self.measure = measure
        self.threshold = threshold
        self.direction = direction
        self.cadence_days = cadence_days
        self.source = source

    def evaluate(self):
        value = self.measure()
        passes = (value >= self.threshold if self.direction == ">="
                  else value <= self.threshold)
        return {"control": self.control_id, "name": self.name,
                "value": value, "threshold": self.threshold,
                "direction": self.direction, "passes": passes,
                "source": self.source, "cadence_days": self.cadence_days}


# --------------------------------------------------------------------------- #
# F1.2 — the inventory, and why a survey produces the wrong one
# --------------------------------------------------------------------------- #
# The inventory is the control most organisations still lack, and the reason is
# that it is usually built by asking. A survey returns the agents somebody
# remembered to declare, which is exactly the complement of the set you are
# looking for — shadow AI is, by definition, the part nobody would put on a
# form.
#
# Derive it. Every agent in this system has a workload identity, and the
# registry knows about all of them because `identity.token_exchange` will not
# mint for one it does not.
def inventory():
    """Every agent the system can actually issue a credential for."""
    from .. import registry
    rows = []
    for w in registry.all_workloads():
        rows.append({
            "spiffe_id": w["spiffe_id"],
            "state": w["state"],
            "approved_by": w["approved_by"],
            "registered_at": w["registered_at"],
            "generation": w["generation"],
            # An identity nobody approved is the row an assessor stops on.
            "unapproved": not w["approved_by"],
        })
    return sorted(rows, key=lambda r: r["spiffe_id"])


def shadow(live_ids):
    """Running workloads nobody registered, and registered ones nothing runs.

    Both directions, because teams check one. B2.5 built `orphans()`; this is
    the governance reading of it.
    """
    from .. import registry
    o = registry.orphans(live_ids)
    return {"running_but_unregistered": o["running_but_unregistered"],
            "registered_but_absent": o["registered_but_absent"],
            "shadow_count": len(o["running_but_unregistered"]),
            "why": "a survey returns the agents somebody declared, which is "
                   "the complement of the set you are looking for"}




