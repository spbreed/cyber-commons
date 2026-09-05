#!/usr/bin/env python3
"""Show why a dead-code finding is a false positive about risk, and why suppressing it rots while deleting the code does not.

This is the executable half of the `dead-code-attack-surface` skill. It runs
against CyberTravels' booking service: eight findings, a call graph with three
untrusted entry points, and one commit six weeks later that wires a dead
function back up.

Standard library only, and deterministic.
"""

# (finding, unit, cwe, severity_if_reachable, why_unreachable | None)
FINDINGS = [
    ("F1", "search_bookings",  "CWE-89",  9, None),
    ("F2", "render_itinerary", "CWE-95",  8, None),
    ("F3", "legacy_export",    "CWE-78",  9, "dead: no caller anywhere in the repo"),
    ("F4", "debug_dump",       "CWE-22",  6, "dead: no caller anywhere in the repo"),
    ("F5", "_fixture_seed",    "CWE-89",  7, "test fixture, not shipped"),
    ("F6", "beta_pricing",     "CWE-89",  7, "behind a flag that has been off for two years"),
    ("F7", "handle_webhook",   "CWE-78",  9, "resolved by the framework at runtime"),
    ("F8", "audit_line",       "CWE-117", 3, "dead: no caller anywhere in the repo"),
]

# Step 1 — three buckets. `handle_webhook` is dynamic dispatch: the analysis
# cannot decide, and "cannot decide" is not "unreachable".
DYNAMIC = {"handle_webhook"}


def bucket(why, unit):
    if why is None:
        return "reachable"
    return "unknown" if unit in DYNAMIC else "unreachable"


rows = [(f, unit, cwe, sev, why, bucket(why, unit)) for f, unit, cwe, sev, why in FINDINGS]
buckets = {b: sum(1 for r in rows if r[5] == b) for b in ("reachable", "unreachable", "unknown")}

print(f"{len(rows)} findings, partitioned by reachability from an untrusted entry point")
for f, unit, cwe, sev, why, b in rows:
    print(f"   {f}  {unit:<18}{cwe:<9}sev {sev}   {b:<12}{why or ''}")
print()
print(f"   reachable {buckets['reachable']}   unreachable {buckets['unreachable']}"
      f"   unknown {buckets['unknown']}")
print()
print("Every one of those eight is a true positive about the code. A reviewer")
print("who opens the file will agree with all eight. Only two of them are true")
print("about the risk, and that is a different claim.")
print()

report = {"buckets": buckets,
          "queue": {"before": len(rows), "after_reachability": buckets["reachable"]}}

# Step 2 — why it is unreachable decides what you may do about it.
print("why unreachable, and what that permits")
DELETABLE = "dead: no caller anywhere in the repo"
candidates = [r for r in rows if r[4] == DELETABLE]
conditional = [r for r in rows if r[5] == "unreachable" and r[4] != DELETABLE]
print(f"   {len(candidates)} dead with no caller       -> deletion candidates")
print(f"   {len(conditional)} unreachable *under a condition* -> not dead. A flag can be")
print(f"       turned on and a fixture can be imported; both are reachable the")
print(f"       day somebody changes one line.")
print()

# Steps 3-5 — the three responses to the same finding, F3.
print("three responses to F3 (dead os.system on a caller-supplied path, sev 9)")
print(f"   {'action':<12}{'finding gone':<14}{'risk gone':<12}rots?")
RESPONSES = [
    ("suppress",  True,  False, True,
     "keyed to file+line+rule; none of those change when it is wired back up"),
    ("wont-fix",  True,  False, True,
     "the same decision with a nicer label and no expiry either"),
    ("delete",    True,  True,  False,
     "the code is gone, so the finding and the latent risk go together"),
]
report["responses"] = []
for action, cleared, risk, rots, why in RESPONSES:
    print(f"   {action:<12}{'yes' if cleared else 'no':<14}"
          f"{'yes' if risk else 'NO':<12}{'yes' if rots else 'no'}   {why}")
    report["responses"].append({"finding": "F3", "action": action,
                                "finding_cleared": cleared, "risk_cleared": risk,
                                "rots": rots})
print()

# The failure, six weeks later. This is the whole argument.
print("six weeks later, one commit:")
print("   + from .legacy import legacy_export      # re-enable the vendor export")
print()
resurrected = 0
for action, *_ in RESPONSES:
    if action == "delete":
        print(f"   {action:<12}-> the import does not resolve. The build fails, loudly,")
        print(f"                  at the moment somebody tries to bring it back.")
    else:
        resurrected += 1
        print(f"   {action:<12}-> legacy_export is now reachable from the vendor")
        print(f"                  webhook. The suppression is keyed to the same file,")
        print(f"                  line and rule, so it still matches. THE FINDING")
        print(f"                  DOES NOT COME BACK.")
report["resurrected"] = resurrected
print()

# Attack surface reduction, stated as what it removes rather than as a project.
surface = [f"{unit} ({cwe}, sev {sev})" for _, unit, cwe, sev, why, _ in rows
           if why == DELETABLE]
report["asr"] = {"deleted": len(candidates), "surface_removed": surface}
print("attack surface reduction — what deleting those three removes")
for s in sorted(surface):
    print(f"   {s}")
print()
print(f"queue: {report['queue']['before']} findings -> "
      f"{report['queue']['after_reachability']} after reachability, and "
      f"{len(candidates)} of the")
print("remainder are a deletion rather than a triage. The security queue is the")
print("cheapest to-delete list anyone in the building has, already ranked by")
print("what each line would cost if it were ever reachable again.")
print()
print(f"resurrected under a suppression: {resurrected} of {len(RESPONSES)} responses.")
print("That is the number suppression optimises and deletion removes.")

assert buckets["unknown"] == 1, "dynamic dispatch must not be filed as unreachable"
assert resurrected == 2, "both non-deleting responses must resurrect"
assert report["asr"]["deleted"] == 3
