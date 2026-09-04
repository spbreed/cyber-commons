#!/usr/bin/env python3
"""Track drift from a signed-off baseline across a quarter and count the change surfaces that bypass change management.

This is the executable half of the `behavioural-drift-monitor` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
from dataclasses import dataclass, field

now = time.time(); DAY = 86400

@dataclass
class Baseline:
    signed_off: float
    tool_mix: dict
    def compare(self, mix):
        total = sum(mix.values()) or 1
        cur = {k: v/total for k, v in mix.items()}
        keys = set(cur) | set(self.tool_mix)
        tvd = sum(abs(cur.get(k,0) - self.tool_mix.get(k,0)) for k in keys)/2
        return {"drift": round(tvd, 3),
                "new_tools": sorted(set(cur) - set(self.tool_mix)),
                "gone": sorted(set(self.tool_mix) - set(cur))}

base = Baseline(signed_off=now - 90*DAY,
                tool_mix={"read_file": 0.80, "search": 0.15, "write_file": 0.05})

TIMELINE = [
 (now - 90*DAY, "control signed off",     {"read_file": 800, "search": 150, "write_file": 50}),
 (now - 60*DAY, "prompt edited",          {"read_file": 700, "search": 150, "write_file": 150}),
 (now - 30*DAY, "tool added (no PR)",     {"read_file": 500, "search": 120, "write_file": 180,
                                           "run_shell": 200}),
 (now -  5*DAY, "model upgraded by vendor",{"read_file": 300, "search": 100, "write_file": 250,
                                            "run_shell": 350}),
]
print(f"{'when':>8}  {'event':26s}{'drift':>7}  new tools")
print("-" * 66)
for ts, event, mix in TIMELINE:
    d = base.compare(mix)
    print(f"{(now-ts)/DAY:>6.0f}d  {event:26s}{d['drift']:>7.3f}  {d['new_tools']}")

def drift_rate(baseline, timeline):
    """How fast does this agent actually drift? Set the window from the answer."""
    pts = [(ts, baseline.compare(mix)["drift"]) for ts, _, mix in timeline]
    pts.sort()
    span_days = (pts[-1][0] - pts[0][0]) / 86400
    return (pts[-1][1] - pts[0][1]) / max(span_days, 1)

rate = drift_rate(base, TIMELINE)
TOLERANCE = 0.25
window = int(TOLERANCE / rate) if rate > 0 else 365
print(f"observed drift rate  {rate:.5f} TVD/day")
print(f"tolerance            {TOLERANCE}")
print(f"→ freshness window   {window} days "
      f"(a control test older than this is unevidenced, not passing)")

@dataclass
class ControlTest:
    cid: str; passed: bool; tested_at: float; valid_for_days: float
    def state(self, at):
        age = (at - self.tested_at) / 86400
        if age > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

tests = [ControlTest("SB-1", True, now - 90*DAY, window),
         ControlTest("SB-2", True, now - 10*DAY, window),
         ControlTest("DR-1", False, now, window)]
print(f"\n{'control':10s}{'age (d)':>9}{'state':>10}")
print("-" * 30)
for t in tests:
    print(f"{t.cid:10s}{(now-t.tested_at)/DAY:>9.0f}{t.state(now):>10}")
evidenced = sum(t.state(now) == "PASS" for t in tests)
print(f"\ncurrently evidenced: {evidenced}/{len(tests)}")
assert any(t.state(now) == "STALE" for t in tests)
