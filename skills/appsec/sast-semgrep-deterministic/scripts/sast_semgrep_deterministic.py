#!/usr/bin/env python3
"""Score three real Semgrep runs against a hand-written key, and report recall per ruleset width.

This is the executable half of the `sast-semgrep-deterministic` skill. The
findings are not synthetic: they are the output of **Semgrep 1.176.0** run
against the `cybertravels/` sample repository — the reference architecture
from A1.1, as source — at three widths. The raw JSON is committed next to
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

# Step 1 — the key, from cybertravels/LABELS.md, written by reading the tree
# before any scan. `expressible` is the question that decides what a scanner
# could ever do, and it has three values rather than two.
#   yes      a pattern matches it
#   library  a pattern matches it in a library the rule knows about
#   no       the defect is the absence of a call; there is nothing to match
KEY = [
    ("tools/bookings_api.py",  20, "get_booking",      "CWE-639", "no",
     "returns the row a caller names, no owner comparison"),
    ("tools/bookings_api.py",  34, "cancel_booking",   "CWE-639", "no",
     "cancels the booking a caller names, and it writes"),
    ("tools/bookings_api.py",  41, "search_bookings",  "CWE-89",  "yes",
     "reference concatenated into the query"),
    ("tools/payments_api.py",   8, "issue_refund",     "CWE-639", "no",
     "refunds against any booking id, on the money path"),
    ("tools/payments_api.py",  23, "download_invoice", "CWE-22",  "yes",
     "vendor filename joined to a root"),
    ("agents/coding_agent.py", 13, "_open_branch",     "CWE-78",  "yes",
     "branch name reaches a shell"),
    ("agents/coding_agent.py", 18, "sync_vendor",      "CWE-295", "library",
     "verify=False, on the house HTTP wrapper rather than requests"),
    ("agents/file_agent.py",   11, "render_template",  "CWE-95",  "yes",
     "customer template evaluated"),
]
KEY_SITES = {(f, ln) for f, ln, *_ in KEY}

runs = json.loads(EVIDENCE.read_text())
ORDER = ["narrow", "wide", "taint"]

expressible = sum(1 for k in KEY if k[4] != "no")
print(f"semgrep {runs['narrow']['semgrep_version']} · cybertravels/ · "
      f"{len(KEY)} defects in the key, {expressible} of them expressible "
      f"as a pattern")
print()

report = {"key": {"defects": len(KEY), "pattern_expressible": expressible},
          "runs": []}
found_by_any = set()

print(f"{'config':<24}{'found':>6}{'tp':>4}{'fp':>4}{'prec':>7}{'recall':>8}")
for name in ORDER:
    run = runs[name]
    sites = {(f["file"], f["line"]) for f in run["findings"]}
    found_by_any |= sites
    tp = len(sites & KEY_SITES)
    fp = len(sites - KEY_SITES)
    precision = tp / len(sites) if sites else 0.0
    recall = tp / len(KEY)
    print(f"{run['config']:<24}{len(run['findings']):>6}{tp:>4}{fp:>4}"
          f"{precision:>7.2f}{recall:>8.2f}")
    report["runs"].append({"config": run["config"], "findings": len(run["findings"]),
                           "true_positives": tp, "precision": round(precision, 2),
                           "recall": round(recall, 2)})
print()

# Step 5 — the width is the finding. Same tree, same engine, three times the
# result on the widest setting, and every scan exits 0.
print("Nothing about the tree changed between those rows. The narrow run looked")
print("for two of the eight and found one; the wide run looked for more. Both")
print("exit 0. A finding count with no config beside it is not a result.")
print()

# Step 4 — partition the misses. This is the part that decides what to buy.
print("missed by every width:")
report["missed_by_all"] = []
for f, ln, unit, cwe, expr, what in KEY:
    if (f, ln) in found_by_any:
        continue
    cls = {"yes": "coverage-gap", "library": "wrong-library",
           "no": "not-expressible"}[expr]
    print(f"   {f.split('/')[-1]:<18}{unit:<18}{cwe:<9}{cls:<17}{what}")
    report["missed_by_all"].append({"file": f, "line": ln, "unit": unit,
                                    "cwe": cwe, "class": cls})
print()

by_class = {}
for m in report["missed_by_all"]:
    by_class.setdefault(m["class"], []).append(m["unit"])

print(f"{len(by_class.get('coverage-gap', []))} coverage gap: a pattern matches this "
      f"and nobody enabled a rule for it.")
print("   Write the rule. It is an afternoon.")
print()
print(f"{len(by_class.get('wrong-library', []))} wrong library: sync_vendor disables TLS "
      f"verification, which is")
print("   textbook - on CyberTravels' own HTTP wrapper. Every registry rule for")
print("   it is written against `requests`, so no pack fires. This is the single")
print("   most common reason a mature codebase scans cleaner than it is, and the")
print("   fix is a rule that names YOUR wrapper, not a different scanner.")
print()
print(f"{len(by_class.get('not-expressible', []))} not expressible as a pattern - all "
      f"three are IDOR:")
for unit in by_class.get("not-expressible", []):
    print(f"      {unit}")
print("   Each takes an identifier and returns or mutates the record it names,")
print("   and never compares an owner. `get_my_booking` two functions away does")
print("   the same read correctly. The defect is not in either function - it is")
print("   the missing comparison BETWEEN loading and returning, and there is no")
print("   syntax for a thing that is absent. No ruleset reaches these at any")
print("   width, ever. That is the boundary, and B2.3's next skill crosses it.")
print()

widest = max(r["recall"] for r in report["runs"])
report["widest_recall"] = widest
print(f"widest recall: {widest:.2f}")
print("Precision is 1.00 at every width. Semgrep's problem here was never that")
print("it was wrong - it is that five of eight were never in scope, and three of")
print("those five could not have been.")

assert all(r["precision"] == 1.0 for r in report["runs"]), "a run reported a false positive"
assert widest < 1.0, "if the widest width found everything, the key is too easy"
assert len(by_class.get("not-expressible", [])) == 3, "the three IDORs must survive every width"
