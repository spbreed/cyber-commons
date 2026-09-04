#!/usr/bin/env python3
"""Map a control catalogue outward to framework clauses, and assemble the evidence pack a tier requires.

This is the executable half of the `control-to-framework-mapping` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Control:
    cid: str; text: str; kind: str; frameworks: tuple

CATALOGUE = [
 Control("AC-1", "agent identities are distinct from human and separately revocable",
         "preventive", ("NIST AI RMF: GOVERN-1.2", "ISO 42001: 6.1", "EU AI Act: Art.14")),
 Control("AC-2", "delegated authority narrows at every hop and is recorded in an act chain",
         "preventive", ("NIST AI RMF: MANAGE-2.2", "ISO 42001: 8.1")),
 Control("SB-1", "agent egress is deny-by-default with an allowlist",
         "preventive", ("NIST AI RMF: MANAGE-2.1", "ISO 27001: A.8.20")),
 Control("SB-2", "privileged tools require approval below autonomy L3",
         "preventive", ("EU AI Act: Art.14 human oversight",)),
 Control("EV-1", "every agent action is logged with the acting identity",
         "detective", ("ISO 42001: 9.1", "EU AI Act: Art.12 record-keeping")),
 Control("EV-2", "harness accuracy evaluated against a held-out key each release",
         "detective", ("NIST AI RMF: MEASURE-2.3",)),
 Control("DR-1", "behavioural drift from the signed-off baseline raises an alert",
         "detective", ("NIST AI RMF: MEASURE-2.4", "ISO 42001: 9.1")),
 Control("ST-1", "a tested stop mechanism halts an agent fleet without vendor help",
         "corrective", ("EU AI Act: Art.14", "DORA: Art.11")),
]
print(f"{'control':8s}{'kind':12s}satisfies")
print("-" * 84)
for c in CATALOGUE:
    print(f"{c.cid:8s}{c.kind:12s}{len(c.frameworks)} clause(s): {c.frameworks[0]}")
    for f in c.frameworks[1:]:
        print(f"{'':20s}{f}")

def map_controls(tier, catalogue=CATALOGUE):
    if tier in ("critical", "high"):
        required = list(catalogue)
    else:
        required = [c for c in catalogue if c.kind == "preventive" or c.cid == "EV-1"]
    frameworks = sorted({f for c in required for f in c.frameworks})
    return {"tier": tier, "controls": [c.cid for c in required],
            "frameworks_satisfied": frameworks}

for tier in ("critical", "medium"):
    m = map_controls(tier)
    print(f"\ntier {tier}: {len(m['controls'])} controls → "
          f"{len(m['frameworks_satisfied'])} framework clauses")
    print(f"   controls   {m['controls']}")
    for f in m["frameworks_satisfied"]:
        print(f"   satisfies  {f}")

FRAMEWORK_CLAUSES = [
 "NIST AI RMF: GOVERN-1.1 policies are documented",
 "NIST AI RMF: GOVERN-1.2 roles and responsibilities are defined",
 "NIST AI RMF: MAP-1.1 context is established",
 "NIST AI RMF: MEASURE-2.3 performance is evaluated",
 "ISO 42001: 6.1 actions to address risks",
 "ISO 42001: 7.2 competence",
 "ISO 42001: 9.1 monitoring and measurement",
]
have = {f for c in CATALOGUE for f in c.frameworks}
print(f"{'clause':52s}{'operating control?':>20}")
print("-" * 74)
orphans = []
for clause in FRAMEWORK_CLAUSES:
    covered = clause in have
    if not covered: orphans.append(clause)
    print(f"{clause:52s}{('yes' if covered else 'NO — checklist only'):>20}")
print(f"\n{len(orphans)}/{len(FRAMEWORK_CLAUSES)} clauses have no operating control behind them.")
print("Working framework-first, those get a policy document and a tick. Working")
print("control-first, they are visibly uncovered — which is the useful state.")
assert orphans

EVIDENCE = {
 "AC-1": "gateway logs containing an act chain for every action; monthly sample",
 "AC-2": "regression suite cases IDN-01/IDN-04, run on every release",
 "SB-1": "90-day egress denial log",
 "SB-2": "tool policy in git + denial log",
 "EV-1": "audit sample of 50 actions with acting identity present",
 "EV-2": "expert accuracy against a held-out key, per release",
 "DR-1": "drift alerts and their dispositions",
 "ST-1": "game-day record with measured time-to-stop",
}
def evidence_pack(tier):
    m = map_controls(tier)
    return [{"control": cid, "evidence": EVIDENCE[cid],
             "satisfies": [f for c in CATALOGUE if c.cid == cid for f in c.frameworks]}
            for cid in m["controls"]]

pack = evidence_pack("critical")
for row in pack[:4]:
    print(f"{row['control']}  {row['evidence']}")
    for f in row["satisfies"]:
        print(f"      → {f}")
print(f"\n{len(pack)} controls produce evidence for "
      f"{len({f for r in pack for f in r['satisfies']})} framework clauses.")
print("One artefact, many clauses. That ratio is why control-first is cheaper.")
