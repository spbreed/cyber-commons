#!/usr/bin/env python3
"""Approve or refuse an autonomy request against the rung its blast radius and gating actually support.

This is the executable half of the `autonomy-ladder-decisions` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}
LADDER = {
 "L1":  "Assist — model proposes, a human performs every action.",
 "L2":  "Act with approval — model calls tools, a human approves each call.",
 "L2.5":"Act within a blast radius — pre-approved tools, bounded scope, review after.",
 "L3":  "Autonomous — model acts and self-verifies; humans see aggregates.",
}
POLICY = {
 "L1":   ("self-service", "register it; no further review", 0),
 "L2":   ("lightweight",  "named owner + approval gate on every writer", 0),
 "L2.5": ("governed",     "risk tier + blast budget + drift monitoring + tested stop", 20),
 "L3":   ("board",        "all of L2.5 + held-out eval per release + board sign-off", 60),
}
for rung, desc in LADDER.items():
    kind, req, budget = POLICY[rung]
    print(f"{rung:5s}{kind:14s}budget {budget:>3}  {req}")
    print(f"{'':19s}{desc}")

def blast(tools, gated):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n,s,rev in tools if n not in gated)

def evaluate_request(name, tools, gated, claimed_rung):
    b = blast(tools, gated)
    kind, req, budget = POLICY[claimed_rung]
    problems = []
    writers = [n for n,s,rev in tools if s != "self" or not rev]
    ungated = [n for n in writers if n not in gated]
    if claimed_rung == "L1" and writers:
        problems.append(f"claims L1 but holds state-changing tools: {writers}")
    if claimed_rung == "L2" and ungated:
        problems.append(f"claims L2 (approve every call) but ungated: {ungated}")
    if b > budget:
        problems.append(f"blast radius {b} exceeds the {claimed_rung} budget of {budget}")
    return {"agent": name, "rung": claimed_rung, "blast": b,
            "decision": "APPROVE" if not problems else "REFUSE or RE-TIER",
            "problems": problems, "governance": req}

REQUESTS = [
 ("doc-summariser", [("read_file","self",True)], set(), "L1"),
 ("triage-bot", [("read_file","self",True), ("post_comment","project",True),
                 ("close_ticket","project",True)], set(), "L2"),
 ("refund-agent", [("read_file","self",True),
                   ("issue_refund","tenant",False)], set(), "L2.5"),
 ("refund-agent (gated)", [("read_file","self",True),
                           ("issue_refund","tenant",False)], {"issue_refund"}, "L2.5"),
]
for name, tools, gated, rung in REQUESTS:
    r = evaluate_request(name, tools, gated, rung)
    print(f"{r['agent']:24s}{r['rung']:6s}blast {r['blast']:>3}  {r['decision']}")
    for p in r["problems"]: print(f"{'':30s}⚠ {p}")

import math
def tool_approval_load(n_agents, tools_per_agent, new_tools_per_month,
                       minutes_per_review=25):
    initial = n_agents * tools_per_agent
    monthly = n_agents * new_tools_per_month
    return {"initial_reviews": initial,
            "initial_hours": round(initial * minutes_per_review / 60, 1),
            "monthly_reviews": monthly,
            "monthly_hours": round(monthly * minutes_per_review / 60, 1)}

print(f"{'agents':>8}{'initial reviews':>18}{'hours':>8}{'monthly reviews':>18}{'hours':>8}")
print("-" * 62)
for n in (5, 25, 120):
    r = tool_approval_load(n, tools_per_agent=8, new_tools_per_month=2)
    print(f"{n:>8}{r['initial_reviews']:>18}{r['initial_hours']:>8}"
          f"{r['monthly_reviews']:>18}{r['monthly_hours']:>8}")

def rung_load(n_agents, re_tier_per_month=0.1, minutes=25):
    monthly = n_agents * re_tier_per_month
    return round(monthly * minutes / 60, 1)
print(f"\nsame estates, governing by rung (re-tier only on a manifest change):")
for n in (5, 25, 120):
    print(f"   {n:>4} agents → {rung_load(n)} hours/month")
print("\nTool approval scales with agents × tools. Rung governance scales with")
print("agents × rate of significant change, which is two orders of magnitude less.")

def registration_rate(l1_requires_approval, friction_hours):
    """People register when it is cheaper than not registering."""
    base = 0.95
    penalty = min(friction_hours * 0.35, 0.9)
    return round(base - (penalty if l1_requires_approval else 0.0), 2)

print(f"{'L1 policy':34s}{'friction (h)':>14}{'registration rate':>20}")
print("-" * 70)
for label, approval, hours in (("self-service (register only)", False, 0.1),
                               ("approval required, fast", True, 1.0),
                               ("approval required, committee", True, 40.0)):
    rate = registration_rate(approval, hours)
    print(f"{label:34s}{hours:>14}{rate:>20.0%}")

def inventory_completeness(rate, n_true_assets=120):
    known = int(n_true_assets * rate)
    return {"true_assets": n_true_assets, "registered": known,
            "shadow": n_true_assets - known}

for label, approval, hours in (("self-service", False, 0.1),
                               ("committee", True, 40.0)):
    inv = inventory_completeness(registration_rate(approval, hours))
    print(f"\n{label}: {inv['registered']}/{inv['true_assets']} registered, "
          f"{inv['shadow']} shadow assets")
print("\nEvery control in E1 depends on the inventory. Charging for L1")
print("registration destroys the input to the entire governance programme.")
assert inventory_completeness(registration_rate(True, 40.0))["shadow"] > \
       inventory_completeness(registration_rate(False, 0.1))["shadow"]
