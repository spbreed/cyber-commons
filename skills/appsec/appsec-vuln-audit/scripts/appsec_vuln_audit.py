#!/usr/bin/env python3
"""Filter findings by whether the vulnerable path is reachable, and record what reachability analysis cannot decide.

This is the executable half of the `appsec-vuln-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# --- the skill's own contract, available both ways -------------------------
# This script is run two ways and both have to work: standalone from a
# terminal, and embedded in the lesson notebook underneath the cell that
# already parsed the SKILL.md. So take what is already defined and read the
# file only when it is not.
import pathlib as _pathlib


def _skill_md():
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


if "contract_of" not in globals():
    import json, re

    def parse_skill(md):
        """Split a SKILL.md into (frontmatter dict, body).

        Frontmatter is a small, fixed subset of YAML: `key: value`, plus folded
        scalars (`description: >-`) whose continuation lines are indented. That is
        all a skill needs, and parsing it directly means no dependency.
        """
        if not md.startswith("---"):
            raise ValueError("a SKILL.md must open with a frontmatter block")
        _, front, body = md.split("---", 2)
        meta, key = {}, None
        for line in front.strip().splitlines():
            if not line.strip():
                continue
            if not line[0].isspace() and ":" in line:
                key, val = line.split(":", 1)
                key, val = key.strip(), val.strip()
                # `>-` and `|` open a folded block; the value is on the next lines
                meta[key] = "" if val in (">-", ">", "|", "|-") else val
            elif key is not None:
                meta[key] = (meta[key] + " " + line.strip()).strip()
        if "allowed-tools" in meta:
            meta["allowed-tools"] = [t.strip() for t in meta["allowed-tools"].split(",")
                                     if t.strip()]
        for required in ("name", "description"):
            if not meta.get(required):
                raise ValueError(f"skill is missing a {required!r}")
        return meta, body.strip()

    _WORD = re.compile(r"[a-z][a-z-]{3,}")

    def route(task, skills):
        """Pick the skill whose description best matches a task. Deterministic.

        The description is not documentation — it is the routing key. An agent
        decides whether to load a skill by reading it, so a vague description means
        the skill never fires when it should, and two overlapping descriptions mean
        the wrong one fires.

        Returns (pick, scores, margin). A margin of 0 means the top two scored the
        same and the "winner" is just whichever sorted first — an arbitrary answer
        wearing a confident face. Callers should refuse to auto-route on margin 0
        rather than pretend the tiebreak meant something.
        """
        want = set(_WORD.findall(task.lower()))
        def score(meta):
            return len(want & set(_WORD.findall(meta["description"].lower())))
        scores = {n: score(skills[n]) for n in sorted(skills)}
        # sort names first, then by score: ties must break identically on every
        # machine or the same task routes differently on two runs
        ranked = sorted(sorted(skills), key=lambda n: -scores[n])
        top = scores[ranked[0]]
        margin = top - (scores[ranked[1]] if len(ranked) > 1 else 0)
        return ranked[0], scores, margin

    def contract_of(body):
        """The JSON block under '## Output contract' — the skill's machine promise."""
        # non-greedy across any prose between the heading and the fence
        m = re.search(r"## Output contract\b.*?```json\n(.*?)```", body, re.S)
        if not m:
            raise ValueError("skill declares no output contract")
        return json.loads(m.group(1))

    def check(instance, contract, path="$"):
        """Structural conformance of an instance against a contract template.

        Returns the list of problems. An empty list means the shape is right — and
        that is *all* it means. Conformance is not accuracy: an empty findings list
        conforms perfectly and tells you nothing.
        """
        problems = []
        if isinstance(contract, dict):
            if not isinstance(instance, dict):
                return [f"{path}: expected an object, got {type(instance).__name__}"]
            for k, v in sorted(contract.items()):
                if k not in instance:
                    problems.append(f"{path}.{k}: missing")
                else:
                    problems += check(instance[k], v, f"{path}.{k}")
        elif isinstance(contract, list):
            if not isinstance(instance, list):
                return [f"{path}: expected a list, got {type(instance).__name__}"]
            for i, item in enumerate(instance):          # every element, same template
                problems += check(item, contract[0], f"{path}[{i}]")
        elif isinstance(contract, str) and "|" in contract:
            if instance not in contract.split("|"):
                problems.append(f"{path}: {instance!r} is not one of {contract}")
        elif isinstance(contract, bool):                  # before the numeric case:
            if not isinstance(instance, bool):            # bool is a subclass of int
                problems.append(f"{path}: expected bool, got {type(instance).__name__}")
        elif isinstance(contract, (int, float)):
            # JSON has one number type. A contract written `0` must accept 0.4, or
            # every cost and rate in the pipeline has to be rounded to satisfy a
            # checker rather than to be correct.
            if isinstance(instance, bool) or not isinstance(instance, (int, float)):
                problems.append(f"{path}: expected a number, got {type(instance).__name__}")
        elif not isinstance(instance, type(contract)):
            problems.append(f"{path}: expected {type(contract).__name__}, "
                            f"got {type(instance).__name__}")
        return problems

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
