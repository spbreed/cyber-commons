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


