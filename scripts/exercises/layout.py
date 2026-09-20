"""Which parts of the lesson template each lesson actually renders.

The seven sections used to be unconditional: every page got a Risk and a
Control panel, a "Use case relevance" section with a CyberTravels scene, and a
Day 0 / Day 1 / Day 2 table, whether or not the lesson had any of those things
to say. That is how a template stops being a shape a reader can learn and
becomes a form an author fills in, and the filling-in is visible:

  * A0.0 sets up a laptop. Its "Risk" was *a reader clones the repository and
    leaves*, which is a risk to the commons, not to a system anybody secures,
    and its "Control" was the lesson itself. `curriculum/frameworks.json` had
    already reached the honest conclusion for the same pages — chapter A0's
    entry reads "Setup only — how to run a lesson. No control maps to it" —
    and the page went on printing a Control anyway.
  * A0.1 explains how to read the commons. Its Day 2, the number that says it
    worked, was "Nothing is computed here."
  * A0.0's CyberTravels grounding, under a heading promising the idea in the
    running system, was "Nothing in CyberTravels yet."
  * D1.1-D1.11 are the stages of one red-team lifecycle. Each carried `risk`
    and `control` as empty strings — the template applied and then abandoned —
    and a lab line that was a verbatim copy of the summary three lines above.

So the parts are declared per lesson rather than assumed, and the declaration
is checked from both sides by `scripts/check_lessons.py`: a part that renders
must have content behind it, and a part that does not render must have no
content left in the sources. The second half is the one that matters. Dropping
a section without deleting what fed it leaves prose nobody reads and nobody
can find to correct — B1.0 carried a "What you just proved" paragraph for a
lesson that runs nothing, and it had been invisible on the page for months.

Adding a lesson does not require an entry here. A lesson takes its kind's
default, and an entry is only needed to say that some part of the template
does not apply to it — with the reason, so the next person can disagree with
the judgement rather than the omission.
"""
from __future__ import annotations

from . import EXERCISES


def runs_something(sid: str) -> bool:
    """Does this lesson execute anything?

    Read from the lesson's own steps. Lives here rather than in build_site.py
    because the answer decides a section, and the gate has to reach the same
    answer the page did.
    """
    return any(k in ("py", "skill_script", "model")
               for k, _ in EXERCISES.get(sid, {}).get("steps", []))


# The parts of a page, in the order they render. `framework` and `skill` are
# not optional: the framework is the lesson, and the skill section also carries
# the checkpoint block, which is how a reader gets the CyberTravels tree as it
# stood at this lesson. A page without either is not a lesson.
PARTS = ("riskcontrol", "relevance", "days", "framework", "skill",
         "proved", "turn", "bridge")
ALWAYS = frozenset({"framework", "skill"})
FULL = frozenset(PARTS)

# What a lesson renders by default, by its `kind` in site/data/curriculum.json.
# Everything except `setup` takes the whole template, because everything except
# `setup` is about the system: it has a risk, it has a scene in CyberTravels,
# and it produces a number.
BY_KIND: dict[str | None, frozenset[str]] = {
    # Orientation: the reader's own machine and how to read the commons. There
    # is no use case, no adversary and no number — A0.0 ends in a model call
    # that either happened or did not, and that is the `proved` section's job.
    "setup": FULL - {"riskcontrol", "relevance", "days"},
}
DEFAULT = FULL

# There is no `runoutput` part, and that is a decision rather than an omission.
# An "Expect" box used to render from `curriculum/labs.json`, below the chapter
# bridge, three screens under the command it described. Of the 133 pages that
# carried one, 59 repeated the "What you just proved" section above it — 35 of
# them word for word — 10 repeated the lab line, and four described a different
# lesson: C2.16's claimed "precision 1.00 across sast, threat model" on a
# patch-validation lesson, D1.2's an attack-success rate on a provenance
# lesson, D1.4's a reproduction rate belonging to D1.3. That file's sibling
# `lab` field had failed the same way and was fixed by reading the lab line
# from the session instead; nothing went back for `expect`. Six lessons where
# the box held the real result and "What you just proved" described the skill's
# contract had the two merged, A0.1's counts moved into its own `proved`, and
# the field is gone from labs.json. check_lessons.py refuses it coming back.

# Deviations from the kind default. (parts, why) — and `why` is not decoration:
# check_lessons.py prints it, so a reader of the failure sees the argument.
EXCEPTIONS: dict[str, tuple[frozenset[str], str]] = {
    # The two function introductions whose Control was the table of contents.
    # A1.0's read "Build it first. Every control in Function B attaches to a
    # component drawn here", and B1.0's "One picture, three chapters: the
    # architecture and its risks, then identity and ingress, then runtime and
    # the gateway" — a reading order, not a mechanism. Both also opened on the
    # same Risk as the lesson immediately after them ("Without a shared
    # architecture/picture, 'secure the agent' has no referent"), so the panel
    # was saying it twice on consecutive pages. B1.1 states that risk and
    # answers it with an artefact, which is where it belongs.
    "A1.0": (FULL - {"riskcontrol"},
             "An introduction to a chapter that builds. Its risk is that "
             "security guidance lands as paperwork on somebody who has never "
             "built an agent, which is a risk to the reader rather than to a "
             "system, and its control was the reading order."),
    "B1.0": (FULL - {"riskcontrol"},
             "The function introduction. Its control was the chapter list, and "
             "its risk is B1.1's risk one page early — B1.1 answers it with a "
             "component map and five topologies, which is a control."),
    "D1.0": (FULL,
             "The function introduction, inside a track that otherwise drops "
             "the panel. Its risk is offensive work that produces anecdotes "
             "and its control is a campaign with a stated criterion, which is "
             "the argument the eleven stages after it carry out — so it is the "
             "one page in D1 where a risk and a control belong."),
}

# Track-wide deviations, applied to every lesson in the track that has no
# entry of its own in EXCEPTIONS.
BY_TRACK: dict[str, tuple[frozenset[str], str]] = {
    "D1": (FULL - {"riskcontrol"},
           "D1 is one red-team lifecycle told in eleven stages, not eleven "
           "risk-and-control lessons. A stage's output is a rate with a "
           "denominator, and the control it hands to a defender is D1.11's "
           "whole subject rather than a line at the top of each page. The "
           "eleven carried `risk` and `control` as empty strings before this "
           "was written down."),
}


def parts_for(sid: str, kind: str | None, track: str, *,
              runs: bool, last_in_track: bool) -> frozenset[str]:
    """The parts this lesson renders.

    `runs` and `last_in_track` are structural rather than editorial: a lesson
    that executes nothing cannot have proved anything, and a bridge belongs to
    the end of a chapter. They are applied here so that build_site.py and
    check_lessons.py cannot reach different answers about the same page.
    """
    parts = EXCEPTIONS.get(sid, (None, ""))[0]
    if parts is None:
        parts = BY_TRACK.get(track, (None, ""))[0]
    if parts is None:
        parts = BY_KIND.get(kind, DEFAULT)
    if not runs:
        parts = parts - {"proved"}
    if not last_in_track:
        parts = parts - {"bridge"}
    return parts | ALWAYS


def why_dropped(sid: str, kind: str | None, track: str) -> str:
    """The recorded reason this lesson is not on the full template."""
    if sid in EXCEPTIONS:
        return EXCEPTIONS[sid][1]
    if track in BY_TRACK:
        return BY_TRACK[track][1]
    if kind in BY_KIND:
        return {"setup": "A setup lesson: the subject is the reader's machine "
                         "and the commons itself, so there is no use case, no "
                         "adversary and no Day 2 number."}.get(kind, "")
    return ""
