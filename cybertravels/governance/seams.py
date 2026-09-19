# step:file F1.10
"""The programme does not fail at the functions. It fails at the seams.

Legal, compliance, privacy, cyber and model risk each hold part of the AI
control estate and none of them holds all of it. Every function is competent,
every function delivers what it owns, and the thing falls over between them —
because a handoff is nobody's deliverable and therefore nobody's deadline.

Three lessons, and they are one argument:

    F1.10  who holds which part, and where two of them both think the other
           has it
    F1.11  model risk management, whose playbook silently breaks once the
           model can act
    F1.12  the handoffs themselves, traced from producer to consumer
"""


# Who holds what. The interesting column is the last one: a part nobody holds
# is a gap, and a part two functions both believe the other holds is worse,
# because it is a gap that looks covered on both sides.
HOLDERS = {
    "legal position on autonomy": ["legal"],
    "privacy impact assessment": ["privacy"],
    "control design": ["cyber"],
    "model validation": ["model risk"],
    "regulatory obligation mapping": ["compliance"],
    "the system prompt's legal wording": ["legal", "cyber"],
    "agent entitlements review": ["cyber", "compliance"],
    "retention of agent telemetry": ["privacy", "cyber"],
    "evidence that a control works": [],
    "who may raise the autonomy of a deployment": [],
}


def seam_map():
    rows = []
    for part, held in sorted(HOLDERS.items()):
        rows.append({
            "part": part, "held_by": held,
            "state": ("unowned" if not held
                      else "shared" if len(held) > 1 else "owned"),
            "risk": ("nobody produces this" if not held
                     else "each may believe the other has it" if len(held) > 1
                     else ""),
        })
    return {"parts": rows,
            "unowned": [r["part"] for r in rows if r["state"] == "unowned"],
            "shared": [r["part"] for r in rows if r["state"] == "shared"],
            "why": "a shared part is not safer than an unowned one — it is an "
                   "unowned one that looks covered from both sides"}


# step:F1.11 add
# --------------------------------------------------------------------------- #
# F1.11 — model risk management, once the model can act
# --------------------------------------------------------------------------- #
# The classical playbook is sound and it validates the wrong surface here. It
# asks whether the model is conceptually sound, whether its outputs are
# accurate, whether it is used within its stated limitations — all of which
# were answered, honestly, before the agent was granted write access to the
# payments API.
#
# The scope has to extend to what the model can *do*, and the extensions are
# not small. Each one below is a validation activity that has no equivalent in
# the classical framework.
CLASSICAL = {
    "conceptual soundness": "is the approach right for the problem",
    "input data quality": "is what it is fed fit for purpose",
    "output accuracy": "does it produce the right answer",
    "use within limitations": "is it being applied where it was validated",
    "ongoing monitoring": "has performance drifted",
}

ONCE_IT_CAN_ACT = {
    "authority": "what can it cause, and under whose identity — B2.3",
    "action reversibility": "which of its effects can be undone — E4.1",
    "blast radius": "what one run can reach at worst — B3.4's ceilings",
    "adversarial reachability": "can a third party steer it — D1.2",
    "containment": "can it be stopped, and which paths is the stop on — D1.9",
}


def validation_scope(deployment):
    """What a validation covered, and what it did not because it could not."""
    covered = set(deployment.get("validated", []))
    return {
        "classical_covered": sorted(covered & set(CLASSICAL)),
        "classical_missing": sorted(set(CLASSICAL) - covered),
        "agentic_covered": sorted(covered & set(ONCE_IT_CAN_ACT)),
        # The list that decides whether the validation means anything for an
        # agent, and the one a classical template does not contain.
        "agentic_missing": sorted(set(ONCE_IT_CAN_ACT) - covered),
        "valid_for_an_acting_model":
            not (set(ONCE_IT_CAN_ACT) - covered),
        "why": "conceptual soundness was validated and then the agent was "
               "granted write access; nothing in the classical scope asks "
               "about the second half",
    }


def capability_delta(before, after):
    """What a change added to what the thing can do, rather than to how well
    it does it. A capability increase is a re-tiering event; an accuracy
    increase is not, and they arrive in the same release note."""
    gained = sorted(set(after) - set(before))
    return {"gained": gained, "retier": bool(gained),
            "why": "more capability is a governance event even when the "
                   "release note calls it an improvement"}
# step:F1.11 end


# step:F1.12 add
# --------------------------------------------------------------------------- #
# F1.12 — trace each handoff to the thing it was supposed to become
# --------------------------------------------------------------------------- #
# A handoff is agreed in a meeting, both sides leave satisfied, and neither
# has a deliverable. The check is blunt: for each handoff, name the artefact
# the consumer should now be holding, and go and look for it.
HANDOFFS = [
    ("privacy", "cyber", "privacy impact assessment",
     "a retention parameter per telemetry field — E1.3"),
    ("legal", "cyber", "legal position on autonomy",
     "a line in the system prompt and a tier in the autonomy ladder"),
    ("model risk", "cyber", "validation report",
     "the KCIs in F1.1 that re-measure what validation asserted"),
    ("cyber", "compliance", "control evidence",
     "the artefacts an obligation maps to — F2.1"),
    ("red team", "cyber", "a finding",
     "an eval case, a control and a detection — D1.11"),
    ("SOC", "compliance", "incident awareness",
     "the regulatory clock, started in hour one — E5.6"),
]


def delivered(held_by_consumer):
    """Which handoffs actually arrived as artefacts."""
    rows = []
    for producer, consumer, what, artefact in HANDOFFS:
        got = artefact in held_by_consumer
        rows.append({"from": producer, "to": consumer, "handoff": what,
                     "expected_artefact": artefact, "delivered": got})
    missing = [r for r in rows if not r["delivered"]]
    return {"handoffs": len(rows), "delivered": len(rows) - len(missing),
            "undelivered": [r["handoff"] for r in missing],
            "rate": round((len(rows) - len(missing)) / len(rows), 3),
            "why": "both sides agreed each of these and neither had a "
                   "deliverable, which is why the artefact column exists"}
# step:F1.12 end
