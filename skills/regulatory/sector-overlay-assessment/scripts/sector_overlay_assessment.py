#!/usr/bin/env python3
"""Find the pre-existing sector clauses that already apply to an AI system without mentioning AI, and assess provider exit.

This is the executable half of the `sector-overlay-assessment` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

OVERLAYS = {
 "DORA (financial)": [
   ("ICT third-party risk", "your model provider is an ICT third party",
    lambda s: s["uses_external_model"]),
   ("exit strategy", "can you stop using this provider and keep operating?",
    lambda s: s["uses_external_model"]),
   ("resilience testing", "your stop mechanism is in scope for testing",
    lambda s: s["autonomy"] in ("L2.5", "L3")),
   ("incident reporting", "clocks measured in hours",
    lambda s: True)],
 "HIPAA (health)": [
   ("minimum necessary", "the context window is a disclosure",
    lambda s: "health" in s["data"]),
   ("audit controls", "the ACTING identity must be recorded",
    lambda s: True)],
 "PCI DSS (cards)": [
   ("scope containment", "an agent with CDE access expands the CDE",
    lambda s: "cardholder" in s["data"]),
   ("access control", "non-human identities need the same rigour",
    lambda s: True)],
}
SYSTEM = {"name": "claims-triage-agent", "uses_external_model": True,
          "autonomy": "L2.5", "data": ("customer", "health")}

print(f"{SYSTEM['name']}: autonomy {SYSTEM['autonomy']}, data {list(SYSTEM['data'])}, "
      f"external model {SYSTEM['uses_external_model']}\n")
hits = []
for fw, clauses in OVERLAYS.items():
    applicable = [(c, why) for c, why, test in clauses if test(SYSTEM)]
    if not applicable: continue
    print(f"{fw}")
    for c, why in applicable:
        hits.append((fw, c)); print(f"   {c:24s}{why}")
    print()
print(f"{len(hits)} pre-existing clauses apply. None of them mentions AI.")

PROVIDERS = {
 "hosted frontier API": {"can_pin_version": False, "can_export_weights": False,
                         "equivalent_alternative": True, "switching_days": 45},
 "hosted open-weight API": {"can_pin_version": True, "can_export_weights": False,
                            "equivalent_alternative": True, "switching_days": 14},
 "self-hosted open weights": {"can_pin_version": True, "can_export_weights": True,
                              "equivalent_alternative": True, "switching_days": 2},
}
def exit_assessment(p):
    problems = []
    if not p["can_pin_version"]:
        problems.append("cannot pin a version — behaviour changes without notice")
    if not p["can_export_weights"]:
        problems.append("cannot retain the artefact — no continuity if withdrawn")
    if p["switching_days"] > 30:
        problems.append(f"{p['switching_days']}d to switch — outside most RTOs")
    return (not problems), problems

print(f"{'provider':28s}{'exit strategy':>15}")
print("-" * 48)
for name, p in PROVIDERS.items():
    ok, problems = exit_assessment(p)
    print(f"{name:28s}{'defensible' if ok else 'NOT DEFENSIBLE':>15}")
    for x in problems: print(f"      ⚠ {x}")
print("\nDORA Art.11 asks this directly. It is the clause most AI procurement")
print("cannot answer, and it was written years before anyone deployed an agent.")

def make_the_case(clause, framework, agent_fact, existing_owner):
    return (f"'{clause}' ({framework}) already applies to us and is owned by "
            f"{existing_owner}.\n"
            f"   The agent fact that engages it: {agent_fact}\n"
            f"   Ask: extend the existing control, not create an AI policy.")

CASES = [
 ("ICT third-party risk", "DORA", "the model provider is an ICT third party",
  "third-party risk management"),
 ("audit controls", "HIPAA", "the acting identity is not currently recorded",
  "the security team"),
 ("access control", "PCI DSS", "non-human identities have no recertification",
  "identity and access management"),
]
for c, fw, fact, owner in CASES:
    print(make_the_case(c, fw, fact, owner)); print()

print("Compare with the alternative ask:")
print("   'We need a new AI governance policy and a new committee.'")
print("   → new owner, new process, new budget line, six months.")
print("versus")
print("   'Extend third-party risk to cover model providers.'")
print("   → existing owner, existing process, next review cycle.")
assert len(CASES) == 3
