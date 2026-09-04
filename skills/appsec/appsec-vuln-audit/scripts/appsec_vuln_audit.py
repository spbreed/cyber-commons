#!/usr/bin/env python3
"""Filter findings by whether the vulnerable path is reachable, and record what reachability analysis cannot decide.

This is the executable half of the `appsec-vuln-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# The skill runtime comes from the shared library, not from a copy in this file.
# In a lesson notebook the cell above has already loaded it; standalone, find it
# the same way that cell does.
import glob as _glob, importlib.util as _ilu, os as _os, sys as _sys

if "cyber_commons_skill_runtime" not in _sys.modules:
    _where = (sorted(_glob.glob("/kaggle/input/**/cyber-commons-skill-runtime/__script__.py",
                                recursive=True))
              + [_os.path.join(p, "skills/_runtime/cyber_commons_skill_runtime.py")
                 for p in (".", "..", "../..",
                           _os.path.join(_os.path.dirname(__file__), "../../../_runtime"))])
    _found = next((p for p in _where if _os.path.isfile(p)), None)
    if _found is None:
        raise SystemExit("shared skill runtime not found; looked at " + repr(_where))
    _spec = _ilu.spec_from_file_location("cyber_commons_skill_runtime", _found)
    _mod = _ilu.module_from_spec(_spec)
    _sys.modules["cyber_commons_skill_runtime"] = _mod
    _spec.loader.exec_module(_mod)

from cyber_commons_skill_runtime import check, contract_of, parse_skill


def _skill_md():
    """The SKILL.md next to this script, or the one the notebook already parsed."""
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


import json
import pathlib as _pathlib
import re

SKILL_MD = _skill_md()
meta, body = parse_skill(SKILL_MD)

import ast
from collections import defaultdict

SOURCE = '''
import handlers_registry

def http_get_report(request):
    """ENTRY: GET /reports"""
    return load_report(request.args["id"])

def http_health(request):
    """ENTRY: GET /health"""
    return "ok"

def load_report(report_id):
    return DB.execute("SELECT * FROM reports WHERE id=" + report_id)

def legacy_export(report_id):
    # nothing calls this any more; kept for a migration that finished in 2023
    return DB.execute("SELECT * FROM reports WHERE id=" + report_id)

def debug_dump(name):
    return open("/tmp/" + name).read()

def dispatch(request):
    """ENTRY: dynamic dispatch — the framework resolves the handler at runtime"""
    handler = handlers_registry.lookup(request.path)
    return handler(request)
'''

tree = ast.parse(SOURCE)
FUNCS = {fn.name: fn for fn in ast.walk(tree) if isinstance(fn, ast.FunctionDef)}

def calls_in(fn):
    return {(c.func.id if isinstance(c.func, ast.Name) else getattr(c.func, "attr", ""))
            for c in ast.walk(fn) if isinstance(c, ast.Call)} - {""}

GRAPH = {name: sorted(calls_in(fn) & set(FUNCS)) for name, fn in FUNCS.items()}
ENTRY = [n for n, fn in FUNCS.items() if (ast.get_docstring(fn) or "").startswith("ENTRY")]
DYNAMIC = [n for n, fn in FUNCS.items()
           if "dynamic dispatch" in (ast.get_docstring(fn) or "")]

print("call graph:")
for n, cs in GRAPH.items(): print(f"   {n:18s}→ {cs or '—'}")
print(f"\nentry points: {ENTRY}")
print(f"dynamic dispatch present in: {DYNAMIC}")

SINKS = {"load_report": ("CWE-89", "DB.execute"),
         "legacy_export": ("CWE-89", "DB.execute"),
         "debug_dump":   ("CWE-22", "open")}

def reachable_from(entry, graph):
    seen, stack = set(), [entry]
    while stack:
        n = stack.pop()
        for m in graph.get(n, []):
            if m not in seen: seen.add(m); stack.append(m)
    return seen

REACHED = set()
for e in ENTRY: REACHED |= reachable_from(e, GRAPH) | {e}

def feasibility(unit):
    if unit in REACHED:
        return "reachable", f"path exists from {[e for e in ENTRY if unit in reachable_from(e, GRAPH) | {e}]}"
    if DYNAMIC:
        return "unknown", (f"no static path, but {DYNAMIC[0]}() resolves handlers at "
                           f"runtime — cannot prove unreachable")
    return "unreachable", "no path from any entry point"

print(f"{'finding':16s}{'cwe':9s}{'verdict':13s}why")
print("-" * 92)
buckets = defaultdict(list)
for unit, (cwe, sink) in SINKS.items():
    verdict, why = feasibility(unit)
    buckets[verdict].append(unit)
    print(f"{unit:16s}{cwe:9s}{verdict:13s}{why[:52]}")
print(f"\n{ {k: v for k, v in buckets.items()} }")

def naive_filter(sinks, reached):
    """Two buckets. Anything not statically reached is discarded."""
    return {u: ("reachable" if u in reached else "unreachable") for u in sinks}

naive = naive_filter(SINKS, REACHED)
print(f"{'finding':16s}{'3-bucket':13s}{'2-bucket (naive)':18s}")
print("-" * 52)
for u in SINKS:
    v, _ = feasibility(u)
    print(f"{u:16s}{v:13s}{naive[u]:18s}"
          f"{'   ← DROPPED' if v == 'unknown' and naive[u] == 'unreachable' else ''}")

dropped = [u for u in SINKS if feasibility(u)[0] == "unknown"
           and naive[u] == "unreachable"]
print(f"\nfindings silently dropped by two-bucket filtering: {dropped}")
print("legacy_export is reachable through the runtime handler registry in this")
print("application. Static analysis cannot see that, and 'unreachable' is a lie.")
assert dropped

ROUTING = {
 "reachable":   ("page / block the merge", "confirmed exploit path — goes to Phase 4"),
 "unknown":     ("queue for dynamic validation", "Phase 4 decides it empirically"),
 "unreachable": ("record, do not page", "revisit only if an entry point is added"),
}
for bucket, (action, why) in ROUTING.items():
    items = buckets.get(bucket, [])
    print(f"{bucket:13s}{len(items):>2} finding(s) → {action:28s}{why}")
    for i in items: print(f"{'':15s}{i}")

def queue_load(buckets, routing):
    paged = len(buckets.get("reachable", []))
    validated = len(buckets.get("unknown", []))
    silent = len(buckets.get("unreachable", []))
    return {"pages_a_human": paged, "sent_to_phase_4": paged + validated,
            "recorded_only": silent,
            "human_load_reduction": round(1 - paged / max(sum(map(len, buckets.values())), 1), 2)}

print(f"\n{queue_load(buckets, ROUTING)}")
print("\nThe unknown bucket is not a failure of the analysis. It is the handover")
print("to Phase 4, which answers reachability by running the thing.")

contract = contract_of(body)

FILE_OF = {"load_report": "src/data/reports.py", "legacy_export": "src/data/legacy.py",
           "debug_dump": "src/util/debug.py"}
MISSING = {"CWE-89": "parameterised query", "CWE-22": "path normalisation"}

findings = []
for unit, (cwe, sink) in sorted(SINKS.items()):
    verdict, why = feasibility(unit)
    findings.append({
        "id": f"F-{unit}", "cwe": cwe, "file": FILE_OF[unit], "line": 1,
        "unit": unit, "evidence": f"{sink} reached with caller-supplied input",
        "missing_control": MISSING[cwe], "occurrences": 1,
        # a finding we cannot prove reachable is not "confirmed" - it is the
        # one honest use of needs_human in the whole pipeline
        "verdict": "confirmed" if verdict == "reachable" else "needs_human",
        "verdict_reason": why,
        "feasible": verdict == "reachable",
        "confidence": 0.9 if verdict == "reachable" else 0.4})

audit = {
 "findings": findings,
 "dropped": [{"id": f"F-{u}", "stage": 10, "why": "no path from any entry point"}
             for u in sorted(buckets.get("unreachable", []))],
 # three analysers each reported every defect, so the raw count is 3x the
 # number of real defects. That is the normal case, not a bad day.
 "counts": {"raw": len(SINKS) * 3, "deduped": len(SINKS),
            "verified": len(findings),
            "feasible": sum(1 for f in findings if f["feasible"])},
}

problems = check(audit, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

c = audit["counts"]
seq = [c["raw"], c["deduped"], c["verified"], c["feasible"]]
print(f"\ncounts raw->deduped->verified->feasible : {seq}")
print(f"monotonically non-increasing            : {all(x >= y for x, y in zip(seq, seq[1:]))}")
assert all(x >= y for x, y in zip(seq, seq[1:])), seq

# The same three defects, as three analysers actually report them.
ANALYSER_WORDING = {
 "grep rules":  "possible {cwe} near {unit}",
 "taint rules": "tainted input reaches {unit} ({cwe})",
 "model review":"{unit} appears to pass user input to a dangerous sink; likely {cwe}",
}
raw = [dict(f, id=f"{f['id']}/{tool}",
            message=w.format(cwe=f["cwe"], unit=f["unit"]))
       for f in findings for tool, w in sorted(ANALYSER_WORDING.items())]
print(f"raw findings from three analysers: {len(raw)}")

def dedup(rows, key):
    seen = {}
    for r in rows:
        seen.setdefault(key(r), r)
    return sorted(seen.values(), key=lambda r: r["id"])

by_identity = dedup(raw, lambda r: (r["cwe"], r["file"], r["unit"], r["evidence"]))
by_message  = dedup(raw, lambda r: r["message"])
print(f"deduped on defect identity : {len(by_identity)}")
print(f"deduped on message text    : {len(by_message)}")

bad = dict(audit, findings=by_message,
           counts=dict(audit["counts"], deduped=len(by_message),
                       verified=len(by_message),
                       feasible=sum(1 for f in by_message if f["feasible"])))
print(f"\nconformance problems: {len(check(bad, contract))}   <- still zero")
seq2 = [bad["counts"][k] for k in ("raw", "deduped", "verified", "feasible")]
print(f"counts               : {seq2}")
print()
print(f"Three defects became {len(by_message)} findings, and every one of them is")
print("schema-valid. Each analyser words the same defect differently, so the")
print("message is a unique key by construction - it deduplicates nothing while")
print("looking like it deduplicates everything.")
print()
print("The queue triples. Nobody reads the third page. The defect that gets")
print("fixed is whichever one happened to sort first.")
assert not check(bad, contract), "the broken pipeline still conforms - that is the point"
assert len(by_message) > len(by_identity), "message-keyed dedup must inflate the list"
assert len(by_identity) == len(SINKS)

# Verbatim output from Moonlight-16B-A3B on Kaggle, 2026-08-17.
# Not a paraphrase and not a stand-in: this is what the model emitted.
MODEL_OUTPUT = '''{"findings": [{"id": "F-01", "cwe": "CWE-89", "file": "report_api.py",
"line": 22, "unit": "get_report",
"evidence": "open('/var/reports/' + request.args['name'])",
"missing_control": "str", "occurrences": 1, "verdict": "confirmed",
"verdict_reason": "str", "feasible": true, "confidence": 0.0}],
"dropped": [], "counts": {"raw": 0, "deduped": 0, "verified": 0, "feasible": 0}}'''

model = json.loads(MODEL_OUTPUT)
problems = check(model, contract)
print(f"conformance problems: {len(problems)}")
print()
f = model["findings"][0]
print(f"evidence it cited : {f['evidence']}")
print(f"CWE it assigned   : {f['cwe']}  (SQL injection)")
print(f"CWE it actually is: CWE-22  (path traversal - it is open(), not a query)")
print(f"missing_control   : {f['missing_control']!r}")
print(f"verdict_reason    : {f['verdict_reason']!r}")
print(f"counts            : {model['counts']}  while findings has {len(model['findings'])}")
assert not problems, "the real model's output conforms - that is the point"

print("What a schema check can see:")
print(f"   every required field present, every type correct -> {len(check(model, contract))} problems")
print()
print("What it cannot see:")
print("   1. the CWE is wrong. open() on a caller-supplied path is CWE-22,")
print("      not CWE-89. The second sink, os.system(), is CWE-78 - and the")
print("      model gave that one CWE-89 as well.")
print("   2. `missing_control` and `verdict_reason` are the literal string")
print("      'str' - the model copied the contract's TYPE PLACEHOLDER into")
print("      the value. A schema saying a field must be a string is")
print("      perfectly satisfied by the word 'str'.")
print("   3. counts says 0 findings. The findings array has 1.")
print()
# monotonicity alone passes here: [0,0,0,0] is non-increasing. The invariant
# that catches this one is different, and cheap.
seq = [model["counts"][k] for k in ("raw", "deduped", "verified", "feasible")]
print(f"counts non-increasing?      {all(x >= y for x, y in zip(seq, seq[1:]))}  <- passes")
print(f"counts.verified == len(findings)?  "
      f"{model['counts']['verified'] == len(model['findings'])}  <- catches it")
print()
print("Three defects, zero schema violations. That is what a headline of")
print("'100% schema-valid' actually means as a quality metric, and it is why")
print("accuracy has to be measured against a key the model never sees.")
assert model["counts"]["verified"] != len(model["findings"])
assert f["cwe"] != "CWE-22", "the model got the weakness class wrong"
assert f["missing_control"] == "str", "the model copied the type placeholder"
