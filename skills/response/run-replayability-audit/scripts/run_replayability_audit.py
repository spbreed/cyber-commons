#!/usr/bin/env python3
"""Check whether an incident run can be replayed at all, and what a later model version does to the replay.

This is the executable half of the `run-replayability-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass, field

@dataclass
class Run:
    prompts: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)
    model_version: str = ""
    seed: object = None

    def replayable(self):
        missing = []
        if not self.prompts:
            missing.append("prompts — cannot reconstruct what it was asked")
        if not self.tool_results:
            missing.append("tool results — the agent saw a world you cannot rebuild")
        if not self.model_version:
            missing.append("model version — a silent upgrade changes the output")
        if self.seed is None:
            missing.append("seed — sampling makes the run unrepeatable")
        return (not missing), missing

CONFIGS = {
 "fully instrumented": Run(["fix SEC-4471"], ["file contents…"], "glm-4.6@2026-07-14", 42),
 "typical production": Run(["fix SEC-4471"], ["file contents…"], "", None),
 "prompts only":       Run(["fix SEC-4471"], [], "", None),
 "actions only":       Run(),
}
for name, r in CONFIGS.items():
    ok, missing = r.replayable()
    print(f"{name:22s} replayable={ok}")
    for m in missing: print(f"      ✗ {m}")

import hashlib

def model_output(prompt, tool_result, version, seed):
    """Deterministic stand-in: output depends on ALL FOUR inputs."""
    h = hashlib.sha256(f"{prompt}|{tool_result}|{version}|{seed}".encode()).hexdigest()
    return "read_credentials" if int(h[:2], 16) % 3 == 0 else "read_source"

INCIDENT_INPUTS = ("fix SEC-4471", "billing.py: charge(card)…")

print("reproduce the incident under the ORIGINAL model version:")
orig = model_output(*INCIDENT_INPUTS, "glm-4.6@2026-07-14", 42)
print(f"   → {orig}")

print("\nreproduce it AFTER the provider upgraded (same prompts, same tool results):")
for v in ("glm-4.6@2026-08-01", "glm-4.7@2026-08-01"):
    out = model_output(*INCIDENT_INPUTS, v, 42)
    match = "reproduces" if out == orig else "DOES NOT REPRODUCE"
    print(f"   {v:22s} → {out:18s} {match}")

print("\nWithout a pinned version you cannot tell 'the agent did not do this'")
print("from 'the model that did it no longer exists'.")

COST = {
 "model version": (1,  "one string per run", "invalidates everything else if missing"),
 "seed":          (1,  "one integer per run", "makes the run repeatable"),
 "prompts":       (3,  "storage + privacy review (D1.5)", "what it was asked"),
 "tool results":  (5,  "largest volume, highest sensitivity", "what it saw"),
}
print(f"{'field':16s}{'cost':>6}  {'what it costs':38s}why it matters")
print("-" * 100)
for f, (c, cost, why) in sorted(COST.items(), key=lambda kv: kv[1][0]):
    print(f"{f:16s}{c:>6}  {cost:38s}{why}")

print("\nrecording order, by value per unit cost:")
for i, f in enumerate(sorted(COST, key=lambda k: COST[k][0]), 1):
    print(f"   {i}. {f}")

def upgrade(run, add):
    return Run(prompts=run.prompts or (["…"] if "prompts" in add else []),
               tool_results=run.tool_results or (["…"] if "tool results" in add else []),
               model_version=run.model_version or ("pinned" if "model version" in add else ""),
               seed=run.seed if run.seed is not None else (42 if "seed" in add else None))

cur = CONFIGS["typical production"]
added = set()
for f in sorted(COST, key=lambda k: COST[k][0]):
    added.add(f)
    ok, missing = upgrade(cur, added).replayable()
    print(f"\nafter adding {f:16s} replayable={ok}  still missing={len(missing)}")
assert upgrade(cur, set(COST)).replayable()[0]
