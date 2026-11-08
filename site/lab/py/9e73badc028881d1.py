"""One programme, mapped to many regimes — not one programme per regime.

The default failure is organisational rather than legal: each regime arrives
through a different function, each function starts a programme, and four
programmes produce four control sets that overlap by about eighty per cent and
disagree at the edges. The work is quadrupled and none of it is joined up.

The fix is the same shape as F1.4's: build the control set once, map it
outward, and let each regime be a **view** over it. Nine lessons here, and
every one of them is a different view of the same evidence.
"""
import re


# An obligation is a sentence in a regime. A control is a thing you built.
# The mapping is many-to-many and that is the point: one control answers
# several obligations, which is the saving.
OBLIGATIONS = {
    "EU AI Act Art. 12": ("record-keeping over the system's lifetime",
                          ["B2.8", "B2.7", "E1.3"]),
    "EU AI Act Art. 14": ("human oversight, effective and not nominal",
                          ["B3.6", "E4.2"]),
    "EU AI Act Art. 15": ("accuracy, robustness and cybersecurity",
                          ["B3.1", "B3.3", "D1.0"]),
    "GDPR Art. 5(1)(e)": ("storage limitation", ["E1.3"]),
    "GDPR Art. 33": ("breach notification within 72 hours", ["E5.6"]),
    "GDPR Art. 17": ("erasure", ["F2.5"]),
    "NIS2 Art. 23": ("incident reporting, 24-hour early warning", ["E5.6"]),
    "DORA Art. 17": ("ICT incident management", ["E4.3", "E5.2"]),
    "SOC 2 CC7.2": ("monitoring for anomalies", ["E2.2", "E2.3"]),
    "ISO 42001 8.3": ("AI system impact assessment", ["F1.3"]),
}


def map_obligations(controls_in_place):
    """Which obligations the controls you have already answer."""
    have = set(controls_in_place)
    rows = []
    for obligation, (what, controls) in sorted(OBLIGATIONS.items()):
        met = [c for c in controls if c in have]
        rows.append({"obligation": obligation, "requires": what,
                     "controls": controls, "in_place": met,
                     "satisfied": len(met) == len(controls),
                     "partial": bool(met) and len(met) < len(controls)})
    return {
        "obligations": len(rows),
        "satisfied": sum(1 for r in rows if r["satisfied"]),
        "partial": sum(1 for r in rows if r["partial"]),
        "unmet": [r["obligation"] for r in rows if not r["in_place"]],
        # The number that argues against one programme per regime.
        "controls_reused": _reuse(),
        "rows": rows,
    }


def _reuse():
    counts = {}
    for _what, controls in OBLIGATIONS.values():
        for c in controls:
            counts[c] = counts.get(c, 0) + 1
    shared = {c: n for c, n in counts.items() if n > 1}
    return {"controls": len(counts), "answering_more_than_one": len(shared),
            "most_reused": sorted(shared.items(), key=lambda kv: -kv[1])[:3]}


# --------------------------------------------------------------------------- #
# F2.2 — "we only deployed it, we didn't build it"
# --------------------------------------------------------------------------- #
# Sometimes true. Often not, and the tests are specific rather than a matter
# of opinion: fine-tuning, putting your name on it, changing its intended
# purpose, or making substantial modifications all move a deployer into the
# provider's obligations, and every one of those is something an engineering
# team does without telling compliance.
DEPLOYER_BECOMES_PROVIDER = {
    "renamed_or_rebranded": "put your name or trademark on it",
    "fine_tuned": "trained it further on your data",
    "changed_intended_purpose": "used it for something the provider did not "
                                "state it was for",
    "substantially_modified": "changed it after it was placed on the market",
}


def role(deployment):
    triggers = [why for k, why in DEPLOYER_BECOMES_PROVIDER.items()
                if deployment.get(k)]
    return {"role": "provider" if triggers else "deployer",
            "triggers": triggers,
            "why": "each trigger is something an engineering team does "
                   "routinely and does not think of as a regulatory event"}


def requirement_to_control(requirement, *, evidence_artefact):
    """Turn a prose requirement into something with an artefact behind it.

    The show-me test: if the answer to "show me" is a paragraph, this is not
    yet a control.
    """
    if not evidence_artefact:
        return {"requirement": requirement, "control": None,
                "passes_show_me": False,
                "why": "the answer to 'show me' is prose — name the artefact, "
                       "or say plainly that this is not yet controlled"}
    return {"requirement": requirement, "control": evidence_artefact,
            "passes_show_me": True}


# --------------------------------------------------------------------------- #
# F2.3 — pick a spine, supply the remainder
# --------------------------------------------------------------------------- #
# Choose the framework that covers the most of the controls you actually have,
# use it as the structure, and take the remainder from the others. The
# alternative — a mapping per regime with nothing to hang it off — produces
# documents rather than a programme.
def choose_spine(frameworks, controls_in_place):
    have = set(controls_in_place)
    scored = []
    for name, covered in frameworks.items():
        overlap = have & set(covered)
        scored.append({"framework": name, "covers": len(overlap),
                       "of_yours": round(len(overlap) / max(len(have), 1), 3)})
    scored.sort(key=lambda s: -s["covers"])
    spine = scored[0]
    remainder = sorted(have - set(frameworks[spine["framework"]]))
    return {"spine": spine["framework"], "ranked": scored,
            "not_covered_by_the_spine": remainder,
            "why": "the remainder comes from the other frameworks as "
                   "supplements; it does not need a second programme"}


# --------------------------------------------------------------------------- #
# F2.4 — the overlay you already comply with
# --------------------------------------------------------------------------- #
# The useful discovery in most sectors is that the agent is already covered by
# rules the organisation has followed for years under a different name. An
# agent that scores, decides or recommends is a **model** under model-risk
# rules, and those rules already have validation, inventory and change
# requirements that nobody thought to apply here.
OVERLAYS = {
    "financial services": [
        ("SR 11-7 / model risk", "an agent that decides is a model, and "
                                 "model inventory and validation already apply"),
        ("DORA", "ICT third-party risk covers the model provider"),
    ],
    "healthcare": [("clinical decision support", "an agent that recommends "
                                                 "may be a medical device")],
    "travel": [("PCI DSS", "the refund path touches cardholder data; "
                           "B3.1's decision point is already in scope")],
}


def overlays(sector):
    rows = OVERLAYS.get(sector, [])
    return {"sector": sector,
            "overlays": [{"regime": r, "why": w} for r, w in rows],
            "already_complied_with": bool(rows),
            "why": "the cheapest control in the programme is one you are "
                   "already operating under another name"}








