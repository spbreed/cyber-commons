#!/usr/bin/env python3
"""Check whether a model validated at one autonomy level and tool set is still covered by that validation as deployed.

This is the executable half of the `model-risk-validation-scope` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

PILLARS = {
 "conceptual_soundness": ("is the method appropriate for the purpose",
                          "assumes the purpose is stable and stated"),
 "ongoing_monitoring":   ("is it still performing as validated",
                          "assumes performance is what changes"),
 "independent_validation":("did someone other than the builder check",
                          "assumes the thing checked is the thing deployed"),
}
print(f"{'pillar':24s}{'what it asks':46s}what it quietly assumes")
for p in sorted(PILLARS):
    asks, assumes = PILLARS[p]
    print(f"{p:24s}{asks:46s}{assumes}")
print()
print("All three survive contact with AI. The assumptions are what break.")

VALIDATED = {
 "model": "glm-5.2", "version": "2026-03",
 "purpose": "summarise support tickets",
 "tools": [],                       # at validation time it had none
 "autonomy": "L1",                  # suggests; a human acts
}

def validation_covers(deployed, validated):
    diffs = []
    if deployed["model"] != validated["model"]:       diffs.append("model changed")
    if deployed["version"] != validated["version"]:   diffs.append("version changed")
    if deployed["purpose"] != validated["purpose"]:   diffs.append("purpose changed")
    if sorted(deployed["tools"]) != sorted(validated["tools"]):
        diffs.append(f"tool surface changed: {sorted(set(deployed['tools']) - set(validated['tools']))}")
    if deployed["autonomy"] != validated["autonomy"]: diffs.append(
        f"autonomy raised {validated['autonomy']} -> {deployed['autonomy']}")
    return (not diffs), diffs

DEPLOYED = dict(VALIDATED, tools=["read_ticket", "write_ticket", "db_update"],
                autonomy="L3")
ok, diffs = validation_covers(DEPLOYED, VALIDATED)
print(f"validation still covers what is deployed: {ok}")
for d in diffs:
    print(f"   {d}")
print()
print("Same weights. Same version. The validation report is accurate about a")
print("system that no longer exists, and nothing in the classical process is")
print("required to notice, because the classical trigger is a model change.")
assert not ok

import random
def monitor(metric, runs=200, seed=4):
    rng = random.Random(seed)
    return [round(rng.gauss(0.92, 0.01), 3) for _ in range(runs)]

acc = monitor("summarisation_accuracy")
print(f"summarisation accuracy over 200 runs: mean {sum(acc)/len(acc):.3f}, "
      f"min {min(acc)}, max {max(acc)}")
print("threshold 0.85 -> breaches:", sum(a < 0.85 for a in acc))
print()
UNMONITORED = ["rows written to production", "tools invoked per run",
               "actions taken without human review", "scope of the credential used"]
print("what is NOT on the dashboard:")
for u in UNMONITORED:
    print(f"   {u}")
print()
print("The monitoring is excellent and it is monitoring the prediction. The")
print("risk moved to the action, and the action has no threshold, no baseline")
print("and no alert.")
assert sum(a < 0.85 for a in acc) == 0

TRIGGERS = {
 "model or version change": True,
 "prompt or config change": True,
 "tool added or scope widened": True,
 "autonomy level raised": True,
 "purpose changed": True,
 "calendar year elapsed": True,
}
CLASSICAL = {"model or version change", "calendar year elapsed"}

print(f"{'trigger':32s}{'classical MRM':16s}extended")
for t in TRIGGERS:
    print(f"{t:32s}{'yes' if t in CLASSICAL else 'no':16s}yes")
missed = [t for t in TRIGGERS if t not in CLASSICAL]
print(f"\ntriggers classical MRM would miss: {len(missed)}")
for m in missed: print(f"   {m}")
print()
ok2, diffs2 = validation_covers(DEPLOYED, VALIDATED)
print(f"under the extended triggers, this deployment requires revalidation: {not ok2}")
print(f"reasons: {diffs2}")
assert len(missed) == 4

record = {
 "model": DEPLOYED["model"], "version": DEPLOYED["version"],
 "purpose": DEPLOYED["purpose"],
 "tool_surface": sorted(DEPLOYED["tools"]),
 "autonomy": DEPLOYED["autonomy"],
 "validated_unit": "model + tool surface + autonomy",
 "monitors": ["summarisation_accuracy", "rows_written", "tools_per_run",
              "actions_without_review"],
 "revalidation_triggers": sorted(TRIGGERS),
 "independent_of_builder": True,
}
for k in sorted(record):
    print(f"   {k:24s}{record[k]}")
print()
print("Three fields carry the whole extension: validated_unit, tool_surface and")
print("autonomy. Without them a validation report describes a text generator,")
print("and the thing in production is an actor.")
assert record["validated_unit"].startswith("model + tool")
