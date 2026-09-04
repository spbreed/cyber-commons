#!/usr/bin/env python3
"""Convert an intel feed into rules, dropping what cannot be matched, and report the three numbers that say whether the feed is worth its price.

This is the executable half of the `threat-intel-to-rules` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
from dataclasses import dataclass

@dataclass
class Indicator:
    value: str; kind: str; source: str; confidence: float

FEED = [
 Indicator("collect.example.com", "host", "vendor-a", 0.95),
 Indicator("169.254.169.254", "host", "internal-research", 0.99),
 Indicator("a1b2c3d4e5f6", "hash", "vendor-b", 0.72),
 Indicator("pastebin.example", "host", "vendor-a", 0.55),
 Indicator("adversaries increasingly use agentic tooling", "narrative", "blog", 0.40),
 Indicator("agents reading ~/.aws/credentials", "technique", "internal-ir", 0.88),
 Indicator("threat actor GOLDEN-OTTER is targeting fintech", "narrative", "vendor-c", 0.60),
]
CONF_FLOOR = 0.70
MATCHABLE = {"host", "hash", "technique"}

def actionable(i):
    if i.kind not in MATCHABLE:
        return False, f"{i.kind} is not matchable in telemetry"
    if i.confidence < CONF_FLOOR:
        return False, f"confidence {i.confidence} below floor {CONF_FLOOR}"
    return True, "convertible to a rule"

print(f"{'indicator':46s}{'kind':11s}{'conf':>6}  verdict")
print("-" * 88)
for i in FEED:
    ok, why = actionable(i)
    print(f"{i.value[:44]:46s}{i.kind:11s}{i.confidence:>6.2f}  "
          f"{'RULE' if ok else 'drop'} — {why}")

@dataclass
class Rule:
    name: str; severity: str; match: object; response: str

def to_rules(feed):
    rules = []
    for i in feed:
        ok, _ = actionable(i)
        if not ok: continue
        sev = "critical" if i.confidence > 0.9 else "high"
        if i.kind == "host":
            m = (lambda v: (lambda e: v in e.get("target", "")))(i.value)
            resp = f"block egress, revoke the agent's token, hunt back 30d ({i.source})"
        elif i.kind == "hash":
            m = (lambda v: (lambda e: v == e.get("hash", "")))(i.value)
            resp = f"quarantine the artefact, check the supply chain ({i.source})"
        else:
            m = (lambda: (lambda e: "/.aws/" in e.get("target", "")))()
            resp = f"revoke, rotate the cloud role, audit reads ({i.source})"
        rules.append(Rule(f"intel:{i.kind}:{i.value[:26]}", sev, m, resp))
    return rules

rules = to_rules(FEED)
print(f"{len(FEED)} indicators → {len(rules)} deployable rules "
      f"({len(rules)/len(FEED):.0%} conversion)\n")
for r in rules:
    print(f"   [{r.severity:8s}] {r.name}")

EVENTS = [
 {"actor": "patch-agent", "target": "https://collect.example.com/x"},
 {"actor": "triage-agent", "target": "https://api.github.com/repos"},
 {"actor": "patch-agent", "target": "/home/app/.aws/credentials"},
 {"actor": "svc-etl", "target": "/data/export.csv"},
 {"actor": "build-agent", "hash": "a1b2c3d4e5f6"},
]
fired = [(r, e) for r in rules for e in EVENTS if r.match(e)]
print("alerts generated from the feed:")
for r, e in fired:
    print(f"   [{r.severity}] {r.name}")
    print(f"        actor={e['actor']}  → {r.response}")

ACTIONED = 2      # of those alerts, how many led to an action
print(f"\nthe three numbers that matter:")
print(f"   indicators received : {len(FEED)}")
print(f"   rules deployed      : {len(rules)}  ({len(rules)/len(FEED):.0%} of the feed)")
print(f"   alerts fired        : {len(fired)}")
print(f"   alerts actioned     : {ACTIONED}  ({ACTIONED/max(len(fired),1):.0%})")
print("\nThe third number is the one that decides whether the subscription renews.")
