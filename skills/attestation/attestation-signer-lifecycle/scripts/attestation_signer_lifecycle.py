#!/usr/bin/env python3
"""Read the same evidence as a point-in-time test and as a continuous one, and derive a freshness window per control from observed drift.

This is the executable half of the `attestation-signer-lifecycle` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
from dataclasses import dataclass, field

now = time.time(); DAY = 86400

@dataclass
class ControlTest:
    cid: str
    passed: bool
    evidence: str
    tested_at: float
    valid_for_days: float = 30

    def age_days(self, at): return (at - self.tested_at) / DAY
    def point_in_time(self, at): return "PASS" if self.passed else "FAIL"
    def continuous(self, at):
        if self.age_days(at) > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

TESTS = [
 ControlTest("AC-1", True,  "act chain sampled from gateway logs", now -   3*DAY),
 ControlTest("AC-2", True,  "delegation refusal regression suite", now -   9*DAY),
 ControlTest("SB-1", True,  "egress denial evidence",              now -  45*DAY),
 ControlTest("SB-2", True,  "approval gate screenshot",            now - 210*DAY),
 ControlTest("EV-1", True,  "audit sample of 50 agent actions",    now -   5*DAY),
 ControlTest("DR-1", False, "drift alerting not deployed",         now),
]
REQUIRED = ["AC-1", "AC-2", "SB-1", "SB-2", "EV-1", "DR-1", "EV-2", "ST-1"]

print(f"{'control':9s}{'age (days)':>12}{'point-in-time':>16}{'continuous':>13}")
print("-" * 52)
by_id = {t.cid: t for t in TESTS}
for cid in REQUIRED:
    t = by_id.get(cid)
    if t is None:
        print(f"{cid:9s}{'—':>12}{'(not tested)':>16}{'NO EVIDENCE':>13}")
        continue
    print(f"{cid:9s}{t.age_days(now):>12.0f}{t.point_in_time(now):>16}{t.continuous(now):>13}")

def posture(tests, required, at, mode):
    by_id = {t.cid: t for t in tests}
    passing = 0
    for cid in required:
        t = by_id.get(cid)
        if t is None: continue
        state = t.point_in_time(at) if mode == "point-in-time" else t.continuous(at)
        passing += state == "PASS"
    return passing, round(passing/len(required), 3)

for mode in ("point-in-time", "continuous"):
    n, pct = posture(TESTS, REQUIRED, now, mode)
    print(f"{mode:16s} {n}/{len(REQUIRED)} controls passing = {pct:.0%}")

print("\nThe difference is entirely SB-1 and SB-2, which nobody did anything")
print("wrong to. Time simply passed, and the agent they were tested against")
print("has had two model upgrades since.")

DRIFT_RATE = {          # observed TVD/day for what each control depends on
 "AC-1": 0.0005,        # identity model changes slowly
 "AC-2": 0.0005,
 "SB-1": 0.0020,        # egress needs change with new integrations
 "SB-2": 0.0090,        # tool manifests change weekly
 "EV-1": 0.0010,
 "DR-1": 0.0090,
}
TOLERANCE = 0.25

def window(cid):
    r = DRIFT_RATE.get(cid)
    return int(TOLERANCE / r) if r else 90

print(f"{'control':9s}{'drift/day':>12}{'window (days)':>15}{'current age':>13}{'state':>9}")
print("-" * 60)
for cid in REQUIRED:
    t = by_id.get(cid)
    w = window(cid)
    if t is None:
        print(f"{cid:9s}{'—':>12}{w:>15}{'—':>13}{'NO EVIDENCE':>9}")
        continue
    t.valid_for_days = w
    print(f"{cid:9s}{DRIFT_RATE.get(cid, 0):>12.4f}{w:>15}{t.age_days(now):>13.0f}"
          f"{t.continuous(now):>9}")

n, pct = posture(TESTS, REQUIRED, now, "continuous")
print(f"\nwith drift-derived windows: {n}/{len(REQUIRED)} = {pct:.0%} currently evidenced")
assert pct < 0.6
print("\nSB-2 tests a tool manifest that changes weekly; a 210-day-old screenshot")
print("cannot evidence it. Saying so is the control, not a criticism of anyone.")
