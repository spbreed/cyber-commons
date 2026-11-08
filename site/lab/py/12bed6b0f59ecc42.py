"""From stopped to back at target — and the change that closes it.

The incident ends, the ticket closes, and two quarters later the same control
gap produces the same incident. That is the failure this track is organised
against, and every lesson in it is a refusal to let the record be a narrative.

Six lessons, and the through-line is that each artefact names something
**specific** and machine-checkable: the failed control, the layer the fix
belongs in, the indicator that moved, the policy line that permitted it. A
postmortem that names a person, a process or "a lack of rigour" is a document
that changes nothing, and everybody involved already knows that when they
write it.

E5.1 imports D1.10's replay audit rather than restating it. The red team and
the SOC ask the same question of the same record; the difference is only when.
"""
from ..redteam.forensics import answerable, reconstruct, replayable  # noqa: F401


def replay_readiness(rows, spans, verify_chain):
    """E5.1, from the defender's side: can we defend this reconstruction?

    The extra question the red team did not have to ask — non-determinism as
    an *evidentiary* problem. Rerunning the agent produces a second run, and a
    second run is not evidence about the first. So what has to be logged at
    design time is the input, not the conclusion.
    """
    r = reconstruct(rows, spans, verify_chain)
    r["defensible"] = r["reconstructable"]
    r["not_evidence"] = [
        "a rerun of the agent — non-determinism means it is a different run",
        "the model's own account of what it did, which is a claim by the "
        "subject of the investigation",
    ]
    return r


# --------------------------------------------------------------------------- #
# E5.2 — the root cause record names a control
# --------------------------------------------------------------------------- #
# Not a person, and not a narrative. Three fields, all required, all
# answerable from the incident: which control was absent or failed, which
# detection should have fired and did not, and what specific change is
# proposed. A record missing any of the three is a story.
class RootCauseIncomplete(Exception):
    """The record would not survive being read in two quarters."""


BANNED = ("human error", "lack of rigour", "insufficient training",
          "a process gap", "communication")


class RootCause:
    __slots__ = ("incident", "failed_control", "detection_that_should_have_fired",
                 "change_proposed", "contributing")

    def __init__(self, incident, failed_control,
                 detection_that_should_have_fired, change_proposed,
                 contributing=()):
        for name, value in (("failed_control", failed_control),
                            ("detection_that_should_have_fired",
                             detection_that_should_have_fired),
                            ("change_proposed", change_proposed)):
            if not value:
                raise RootCauseIncomplete(
                    f"{incident}: {name} is empty. All three are answerable "
                    f"from the incident, and a record missing one closes "
                    f"without changing anything")
        low = str(failed_control).lower()
        if any(b in low for b in BANNED):
            raise RootCauseIncomplete(
                f"{incident}: {failed_control!r} names a person or a mood. "
                f"Name the control — the thing that would have stopped it "
                f"whoever was on shift")
        self.incident = incident
        self.failed_control = failed_control
        self.detection_that_should_have_fired = detection_that_should_have_fired
        self.change_proposed = change_proposed
        self.contributing = list(contributing)

    def as_dict(self):
        return {"incident": self.incident,
                "failed_control": self.failed_control,
                "detection": self.detection_that_should_have_fired,
                "change": self.change_proposed,
                "contributing": self.contributing}


# --------------------------------------------------------------------------- #
# E5.3 — which layer does the fix belong in
# --------------------------------------------------------------------------- #
# The instinct is to fix the prompt, because the prompt is editable, visible
# and the change can ship this afternoon. It is almost never the right layer,
# and a prompt fix for a control-plane bug is worse than no fix: it closes the
# ticket and leaves the gap.
#
# Seven surfaces, ordered by how durable a fix at that layer is. A fix at a
# lower layer survives a model change, a prompt rewrite and a new agent.
SURFACES = [
    ("identity", 7, "who may act, and for whom — B2.x"),
    ("policy", 6, "what may be called, and under what obligation — B3.1"),
    ("sandbox", 5, "what an execution can reach — B3.2"),
    ("tool", 4, "what the tool itself permits, regardless of caller"),
    ("eval", 3, "the case that fails if this regresses — D1.11"),
    ("prompt", 2, "what the model is told; durable until anyone edits it"),
    ("model", 1, "the vendor's, on their schedule"),
]


def choose_surface(symptom, *, model_can_be_persuaded, survives_prompt_edit):
    """Rank the surfaces for this symptom, worst-durability last."""
    ranked = sorted(SURFACES, key=lambda s: -s[1])
    advice = []
    for name, durability, why in ranked:
        fits = not (name in ("prompt", "model") and
                    (model_can_be_persuaded or survives_prompt_edit))
        advice.append({"surface": name, "durability": durability, "why": why,
                       "appropriate": fits})
    return {"symptom": symptom, "surfaces": advice,
            "recommended": next(a["surface"] for a in advice
                                if a["appropriate"]),
            "note": "if the answer is 'prompt' and the model can be persuaded "
                    "out of it, the answer is not prompt"}






