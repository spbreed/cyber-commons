#!/usr/bin/env python3
"""Simulate a programme order against its prerequisites and find the steps that block on something not yet done.

This is the executable half of the `programme-sequencing` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

STEPS = {
 1: ("inventory",   [],     ["you can now tier and assign owners"]),
 2: ("identity",    [1],    ["per-agent revocation", "attribution in logs"]),
 3: ("containment", [1],    ["bounded blast radius", "a red team has something to test"]),
 4: ("evidence",    [2],    ["act chains", "replayable runs", "a drift baseline"]),
 5: ("evaluation",  [4],    ["accuracy you can defend", "regression cases"]),
 6: ("continuous",  [4,5],  ["freshness windows", "drift alerts", "live posture"]),
}
print(f"{'step':>5}  {'name':14s}{'needs':10s}unlocks")
print("-" * 84)
for n, (name, needs, unlocks) in STEPS.items():
    print(f"{n:>5}  {name:14s}{str(needs):10s}{'; '.join(unlocks)}")

def can_do(step, done):
    return all(d in done for d in STEPS[step][1])

print("\nwhat is doable from a standing start:")
print("   ", [n for n in STEPS if can_do(n, set())])

def simulate(order):
    done, blocked, timeline = set(), [], []
    for step in order:
        if can_do(step, done):
            done.add(step); timeline.append((step, STEPS[step][0], "done"))
        else:
            missing = [STEPS[d][0] for d in STEPS[step][1] if d not in done]
            blocked.append((step, STEPS[step][0], missing))
            timeline.append((step, STEPS[step][0], f"BLOCKED on {missing}"))
    return done, blocked, timeline

POPULAR = [5, 6, 1, 3, 2, 4]     # evaluation and dashboards first
CORRECT = [1, 2, 3, 4, 5, 6]

for label, order in (("popular order", POPULAR), ("correct order", CORRECT)):
    done, blocked, timeline = simulate(order)
    print(f"=== {label} ===")
    for step, name, state in timeline:
        print(f"   {step}. {name:14s}{state}")
    print(f"   completed {len(done)}/6, blocked {len(blocked)}\n")

done_pop, blocked_pop, _ = simulate(POPULAR)
print(f"popular order completes {len(done_pop)}/6 on the first pass;")
print(f"{len(blocked_pop)} step(s) have to be redone after their prerequisites land.")
assert len(blocked_pop) > 0

CAPABILITY = {
 1: "can list every AI asset with an owner",
 2: "can revoke one agent without stopping the others",
 3: "can bound what a compromised agent reaches",
 4: "can say who caused a specific action, and replay it",
 5: "can defend an accuracy number to a supervisor",
 6: "can say what is TRUE TODAY, not what passed once",
}
def programme_state(done):
    return [(n, CAPABILITY[n], n in done) for n in STEPS]

for label, order in (("eval-first, one quarter in", POPULAR[:2]),
                     ("correct order, one quarter in", CORRECT[:3])):
    done, _, _ = simulate(order)
    print(f"=== {label} — {len(done)} capabilit(y/ies) ===")
    for n, cap, have in programme_state(done):
        print(f"   {'YES' if have else 'no ':4s} {cap}")
    print()

done_a, _, _ = simulate(POPULAR[:2])
done_b, _, _ = simulate(CORRECT[:3])
print(f"after equal effort: eval-first has {len(done_a)} capabilities, "
      f"correct order has {len(done_b)}")
print("\nThe eval-first programme can produce a dashboard. It cannot switch")
print("anything off, and it cannot say who did what.")
assert len(done_b) > len(done_a)
