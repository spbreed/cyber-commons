#!/usr/bin/env python3
"""Re-measure the key control indicators an incident moved, and say which the fix actually restored.

This is the executable half of `kci-fix-validation`. Closing a ticket is not
evidence. The KCIs defined in E1.1 are measurements; a fix is validated when
the indicators it claimed to restore have been measured again and come back.

Standard library only, and deterministic.
"""

# KCI, what it measures, target, and three readings: healthy, during, after fix.
KCIS = [
    ("KCI-01", "tool calls carrying provenance",        ">= 0.99", 1.00, 0.41, 1.00),
    ("KCI-02", "vendor tool descriptions pinned",       "== 1.00", 1.00, 0.00, 1.00),
    ("KCI-03", "refunds with a matching approval",      ">= 0.99", 1.00, 0.86, 0.94),
    ("KCI-04", "mean minutes to detect a scope breach", "<= 15",   9.0, 194.0, 118.0),
    ("KCI-05", "agents inside declared scope",          "== 1.00", 1.00, 0.97, 1.00),
]


def meets(target, value):
    op, bound = target.split()
    bound = float(bound)
    return {">=": value >= bound, "==": value == bound, "<=": value <= bound}[op]


print(f"{'kci':<8}{'measures':<38}{'target':>9}{'before':>8}{'incident':>10}{'after':>8}  verdict")
report = {"restored": [], "not_restored": [], "regressed": []}
for kid, what, target, before, during, after in KCIS:
    was_ok, broke, now_ok = meets(target, before), not meets(target, during), meets(target, after)
    if not broke:
        verdict = "untouched"
    elif now_ok:
        verdict = "restored"
        report["restored"].append(kid)
    else:
        verdict = "NOT RESTORED"
        report["not_restored"].append(kid)
    print(f"{kid:<8}{what:<38}{target:>9}{before:>8.2f}{during:>10.2f}{after:>8.2f}  {verdict}")
print()
print(f"{len(report['restored'])} restored · {len(report['not_restored'])} not restored")
print()
for kid in report["not_restored"]:
    row = next(k for k in KCIS if k[0] == kid)
    print(f"   {kid}  {row[1]}")
    print(f"          target {row[2]}, measured {row[5]} — the fix did not reach this one")
print()
broke = len(report["restored"]) + len(report["not_restored"])
print(f"This is the whole point of measuring rather than closing. "
      f"{len(report['restored'])} indicators came")
print(f"back to target and {len(report['not_restored'])} did not, and the incident "
      f"record would have said")
print(f"'remediated' for all {broke}.")
print()
print("KCI-04 is the uncomfortable one. Detection time improved from 194 minutes")
print("to 118 and is still eight times the target, so the control the root cause")
print("record named has been partially built. Partially built is not built, and")
print("without the re-measurement it reads as done.")

assert report["not_restored"] == ["KCI-03", "KCI-04"]
assert "KCI-01" in report["restored"] and "KCI-02" in report["restored"]
assert not meets("<= 15", 118.0)
