#!/usr/bin/env python3
"""Find the smallest slice of a file in which a defect is decidable, and measure what larger contexts add.

This is the executable half of the `context-window-sizing` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SOURCE = '''"""Reporting service."""
import logging, os, json, datetime

log = logging.getLogger(__name__)
DEFAULT_LIMIT = 100
CACHE = {}

def _format_row(row):
    return {"id": row[0], "name": row[1], "created": str(row[2])}

def _cache_key(*parts):
    return ":".join(str(p) for p in parts)

def healthcheck():
    return {"status": "ok", "ts": datetime.datetime.utcnow().isoformat()}

def list_reports(conn, owner, limit=DEFAULT_LIMIT):
    """Called from GET /reports?owner=... — owner is user-controlled."""
    key = _cache_key("reports", owner, limit)
    if key in CACHE:
        return CACHE[key]
    rows = conn.execute("SELECT * FROM reports WHERE owner = '" + owner + "' LIMIT " + str(limit))
    out = [_format_row(r) for r in rows]
    CACHE[key] = out
    return out

def purge_cache():
    CACHE.clear()
    log.info("cache purged")
'''
lines = SOURCE.splitlines()
BUG_LINE = next(i for i, l in enumerate(lines, 1) if "SELECT * FROM reports" in l)
print(f"the bug is on line {BUG_LINE}")

def whole_file(_):     return SOURCE
def window(n, radius): return "\n".join(lines[max(n-radius-1,0):n+radius])

STRATEGIES = {"whole file": whole_file(BUG_LINE),
              "±2 line window": window(BUG_LINE, 2),
              "±6 line window": window(BUG_LINE, 6)}
for name, ctx in STRATEGIES.items():
    print(f"{name:20s}{len(ctx):>6} chars{len(ctx.splitlines()):>5} lines")

def decidable(ctx):
    """Can a reviewer judge exploitability from this context alone?"""
    return {"sink": "conn.execute" in ctx,
            "concatenation": "' + owner +" in ctx or "+ owner +" in ctx,
            "source (signature)": "def list_reports" in ctx,
            "intent (docstring)": "user-controlled" in ctx}

print(f"{'strategy':20s}{'sink':7s}{'concat':8s}{'source':8s}{'intent':8s}decidable")
print("-" * 64)
for name, ctx in STRATEGIES.items():
    d = decidable(ctx)
    ok = d["sink"] and d["concatenation"] and d["source (signature)"]
    print(f"{name:20s}{str(d['sink']):7s}{str(d['concatenation']):8s}"
          f"{str(d['source (signature)']):8s}{str(d['intent (docstring)']):8s}{ok}")
print("\nThe ±2 window has the sink and the concatenation but not the signature,")
print("so you cannot tell whether owner is user-controlled — which is the")
print("difference between critical and won't-fix.")

def path_slice(source, bug_line):
    ls = source.splitlines()
    start = max(i for i in range(bug_line) if ls[i-1].startswith("def "))
    end = next((i for i in range(start, len(ls)) if i > start and ls[i].startswith("def ")),
               len(ls))
    return "\n".join(ls[start-1:end])

sliced = path_slice(SOURCE, BUG_LINE)
print(sliced)
d = decidable(sliced)
print(f"\n{len(sliced)} chars ({len(sliced)/len(SOURCE):.0%} of the file), "
      f"decidable={d['sink'] and d['concatenation'] and d['source (signature)']}")

def evaluate(name, ctx):
    d = decidable(ctx)
    return {"strategy": name, "chars": len(ctx),
            "share": round(len(ctx)/len(SOURCE), 3),
            "decidable": d["sink"] and d["concatenation"] and d["source (signature)"],
            "noise_fns": max(ctx.count("def ") - 1, 0)}

rows = [evaluate(n, c) for n, c in STRATEGIES.items()] + [evaluate("path slice", sliced)]
print(f"{'strategy':20s}{'chars':>7}{'share':>8}{'decidable':>11}{'noise fns':>11}")
print("-" * 58)
for r in rows:
    print(f"{r['strategy']:20s}{r['chars']:>7}{r['share']:>8.0%}"
          f"{str(r['decidable']):>11}{r['noise_fns']:>11}")

best = sorted((r for r in rows if r["decidable"]), key=lambda r: r["chars"])[0]
whole = next(r for r in rows if r["strategy"] == "whole file")
print(f"\nsmallest decidable context: {best['strategy']} "
      f"({best['share']:.0%} of the file, {best['noise_fns']} unrelated functions)")
print(f"vs whole file: {1 - best['chars']/whole['chars']:.0%} smaller, "
      f"{whole['noise_fns']}→{best['noise_fns']} unrelated functions")
assert best["strategy"] == "path slice"

# ---------------------------------------------------------------------------
# Why this is measured in false positives rather than in tokens.
#
# The two failure shapes below are the ones B2.3's model pass actually produced,
# and each is a slice defect rather than a model defect.
print()
print("what each slice costs, in the only unit that matters")
print(f"   {'slice':<20}{'decidable':<11}{'unrelated fns':<15}what the model does with it")
COSTS = {
    "whole file":     "reviews whatever survived truncation; you cannot tell which parts",
    "±2 line window": "cannot see the signature, so it GUESSES whether owner is tainted",
    "±6 line window": "decidable, and carrying one function the defect does not depend on",
    "path slice":     "decidable, nothing unrelated - the answer is checkable",
}
for r in rows:
    print(f"   {r['strategy']:<20}{str(r['decidable']):<11}{r['noise_fns']:<15}"
          f"{COSTS[r['strategy']]}")
print()
print("The undecidable slice is the expensive one, and not because it is wrong -")
print("because it is UNANSWERABLE and the model answers anyway. Asked whether a")
print("value is user-controlled without being shown where it comes from, it")
print("produces a confident verdict from the only thing it has, which is the")
print("shape of the line. That is where a false positive comes from.")
print()
print("B2.3 is the worked case. Given the function, its signature and the caller's")
print("authority, the model pass found a real missing-authorisation defect and")
print("quoted a line that exists. Given a slice it could not decide, it returned")
print("CWE-89 at 0.71 confidence quoting a concatenation that is not in the file.")
print("Same model, same prompt, different slice.")
print()
print("So the rule is not 'send less'. It is: find the smallest slice in which the")
print("defect is DECIDABLE, and only then make it smaller. Cutting below that line")
print("does not save money, it buys false positives at a discount.")
