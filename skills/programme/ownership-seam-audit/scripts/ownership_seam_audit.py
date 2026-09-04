#!/usr/bin/env python3
"""Find the decisions with no named owner and measure what they cost during a simulated incident.

This is the executable half of the `ownership-seam-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SEAMS = [
 ("AppSec", "Platform",     "who owns the agent's sandbox?",              "A3.1"),
 ("Identity", "SecOps",     "who revokes a non-human identity at 03:00?", "A3.6"),
 ("GRC", "Engineering",     "who decides an autonomy rung?",              "E3.2"),
 ("SOC", "Data",            "who retains agent traces, and for how long?","D1.5"),
 ("CISO office", "Legal",   "who starts the regulatory clock?",           "E2.6"),
 ("AppSec", "SOC",          "who owns detections FOR agents?",            "D1.4"),
]
ANSWERS = {
 "who owns the agent's sandbox?": "platform-security",
 "who revokes a non-human identity at 03:00?": "on-call SRE, pre-authorised",
 "who decides an autonomy rung?": "",                    # unanswered
 "who retains agent traces, and for how long?": "",      # unanswered
 "who starts the regulatory clock?": "legal, on IR notification",
 "who owns detections FOR agents?": "detection engineering",
}
print(f"{'seam':28s}{'owner':32s}lesson")
print("-" * 78)
unanswered = []
for a, b, q, lesson in SEAMS:
    owner = ANSWERS.get(q, "")
    if not owner: unanswered.append(q)
    print(f"{a + ' ↔ ' + b:28s}{owner or '⚠ NOBODY':32s}{lesson}")
print(f"\n{len(unanswered)}/{len(SEAMS)} seams have no named owner:")
for q in unanswered: print(f"   {q}")
assert unanswered

INCIDENT = [
 ("detection fires",                     "SOC",              True,  0.2),
 ("agent identified as the actor",       "SOC",              True,  1.0),
 ("decision to revoke the identity",     "Identity ↔ SecOps",True,  0.3),
 ("decide trace retention for evidence", "SOC ↔ Data",       False, 14.0),
 ("re-tier the agent post-incident",     "GRC ↔ Engineering",False, 21.0),
]
print(f"{'step':38s}{'seam':20s}{'owned':>7}{'hours':>8}")
print("-" * 76)
total = 0
for step, seam, owned, hours in INCIDENT:
    total += hours
    flag = "" if owned else "   ← stalls"
    print(f"{step:38s}{seam:20s}{str(owned):>7}{hours:>8}{flag}")
print(f"\ntotal elapsed: {total:.1f} hours")
owned_only = sum(h for _, _, o, h in INCIDENT if o)
print(f"if every seam were owned: {owned_only:.1f} hours "
      f"({total/owned_only:.0f}× faster)")
print("\nThe two unowned steps account for "
      f"{(total-owned_only)/total:.0%} of the elapsed time, and both are")
print("decisions rather than work.")
assert total > owned_only * 5
