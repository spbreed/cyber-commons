#!/usr/bin/env python3
"""Scan an agent run record for sensitive content it read legitimately, and retain per field rather than per record.

This is the executable half of the `agent-telemetry-retention` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time, hashlib
from dataclasses import dataclass, field

@dataclass
class Step:
    n: int; tool: str; target: str; verifier: str; ok: bool
    prompt: str = ""; result: str = ""

RUN = [
 Step(1, "read_file", "/work/repo/billing.py", "n/a", True,
      prompt="Investigate finding SEC-4471 in billing.py",
      result="def charge(card_number, amount):  # card_number = 4111111111111111"),
 Step(2, "search_code", "charge(", "n/a", True,
      prompt="find callers of charge()",
      result="api/checkout.py:88 charge(user.card, total)"),
 Step(3, "write_file", "/work/repo/billing.py", "tests pass", True,
      prompt="apply the fix", result="patch applied"),
]
def render(steps, fields):
    out = []
    for s in steps:
        row = {k: getattr(s, k) for k in fields}
        out.append(row)
    return out

print("full record (everything the harness saw):")
for r in render(RUN, ["n", "tool", "target", "verifier", "ok", "prompt", "result"]):
    print("   ", r)

import re
SENSITIVE = {
 "payment card": re.compile(r"\b4[0-9]{12}(?:[0-9]{3})?\b"),
 "email":        re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
 "aws key":      re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}
def scan_record(steps):
    hits = []
    for s in steps:
        for field in ("prompt", "result"):
            text = getattr(s, field)
            for name, pat in SENSITIVE.items():
                if pat.search(text):
                    hits.append((s.n, field, name))
    return hits

hits = scan_record(RUN)
print("sensitive content found in the trace:")
for n, field, kind in hits:
    print(f"   step {n}  {field:8s} {kind}")
print("\nNobody put a card number in the trace deliberately. The agent read a")
print("source file, and the file contained a test fixture with a real-shaped PAN.")
print("The trace is now in scope for PCI, and it is in your SIEM for 400 days.")

RETENTION = {
 "n":        (400, "low",  "cheap, high forensic value"),
 "tool":     (400, "low",  "cheap, high forensic value"),
 "target":   (400, "low",  "path only, no contents"),
 "verifier": (400, "low",  "what the harness believed — the key forensic field"),
 "ok":       (400, "low",  ""),
 "prompt":   (30,  "high", "may contain anything the task included"),
 "result":   (7,   "high", "tool output — the highest-risk field"),
}
print(f"{'field':10s}{'days':>6}{'sensitivity':>13}  rationale")
print("-" * 74)
for f, (days, sens, why) in RETENTION.items():
    print(f"{f:10s}{days:>6}{sens:>13}  {why}")

def age_record(steps, age_days):
    """What survives after N days."""
    keep = [f for f, (d, _, _) in RETENTION.items() if d >= age_days]
    out = []
    for s in steps:
        row = {k: getattr(s, k) for k in keep}
        for f in ("prompt", "result"):
            if f not in keep and getattr(s, f):
                row[f + "_sha256"] = hashlib.sha256(
                    getattr(s, f).encode()).hexdigest()[:16]
        out.append(row)
    return out

for age in (1, 14, 90):
    aged = age_record(RUN, age)
    print(f"\nafter {age} days — step 1 record:")
    print("   ", aged[0])

# Verify: the aged record is still forensically useful and no longer sensitive.
aged = age_record(RUN, 90)
class Fake:
    def __init__(self, d): self.__dict__.update(d); self.prompt = d.get("prompt",""); self.result = d.get("result","")
remaining = scan_record([Fake(r) for r in aged])
print(f"sensitive content after 90 days: {remaining or 'none'}")
assert not remaining

can_answer = all("verifier" in r and "tool" in r and "target" in r for r in aged)
print(f"can still answer 'what did it do and what did the harness believe?': {can_answer}")
assert can_answer
print("\nThe hash is retained, so if the original is recovered from a backup you")
print("can still prove it is the same content the agent saw.")
