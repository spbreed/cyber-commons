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










