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














