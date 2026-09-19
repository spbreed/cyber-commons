# step:file C2.0
"""The AppSec pipeline — what reviews CyberTravels, shipping inside CyberTravels.

Function G built the product. Function A put controls on it. This package is
the third thing, and it is not part of the product: it is the pipeline Alex's
team runs **over** this repository, stage by stage, one stage per lesson.

**It lives in the same repository as the code it scans, on purpose.** A pipeline
in its own repository is a pipeline that drifts from the thing it reviews and
that nobody runs locally. The cost of keeping it here is stated rather than
hidden: `appsec/` is inside the tree the scanners walk, so the pipeline is
subject to its own findings. That is C2.0's argument — a security pipeline
built as if it were exempt from the risks it exists to find is the most
expensive kind, because its failures are reported as clean runs.

The stages are numbered as the lessons number them. Stages 1-4 are the estate
work Function A did; this package starts where B does.

    before a deploy                        after a deploy
    ---------------                        --------------
     5  threat model      C2.2             10  feasibility       C2.5
     6  context slice     C2.17            11  sandbox replica   C2.6
     7  SAST              C2.3             12  dynamic exploit   C2.8
     8  deduplication     C2.4             13  exploit chaining  C2.9
     9  verification      C2.4             14  remediation       C2.16
                                           15  severity + report C2.15

The split is not chronological tidiness. It is about what each half is allowed
to claim. Before a deploy you have the source and no running system, so every
finding is a **hypothesis** — reported as one, with the reachability that
supports it. After a deploy you have a running system in a disposable replica,
so a finding can be **demonstrated**, and a hypothesis that cannot be
demonstrated there is dropped rather than shipped as a medium.

The two halves differ in one more way, and it is the practical one. The
**before** stages never import the application — they read it as text and as an
AST, so they run against a checkout that could not be imported, which is most
checkouts most of the time. The **after** stages import and run it, inside the
replica C2.6 builds, because a claim that something was exploited cannot be
made by reading. Which half a stage is in tells you what it is allowed to say.
"""

# One row per stage: number, name, half, the lesson that builds it, and what
# the stage is allowed to assert when it is finished. That last column is the
# one that stops a pipeline over-claiming: it is the difference between "this
# is reachable" and "this was exploited", and a report that blurs them is a
# report nobody can act on.
STAGES = [
    (5,  "threat model",   "before", "C2.2",
     "these are the assets and entry points, derived from the tree"),
    (6,  "context slice",  "before", "C2.17",
     "this is the smallest source-to-sink context that supports a decision"),
    (7,  "static analysis", "before", "C2.3",
     "a pattern matched here, or a model read here — labelled which"),
    (8,  "deduplication",  "before", "C2.4",
     "these reports are one finding"),
    (9,  "verification",   "before", "C2.4",
     "this finding names code that exists"),
    (10, "feasibility",    "after",  "C2.5",
     "an external caller can, or cannot, reach this sink"),
    (11, "sandbox replica", "after", "C2.6",
     "this is the system, running, with no path to production"),
    (12, "dynamic exploit", "after", "C2.8",
     "this was exploited, here is the request and the response"),
    (13, "exploit chain",  "after",  "C2.9",
     "these findings compose, and the chain scores higher than its links"),
    (14, "remediation",    "after",  "C2.16",
     "this patch stops the exploit, and a test fails without it"),
    (15, "severity",       "after",  "C2.15",
     "this severity was calibrated from evidence, not copied from a rule"),
]


def stages(half=None):
    """The stage table, optionally one half of it."""
    return [s for s in STAGES if half is None or s[2] == half]


def claim_for(stage_number):
    """What a stage is allowed to assert. Used by the report, so a stage
    cannot quietly start claiming the next stage's confidence."""
    for n, _name, _half, _lesson, claim in STAGES:
        if n == stage_number:
            return claim
    raise KeyError(f"no stage {stage_number} — the pipeline has "
                   f"{len(STAGES)} and they are numbered as the lessons are")
