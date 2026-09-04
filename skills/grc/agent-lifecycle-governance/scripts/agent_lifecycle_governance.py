#!/usr/bin/env python3
"""Check which lifecycle events leave a record, and find the active credentials belonging to decommissioned services.

This is the executable half of the `agent-lifecycle-governance` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
now = time.time(); DAY = 86400

IDENTITIES = {
 "triage-agent":   {"created": now - 200*DAY, "last_auth": now - 0.2*DAY,
                    "owner": "appsec", "service_running": True},
 "patch-agent":    {"created": now - 180*DAY, "last_auth": now - 1*DAY,
                    "owner": "platform", "service_running": True},
 "legacy-scanner": {"created": now - 900*DAY, "last_auth": now - 400*DAY,
                    "owner": "", "service_running": False},
 "poc-agent-2025": {"created": now - 500*DAY, "last_auth": now - 300*DAY,
                    "owner": "", "service_running": False},
 "sunset-agent":   {"created": now - 300*DAY, "last_auth": now - 2*DAY,
                    "owner": "", "service_running": False},
}
print(f"{'identity':18s}{'last auth (d)':>15}{'service running':>18}{'owner':>12}  finding")
print("-" * 92)
for name, i in IDENTITIES.items():
    age = (now - i["last_auth"])/DAY
    finding = ""
    if not i["service_running"] and age < 30:
        finding = "ACTIVE CREDENTIAL FOR A RETIRED SERVICE"
    elif not i["service_running"]:
        finding = "orphan — decommissioning never finished"
    elif not i["owner"]:
        finding = "no owner"
    print(f"{name:18s}{age:>15.0f}{str(i['service_running']):>18}"
          f"{i['owner'] or '—':>12}  {finding}")
print("\nRead the sunset-agent row twice. The service was retired. The identity")
print("authenticated two days ago. Somebody or something is still using it.")

def lifecycle_checks(identities, now, stale_days=90):
    findings = []
    for name, i in identities.items():
        age = (now - i["last_auth"])/DAY
        if not i["service_running"] and age < stale_days:
            findings.append((name, "critical",
                             "identity active for a decommissioned service"))
        elif age > stale_days:
            findings.append((name, "medium",
                             f"no authentication in {age:.0f}d — decommission it"))
        elif not i["owner"]:
            findings.append((name, "medium", "no named owner"))
    return findings

for name, sev, why in lifecycle_checks(IDENTITIES, now):
    print(f"[{sev:8s}] {name:18s} {why}")

print("\nand the manifest-diff check, for the events that change behaviour:")
SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n,s,rev in tools if n not in gated)
BEFORE = [("read_file","self",True)]
AFTER  = [("read_file","self",True), ("deploy","org",False)]
d = blast(AFTER) - blast(BEFORE)
print(f"   manifest changed: blast {blast(BEFORE)} → {blast(AFTER)} (+{d})")
print(f"   → requires re-tiering (E1.3) and a fresh SB-2 test (E1.7)")

crit = [f for f in lifecycle_checks(IDENTITIES, now) if f[1] == "critical"]
assert crit
print(f"\n{len(crit)} critical lifecycle finding(s) — each is a standing credential")
print("for something everyone believes is switched off.")
