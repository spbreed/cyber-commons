# step:file D5.1
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

D5.1 imports C1.10's replay audit rather than restating it. The red team and
the SOC ask the same question of the same record; the difference is only when.
"""
from ..redteam.forensics import answerable, reconstruct, replayable  # noqa: F401


def replay_readiness(rows, spans, verify_chain):
    """D5.1, from the defender's side: can we defend this reconstruction?

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


# step:D5.2 add
# --------------------------------------------------------------------------- #
# D5.2 — the root cause record names a control
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
# step:D5.2 end


# step:D5.3 add
# --------------------------------------------------------------------------- #
# D5.3 — which layer does the fix belong in
# --------------------------------------------------------------------------- #
# The instinct is to fix the prompt, because the prompt is editable, visible
# and the change can ship this afternoon. It is almost never the right layer,
# and a prompt fix for a control-plane bug is worse than no fix: it closes the
# ticket and leaves the gap.
#
# Seven surfaces, ordered by how durable a fix at that layer is. A fix at a
# lower layer survives a model change, a prompt rewrite and a new agent.
SURFACES = [
    ("identity", 7, "who may act, and for whom — A2.x"),
    ("policy", 6, "what may be called, and under what obligation — A3.1"),
    ("sandbox", 5, "what an execution can reach — A3.2"),
    ("tool", 4, "what the tool itself permits, regardless of caller"),
    ("eval", 3, "the case that fails if this regresses — C1.11"),
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
# step:D5.3 end


# step:D5.4 add
# --------------------------------------------------------------------------- #
# D5.4 — the fix is done when the indicator moved
# --------------------------------------------------------------------------- #
# Not when the ticket closed. The two are routinely different and only one of
# them is checkable, so re-measure the indicators the incident moved and
# attach the before and after to the incident record.
def validate_fix(before, after, *, indicators):
    rows = []
    for name, want in indicators.items():
        was, now = before.get(name), after.get(name)
        moved = None if was is None or now is None else now - was
        rows.append({"indicator": name, "before": was, "after": now,
                     "delta": moved, "wanted": want,
                     "improved": None if moved is None else
                     (moved > 0 if want == "up" else moved < 0)})
    unmeasured = [r["indicator"] for r in rows if r["improved"] is None]
    return {"indicators": rows,
            "all_improved": all(r["improved"] for r in rows
                                if r["improved"] is not None) and not unmeasured,
            "unmeasured": unmeasured,
            "why": "an unmeasured indicator is the ticket closing on its own "
                   "authority"}
# step:D5.4 end


# step:D5.5 add
# --------------------------------------------------------------------------- #
# D5.5 — the policy change, as a diff
# --------------------------------------------------------------------------- #
# The lesson from the incident lives in a postmortem nobody reads, and the
# policy that permitted it is unchanged — so the next incident is permitted
# too. The proposal is generated from the root cause record, carries the
# incident as its evidence, and states what it does **not** fix, because a
# change presented as closing everything is one nobody scrutinises.
def propose(root_cause, *, policy_line, was, now, does_not_fix):
    if not does_not_fix:
        raise RootCauseIncomplete(
            "a proposal has to say what it does not fix. One presented as "
            "closing the whole class is one nobody reads carefully")
    return {
        "incident": root_cause.incident,
        "evidence": root_cause.as_dict(),
        "policy_line": policy_line,
        "diff": {"was": was, "now": now},
        "does_not_fix": list(does_not_fix),
        "why": "the diff is the deliverable; a postmortem is the reasoning "
               "behind it and does not change anything on its own",
    }
# step:D5.5 end


# step:D5.6 add
# --------------------------------------------------------------------------- #
# D5.6 — the clock started at awareness, not at confirmation
# --------------------------------------------------------------------------- #
# The obligation is discovered in week two, and the deadline was counted from
# an hour in week one. The distinction that catches people is that most
# regimes start the clock at **awareness of a likely incident**, not at the
# completion of an investigation — so "we were still confirming" is not a
# defence, it is a description of the period the clock was running.
#
# This is the handoff into Track E2, and it happens in hour one.
REGIMES = [
    ("GDPR Art. 33", 72, "awareness of a personal data breach",
     "supervisory authority"),
    ("NIS2 early warning", 24, "awareness of a significant incident", "CSIRT"),
    ("DORA major ICT", 4, "classification as major", "competent authority"),
    ("SEC 8-K Item 1.05", 96, "determination of materiality", "the filing"),
]


def clock_check(aware_at, *, personal_data, significant, financial_entity,
                listed):
    """Which clocks are running, and when each expires."""
    applies = {
        "GDPR Art. 33": personal_data,
        "NIS2 early warning": significant,
        "DORA major ICT": financial_entity and significant,
        "SEC 8-K Item 1.05": listed,
    }
    out = []
    for name, hours, trigger, to in REGIMES:
        if applies.get(name):
            out.append({"regime": name, "hours": hours, "trigger": trigger,
                        "notify": to, "deadline": aware_at + hours * 3600})
    return {"running": sorted(out, key=lambda r: r["hours"]),
            "tightest_hours": min((r["hours"] for r in out), default=None),
            "why": "the clock starts at awareness; an investigation that is "
                   "still confirming is an investigation running on the clock"}
# step:D5.6 end
