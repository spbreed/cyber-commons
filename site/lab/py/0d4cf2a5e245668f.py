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


# --------------------------------------------------------------------------- #
# F1.6 — two kinds of guardrail, and only one is enforceable today
# --------------------------------------------------------------------------- #
# "The agent must not act outside its authority" is enforceable: B3.1 decides
# it per call. "The agent must not mislead a customer" is not — not because it
# is unimportant, but because nothing in the system can evaluate it, and a
# policy containing a rule nobody can enforce teaches its readers that the
# policy is aspirational.
#
# The honest move is not to delete the second kind. It is to name the
# measurement it needs, and to say plainly that until that exists the
# guardrail is an outcome you are watching rather than a control you have.
def classify_guardrail(text, *, enforced_by=None, measured_by=None):
    if enforced_by:
        return {"guardrail": text, "kind": "operating",
                "enforced_by": enforced_by, "status": "in place"}
    if measured_by:
        return {"guardrail": text, "kind": "outcome",
                "measured_by": measured_by, "status": "watched",
                "why": "not enforced — this is an outcome with a measurement, "
                       "which is honest and is not a control"}
    return {"guardrail": text, "kind": "outcome", "status": "aspirational",
            "why": "nothing enforces it and nothing measures it. Specify the "
                   "measurement, or take it out of the policy — a rule nobody "
                   "can enforce teaches readers the policy is decorative"}


# --------------------------------------------------------------------------- #
# F1.7 — automate the collection, not the judgement
# --------------------------------------------------------------------------- #
# Continuous control verification goes wrong in one specific way: a model is
# asked whether the control is adequate, answers yes, and the answer is filed
# as evidence. What can be automated is *gathering* the artefact. Whether it
# is adequate is a judgement, it has an owner, and the owner's name goes on it.
def collect(control_id, collector, *, judged_by):
    if not judged_by:
        raise ValueError(
            f"{control_id}: collection can be automated and judgement cannot. "
            f"An adequacy verdict with no named human is a model grading a "
            f"control on behalf of the people accountable for it")
    return {"control": control_id, "collected_at": time.time(),
            "artefact": collector(), "judged_by": judged_by,
            "judgement": None,
            "why": "the verdict field is empty on purpose; it is filled by "
                   "the named person, not by this function"}


# --------------------------------------------------------------------------- #
# F1.8 — the vendor, and the chain behind the vendor
# --------------------------------------------------------------------------- #
# Two failures, and the second is the one nobody has mapped. Vendor AI
# features arrive enabled by default in a product you already bought, so
# nothing triggers a review. And behind the vendor is a sub-processor chain —
# their model provider, their retrieval provider, their logging provider —
# which is where the data actually goes.
def assess_third_party(vendor):
    gaps = []
    if vendor.get("ai_features_default_on"):
        gaps.append("AI features on by default — no purchase event triggered "
                    "a review, so nothing was reviewed")
    if not vendor.get("sub_processors"):
        gaps.append("no sub-processor list — the chain behind this vendor is "
                    "where the data actually goes")
    if vendor.get("trains_on_customer_data"):
        gaps.append("trains on customer data; F2.5's deletion question has no "
                    "good answer once it is in weights")
    if not vendor.get("change_notification"):
        gaps.append("no notification on model change — E1.2's first drift "
                    "surface, on somebody else's schedule")
    return {"vendor": vendor.get("name"), "gaps": gaps,
            "acceptable": not gaps,
            "depth_mapped": len(vendor.get("sub_processors", []))}




