# step:file F3.1
"""Running the programme — eight decisions the CISO office actually makes.

Everything before this is machinery. This is where somebody has to choose what
to build first with a fixed team, what to say to a board, and when to say no.
Every function here returns a comparison rather than an answer, because the
answer depends on facts the code does not have and the comparison is the part
that gets skipped.
"""


# --------------------------------------------------------------------------- #
# F3.1 — translating blast radius into consequence
# --------------------------------------------------------------------------- #
# A board does not need to know that the agent holds a `payments:refund` scope.
# It needs to know that one compromised run can move money without a person,
# and how much. The translation is mechanical once you have B3.4's ceilings —
# and the engineering sentence is the thing that gets said instead.
def translate(*, scope, max_calls, amount_per_call, reversible, detected_in):
    exposure = max_calls * amount_per_call
    return {
        "engineering_sentence": f"the agent holds {scope} with a ceiling of "
                                f"{max_calls} calls per run",
        "board_sentence": (
            f"one compromised run can move up to {exposure:,.0f} before any "
            f"human is involved; it is "
            f"{'recoverable' if reversible else 'not recoverable'} and we "
            f"would know within {detected_in} minutes"),
        "exposure": exposure,
        "why": "the first sentence is true and answers a question nobody "
               "asked; the second is the same fact stated as consequence",
    }


# step:F3.2 add
# --------------------------------------------------------------------------- #
# F3.2 — govern the autonomy, not the tool
# --------------------------------------------------------------------------- #
# A per-tool review queue becomes a bottleneck, and a bottleneck becomes a
# bypass — teams route around it and the queue stops seeing the interesting
# deployments. Approving a *rung* rather than a tool scales, because the rung
# carries its own conditions and a team can move within it without asking.
RUNGS = [
    (0, "suggests to a person", "no approval needed"),
    (1, "acts on reversible things, logged", "team lead, one page"),
    (2, "acts on reversible things at volume", "the autonomy board, with a "
                                               "measured containment time"),
    (3, "acts on irreversible things with a human gate", "the autonomy board, "
                                                         "plus E4.2's real "
                                                         "decision point"),
    (4, "acts on irreversible things unattended", "not granted in this "
                                                  "system; B3.6 says the gate "
                                                  "stops working before this"),
]


def rung_for(*, reversible, unattended, volume):
    if not reversible and unattended:
        return 4
    if not reversible:
        return 3
    if volume == "high":
        return 2
    return 1 if not unattended else 2


def request(deployment):
    want = deployment.get("requested_rung")
    supported = rung_for(reversible=deployment.get("reversible", True),
                         unattended=deployment.get("unattended", False),
                         volume=deployment.get("volume", "low"))
    rung = next(r for r in RUNGS if r[0] == supported)
    return {"requested": want, "supported_by_blast_radius": supported,
            "approve_at": min(want, supported) if want is not None else supported,
            "approver": rung[2],
            "over_asking": want is not None and want > supported,
            "why": "the request is for a tool; the decision is about a rung, "
                   "which is what lets the next tool ship without a review"}
# step:F3.2 end


# step:F3.3 add
# --------------------------------------------------------------------------- #
# F3.3 — most winnable, not most visible
# --------------------------------------------------------------------------- #
# The instinct is to start with the workflow the executive sponsor mentions.
# It is usually the hardest one, and failing it publicly costs the programme
# more than the workflow was worth. Sequence by winnability, and use the win
# to buy the visible one.
def sequence(candidates):
    """candidates: [{name, visibility, difficulty, control_reuse}]"""
    scored = []
    for c in candidates:
        # Reuse is weighted hardest: a workflow that exercises controls you
        # already have produces coverage rather than a new control set.
        score = (c.get("control_reuse", 0) * 2 - c.get("difficulty", 0)
                 + c.get("visibility", 0) * 0.5)
        scored.append({**c, "score": round(score, 2)})
    scored.sort(key=lambda c: -c["score"])
    return {"order": [c["name"] for c in scored], "scored": scored,
            "why": "control reuse is weighted double: the first workflow's "
                   "job is to produce controls the second one inherits"}
# step:F3.3 end


# step:F3.4 add
# --------------------------------------------------------------------------- #
# F3.4 — the two functions with no home
# --------------------------------------------------------------------------- #
# Harness engineering and research are the two that fall between org charts.
# Harness engineering is not AppSec and not platform; research is treated as a
# hobby until an incident, and then as an emergency. Both need a named owner
# and a budget line, and the failure mode of neither is dramatic — it is that
# they quietly do not happen.
FUNCTIONS = {
    "control design": "cyber",
    "detection engineering": "SOC",
    "incident response": "SOC",
    "harness engineering": None,
    "red team / research": None,
    "model validation": "model risk",
    "regulatory mapping": "compliance",
}


def ownership():
    homeless = sorted(k for k, v in FUNCTIONS.items() if v is None)
    return {"functions": len(FUNCTIONS), "homeless": homeless,
            "why": "neither of these fails loudly; they quietly do not "
                   "happen, and the first evidence is an incident nobody had "
                   "the tooling to investigate"}
# step:F3.4 end


# step:F3.5 add
# --------------------------------------------------------------------------- #
# F3.5 — exposure, not activity
# --------------------------------------------------------------------------- #
# Activity metrics are easy to collect and move in the right direction whether
# or not anything improved. "Agents reviewed" goes up when the queue gets
# longer. Each pairing below replaces one with the exposure question it was
# standing in for.
INSTEAD_OF = {
    "agents reviewed": "agents running at a rung above what their blast "
                       "radius supports",
    "findings closed": "findings that became an eval case, a control and a "
                       "detection — D1.11's durability",
    "alerts triaged": "the floor miss rate — what the closing rule missed",
    "controls implemented": "control coverage measured against the tree, "
                            "with the gaps named — F1.13",
    "policies published": "obligations satisfied by controls that exist",
    "training completed": "time to stop, measured from a real attempt",
}


def replace(metric):
    better = INSTEAD_OF.get(metric)
    return {"activity_metric": metric, "exposure_metric": better,
            "is_activity": better is not None,
            "why": "an activity metric moves when the work gets bigger, "
                   "which is the opposite of what it is read as meaning"}
# step:F3.5 end


# step:F3.6 add
# --------------------------------------------------------------------------- #
# F3.6 — saying yes with conditions that are real
# --------------------------------------------------------------------------- #
# A flat no costs visibility: the capability ships anyway, somewhere you
# cannot see it, which is strictly worse than the thing you refused. A yes
# with aspirational conditions costs more, because it is recorded as a control.
#
# A condition is real when it is testable, time-bound and has a named owner,
# and when there is a stated consequence if it is not met.
def condition(text, *, testable_by, due, owner, consequence):
    missing = [name for name, v in (("testable_by", testable_by),
                                    ("due", due), ("owner", owner),
                                    ("consequence", consequence)) if not v]
    return {"condition": text, "real": not missing, "missing": missing,
            "why": "a condition with no consequence is a preference, and it "
                   "will be recorded in the register as a control"}


def approve_with(conditions):
    unreal = [c["condition"] for c in conditions if not c["real"]]
    return {"conditions": len(conditions), "aspirational": unreal,
            "enforceable": not unreal,
            "verdict": ("approved with conditions" if not unreal else
                        "this is a yes with a wish list; either make the "
                        "conditions testable or say no")}
# step:F3.6 end


# step:F3.7 add
# --------------------------------------------------------------------------- #
# F3.7 — build order for the capability, not the headcount plan
# --------------------------------------------------------------------------- #
# Hiring for conceptual familiarity produces a team that can discuss the
# problem. The order below produces a team that has done it, and it is chosen
# so each quarter's output is the next quarter's input — which is also why it
# starts with the inventory rather than with the red team.
BUILD_ORDER = [
    ("inventory and tiering", "F1.2, F1.3",
     "everything downstream needs to know what exists"),
    ("control baseline and KCIs", "F1.1, F1.13",
     "so coverage is a number before anybody improves it"),
    ("detection and telemetry", "E1.3, E2.2",
     "you cannot red-team what you cannot observe"),
    ("harness engineering", "C2.1",
     "the thing that makes the rest repeatable"),
    ("red team", "D1.0",
     "last, because its findings need somewhere to land — D1.11"),
]


def build_order(*, demos_first=False):
    if demos_first:
        return {"order": ["red team", "detection", "controls", "inventory"],
                "produces": "a sequence of striking findings with nowhere to "
                            "land, and a control baseline nobody built",
                "coverage_at_end": "unknown, because nothing measured it"}
    return {"order": [b[0] for b in BUILD_ORDER],
            "rationale": [{"stage": s, "lessons": l, "why": w}
                          for s, l, w in BUILD_ORDER],
            "produces": "control coverage, measured, with each stage's output "
                        "as the next stage's input"}
# step:F3.7 end


# step:F3.8 add
# --------------------------------------------------------------------------- #
# F3.8 — resilience, because the enumeration does not terminate
# --------------------------------------------------------------------------- #
# A probabilistic system has no complete list of failure modes, so a programme
# organised around enumerating them never finishes and never ships. The
# alternative is not resignation: it is to assume the failure and measure how
# quickly and how completely you recover from it.
#
# Four questions, all of which this commons has already produced numbers for.
def readiness(state):
    questions = {
        "time_to_detect": "E1.0's clock, measured rather than targeted",
        "time_to_stop": "E4.4, from a real attempt",
        "containment_coverage": "D1.9 — which act-paths the stop is on",
        "reconstructable": "D1.10 — can the run be defended afterwards",
    }
    missing = {k: why for k, why in questions.items() if state.get(k) is None}
    return {
        "answered": sorted(set(questions) - set(missing)),
        "unanswered": missing,
        "resilient": not missing,
        "why": "each of these is a number this curriculum already produces; "
               "a programme that cannot fill them in has been enumerating "
               "failure modes instead of measuring recovery",
    }


def durable(findings_handed_over, findings_total):
    """D1.11's durability, read as a programme metric rather than an
    engagement one: the fraction of what was learned that survived."""
    total = findings_total or 1
    return {"durability": round(findings_handed_over / total, 3),
            "repeated_next_time": findings_total - findings_handed_over,
            "why": "the rest will be rediscovered by the next engagement at "
                   "full price, and reported as a new finding"}
# step:F3.8 end
