#!/usr/bin/env python3
"""Read a repository the way stage 1 to 4 of the pipeline does: history, structural index, component summaries, and the map they synthesise.

This is the executable half of the `appsec-repo-recon` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# --- model backend: replay by default, a Kaggle open-weight model when served -
# One URL and one header shape, no vendor SDK. Standard library only, so the
# notebook stays self-contained.
import json, os, urllib.error, urllib.request

# Qwen2.5-7B-Instruct is the floor established in MODELS.md: below it two of
# the lessons' acceptance properties stop holding.
OPEN_WEIGHT_DEFAULT = "qwen2.5-7b-instruct"
TIMEOUT = 60

def backend():
    """(kind, model). Configuration comes from the environment, never a literal."""
    if os.environ.get("OPENAI_BASE_URL"):
        return "open-weight", os.environ.get("MODEL", OPEN_WEIGHT_DEFAULT)
    return "replay", "deterministic stand-in (no backend configured)"

def _post(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())

def _openai_compatible(prompt, system, model, max_tokens, temperature):
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    base = os.environ["OPENAI_BASE_URL"].rstrip("/")
    key = os.environ.get("OPENAI_API_KEY", "not-needed")
    out = _post(f"{base}/chat/completions",
                {"model": model, "messages": msgs, "max_tokens": max_tokens,
                 "temperature": temperature},
                {"authorization": f"Bearer {key}"})
    return out["choices"][0]["message"]["content"].strip()

def ask(prompt, *, replay, system=None, max_tokens=512, temperature=0.0):
    """Answer `prompt` with the configured backend, or return `replay`.

    `replay` is required, not optional: a lesson must be able to run offline,
    and the answer it falls back to has to be visible in the source rather than
    invented at runtime.
    """
    kind, model = backend()
    if kind == "replay":
        return replay, kind, model
    try:
        return _openai_compatible(prompt, system, model, max_tokens,
                                  temperature), kind, model
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as e:
        # Print what the server actually said. "failed: 400" costs whoever hits
        # this an hour; the body usually names the exact missing parameter, and
        # it never contains a key.
        detail = getattr(e, "code", None) or type(e).__name__
        why = ""
        if hasattr(e, "read"):
            try:
                why = json.loads(e.read().decode()).get("error", {}).get("message", "")
            except Exception:
                why = ""
        print(f"   !! {kind} backend ({model}) failed: {detail}"
              f"{' - ' + why if why else ''}")
        print("      Using the replay, which is labelled as one. No model answered.")
        return replay, "replay", f"{model} unreachable"

_kind, _model = backend()
print(f"model backend : {_kind}")
print(f"model         : {_model}")
if _kind == "replay":
    print()
    print("This lesson runs offline against a deterministic replay, which is why")
    print("it works on a Kaggle kernel with the internet switched off. To run the")
    print("identical code against a real model, serve an open-weight model from")
    print("Kaggle Models and point the adapter at it:")
    print()
    print("   python3 -m llama_cpp.server --model <the .gguf from Kaggle> \\")
    print("           --model_alias qwen2.5-7b-instruct --port 11434 --chat_format qwen")
    print("   export OPENAI_BASE_URL=http://127.0.0.1:11434/v1 \\")
    print("          MODEL=qwen2.5-7b-instruct")
    print()
    print("   MODELS.md has the exact Kaggle download. There is no paid backend:")
    print("   every model result in this repository was produced this way.")


import ast, math, re
from collections import Counter, defaultdict
from dataclasses import dataclass

@dataclass(frozen=True)
class Commit:
    sha: str; subject: str; files: tuple; days_ago: int

HISTORY = [
 Commit("a1b2c3d", "fix(api): reject empty session tokens (CVE-2025-0091)",
        ("src/api/bookings.py",), 420),
 Commit("b2c3d4e", "refactor: extract render helper", ("src/util/render.py",), 400),
 Commit("c3d4e5f", "fix(data): SQL injection in the booking filter (CVE-2025-1188)",
        ("src/data/reports.py",), 300),
 Commit("d4e5f6a", "feat: CSV export of itineraries",
        ("src/data/reports.py", "src/util/render.py"), 260),
 Commit("e5f6a7b", "security: patch path traversal in the voucher store",
        ("src/data/docs.py",), 210),
 Commit("f6a7b8c", "chore: bump deps", ("requirements.txt",), 180),
 Commit("a7b8c9d", "fix(api): timing leak in the token compare",
        ("src/api/bookings.py",), 150),
 Commit("b8c9d0e", "feat: pagination on bookings", ("src/data/reports.py",), 120),
 Commit("c9d0e1f", "fix: harden the voucher path join after the report",
        ("src/data/docs.py",), 60),
 Commit("d0e1f2a", "style: formatting", ("src/util/render.py",), 30),
]

MARKERS = re.compile(
    r"\b(cve-\d{4}-\d+|security|injection|traversal|xss|ssrf|auth|hardcoded|"
    r"leak|sanitis|sanitiz|escap)\w*", re.I)

def is_security_fix(c):
    return bool(MARKERS.search(c.subject))

def risk_zones(history, half_life_days=180):
    """Prior-defect density, decayed by age. A recent security fix weighs more."""
    score, fixes, churn = defaultdict(float), defaultdict(int), Counter()
    for c in history:
        for f in c.files:
            churn[f] += 1
            if is_security_fix(c):
                fixes[f] += 1
                score[f] += math.exp(-c.days_ago / half_life_days)
    return sorted(
        ({"file": f, "commits": churn[f], "security_fixes": fixes[f],
          "risk": round(score[f], 3)} for f in churn),
        key=lambda r: (-r["risk"], r["file"]))

zones = risk_zones(HISTORY)
print(f"{'file':24s}{'commits':>9}{'sec fixes':>11}{'risk':>8}")
print("-" * 52)
for r in zones:
    print(f"{r['file']:24s}{r['commits']:>9}{r['security_fixes']:>11}{r['risk']:>8}")

print("\nsrc/api/bookings.py and src/data/docs.py are the repeat zones, and the")
print("ordering comes entirely from history - no rule has run.")
print("Note what stage 1 missed: 'harden the voucher path join' is the most")
print("recent security commit in the list and matches no marker, so it scores")
print("nothing. Marker quality IS the accuracy of this stage.")

SOURCES = {
 "src/api/bookings.py": '''
def get_booking(request):
    """HTTP GET /bookings/<ref> - request.args is traveller-controlled."""
    return render(load_booking(request.args["ref"], request.args["owner"]))

def upload_voucher(request):
    """HTTP POST /vouchers - the multipart body is traveller-controlled."""
    return store(request.files["doc"], request.args["name"])
''',
 "src/data/reports.py": '''
def load_booking(ref, owner):
    return DB.execute("SELECT * FROM bookings WHERE ref=" + ref +
                      " AND owner='" + owner + "'")
''',
 "src/data/docs.py": '''
def store(blob, name):
    path = "/srv/vouchers/" + name
    open(path, "wb").write(blob)
    return path
''',
 "src/util/render.py": '''
def render(rows):
    return "\\n".join(str(r) for r in rows)
''',
}

DANGEROUS = {"execute": "database", "open": "filesystem", "write": "filesystem"}

def units_of(src, path):
    out = []
    for fn in [n for n in ast.walk(ast.parse(src))
               if isinstance(n, ast.FunctionDef)]:
        calls = sorted({(c.func.id if isinstance(c.func, ast.Name)
                         else getattr(c.func, "attr", ""))
                        for c in ast.walk(fn) if isinstance(c, ast.Call)} - {""})
        # file AND line, never a bare name: two functions called `handler` in
        # two files are two units, and merging them loses a finding
        out.append({"name": fn.name, "file": path, "line": fn.lineno,
                    "params": [a.arg for a in fn.args.args], "calls": calls,
                    "doc": ast.get_docstring(fn) or ""})
    return out

UNITS = [u for p, s in sorted(SOURCES.items()) for u in units_of(s, p)]
NAMES = {u["name"] for u in UNITS}

print(f"{'unit':16s}{'file':24s}{'line':>5}  params -> calls")
print("-" * 78)
for u in UNITS:
    print(f"{u['name']:16s}{u['file']:24s}{u['line']:>5}  "
          f"{u['params']} -> {u['calls']}")

# The question every later stage asks, and what each kind of index can say.
def callers_of(name):
    return sorted(u["name"] for u in UNITS if name in u["calls"])

print("\n\"who reaches store(), and with what?\"")
print("   line-based index : cannot answer - the token appears in two places")
print("   file-based index : \"it is in src/data/docs.py\"")
print(f"   semantic index   : callers = {callers_of('store')}, and its input is "
      f"a traveller-supplied filename")
entries = sorted(u["name"] for u in UNITS if not callers_of(u["name"]))
print(f"\nentry points (nothing in the repository calls them): {entries}")

def summarise(component, units):
    """Stage 3 - a LOCAL summary. One component, not the repository."""
    names = [u["name"] for u in units]
    return {
      "component": component,
      "units": names,
      "entry_points": [u["name"] for u in units if u["doc"].startswith("HTTP")],
      "talks_to": sorted({c for u in units for c in u["calls"]
                          if c in NAMES and c not in names}),
      "touches": sorted({DANGEROUS[c] for u in units for c in u["calls"]
                         if c in DANGEROUS}),
    }

by_dir = defaultdict(list)
for u in UNITS:
    by_dir[u["file"].rsplit("/", 1)[0]].append(u)

SUMMARIES = [summarise(d, us) for d, us in sorted(by_dir.items())]
for s in SUMMARIES:
    print(s["component"])
    print(f"   units       {s['units']}")
    print(f"   entry pts   {s['entry_points'] or '-'}")
    print(f"   talks to    {s['talks_to'] or '-'}")
    print(f"   touches     {s['touches'] or '-'}\n")

TRUST = {"src/api": 0, "src/util": 1, "src/data": 2}   # 0 = untrusted edge

def synthesise(summaries, units):
    comp = {u["name"]: u["file"].rsplit("/", 1)[0] for u in units}
    flows = sorted({(u["name"], c) for u in units for c in u["calls"]
                    if c in NAMES})
    return {
      "entry_points": sorted(e for s in summaries for e in s["entry_points"]),
      "flows": flows,
      "sinks": sorted({(u["name"], DANGEROUS[c]) for u in units
                       for c in u["calls"] if c in DANGEROUS}),
      "boundaries": [(a, b, comp[a], comp[b]) for a, b in flows
                     if TRUST[comp[a]] < TRUST[comp[b]]],
    }

MAP = synthesise(SUMMARIES, UNITS)
print("ENTRY POINTS   ", MAP["entry_points"])
print("DATA FLOWS")
for a, b in MAP["flows"]:
    print(f"   {a} -> {b}")
print("SINKS")
for u, res in MAP["sinks"]:
    print(f"   {u:16s}touches the {res}")
print("TRUST BOUNDARY CROSSINGS")
for a, b, ca, cb in MAP["boundaries"]:
    print(f"   {a + ' -> ' + b:34s}{ca} (trust {TRUST[ca]}) -> "
          f"{cb} (trust {TRUST[cb]})")

adj = defaultdict(list)
for a, b in MAP["flows"]:
    adj[a].append(b)

def reaches(start, seen=None):
    seen = seen or set()
    if start in seen:
        return set()
    out = {start}
    for n in adj[start]:
        out |= reaches(n, seen | {start})
    return out

# sorted(), not the set: a reachability report that lists the same entry points
# in a different order on every machine cannot be diffed between two scans, and
# diffing scans is the whole point of deriving the map rather than drawing it.
print("\nSINKS REACHABLE FROM AN ENTRY POINT")
for e in MAP["entry_points"]:
    for u, res in MAP["sinks"]:
        if u in reaches(e):
            print(f"   {e:16s} -> {u:16s} touches the {res}")

SOURCES_V2 = dict(SOURCES)
SOURCES_V2["src/api/bookings.py"] += '''
def admin_export(request):
    """HTTP GET /admin/export - was internal-only until this morning."""
    return store(load_booking(request.args["ref"], request.args["owner"]),
                 request.args["name"])
'''

units2 = [u for p, s in sorted(SOURCES_V2.items()) for u in units_of(s, p)]
NAMES = {u["name"] for u in units2}
by_dir2 = defaultdict(list)
for u in units2:
    by_dir2[u["file"].rsplit("/", 1)[0]].append(u)
map2 = synthesise([summarise(d, us) for d, us in sorted(by_dir2.items())], units2)

before, after = set(MAP["entry_points"]), set(map2["entry_points"])
print(f"entry points before : {sorted(before)}")
print(f"entry points after  : {sorted(after)}")
print(f"NEW                 : {sorted(after - before)}")
print(f"flows {len(MAP['flows'])} -> {len(map2['flows'])}, "
      f"boundary crossings {len(MAP['boundaries'])} -> {len(map2['boundaries'])}")
print()
print("One function. A new untrusted entry point now reaches both the database")
print("and the filesystem, and two new edges cross a trust boundary. A threat")
print("model drawn in a workshop last quarter says nothing about any of it.")
assert after - before == {"admin_export"}
assert len(map2["boundaries"]) > len(MAP["boundaries"])
assert MAP["entry_points"] == ["get_booking", "upload_voucher"]

# ------------------------------------ the same task, against a real model
# Offline this is a labelled replay; with an open-weight model served
# from Kaggle it is the same code calling a real one.

TASK = 'Summarise what this component does in one sentence, then name its trust boundary.\n\nFiles: src/api/bookings.py\nExports: get_booking(request), upload_voucher(request)\nCallers: the public HTTP router. Calls into: src/data/reports.py, src/data/docs.py'

REPLAY = 'Accepts traveller HTTP requests for bookings and voucher uploads, passing both straight into the data layer.\nTrust boundary: every parameter here arrives from the public internet, so the edge between src/api and src/data is where untrusted input crosses into a component that reaches the database and the filesystem.'

answer, used, model = ask(TASK, replay=REPLAY,
            system='You summarise code components for a security architecture map. Two sentences, no preamble.',
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

label, held = ("names a trust boundary", "trust" in answer.lower() or "boundary" in answer.lower())
print()
print(f"property checked : {label}")
print(f"held on {used:12s} : {held}")
print()
print("Same code, same assertions, two possible backends. Offline the answer is")
print("the replay and is labelled as one; with a served model it is the model's.")
