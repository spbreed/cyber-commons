#!/usr/bin/env python3
"""Assess AI components of a supply chain for silent change and agent authority, and invalidate the control tests taken before a model changed.

This is the executable half of the `third-party-ai-assessment` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Component:
    name: str; kind: str; signed: bool = False
    pinned: bool = False; can_change_silently: bool = False
    runs_with_agent_authority: bool = False; downloads: int = 0

COMPONENTS = [
 Component("cryptography==42.0.5", "library", True, True, False, False, 900_000),
 Component("langchain==0.2.1", "library", False, True, False, False, 400_000),
 Component("hosted GLM-4.6 endpoint", "hosted model", False, False, True, False),
 Component("local glm-4.6 weights (pinned digest)", "weights", True, True, False, False),
 Component("mcp-jira-connector==0.0.3", "tool package", False, True, False, True, 180),
]
def assess(c):
    flags = []
    if not c.signed:                  flags.append("unsigned")
    if not c.pinned:                  flags.append("not version-pinned")
    if c.can_change_silently:         flags.append("CAN CHANGE WITHOUT NOTICE")
    if c.runs_with_agent_authority:   flags.append("runs with agent authority")
    if c.kind == "library" and c.downloads < 1000: flags.append("little scrutiny")
    tier = ("high" if c.can_change_silently or c.runs_with_agent_authority
            else "medium" if flags else "low")
    return tier, flags

print(f"{'component':40s}{'kind':14s}{'tier':8s}flags")
print("-" * 96)
for c in COMPONENTS:
    tier, flags = assess(c)
    print(f"{c.name:40s}{c.kind:14s}{tier:8s}{', '.join(flags) or '—'}")

import time
now = time.time(); DAY = 86400

CONTROL_TESTS = {"SB-2": now - 20*DAY, "EV-2": now - 20*DAY, "DR-1": now - 20*DAY}
MODEL_CHANGED_AT = now - 5*DAY

print("your controls were tested against a model that changed 5 days ago:")
for cid, tested in CONTROL_TESTS.items():
    valid = tested > MODEL_CHANGED_AT
    print(f"   {cid}  tested {int((now-tested)/DAY)}d ago  "
          f"{'still valid' if valid else 'INVALIDATED by the model change'}")
invalidated = [c for c, t in CONTROL_TESTS.items() if t <= MODEL_CHANGED_AT]
print(f"\n{len(invalidated)}/{len(CONTROL_TESTS)} control tests invalidated by a "
      f"change you did not make and were not told about.")
assert invalidated

QUESTIONS = [
 ("Can this component change without notifying us?",
  "if yes, every control test has an implicit expiry tied to the vendor"),
 ("Does it execute with our agent's authority?",
  "if yes, assess it as code, not as a dependency"),
 ("Can we pin a digest, and do we?",
  "the difference between a supply chain and a subscription"),
 ("What is our exit if we stop using it?",
  "DORA Art.11 asks this directly; most AI contracts have no answer"),
]
for q, why in QUESTIONS: print(f"Q: {q}\n   → {why}\n")

SIGNALS = {
 "library":      {"signature": True, "downloads": True, "pinning": True, "lineage": True},
 "hosted model": {"signature": False, "downloads": False, "pinning": False, "lineage": False},
 "weights":      {"signature": True, "downloads": False, "pinning": True, "lineage": False},
 "tool package": {"signature": False, "downloads": False, "pinning": True, "lineage": False},
}
print(f"{'artefact class':16s}{'signals available':>20}  unavailable")
print("-" * 74)
for kind, sig in SIGNALS.items():
    have = [k for k, v in sig.items() if v]
    lack = [k for k, v in sig.items() if not v]
    print(f"{kind:16s}{f'{len(have)}/{len(sig)}':>20}  {lack or '—'}")

def assessment_statement(kind):
    sig = SIGNALS[kind]
    lack = [k for k, v in sig.items() if not v]
    return (f"{kind}: assessed on {len(sig)-len(lack)}/{len(sig)} signals. "
            f"{', '.join(lack) or 'none'} unavailable for this artefact class.")
print()
for kind in SIGNALS: print("  " + assessment_statement(kind))
print("\nThat last sentence is the deliverable. A rating that hides which signals")
print("were unavailable is a number someone will later rely on.")
