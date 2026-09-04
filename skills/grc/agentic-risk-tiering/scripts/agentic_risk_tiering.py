#!/usr/bin/env python3
"""Tier a use case by autonomy, data and reach, and compare the answer against tiering by model.

This is the executable half of the `agentic-risk-tiering` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass

@dataclass
class AIAsset:
    name: str; kind: str; owner: str = ""; autonomy: str = "L1"
    data: tuple = (); external: bool = False; registered: bool = True

TIER_THRESHOLDS = [(9, "critical"), (6, "high"), (3, "medium"), (0, "low")]

def risk_tier(a):
    score, why = 0, []
    pts = {"L1": 0, "L2": 1, "L2.5": 3, "L3": 5}[a.autonomy]
    if pts: score += pts; why.append(f"autonomy {a.autonomy} (+{pts})")
    if "regulated" in a.data: score += 3; why.append("regulated data (+3)")
    if "customer" in a.data:  score += 2; why.append("customer data (+2)")
    if a.external:            score += 2; why.append("can act externally (+2)")
    if not a.registered:      score += 1; why.append("unregistered (+1)")
    tier = next(t for th, t in TIER_THRESHOLDS if score >= th)
    return {"tier": tier, "score": score, "because": why}

ASSETS = [
 AIAsset("frontier chatbot, public docs, read-only", "copilot", "x", "L1", ("public",)),
 AIAsset("small local model with prod deploy rights", "agent", "x", "L3",
         ("customer", "regulated"), True),
 AIAsset("mid model, gated writes, internal only", "agent", "x", "L2", ("employee",)),
 AIAsset("frontier model summarising customer tickets", "copilot", "x", "L1",
         ("customer",)),
 AIAsset("unregistered remediation agent", "agent", "", "L2.5", ("customer",),
         True, registered=False),
]
print(f"{'asset':46s}{'tier':10s}{'score':>6}")
print("-" * 66)
for a in ASSETS:
    t = risk_tier(a)
    print(f"{a.name:46s}{t['tier']:10s}{t['score']:>6}")
    for w in t["because"]:
        print(f"{'':46s}{w}")

MODEL_TIER = {   # the questionnaire that asks 'which model?' first
 "frontier chatbot, public docs, read-only": "high",
 "small local model with prod deploy rights": "low",
 "mid model, gated writes, internal only": "medium",
 "frontier model summarising customer tickets": "high",
 "unregistered remediation agent": "medium",
}
print(f"{'asset':46s}{'by model':10s}{'by authority':14s}agreement")
print("-" * 84)
disagreements = 0
for a in ASSETS:
    by_auth = risk_tier(a)["tier"]
    by_model = MODEL_TIER[a.name]
    agree = by_auth == by_model
    disagreements += not agree
    print(f"{a.name:46s}{by_model:10s}{by_auth:14s}{'' if agree else '← DISAGREE'}")
print(f"\n{disagreements}/{len(ASSETS)} disagree.")
print("The worst inversion: the small local model with deploy rights tiers LOW")
print("on model capability and CRITICAL on what it can actually do.")
assert risk_tier(ASSETS[1])["tier"] == "critical"
assert MODEL_TIER[ASSETS[1].name] == "low"

QUESTIONS = [
 ("What can it change without a human approving that specific action?",
  "autonomy — the largest term"),
 ("What data can it read, and is any of it regulated or customer data?",
  "consequence of a leak"),
 ("Can it act outside our boundary?",
  "reach"),
 ("Is it registered, with a named owner?",
  "governability — an unowned asset cannot be remediated"),
]
NOT_ASKED = [
 "Which model does it use?",
 "How many parameters?",
 "Is the vendor SOC 2 certified?",
]
print("ASK:")
for q, why in QUESTIONS: print(f"   {q}\n      → {why}")
print("\nDO NOT tier on:")
for q in NOT_ASKED: print(f"   {q}")
print("   (these matter for LIKELIHOOD and vendor risk — a separate, smaller term)")

def tier_from_answers(can_change, reads_regulated, reads_customer, external, registered):
    a = AIAsset("x", "agent", "o" if registered else "", can_change,
                tuple(filter(None, ("regulated" if reads_regulated else "",
                                    "customer" if reads_customer else ""))),
                external, registered)
    return risk_tier(a)["tier"]

print("\nworked example — a new request:")
print("   'an agent that can issue refunds up to £500, reads customer orders,'")
print("   'runs internally, owned by payments-eng'")
print("   tier:", tier_from_answers("L2.5", False, True, False, True))
