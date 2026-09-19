# step:file E1.1
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

    E1.1  the KCI itself — control -> measurement -> threshold
    E1.2  the inventory, derived from the tree rather than from a survey
    E1.3  tiering by what the thing can do, not by which model it uses
    E1.4  mapping outward to frameworks, never inward from them
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


# step:E1.2 add
# --------------------------------------------------------------------------- #
# E1.2 — the inventory, and why a survey produces the wrong one
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

    Both directions, because teams check one. A2.5 built `orphans()`; this is
    the governance reading of it.
    """
    from .. import registry
    o = registry.orphans(live_ids)
    return {"running_but_unregistered": o["running_but_unregistered"],
            "registered_but_absent": o["registered_but_absent"],
            "shadow_count": len(o["running_but_unregistered"]),
            "why": "a survey returns the agents somebody declared, which is "
                   "the complement of the set you are looking for"}
# step:E1.2 end


# step:E1.3 add
# --------------------------------------------------------------------------- #
# E1.3 — tier by what it can do
# --------------------------------------------------------------------------- #
# Tiering by model name is the default because the model name is the thing on
# the form. It produces a register where every large-model deployment is high
# risk and a small-model agent with write access to the payments API is
# medium, which is backwards.
#
# Three inputs, all readable off the deployment: how autonomously it runs,
# what data it reaches, and whether its effects leave the building.
AUTONOMY = {"suggests": 0, "acts-with-approval": 1, "acts-unattended": 2}
DATA_REACH = {"public": 0, "internal": 1, "personal": 2, "payments": 3}
EXTERNAL_EFFECT = {"none": 0, "internal-write": 1, "customer-visible": 2,
                   "money-moves": 3}


def tier(autonomy, data_reach, external_effect, *, model=""):
    """The tier, and — deliberately — what tiering by model would have said."""
    score = (AUTONOMY[autonomy] + DATA_REACH[data_reach]
             + EXTERNAL_EFFECT[external_effect])
    band = ("low" if score <= 2 else "medium" if score <= 4
            else "high" if score <= 6 else "critical")
    by_model = "high" if "opus" in model.lower() or "gpt-4" in model.lower() \
        else "medium"
    return {"tier": band, "score": score,
            "inputs": {"autonomy": autonomy, "data_reach": data_reach,
                       "external_effect": external_effect},
            "tier_by_model_name_would_say": by_model,
            "disagrees": band != by_model,
            "why": "the model is the least deployment-specific fact about a "
                   "deployment; these three are properties of what was built"}


def tier_the_workflow_agent():
    """CyberTravels' own, read off the tree rather than judged."""
    moves_money = any(r["scope"] == "payments:refund"
                      for r in config.TOOL_POLICY.values())
    return tier("acts-with-approval", "payments" if moves_money else "personal",
                "money-moves" if moves_money else "customer-visible",
                model=config.CLAUDE_MODEL)
# step:E1.3 end


# step:E1.4 add
# --------------------------------------------------------------------------- #
# E1.4 — map outward, never inward
# --------------------------------------------------------------------------- #
# Starting from a framework produces a control per clause, which is a
# programme shaped like a document. Starting from the controls you have and
# mapping them outward produces the same coverage answer and, crucially, tells
# you which clauses nothing covers — which is the question the framework was
# for.
#
# The other half is the one E1.4's risk line names: before inventing a control
# for agents, check whether an existing one applies to a new principal type.
# Most of them do, and a new control is a new thing to maintain and evidence.
EXISTING_CONTROL_APPLIES = {
    "access review": "an agent's entitlements are entitlements; the review "
                     "needs a non-human principal type, not a new control",
    "change management": "a system prompt change is a change — D1.2 counts "
                         "the surfaces that avoid this one",
    "joiner-mover-leaver": "A2.5's revoke is the leaver process; what is "
                           "missing is the trigger, not the capability",
    "privileged access management": "a delegated token is privileged access "
                                    "with a two-minute lifetime",
    "data retention": "per field rather than per record, which is a "
                      "parameter change and not a new policy",
}


def map_outward(controls, framework_clauses):
    """controls: {control_id: [clause, ...]}. Returns coverage both ways."""
    covered = {c for clauses in controls.values() for c in clauses}
    return {
        "controls": len(controls),
        "clauses_covered": sorted(covered & set(framework_clauses)),
        # The answer the framework was for.
        "clauses_uncovered": sorted(set(framework_clauses) - covered),
        "controls_mapping_nowhere": sorted(
            c for c, clauses in controls.items()
            if not set(clauses) & set(framework_clauses)),
        "coverage": round(len(covered & set(framework_clauses))
                          / max(len(framework_clauses), 1), 3),
    }


def needs_a_new_control(proposed, *, for_principal="agent"):
    """Is this genuinely new, or an existing control with a new subject?"""
    for existing, why in EXISTING_CONTROL_APPLIES.items():
        if existing in proposed.lower():
            return {"new": False, "existing_control": existing, "why": why}
    return {"new": True,
            "why": f"nothing in the existing set covers {proposed!r} for a "
                   f"{for_principal} principal — this one is genuinely new, "
                   f"and it now has to be maintained and evidenced"}
# step:E1.4 end
