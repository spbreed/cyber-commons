#!/usr/bin/env python3
"""Pick the framework that covers the most controls as a spine, and supply the remainder from the others rather than building per-framework.

This is the executable half of the `framework-spine-selection` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from collections import defaultdict

CONTROLS = {
 "AC-1": ("NIST AI RMF: GOVERN-1.2", "ISO 42001: 6.1", "EU AI Act: Art.14"),
 "AC-2": ("NIST AI RMF: MANAGE-2.2", "ISO 42001: 8.1"),
 "SB-1": ("NIST AI RMF: MANAGE-2.1", "ISO 27001: A.8.20"),
 "SB-2": ("EU AI Act: Art.14",),
 "EV-1": ("ISO 42001: 9.1", "EU AI Act: Art.12"),
 "EV-2": ("NIST AI RMF: MEASURE-2.3",),
 "DR-1": ("NIST AI RMF: MEASURE-2.4", "ISO 42001: 9.1"),
 "ST-1": ("EU AI Act: Art.14", "DORA: Art.11"),
}
by_fw = defaultdict(set)
for cid, fws in CONTROLS.items():
    for f in fws:
        by_fw[f.split(":")[0]].add(cid)

print(f"{'framework':18s}{'covers':>8}  controls")
print("-" * 62)
for fw, cids in sorted(by_fw.items(), key=lambda kv: -len(kv[1])):
    print(f"{fw:18s}{len(cids):>8}  {sorted(cids)}")

spine = max(by_fw, key=lambda f: len(by_fw[f]))
gaps = sorted(set(CONTROLS) - by_fw[spine])
print(f"\nbest spine: {spine} covering {len(by_fw[spine])}/{len(CONTROLS)}")
print(f"not reached by the spine: {gaps}")

def per_regulation(controls):
    """Build a separate control set for each instrument. The usual approach."""
    sets = defaultdict(set)
    for cid, fws in controls.items():
        for f in fws:
            sets[f.split(":")[0]].add(cid)
    return sets

sets = per_regulation(CONTROLS)
total_implementations = sum(len(v) for v in sets.values())
distinct_controls = len(CONTROLS)
print(f"distinct controls actually needed : {distinct_controls}")
print(f"control implementations if built per-framework : {total_implementations}")
print(f"duplication factor : {total_implementations/distinct_controls:.1f}×")

print("\ncontrols claimed by more than one framework:")
for cid, fws in CONTROLS.items():
    if len(fws) > 1:
        print(f"   {cid}  {len(fws)} frameworks: {[f.split(':')[0] for f in fws]}")
print("\nBuilt separately, these drift: the ISO version of AC-1 and the AI Act")
print("version diverge, evidence is produced twice, and neither is trusted.")
assert total_implementations > distinct_controls

def spine_plan(controls, spine):
    covered = {c for c, fws in controls.items() if any(f.startswith(spine) for f in fws)}
    gaps = sorted(set(controls) - covered)
    secondary = defaultdict(list)
    for g in gaps:
        for f in controls[g]:
            secondary[f.split(":")[0]].append(g)
    return {"spine": spine, "covered": sorted(covered), "gaps": gaps,
            "secondary_sources": {k: v for k, v in secondary.items()
                                  if not k.startswith(spine)}}

plan = spine_plan(CONTROLS, "NIST AI RMF")
print(f"spine              {plan['spine']}")
print(f"covered by spine   {len(plan['covered'])}/{len(CONTROLS)}  {plan['covered']}")
print(f"gaps               {plan['gaps']}")
print("secondary sources needed for the gaps:")
for fw, cids in plan["secondary_sources"].items():
    print(f"   {fw:20s} supplies {cids}")

print("\nstatement for the assessor:")
print(f"   'We operate {len(CONTROLS)} AI controls, built against {plan['spine']}.")
print(f"    {len(plan['covered'])} map directly to it; {len(plan['gaps'])} come from")
print(f"    {list(plan['secondary_sources'])}. Each control produces one artefact,")
print("    which satisfies every clause it maps to.'")
assert plan["gaps"]
