#!/usr/bin/env python3
"""Score three real Semgrep runs against a hand-written key, and report recall per ruleset width.

This is the executable half of the `sast-semgrep-deterministic` skill. The
findings are not synthetic: they are the output of **Semgrep 1.176.0** run
against `labs/tools/semgrep-sast/booking.py` — a pull request from
CyberTravels' Coding Agent — at three widths. The raw JSON is committed next to
this script in `evidence/semgrep_runs.json`, and
`labs/tools/semgrep-sast/run.sh` reproduces it:

    semgrep --config=p/python --config=p/secrets            -> narrow
    semgrep --config=p/default ... seven packs ...          -> wide
    semgrep --config=rules/cybertravels-taint.yaml          -> taint

Replaying committed output rather than shelling out keeps the lesson
deterministic and runnable on a kernel with no Semgrep installed. It is the
same JSON the run produced.

Standard library only, and deterministic.
"""

import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent.parent / "evidence" / "semgrep_runs.json"

# Step 1 — the key, written by reading booking.py by hand, before any scan.
# `expressible` is the question that decides whether a rule could ever find it.
KEY = [
    (7,  "CWE-862", "find_booking performs no authorisation check", False),
    (9,  "CWE-89",  "traveller reference concatenated into SQL", True),
    (14, "CWE-95",  "eval() on a customer-supplied template", True),
    (17, "CWE-78",  "vendor host concatenated into a shell command", True),
    (20, "CWE-295", "TLS certificate validation disabled", True),
    (22, "CWE-798", "live-looking API key on a module-level constant", True),
]
KEY_LINES = {line for line, _, _, _ in KEY}

runs = json.loads(EVIDENCE.read_text())
ORDER = ["narrow", "wide", "taint"]

print(f"semgrep {runs['narrow']['semgrep_version']} · booking.py · "
      f"{len(KEY)} defects in the key, "
      f"{sum(1 for k in KEY if k[3])} of them expressible as a pattern")
print()

report = {"key": {"defects": len(KEY),
                  "pattern_expressible": sum(1 for k in KEY if k[3])},
          "runs": []}
found_by_any = set()

print(f"{'config':<24}{'found':>6}{'tp':>4}{'fp':>4}{'prec':>7}{'recall':>8}")
for name in ORDER:
    run = runs[name]
    lines = {f["line"] for f in run["findings"]}
    found_by_any |= lines
    tp = len(lines & KEY_LINES)
    fp = len(lines - KEY_LINES)
    precision = tp / len(lines) if lines else 0.0
    recall = tp / len(KEY)
    print(f"{run['config']:<24}{len(run['findings']):>6}{tp:>4}{fp:>4}"
          f"{precision:>7.2f}{recall:>8.2f}")
    report["runs"].append({"config": run["config"], "findings": len(run["findings"]),
                           "true_positives": tp, "precision": round(precision, 2),
                           "recall": round(recall, 2)})
print()

# Step 5 — the width is the finding. Same file, same engine, four times the
# result, and both scans exit 0.
print("Nothing about the file changed between those rows. Three of the four")
print("defects the wide run reports were simply not looked for on the narrow")
print("one, and it exits 0 either way. A finding count with no config beside")
print("it is not a result.")
print()

# Step 4 — partition the misses. This is the only part that argues for a model.
print("missed by every width:")
report["missed_by_all"] = []
for line, cwe, what, expressible in KEY:
    if line in found_by_any:
        continue
    cls = "coverage-gap" if expressible else "not-expressible"
    print(f"   line {line:>3}  {cwe:<9}{cls:<17}{what}")
    report["missed_by_all"].append({"line": line, "cwe": cwe, "class": cls})
print()

gaps = [m for m in report["missed_by_all"] if m["class"] == "coverage-gap"]
hard = [m for m in report["missed_by_all"] if m["class"] == "not-expressible"]
print(f"{len(gaps)} coverage gap(s): a rule could match this, and nobody wrote it.")
print(f"   line 22 is lexical. p/secrets was enabled and did not fire, because")
print(f"   the string matches no known provider's format. That is a rule to")
print(f"   write, not a reason to buy a different generation of scanner.")
print()
print(f"{len(hard)} not expressible as a pattern:")
print(f"   line 7 is the *absence* of a call, in a function whose caller holds")
print(f"   payments scope. There is no syntax to match. No ruleset reaches it,")
print(f"   at any width, ever - and that is the whole argument for the model")
print(f"   pass, which is the next skill rather than a wider config.")
print()

widest = max(r["recall"] for r in report["runs"])
report["widest_recall"] = widest
print(f"widest recall: {widest:.2f}")
print("Precision is 1.00 at every width. Semgrep's problem here was never")
print("that it was wrong - it is that a third of the key was never in scope.")

assert all(r["precision"] == 1.0 for r in report["runs"]), "a run reported a false positive"
assert widest < 1.0, "if the widest width found everything, the key is too easy"
