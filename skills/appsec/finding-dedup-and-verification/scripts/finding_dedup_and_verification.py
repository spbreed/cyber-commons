#!/usr/bin/env python3
"""Collapse raw findings to distinct defects across aliases and tools, then reject the ones whose symbols are not in the file.

This is the executable half of the `finding-dedup-and-verification` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass, field

SOURCE = {
"billing.py": '''
import sqlite3

def build_filter(owner):
    return "WHERE owner = '" + owner + "'"

def list_reports(conn, owner):
    return conn.execute("SELECT * FROM reports " + build_filter(owner))

def total(conn):
    return conn.execute("SELECT SUM(amount) FROM reports").fetchone()
'''
}

@dataclass
class Finding:
    src: str; cwe: str; file: str; line: int; symbol: str
    rationale: str; confidence: float = 1.0

RAW = [
 Finding("grep",   "CWE-89", "billing.py", 7,  "execute",
         "execute() with string concatenation", 0.5),
 Finding("taint",  "CWE-89", "billing.py", 7,  "execute",
         "owner flows into the query via build_filter", 1.0),
 Finding("model",  "CWE-89", "billing.py", 8,  "execute",
         "user-controlled owner is interpolated into SQL", 0.93),
 Finding("model",  "CWE-943","billing.py", 7,  "execute",
         "query language injection", 0.71),
 Finding("model",  "CWE-89", "billing.py", 11, "execute",
         "total() builds a query from input", 0.44),
 Finding("model",  "CWE-798","billing.py", 3,  "DB_PASSWORD",
         "hardcoded database password in DB_PASSWORD", 0.88),
 Finding("model",  "CWE-78", "billing.py", 6,  "os.system",
         "shell invocation with user data", 0.67),
]
print(f"{len(RAW)} raw findings from 3 tracks")
for f in RAW:
    print(f"   {f.src:6s}{f.cwe:9s}{f.file}:{f.line:<3}{f.symbol:14s}conf={f.confidence:.2f}")

import ast

def enclosing_function(src, line):
    tree = ast.parse(src)
    best = None
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        end = max((getattr(n, "lineno", fn.lineno) for n in ast.walk(fn)),
                  default=fn.lineno)
        if fn.lineno <= line <= end + 1:
            if best is None or fn.lineno > best.lineno: best = fn
    return best.name if best else None

CWE_ALIASES = {"CWE-943": "CWE-89", "CWE-89": "CWE-89"}

def defect_key(f, src):
    fn = enclosing_function(src, f.line)
    cwe = CWE_ALIASES.get(f.cwe, f.cwe)
    return (f.file, fn, f.symbol, cwe)

SRC = SOURCE["billing.py"]
clusters = {}
for f in RAW:
    clusters.setdefault(defect_key(f, SRC), []).append(f)

RANK = {"taint": 3, "grep": 1, "model": 2}
deduped = []
for key, group in clusters.items():
    best = max(group, key=lambda f: (RANK[f.src], f.confidence))
    deduped.append({"key": key, "keep": best, "merged": len(group),
                    "sources": sorted({g.src for g in group})})

print(f"{len(RAW)} findings → {len(deduped)} distinct defects\n")
for d in deduped:
    file, fn, sym, cwe = d["key"]
    print(f"   {cwe:8s}{str(fn):14s}{sym:14s}merged {d['merged']} "
          f"from {d['sources']}  (kept {d['keep'].src})")

def verify(finding, src):
    tree = ast.parse(src)
    problems = []

    # check 1 — does the referenced symbol exist at all?
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    root = finding.symbol.split(".")[0]
    if finding.symbol not in names and root not in names:
        problems.append(f"symbol {finding.symbol!r} does not appear in the file")

    # check 2 — is the module it implies actually imported?
    imports = {a.name.split(".")[0] for n in ast.walk(tree)
               if isinstance(n, ast.Import) for a in n.names}
    imports |= {n.module.split(".")[0] for n in ast.walk(tree)
                if isinstance(n, ast.ImportFrom) and n.module}
    if "." in finding.symbol and root not in imports:
        problems.append(f"module {root!r} is never imported")

    # check 3 — is the line inside a function at all?
    if enclosing_function(src, finding.line) is None:
        problems.append(f"line {finding.line} is not inside any function")

    return (not problems), problems

print(f"{'cwe':9s}{'symbol':14s}{'line':>5}  verdict")
print("-" * 74)
verified, rejected = [], []
for d in deduped:
    f = d["keep"]
    ok, problems = verify(f, SRC)
    (verified if ok else rejected).append((f, problems))
    print(f"{f.cwe:9s}{f.symbol:14s}{f.line:>5}  "
          f"{'verified' if ok else 'REJECTED — ' + problems[0]}")
print(f"\n{len(verified)} verified, {len(rejected)} rejected as hallucinations")

# Verify the stage pays for itself.
STAGE7_COUNT = len(RAW)
after8 = len(deduped)
after9 = len(verified)
print(f"stage 7 emitted        {STAGE7_COUNT}")
print(f"after stage 8 (dedup)  {after8}   ({1-after8/STAGE7_COUNT:.0%} removed)")
print(f"after stage 9 (verify) {after9}   ({1-after9/STAGE7_COUNT:.0%} removed overall)")

TRUE_DEFECTS = {("billing.py", "list_reports", "execute", "CWE-89")}
found = {d["key"] for d in deduped if any(d["keep"] is f for f, _ in verified)}
tp = len(found & TRUE_DEFECTS); fp = len(found - TRUE_DEFECTS)
print(f"\nsurviving: tp={tp} fp={fp}")
for f, _ in rejected:
    print(f"   rejected {f.cwe} on {f.symbol!r} — provably not in the code")
assert any("DB_PASSWORD" in f.symbol for f, _ in rejected)
assert any("os.system" in f.symbol for f, _ in rejected)
print("\nBoth hallucinations named things that are not in the file. No model,")
print("no judgement, no cost — just the AST disagreeing with the claim.")
