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

# The corpus. Small enough to read, and it contains all three of the shapes the
# procedure has to tell apart: a plain call chain, a function nothing calls, and
# a module whose dispatch the AST cannot resolve.
SOURCES = {
    "api/bookings.py": '''
@route("/bookings")
def search_bookings(request):
    return render(_query(request.args["q"]))

def _query(q):
    return DB.execute("SELECT * FROM bookings WHERE ref LIKE '%" + q + "%'")

def legacy_export(path):
    os.system("tar czf /tmp/out.tgz " + path)

def audit_line(msg):
    LOG.write(msg + "\\n")
''',
    "api/itinerary.py": '''
@route("/itinerary")
def render_itinerary(request):
    return eval(request.args["template"])

def debug_dump(name):
    return open("/var/dumps/" + name).read()
''',
    "jobs/runner.py": '''
def run_job(name, arg):
    handler = getattr(HANDLERS, name)
    return handler(arg)

def nightly_reconcile():
    return _settle()

def _settle():
    return DB.execute("UPDATE ledger SET settled = 1")
''',
}

# Findings from the audit stage, each naming the unit it landed in.
FINDINGS = [
    ("F1", "_query",            "CWE-89",  9),
    ("F2", "render_itinerary",  "CWE-95",  8),
    ("F3", "legacy_export",     "CWE-78",  9),
    ("F4", "debug_dump",        "CWE-22",  6),
    ("F5", "audit_line",        "CWE-117", 3),
    ("F6", "_settle",           "CWE-89",  7),
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
                # 5 — the call the AST cannot follow. Record it against the
                # file: every unreached function in that module becomes
                # `unknown` rather than `unreachable`.
                if call_name(inner) == "getattr":
                    unresolved.append({"file": path, "why": "getattr"})
                callee = call_name(inner)
                if callee:
                    edges[node.name].add(callee)

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


def bucket(fn):
    if fn in reachable:
        return "reachable"
    return "unknown" if functions[fn] in opaque_files else "unreachable"


buckets = defaultdict(list)
for fn in sorted(functions):
    buckets[bucket(fn)].append(fn)

print("the three buckets, and the third is the honest one")
for b in ("reachable", "unreachable", "unknown"):
    print(f"   {b:<12}{len(buckets[b]):>2}  {', '.join(buckets[b]) or '-'}")
print()
print("nightly_reconcile and _settle are NOT dead. They are in a module whose")
print("dispatch is getattr(HANDLERS, name)(), so the AST cannot say who calls")
print("them. Filing that as unreachable is how a pipeline drops real bugs.")
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
print(f"Every one of the {len(FINDINGS)} is a true positive about the code - a")
print(f"reviewer who opens the file agrees with all of them. {len(dead)} are false")
print(f"positives about the RISK, because the graph says nothing reaches them.")
print(f"Those belong in a deletion list, not a triage queue: the code is gone")
print(f"and the finding goes with it, which is the only resolution that cannot")
print(f"rot the way a suppression does.")
print()
print(f"queue: {report['queue']['before']} findings -> "
      f"{report['queue']['after']} reachable, {len(dead)} to delete, "
      f"{len(unk)} unresolved.")
print("The last number is work, not a result. A two-bucket pipeline reports it")
print("as zero and calls the queue clean.")

assert report["buckets"]["unknown"] == 3, "every unreached function in the getattr module is undecided, not dead"
assert report["buckets"]["unreachable"] == 3, "three functions have no caller"
assert unresolved, "the unresolved call must be recorded, or the bucket is unauditable"
assert report["queue"]["after"] < report["queue"]["before"]
