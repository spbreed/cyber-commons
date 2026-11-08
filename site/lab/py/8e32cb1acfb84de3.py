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














