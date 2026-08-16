"""B1 (part 1) — The AppSec pipeline, phases 1 to 3. Sessions B1.1–B1.7.

The whole track is one artefact built in order: a five-phase, fifteen-stage
automated application-security pipeline.

    [Ingestion & Mapping] → [Threat Modelling] → [Discovery]
        → [Dynamic Validation] → [Reporting]

    Phase 1 · Ingestion & Structural Mapping
        1 historical parsing        2 structural indexing          → B1.1
        3 component summarisation   4 architecture synthesis       → B1.2
    Phase 2 · Threat Modelling & Strategy
        5 threat modelling                                         → B1.3
        6 strategic planning                                       → B1.4
    Phase 3 · Analysis & Filtering
        7 vulnerability auditing                                   → B1.5
        8 deduplication             9 contextual verification      → B1.6
       10 feasibility filtering                                    → B1.7

Phases 4 and 5 continue in track_b1b.py, and B1.16 closes the track with Google
Mantis as a bonus: a real implementation of this pipeline, mapped stage by stage
onto what you built.
"""

from .skills import SKILL_RUNTIME

PIPELINE_NOTE = """
> **Where you are in the pipeline.**
>
> ```
> [Ingestion & Mapping] ──> [Threat Modelling] ──> [Discovery]
>          └─ stages 1-4         └─ stages 5-6        └─ stages 7-10
>                    ──> [Dynamic Validation] ──> [Reporting]
>                              └─ stages 11-14        └─ stage 15
> ```
"""

MODEL_NOTE = """
> **About the model in this notebook.** It runs offline against a deterministic
> stand-in so the lesson executes on a Kaggle kernel with no network. The
> stand-in is not a language model and is labelled as such wherever it appears.
> To run the identical pipeline stage against a real open-weight model:
>
> ```bash
> ollama pull glm-4.6            # or kimi-k2, llama3.3
> export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
> ```
"""

EXERCISES: dict[str, dict] = {

"B1.1": {
 "concept": """
Most review starts at the diff. That is the smallest possible context and it
throws away the single best predictor you have: **this repository has already
told you where it breaks.**

Phase 1 of the pipeline fixes that, and it begins with two stages that run
before any analysis:

**Stage 1 — Historical parsing.** Extract prior vulnerabilities, the commits
that fixed them, and pull-request history. Files that have been fixed for
security reasons before are dramatically more likely to be fixed again. This is
one of the oldest empirical results in software engineering and almost nobody
wires it into a scanner.

**Stage 2 — Structural indexing.** Break the codebase into *semantic units* —
functions, classes, modules — and index how they relate. Not lines, not files.
A scanner that reasons over lines cannot answer "who calls this?", and every
later stage needs that answer.

Together these produce the two inputs the rest of the pipeline runs on: a
**risk-ranked file list** and a **structural index**.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 1 — historical parsing\n\n"
         "A realistic slice of repository history: commits, their subjects, and "
         "which of them were security fixes."),
  ("py", '''import re, math
from dataclasses import dataclass, field
from collections import Counter, defaultdict

@dataclass(frozen=True)
class Commit:
    sha: str; subject: str; files: tuple; days_ago: int

HISTORY = [
 Commit("a1b2c3d", "fix(auth): reject empty session tokens (CVE-2025-0091)",
        ("src/auth.py", "src/session.py"), 420),
 Commit("b2c3d4e", "refactor: extract render helper", ("src/render.py",), 400),
 Commit("c3d4e5f", "fix(billing): SQL injection in report filter (CVE-2025-1188)",
        ("src/billing.py",), 300),
 Commit("d4e5f6a", "feat: add CSV export", ("src/billing.py", "src/export.py"), 260),
 Commit("e5f6a7b", "security: patch path traversal in doc fetch",
        ("src/docs.py",), 210),
 Commit("f6a7b8c", "chore: bump deps", ("requirements.txt",), 180),
 Commit("a7b8c9d", "fix(auth): timing leak in token compare",
        ("src/auth.py",), 150),
 Commit("b8c9d0e", "feat: pagination on reports", ("src/billing.py",), 120),
 Commit("c9d0e1f", "fix: harden docs path join after report", ("src/docs.py",), 60),
 Commit("d0e1f2a", "style: formatting", ("src/render.py", "src/export.py"), 30),
]

SECURITY_MARKERS = re.compile(
    r"\\b(cve-\\d{4}-\\d+|security|injection|traversal|xss|ssrf|auth|hardcoded|"
    r"leak|sanitis|sanitiz|escap)\\w*", re.I)

def is_security_fix(c):
    return bool(SECURITY_MARKERS.search(c.subject))

sec = [c for c in HISTORY if is_security_fix(c)]
print(f"{len(HISTORY)} commits, {len(sec)} security-relevant\\n")
for c in sec:
    print(f"   {c.sha}  {c.days_ago:>4}d  {c.subject[:56]}")
    print(f"{'':14s}touched {list(c.files)}")
'''),
  ("py", '''def risk_zones(history, half_life_days=180):
    """Prior-defect density, decayed by age. Recent security fixes weigh more."""
    score = defaultdict(float)
    fixes = defaultdict(int)
    churn = Counter()
    for c in history:
        for f in c.files:
            churn[f] += 1
            if is_security_fix(c):
                fixes[f] += 1
                score[f] += math.exp(-c.days_ago / half_life_days)
    rows = []
    for f in churn:
        rows.append({"file": f, "commits": churn[f], "security_fixes": fixes[f],
                     "risk": round(score[f], 3)})
    return sorted(rows, key=lambda r: -r["risk"])

zones = risk_zones(HISTORY)
print(f"{'file':22s}{'commits':>9}{'sec fixes':>11}{'risk':>8}")
print("-" * 52)
for r in zones:
    print(f"{r['file']:22s}{r['commits']:>9}{r['security_fixes']:>11}{r['risk']:>8}")
print("\\nsrc/auth.py and src/docs.py are the repeat zones. Nothing has been")
print("scanned yet — this ordering comes entirely from history.")
'''),
  ("md", "## 3 · Stage 2 — structural indexing\n\n"
         "Now index the code into semantic units. `ast` does the real work here; "
         "in a polyglot repo this is what tree-sitter is for."),
  ("py", '''import ast

SOURCES = {
 "src/auth.py": \'\'\'
def compare_token(supplied, stored):
    return supplied == stored

def login(request):
    user = lookup(request["user"])
    if user and compare_token(request["token"], user.token):
        return make_session(user)
    return None
\'\'\',
 "src/billing.py": \'\'\'
def build_filter(owner):
    return "WHERE owner = '" + owner + "'"

def list_reports(conn, owner):
    return conn.execute("SELECT * FROM reports " + build_filter(owner))
\'\'\',
 "src/docs.py": \'\'\'
def safe_join(base, name):
    return base + "/" + name

def fetch(base, name):
    return open(safe_join(base, name)).read()
\'\'\',
}

@dataclass
class Unit:
    name: str; file: str; line: int; calls: tuple; params: tuple

def index(sources):
    units, by_name = [], {}
    for path, src in sources.items():
        tree = ast.parse(src)
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            calls = tuple(sorted({
                (c.func.id if isinstance(c.func, ast.Name) else
                 getattr(c.func, "attr", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)} - {""}))
            u = Unit(fn.name, path, fn.lineno, calls,
                     tuple(a.arg for a in fn.args.args))
            units.append(u); by_name[fn.name] = u
    return units, by_name

units, by_name = index(SOURCES)
print(f"{'unit':16s}{'file':16s}{'line':>5}  params → calls")
print("-" * 74)
for u in units:
    print(f"{u.name:16s}{u.file:16s}{u.line:>5}  {list(u.params)} → {list(u.calls)}")
'''),
  ("md", "## 4 · Where it breaks — an index of files cannot answer the question\n\n"
         "The whole point of semantic units is the relationships between them. "
         "Here is the question every later stage asks, and what each kind of "
         "index can say about it."),
  ("py", '''def callers_of(name, units):
    return [u.name for u in units if name in u.calls]

QUESTION = "who reaches safe_join(), and with what?"
print(QUESTION)
print(f"   line-based index : cannot answer — 'safe_join' appears in 2 places")
print(f"   file-based index : 'it is in src/docs.py'")
print(f"   semantic index   : callers = {callers_of('safe_join', units)}, "
      f"reached from fetch(base, name)")

reverse = {u.name: callers_of(u.name, units) for u in units}
print("\\nreverse call index:")
for name, callers in reverse.items():
    print(f"   {name:16s}← {callers or '(entry point)'}")
entry_points = [n for n, c in reverse.items() if not c]
print(f"\\nentry points (nothing calls them): {entry_points}")
'''),
  ("py", '''# Stage 1 + Stage 2 combined: the pipeline's actual input.
def phase1_partial(history, sources):
    zones = {r["file"]: r["risk"] for r in risk_zones(history)}
    units, _ = index(sources)
    out = []
    for u in units:
        out.append({"unit": u.name, "file": u.file,
                    "historical_risk": zones.get(u.file, 0.0),
                    "params": list(u.params), "calls": list(u.calls)})
    return sorted(out, key=lambda r: -r["historical_risk"])

pipeline_input = phase1_partial(HISTORY, SOURCES)
print(f"{'unit':16s}{'file':16s}{'hist risk':>11}")
print("-" * 44)
for r in pipeline_input:
    print(f"{r['unit']:16s}{r['file']:16s}{r['historical_risk']:>11.3f}")

top = pipeline_input[0]["file"]
assert top == "src/auth.py", top
print(f"\\nAnalysis budget goes to {top} first — decided before a single rule ran.")
print("Note why docs.py ranks below it: the recent 'harden docs path join' commit")
print("does not match the security markers, so it scores nothing. Marker quality")
print("is the whole accuracy of stage 1, and it is worth tuning on your own history.")
'''),
 ],
 "expect": "Four of ten commits match the security markers. `src/auth.py` ranks "
           "highest on decayed risk (0.53) — two dated security fixes, the more "
           "recent dominating — followed by `src/docs.py` (0.31) and "
           "`src/billing.py` (0.19), purely from history. Note that a recent "
           "'harden docs path join' commit scores nothing because it matches no "
           "marker. The structural index extracts six functions with their "
           "parameters and calls, the reverse index identifies `login`, "
           "`list_reports` and `fetch` as entry points, and the combined Phase 1 "
           "output orders units by historical risk before any scanning.",
 "challenge": "Run the stage-1 query against a real repository: `git log "
              "--name-only --grep='CVE\\|security\\|injection'`. Rank the files by "
              "how often they appear. That list usually surprises people, and it "
              "is free.",
},

"B1.2": {
 "concept": """
Stages 1 and 2 produced units and their call relationships. That is still a
pile of functions. Phase 1 finishes by turning it into something a threat model
can be derived from.

**Stage 3 — Component summarisation.** Generate a localised summary per
directory or module: what it is for, what it talks to, what data passes through
it. Localised is the important word — summarising the whole repository at once
produces a paragraph that is true of every repository.

**Stage 4 — Architecture synthesis.** Compile those summaries into a single map
with three things on it:

- **entry points** — where untrusted input arrives,
- **data flows** — how it travels between components,
- **trust boundaries** — where it crosses from less trusted to more trusted.

The map is the artefact. Every later stage consumes it: threat modelling reads
the boundaries, planning allocates against them, feasibility filtering walks the
flows.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", MODEL_NOTE),
  ("md", "## 2 · Stage 3 — summarise each component, locally"),
  ("py", '''import ast
from dataclasses import dataclass, field
from collections import defaultdict

SOURCES = {
 "src/web/handlers.py": \'\'\'
def get_report(request):
    """HTTP GET /reports/<id> — request.args is user-controlled."""
    return render(load_report(request.args["id"], request.args["owner"]))

def upload_doc(request):
    """HTTP POST /docs — multipart body is user-controlled."""
    return store(request.files["doc"], request.args["name"])
\'\'\',
 "src/data/reports.py": \'\'\'
def load_report(report_id, owner):
    return DB.execute("SELECT * FROM reports WHERE id=" + report_id +
                      " AND owner='" + owner + "'")
\'\'\',
 "src/data/docs.py": \'\'\'
def store(blob, name):
    path = "/srv/docs/" + name
    open(path, "wb").write(blob)
    return path
\'\'\',
 "src/util/render.py": \'\'\'
def render(rows):
    return "\\\\n".join(str(r) for r in rows)
\'\'\',
}

def units_of(src, path):
    tree = ast.parse(src)
    out = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        calls = sorted({(c.func.id if isinstance(c.func, ast.Name)
                         else getattr(c.func, "attr", ""))
                        for c in ast.walk(fn) if isinstance(c, ast.Call)} - {""})
        doc = ast.get_docstring(fn) or ""
        # file + line, never a bare name: two `handler` functions in different
        # files are two different units, and merging them loses a finding
        out.append({"name": fn.name, "file": path, "line": fn.lineno,
                    "params": [a.arg for a in fn.args.args],
                    "calls": calls, "doc": doc})
    return out

ALL_UNITS = [u for p, s in SOURCES.items() for u in units_of(s, p)]

DANGEROUS = {"execute": "database", "open": "filesystem", "write": "filesystem",
             "system": "shell", "get": "network"}

def summarise_component(directory, units):
    """Stage 3 — a LOCAL summary. Deterministic here; a model does this in production."""
    names = [u["name"] for u in units]
    external = sorted({c for u in units for c in u["calls"]
                       if c not in names and c in DANGEROUS})
    outbound = sorted({c for u in units for c in u["calls"] if c in
                       {x["name"] for x in ALL_UNITS} and c not in names})
    entry = [u["name"] for u in units if u["doc"].startswith("HTTP")]
    return {"component": directory, "units": names, "entry_points": entry,
            "talks_to": outbound,
            "touches": sorted({DANGEROUS[c] for c in external})}

by_dir = defaultdict(list)
for u in ALL_UNITS:
    by_dir["/".join(u["file"].split("/")[:-1])].append(u)

SUMMARIES = [summarise_component(d, us) for d, us in sorted(by_dir.items())]
for s in SUMMARIES:
    print(f"{s['component']}")
    print(f"   units       {s['units']}")
    print(f"   entry pts   {s['entry_points'] or '—'}")
    print(f"   talks to    {s['talks_to'] or '—'}")
    print(f"   touches     {s['touches'] or '—'}")
    print()
'''),
  ("md", "## 3 · Stage 4 — synthesise the architecture map"),
  ("py", '''def synthesise(summaries, units):
    by_name = {u["name"]: u for u in units}
    entry_points, flows, sinks = [], [], []
    for s in summaries:
        for e in s["entry_points"]:
            entry_points.append({"unit": e, "component": s["component"],
                                 "input": "HTTP request (untrusted)"})
    for u in units:
        for c in u["calls"]:
            if c in by_name:
                flows.append((u["name"], c))
            elif c in DANGEROUS:
                sinks.append({"unit": u["name"], "sink": c,
                              "resource": DANGEROUS[c]})
    return {"entry_points": entry_points, "flows": sorted(set(flows)), "sinks": sinks}

MAP = synthesise(SUMMARIES, ALL_UNITS)
print("ENTRY POINTS (untrusted input arrives here)")
for e in MAP["entry_points"]:
    print(f"   {e['unit']:14s} {e['component']:22s} {e['input']}")
print("\\nDATA FLOWS")
for a, b in MAP["flows"]:
    print(f"   {a} → {b}")
print("\\nSINKS (state changes / external resources)")
for s in MAP["sinks"]:
    print(f"   {s['unit']:14s} {s['sink']:10s} {s['resource']}")
'''),
  ("md", "## 4 · Trust boundaries — the part the map exists for\n\n"
         "A boundary is any edge where data crosses from a less-trusted component "
         "into a more-trusted one. Those edges are where every finding in the rest "
         "of the pipeline will turn out to live."),
  ("py", '''TRUST = {"src/web": 0, "src/data": 2, "src/util": 1}   # 0 = untrusted edge

def boundaries(flows, units):
    comp = {u["name"]: "/".join(u["file"].split("/")[:-1]) for u in units}
    out = []
    for a, b in flows:
        ca, cb = comp[a], comp[b]
        if TRUST.get(ca, 0) < TRUST.get(cb, 0):
            out.append({"edge": f"{a} → {b}", "from": ca, "to": cb,
                        "crossing": f"trust {TRUST[ca]} → {TRUST[cb]}"})
    return out

B = boundaries(MAP["flows"], ALL_UNITS)
print("TRUST BOUNDARY CROSSINGS")
for b in B:
    print(f"   {b['edge']:28s}{b['from']:10s} → {b['to']:10s} ({b['crossing']})")

reachable_sinks = []
entry_names = {e["unit"] for e in MAP["entry_points"]}
adj = defaultdict(list)
for a, b in MAP["flows"]: adj[a].append(b)
def walk(start, seen=None):
    seen = seen or set()
    if start in seen: return set()
    seen |= {start}
    out = {start}
    for n in adj[start]: out |= walk(n, seen)
    return out
# sorted(), not the set itself: a reachability report that lists the same
# entry points in a different order on every machine cannot be diffed between
# two scans, and diffing scans is the whole point of mapping the architecture.
for e in sorted(entry_names):
    for s in MAP["sinks"]:
        if s["unit"] in walk(e):
            reachable_sinks.append((e, s["unit"], s["resource"]))
print("\\nSINKS REACHABLE FROM AN ENTRY POINT")
for e, u, res in reachable_sinks:
    print(f"   {e:14s} → {u:14s} touches {res}")
assert reachable_sinks
'''),
  ("py", '''# Verify: the map must change when the architecture changes.
SOURCES_V2 = dict(SOURCES)
SOURCES_V2["src/web/handlers.py"] = SOURCES["src/web/handlers.py"] + \'\'\'
def admin_export(request):
    """HTTP GET /admin/export — user-controlled, previously internal only."""
    return store(load_report(request.args["id"], request.args["owner"]),
                 request.args["name"])
\'\'\'
units_v2 = [u for p, s in SOURCES_V2.items() for u in units_of(s, p)]
by_dir2 = defaultdict(list)
for u in units_v2: by_dir2["/".join(u["file"].split("/")[:-1])].append(u)
map_v2 = synthesise([summarise_component(d, us) for d, us in sorted(by_dir2.items())],
                    units_v2)

before = {e["unit"] for e in MAP["entry_points"]}
after  = {e["unit"] for e in map_v2["entry_points"]}
print(f"entry points before: {sorted(before)}")
print(f"entry points after : {sorted(after)}")
print(f"NEW ENTRY POINT    : {sorted(after - before)}")
print(f"flows before {len(MAP['flows'])} → after {len(map_v2['flows'])}")
print("\\nOne function added. A new untrusted entry point now reaches both the")
print("database and the filesystem. That delta is what B1.3 threat-models.")
assert after - before
'''),

  ("md", """## 6 · Write the procedure down as an agent skill

You have just run four stages by hand. The next repository needs the same four,
and so does the next agent. An **agent skill** is how that procedure stops
living in your head.

A skill is a markdown file with a small header:

```
---
name: appsec-repo-recon
description: >-
  Build the structural and historical map of a codebase before any security
  analysis. Use at the start of an application security review, when asked to
  find entry points, sinks, trust boundaries or attack surface ...
allowed-tools: Read, Grep, Glob, Bash
---

# the procedure, written for whoever runs it next
```

Three fields, three different jobs:

- **`name`** identifies it.
- **`description`** is the **routing key**, not documentation. An agent decides
  whether to load a skill by reading this sentence and nothing else. A
  description that says "helps with security stuff" never fires, and two
  descriptions that overlap fire the wrong one.
- **`allowed-tools`** bounds it. This skill reads a repository; it never writes
  to one, and that is enforceable rather than merely stated.

The body carries the procedure and — the part that matters here — an **output
contract**: the exact JSON shape Phase 2 will join against. A skill with a
contract is testable. A skill without one is a wish."""),

  ("py", SKILL_RUNTIME),
  ("skill", "appsec/appsec-repo-recon"),

  ("md", "## 7 · The contract is executable — check the map you just built\n\n"
         "The skill promised a shape. You built a map. Those two claims can be "
         "checked against each other mechanically, which is the whole reason to "
         "write the contract down."),
  ("py", '''# Express the map this lesson built in the shape the skill promises.
contract = contract_of(body)
at = {u["name"]: u for u in ALL_UNITS}
EXPOSURE = {"src/web": "public", "src/util": "internal", "src/data": "internal"}

recon = {"architecture_map": {
  "entry_points": [
      {"unit": e["unit"], "file": at[e["unit"]]["file"], "line": at[e["unit"]]["line"],
       "exposure": EXPOSURE.get("/".join(at[e["unit"]]["file"].split("/")[:-1]), "internal")}
      for e in MAP["entry_points"]],
  "sinks": [
      {"unit": s["unit"], "file": at[s["unit"]]["file"], "resource": s["resource"]}
      for s in MAP["sinks"]],
  "flows": [[a, b] for a, b in MAP["flows"]],
  "boundaries": [
      {"edge": b["edge"], "from_trust": TRUST[b["from"]], "to_trust": TRUST[b["to"]]}
      for b in B],
  "reachable": [
      {"entry": e, "sink": u, "path": [e, u]} for e, u, _ in reachable_sinks],
  # carried forward from stage 1 in B1.1 — each notebook stands alone, so the
  # result of the previous stage arrives as a literal rather than an import
  "hotspots": [{"file": "src/auth.py", "fix_count": 3},
               {"file": "src/data/reports.py", "fix_count": 1}],
  "caveats": ["single language; vendored trees not indexed"],
}}

problems = check(recon, contract)
print(f"conformance check: {len(problems)} problem(s)")
for p in problems:
    print("   ", p)
assert not problems, problems
print("\\nThe map satisfies the contract, so Phase 2 can consume it without")
print("negotiating a format.")
'''),

  ("md", "## 8 · Where it breaks — conformance is not accuracy\n\n"
         "A contract check is cheap to pass and easy to over-read. Watch what "
         "else satisfies it."),
  ("py", '''# An empty map. Every required key present, every type correct.
hollow = {"architecture_map": {
    "entry_points": [], "sinks": [], "flows": [], "boundaries": [],
    "reachable": [], "hotspots": [], "caveats": [],
}}
print(f"hollow map, conformance problems: {len(check(hollow, contract))}")
print(f"real map,   conformance problems: {len(check(recon, contract))}")
print()
print("Both conform. One of them found nothing at all.")
print()
print("Conformance is a statement about the serialiser: it is close to free by")
print("construction, and an empty result scores perfectly. Accuracy is the")
print("expensive part and the contract cannot measure it. Any pipeline that")
print("reports '100% schema-valid' as a quality metric is reporting this number.")
print()
print(f"what the contract can tell you : shape is right ({len(check(recon, contract))} problems)")
print(f"what only the map can tell you : {len(recon['architecture_map']['reachable'])} "
      f"reachable entry->sink pairs, {len(recon['architecture_map']['boundaries'])} "
      f"boundary crossings")
assert not check(hollow, contract), "the hollow map conforms - that is the point"
'''),

  ("md", "## 9 · The control — route by description, and refuse a tie\n\n"
         "An agent picks a skill by reading descriptions. That makes the "
         "description a piece of security-relevant configuration: route wrong "
         "and you run the wrong procedure with the wrong tools."),
  ("py", '''# Four skills from this repository, by description alone.
CATALOGUE = {
 "appsec-repo-recon": {"description":
   "Build the structural and historical map of a codebase before any security "
   "analysis. Use at the start of an application security review, when asked to "
   "find entry points, sinks, trust boundaries or attack surface."},
 "appsec-threat-model": {"description":
   "Turn an architecture map into a ranked, testable threat model and an audit "
   "plan. Use after repository reconnaissance, when asked what could go wrong."},
 "appsec-vuln-audit": {"description":
   "Audit code for vulnerabilities against a threat model, then deduplicate, "
   "verify in context, and filter to what is actually reachable. Use when asked "
   "to review code for security bugs or check whether a finding is a false positive."},
 "detection-triage": {"description":
   "Triage security alerts with the context needed to reach a defensible verdict. "
   "Use when working an alert queue or deciding whether an alert is a true positive."},
}

for task in ["map the attack surface of this repo before we review it",
             "what could go wrong with this architecture",
             "is this alert a false positive"]:
    pick, scores, margin = route(task, CATALOGUE)
    verdict = f"-> {pick}" if margin > 0 else f"-> AMBIGUOUS (tie at {scores[pick]})"
    print(f"{task[:44]:46s} {verdict}  margin={margin}")

print()
print("The third routes with margin 0. 'false positive' appears in the audit")
print("skill's description and 'alert' in the triage skill's, so both score the")
print("same and the winner is whichever sorted first alphabetically - an")
print("arbitrary answer wearing a confident face.")
print()
print("That is why route() returns the margin. A tie is a configuration bug in")
print("the descriptions, and the fix is to make them disjoint, not to let the")
print("sort decide which procedure runs.")
assert route("is this alert a false positive", CATALOGUE)[2] == 0
'''),
 ],
 "expect": "Three components summarise with their entry points, outbound calls "
           "and the resources they touch. The architecture map lists two HTTP "
           "entry points, the data flows between units, and three sinks. Two "
           "trust-boundary crossings are identified, both from `src/web` into "
           "`src/data`, and both database and filesystem sinks are reachable from "
           "an entry point. Adding one handler introduces a new entry point and "
           "extends the flow graph.",
 "challenge": "Draw the trust-boundary edges for one service you own. The "
              "interesting output is not the diagram — it is the count of sinks "
              "reachable from an untrusted entry point, which is the number Phase "
              "3 will spend its budget on.",
},

"B1.3": {
 "concept": """
Phase 2 opens with the stage everyone claims to do and almost nobody re-runs.

**Stage 5 — Threat modelling.** Read the architecture map from stage 4 and
derive, mechanically: high-value assets, untrusted entry points, and the attack
vectors that connect them.

The word doing the work is *mechanically*. A threat model produced by hand in a
workshop is a snapshot; it is stale the moment an entry point is added, and
adding an entry point is a Tuesday. A threat model **derived from the map** is
regenerated whenever the map changes, so the useful artefact is not the model —
it is the **diff between two models**.

That reframing is what makes threat modelling a pipeline stage rather than a
document. It also means the output has to be data: ranked, machine-readable, and
consumable by stage 6, which allocates the analysis budget against it.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 5 — derive threats from the map"),
  ("py", '''from dataclasses import dataclass, field
from collections import defaultdict

# The stage-4 output, as data.
ARCH = {
 "entry_points": [
   {"unit": "get_report",   "component": "src/web", "auth": "session"},
   {"unit": "upload_doc",   "component": "src/web", "auth": "session"},
   {"unit": "health",       "component": "src/web", "auth": "none"},
 ],
 "flows": [("get_report", "load_report"), ("get_report", "render"),
           ("upload_doc", "store"), ("load_report", "execute"),
           ("store", "open")],
 "sinks": [{"unit": "load_report", "sink": "execute", "resource": "database"},
           {"unit": "store", "sink": "open", "resource": "filesystem"}],
 "assets": {"database": {"data": ("customer", "financial"), "value": 5},
            "filesystem": {"data": ("documents",), "value": 3},
            "session_store": {"data": ("credentials",), "value": 5}},
}

VECTOR_FOR = {
 "database":   [("CWE-89",  "SQL injection", 5)],
 "filesystem": [("CWE-22",  "path traversal", 4), ("CWE-434", "unrestricted upload", 4)],
 "shell":      [("CWE-78",  "command injection", 5)],
}

def reachable(entry, flows):
    adj = defaultdict(list)
    for a, b in flows: adj[a].append(b)
    seen, stack = set(), [entry]
    while stack:
        n = stack.pop()
        for m in adj[n]:
            if m not in seen: seen.add(m); stack.append(m)
    return seen

def threat_model(arch):
    threats = []
    for ep in arch["entry_points"]:
        reach = reachable(ep["unit"], arch["flows"])
        for sink in arch["sinks"]:
            if sink["unit"] not in reach: continue
            asset = arch["assets"].get(sink["resource"], {"value": 1, "data": ()})
            for cwe, name, base in VECTOR_FOR.get(sink["resource"], []):
                score = base + asset["value"] + (2 if ep["auth"] == "none" else 0)
                threats.append({
                    "entry": ep["unit"], "auth": ep["auth"],
                    "sink": sink["unit"], "resource": sink["resource"],
                    "cwe": cwe, "vector": name, "score": score,
                    "path": f"{ep['unit']} → … → {sink['unit']}",
                    "data_at_risk": list(asset["data"])})
    # deterministic on every machine: score first, then a stable tiebreak
    return sorted(threats, key=lambda t: (-t["score"], t["cwe"], t["entry"], t["sink"]))

TM = threat_model(ARCH)
print(f"{'entry':13s}{'sink':13s}{'cwe':9s}{'vector':22s}{'score':>6}  data at risk")
print("-" * 88)
for t in TM:
    print(f"{t['entry']:13s}{t['sink']:13s}{t['cwe']:9s}{t['vector']:22s}"
          f"{t['score']:>6}  {t['data_at_risk']}")
print(f"\\n{len(TM)} threats derived. No human wrote this; it fell out of the map.")
'''),
  ("md", "## 3 · Where it breaks — the model that was true last quarter\n\n"
         "Add one entry point. The hand-written threat model does not change, "
         "because documents do not change themselves."),
  ("py", '''ARCH_V2 = {**ARCH,
 "entry_points": ARCH["entry_points"] + [
   {"unit": "admin_export", "component": "src/web", "auth": "none"}],
 "flows": ARCH["flows"] + [("admin_export", "load_report"),
                           ("admin_export", "store")]}

TM2 = threat_model(ARCH_V2)

def diff(before, after):
    key = lambda t: (t["entry"], t["sink"], t["cwe"])
    b = {key(t): t for t in before}
    a = {key(t): t for t in after}
    # sorted() over a set difference is NOT deterministic across processes:
    # set iteration order depends on PYTHONHASHSEED, and a stable sort then
    # preserves that order for equal scores. Sort the keys first.
    return {"new": [a[k] for k in sorted(a.keys() - b.keys())],
            "removed": [b[k] for k in sorted(b.keys() - a.keys())],
            "max_before": max(t["score"] for t in before),
            "max_after": max(t["score"] for t in after)}

d = diff(TM, TM2)
print(f"threats before {len(TM)} → after {len(TM2)}")
print(f"max severity   {d['max_before']} → {d['max_after']}")
print("\\nNEW THREATS:")
# full tiebreak, so equal scores order the same way on every machine
for t in sorted(d["new"], key=lambda t: (-t["score"], t["cwe"], t["entry"], t["sink"])):
    print(f"   [{t['score']:>2}] {t['cwe']:9s}{t['path']:34s}auth={t['auth']}")
print("\\nOne unauthenticated handler introduced 3 new threats, two of them")
print("higher-scoring than anything in the original model.")
assert d["new"] and d["max_after"] >= d["max_before"]
'''),
  ("md", "## 4 · The control — regenerate on every map change, and gate on the delta"),
  ("py", '''def threat_gate(before, after, max_new_critical=0, critical_at=11):
    d = diff(before, after)
    new_crit = [t for t in d["new"] if t["score"] >= critical_at]
    ok = len(new_crit) <= max_new_critical
    return ok, {"new_threats": len(d["new"]), "new_critical": len(new_crit),
                "detail": [f"{t['cwe']} via {t['path']} (score {t['score']})"
                           for t in new_crit]}

ok, info = threat_gate(TM, TM2)
print(f"CI gate: {'PASS' if ok else 'FAIL'}")
for k, v in info.items(): print(f"   {k:14s}{v}")

print("\\nafter requiring auth on the new handler:")
ARCH_V3 = {**ARCH_V2,
 "entry_points": [{**e, "auth": "session"} if e["unit"] == "admin_export" else e
                  for e in ARCH_V2["entry_points"]]}
TM3 = threat_model(ARCH_V3)
ok3, info3 = threat_gate(TM, TM3)
print(f"CI gate: {'PASS' if ok3 else 'FAIL'}   new_critical={info3['new_critical']}")
print("\\nThe gate did not ask anyone to write a document. It compared two")
print("generated models and refused a specific, named regression.")
'''),
 ],
 "expect": "Six threats are derived from the map, ranked by combined vector, "
           "asset value and authentication, with SQL injection against customer "
           "and financial data scoring highest. Adding one unauthenticated "
           "handler produces three new threats and raises the maximum score. The "
           "CI gate fails on the new criticals and passes once the handler "
           "requires a session.",
 "challenge": "Wire the threat diff into CI for one service: regenerate on every "
              "merge and fail when a new critical path appears. It is the "
              "cheapest form of continuous threat modelling that exists, and it "
              "needs no workshop.",
},

"B1.4": {
 "concept": """
**Stage 6 — Strategic planning.** You now have a ranked threat model. This stage
decides *where to spend the analysis budget* and *which tool or agent to point at
each target*.

The default is a uniform sweep: run every rule over every file. It is simple,
and it scales cost with repository size rather than with risk — so on a large
monorepo the deep, expensive analysis gets turned off for everything, including
the parts that needed it.

Allocation makes the trade explicit. Three inputs:

- **threat rank** from stage 5,
- **historical risk** from stage 1,
- **tool fit** — rules are cheap and precise on known patterns; model review is
  expensive and finds what rules cannot express (B1.5 measures both).

The output is an assignment: which analyser runs against which boundary, with
what budget. And the honest measure of a good allocation is not coverage — it is
**threat-weighted coverage**, because covering the health endpoint thoroughly is
not an achievement.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 6 — the budget, and two ways to spend it"),
  ("py", '''from dataclasses import dataclass

@dataclass(frozen=True)
class Target:
    name: str; file: str; threat_score: int; historical_risk: float; loc: int

TARGETS = [
 Target("load_report → execute", "src/data/reports.py", 12, 0.82, 40),
 Target("store → open",          "src/data/docs.py",     9, 0.91, 30),
 Target("render",                "src/util/render.py",   2, 0.05, 15),
 Target("health",                "src/web/health.py",    1, 0.00, 10),
 Target("upload_doc",            "src/web/handlers.py",  9, 0.30, 60),
 Target("get_report",            "src/web/handlers.py", 11, 0.30, 60),
]

ANALYSERS = {
 # name          cost/100 LOC   finds                         precision
 "grep rules":   (1,   {"CWE-798"},                          0.50),
 "taint rules":  (4,   {"CWE-89", "CWE-78", "CWE-22"},       1.00),
 "model review": (40,  {"CWE-89","CWE-78","CWE-22","CWE-863","CWE-434"}, 0.85),
}
BUDGET = 30         # arbitrary units for one CI run — deliberately tight,
                    # because an unconstrained budget hides the whole problem

def uniform(targets, analyser, budget):
    cost_per = ANALYSERS[analyser][0]
    spend, covered = 0, []
    for t in sorted(targets, key=lambda t: t.name):
        c = cost_per * t.loc / 100
        if spend + c > budget: break
        spend += c; covered.append(t)
    return {"strategy": f"uniform · {analyser}", "spend": round(spend, 1),
            "covered": covered}

def allocated(targets, budget):
    """Deep analysis on high-threat targets, cheap rules everywhere else."""
    ranked = sorted(targets, key=lambda t: -(t.threat_score + t.historical_risk * 3))
    spend, plan = 0.0, []
    for t in ranked:
        for analyser in ("model review", "taint rules", "grep rules"):
            c = ANALYSERS[analyser][0] * t.loc / 100
            wants_deep = (t.threat_score + t.historical_risk * 3) >= 9
            if analyser == "model review" and not wants_deep: continue
            if spend + c <= budget:
                spend += c; plan.append((t, analyser)); break
    return {"strategy": "allocated by threat rank", "spend": round(spend, 1),
            "plan": plan}

u = uniform(TARGETS, "model review", BUDGET)
a = allocated(TARGETS, BUDGET)
print(f"{u['strategy']:34s}spend {u['spend']:>6}  covered {len(u['covered'])}/{len(TARGETS)}")
for t in u["covered"]: print(f"      {t.name}")
print(f"\\n{a['strategy']:34s}spend {a['spend']:>6}  covered {len(a['plan'])}/{len(TARGETS)}")
for t, an in a["plan"]: print(f"      {t.name:24s}{an}")
'''),
  ("md", "## 3 · Where it breaks — coverage is the wrong metric"),
  ("py", '''def coverage(plan_targets, targets):
    return len(plan_targets) / len(targets)

def threat_weighted_coverage(plan_targets, targets):
    total = sum(t.threat_score for t in targets)
    got = sum(t.threat_score for t in plan_targets)
    return got / total

u_targets = u["covered"]
a_targets = [t for t, _ in a["plan"]]

print(f"{'strategy':34s}{'coverage':>10}{'threat-weighted':>18}")
print("-" * 64)
for label, ts in (("uniform · model review", u_targets),
                  ("allocated by threat rank", a_targets)):
    print(f"{label:34s}{coverage(ts, TARGETS):>10.0%}{threat_weighted_coverage(ts, TARGETS):>18.0%}")

print("\\nThe uniform sweep spent its whole budget alphabetically and covered")
print("the health endpoint before it reached the SQL sink.")
missed = [t.name for t in TARGETS if t not in u_targets and t.threat_score >= 9]
print(f"high-threat targets the uniform sweep never reached: {missed}")
assert missed
'''),
  ("md", "## 4 · The control — allocate, then prove the allocation was right"),
  ("py", '''def plan_report(plan, targets, budget):
    spend = sum(ANALYSERS[an][0] * t.loc / 100 for t, an in plan)
    covered = [t for t, _ in plan]
    deep = [t.name for t, an in plan if an == "model review"]
    uncovered_high = [t.name for t in targets
                      if t not in covered and t.threat_score >= 9]
    return {"budget": budget, "spend": round(spend, 1),
            "threat_weighted_coverage": round(threat_weighted_coverage(covered, targets), 3),
            "deep_analysis_on": deep,
            "uncovered_high_threat": uncovered_high,
            "acceptable": not uncovered_high}

r = plan_report(a["plan"], TARGETS, BUDGET)
for k, v in r.items(): print(f"{k:26s}{v}")
assert r["acceptable"]

print("\\nsame budget, if someone doubles the repo with low-risk code:")
BLOAT = TARGETS + [Target(f"vendor_{i}", f"vendor/{i}.py", 1, 0.0, 200)
                   for i in range(1, 9)]
a2 = allocated(BLOAT, BUDGET)
r2 = plan_report(a2["plan"], BLOAT, BUDGET)
print(f"   threat-weighted coverage {r['threat_weighted_coverage']:.0%} → "
      f"{r2['threat_weighted_coverage']:.0%}")
print(f"   uncovered high-threat targets: {r2['uncovered_high_threat'] or 'none'}")
print("\\nAllocation is what stops repository growth from silently degrading")
print("the analysis of the parts that matter.")
'''),

  ("md", "## 6 · The skill that carries Phase 2\n\n"
         "Stages 5 and 6 are now a procedure rather than a one-off. The skill "
         "below is the version an agent runs, and its contract is the reason "
         "the plan can be handed to Phase 3 without a conversation.\n\n"
         "Note what the contract insists on: `score_inputs` alongside every "
         "score. A severity you cannot decompose is a severity nobody can "
         "argue with — and an unarguable severity is one nobody fixes."),
  ("py", SKILL_RUNTIME),
  ("skill", "appsec/appsec-threat-model"),

  ("py", '''contract = contract_of(body)

# The weakness class each target would be, named rather than implied — the
# contract needs it and "distinct CWEs covered" is meaningless without it.
CWE_OF = {"load_report → execute": "CWE-89", "store → open": "CWE-22",
          "render": "CWE-79", "health": "CWE-200",
          "upload_doc": "CWE-434", "get_report": "CWE-22"}

def cost_of(target, analyser):
    return ANALYSERS[analyser][0] * target.loc / 100

# The plan this lesson produced, in the shape the skill promises.
# threat_index points into `threat_model` below, which is TARGETS order.
# a["plan"] is in *ranked* order, so enumerating it would number the threats
# by rank and every index in the contract would point at the wrong threat.
IDX = {t.name: i for i, t in enumerate(TARGETS)}
sel = [{"threat_index": IDX[t.name], "cost": cost_of(t, analyser),
        "why": analyser}
       for t, analyser in a["plan"]]
chosen = {t.name for t, _ in a["plan"]}
plan = {
 "threat_model": [
   {"cwe": CWE_OF[t.name], "entry": t.name.split(" ")[0], "sink": t.name.split(" ")[-1],
    "path": t.name.split(" → "), "crosses_boundary": t.threat_score >= 6,
    "auth": "none" if t.threat_score >= 8 else "user",
    "score": t.threat_score,
    "score_inputs": {"exposure": t.threat_score,
                     "resource": round(t.historical_risk, 2),
                     "boundary": 2 if t.threat_score >= 6 else 1}}
   for t in TARGETS],
 # What the budget deferred is *depth*, not targets: everything gets some
 # analyser, but the ones that wanted model review and got taint rules are
 # exactly the gap the report must disclose.
 "plan": {"budget": float(BUDGET), "selected": sel,
          "deferred": [{"threat_index": IDX[t.name],
                        "why": f"wanted model review, budget allowed {analyser}"}
                       for t, analyser in a["plan"]
                       if (t.threat_score + t.historical_risk * 3) >= 9
                       and analyser != "model review"],
          "coverage": {"threat_weighted": float(r2["threat_weighted_coverage"]),
                       "distinct_cwes": len({CWE_OF[t.name] for t, _ in a["plan"]})}},
}
problems = check(plan, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\\nselected {len(sel)} of {len(TARGETS)} threats; "
      f"{len(plan['plan']['deferred'])} of them wanted deep review and did not get it")
print(f"distinct CWEs covered: {plan['plan']['coverage']['distinct_cwes']}")
print()
for d in plan["plan"]["deferred"]:
    print(f"   deferred: {TARGETS[d['threat_index']].name:22s} {d['why']}")
print()
print("`deferred` is not bookkeeping. Every target got *an* analyser, so a")
print("coverage number counting targets would read 100%. What the budget")
print("actually cut was depth, on three of the four highest-threat targets.")
print("That distinction travels to the report as the scope statement, and a")
print("plan that drops it produces a report that overclaims.")
assert plan["plan"]["deferred"], "a budget that defers nothing proves nothing"
'''),
 ],
 "expect": "On a tight budget the uniform model-review sweep covers only 2 of 6 "
           "targets — alphabetically, so it reaches the health endpoint before the "
           "SQL sink — giving 33% coverage but only 27% threat-weighted coverage, "
           "and missing all three high-threat targets. The allocated plan covers "
           "all six within the same budget at 100% threat-weighted coverage, puts "
           "deep model review on the SQL sink, and still holds 90% when the "
           "repository doubles in size with low-risk code.",
 "challenge": "Compute threat-weighted coverage for your current scanning setup. "
              "If you scan everything uniformly, the number equals your raw "
              "coverage — which means you have no allocation strategy, only a "
              "budget that will eventually be cut.",
},

"B1.5": {
 "concept": """
**Stage 7 — Vulnerability auditing.** The deep-dive analysis stage, and the one
people think of as "SAST". It has had three generations, and knowing what each
can and cannot see is what stops you buying the wrong one.

**Generation 1 — grep.** Pattern-match dangerous constructs. Fast, zero setup,
fires on every occurrence whether reachable or not. Precision is poor, so it gets
muted.

**Generation 2 — rules with dataflow.** Semgrep, CodeQL, OpenGrep. Parse to an
AST or graph and track *taint*: does untrusted input reach a dangerous sink?
Precision improves enormously. The cost is that a rule only finds the pattern
someone wrote it for.

**Generation 3 — model review.** An open-weight model reads the code and reasons.
No rule needs to exist first, which is exactly its value — and it also invents
bugs that are not there, confidently.

The mistake is treating generation 3 as a replacement for generation 2. The
combination that works: rules for what rules do well, deterministically; the
model for what rules cannot express; and everything the model says treated as a
**hypothesis** until stages 8–12 confirm it.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", MODEL_NOTE),
  ("md", "## 2 · Generation 1 — grep, and why it gets muted\n\n"
         "The safe functions in this corpus matter more than the buggy ones: a "
         "scanner that fires on parameterised SQL is one nobody runs twice."),
  ("py", '''CODE = {
"db.py": \'\'\'
def get_user(conn, name):
    # BUG: user input concatenated into SQL
    return conn.execute("SELECT * FROM users WHERE name = \\'" + name + "\\'")

def get_user_safe(conn, name):
    # parameterised — the driver escapes it
    return conn.execute("SELECT * FROM users WHERE name = ?", (name,))

def audit_note(conn, msg):
    # a constant string. No user input anywhere.
    return conn.execute("INSERT INTO audit(msg) VALUES (\\'startup\\')")
\'\'\',
"ops.py": \'\'\'
import os, subprocess

def ping(host):
    # BUG: shell string built from user input
    os.system("ping -c1 " + host)

def ping_safe(host):
    subprocess.run(["ping", "-c1", host], check=True)
\'\'\',
"files.py": \'\'\'
def read_doc(base, filename):
    # BUG: path joined from untrusted input
    return open(base + "/" + filename).read()
\'\'\',
}
import re
GREP_RULES = [("CWE-89","SQL injection",r"execute\\("),
              ("CWE-78","command injection",r"os\\.system|subprocess"),
              ("CWE-22","path traversal",r"open\\(")]
def gen1(code):
    return [(cwe, name, f, i, ln.strip())
            for f, src in code.items()
            for i, ln in enumerate(src.splitlines(), 1)
            for cwe, name, pat in GREP_RULES if re.search(pat, ln)]

g1 = gen1(CODE)
print(f"generation 1 (grep): {len(g1)} findings")
for cwe, name, f, i, ln in g1:
    print(f"   {cwe:8s}{f}:{i:<3} {ln[:52]}")
'''),
  ("py", '''TRUTH = {("CWE-89","db.py",4), ("CWE-78","ops.py",6), ("CWE-22","files.py",4)}
def score(findings, label):
    got = {(c, f, i) for c, _, f, i, _ in findings}
    tp, fp, fn = len(got & TRUTH), len(got - TRUTH), len(TRUTH - got)
    prec = tp/(tp+fp) if tp+fp else 0.0
    rec  = tp/(tp+fn) if tp+fn else 0.0
    print(f"{label:32s} tp={tp} fp={fp} fn={fn}  precision={prec:.2f} recall={rec:.2f}")
    return prec, rec
score(g1, "generation 1 · grep")
print("\\nfalse positives:")
for cwe, name, f, i, ln in g1:
    if (cwe, f, i) not in TRUTH: print(f"   {f}:{i:<3} {ln[:56]}")
'''),
  ("md", "## 3 · Generation 2 — taint rules\n\n"
         "The improvement is not a better pattern. It is a different question: "
         "*does untrusted input reach this sink?* A function parameter is "
         "untrusted; a string literal is not."),
  ("py", '''import ast
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
'''),
  ("md", "## 4 · Generation 3 — what rules structurally cannot see\n\n"
         "Generation 2 is perfect on this corpus. So why involve a model? Because "
         "a rule only finds what someone wrote it for. Here is a bug with no "
         "rule: an authorization check that is *present* and wrong."),
  ("py", '''CODE["authz.py"] = \'\'\'
def can_delete(user, doc):
    # Reads "or" where it means "and". No sink, no taint, no pattern.
    if user.is_admin or user.id == doc.owner_id or doc.is_public:
        return True
    return False
\'\'\'
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
print("\\ngeneration 3 (model review):")
for fname in ("authz.py", "db.py"):
    for f in model.review(fname, CODE[fname]):
        print(f"   {f['cwe']:9s}{fname}:{f['line']:<3} conf={f['confidence']:.2f}  "
              f"{f['rationale'][:52]}")
print("\\nIt found the authorization bug neither earlier generation can see.")
print("It also invented a SQL injection in a function with a constant string.")
'''),
  ("py", '''# Stage 7 output: rules + gated model hypotheses. Confirmation is stages 8-12.
GATE = 0.70
def stage7(code, rule, model, gate=GATE):
    findings, suppressed = [], []
    for fname, src in code.items():
        for cwe, name, f, i, snip in rule.scan(fname, src):
            findings.append({"src":"rules","cwe":cwe,"file":f,"line":i,
                             "confidence":1.0,"status":"confirmed-by-rule"})
        for m in model.review(fname, src):
            row = {"src":"model","cwe":m["cwe"],"file":fname,"line":m["line"],
                   "confidence":m["confidence"],"status":"HYPOTHESIS"}
            (findings if m["confidence"] >= gate else suppressed).append(row)
    seen, dedup = set(), []
    for f in sorted(findings, key=lambda r: r["src"]):
        k = (f["cwe"], f["file"], f["line"])
        if k in seen: continue
        seen.add(k); dedup.append(f)
    return dedup, suppressed

final, suppressed = stage7(CODE, rule, model)
print(f"stage 7 emits {len(final)} findings, {len(suppressed)} suppressed below {GATE}")
for f in final:
    print(f"   [{f['src']:5s}] {f['cwe']:9s}{f['file']}:{f['line']:<3} "
          f"conf={f['confidence']:.2f}  {f['status']}")
TRUTH_FULL = TRUTH | {("CWE-863","authz.py",4)}
got = {(f["cwe"], f["file"], f["line"]) for f in final}
print(f"\\ntp={len(got & TRUTH_FULL)} fp={len(got - TRUTH_FULL)} fn={len(TRUTH_FULL - got)}")
assert not (got - TRUTH_FULL) and not (TRUTH_FULL - got)
print("Every model finding is marked HYPOTHESIS. Stages 8-12 decide.")
'''),
 ],
 "expect": "Grep produces 6 findings at 50% precision, flagging the parameterised "
           "query, the constant insert and the safe subprocess call. Taint rules "
           "find exactly the 3 real injection bugs at 100% precision and recall "
           "and find nothing in `authz.py`. The model finds the authorization bug "
           "at 0.82 confidence and hallucinates one SQL injection at 0.41. Stage 7 "
           "emits 4 findings with zero false positives, every model finding "
           "marked as a hypothesis.",
 "challenge": "Point the stand-in at a real GLM-4.6 or Kimi K2 through Ollama and "
              "run it on `authz.py` ten times. The variance in what it reports — "
              "and in its confidence — decides whether you can gate on confidence "
              "at all.",
},

"B1.6": {
 "concept": """
Stage 7 ran several analysers in parallel. That produces two problems this stage
exists to solve, and they are different problems.

**Stage 8 — Deduplication.** Three analysers find the same bug and report it
three times. Worse, they report it at slightly different line numbers with
different CWE labels, so naive matching does not collapse them. An engineer who
sees the same bug three times stops trusting the count.

**Stage 9 — Contextual verification.** Cross-reference each finding against the
actual syntax and imports to weed out hallucinations. This is the cheapest,
highest-yield filter in the whole pipeline, because a model finding that
references a function that does not exist, or a module that was never imported,
is *provably* wrong — no judgement required.

The order matters: deduplicate first, then verify, or you spend verification
effort on three copies of the same claim.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · The raw output of three parallel tracks"),
  ("py", '''from dataclasses import dataclass, field

SOURCE = {
"billing.py": \'\'\'
import sqlite3

def build_filter(owner):
    return "WHERE owner = '" + owner + "'"

def list_reports(conn, owner):
    return conn.execute("SELECT * FROM reports " + build_filter(owner))

def total(conn):
    return conn.execute("SELECT SUM(amount) FROM reports").fetchone()
\'\'\'
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
'''),
  ("md", "## 3 · Stage 8 — deduplicate on the defect, not the report\n\n"
         "Two findings are the same defect if they name the same sink in the same "
         "function, even at different lines and under different CWE labels. "
         "Cluster on that, and keep the *best-evidenced* member."),
  ("py", '''import ast

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

print(f"{len(RAW)} findings → {len(deduped)} distinct defects\\n")
for d in deduped:
    file, fn, sym, cwe = d["key"]
    print(f"   {cwe:8s}{str(fn):14s}{sym:14s}merged {d['merged']} "
          f"from {d['sources']}  (kept {d['keep'].src})")
'''),
  ("md", "## 4 · Stage 9 — contextual verification against the real syntax\n\n"
         "Now check each surviving claim against the code. Three checks, all "
         "mechanical, none requiring judgement."),
  ("py", '''def verify(finding, src):
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
print(f"\\n{len(verified)} verified, {len(rejected)} rejected as hallucinations")
'''),
  ("py", '''# Verify the stage pays for itself.
STAGE7_COUNT = len(RAW)
after8 = len(deduped)
after9 = len(verified)
print(f"stage 7 emitted        {STAGE7_COUNT}")
print(f"after stage 8 (dedup)  {after8}   ({1-after8/STAGE7_COUNT:.0%} removed)")
print(f"after stage 9 (verify) {after9}   ({1-after9/STAGE7_COUNT:.0%} removed overall)")

TRUE_DEFECTS = {("billing.py", "list_reports", "execute", "CWE-89")}
found = {d["key"] for d in deduped if any(d["keep"] is f for f, _ in verified)}
tp = len(found & TRUE_DEFECTS); fp = len(found - TRUE_DEFECTS)
print(f"\\nsurviving: tp={tp} fp={fp}")
for f, _ in rejected:
    print(f"   rejected {f.cwe} on {f.symbol!r} — provably not in the code")
assert any("DB_PASSWORD" in f.symbol for f, _ in rejected)
assert any("os.system" in f.symbol for f, _ in rejected)
print("\\nBoth hallucinations named things that are not in the file. No model,")
print("no judgement, no cost — just the AST disagreeing with the claim.")
'''),
 ],
 "expect": "Seven raw findings collapse to four distinct defects, with the "
           "CWE-943 alias merging into CWE-89 and the taint result kept over grep "
           "and model duplicates. Contextual verification then rejects the "
           "hallucinated `DB_PASSWORD` and `os.system` findings because neither "
           "symbol appears in the file and `os` is never imported, leaving the "
           "real SQL injection.",
 "challenge": "Add a fourth verification check: does the CWE class match the sink "
              "type? A CWE-22 finding on a `conn.execute` call is provably "
              "mislabelled, and that check costs nothing to run.",
},

"B1.7": {
 "concept": """
**Stage 10 — Feasibility filtering.** The last stage of Phase 3, and the one
that decides whether anyone gets paged.

A verified finding is a real bug in the code. It is not necessarily a real risk,
because the code may be unreachable: dead code, a test fixture, an internal
function no external caller can drive, a branch behind a feature flag that has
been off for two years.

Triaging an unreachable finding costs exactly as much as triaging one on the
login path, and there are usually far more of them. So this stage partitions
findings into three buckets — and the third bucket is the honest one:

- **reachable** — a path exists from an untrusted entry point to the sink,
- **unreachable** — no path exists,
- **unknown** — the analysis cannot decide, usually because of dynamic dispatch,
  reflection, or a framework that wires callers at runtime.

Reporting `unknown` as `unreachable` is how a pipeline quietly drops real bugs.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 10 — build the call graph from entry points"),
  ("py", '''import ast
from collections import defaultdict

SOURCE = \'\'\'
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
\'\'\'

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
print(f"\\nentry points: {ENTRY}")
print(f"dynamic dispatch present in: {DYNAMIC}")
'''),
  ("py", '''SINKS = {"load_report": ("CWE-89", "DB.execute"),
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
print(f"\\n{ {k: v for k, v in buckets.items()} }")
'''),
  ("md", "## 3 · Where it breaks — collapsing `unknown` into `unreachable`\n\n"
         "The tempting simplification. It makes the queue shorter and it is how "
         "real bugs get dropped, because dynamic dispatch is exactly where "
         "framework-wired handlers live."),
  ("py", '''def naive_filter(sinks, reached):
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
print(f"\\nfindings silently dropped by two-bucket filtering: {dropped}")
print("legacy_export is reachable through the runtime handler registry in this")
print("application. Static analysis cannot see that, and 'unreachable' is a lie.")
assert dropped
'''),
  ("md", "## 4 · The control — route each bucket to a different place"),
  ("py", '''ROUTING = {
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

print(f"\\n{queue_load(buckets, ROUTING)}")
print("\\nThe unknown bucket is not a failure of the analysis. It is the handover")
print("to Phase 4, which answers reachability by running the thing.")
'''),

  ("md", "## 6 · Phase 3 as a skill — and the counts that police it\n\n"
         "Stages 7 to 10 only ever *shrink* the list. That is a property worth "
         "enforcing rather than trusting, so the skill's contract carries a "
         "`counts` object and the rule that it must never increase.\n\n"
         "A pipeline whose `verified` count exceeds its `deduped` count has "
         "invented findings somewhere after the audit stage — and that is far "
         "easier to do by accident than it sounds, because a verification step "
         "that expands one finding per code path looks perfectly reasonable "
         "from the inside."),
  ("py", SKILL_RUNTIME),
  ("skill", "appsec/appsec-vuln-audit"),

  ("py", '''contract = contract_of(body)

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
print(f"\\ncounts raw->deduped->verified->feasible : {seq}")
print(f"monotonically non-increasing            : {all(x >= y for x, y in zip(seq, seq[1:]))}")
assert all(x >= y for x, y in zip(seq, seq[1:])), seq
'''),

  ("md", "## 7 · Where it breaks — deduplicating on the wrong key\n\n"
         "The skill says to collapse on the **defect identity**, "
         "`(cwe, file, unit, sink_expression)`, and never on the message text. "
         "Here is why that sentence is in the procedure."),
  ("py", '''# The same three defects, as three analysers actually report them.
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
print(f"\\nconformance problems: {len(check(bad, contract))}   <- still zero")
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
'''),
 ],
 "expect": "The call graph identifies three entry points, one of which uses "
           "dynamic dispatch. `load_report` is reachable, `debug_dump` and "
           "`legacy_export` are unknown rather than unreachable because runtime "
           "handler resolution cannot be ruled out. Two-bucket filtering silently "
           "drops both, and the three-bucket routing sends the unknowns to Phase 4 "
           "instead of paging or discarding them.",
 "challenge": "Count how many `unknown` cases your own reachability analysis "
              "produces, and find out what your tooling does with them. If it "
              "reports them as clean, the number of real bugs you are dropping is "
              "the size of that bucket.",
},
}
