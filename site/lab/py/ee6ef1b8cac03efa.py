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












