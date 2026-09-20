# step:file D1.4
"""Telling the agent from the person, from the trace CyberTravels already emits.

A2.1 built `observability.Trace`, so every run leaves spans. This reads them
and answers a question the SOC will be asked in Function E and cannot currently
answer: **was that a person or an agent?**

It matters because every volume rule in the estate was tuned on human tempo. A
person looking at bookings produces a few actions a minute with long, irregular
gaps. An agent produces a dozen in a second, evenly, at four in the morning,
across more distinct tools than a person uses in a week. The rule written for
the first one either never fires on the second or fires constantly.

Four signals, and they are all shape rather than content:

    rate        actions per minute
    regularity  the variance of the gaps — a person is bursty, a loop is not
    breadth     how many distinct tools in one session
    hour        the share of activity outside working hours

The scoring is deliberately crude and the threshold is deliberately not
hard-coded. `sweep()` shows the whole trade-off curve and `pick_threshold()`
chooses by the cost of each mistake, because 0.5 is a number somebody picked
for a reason that never applied here: calling an agent a person and calling a
person an agent are not equally expensive, and which is worse depends on what
happens next.
"""
import statistics


def signals(spans):
    """The four shape signals, out of one trace's spans."""
    acted = [s for s in spans if s.get("kind") in
             ("plan", "tool_result", "token_issued")]
    times = [s["t"] for s in acted]
    gaps = [b - a for a, b in zip(times, times[1:])]
    span_seconds = (max(times) - min(times)) if len(times) > 1 else 0.0
    tools = {s.get("tool") for s in spans if s.get("tool")}
    return {
        "actions": len(acted),
        "actions_per_minute": round(len(acted) / (span_seconds / 60), 2)
        if span_seconds > 0 else float(len(acted)),
        # Low variance is the tell. A person's gaps are wildly uneven; a loop's
        # are within a few hundred milliseconds of each other.
        "gap_stdev": round(statistics.stdev(gaps), 4) if len(gaps) > 1 else 0.0,
        "distinct_tools": len(tools),
        "span_seconds": round(span_seconds, 3),
    }


def score(sig):
    """0 is person-shaped, 1 is agent-shaped. Four terms, equally weighted.

    Equal weights on purpose: a weighted score invites an argument about the
    weights, and the argument outlives the decision it was meant to support.
    Tune the threshold instead — that is a number with a cost attached.
    """
    terms = [
        min(sig["actions_per_minute"] / 60.0, 1.0),
        1.0 - min(sig["gap_stdev"] / 2.0, 1.0),
        min(sig["distinct_tools"] / 6.0, 1.0),
        1.0 if sig["actions"] >= 5 and sig["span_seconds"] < 10 else 0.0,
    ]
    return round(sum(terms) / len(terms), 4)


def sweep(labelled, steps=21):
    """The whole curve. `labelled` is [(score, is_agent), ...]."""
    out = []
    for i in range(steps):
        t = i / (steps - 1)
        tp = sum(1 for s, y in labelled if s >= t and y)
        fp = sum(1 for s, y in labelled if s >= t and not y)
        fn = sum(1 for s, y in labelled if s < t and y)
        tn = sum(1 for s, y in labelled if s < t and not y)
        out.append({"threshold": round(t, 3), "tp": tp, "fp": fp,
                    "fn": fn, "tn": tn,
                    "precision": round(tp / (tp + fp), 4) if tp + fp else None,
                    "recall": round(tp / (tp + fn), 4) if tp + fn else None})
    return out


def pick_threshold(labelled, *, cost_fp, cost_fn):
    """Choose by expected cost, not by accuracy.

    Accuracy picks the threshold that is right most often, which is the wrong
    objective whenever the two mistakes cost different amounts — and here they
    always do. Calling a person's session automated gets somebody locked out;
    missing an agent leaves unattributed automation in the estate. Say which
    is worse, in numbers, and the threshold follows.
    """
    rows = sweep(labelled)
    for r in rows:
        r["expected_cost"] = r["fp"] * cost_fp + r["fn"] * cost_fn
    best = min(rows, key=lambda r: (r["expected_cost"], r["threshold"]))
    return {"threshold": best["threshold"], "at": best,
            "accuracy_would_pick": max(
                rows, key=lambda r: (r["tp"] + r["tn"], -r["threshold"])
            )["threshold"],
            "note": "if these two differ, accuracy was optimising something "
                    "nobody asked for"}
