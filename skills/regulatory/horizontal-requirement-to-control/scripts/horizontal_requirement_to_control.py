#!/usr/bin/env python3
"""Turn horizontal AI regulation themes into named controls with evidence artefacts, and apply the show-me test to prose answers.

This is the executable half of the `horizontal-requirement-to-control` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

CATALOGUE = {
 "AC-1": ("agent identities distinct from human and separately revocable",
          "gateway logs with an act chain; monthly sample"),
 "AC-2": ("delegated authority narrows at every hop",
          "regression suite IDN-01/IDN-04 on every release"),
 "SB-1": ("egress deny-by-default with an allowlist", "90-day denial log"),
 "SB-2": ("privileged tools require approval below L3", "tool policy in git + denial log"),
 "EV-1": ("every action logged with the acting identity", "audit sample of 50 actions"),
 "EV-2": ("accuracy evaluated against a held-out key per release",
          "expert accuracy report with sample size"),
 "DR-1": ("behavioural drift raises an alert", "drift alerts and dispositions"),
 "ST-1": ("a tested stop mechanism you own", "game-day record with measured time-to-stop"),
}
THEMES = {
 "risk management system":       ["AC-1", "SB-2", "DR-1"],
 "record-keeping (Art.12)":      ["EV-1", "AC-2"],
 "human oversight (Art.14)":     ["SB-2", "ST-1"],
 "accuracy and robustness":      ["EV-2", "DR-1"],
}
for theme, cids in THEMES.items():
    print(f"{theme}")
    for cid in cids:
        text, evidence = CATALOGUE[cid]
        print(f"   {cid}  {text}")
        print(f"         evidence: {evidence}")
    print()

WEAK = {
 "risk management system":   "We operate a risk management framework for AI systems.",
 "record-keeping (Art.12)":  "Appropriate logs are retained.",
 "human oversight (Art.14)": "Human oversight is maintained at all times.",
 "accuracy and robustness":  "Models are tested prior to deployment.",
}
def survives_followup(answer, controls):
    """The follow-up question is always 'show me'."""
    return bool(controls), ("names a control with an artefact" if controls
                            else "no artefact — the answer IS the evidence, which is the problem")

print(f"{'theme':28s}{'prose answer survives?':>24}")
print("-" * 56)
for theme in THEMES:
    ok_weak, _ = survives_followup(WEAK[theme], [])
    print(f"{theme:28s}{str(ok_weak):>24}")
print("\nAll four fail the same way: there is nothing to produce when asked.")

import time
from dataclasses import dataclass
now = time.time(); DAY = 86400

@dataclass
class ControlTest:
    cid: str; passed: bool; tested_at: float; valid_for_days: float
    def state(self, at):
        if (at - self.tested_at)/DAY > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

TESTS = [ControlTest("AC-1", True,  now -  3*DAY, 30),
         ControlTest("AC-2", True,  now -  9*DAY, 30),
         ControlTest("SB-2", True,  now - 40*DAY, 30),
         ControlTest("EV-1", True,  now -  5*DAY, 60),
         ControlTest("EV-2", True,  now - 12*DAY, 30),
         ControlTest("DR-1", False, now,          30),
         ControlTest("ST-1", True,  now - 41*DAY, 180)]
by = {t.cid: t for t in TESTS}

print(f"{'theme':28s}{'controls':22s}{'evidenced now':>15}")
print("-" * 68)
for theme, cids in THEMES.items():
    states = [by[c].state(now) if c in by else "NO EVIDENCE" for c in cids]
    ok = all(s == "PASS" for s in states)
    blockers = ",".join(c for c, s in zip(cids, states) if s != "PASS")
    verdict = "yes" if ok else f"NO — {blockers}"
    print(f"{theme:28s}{str(cids):22s}{verdict:>15}")

fully = [t for t, cids in THEMES.items()
         if all((by[c].state(now) if c in by else "X") == "PASS" for c in cids)]
print(f"\nthemes fully evidenced right now: {len(fully)}/{len(THEMES)}  {fully}")
print("\nThat sentence is what you say to a supervisor. It is smaller than the")
print("prose version and it is defensible, which is the trade worth making.")
assert len(fully) < len(THEMES)
