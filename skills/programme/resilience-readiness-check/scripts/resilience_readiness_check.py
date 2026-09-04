#!/usr/bin/env python3
"""Check the three properties a programme needs when a control fails: drift detected, stop tested, run replayable.

This is the executable half of the `resilience-readiness-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time, statistics
now = time.time()

# --- NOTICE ------------------------------------------------------------
BASELINE = {"read_file": 0.85, "search": 0.15}
TODAY    = {"read_file": 300, "search": 100, "run_shell": 400}
total = sum(TODAY.values())
mix = {k: v/total for k, v in TODAY.items()}
keys = set(mix) | set(BASELINE)
drift = sum(abs(mix.get(k,0) - BASELINE.get(k,0)) for k in keys)/2
new_tools = sorted(set(mix) - set(BASELINE))
notice = drift > 0.25 or bool(new_tools)
print(f"NOTICE   drift {drift:.3f}  new tools {new_tools}  → "
      f"{'detected' if notice else 'MISSED'}")

# --- STOP --------------------------------------------------------------
STOP = {"mechanism": "revoke the SPIFFE identity at the gateway",
        "measured_seconds": 12, "tested_days_ago": 41, "survives_restart": True}
stop_ok = (STOP["measured_seconds"] is not None and STOP["tested_days_ago"] <= 180
           and STOP["survives_restart"])
print(f"STOP     {STOP['measured_seconds']}s, tested {STOP['tested_days_ago']}d ago, "
      f"survives restart {STOP['survives_restart']}  → {'ready' if stop_ok else 'NOT READY'}")

# --- RECOVER -----------------------------------------------------------
RUN = {"prompts": ["fix SEC-4471"], "tool_results": ["contents…"],
       "model_version": "glm-4.6@2026-07-14", "seed": 42}
missing = [k for k, v in RUN.items() if not v and v != 0]
CHAIN = ["dana@corp", "orchestrator", "patch-agent"]
REACHED = {"dana@corp": ["repo-core"], "orchestrator": ["queue"],
           "patch-agent": ["repo-core","repo-payments"]}
scope = sorted({r for a in CHAIN for r in REACHED.get(a, [])})
recover = not missing and bool(scope)
print(f"RECOVER  replayable {not missing}, scope from the chain {scope}  → "
      f"{'ready' if recover else 'NOT READY'}")

PROGRAMMES = {
 "prevention only": {"notice": False, "stop": False, "recover": False,
                     "containment_asr": 0.0},
 "prevention + notice": {"notice": True, "stop": False, "recover": False,
                         "containment_asr": 0.0},
 "resilient": {"notice": True, "stop": True, "recover": True,
               "containment_asr": 0.0},
}
def incident_outcome(p, containment_failed=True):
    if not containment_failed:
        return "no incident", 0
    if not p["notice"]:
        return "undetected — found by a third party, weeks later", 720
    if not p["stop"]:
        return "detected, cannot halt it — damage continues while you improvise", 96
    if not p["recover"]:
        return "detected and halted, cannot say what was touched or why", 48
    return "detected, halted in seconds, scope known, run replayable", 6

print(f"{'programme':24s}{'containment ASR':>17}  outcome when containment fails")
print("-" * 96)
for name, p in PROGRAMMES.items():
    outcome, hours = incident_outcome(p)
    print(f"{name:24s}{p['containment_asr']:>17.0%}  {outcome}")
    print(f"{'':41s}elapsed to resolution: {hours}h")
print("\nAll three have a 0% attack success rate. On a prevention-only")
print("scorecard they are identical. They are not remotely identical.")

def game_day(programme):
    """Assume the prevention worked until it didn't. Measure the other three."""
    results = {}
    results["notice"]  = (0.2, "drift alert fired") if programme["notice"] \
                         else (None, "no signal — nothing fired")
    results["stop"]    = (12, "identity revoked, survives restart") if programme["stop"] \
                         else (None, "no tested mechanism")
    results["recover"] = (6, "replayed the run, scope from the act chain") \
                         if programme["recover"] else (None, "cannot reconstruct")
    weakest = next((k for k, (v, _) in results.items() if v is None), None)
    return results, weakest

for name, p in PROGRAMMES.items():
    res, weakest = game_day(p)
    print(f"=== {name} ===")
    for cap, (val, note) in res.items():
        print(f"   {cap:9s}{(str(val) + 'h') if val is not None else 'FAIL':>7}  {note}")
    print(f"   weakest capability: {weakest or 'none — all three hold'}\n")

_, weakest = game_day(PROGRAMMES["resilient"])
assert weakest is None
print("The weakest capability is next quarter's plan. That is the whole")
print("programme-management loop, and it does not require predicting the attack.")

# Close the curriculum: what you built, and what it is for.
BUILT = [
 ("A1-A3", "a control plane: planes, identity, containment"),
 ("B1",    "a 15-stage AppSec pipeline, ending in confirmed-by-exploitation severity"),
 ("B2",    "a harness whose verifier does not lie"),
 ("C1-C2", "the ability to attack it and to research it repeatably"),
 ("D1-D2", "the ability to notice, stop and recover"),
 ("E1-E3", "the ability to evidence all of it, and to decide"),
]
for track, what in BUILT:
    print(f"   {track:8s}{what}")
print("\nNone of it assumes a frontier-lab account, a vendor platform, or a")
print("budget. That was the point: shared defense is stronger defense, and a")
print("commons only works if everyone can actually run it.")
