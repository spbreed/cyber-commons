#!/usr/bin/env python3
"""Run the impossible task against per-target, token and action ceilings and see which one halts it first.

This is the executable half of the `budget-and-stop-condition-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

class Budget:
    def __init__(self, tokens=50_000, seconds=60, actions=20, per_target=5):
        self.limits = {"tokens": tokens, "seconds": seconds,
                       "actions": actions, "per_target": per_target}
        self.used = {"tokens": 0, "seconds": 0, "actions": 0}
        self.targets = {}
    def spend(self, tokens=0, seconds=0, action=None, target=None):
        self.used["tokens"] += tokens
        self.used["seconds"] += seconds
        if action: self.used["actions"] += 1
        if target:
            self.targets[target] = self.targets.get(target, 0) + 1
            if self.targets[target] > self.limits["per_target"]:
                return False, f"per_target ({target})"
        for k in ("tokens", "seconds", "actions"):
            if self.used[k] > self.limits[k]:
                return False, k
        return True, None

def loop(budget):
    """A task that cannot succeed - A1.13's exact scenario, now bounded."""
    steps = 0
    while True:
        steps += 1
        ok, hit = budget.spend(tokens=1800, seconds=0.4, action="query",
                               target="reports-db")
        if not ok:
            return {"steps": steps, "stopped_by": hit, "complete": False}

b = Budget()
r = loop(b)
print(f"steps taken : {r['steps']}")
print(f"stopped by  : {r['stopped_by']}")
print(f"complete    : {r['complete']}   <- visible in the output, not silent")
print()
print(f"{'ceiling':14s}{'limit':>9}{'used':>9}")
for k in ("tokens", "seconds", "actions"):
    print(f"{k:14s}{b.limits[k]:>9}{round(b.used[k], 1):>9}")
print(f"{'per_target':14s}{b.limits['per_target']:>9}{b.targets['reports-db']:>9}")
print()
print("per_target fired first, at 6 calls - long before the token budget or the")
print("action budget. That is the ceiling that protects everyone else, and it is")
print("the one most budgets do not have.")
print()
print("`complete: False` is the other half. A run that stops silently and")
print("reports what it managed becomes A1.16 with extra steps.")
assert r["stopped_by"].startswith("per_target") and not r["complete"]
