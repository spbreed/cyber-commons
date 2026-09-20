# step:file D1.11
"""The handoff — what has to exist before a finding is finished.

A red-team engagement ends with a report, the report is read, and six months
later the same technique works again. Not because anybody ignored it: because
a report is a description of a moment, and nothing in the estate changed shape
to keep it closed.

So a finding is not done when it is written up. It is done when it has become
three artefacts, each owned by a different function, and each of which fails
loudly if the fix regresses:

    an eval case    Function D keeps it — it must FAIL on the old build and
                    PASS on the new one, or it is testing something else
    a control       Function B owns it — the thing that actually closes it
    a detection     Function E owns it — because the control will have a gap,
                    and the gap is where the next one comes through

The eval case is the load-bearing one and it is the one that gets skipped,
because writing a test that passes feels like finishing. A test that passes
against the unpatched build is testing the weather. `verify()` below runs it
both ways and refuses the handoff if it does not discriminate — the same rule
C2.16 applies to a patch, for the same reason.

The fourth artefact is the one nobody writes down: **who accepted it.** A
handoff with no named owner per artefact is three tickets in a backlog.
"""


class HandoffRejected(Exception):
    """The finding is not finished."""


class Finding:
    """What the engagement found, and what it has to become."""

    __slots__ = ("title", "technique", "rate", "interval", "evidence",
                 "eval_case", "control", "detection", "owners")

    def __init__(self, title, technique, rate, interval, evidence):
        if rate is None or interval is None:
            raise HandoffRejected(
                f"{title}: a finding with no rate and no interval is an "
                f"anecdote. D1.0 exists to stop this one reaching a report")
        if not evidence:
            raise HandoffRejected(f"{title}: no evidence attached")
        self.title = title
        self.technique = technique
        self.rate = rate
        self.interval = interval
        self.evidence = list(evidence)
        self.eval_case = None
        self.control = None
        self.detection = None
        self.owners = {}

    def hand_to(self, artefact, owner):
        if artefact not in ("eval_case", "control", "detection"):
            raise HandoffRejected(f"{artefact!r} is not one of the three")
        self.owners[artefact] = owner
        return self

    def as_dict(self):
        return {"finding": self.title, "technique": self.technique,
                "rate": self.rate, "interval_95": self.interval,
                "evidence": self.evidence, "owners": dict(self.owners),
                "artefacts": {"eval_case": bool(self.eval_case),
                              "control": bool(self.control),
                              "detection": bool(self.detection)}}


def verify(finding, *, old_build, new_build):
    """Run the eval case both ways. It must fail on old and pass on new.

    `finding.eval_case` is a callable taking a build and returning True when
    the system behaves correctly. A case that passes on the old build is not
    testing the defect; a case that fails on the new one means the control
    does not close it, and either way the handoff is refused rather than
    filed.
    """
    if finding.eval_case is None:
        raise HandoffRejected(
            f"{finding.title}: no eval case. The report will be read once and "
            f"the technique will work again when nobody is looking")
    if finding.eval_case(old_build):
        raise HandoffRejected(
            f"{finding.title}: the eval case PASSES against the old build, so "
            f"it does not discriminate. It is testing something that was "
            f"never broken")
    if not finding.eval_case(new_build):
        raise HandoffRejected(
            f"{finding.title}: the eval case fails against the new build — "
            f"the control does not close the finding")
    return {"discriminates": True,
            "fails_on": "old build", "passes_on": "new build"}


def complete(finding):
    """Everything present, and owned. Returns what is missing rather than a
    boolean, because 'incomplete' is not actionable and 'no detection owner'
    is."""
    missing = []
    for artefact in ("eval_case", "control", "detection"):
        if getattr(finding, artefact) is None:
            missing.append(f"{artefact}: not written")
        elif artefact not in finding.owners:
            missing.append(f"{artefact}: written, nobody accepted it")
    return {"finding": finding.title, "complete": not missing,
            "missing": missing}


def durability(findings):
    """D1.11's Day 2: how much of the engagement outlived it.

    Report the fraction with all three artefacts, and separately the fraction
    with only a report. The second number is the honest one — it is the work
    that will be redone.
    """
    total = len(findings) or 1
    done = [f for f in findings if complete(f)["complete"]]
    report_only = [f for f in findings
                   if not (f.eval_case or f.control or f.detection)]
    return {"findings": len(findings),
            "fully_handed_over": len(done),
            "durability": round(len(done) / total, 3),
            "report_only": len(report_only),
            "note": "the report-only count is the work that will be repeated "
                    "by the next engagement, at full price"}
