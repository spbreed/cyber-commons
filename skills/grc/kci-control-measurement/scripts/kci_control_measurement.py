#!/usr/bin/env python3
"""Measure five key control indicators against the CyberTravels tree, and report each gap with the lesson that closes it.

This is the executable half of `kci-control-measurement`. A KCI is only a
control indicator if something measures it; otherwise it is a sentence in a
policy. So this reads the actual repository — `cybertravels/`, the same tree
B2.3 scans and A1.1 draws — and computes each indicator from the source.

The output is deliberately not a score. It is a list of gaps, each with the
lesson that closes it, because a governance report whose only artefact is a
number changes nothing.

Standard library only, and deterministic.
"""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REPO = ROOT / "cybertravels"
SRC = {p.relative_to(REPO).as_posix(): p.read_text()
       for p in sorted(REPO.rglob("*.py"))}


def functions(text):
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.FunctionDef):
            yield node


# KCI-01 — object handlers that compare an owner before returning a record.
handlers, authorised = [], []
for path, text in SRC.items():
    for fn in functions(text):
        args = [a.arg for a in fn.args.args]
        takes_id = any(a in ("booking_id", "payment_id", "path", "reference") for a in args)
        touches = "execute" in ast.dump(fn) or "open" in ast.dump(fn)
        if takes_id and touches:
            handlers.append(f"{path}:{fn.name}")
            src = ast.dump(fn)
            if "require_owner" in src or "user_id" in src:
                authorised.append(f"{path}:{fn.name}")

# KCI-02 — outbound HTTP calls that verify TLS.
tls_calls = re.findall(r"verify\s*=\s*(True|False)", "\n".join(SRC.values()))
tls_ok = sum(1 for v in tls_calls if v == "True")

# KCI-03 — no evaluation of caller-supplied text.
evals = [f"{p}:{fn.name}" for p, t in SRC.items() for fn in functions(t)
         if any(getattr(c.func, "id", "") in ("eval", "exec")
                for c in ast.walk(fn) if isinstance(c, ast.Call))]

# KCI-04 — no shell invocation carrying a model-supplied argument.
shells = [f"{p}:{fn.name}" for p, t in SRC.items() for fn in functions(t)
          if "shell=True" in ast.get_source_segment(t, fn) or "os.system" in
          ast.get_source_segment(t, fn)]

# KCI-05 — an egress control exists at all.
egress = (REPO / "egress").is_dir()

# KCI-06 — no credential literal in the tree. Included because a set of
# indicators that all fail cannot show it discriminates: this one passes, and a
# reader can see the measurement says so rather than saying GAP by default.
SECRETISH = re.compile(r"""(?ix)\b(password|secret|api[_-]?key|token)\b\s*=\s*['"][^'"]{6,}""")
secrets = [p for p, t in SRC.items() if SECRETISH.search(t)]

KCIS = [
    ("KCI-01", "object handlers that compare an owner", "== 1.00",
     len(authorised) / len(handlers) if handlers else 0.0,
     f"{len(handlers) - len(authorised)} of {len(handlers)} handlers do not",
     "A2.4 and B2.3 — the ownership check, and finding the ones that lack it"),
    ("KCI-02", "outbound HTTP calls verifying TLS", "== 1.00",
     tls_ok / len(tls_calls) if tls_calls else 1.0,
     f"{len(tls_calls) - tls_ok} of {len(tls_calls)} disable verification",
     "B2.7 — a rule that names your own HTTP wrapper, not requests"),
    ("KCI-03", "no evaluation of caller-supplied text", "== 0",
     float(len(evals)), f"{len(evals)} function(s) call eval or exec",
     "A3.4 — default-deny on the tool call"),
    ("KCI-04", "no shell carrying a model-supplied argument", "== 0",
     float(len(shells)), f"{len(shells)} function(s) reach a shell",
     "A3.4 and B2.3 — CWE-78 is expressible; a rule catches it"),
    ("KCI-05", "egress control present", "== 1", float(egress),
     "no egress component exists in the architecture",
     "A3.7 — the agent gateway as one choke point"),
    ("KCI-06", "no credential literal in the source", "== 0",
     float(len(secrets)), f"{len(secrets)} module(s) carry one",
     "already met — kept so the set can be seen to discriminate"),
]


def meets(target, value):
    op, bound = target.split()
    bound = float(bound)
    return {"==": value == bound, ">=": value >= bound, "<=": value <= bound}[op]


print(f"cybertravels/ · {len(SRC)} modules · {len(handlers)} object handlers")
print()
print(f"{'kci':<8}{'indicator':<42}{'target':>9}{'measured':>10}  status")
report = {"kcis": [], "gaps": []}
for kid, what, target, value, gap, fix in KCIS:
    ok = meets(target, value)
    print(f"{kid:<8}{what:<42}{target:>9}{value:>10.2f}  {'ok' if ok else 'GAP'}")
    report["kcis"].append({"id": kid, "indicator": what, "target": target,
                           "measured": round(value, 2), "met": ok})
    if not ok:
        report["gaps"].append({"id": kid, "gap": gap, "mitigation": fix})
print()
print(f"{len(report['kcis']) - len(report['gaps'])} met · {len(report['gaps'])} gaps")
print()
for g in report["gaps"]:
    print(f"   {g['id']}  {g['gap']}")
    print(f"           -> {g['mitigation']}")
print()
print("Every number above was computed from the tree just now, which is the only")
print("property that makes these control INDICATORS rather than control claims.")
print("Re-run it after a change and the same five numbers move or they do not.")
print()
print("KCI-05 is the one worth arguing about. It measures a component that does")
print("not exist, so it reads 0.00 and always will until somebody builds a")
print("gateway. An indicator for a control you have not built is not a failure")
print("of the estate - it is the backlog, stated in the same units as the rest.")

assert len(handlers) >= 5, "the handler denominator looks wrong"
assert report["gaps"], "a tree with known defects must show gaps"
assert any(k["met"] for k in report["kcis"]), \
    "a set of indicators that all fail cannot be shown to discriminate"
assert all(g["mitigation"] for g in report["gaps"]), "every gap names a lesson"
