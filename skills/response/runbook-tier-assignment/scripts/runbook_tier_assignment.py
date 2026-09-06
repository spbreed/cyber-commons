#!/usr/bin/env python3
"""Run one incident's response at all three tiers and compare what each costs and risks.

This is the executable half of `runbook-tier-assignment`. The tiers are not
three levels of ambition. They are three different trades between time-to-contain
and the cost of being wrong, and the right one depends on how good the signal is.

Standard library only, and deterministic.
"""

# One incident, three ways. Times in seconds.
STEPS = [
    ("detect",            2,   2,    2),
    ("decide",            1, 240, 1800),      # automated / HITL / manual
    ("throttle agent",    3,   3,   60),
    ("revoke token",      3,   3,   90),
    ("confirm contained", 5,   5,  120),
]
TIERS = ["automated", "human-in-the-loop", "manual"]
# How often the signal is wrong, and what a wrong action costs at each tier.
FP_RATE = 0.08
WRONG_ACTION_COST = {"automated": 1.0, "human-in-the-loop": 0.15, "manual": 0.02}

print(f"{'step':<20}" + "".join(f"{t:>20}" for t in TIERS))
totals = [0, 0, 0]
for name, *secs in STEPS:
    print(f"{name:<20}" + "".join(f"{s:>18}s " for s in secs))
    totals = [a + b for a, b in zip(totals, secs)]
print(f"{'time to contain':<20}" + "".join(f"{t:>18}s " for t in totals))
print()

report = {"tiers": []}
print(f"{'tier':<20}{'contain':>10}{'reaches the estate wrongly / 100':>34}")
for tier, secs in zip(TIERS, totals):
    wrong = FP_RATE * 100 * WRONG_ACTION_COST[tier]
    print(f"{tier:<20}{secs:>9}s{wrong:>34.1f}")
    report["tiers"].append({"tier": tier, "seconds_to_contain": secs,
                            "wrong_actions_per_100": round(wrong, 1)})
print()
print("There is deliberately no third column ranking these. Seconds of exposure")
print("and wrongly-contained agents are not in the same unit, and any single")
print("score that ranks them has smuggled in an exchange rate somebody chose.")
print("Choose it openly, per incident class, or do not choose it at all.")
print()
print("The automated tier contains in a quarter of a minute and is wrong eight")
print("times in a hundred, with nobody between the mistake and the estate. The")
print("manual tier is wrong far less often and takes over half an hour, which on")
print("a 29-minute breakout time means containment lands after the attacker has")
print("finished. Neither is 'safe'. They fail differently.")
print()
print("This is why the tier comes from the remediation policy and not from the")
print("runbook author's confidence: the trade is a property of the ACTION, and")
print("the false-positive rate is a property of the DETECTION. Neither of them")
print("is a property of how bold the person writing the runbook was feeling.")

assert [t["tier"] for t in report["tiers"]] == TIERS
assert report["tiers"][0]["seconds_to_contain"] < report["tiers"][2]["seconds_to_contain"]
assert report["tiers"][0]["wrong_actions_per_100"] > report["tiers"][2]["wrong_actions_per_100"]
assert not any("residual" in t for t in report["tiers"]), \
    "no single score may rank tiers whose costs are in different units"
