#!/usr/bin/env python3
"""Build an AI inventory from three sources and measure ownership coverage against what the third one finds.

This is the executable half of the `deployment-inventory-resolver` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass, field

@dataclass
class AIAsset:
    name: str
    kind: str              # model | agent | copilot | embedded-feature
    owner: str = ""
    autonomy: str = "L1"
    data: tuple = ()
    external: bool = False
    discovered_via: str = "registry"

    def gaps(self):
        g = []
        if not self.owner:
            g.append("no named owner — nobody can accept the risk or recertify it")
        if self.discovered_via != "registry":
            g.append(f"not registered — found via {self.discovered_via}")
        if self.autonomy in ("L2.5", "L3") and not self.owner:
            g.append("acts semi-autonomously with nobody accountable")
        return g

REGISTRY = [
 AIAsset("fraud-scoring-model", "model", "risk-eng", "L1", ("customer",)),
 AIAsset("support-summariser", "copilot", "support-eng", "L1", ("customer",)),
]
PROCUREMENT = [
 AIAsset("vendor-contract-analyser", "embedded-feature", "", "L1", ("regulated",),
         discovered_via="expense report"),
]
EGRESS = [
 AIAsset("unknown-openai-usage-marketing", "copilot", "", "L1", ("public",),
         discovered_via="egress logs"),
 AIAsset("pr-remediation-agent", "agent", "", "L2.5", ("customer",), True,
         discovered_via="egress logs"),
 AIAsset("agent-worker-7f3c", "agent", "", "L2.5", ("customer",),
         discovered_via="egress logs"),
]
ALL = REGISTRY + PROCUREMENT + EGRESS
print(f"{'asset':34s}{'kind':18s}{'autonomy':10s}{'owner':14s}found via")
print("-" * 92)
for a in ALL:
    print(f"{a.name:34s}{a.kind:18s}{a.autonomy:10s}{a.owner or '—':14s}{a.discovered_via}")
print(f"\nregistry found {len(REGISTRY)}; the other two sources found "
      f"{len(ALL)-len(REGISTRY)} more.")

unowned = [a for a in ALL if not a.owner]
unregistered = [a for a in ALL if a.discovered_via != "registry"]
high_autonomy_unowned = [a for a in ALL if a.autonomy in ("L2.5","L3") and not a.owner]

print(f"assets                    {len(ALL)}")
print(f"no named owner            {len(unowned)}  {[a.name for a in unowned]}")
print(f"never registered          {len(unregistered)}")
print(f"L2.5+ with no owner       {len(high_autonomy_unowned)}  "
      f"{[a.name for a in high_autonomy_unowned]}")

print("\ngaps in detail:")
for a in ALL:
    for g in a.gaps():
        print(f"   {a.name:34s}{g}")
assert high_autonomy_unowned

MODEL_PROVIDER_DOMAINS = {"api.openai.com", "api.anthropic.com",
                          "generativelanguage.googleapis.com",
                          "api.mistral.ai", "api.together.xyz"}

EGRESS_LOG = [
 {"src": "marketing-workstation-14", "host": "api.openai.com", "bytes": 240_000},
 {"src": "svc-pr-remediation",       "host": "api.anthropic.com", "bytes": 8_400_000},
 {"src": "build-runner-3",           "host": "registry.npmjs.org", "bytes": 90_000},
 {"src": "agent-worker-7f3c",        "host": "api.together.xyz", "bytes": 1_200_000},
]
def discover(log, known_names):
    found = []
    for row in log:
        if row["host"] not in MODEL_PROVIDER_DOMAINS: continue
        if row["src"] in known_names: continue
        found.append({"source": row["src"], "provider": row["host"],
                      "volume": row["bytes"],
                      "finding": "AI usage not present in the inventory"})
    return found

known = {a.name for a in REGISTRY + PROCUREMENT}
for f in discover(EGRESS_LOG, known):
    print(f"{f['source']:30s}{f['provider']:34s}{f['volume']:>10,} bytes")
    print(f"{'':30s}{f['finding']}")

def inventory_health(assets):
    return {"total": len(assets),
            "owned": sum(1 for a in assets if a.owner),
            "registered": sum(1 for a in assets if a.discovered_via == "registry"),
            "coverage": round(sum(1 for a in assets if a.owner)/len(assets), 2)}
print(f"\n{inventory_health(ALL)}")
