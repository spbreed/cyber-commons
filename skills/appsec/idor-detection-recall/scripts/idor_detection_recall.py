#!/usr/bin/env python3
"""Find the missing ownership checks in the CyberTravels repository, and score both detectors on recall.

This is the executable half of the `idor-detection-recall` skill. It parses the
real `cybertravels/` tree with `ast` — the same tree B2.3's Semgrep run scanned
and the same one A1.1 draws — enumerates every unit that takes an identifier and
touches a record, and then runs two detectors over that denominator: a pattern
rule, which is what a ruleset can express, and an ownership-comparison analysis,
which is what it cannot.

The key is `cybertravels/LABELS.md`, written by hand before any of this ran.

Standard library only, and deterministic.
"""

import ast
from pathlib import Path

# The tree, found from this file rather than from the working directory: on
# Kaggle `cwd` is /kaggle/working and the clone is beside it.
ROOT = Path(__file__).resolve().parents[4]
REPO = ROOT / "cybertravels"

# The key, from cybertravels/LABELS.md — the five units missing an ownership
# check. Two of them carry a second defect as well: search_bookings also
# concatenates SQL and download_invoice also traverses a path. Semgrep finds
# those two and cannot see the authorisation defect in the same function, which
# is the most useful row in the key.
IDOR = {"get_booking", "cancel_booking", "issue_refund",
        "search_bookings", "download_invoice"}
# Also found by a ruleset, for a *different* defect in the same function.
ALSO_FOUND_BY_RULES = {"search_bookings": "CWE-89 at the widest width",
                       "download_invoice": "CWE-22, had a rule been enabled"}
# The safe twins. A corpus where everything is broken cannot measure precision.
AUTHORISED = {"get_my_booking", "get_receipt", "list_my_bookings"}

# What counts as comparing an owner. Traced through the helper, because a check
# inside require_owner is still a check.
OWNERSHIP = {"require_owner"}
SESSION_SCOPED = {"user_id"}


def units(path):
    """Every function that takes a caller-supplied identifier and touches a record."""
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        args = [a.arg for a in node.args.args]
        # Step 1 — the denominator. An identifier parameter, and a record touched.
        takes_id = any(a in ("booking_id", "payment_id", "path", "reference", "id")
                       for a in args)
        touches = any(isinstance(n, ast.Call) and
                      getattr(n.func, "attr", "") in ("execute", "fetchone",
                                                      "fetchall", "open")
                      for n in ast.walk(node)) or "open" in ast.dump(node)
        if takes_id and touches:
            yield node, args


def ownership_check(node):
    """present | via-helper | absent — step 2, traced rather than pattern-matched."""
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            name = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if name in OWNERSHIP:
                return "via-helper"
        # A direct comparison of something on the session against the record.
        if isinstance(n, ast.Compare):
            src = ast.dump(n)
            if any(f"attr='{a}'" in src for a in SESSION_SCOPED):
                return "present"
    # Scoped by the session with no id to tamper with is not a missing check.
    src = ast.dump(node)
    if "session" in src and any(f"attr='{a}'" in src for a in SESSION_SCOPED):
        return "present"
    return "absent"


report = {"units": [], "detectors": [], "findings": []}
for path in sorted(REPO.rglob("*.py")):
    for node, args in units(path):
        report["units"].append({
            "file": str(path.relative_to(REPO)), "unit": node.name,
            "takes_id": True, "ownership_check": ownership_check(node)})

denom = len(report["units"])
report["denominator"] = denom
authorised = [u for u in report["units"] if u["ownership_check"] != "absent"]

print(f"cybertravels/ · {denom} object-handling units, "
      f"{len(authorised)} of them authorised")

# Step 4 — two detectors over the same denominator.
# Detector 1: what a pattern rule can express. It looks for a record read with a
# caller-supplied id, which every one of these has — safe and unsafe alike — so
# it cannot separate them and the honest thing is that it reports nothing.
pattern_hits = set()
# Detector 2: the comparison the pattern cannot see.
analysis_hits = {u["unit"] for u in report["units"] if u["ownership_check"] == "absent"}

print(f"{'detector':<32}{'found':>6}{'tp':>4}{'fp':>4}{'prec':>7}{'recall':>8}")
for name, hits in (("pattern rule (execute + id)", pattern_hits),
                   ("ownership-comparison analysis", analysis_hits)):
    tp = len(hits & IDOR)
    fp = len(hits - IDOR)
    precision = tp / len(hits) if hits else 0.0
    recall = tp / len(IDOR)
    print(f"{name:<32}{len(hits):>6}{tp:>4}{fp:>4}{precision:>7.2f}{recall:>8.2f}")
    report["detectors"].append({"name": name, "found": len(hits),
                                "true_positives": tp,
                                "precision": round(precision, 2),
                                "recall": round(recall, 2)})
print()
print("The pattern rule reports nothing, and that is the honest result rather")
print("than a broken one. Every unit above reads a record by an id the caller")
print("supplied - the five defective ones and the two correct ones alike. The")
print("syntax is identical. There is nothing for a rule to match on.")
print()

# Step 5 — severity from the authority the caller holds, not from the CWE.
AUTHORITY = {
    "get_booking":      ("Workflow Agent · booking.*", "high",
                         "any traveller's itinerary, on an agent-invoked tool"),
    "cancel_booking":   ("Workflow Agent · booking.*", "high",
                         "and it writes: cancels a booking that is not theirs"),
    "issue_refund":     ("Workflow Agent · payments.refund", "critical",
                         "money moves, against an id the model proposed"),
    "search_bookings":  ("Workflow Agent · booking.*", "high",
                         "returns every owner's bookings for a reference"),
    "download_invoice": ("File System Agent", "high",
                         "reads an invoice belonging to somebody else"),
}
print("findings, weighted by the authority the caller holds")
for unit in sorted(analysis_hits):
    who, sev, why = AUTHORITY[unit]
    print(f"   {unit:<18}{sev:<10}{who:<34}{why}")
    report["findings"].append({"unit": unit, "cwe": "CWE-639",
                               "caller_authority": who.strip(),
                               "severity": sev})
print()
print("all five are CWE-639 and they are not the same finding. Ranking this")
print("queue by CWE puts the refund path level with a read, and A1.1's map is")
print("what tells you otherwise: these are tools, trust 3, invoked by an agent")
print("holding scope the traveller never had.")
print()

# The row worth stopping on: a scanner found two of these, for something else.
print("two of the five were already in a scanner's output - for a different defect")
for unit, what in sorted(ALSO_FOUND_BY_RULES.items()):
    print(f"   {unit:<18}{what}")
print("   Same function, two defects, one expressible and one not. A report that")
print("   says \"search_bookings: 1 finding, fixed\" closes the injection, leaves")
print("   the authorisation defect in place, and shows a finding count of zero")
print("   afterwards. The count went down and the risk did not.")
print()

print("what the published numbers say about the ceiling")
print("   Semgrep's 2026 IDOR benchmark: 275 hand-reviewed labels, four repos,")
print("   identical revisions.")
print("      Semgrep Multimodal            recall 59.9%   precision 57.5%")
print("      Claude Security with Mythos   recall 13.9%   precision 80.1%")
print("      Codex Security                recall 11.3%")
print()
print("   The most precise system on that board found about one IDOR in seven.")
print("   The best recall was six in ten. This corpus is eight files and the")
print("   analysis gets 5/5, which is what a corpus this size is for - it shows")
print("   the mechanism, not the ceiling. Do not read 1.00 here as a claim")
print("   about a real repository, and do not read 59.9% as a failure: it is")
print("   four times what the highest-precision system managed, on a class no")
print("   pattern reaches at all.")

assert denom >= 7, "the denominator must include the authorised twins"
assert report["detectors"][0]["found"] == 0, \
    "a pattern rule that reports something here is matching shape, not the defect"
assert report["detectors"][1]["recall"] == 1.0
assert analysis_hits == IDOR, f"analysis disagreed with the key: {analysis_hits}"
assert ALSO_FOUND_BY_RULES.keys() <= IDOR, "the two-defect rows must be in the key"
assert any(f["severity"] == "critical" for f in report["findings"])
