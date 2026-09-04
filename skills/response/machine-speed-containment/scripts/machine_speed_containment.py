#!/usr/bin/env python3
"""Race an agent's action rate against an approval delay, time the whole containment path, and decide what may auto-revoke.

This is the executable half of the `machine-speed-containment` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

def race(actions_per_min, human_minutes, auto_seconds=12):
    manual = actions_per_min * human_minutes
    auto   = actions_per_min * (auto_seconds/60)
    return {"manual": round(manual), "auto": round(auto),
            "ratio": round(manual/max(auto, 1e-9), 1)}

print(f"{'agent rate':>13}{'human 8min':>13}{'auto 12s':>11}{'ratio':>8}")
print("-" * 46)
for rate in (30, 120, 300, 1200):
    r = race(rate, 8)
    print(f"{rate:>9}/min{r['manual']:>13}{r['auto']:>11}{r['ratio']:>8}×")
print("\nAt 300/min an 8-minute approval costs 2,400 further actions.")

PATH = [
 ("detection fires",              8,   "rule evaluation + SIEM ingestion lag"),
 ("analyst picks it up",          240, "queue depth at 02:00"),
 ("analyst decides to contain",   180, "confirming it is not a false positive"),
 ("approval requested",           480, "on-call manager, out of hours"),
 ("revocation executed",          12,  "the only step anyone measures"),
]
total = sum(s for _, s, _ in PATH)
print(f"{'step':30s}{'seconds':>9}  why")
print("-" * 74)
for name, secs, why in PATH:
    print(f"{name:30s}{secs:>9}  {why}")
print(f"{'TOTAL':30s}{total:>9}  = {total/60:.0f} minutes")
print(f"\nat 300 actions/min that is {300*total/60:,.0f} further actions.")
print("The 12-second revocation is 1.3% of the elapsed time. Optimising it")
print("is not where the win is.")

SIGNALS = {
 "reached the cloud metadata service": 0.99,
 "read a path matching */.ssh/* or */.aws/*": 0.97,
 "egress to a host not on the allowlist": 0.90,
 "tool-call rate 20× its own baseline": 0.75,
 "activity outside usual hours": 0.30,
}
THRESHOLD = 0.70

def policy(signal, subject_is_human):
    conf = SIGNALS[signal]
    if subject_is_human:
        return f"page on-call (confidence {conf:.2f}) — human lockout needs a person"
    if conf >= THRESHOLD:
        return f"AUTO-REVOKE (confidence {conf:.2f}) — no approval in the path"
    return f"alert only (confidence {conf:.2f} < {THRESHOLD})"

for s in SIGNALS:
    print(f"{s:44s}{policy(s, False)}")
print()
print(f"{'same signal, human subject':44s}"
      f"{policy('reached the cloud metadata service', True)}")

auto_path = [("detection fires", 8), ("policy evaluates", 1), ("revocation executed", 12)]
auto_total = sum(s for _, s in auto_path)
print(f"\nautomated path: {auto_total}s vs manual {total}s "
      f"({total/auto_total:.0f}× faster)")
print(f"actions prevented at 300/min: {300*(total-auto_total)/60:,.0f}")
assert auto_total < total / 10

# Verify: model the cost of getting it wrong, which is what makes it safe.
def cost_of_false_revocation(subject_is_human, agent_can_rerequest=True):
    if subject_is_human:
        return {"impact": "person locked out mid-shift", "recovery": "helpdesk, 20-60 min",
                "cost": "high"}
    if agent_can_rerequest:
        return {"impact": "task fails, agent re-requests with a reason (A2.4)",
                "recovery": "seconds to minutes", "cost": "low"}
    return {"impact": "agent stops until an on-call re-enables it",
            "recovery": "minutes", "cost": "moderate"}

for label, human in (("human subject", True), ("non-human identity", False)):
    c = cost_of_false_revocation(human)
    print(f"{label:22s}{c['cost']:10s}{c['impact']}")
print("\nThat asymmetry is the entire justification for two different policies.")
