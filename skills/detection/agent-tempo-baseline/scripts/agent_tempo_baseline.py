#!/usr/bin/env python3
"""Measure the behavioural signals that separate an agent's tempo from a human's, and show what a rule tuned for human volume does to an agent.

This is the executable half of the `agent-tempo-baseline` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

def burst_rule(actions_per_hour, threshold=60):
    return actions_per_hour > threshold

RATE = {"Alex": 12, "workflow agent": 1400}
for who, n in RATE.items():
    print(f"   {who:16s}{n:>6} actions/hour -> "
          f"{'ALERT' if burst_rule(n) else 'silent'}")

seconds_to_trip = 60 * 3600 / RATE["workflow agent"]
print(f"\nthe agent crosses the threshold after {seconds_to_trip:.0f} seconds")
print(f"and keeps going for the remaining {3600 - seconds_to_trip:.0f}.")
print()
print("So the rule fires, about two and a half minutes into a sixty-minute run -")
print("by which point most of what the actor was going to do is done. If those")
print("were refunds, the alert arrives after the money has moved.")
print()
print("Chapter 8 is about detections that fire on shape rather than volume.")
print("Chapter 9 is about who can pull the stop lever without asking.")
assert burst_rule(1400) and not burst_rule(12) and seconds_to_trip < 200
