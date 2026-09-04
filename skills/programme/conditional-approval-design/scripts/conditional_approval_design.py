#!/usr/bin/env python3
"""Tier a request, show what a flat refusal costs, and write the conditions that make a yes safe and testable.

This is the executable half of the `conditional-approval-design` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n,s,rev in tools if n not in gated)

REQUEST = {
 "name": "customer-refund-agent",
 "asks_for": "issue refunds up to GBP 500 without human approval",
 "tools": [("read_order","self",True), ("read_customer","self",True),
           ("issue_refund","tenant",False)],
 "rung": "L2.5",
 "data": ("customer","regulated"),
 "business_case": "42% of refund tickets are mechanical; 3.5 FTE of manual work",
}
b = blast(REQUEST["tools"])
print(f"request        {REQUEST['name']}")
print(f"asks for       {REQUEST['asks_for']}")
print(f"business case  {REQUEST['business_case']}")
print(f"claimed rung   {REQUEST['rung']}")
print(f"blast radius   {b}  (irreversible, tenant-wide)")

TIER_PTS = {"L1":0,"L2":1,"L2.5":3,"L3":5}
score = TIER_PTS[REQUEST["rung"]] + 3*("regulated" in REQUEST["data"]) + \
        2*("customer" in REQUEST["data"])
tier = "critical" if score >= 9 else "high" if score >= 6 else "medium"
print(f"risk tier      {tier} (score {score})")

def flat_no_outcome(request):
    return {
      "decision": "refused",
      "what happens": "the team ships it as a 'workflow automation' outside the "
                      "AI register",
      "your visibility": "none — it will not appear in the inventory (E1.2)",
      "controls applied": "whatever the team chose",
      "when you find out": "at the first incident, or at audit",
    }
for k, v in flat_no_outcome(REQUEST).items():
    print(f"{k:20s}{v}")
print("\nThe capability ships either way. The only variable is whether you")
print("have visibility and conditions on it.")

CONDITIONS = [
 ("refund cap of GBP 500 enforced in the tool, not the prompt",
  "the irreversible step is bounded by code", "payments-eng", "SB-2", "2026-09-30"),
 ("approval gate above the cap",
  "L2 for the tail, L2.5 for the body", "payments-eng", "SB-2", "2026-09-30"),
 ("act chain on every refund",
  "attribution survives an incident (D2.1)", "platform-sec", "AC-1/EV-1", "2026-09-15"),
 ("tested stop, measured in seconds",
  "you can halt it without the vendor", "SRE", "ST-1", "2026-10-12"),
 ("re-tier automatically if the tool list changes",
  "A1.1 manifest diff wired into CI", "platform-sec", "DR-1", "2026-10-31"),
]
print(f"{'condition':52s}{'owner':16s}{'control':10s}{'by':>12}")
print("-" * 94)
for cond, why, owner, control, date in CONDITIONS:
    print(f"{cond:52s}{owner:16s}{control:10s}{date:>12}")
    print(f"   why: {why}")

def testable(cond):
    """A condition is testable if a control produces evidence for it."""
    return bool(cond[3])
print(f"\nall conditions testable: {all(testable(c) for c in CONDITIONS)}")
print(f"count: {len(CONDITIONS)} — few enough to be met rather than negotiated")
assert len(CONDITIONS) <= 6 and all(testable(c) for c in CONDITIONS)

# Verify: the conditions actually change the risk, not just the paperwork.
gated = {"issue_refund"}
before, after = blast(REQUEST["tools"]), blast(REQUEST["tools"], gated)
print(f"blast radius   {before} → {after} with the cap and gate applied")

def residual(tier, conditions_met):
    reduction = 0.18 * conditions_met
    base = {"critical": 1.0, "high": 0.7, "medium": 0.4}[tier]
    return round(max(base - reduction, 0.05), 2)

print(f"\n{'conditions met':>16}{'residual risk':>16}")
print("-" * 34)
for n in range(len(CONDITIONS) + 1):
    print(f"{n:>16}{residual(tier, n):>16.2f}")

print(f"\nyes, with {len(CONDITIONS)} conditions → residual "
      f"{residual(tier, len(CONDITIONS)):.2f} from {residual(tier, 0):.2f}")
print("\nAnd the sentence that makes it a decision rather than a demand:")
print("   'If any condition slips its date, the agent drops to L2 — every refund")
print("    needs approval — until it is met. That is automatic, not a negotiation.'")
assert after < before
