#!/usr/bin/env python3
"""Find personal data nobody placed in an agent trace deliberately, and run an erasure request through every system that holds it.

This is the executable half of the `trace-personal-data-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import re, hashlib
from dataclasses import dataclass, field

@dataclass
class Step:
    n: int; tool: str; target: str; result: str

RUN = [
 Step(1, "read_ticket", "SUP-4471",
      "Customer J. Okonkwo (dana.okonkwo@example.com, acct 8812) reports a "
      "double charge on card 4111111111111111."),
 Step(2, "search_orders", "acct=8812",
      "3 orders found for account 8812, total GBP 412.90"),
 Step(3, "post_reply", "SUP-4471", "Refund issued for the duplicate charge."),
]
DETECTORS = {
 "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
 "payment card": re.compile(r"\b4[0-9]{12}(?:[0-9]{3})?\b"),
 "account number": re.compile(r"\bacct \d{4}\b"),
 "name": re.compile(r"\b[A-Z]\. [A-Z][a-z]+\b"),
}
found = []
for s in RUN:
    for kind, pat in DETECTORS.items():
        for m in pat.finditer(s.result):
            found.append((s.n, kind, m.group(0)))
print("personal data present in the agent trace:")
for n, kind, val in found:
    print(f"   step {n}  {kind:16s}{val}")
print(f"\n{len(found)} items. Nobody put them there deliberately — the agent read")
print("a support ticket, which is exactly what it was asked to do.")

SYSTEMS = {
 "primary CRM":        {"has_index": True,  "retention_days": 2555},
 "data warehouse":     {"has_index": True,  "retention_days": 1095},
 "agent traces":       {"has_index": False, "retention_days": 400},
 "eval corpus":        {"has_index": False, "retention_days": 9999},
 "fine-tuning set":    {"has_index": False, "retention_days": 9999},
 "backups":            {"has_index": True,  "retention_days": 90},
}
SUBJECT = "dana.okonkwo@example.com"

print(f"erasure request for {SUBJECT}\n")
print(f"{'system':22s}{'can locate?':>13}{'retention (d)':>15}  outcome")
print("-" * 76)
unreachable = []
for name, s in SYSTEMS.items():
    if s["has_index"]:
        outcome = "erased"
    else:
        outcome = "CANNOT LOCATE — request cannot be completed"
        unreachable.append(name)
    print(f"{name:22s}{str(s['has_index']):>13}{s['retention_days']:>15}  {outcome}")
print(f"\n{len(unreachable)} system(s) where the request fails: {unreachable}")
print("The response to the data subject says 'erased'. It is not true in three")
print("systems, two of which retain indefinitely.")
assert unreachable

def content_hash(text): return hashlib.sha256(text.encode()).hexdigest()[:16]

def index_trace(run, detectors):
    """A subject index: which steps contain data about whom."""
    idx = {}
    for s in run:
        for kind, pat in detectors.items():
            for m in pat.finditer(s.result):
                subj = m.group(0)
                idx.setdefault(subj, []).append(
                    {"step": s.n, "kind": kind, "hash": content_hash(s.result)})
    return idx

IDX = index_trace(RUN, DETECTORS)
print("subject index built from the trace:")
for subj, entries in IDX.items():
    print(f"   {subj:36s}{len(entries)} occurrence(s) in steps "
          f"{sorted({e['step'] for e in entries})}")

def erase(run, idx, subject):
    steps = sorted({e["step"] for e in idx.get(subject, [])})
    out = []
    for s in run:
        if s.n in steps:
            out.append(Step(s.n, s.tool, s.target,
                            f"[erased on request; original sha256={content_hash(s.result)}]"))
        else:
            out.append(s)
    return out, steps

erased, touched = erase(RUN, IDX, SUBJECT)
print(f"\nerasure for {SUBJECT}: steps {touched}")
for s in erased:
    print(f"   step {s.n}: {s.result[:66]}")

remaining = [(n, k, v) for s in erased for k, pat in DETECTORS.items()
             for m in pat.finditer(s.result) for n, v in [(s.n, m.group(0))]]
print(f"\npersonal data remaining in the trace: {remaining or 'none'}")
assert not remaining
print("The hash is retained, so if the original surfaces in a backup you can")
print("still prove it is the same content — which is what makes the erasure auditable.")

# Per-field retention: keep the forensically useful parts, drop the rest early.
RETENTION = {"n": 400, "tool": 400, "target": 400, "result": 7}
print(f"{'field':10s}{'days':>6}  rationale")
print("-" * 62)
for f, d in RETENTION.items():
    why = ("tool output — highest sensitivity, lowest retention" if f == "result"
           else "cheap, high forensic value, no personal data")
    print(f"{f:10s}{d:>6}  {why}")
print("\nAt 7 days the result field is gone and the trace is still forensically")
print("useful: you know what the agent did, to what, and when.")
