#!/usr/bin/env python3
"""Resolve which regulatory layers apply to a system and register the shortest clock among them.

This is the executable half of the `obligation-mapping` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass

@dataclass
class System:
    name: str; sector: str; data: tuple; autonomy: str
    affects_individuals: bool; is_ict_service: bool

CLAIMS = System("claims-triage-agent", sector="insurance",
                data=("customer", "health", "regulated"), autonomy="L2.5",
                affects_individuals=True, is_ict_service=True)

def applicable(sys_):
    out = []
    # layer 1
    if sys_.autonomy in ("L2", "L2.5", "L3") and sys_.affects_individuals:
        out.append(("EU AI Act", 1, "automated decision affecting individuals; "
                    "human oversight and record-keeping obligations"))
    # layer 2
    if sys_.sector in ("insurance", "banking", "financial"):
        out.append(("DORA", 2, "ICT third-party risk, incident reporting, "
                    "resilience testing, exit strategy"))
    if "health" in sys_.data:
        out.append(("HIPAA-equivalent", 2, "minimum necessary; audit controls"))
    # layer 3
    if sys_.affects_individuals and "customer" in sys_.data:
        out.append(("GDPR", 3, "lawful basis, erasure, automated decision-making"))
    return sorted(out, key=lambda r: r[1])

print(f"{CLAIMS.name} — autonomy {CLAIMS.autonomy}, data {list(CLAIMS.data)}\n")
print(f"{'instrument':22s}{'layer':>6}  obligation")
print("-" * 92)
for name, layer, why in applicable(CLAIMS):
    print(f"{name:22s}{layer:>6}  {why}")

CLOCKS = {
 "DORA (major ICT incident)":       (4,  "initial notification to the regulator"),
 "contractual (major client)":      (12, "client security contact"),
 "NIS2 (early warning)":            (24, "national CSIRT"),
 "GDPR (personal data breach)":     (72, "supervisory authority"),
 "EU AI Act (serious incident)":    (72, "market surveillance authority"),
}
applicable_names = {n for n, _, _ in applicable(CLAIMS)}
mine = {k: v for k, v in CLOCKS.items()
        if any(a.split()[0] in k for a in applicable_names) or "contractual" in k}

print(f"{'obligation':36s}{'deadline (h)':>14}  notify")
print("-" * 78)
for name, (hours, who) in sorted(mine.items(), key=lambda kv: kv[1][0]):
    print(f"{name:36s}{hours:>14}  {who}")
shortest = min(mine.items(), key=lambda kv: kv[1][0])
print(f"\nBINDING DEADLINE: {shortest[0]} at {shortest[1][0]}h")
print("Every runbook, every escalation path and every out-of-hours rota is")
print("designed against that number, not against the 72-hour one people quote.")
assert shortest[1][0] <= 12

# Verify: which layer actually drove the requirements?
from collections import Counter
layers = Counter(layer for _, layer, _ in applicable(CLAIMS))
print("obligations by layer:", dict(layers))
print()
for layer, label in ((1, "horizontal AI regulation"), (2, "sector overlay"),
                     (3, "cross-cutting")):
    n = layers.get(layer, 0)
    print(f"   layer {layer} ({label:26s}) {n} obligation(s)")
print("\nLayers 2 and 3 produce more obligations than layer 1, and they were")
print("already in force before anyone deployed an agent. That is the finding.")
assert layers.get(2, 0) + layers.get(3, 0) > layers.get(1, 0)
