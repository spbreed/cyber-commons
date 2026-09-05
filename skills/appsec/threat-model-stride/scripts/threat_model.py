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

import ast
import json

from cyber_commons_skill_runtime import (
    dot_graph, emit_diagram, puml_sequence)
from collections import defaultdict

# ---------------------------------------------------------------- the inputs
# Synthetic, and deliberately so: every value below stands in for something a
# real estate already holds, and the point of the lesson is that all five are
# read rather than just the first.

# ------------------------------------------------- the architecture, derived
# The recon stage used to be a lesson of its own and this file retyped its
# result. Retyping is the failure this lesson warns about: a threat model that
# describes the system as somebody once described it, rather than as the code
# is now. So the minimum of the recon stage lives here — parse the sources,
# take the units nothing calls as entry points, take a call into a dangerous
# builtin as a sink — and the model below is built from what that returns.

SOURCES = {
 "src/api/bookings.py": '''
def get_booking(request):
    """HTTP GET /bookings/<ref> - request.args is traveller-controlled."""
    return render(load_booking(request.args["ref"], request.args["owner"]))

def upload_voucher(request):
    """HTTP POST /vouchers - the multipart body is traveller-controlled."""
    return store(request.files["doc"], request.args["name"])

def health(request):
    """HTTP GET /health - no session required."""
    return "ok"
''',
 "src/data/reports.py": '''
def load_booking(ref, owner):
    return DB.execute("SELECT * FROM bookings WHERE ref=" + ref)
''',
 "src/data/docs.py": '''
def store(blob, name):
    open("/srv/vouchers/" + name, "wb").write(blob)
''',
 "src/util/render.py": '''
def render(rows):
    return "\\n".join(str(r) for r in rows)
''',
}

TRUST = {"src/api": 0, "src/util": 1, "src/data": 2}   # 0 = the untrusted edge
DANGEROUS = {"execute": "bookings_db", "open": "voucher_bucket"}
UNAUTHENTICATED = {"health"}          # what the router leaves open
ASSETS = {"bookings_db": {"data": ["customer", "financial"], "value": 5},
          "voucher_bucket": {"data": ["documents"], "value": 3}}


def units_of(src, path):
    """Semantic units and what each one calls. Not lines, not files."""
    out = []
    for fn in [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)]:
        calls = sorted({(c.func.id if isinstance(c.func, ast.Name)
                         else getattr(c.func, "attr", ""))
                        for c in ast.walk(fn) if isinstance(c, ast.Call)} - {""})
        out.append({"name": fn.name, "component": path.rsplit("/", 1)[0],
                    "calls": calls})
    return out


def derive(sources):
    """The map: entry points, flows, sinks, and the trust level per component.

    An entry point is a unit nothing in the repository calls — which is what
    makes it reachable from outside. Deriving it beats declaring it, because
    adding a function changes the answer and nobody has to remember to.
    """
    units = [u for p, s in sorted(sources.items()) for u in units_of(s, p)]
    names = {u["name"] for u in units}
    called = {c for u in units for c in u["calls"] if c in names}
    entries = [{"unit": u["name"], "component": u["component"],
                "auth": "none" if u["name"] in UNAUTHENTICATED else "session"}
               for u in units if u["name"] not in called]
    flows = sorted({(u["name"], c) for u in units for c in u["calls"]
                    if c in names or c in DANGEROUS})
    sinks = [{"unit": u["name"], "component": u["component"],
              "resource": DANGEROUS[c], "sink": c}
             for u in units for c in u["calls"] if c in DANGEROUS]
    return {"components": TRUST, "entry_points": sorted(entries, key=lambda e: e["unit"]),
            "flows": flows, "sinks": sorted(sinks, key=lambda s: s["unit"]),
            "assets": ASSETS}


ARCHITECTURE = derive(SOURCES)

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


def dot_diagram(architecture, bnds):
    """Step 4, as Graphviz: the same graph, rendered by a real layout engine.

    Mermaid renders in a notebook and lays nothing out well past a dozen nodes.
    DOT is the format the tools a security team already runs speak, and
    `scripts/render_diagrams.py` turns this into the SVG on the lesson page
    with the actual `dot` binary.
    """
    comp = {}
    for e in architecture["entry_points"]:
        comp[e["unit"]] = e["component"]
    for s in architecture["sinks"]:
        comp[s["unit"]] = s["component"]
    entry_units = {e["unit"] for e in architecture["entry_points"]}
    sink_units = {s["unit"] for s in architecture["sinks"]}

    nodes, clusters = {}, {}
    for unit, component in comp.items():
        kind = "entry" if unit in entry_units else (
            "sink" if unit in sink_units else "unit")
        nodes[unit] = {"label": unit, "kind": kind}
        level = architecture["components"].get(component, 0)
        clusters.setdefault(f"{component} · trust {level}", []).append(unit)

    crossing = {(b["from"], b["to"]): b["trust"] for b in bnds}
    edges = [(a, b, crossing.get((a, b), ""))
             for a, b in architecture["flows"] if a in nodes and b in nodes]
    return dot_graph("threat_model", nodes, edges, clusters=clusters,
                     legend_labels={"entry": "entry point",
                                    "sink": "dangerous sink",
                                    "unit": "neither"})


def puml_diagram(architecture, bnds):
    """The same finding as a sequence, which is the shape a boundary crossing
    actually has: a request moving between components over time.

    A graph says which edges cross a boundary. A sequence says *when*, and the
    reader can follow one request through it, which is what a threat model is
    usually being read for.
    """
    comp = {}
    for e in architecture["entry_points"]:
        comp[e["unit"]] = e["component"]
    for s in architecture["sinks"]:
        comp[s["unit"]] = s["component"]
    order, seen = [], set()
    for a, b in architecture["flows"]:
        for u in (a, b):
            if u in comp and u not in seen:
                seen.add(u)
                order.append(u)
    entry_units = {e["unit"] for e in architecture["entry_points"]}
    sink_units = {s["unit"] for s in architecture["sinks"]}
    participants = [
        (u.replace(".", "_"), f"{u}\\n{comp[u]}",
         "entry" if u in entry_units else "sink" if u in sink_units else "unit")
        for u in order]
    crossing = {(b["from"], b["to"]): b["trust"] for b in bnds}
    messages = []
    for a, b in architecture["flows"]:
        if a not in comp or b not in comp:
            continue
        t = crossing.get((a, b))
        messages.append((a.replace(".", "_"), b.replace(".", "_"),
                         f"TRUST BOUNDARY {t}" if t else "call",
                         "danger" if t else ""))
    notes = [(order[0].replace(".", "_"),
              "every threat in the table\nlives on a red arrow")] if order else []
    return puml_sequence("CyberTravels — one request, and where it crosses",
                         participants, messages, notes=notes)


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

# The same graph twice more, in the two languages a real renderer reads. DOT
# for the structure, PlantUML for the sequence — a graph says which edges cross
# a boundary and a sequence says when, and the second is what somebody reading
# a threat model is usually after.
print()
emit_diagram("b2-2-trust-boundaries", dot=dot_diagram(ARCHITECTURE, bnds))
print()
emit_diagram("b2-2-request-sequence", puml=puml_diagram(ARCHITECTURE, bnds))
print()

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
