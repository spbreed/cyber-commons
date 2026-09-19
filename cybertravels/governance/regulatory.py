# step:file F2.1
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


# step:F2.2 add
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
# step:F2.2 end


# step:F2.3 add
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
# step:F2.3 end


# step:F2.4 add
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
# step:F2.4 end


# step:F2.5 add
# --------------------------------------------------------------------------- #
# F2.5 — personal data, in places a database rights request does not reach
# --------------------------------------------------------------------------- #
# Deletion is straightforward while the data is in a table. It stops being
# straightforward the moment the same text is in a trace, in a memory row, in
# a prompt somebody logged, and — the one with no good answer — in weights.
#
# So audit where it actually is. E1.3 already decided retention per field;
# this is the same list read as a privacy question rather than a cost one.
PII_SHAPES = [
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"), "email address"),
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "a card-length number"),
    (re.compile(r"\bCT-\d{4}\b"), "a booking reference"),
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "an IP address"),
]

# Where the same personal data ends up, and whether erasure reaches it.
SURFACES = {
    "bookings table": True,
    "audit.detail": True,
    "audit.motive_digest": True,     # a digest, which is the point of B2.7
    "trace spans": True,
    "memory rows": True,
    "model provider's logs": False,
    "model weights (if fine-tuned)": False,
}


def scan_text(text):
    return sorted({what for pattern, what in PII_SHAPES
                   if pattern.search(text or "")})


def erasure_reach():
    reachable = [s for s, ok in SURFACES.items() if ok]
    return {"surfaces": len(SURFACES), "erasable": len(reachable),
            "not_erasable": sorted(s for s, ok in SURFACES.items() if not ok),
            "coverage": round(len(reachable) / len(SURFACES), 3),
            "why": "an erasure request answered only for the database is "
                   "answered for the surface that was easiest to reach"}


def audit_trace(rows, *, fields=("detail", "chain")):
    """Personal data sitting in a long-lived store.

    B2.7 records a digest rather than the motivating text precisely so this
    comes back empty for the motive. It does not protect `detail`, which is
    where a tool's arguments land.
    """
    found = []
    for i, r in enumerate(rows):
        for f in fields:
            shapes = scan_text(str(r.get(f, "")))
            if shapes:
                found.append({"row": i, "field": f, "shapes": shapes})
    return {"rows_scanned": len(rows), "hits": found,
            "clean": not found,
            "why": "long-lived rows keep whatever was written into them; "
                   "E1.3's per-field retention is the lever"}
# step:F2.5 end


# step:F2.7 add
# --------------------------------------------------------------------------- #
# F2.7 — documentation a supervisor can use
# --------------------------------------------------------------------------- #
# "Explainability" for a system with no deterministic reasoning is a demand
# that cannot be met as stated, and answering it with a paragraph about
# attention weights fails badly. What can be produced is better and is what a
# supervisor actually needs: what the system is for, what it may do, what
# bounds it, what happened on a given run, and who decided each of those.
SUPERVISORY_SECTIONS = {
    "intended purpose": "what it is for, and what it is not for",
    "authority": "what it may do, and under whose identity",
    "bounds": "budgets, scopes, the human gate and where each is enforced",
    "run record": "what happened on a specific date, reconstructable",
    "decisions": "who approved the autonomy level, and when",
    "known limitations": "including the ones in F1.13's known_gaps",
}


def score_documentation(present):
    have = set(present)
    missing = {k: why for k, why in SUPERVISORY_SECTIONS.items()
               if k not in have}
    return {"sections": len(SUPERVISORY_SECTIONS),
            "present": sorted(have & set(SUPERVISORY_SECTIONS)),
            "missing": missing,
            "score": round(len(have & set(SUPERVISORY_SECTIONS))
                           / len(SUPERVISORY_SECTIONS), 3),
            "why": "none of these is an explanation of the model's reasoning, "
                   "and all of them are things a supervisor can act on"}
# step:F2.7 end


# step:F2.8 add
# --------------------------------------------------------------------------- #
# F2.8 — under whose authority did it act
# --------------------------------------------------------------------------- #
# Imports D1.10's checker rather than restating it. The governance question is
# the same question the investigation asks, arriving earlier and from a
# different person, and it is worth exactly one call.
def auditability(rows, spans, verify_chain):
    from ..redteam.forensics import reconstruct
    r = reconstruct(rows, spans, verify_chain)
    return {"answerable": r["reconstructable"],
            "blockers": r["blockers"],
            "regulator_asks": "under whose authority did the agent act, and "
                              "can you show me for a specific action",
            "why": "this is D1.10's check, asked by a different person at a "
                   "different time; a second implementation would give a "
                   "second answer"}
# step:F2.8 end


# step:F2.9 add
# --------------------------------------------------------------------------- #
# F2.9 — the conversation
# --------------------------------------------------------------------------- #
# Two ways to lose it. Overclaim, and the first thing checked will be the
# claim. Underclaim, and the conversation becomes about whether the system
# should be running at all.
#
# The preparation is arithmetic rather than rhetoric: report accuracy and
# conformance **separately**, report control coverage with the gaps named, and
# rehearse the three openings that actually get used.
OPENINGS = [
    "show me a specific action and tell me who authorised it",
    "what does this system do that you cannot explain",
    "what would have to go wrong for you to stop it",
]


def prepare(measurement, eval_result):
    ev = None
    try:
        from .evidence import evidences
        ev = evidences(eval_result)
    except Exception:  # noqa: BLE001
        pass
    return {
        "control_coverage": measurement["coverage"],
        "controls_failing": measurement["failing"],
        "gaps_named_up_front": [g["gap"] for g in measurement["known_gaps"]],
        "accuracy": eval_result.get("accuracy"),
        "conformance": eval_result.get("conformance"),
        "reported_separately": True,
        "evidence_check": ev,
        "openings": OPENINGS,
        "why": "naming the gaps first is not candour for its own sake — it "
               "is the only version of this conversation where the answers "
               "to the three openings are already written down",
    }
# step:F2.9 end
