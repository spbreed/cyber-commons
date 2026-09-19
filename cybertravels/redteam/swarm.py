# step:file D1.5
"""Many runs at once — and the three problems that only exist at that scale.

One agent is a system you can reason about. Two hundred running concurrently
is a different object, and the difference is not arithmetic. Three lessons
here, each about something that is invisible from inside a single run:

    D1.5  correlation — every run passes its own checks, and together they
          are doing one thing
    D1.6  detections that survive the volume — a rule with 2% false positives
          is excellent at ten runs an hour and unusable at ten thousand
    D1.7  triage with a floor — what happens to the queue nobody can read

B3.8 built the record this reads: `db.run_artefacts` says which run touched
which object. That table exists because per-run isolation checks cannot see a
channel between runs, and this is the analysis it was built for.
"""
import statistics
from collections import Counter


# --------------------------------------------------------------------------- #
# D1.5 — what only shows up across runs
# --------------------------------------------------------------------------- #
def correlate(runs):
    """`runs` is [{"trace_id", "tools", "targets", "artefacts"}, ...].

    Three signals, and none of them is anomalous inside one run:

    * a **shared artefact** — one run writes, others read (B3.8's channel);
    * a **repeated trajectory** — the same tool sequence, which is either a
      fleet doing its job or a fleet being driven;
    * a **novel token** — a string that appears in many runs and in no
      baseline, which is what a coordinating instruction looks like from the
      outside.
    """
    writers, readers = {}, {}
    for run in runs:
        for ref, mode in run.get("artefacts", []):
            (writers if mode == "write" else readers).setdefault(
                ref, set()).add(run["trace_id"])
    shared = [{"ref": ref, "written_by": sorted(w),
               "read_by_others": sorted(readers.get(ref, set()) - w)}
              for ref, w in writers.items() if readers.get(ref, set()) - w]

    paths = Counter(tuple(r.get("tools", ())) for r in runs)
    repeated = [{"trajectory": list(p), "runs": n}
                for p, n in paths.most_common() if n > 1]

    return {"runs": len(runs),
            "shared_artefacts": sorted(shared, key=lambda s: s["ref"]),
            "repeated_trajectories": repeated,
            "distinct_trajectories": len(paths),
            # The ratio worth watching. A fleet doing varied work has many
            # distinct paths; a driven one converges.
            "convergence": round(1 - len(paths) / max(len(runs), 1), 4)}


def novel_tokens(runs, baseline, *, min_runs=3):
    """Strings present across several runs and absent from the baseline."""
    seen = Counter()
    for run in runs:
        for token in set(run.get("tokens", ())):
            if token not in baseline:
                seen[token] += 1
    return sorted(t for t, n in seen.items() if n >= min_runs)


# step:D1.6 add
# --------------------------------------------------------------------------- #
# D1.6 — a rule's false-positive rate is a volume, not a percentage
# --------------------------------------------------------------------------- #
# Detection engineering habitually reports precision. Precision is a ratio and
# an analyst's day is a count, so the useful question is not "how precise is
# this rule" but "how many alerts does it produce per shift, and can anybody
# work them".
#
# The arithmetic is unforgiving and it is the whole lesson: a rule with 98%
# precision on a hundred events a day is two alerts. The same rule on a
# hundred thousand agent events is two thousand.
def firing_volume(rule, events_per_day):
    """Alerts per day at this volume, and whether a team could work them."""
    tp = events_per_day * rule["true_rate"]
    fp = events_per_day * rule["false_rate"]
    total = tp + fp
    return {
        "rule": rule["name"], "events_per_day": events_per_day,
        "alerts_per_day": round(total, 1),
        "false_per_day": round(fp, 1),
        "precision": round(tp / total, 4) if total else None,
        # Ten minutes an alert, one analyst, a seven-hour working day.
        "analyst_days": round(total * 10 / 60 / 7, 2),
    }


def deployable(rule, events_per_day, *, analysts=1):
    """Would this rule be worked, or silently ignored?

    A rule that needs three analysts and has one is not a rule with a backlog.
    It is a rule that gets muted, and a muted rule is worse than an absent one
    because the coverage report still counts it.
    """
    v = firing_volume(rule, events_per_day)
    v["deployable"] = v["analyst_days"] <= analysts
    v["verdict"] = ("workable" if v["deployable"] else
                    f"needs {v['analyst_days']} analysts and has {analysts} — "
                    f"this rule will be muted, and coverage will still count it")
    return v
# step:D1.6 end


# step:D1.7 add
# --------------------------------------------------------------------------- #
# D1.7 — triage with a floor
# --------------------------------------------------------------------------- #
# When the queue is longer than the day, something is not going to be looked
# at. That is arithmetic, and pretending otherwise is how the thing nobody
# looked at turns out to be the incident.
#
# So decide it explicitly. Rank, take what the capacity allows, and — the part
# that makes this a control rather than a triage strategy — **sample what was
# auto-closed**, so the closing rule itself is measured. Without the sample,
# the rule that closes 80% of the queue is unfalsifiable.
FLOOR_SAMPLE = 0.05


def triage(alerts, capacity, *, rank, sample=FLOOR_SAMPLE):
    """Rank, cut at capacity, and sample below the line."""
    ordered = sorted(alerts, key=rank, reverse=True)
    worked, below = ordered[:capacity], ordered[capacity:]
    # Deterministic stride rather than a random draw: a sample somebody cannot
    # reproduce is a sample somebody can argue with after the incident.
    step = max(1, int(1 / sample)) if sample else 0
    sampled = below[::step] if step else []
    return {
        "received": len(alerts), "capacity": capacity,
        "worked": len(worked), "below_the_line": len(below),
        "sampled_from_below": len(sampled),
        "sample_rate": sample,
        "unreviewed": len(below) - len(sampled),
        "items": {"worked": worked, "sampled": sampled},
    }


def floor_miss_rate(sampled, is_real):
    """What the sample found below the line. The number that makes the floor
    honest — if it is not zero, the ranking is wrong, and the queue is being
    cut in the wrong place rather than merely being too long."""
    if not sampled:
        return {"sampled": 0, "missed": 0, "rate": None,
                "note": "nothing was sampled, so the closing rule is untested"}
    missed = sum(1 for a in sampled if is_real(a))
    return {"sampled": len(sampled), "missed": missed,
            "rate": round(missed / len(sampled), 4),
            "note": "a non-zero rate here means real alerts are below the "
                    "line: fix the ranking before adding capacity"}


def queue_pressure(arrivals_per_day, capacity_per_day, days=30):
    """How the backlog grows. A queue that grows at all grows without bound."""
    backlog, series = 0, []
    for _ in range(days):
        backlog = max(0, backlog + arrivals_per_day - capacity_per_day)
        series.append(backlog)
    return {"final_backlog": series[-1], "peak": max(series),
            "stable": series[-1] == 0,
            "mean": round(statistics.mean(series), 1)}
# step:D1.7 end
