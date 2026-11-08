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








