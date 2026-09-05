#!/usr/bin/env python3
"""Parse CyberTravels' booking service to an AST, build the call graph, and split the finding queue on it.

This is the executable half of the `dead-code-ast-reachability` skill. It does
the parsing for real — `ast.parse`, `FunctionDef` for the nodes, `Call` for the
edges — against the sources below, so the buckets it reports are derived rather
than asserted, and changing a line of that source changes the answer.

Standard library only, and deterministic.
"""

import ast
from collections import defaultdict
from pathlib import Path

from cyber_commons_skill_runtime import dot_graph, emit_diagram

# The corpus is the shared CyberTravels tree, parsed from disk rather than
# retyped here. Every skill in this chapter now scans the same repository, so a
# reader meets one system rather than a slightly different one per lesson.
ROOT = Path(__file__).resolve().parents[4]
REPO = ROOT / "cybertravels"
SOURCES = {str(f.relative_to(REPO)): f.read_text()
           for f in sorted(REPO.rglob("*.py"))
           if f.name != "_stubs.py" and f.stat().st_size > 0}

# Findings from the audit stage, each naming the unit it landed in. These are
# the rows of cybertravels/LABELS.md that this stage receives.
FINDINGS = [
    ("F1", "search_bookings",  "CWE-89",  9),
    ("F2", "render_template",  "CWE-95",  8),
    ("F3", "_open_branch",     "CWE-78",  9),
    ("F4", "download_invoice", "CWE-22",  6),
    ("F5", "sync_vendor",      "CWE-295", 5),
    ("F6", "receive",          "CWE-940", 4),
]

ENTRY_DECORATORS = {"route"}


# ------------------------------------------------------------- 1, 2 · the graph
def call_name(node):
    """Resolve a Call to the name being called, or None.

    `f()` is a Name and `obj.f()` is an Attribute. Taking `.attr` for the second
    is deliberately naive — it loses the receiver, so two methods with the same
    name merge — and that errs toward *reachable*, which is the safe direction.
    A cleverer resolver that guesses wrong marks a live function dead.
    """
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


functions, edges, entries, unresolved = {}, defaultdict(set), [], []

for path, src in sorted(SOURCES.items()):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        functions[node.name] = path
        # 3 — an entry point is reachable by definition. A decorated handler has
        # no caller in the source and is called by the framework at import.
        for dec in node.decorator_list:
            name = call_name(dec) if isinstance(dec, ast.Call) else (
                dec.id if isinstance(dec, ast.Name) else
                getattr(dec, "attr", None))
            if name in ENTRY_DECORATORS:
                entries.append(node.name)
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                # 5 — the calls the AST cannot follow. Both shapes the SKILL.md
                # names: a callee fetched by getattr, and a callee looked up in
                # a table. CyberTravels' router is the second — AGENTS[intent]
                # (...) — and it is why the whole agent layer below it is
                # undecided rather than dead.
                if call_name(inner) == "getattr":
                    unresolved.append({"file": path, "why": "getattr"})
                if isinstance(inner.func, ast.Subscript):
                    unresolved.append({"file": path, "why": "dispatch-table"})
                callee = call_name(inner)
                if callee:
                    edges[node.name].add(callee)

# A dispatch table's targets are whatever the table holds. The AST can read the
# table's *values* even though it cannot resolve the lookup, so those names are
# roots of an `unknown` region rather than functions nothing calls.
dispatch_roots = set()
for path, src in sorted(SOURCES.items()):
    if not any(u["file"] == path and u["why"] == "dispatch-table"
               for u in unresolved):
        continue
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Attribute):
            dispatch_roots.add(n.attr)
        elif isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Store):
            dispatch_roots.add(n.id)

entries = sorted(set(entries))
edge_count = sum(len(v & set(functions)) for v in edges.values())

print(f"ast: {len(functions)} functions, {edge_count} resolved call edges, "
      f"{len(entries)} entry point(s)")
for e in entries:
    print(f"   entry  {e}  ({functions[e]})")
for u in unresolved:
    print(f"   UNRESOLVED  {u['file']}: {u['why']}(...)() - the callee is a "
          f"runtime value")
print()

# --------------------------------------------------------- 4 · walk from entries
reachable, stack = set(), list(entries)
while stack:
    fn = stack.pop()
    if fn in reachable or fn not in functions:
        continue
    reachable.add(fn)
    stack.extend(sorted(edges[fn]))

opaque_files = {u["file"] for u in unresolved}

# Everything reachable from a dispatch root is undecided, not dead: the table
# may hold it, and the AST cannot say whether the lookup ever selects it.
undecided, stack = set(), [r for r in dispatch_roots if r in functions]
while stack:
    fn = stack.pop()
    if fn in undecided or fn not in functions:
        continue
    undecided.add(fn)
    stack.extend(sorted(edges[fn]))


def bucket(fn):
    if fn in reachable:
        return "reachable"
    if fn in undecided or functions[fn] in opaque_files:
        return "unknown"
    return "unreachable"


buckets = defaultdict(list)
for fn in sorted(functions):
    buckets[bucket(fn)].append(fn)

print("the three buckets, and the third is the honest one")
for b in ("reachable", "unreachable", "unknown"):
    print(f"   {b:<12}{len(buckets[b]):>2}  {', '.join(buckets[b]) or '-'}")
print()
print("The agent layer is NOT dead. CyberTravels' router dispatches through")
print("AGENTS[intent](message, session) - a table lookup - so the AST cannot")
print("say which handler a request selects, and everything reachable from the")
print("table's values is undecided. Filing that as unreachable would drop the")
print("whole tool layer, including the refund path.")
print()

# ------------------------------------------------------- 6 · classify the queue
report = {"graph": {"functions": len(functions), "edges": edge_count,
                    "entry_points": entries},
          "buckets": {b: len(buckets[b]) for b in
                      ("reachable", "unreachable", "unknown")},
          "unresolved_calls": unresolved, "findings": []}

print("the queue, split on the graph")
print(f"   {'':<4}{'unit':<20}{'cwe':<9}{'sev':<5}{'bucket':<13}"
      f"true about code / risk")
kept = 0
for fid, unit, cwe, sev in FINDINGS:
    b = bucket(unit)
    risk = b != "unreachable"
    kept += b == "reachable"
    print(f"   {fid:<4}{unit:<20}{cwe:<9}{sev:<5}{b:<13}"
          f"{'yes':<5}/ {'yes' if risk else 'NO'}")
    report["findings"].append({"id": fid, "unit": unit, "bucket": b,
                               "true_about_code": True, "true_about_risk": risk})
report["queue"] = {"before": len(FINDINGS), "after": kept}
print()

dead = [f for f in report["findings"] if f["bucket"] == "unreachable"]
unk = [f for f in report["findings"] if f["bucket"] == "unknown"]
print()
print(f"Every one of the {len(FINDINGS)} is a true positive about the code - a")
print(f"reviewer who opens the file agrees with all of them. {len(dead)} are false")
print(f"positives about the RISK, because nothing in the tree reaches them.")
print()
print(f"queue: {report['queue']['before']} findings -> "
      f"{report['queue']['after']} reachable, {len(dead)} unreachable, "
      f"{len(unk)} undecided.")
print()
print("Read the middle column rather than the total. Only the unreachable ones")
print("are a deletion, and that resolution is the one that cannot rot: a")
print("suppression is keyed to a file, a line and a rule, and none of those")
print("change when somebody wires the function back up.")
print()
print("The undecided ones are work, not a result. Three of them sit behind the")
print("router's table - including the command injection in the Coding Agent and")
print("the traversal on the File System Agent's invoice path. A two-bucket")
print("pipeline files all three as unreachable and reports the queue clean.")

# The graph, in a language a renderer reads. The buckets are what the reader
# needs to see at a glance and a three-colour picture carries that faster than
# the table above does. scripts/render_diagrams.py turns this into the SVG on
# the lesson page, with real Graphviz.
KIND = {"reachable": "unit", "unreachable": "dead", "unknown": "unknown"}
nodes = {fn: {"label": fn, "kind": "entry" if fn in entries else KIND[bucket(fn)]}
         for fn in functions}
graph_edges = sorted((src, dst, "")
                     for src, dsts in edges.items() for dst in dsts
                     if src in functions and dst in functions)
clusters = defaultdict(list)
for fn, path in functions.items():
    clusters[path].append(fn)

print()
emit_diagram("b2-5-call-graph",
             dot=dot_graph("call_graph", nodes, graph_edges,
                           clusters=dict(clusters)))
print()
print("Red is an entry point, grey is reached, dim is dead, blue is undecided.")
print("Almost everything below the router is blue: the table lookup is what")
print("the AST cannot follow, not a property of the functions themselves.")

assert report["buckets"]["unknown"] > report["buckets"]["reachable"], \
    "a dispatch table makes most of this tree undecided; if it does not, the " \
    "lookup was resolved and the analysis is claiming more than it can know"
assert any(u["why"] == "dispatch-table" for u in unresolved), \
    "the router's table lookup must be recorded, or the bucket is unauditable"
assert report["buckets"]["unreachable"], "nothing is genuinely uncalled - check the roots"
assert report["queue"]["after"] < report["queue"]["before"]
