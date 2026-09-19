# step:file E1.0
"""The SOC that watches CyberTravels — and the hole every product leaves.

Functions A and B made the system defensible and reviewable. Function C
attacked it and, at D1.11, handed over three artefacts per finding: an eval
case, a control, and a **detection**. This package is where the third one
lands, which is why it imports from `cybertravels.redteam` rather than
reimplementing it — the handoff is literal or it is rhetoric.

The premise of the whole function is one sentence: **the estate's detection
content was written for an actor that acts a few times a minute, and it is now
watching one that acts a thousand times an hour and never repeats a session.**
Nothing in the stack is broken. Every rule still fires as designed. The
designs are about a different animal.

Five tracks, and they are the incident in order:

    E1  discover   what the sensors see, and what falls between them
    E2  detect     the lake, and rules whose subject is a non-human principal
    E3  understand correlation, admission, attribution, the hunt
    E4  respond    from a conclusion to the actor actually stopped
    E5  recover    replay, root cause, and the change that closes it

**The clock is the spine.** Every lesson in D names where it sits on it, and
the number that matters is not mean-time-to-detect — it is how much of the
clock is spent establishing *who acted*, which for an agent is a different
question than for a person and is where the hours go.
"""

# The incident clock, in the order it actually runs. Minutes are a target, not
# a measurement: the point of writing them down is that a stage with no target
# is a stage nobody has noticed is taking four hours.
CLOCK = [
    ("emit", 0, "the agent acts; a span and an audit row exist", "E1.3"),
    ("ingest", 2, "telemetry reaches the lake, at the tier it was priced at",
     "E2.1"),
    ("detect", 5, "a rule whose subject is the agent fires", "E2.2"),
    ("triage", 15, "an analyst, or a loop with a floor, reaches a verdict",
     "E3.1"),
    ("attribute", 45, "which human, which workload, which delegation hop — "
     "the stage that consumes the clock", "E3.4"),
    ("scope", 70, "the delegation graph, across every run involved", "E3.7"),
    ("contain", 85, "throttle, scope-reduce, reroute, force HITL, revoke",
     "E4.3"),
    ("recover", 240, "replay, root cause, the control that changes", "E5.2"),
]


def clock(stage=None):
    return [c for c in CLOCK if stage is None or c[0] == stage]


def target_minutes(stage):
    for name, minutes, _why, _lesson in CLOCK:
        if name == stage:
            return minutes
    raise KeyError(f"no stage {stage!r} on the clock — the stages are "
                   f"{[c[0] for c in CLOCK]}")


def elapsed_budget(stage):
    """How much of the clock is gone by the end of this stage, and what share
    of it attribution takes. That share is the number worth putting on a
    slide: in this design it is the single largest block, and for a human
    actor it would be near zero."""
    total = CLOCK[-1][1]
    reached = target_minutes(stage)
    attribute = target_minutes("attribute") - target_minutes("triage")
    return {"stage": stage, "minutes_elapsed": reached,
            "share_of_clock": round(reached / total, 3),
            "attribution_minutes": attribute,
            "attribution_share": round(attribute / total, 3)}
