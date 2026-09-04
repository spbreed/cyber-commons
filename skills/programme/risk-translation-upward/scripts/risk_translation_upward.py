#!/usr/bin/env python3
"""Compute fleet exposure, containment ASR and control coverage, and translate them into a board statement rather than a findings list.

This is the executable half of the `risk-translation-upward` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}

FLEET = {
 "pr-remediation-agent": [("read_file","self",True),
                          ("write_file","project",True),
                          ("deploy","org",False)],
 "claims-triage-agent":  [("read_file","self",True),
                          ("issue_refund","tenant",False)],
 "doc-summariser":       [("read_file","self",True)],
}
GATED = {"pr-remediation-agent": set(), "claims-triage-agent": {"issue_refund"},
         "doc-summariser": set()}

def blast(tools, gated):
    return sum(SCOPE_WEIGHT[s] * (1 if rev else 2)
               for n, s, rev in tools if n not in gated)

exposure = {a: blast(t, GATED[a]) for a, t in FLEET.items()}
print(f"{'agent':24s}{'blast radius':>14}")
print("-" * 40)
for a, b in sorted(exposure.items(), key=lambda kv: -kv[1]):
    print(f"{a:24s}{b:>14}")
total_exposure = sum(exposure.values())
print(f"{'FLEET TOTAL':24s}{total_exposure:>14}")

# likelihood — measured, from C1.2
ATTACKS = [("metadata service", False), ("path traversal", False),
           ("unlisted egress", True), ("denied tool", False)]
asr = sum(1 for _, through in ATTACKS if through) / len(ATTACKS)
print(f"\nred-team attack success rate (containment surface): {asr:.0%}")

# assurance — from E1.7
REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]
EVIDENCED = ["AC-1","AC-2","EV-1","EV-2"]
coverage = len(EVIDENCED) / len(REQUIRED)
print(f"controls currently evidenced: {len(EVIDENCED)}/{len(REQUIRED)} = {coverage:.0%}")

FINDINGS_UPDATE = """
This quarter the team identified prompt injection in the code review agent,
insufficient scope narrowing in the delegation chain, and gaps in our egress
allowlist. We ran garak and promptfoo against three agents and found a 25%
attack success rate on the containment surface. We recommend prioritising
provenance controls and completing the SPIFFE rollout.
"""
print(FINDINGS_UPDATE)
print("Problems with this, from the audience's side:")
for p in ["no exposure figure — how much can actually happen?",
          "'25% attack success rate' against what, and is that good or bad?",
          "four tool names nobody in the room can evaluate",
          "'recommend prioritising' is not a decision anyone can take",
          "no option to decline, so it reads as lobbying rather than a choice"]:
    print(f"   · {p}")

def board_translation(tier, exposure, asr, coverage, ask, cost, owner):
    likelihood = ("demonstrated" if asr > 0.2 else
                  "reduced but not eliminated" if asr > 0 else "not demonstrated")
    return f"""
EXPOSURE     A {tier}-tier system can take {exposure} units of unreviewed action.
             (One unit ≈ one irreversible change inside one project.)

LIKELIHOOD   We attacked it. {asr:.0%} of our attack suite succeeded — {likelihood}.
             This is a measurement, not an assessment.

ASSURANCE    {coverage:.0%} of the controls we say we operate are currently
             evidenced. The remainder are untested or their evidence has expired.

DECISION     {ask}
             Cost: {cost}.
             The alternative is to accept the unevidenced portion in writing,
             owned by {owner}, with a review date. Both are acceptable outcomes;
             we need one of them recorded."""

print(board_translation(
    tier="critical", exposure=total_exposure, asr=asr, coverage=coverage,
    ask="Fund continuous control verification for the agent fleet.",
    cost="0.5 FTE for two quarters, no new licences",
    owner="the Chief Operating Officer"))

# Verify: the translation must contain no mechanism and must offer a choice.
JARGON = ["prompt injection", "spiffe", "garak", "promptfoo", "cwe",
          "provenance", "allowlist", "delegation chain", "token exchange"]
text = board_translation("critical", total_exposure, asr, coverage,
                         "Fund continuous control verification.", "0.5 FTE", "the COO")
found = [j for j in JARGON if j in text.lower()]
print(f"mechanism terms present: {found or 'none'}")
has_choice = "alternative" in text.lower() and "accept" in text.lower()
has_number = str(total_exposure) in text and f"{asr:.0%}" in text
print(f"offers a genuine alternative : {has_choice}")
print(f"carries measured numbers     : {has_number}")
assert not found and has_choice and has_number
print("\nFour facts, no mechanism, and a decision that can go either way.")
