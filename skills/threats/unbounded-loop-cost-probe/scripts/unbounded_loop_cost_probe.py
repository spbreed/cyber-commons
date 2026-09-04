#!/usr/bin/env python3
"""Run an agent at an impossible task and measure what it spends, and who else pays for it.

This is the executable half of the `unbounded-loop-cost-probe` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

DOWNSTREAM = {"calls": 0, "capacity": 50, "rejected": 0}

def flaky_api(query):
    """A downstream service. It is not broken - the query cannot be satisfied."""
    DOWNSTREAM["calls"] += 1
    if DOWNSTREAM["calls"] > DOWNSTREAM["capacity"]:
        DOWNSTREAM["rejected"] += 1
        return {"error": "capacity exceeded"}
    return {"result": None}                     # no match, ever

def agent_loop(task, max_steps=None):
    """plan -> act -> observe -> decide again. Stops when it succeeds."""
    steps, tokens = 0, 0
    while True:
        steps += 1
        tokens += 1800
        result = flaky_api(task)
        if result.get("result"):
            return {"done": True, "steps": steps, "tokens": tokens}
        if max_steps and steps >= max_steps:
            return {"done": False, "steps": steps, "tokens": tokens, "stopped_by": "budget"}
        if steps > 500:                          # the notebook's own safety net
            return {"done": False, "steps": steps, "tokens": tokens, "stopped_by": "runaway"}

r = agent_loop("find the order for customer 99999")     # this order does not exist
print(f"steps taken           : {r['steps']}")
print(f"tokens spent          : {r['tokens']:,}  (about ${r['tokens']/1000*0.002:,.2f})")
print(f"downstream calls      : {DOWNSTREAM['calls']}")
print(f"downstream rejections : {DOWNSTREAM['rejected']}  <- other callers got these")
print(f"stopped by            : {r['stopped_by']}")
print()
print("The agent was not attacked and nothing malfunctioned. It was given a")
print("task that cannot succeed, and the loop did what loops do.")
print()
print(f"{DOWNSTREAM['rejected']} rejections went to whoever else was using that")
print("service - a denial of service launched from inside the perimeter, by")
print("something holding valid credentials.")
assert DOWNSTREAM["rejected"] > 0
