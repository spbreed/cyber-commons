#!/usr/bin/env python3
"""Run grep rules, taint rules and a model over the same code and compare precision, recall and what only the third one finds.

This is the executable half of the `sast-generation-comparison` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# --- model backend: replay by default, a Kaggle open-weight model when served -
# One URL and one header shape, no vendor SDK. Standard library only, so the
# notebook stays self-contained.
# The model adapter comes from the shared runtime, not from a copy in this
# file. In a lesson notebook the cell above has already loaded it; standalone,
# find it the same way that cell does.
import glob as _glob, importlib.util as _ilu, os as _os, sys as _sys

if "cyber_commons_skill_runtime" not in _sys.modules:
    _where = (sorted(_glob.glob("/kaggle/input/**/cyber-commons-skill-runtime/__script__.py",
                                recursive=True))
              + [_os.path.join(p, "skills/_runtime/cyber_commons_skill_runtime.py")
                 for p in (".", "..", "../..", _os.path.join(_os.path.dirname(__file__), "../../../_runtime"))])
    _found = next((p for p in _where if _os.path.isfile(p)), None)
    if _found is None:
        raise SystemExit("shared skill runtime not found; looked at " + repr(_where))
    _spec = _ilu.spec_from_file_location("cyber_commons_skill_runtime", _found)
    _mod = _ilu.module_from_spec(_spec)
    _sys.modules["cyber_commons_skill_runtime"] = _mod
    _spec.loader.exec_module(_mod)

from cyber_commons_skill_runtime import announce_backend, ask

announce_backend()


CODE = {
"db.py": '''
def get_user(conn, name):
    # BUG: user input concatenated into SQL
    return conn.execute("SELECT * FROM users WHERE name = \'" + name + "\'")

def get_user_safe(conn, name):
    # parameterised — the driver escapes it
    return conn.execute("SELECT * FROM users WHERE name = ?", (name,))

def audit_note(conn, msg):
    # a constant string. No user input anywhere.
    return conn.execute("INSERT INTO audit(msg) VALUES (\'startup\')")
''',
"ops.py": '''
import os, subprocess

def ping(host):
    # BUG: shell string built from user input
    os.system("ping -c1 " + host)

def ping_safe(host):
    subprocess.run(["ping", "-c1", host], check=True)
''',
"files.py": '''
def read_doc(base, filename):
    # BUG: path joined from untrusted input
    return open(base + "/" + filename).read()
''',
}
import re
GREP_RULES = [("CWE-89","SQL injection",r"execute\("),
              ("CWE-78","command injection",r"os\.system|subprocess"),
              ("CWE-22","path traversal",r"open\(")]
def gen1(code):
    return [(cwe, name, f, i, ln.strip())
            for f, src in code.items()
            for i, ln in enumerate(src.splitlines(), 1)
            for cwe, name, pat in GREP_RULES if re.search(pat, ln)]

g1 = gen1(CODE)
print(f"generation 1 (grep): {len(g1)} findings")
for cwe, name, f, i, ln in g1:
    print(f"   {cwe:8s}{f}:{i:<3} {ln[:52]}")

TRUTH = {("CWE-89","db.py",4), ("CWE-78","ops.py",6), ("CWE-22","files.py",4)}
def score(findings, label):
    got = {(c, f, i) for c, _, f, i, _ in findings}
    tp, fp, fn = len(got & TRUTH), len(got - TRUTH), len(TRUTH - got)
    prec = tp/(tp+fp) if tp+fp else 0.0
    rec  = tp/(tp+fn) if tp+fn else 0.0
    print(f"{label:32s} tp={tp} fp={fp} fn={fn}  precision={prec:.2f} recall={rec:.2f}")
    return prec, rec
score(g1, "generation 1 · grep")
print("\nfalse positives:")
for cwe, name, f, i, ln in g1:
    if (cwe, f, i) not in TRUTH: print(f"   {f}:{i:<3} {ln[:56]}")

import ast
class TaintRule:
    SINKS = {"execute": ("CWE-89","SQL injection"),
             "system":  ("CWE-78","command injection"),
             "open":    ("CWE-22","path traversal")}
    def scan(self, fname, src):
        out = []
        for fn in [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)]:
            tainted = {a.arg for a in fn.args.args}
            for call in [n for n in ast.walk(fn) if isinstance(n, ast.Call)]:
                sink = (call.func.attr if isinstance(call.func, ast.Attribute)
                        else getattr(call.func, "id", ""))
                if sink not in self.SINKS: continue
                cwe, name = self.SINKS[sink]
                for arg in call.args:
                    if self._concat_taint(arg, tainted):
                        out.append((cwe, name, fname, call.lineno,
                                    ast.get_source_segment(src, call) or ""))
                        break
        return out
    @staticmethod
    def _concat_taint(node, tainted):
        for n in ast.walk(node):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                if {x.id for x in ast.walk(n) if isinstance(x, ast.Name)} & tainted:
                    return True
        return False

rule = TaintRule()
g2 = [f for n, s in CODE.items() for f in rule.scan(n, s)]
print(f"generation 2 (taint rules): {len(g2)} findings")
for cwe, name, f, i, snip in g2: print(f"   {cwe:8s}{f}:{i:<3} {snip[:52]}")
print()
score(g2, "generation 2 · taint rules")

CODE["authz.py"] = '''
def can_delete(user, doc):
    # Reads "or" where it means "and". No sink, no taint, no pattern.
    if user.is_admin or user.id == doc.owner_id or doc.is_public:
        return True
    return False
'''
print("generation 1 on authz.py:", gen1({"authz.py": CODE["authz.py"]}) or "nothing")
print("generation 2 on authz.py:", rule.scan("authz.py", CODE["authz.py"]) or "nothing")

class StandIn:
    """DETERMINISTIC STAND-IN — not a language model. See the note above."""
    KNOWN = {
     "authz.py": [{"cwe":"CWE-863","line":4,"confidence":0.82,
                   "rationale":"disjunctive permission check: a non-public document "
                               "owned by another user is deletable whenever is_public "
                               "is true, and delete rights are never checked"}],
     "db.py": [{"cwe":"CWE-89","line":4,"confidence":0.95,
                "rationale":"name is concatenated into the query string"},
               {"cwe":"CWE-89","line":12,"confidence":0.41,
                "rationale":"audit_note also calls execute"}],     # HALLUCINATION
    }
    def review(self, fname, src): return self.KNOWN.get(fname, [])

model = StandIn()
print("\ngeneration 3 (model review):")
for fname in ("authz.py", "db.py"):
    for f in model.review(fname, CODE[fname]):
        print(f"   {f['cwe']:9s}{fname}:{f['line']:<3} conf={f['confidence']:.2f}  "
              f"{f['rationale'][:52]}")
print("\nIt found the authorization bug neither earlier generation can see.")
print("It also invented a SQL injection in a function with a constant string.")

# What stage 1 said, and what generation 2 found. The agent has both.
HISTORICAL_RISK = {"db.py": 0.53, "authz.py": 0.48, "ops.py": 0.19,
                   "safe.py": 0.02}
MODEL_COST_PER_FILE = 0.031      # dollars, measured on a small open-weight model

def audit_agent(code, rule, model, risk, gate=0.70, risk_floor=0.30):
    """Stage 7, allocated. Rules everywhere; the model where rules went quiet."""
    findings, suppressed, plan = [], [], []
    rule_hits = {f: rule.scan(f, s) for f, s in sorted(code.items())}

    for fname, hits in rule_hits.items():
        for cwe, name, f, i, snip in hits:
            findings.append({"src": "rules", "cwe": cwe, "file": f, "line": i,
                             "confidence": 1.0, "status": "confirmed-by-rule"})

    for fname in sorted(code):
        r = risk.get(fname, 0.0)
        quiet = not rule_hits[fname]
        if r >= risk_floor and quiet:
            plan.append((fname, r, "high risk, rules silent -> REVIEW"))
        elif r >= risk_floor:
            plan.append((fname, r, "high risk, rules already fired -> skip"))
        else:
            plan.append((fname, r, "low historical risk -> skip"))

    reviewed = [f for f, _, why in plan if why.endswith("REVIEW")]
    for fname in reviewed:
        for m in model.review(fname, code[fname]):
            row = {"src": "model", "cwe": m["cwe"], "file": fname,
                   "line": m["line"], "confidence": m["confidence"],
                   "status": "HYPOTHESIS"}
            (findings if m["confidence"] >= gate else suppressed).append(row)

    seen, dedup = set(), []
    for f in sorted(findings, key=lambda r: (r["src"], r["file"], r["line"])):
        k = (f["cwe"], f["file"], f["line"])
        if k not in seen:
            seen.add(k); dedup.append(f)
    return dedup, suppressed, plan, reviewed

final, suppressed, plan, reviewed = audit_agent(CODE, rule, model, HISTORICAL_RISK)

print("the agent's allocation:")
for fname, r, why in plan:
    print(f"   {fname:12s}risk {r:.2f}   {why}")
print(f"\nmodel pass on {len(reviewed)} of {len(CODE)} files "
      f"(${len(reviewed) * MODEL_COST_PER_FILE:.3f} rather than "
      f"${len(CODE) * MODEL_COST_PER_FILE:.3f})")

print(f"\nstage 7 emits {len(final)}, {len(suppressed)} suppressed below 0.70")
for f in final:
    print(f"   [{f['src']:5s}] {f['cwe']:9s}{f['file']}:{f['line']:<3} "
          f"conf={f['confidence']:.2f}  {f['status']}")

TRUTH_FULL = TRUTH | {("CWE-863", "authz.py", 4)}
got = {(f["cwe"], f["file"], f["line"]) for f in final}
print(f"\ntp={len(got & TRUTH_FULL)} fp={len(got - TRUTH_FULL)} "
      f"fn={len(TRUTH_FULL - got)}")
assert not (got - TRUTH_FULL) and not (TRUTH_FULL - got)

# The allocation is a bet, so measure what it costs when it loses. Move the
# authorisation bug into a file with LOW historical risk and re-run.
print("the same corpus, with authz.py carrying no history:")
_, _, plan_b, reviewed_b = audit_agent(CODE, rule, model,
                                       {**HISTORICAL_RISK, "authz.py": 0.04})
final_b, _, _, _ = audit_agent(CODE, rule, model,
                               {**HISTORICAL_RISK, "authz.py": 0.04})
got_b = {(f["cwe"], f["file"], f["line"]) for f in final_b}
missed = TRUTH_FULL - got_b
print(f"   model pass on {len(reviewed_b)} file(s): {reviewed_b}")
print(f"   MISSED: {sorted(missed)}")
print()
print("A new file with no history is invisible to the allocator, and the")
print("allocator is what makes generation 3 affordable. The mitigation is not")
print("subtle - review everything a pull request touched regardless of history,")
print("and let the risk floor decide only where to spend the SECOND pass.")
assert missed == {("CWE-863", "authz.py", 4)}
print()
print("Every model finding above is marked HYPOTHESIS. Stages 8 to 12 decide.")

# ------------------------------------ the same task, against a real model
# Offline this is a labelled replay; with an open-weight model served
# from Kaggle it is the same code calling a real one.

TASK = 'Is this function vulnerable? Name the CWE if so, and say which value reaches the sink.\n\ndef report(request):\n    q = "SELECT * FROM orders WHERE ref = \'" + request.args[\'ref\'] + "\'"\n    return db.execute(q)'

REPLAY = "Yes - CWE-89, SQL injection. request.args['ref'] is concatenated directly into the query string and reaches db.execute unsanitised."

answer, used, model = ask(TASK, replay=REPLAY,
            system='You are a code reviewer. Answer in at most three lines.',
            max_tokens=300)

print(f"backend used : {used}")
print(f"model        : {model}")
print(f"prompt       : {TASK[:66]}...")
print()
print("answer:")
for line in (answer.splitlines() or [answer]):
    print(f"   {line}")

# Two assertions that must hold on every backend, and one property that is
# reported rather than asserted - a real model failing it is a finding about
# the model, not a broken notebook.
assert answer.strip(), "the configured backend returned nothing"
if used == "replay":
    assert answer == REPLAY, "the offline path must return the replay verbatim"

label, held = ("names the CWE identifier", "CWE-89" in answer.upper() or "SQL INJECT" in answer.upper())
print()
print(f"property checked : {label}")
print(f"held on {used:12s} : {held}")
print()
print("Same code, same assertions, two possible backends. Offline the answer is")
print("the replay and is labelled as one; with a served model it is the model's.")
