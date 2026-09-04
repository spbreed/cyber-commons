#!/usr/bin/env python3
"""Compute a control posture honestly, then automate one test and watch coverage move.

This is the executable half of the `aws-runtime-posture-collector` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
from dataclasses import dataclass

now = time.time(); DAY = 86400

@dataclass
class ControlTest:
    cid: str; passed: bool; evidence: str
    tested_at: float; valid_for_days: float
    def age(self, at): return (at - self.tested_at)/DAY
    def state(self, at):
        if self.age(at) > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]
TESTS = [
 ControlTest("AC-1", True,  "act chain sample",        now -   2*DAY, 30),
 ControlTest("AC-2", True,  "delegation regression",   now -   9*DAY, 30),
 ControlTest("SB-1", True,  "egress denial log",       now -  31*DAY, 30),
 ControlTest("SB-2", True,  "approval gate screenshot",now - 120*DAY, 27),
 ControlTest("EV-1", True,  "audit sample of 50",      now -   5*DAY, 60),
 ControlTest("EV-2", True,  "expert accuracy 0.81",    now -  12*DAY, 30),
 ControlTest("DR-1", False, "drift alerting not deployed", now,       30),
]

def verify(tests, required, at):
    by = {t.cid: t for t in tests}
    rows, evidenced = [], 0
    for cid in required:
        t = by.get(cid)
        if t is None:
            rows.append({"control": cid, "state": "NO EVIDENCE", "age": None})
            continue
        st = t.state(at)
        rows.append({"control": cid, "state": st, "age": round(t.age(at), 1)})
        evidenced += st == "PASS"
    return {"required": len(required), "evidenced": evidenced,
            "coverage": round(evidenced/len(required), 3), "rows": rows}

v = verify(TESTS, REQUIRED, now)
print(f"{'control':9s}{'state':14s}{'age (days)':>12}")
print("-" * 36)
for r in v["rows"]:
    print(f"{r['control']:9s}{r['state']:14s}{str(r['age']):>12}")
print(f"\ncurrently evidenced {v['evidenced']}/{v['required']} = {v['coverage']:.0%}")

point_in_time = sum(1 for t in TESTS if t.passed)
print(f"point-in-time  : {point_in_time}/{len(REQUIRED)} = "
      f"{point_in_time/len(REQUIRED):.0%}")
print(f"continuous     : {v['evidenced']}/{v['required']} = {v['coverage']:.0%}")
stale = [r["control"] for r in v["rows"] if r["state"] == "STALE"]
none  = [r["control"] for r in v["rows"] if r["state"] == "NO EVIDENCE"]
fail  = [r["control"] for r in v["rows"] if r["state"] == "FAIL"]
print(f"\nthe gap: STALE {stale}  NO EVIDENCE {none}  FAIL {fail}")
print("Nobody did anything wrong to produce the STALE rows. Time passed.")

def automated_test(cid, run_now):
    """A control test that re-runs on a schedule writes its own evidence."""
    passed, evidence = run_now()
    return ControlTest(cid, passed, evidence, tested_at=time.time(),
                       valid_for_days=30)

def check_egress_policy():
    ALLOW = {"api.github.com"}
    attempts = ["https://api.github.com/x", "http://169.254.169.254/",
                "https://collect.example.com/x"]
    from urllib.parse import urlparse
    denied = [u for u in attempts if (urlparse(u).hostname or "") not in ALLOW]
    return len(denied) == 2, f"{len(denied)}/3 destinations denied, run automatically"

fresh = [t for t in TESTS if t.cid != "SB-1"] + [automated_test("SB-1", check_egress_policy)]
v2 = verify(fresh, REQUIRED, now)
print(f"after automating SB-1: {v2['evidenced']}/{v2['required']} = {v2['coverage']:.0%}")
print(f"   SB-1 is now {[r['state'] for r in v2['rows'] if r['control']=='SB-1'][0]}"
      f" and will stay fresh without anyone remembering")
assert v2["coverage"] > v["coverage"]

print("\nprioritise automation by how often a control goes stale:")
for t in sorted(TESTS, key=lambda t: t.valid_for_days):
    per_year = round(365 / t.valid_for_days, 1)
    print(f"   {t.cid}  window {t.valid_for_days:>3.0f}d → "
          f"{per_year:>4} manual re-tests per year")
