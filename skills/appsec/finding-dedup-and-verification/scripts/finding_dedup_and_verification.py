#!/usr/bin/env python3
"""Collapse raw findings to distinct defects across aliases and tools, then reject the ones whose symbols are not in the file.

This is the executable half of the `finding-dedup-and-verification` skill, and
it is the stage directly downstream of B2.3. The file it verifies against is
not a fixture: it is `cybertravels/tools/bookings_api.py`, read off disk — the
same file Semgrep scanned at three widths and the same one the model pass took
its slice from.

The raw findings are what those two runs actually emitted, plus the duplicates
you get for free when three tracks report the same defect and two hallucinations
recorded from a smaller model. Line numbers below are real line numbers in that
file; change the file and the enclosing-function lookup follows it.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass, field
from pathlib import Path

# The tree, found from this file rather than from the working directory: on
# Kaggle `cwd` is /kaggle/working and the clone is beside it.
ROOT = Path(__file__).resolve().parents[4]
TARGET = "tools/bookings_api.py"
SOURCE = {TARGET: (ROOT / "cybertravels" / TARGET).read_text()}

@dataclass
class Finding:
    src: str; cwe: str; file: str; line: int; symbol: str
    rationale: str; confidence: float = 1.0

RAW = [
 # search_bookings — the one defect in this file every track saw, three times.
 Finding("grep",   "CWE-89", TARGET, 41, "execute",
         "execute() with string concatenation", 0.5),
 Finding("taint",  "CWE-89", TARGET, 41, "execute",
         "reference flows from the caller into the query", 1.0),
 Finding("model",  "CWE-89", TARGET, 42, "execute",
         "the reference is interpolated into SQL", 0.93),
 # The same defect again under a different CWE. An alias, not a second defect.
 Finding("model",  "CWE-943",TARGET, 41, "execute",
         "query language injection", 0.71),
 # get_booking — B2.3's model hypothesis arriving here. No tool but the model
 # reported it, because no tool could.
 Finding("model",  "CWE-639",TARGET, 20, "get_booking",
         "returns the row a caller names without comparing an owner", 0.82),
 # list_my_bookings is parameterised and session-scoped. A low-confidence model
 # claim on real code: it survives both stages, because neither stage is triage.
 Finding("model",  "CWE-89", TARGET, 47, "execute",
         "list_my_bookings builds a query from input", 0.44),
 # Two hallucinations, recorded from a smaller model. Neither symbol is in the
 # file at all.
 Finding("model",  "CWE-798",TARGET,  8, "DB_PASSWORD",
         "hardcoded database password in DB_PASSWORD", 0.88),
 Finding("model",  "CWE-78", TARGET, 34, "os.system",
         "shell invocation with the booking id", 0.67),
]
print(f"{len(RAW)} raw findings from 3 tracks, against {TARGET}")
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

SRC = SOURCE[TARGET]
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
    print(f"   {cwe:8s}{str(fn):18s}{sym:14s}merged {d['merged']} "
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

TRUE_DEFECTS = {(TARGET, "search_bookings", "execute", "CWE-89"),
                (TARGET, "get_booking", "get_booking", "CWE-639")}
found = {d["key"] for d in deduped if any(d["keep"] is f for f, _ in verified)}
tp = len(found & TRUE_DEFECTS); fp = len(found - TRUE_DEFECTS)
print(f"\nsurviving: tp={tp} fp={fp}")
for f, _ in rejected:
    print(f"   rejected {f.cwe} on {f.symbol!r} — provably not in the code")
assert any("DB_PASSWORD" in f.symbol for f, _ in rejected)
assert any("os.system" in f.symbol for f, _ in rejected)
print("\nBoth hallucinations named things that are not in the file. No model,")
print("no judgement, no cost — just the AST disagreeing with the claim.")
print()
print(f"And one survivor is wrong: the CWE-89 on list_my_bookings, whose query")
print("is parameterised and scoped to the session. Nothing here rejected it,")
print("because nothing here is triage. These two stages remove what is provably")
print("duplicated and provably absent. Deciding that a claim about real code is")
print("wrong takes context, and that is the next stage, not this one.")
