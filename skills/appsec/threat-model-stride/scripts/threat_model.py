#!/usr/bin/env python3
"""Derive a STRIDE threat model and a trust-boundary diagram from five inputs.

This is the executable half of the `threat-model-stride` skill. The SKILL.md
next to it is the procedure a model follows; this is the deterministic part it
calls, so the scoring is reproducible and two runs can be diffed.

    python3 threat_model.py     # the synthetic CyberTravels estate, then the
                                # same estate hardened, then the diff

There is no CLI. The module prints its demonstration at import, because it is
embedded into a notebook cell where `__name__` is `__main__` and `sys.argv`
belongs to the kernel — an `if __name__ == "__main__"` block guarded on
arguments ran argparse against a Kaggle kernel's argv and failed the notebook.
Call `model()`, `boundaries()` and `diagram()` directly for the JSON contract.

Standard library only, so it runs on a Kaggle kernel with the internet off.
"""
from __future__ import annotations

import json
from collections import defaultdict

# ---------------------------------------------------------------- the inputs
# Synthetic, and deliberately so: every value below stands in for something a
# real estate already holds, and the point of the lesson is that all five are
# read rather than just the first.

ARCHITECTURE = {
    "components": {"src/api": 0, "src/util": 1, "src/data": 2},   # trust level
    "entry_points": [
        {"unit": "get_booking", "component": "src/api", "auth": "session"},
        {"unit": "upload_voucher", "component": "src/api", "auth": "session"},
        {"unit": "health", "component": "src/api", "auth": "none"},
    ],
    "flows": [("get_booking", "load_booking"), ("get_booking", "render"),
              ("upload_voucher", "store"), ("load_booking", "execute"),
              ("store", "open")],
    "sinks": [
        {"unit": "load_booking", "component": "src/data",
         "resource": "bookings_db", "sink": "execute"},
        {"unit": "store", "component": "src/data",
         "resource": "voucher_bucket", "sink": "open"},
    ],
    "assets": {"bookings_db": {"data": ["customer", "financial"], "value": 5},
               "voucher_bucket": {"data": ["documents"], "value": 3}},
}

CSPM = [
    {"resource": "voucher_bucket", "finding": "bucket policy allows public read",
     "severity": 4},
]

IAM = {"src/api": {"role": "cybertravels-api",
                   "assumable_by": ["ci-deploy-role", "*"],
                   "mfa_required": False}}

NETWORK = {"src/api": {"exposed": "internet", "waf": False,
                       "egress_default_deny": False,
                       "egress_allowed": ["0.0.0.0/0"]}}

ENTITLEMENTS = {"src/api": ["db:select", "db:update",
                            "s3:GetObject", "s3:PutObject"]}

HARDENED = {
    "cspm": [],
    "iam": {"src/api": {"role": "cybertravels-api",
                        "assumable_by": ["ci-deploy-role"], "mfa_required": True}},
    "network": {"src/api": {"exposed": "vpc-only", "waf": True,
                            "egress_default_deny": True,
                            "egress_allowed": ["bookings-db.prod:5432"]}},
    "entitlements": {"src/api": ["db:select", "s3:GetObject"]},
}

# The six questions. Each one applies to a path structurally — an agent that
# calls a sink can always be spoofed, can always repudiate, can always disclose.
# What the evidence changes is the SCORE, not whether the row exists. A model
# that deletes rows when the estate is hardened teaches that hardening removes
# threats; it does not, it removes severity, and the row is what you re-check
# after the next terraform change.
STRIDE = [
    ("S", "Spoofing", "iam",
     lambda c: (2, "the running role is assumable by *")
     if "*" in c["iam"].get("assumable_by", []) else
     (0, "role assumable only by named principals")),
    ("T", "Tampering", "architecture",
     lambda c: (2, "an unauthenticated entry point reaches this sink")
     if c["entry"]["auth"] == "none" else
     (0, "entry point requires a session")),
    ("R", "Repudiation", "iam",
     lambda c: (1, "no MFA on the assumable role, so the actor is not established")
     if not c["iam"].get("mfa_required", False) else
     (0, "MFA required to assume the role")),
    ("I", "Information disclosure", "cspm",
     lambda c: (c["cspm_severity"],
                "a live CSPM finding on the resource this path reaches")
     if c["cspm_severity"] else (0, "no open CSPM finding on the resource")),
    ("D", "Denial of service", "network",
     lambda c: (1, "internet-facing with no WAF in front of it")
     if c["net"].get("exposed") == "internet" and not c["net"].get("waf") else
     (0, "not directly reachable, or a WAF is in front")),
    ("E", "Elevation of privilege", "entitlements",
     lambda c: (1, "the identity holds write, not just read")
     if any(e in c["entitlements"] for e in ("db:update", "s3:PutObject")) else
     (0, "the identity is read-only on this resource")),
]


def reachable(entry, flows):
    adj = defaultdict(list)
    for a, b in flows:
        adj[a].append(b)
    seen, stack = set(), [entry]
    while stack:
        for nxt in adj[stack.pop()]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def model(architecture, cspm, iam, network, entitlements):
    """Step 2 and 3 of the procedure: walk, question, score from evidence."""
    by_resource = defaultdict(int)
    for f in cspm:
        by_resource[f["resource"]] += f["severity"]

    threats, n = [], 0
    for entry in architecture["entry_points"]:
        reach = reachable(entry["unit"], architecture["flows"])
        comp = entry["component"]
        for sink in architecture["sinks"]:
            if sink["unit"] not in reach:
                continue
            asset = architecture["assets"][sink["resource"]]
            ctx = {"entry": entry, "sink": sink, "iam": iam.get(comp, {}),
                   "net": network.get(comp, {}),
                   "entitlements": entitlements.get(comp, []),
                   "cspm_severity": by_resource[sink["resource"]]}
            exposure = 2 if ctx["net"].get("exposed") == "internet" else -3
            egress = 0 if ctx["net"].get("egress_default_deny", True) else 2
            for letter, name, source, assess in STRIDE:
                bump, why = assess(ctx)
                n += 1
                score = max(1, asset["value"] + bump + exposure + egress)
                threats.append({
                    "id": f"T-{n:02d}", "stride": letter, "category": name,
                    "entry": entry["unit"], "sink": sink["unit"],
                    "asset": sink["resource"], "score": score,
                    "mitigated": bump == 0,
                    "reasons": [why]
                               + (["internet-facing"] if exposure > 0 else ["vpc-only"])
                               + (["egress open"] if egress else ["egress default-deny"]),
                    "evidence": {"source": source, "detail": why},
                })
    return sorted(threats, key=lambda t: (-t["score"], t["stride"], t["id"]))


def boundaries(architecture):
    """Step 4: an edge from a lower trust level to a higher one."""
    comp = {}
    for e in architecture["entry_points"]:
        comp[e["unit"]] = e["component"]
    for s in architecture["sinks"]:
        comp[s["unit"]] = s["component"]
    lv = architecture["components"]
    out = []
    for a, b in architecture["flows"]:
        ca, cb = comp.get(a), comp.get(b)
        if ca and cb and lv.get(ca, 0) < lv.get(cb, 0):
            out.append({"from": a, "to": b, "trust": f"{lv[ca]}->{lv[cb]}"})
    return out


def diagram(architecture, bnds):
    """Step 4: mermaid, because it renders in the notebook without a library."""
    lines = ["flowchart LR"]
    for comp, level in sorted(architecture["components"].items()):
        label = comp.replace("/", "_")
        lines.append(f'  subgraph {label}["{comp} · trust {level}"]')
        members = [e["unit"] for e in architecture["entry_points"]
                   if e["component"] == comp]
        members += [s["unit"] for s in architecture["sinks"]
                    if s["component"] == comp]
        for m in sorted(set(members)) or ["·"]:
            lines.append(f"    {m}")
        lines.append("  end")
    crossing = {(b["from"], b["to"]) for b in bnds}
    for a, b in architecture["flows"]:
        lines.append(f"  {a} ==>|BOUNDARY| {b}" if (a, b) in crossing
                     else f"  {a} --> {b}")
    return "\n".join(lines)


def diff(before, after):
    """Step 5: arrivals AND escalations."""
    key = lambda t: (t["stride"], t["entry"], t["sink"])
    prev = {key(t): t["score"] for t in before}
    new = [t["id"] for t in after if key(t) not in prev]
    esc = [{"id": t["id"], "from": prev[key(t)], "to": t["score"]}
           for t in after if key(t) in prev and t["score"] > prev[key(t)]]
    return {"new": new, "escalated": esc}


# ---------------------------------------------------- the demonstration
# What the lesson runs, at module level, so the notebook and a terminal
# both print the same thing. `main()` below is still the CLI, and only
# fires when arguments are given.

threats = model(ARCHITECTURE, cspm=CSPM, iam=IAM, network=NETWORK,
                 entitlements=ENTITLEMENTS)
bnds = boundaries(ARCHITECTURE)

print(f"{'id':6s}{'':2s}{'entry':16s}{'sink':14s}{'score':>6}  why")
print("-" * 92)
for t in threats:
    print(f"{t['id']:6s}{t['stride']:2s}{t['entry']:16s}{t['sink']:14s}"
          f"{t['score']:>6}  {t['reasons'][0]}")

print(f"\n{len(threats)} threats across "
      f"{len({t['stride'] for t in threats})} STRIDE categories")
print(f"{len(bnds)} trust-boundary crossing(s):")
for b in bnds:
    print(f"   {b['from']} -> {b['to']}   ({b['trust']})")
assert len({t["stride"] for t in threats}) == 6

print(diagram(ARCHITECTURE, bnds))

hard = model(ARCHITECTURE, cspm=HARDENED["cspm"], iam=HARDENED["iam"],
              network=HARDENED["network"],
              entitlements=HARDENED["entitlements"])
by_id = {(t["stride"], t["entry"], t["sink"]): t["score"] for t in hard}

print(f"{'':2s}{'entry -> sink':34s}{'deployed':>10}{'hardened':>10}")
print("-" * 58)
for t in threats[:6]:
    k = (t["stride"], t["entry"], t["sink"])
    print(f"{t['stride']:2s}{t['entry'] + ' -> ' + t['sink']:34s}"
          f"{t['score']:>10}{by_id[k]:>10}")

print(f"\nthreat rows: {len(threats)} -> {len(hard)}   (unchanged)")
print(f"max severity: {max(t['score'] for t in threats)} -> "
      f"{max(t['score'] for t in hard)}")
print()
print("The rows do not disappear. Hardening removes severity, not threats -")
print("and the row is what you re-check after the next terraform change.")
assert len(hard) == len(threats)
assert max(t["score"] for t in hard) < max(t["score"] for t in threats)
