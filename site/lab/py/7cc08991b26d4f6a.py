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




