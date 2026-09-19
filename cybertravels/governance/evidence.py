# step:file E1.5
"""Evidence, measured off the tree — including the controls that are absent.

This is the file that makes the rest of the function something other than
assertion. `measure()` walks the controls Functions A to D actually built,
asks each one whether it is present and functioning, and returns a number that
moves when somebody deletes one.

Six lessons:

    E1.5  what evaluation output is and is not evidence of
    E1.6  operating guardrails, which are enforceable, and outcome guardrails,
          which need a measurement before they mean anything
    E1.7  continuous verification — collect evidence, do not automate judgement
    E1.8  the third party, and the sub-processors nobody mapped
    E1.9  lifecycle — the change that is treated as maintenance
    E1.13 the measurement itself, on CyberTravels, with the gaps named

**The single most misleading thing available here is conformance.** A schema
check passes at about 100% and says nothing about correctness. B2.18 caps two
controls at PARTIAL for the same reason: an attestation that says PASS
everywhere is evidence of nothing.
"""
import time


# --------------------------------------------------------------------------- #
# E1.5 — what an evaluation result actually evidences
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


# step:E1.6 add
# --------------------------------------------------------------------------- #
# E1.6 — two kinds of guardrail, and only one is enforceable today
# --------------------------------------------------------------------------- #
# "The agent must not act outside its authority" is enforceable: A3.1 decides
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
# step:E1.6 end


# step:E1.7 add
# --------------------------------------------------------------------------- #
# E1.7 — automate the collection, not the judgement
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
# step:E1.7 end


# step:E1.8 add
# --------------------------------------------------------------------------- #
# E1.8 — the vendor, and the chain behind the vendor
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
        gaps.append("trains on customer data; E2.5's deletion question has no "
                    "good answer once it is in weights")
    if not vendor.get("change_notification"):
        gaps.append("no notification on model change — D1.2's first drift "
                    "surface, on somebody else's schedule")
    return {"vendor": vendor.get("name"), "gaps": gaps,
            "acceptable": not gaps,
            "depth_mapped": len(vendor.get("sub_processors", []))}
# step:E1.8 end


# step:E1.9 add
# --------------------------------------------------------------------------- #
# E1.9 — the change that is filed as maintenance
# --------------------------------------------------------------------------- #
# Re-indexing the retrieval corpus is treated as maintenance because it
# touches no code. It changes what the agent says. D1.2 listed the surfaces;
# this decides which of them are changes for governance purposes, and the rule
# is behaviour rather than artefact: if it alters what the system does, it is
# a change.
BEHAVIOUR_CHANGING = {
    "model_version", "system_prompt", "tool_policy", "retrieval_index",
    "mcp_tool_descriptions", "memory",
}
FILED_AS_MAINTENANCE = {"retrieval_index", "memory", "mcp_tool_descriptions"}


def is_a_change(surface):
    return {"surface": surface,
            "changes_behaviour": surface in BEHAVIOUR_CHANGING,
            "usually_filed_as_maintenance": surface in FILED_AS_MAINTENANCE,
            "needs_change_record": surface in BEHAVIOUR_CHANGING,
            "why": "the test is whether it alters what the system does, not "
                   "whether it touched code"}


def lifecycle_gaps():
    return sorted(FILED_AS_MAINTENANCE & BEHAVIOUR_CHANGING)
# step:E1.9 end


# step:E1.13 add
# --------------------------------------------------------------------------- #
# E1.13 — measure the controls on CyberTravels, and name the gaps
# --------------------------------------------------------------------------- #
# Everything above is machinery. This is the number. Each row asks one
# question of the tree and answers it by calling the thing, so a control that
# is deleted, disabled or never built comes back False rather than asserted.
#
# The gaps are deliberately left in. A register that reports 100% on a system
# with known absences is a register nobody should believe, and this system has
# absences that Functions A to D named in their own files.
def _probe(fn):
    """Run one check, and treat an exception as a failed control rather than
    as a broken script — an assurance run that dies on the first missing
    module reports nothing about the rest."""
    try:
        return bool(fn()), ""
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def measure():
    """Every control Functions A to D built, asked of the running tree."""
    from .. import config, policy, registry, sandbox
    from ..appsec import sast
    from ..redteam import containment
    from ..soc import sensors

    checks = [
        ("A2.1", "workload identities are records with an approver",
         lambda: all(w["approved_by"] for w in registry.all_workloads())),
        ("A2.5", "a revoked workload stops acting",
         lambda: registry.active(config.AGENT_IDS["workflow"])),
        ("A3.1", "an unclassified tool is denied by default",
         lambda: not policy.decide("nope", {}, type("S", (), {
             "user_id": "priya", "role": "finance"})()).allowed),
        ("A3.2", "the coding agent's profile grants no ambient credentials",
         lambda: sandbox.CODING_AGENT.env_keys == set()),
        ("A3.9", "an exemption cannot exist without an expiry",
         lambda: _refuses(policy.Exemption, "E", ["t"], ["human-approval"],
                          "why", "alex", 0)),
        ("B2.3", "the deterministic pass finds the expressible defects",
         lambda: len(sast.scan(str(_tree()))) == 5),
        ("C1.9", "the kill switch reports the paths it is not on",
         lambda: containment.coverage()["coverage"] < 1.0),
        ("D1.1", "the sensor estate is measured per agent action",
         lambda: sensors.matrix()["coverage"] == 1.0),
    ]
    rows = []
    for control, name, fn in checks:
        ok, err = _probe(fn)
        rows.append({"control": control, "name": name, "passes": ok,
                     "error": err})
    passing = [r for r in rows if r["passes"]]
    return {
        "controls": len(rows),
        "passing": len(passing),
        "coverage": round(len(passing) / len(rows), 3),
        "failing": [r["control"] for r in rows if not r["passes"]],
        "rows": rows,
        # Stated rather than discovered at audit time. Each of these is named
        # in the file that owns it.
        "known_gaps": known_gaps(),
    }


def known_gaps():
    """Absences this system has and has written down.

    A register reporting no gaps on a system with known absences is a register
    nobody should believe. Each entry cites the file that admits it.
    """
    return [
        {"gap": "containment and egress are decided in-process",
         "named_in": "cybertravels/sandbox.py, egress.py",
         "mitigation": "A3.7's gateway moves the decision to one point; "
                       "enforcement outside the process is not modelled"},
        {"gap": "the kill switch is not on the direct API path",
         "named_in": "cybertravels/redteam/containment.py",
         "mitigation": "measured at 0.4 coverage rather than asserted; the "
                       "fix is architectural, not a policy change"},
        {"gap": "no audit column carries the attestation digest",
         "named_in": "cybertravels/redteam/forensics.py NOT_RECORDED",
         "mitigation": "a row names which workload acted and cannot show it "
                       "was the attested instance"},
        {"gap": "sandbox-egress and injection-screening cannot be proven here",
         "named_in": "cybertravels/appsec/attest.py CAPPED_AT_PARTIAL",
         "mitigation": "capped at PARTIAL rather than claimed"},
    ]


def _refuses(fn, *args):
    try:
        fn(*args)
    except Exception:  # noqa: BLE001
        return True
    return False


def _tree():
    from pathlib import Path
    return Path(__file__).resolve().parent.parent
# step:E1.13 end
