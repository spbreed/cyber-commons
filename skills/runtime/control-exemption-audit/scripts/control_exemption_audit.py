#!/usr/bin/env python3
"""Decide a launch one control at a time and then against an exemption class, and watch the two answers disagree.

This is the executable half of the `control-exemption-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

EXEMPTIONS = {
 "EX-118": {"control": "cyber-classifier", "scope": "exploitgym-eval",
            "justification": "classifier blocks the behaviour under test",
            "compensating": "egress allowlist + concurrency cap",
            "expires_day": 30, "approved_by": "security"},
}
CONTROL_STATE = {"cyber-classifier": "disabled", "egress-allowlist": "enabled",
                 "transcript-signing": "enabled"}

def may_disable(control, day, exemptions):
    for eid, x in sorted(exemptions.items()):
        if x["control"] == control and day <= x["expires_day"]:
            return True, eid
    return False, None

for control, day in (("cyber-classifier", 12), ("cyber-classifier", 44),
                     ("transcript-signing", 12)):
    ok, eid = may_disable(control, day, EXEMPTIONS)
    print(f"day {day:>3}  disable {control:20s}"
          f"{'ALLOW via ' + eid if ok else 'REFUSE - no approved exemption'}")
print()
print("The record is the mechanism, not a wiki page describing one. An")
print("exemption the platform cannot express is an exemption you cannot grant.")
assert may_disable("cyber-classifier", 12, EXEMPTIONS)[0]
assert not may_disable("transcript-signing", 12, EXEMPTIONS)[0]

LAUNCH = {"agents": 50000, "runtime_hours": 72, "egress": "any",
          "exemptions": ["EX-118"]}

def naive_launch(request):
    """Each decision checked alone, which is how the incident's was."""
    ok, _ = may_disable("cyber-classifier", 12, EXEMPTIONS)
    return {"exemption_valid": ok, "launched": True, "agents": request["agents"]}

r = naive_launch(LAUNCH)
print("checked one decision at a time:")
print(f"   exemption valid : {r['exemption_valid']}")
print(f"   launch approved : {r['launched']}  ({r['agents']:,} agents)")
print()
print("Both answers are correct. Turning the classifier off was justified and")
print("approved; launching at scale was a normal request. Nothing in the path")
print("required the two to be considered in the same sentence, and the report")
print("assesses the classifier would likely have blocked many of the actions")
print("that followed.")
assert r["launched"] and r["agents"] == 50000

CAPS = {                       # exemption class -> caps
 "none":              {"agents": 50000, "runtime_hours": 72, "egress": "allowlist+"},
 "one-detective-off": {"agents": 200,   "runtime_hours": 8,  "egress": "allowlist"},
 "two-or-more-off":   {"agents": 25,    "runtime_hours": 2,  "egress": "allowlist"},
}
DETECTIVE = {"cyber-classifier", "egress-allowlist", "transcript-signing"}

def exemption_class(state):
    off = sum(1 for c, s in state.items() if c in DETECTIVE and s != "enabled")
    return "none" if off == 0 else "one-detective-off" if off == 1 else "two-or-more-off"

def orchestrate(request, state):
    cls = exemption_class(state)
    caps = CAPS[cls]
    breaches = [k for k in ("agents", "runtime_hours")
                if request[k] > caps[k]]
    if request["egress"] != "allowlist" and cls != "none":
        breaches.append("egress")
    return {"class": cls, "caps": caps, "breaches": breaches,
            "launched": not breaches}

for label, state in (("all controls on", {"cyber-classifier": "enabled",
                                          "egress-allowlist": "enabled",
                                          "transcript-signing": "enabled"}),
                     ("classifier off", CONTROL_STATE)):
    out = orchestrate(LAUNCH, state)
    print(f"{label:18s}class={out['class']:18s}"
          f"cap={out['caps']['agents']:>6,} agents  "
          f"{'LAUNCH' if out['launched'] else 'REFUSED: ' + ','.join(out['breaches'])}")

ok = orchestrate({"agents": 200, "runtime_hours": 8, "egress": "allowlist"},
                 CONTROL_STATE)
print(f"\nsame exemption, 200 agents for 8h on an allowlist: "
      f"{'LAUNCH' if ok['launched'] else 'refused'}")
print()
print("The exemption did not become unavailable. Its price became visible, and")
print("the orchestrator charges it rather than asking someone to remember.")
assert not orchestrate(LAUNCH, CONTROL_STATE)["launched"] and ok["launched"]

SCENARIOS = [
 ("classifiers on",                {"cyber-classifier": "enabled",
                                    "egress-allowlist": "enabled",
                                    "transcript-signing": "enabled"}),
 ("classifier off",                {"cyber-classifier": "disabled",
                                    "egress-allowlist": "enabled",
                                    "transcript-signing": "enabled"}),
 ("classifier + signing off",      {"cyber-classifier": "disabled",
                                    "egress-allowlist": "enabled",
                                    "transcript-signing": "disabled"}),
]
print(f"{'state':28s}{'class':20s}{'agent cap':>10}{'runtime':>9}")
for label, state in SCENARIOS:
    cls = exemption_class(state)
    caps = CAPS[cls]
    print(f"{label:28s}{cls:20s}{caps['agents']:>10,}{caps['runtime_hours']:>8}h")

print()
print("50,000 -> 200 -> 25. The second exemption costs an order of magnitude")
print("more than the first, which is the correct shape: compounding is where")
print("the incident's risk sat, and it is the case a human reviewer is worst at")
print("holding in their head.")
assert CAPS["two-or-more-off"]["agents"] < CAPS["one-detective-off"]["agents"]
