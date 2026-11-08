"""Evidence, measured off the tree — including the controls that are absent.

This is the file that makes the rest of the function something other than
assertion. `measure()` walks the controls Functions A to E actually built,
asks each one whether it is present and functioning, and returns a number that
moves when somebody deletes one.

Six lessons:

    F1.5  what evaluation output is and is not evidence of
    F1.6  operating guardrails, which are enforceable, and outcome guardrails,
          which need a measurement before they mean anything
    F1.7  continuous verification — collect evidence, do not automate judgement
    F1.8  the third party, and the sub-processors nobody mapped
    F1.9  lifecycle — the change that is treated as maintenance
    F1.13 the measurement itself, on CyberTravels, with the gaps named

**The single most misleading thing available here is conformance.** A schema
check passes at about 100% and says nothing about correctness. C2.18 caps two
controls at PARTIAL for the same reason: an attestation that says PASS
everywhere is evidence of nothing.
"""
import time


# --------------------------------------------------------------------------- #
# F1.5 — what an evaluation result actually evidences
# --------------------------------------------------------------------------- #
def evidences(result):
    """Split an eval result into what it supports and what it does not.

    `best_of_k` is the field that matters and the one vendors report. A
    best-of-k demonstration is evidence that the system *can* produce the
    right answer, which is a different claim from the one a control needs.
    """
    claims, refused = [], []
    if result.get("best_of_k", 1) > 1:
        refused.append(
            f"best-of-{result['best_of_k']} shows the system can produce this "
            f"answer, not that it does. A control needs the rate")
    else:
        claims.append("a single-sample rate, which is what a control needs")
    if result.get("conformance") is not None and result.get("accuracy") is None:
        refused.append(
            "conformance is schema validity — about 100%, and structural. "
            "Reporting it as quality is the most misleading thing this "
            "toolchain makes easy")
    if result.get("interval") is None:
        refused.append("no interval, so the rate cannot be compared to the "
                       "next one")
    if result.get("held_out") is False:
        refused.append("scored against cases the system was tuned on")
    return {"evidences": claims, "does_not_evidence": refused,
            "usable_as_control_evidence": bool(claims) and not refused}










