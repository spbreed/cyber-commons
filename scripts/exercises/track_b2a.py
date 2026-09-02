"""B1 (part 1) — The AppSec pipeline, phases 1 to 3. Sessions B2.1–B2.5.

The whole track is one artefact built in order: a five-phase, fifteen-stage
automated application-security pipeline, and the lessons run in exactly the
order the stages do.

    [Ingestion & Mapping] → [Threat Modelling] → [Discovery]
        → [Dynamic Validation] → [Reporting]

    Phase 1 · Ingestion & Structural Mapping
        1 historical parsing        2 structural indexing
        3 component summarisation   4 architecture synthesis       → B2.1
    Phase 2 · Threat Modelling
        5 threat modelling, from six static inputs                 → B2.2
    Phase 3 · Analysis & Filtering
        7 vulnerability auditing, three generations of SAST        → B2.3
        8 deduplication             9 contextual verification      → B2.4
       10 feasibility filtering                                    → B2.5

Stage 6 (strategic planning) is not a lesson of its own. Allocation is a
property of the stage that spends the budget rather than a stage that spends
none, so it is taught where the money actually goes: the audit agent in B2.3
decides where to run the model pass, and B2.5 decides what is worth
reproducing.

Phases 4 and 5 continue in track_b1b.py, and B2.14 closes the track with Google
Mantis as a bonus: a real implementation of this pipeline, mapped stage by stage
onto what you built.
"""

from .skills import SKILL_RUNTIME, runtime_step

RUNTIME_STEP = runtime_step()

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

from . import diagrams as D

EXERCISES: dict[str, dict] = {

"B2.1": {
 "concept": """
Most review starts at the diff. That is the smallest possible context, and it
throws away the single best predictor you have: **this repository has already
told you where it breaks.**

Phase 1 is four stages, and they run before any analysis. They take a
repository and produce the one artefact everything downstream consumes — a map.

**Stage 1 — Historical parsing.** Extract prior vulnerabilities, the commits
that fixed them, and pull-request history. Files that have been fixed for
security reasons before are dramatically more likely to be fixed again. It is
one of the oldest empirical results in software engineering, and almost nobody
wires it into a scanner.

**Stage 2 — Structural indexing.** Break the code into *semantic units* —
functions, classes, modules — and index how they call each other. Not lines,
not files. A scanner that reasons over lines cannot answer "who reaches this?",
and every later stage needs that answer.

**Stage 3 — Component summarisation.** One short summary per directory: what it
is for, what it talks to, what data passes through it. *Local* is the important
word — summarise the whole repository at once and you get a paragraph that is
true of every repository.

**Stage 4 — Architecture synthesis.** Compile the summaries into a single map
carrying three things: **entry points** where untrusted input arrives, **data
flows** between components, and **trust boundaries** where data crosses from
less trusted to more trusted.

The map is the artefact. Stage 5 reads its boundaries, stage 7 prioritises
against them, stage 10 walks its flows. And because it is derived rather than
drawn, it changes when the code changes — which is the property the last cell
in this lesson demonstrates and the reason the next lesson works at all.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 1 — historical parsing\n\n"
         "A slice of the CyberTravels bookings repository: commits, their "
         "subjects, and which of them were security fixes. Nothing has been "
         "scanned yet."),
  ("py", '''import ast, math, re
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
    r"\\b(cve-\\d{4}-\\d+|security|injection|traversal|xss|ssrf|auth|hardcoded|"
    r"leak|sanitis|sanitiz|escap)\\w*", re.I)

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

print("\\nsrc/api/bookings.py and src/data/docs.py are the repeat zones, and the")
print("ordering comes entirely from history - no rule has run.")
print("Note what stage 1 missed: 'harden the voucher path join' is the most")
print("recent security commit in the list and matches no marker, so it scores")
print("nothing. Marker quality IS the accuracy of this stage.")'''),
  ("md", "## 3 · Stage 2 — structural indexing\n\n"
         "Index the code into semantic units. `ast` does the work here; in a "
         "polyglot repository this is what tree-sitter is for."),
  ("py", '''SOURCES = {
 "src/api/bookings.py": \'\'\'
def get_booking(request):
    """HTTP GET /bookings/<ref> - request.args is traveller-controlled."""
    return render(load_booking(request.args["ref"], request.args["owner"]))

def upload_voucher(request):
    """HTTP POST /vouchers - the multipart body is traveller-controlled."""
    return store(request.files["doc"], request.args["name"])
\'\'\',
 "src/data/reports.py": \'\'\'
def load_booking(ref, owner):
    return DB.execute("SELECT * FROM bookings WHERE ref=" + ref +
                      " AND owner='" + owner + "'")
\'\'\',
 "src/data/docs.py": \'\'\'
def store(blob, name):
    path = "/srv/vouchers/" + name
    open(path, "wb").write(blob)
    return path
\'\'\',
 "src/util/render.py": \'\'\'
def render(rows):
    return "\\\\n".join(str(r) for r in rows)
\'\'\',
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

print("\\n\\"who reaches store(), and with what?\\"")
print("   line-based index : cannot answer - the token appears in two places")
print("   file-based index : \\"it is in src/data/docs.py\\"")
print(f"   semantic index   : callers = {callers_of('store')}, and its input is "
      f"a traveller-supplied filename")
entries = sorted(u["name"] for u in UNITS if not callers_of(u["name"]))
print(f"\\nentry points (nothing in the repository calls them): {entries}")'''),
  ("model", {
   "title": "Stage 3, with a model actually doing the summarising",
   "task": ("Summarise what this component does in one sentence, then name its "
            "trust boundary.\n\nFiles: src/api/bookings.py\nExports: "
            "get_booking(request), upload_voucher(request)\nCallers: the public "
            "HTTP router. Calls into: src/data/reports.py, src/data/docs.py"),
   "replay": ("Accepts traveller HTTP requests for bookings and voucher "
              "uploads, passing both straight into the data layer.\nTrust "
              "boundary: every parameter here arrives from the public internet, "
              "so the edge between src/api and src/data is where untrusted "
              "input crosses into a component that reaches the database and "
              "the filesystem."),
   "system": ("You summarise code components for a security architecture map. "
              "Two sentences, no preamble."),
   "check": ('("names a trust boundary", "trust" in answer.lower() '
             'or "boundary" in answer.lower())')}),
  ("md", "## 5 · Stage 3 — summarise each component, locally\n\n"
         "The model call above is what stage 3 looks like in production. Below "
         "is the deterministic version, so the rest of the lesson has a fixed "
         "input to work from."),
  ("py", '''def summarise(component, units):
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
    print(f"   touches     {s['touches'] or '-'}\\n")'''),
  ("md", "## 6 · Stage 4 — synthesise the map, and find the boundaries\n\n"
         "A trust boundary is any edge where data crosses from a less-trusted "
         "component into a more-trusted one. Those edges are where every "
         "finding in the rest of the pipeline turns out to live."),
  ("py", '''TRUST = {"src/api": 0, "src/util": 1, "src/data": 2}   # 0 = untrusted edge

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
print("\\nSINKS REACHABLE FROM AN ENTRY POINT")
for e in MAP["entry_points"]:
    for u, res in MAP["sinks"]:
        if u in reaches(e):
            print(f"   {e:16s} -> {u:16s} touches the {res}")'''),
  ("md", "## 7 · The map changes when the code changes\n\n"
         "This is the whole reason for deriving it. One function is added; the "
         "map is regenerated; the delta is the thing the next lesson threat-models."),
  ("py", '''SOURCES_V2 = dict(SOURCES)
SOURCES_V2["src/api/bookings.py"] += \'\'\'
def admin_export(request):
    """HTTP GET /admin/export - was internal-only until this morning."""
    return store(load_booking(request.args["ref"], request.args["owner"]),
                 request.args["name"])
\'\'\'

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
assert MAP["entry_points"] == ["get_booking", "upload_voucher"]'''),
  ("md", "## 8 · Write the four stages down as an agent skill\n\n"
         "You have just run Phase 1 by hand. The next repository needs the same "
         "four stages and so does the next agent, so the procedure belongs in a "
         "file rather than in your head. This is the one in this repository:"),
  RUNTIME_STEP,
  ("skill", "appsec/appsec-repo-recon"),
 ],
 "expect": "Four of ten commits match the security markers, and `src/api/"
           "bookings.py` ranks highest on decayed risk purely from history — "
           "with the most recent security commit scoring nothing, because it "
           "matches no marker. The structural index extracts five functions and "
           "identifies two entry points. Component summaries name what each "
           "directory touches, and the synthesised map shows both entry points "
           "reaching the database and the filesystem across a trust boundary. "
           "Adding one function adds a third entry point and two more boundary "
           "crossings.",
 "challenge": "Run stage 1 against a repository you own: `git log --name-only "
              "--grep='CVE\\|security\\|injection'`, then rank the files by how "
              "often they appear. That list usually surprises people, and it is "
              "free. Then check how many of your recent security fixes your "
              "markers would have missed.",
},

"B2.2": {
 "concept": """
Phase 2 opens with the stage everyone claims to do and almost nobody re-runs.

**Stage 5 — Threat modelling.** Derive, mechanically: high-value assets,
untrusted entry points, and the attack vectors that connect them.

The word doing the work is *mechanically*. A threat model produced by hand in a
workshop is a snapshot; it is stale the moment an entry point is added, and
adding an entry point is a Tuesday. A model **derived** is regenerated whenever
its inputs change, so the useful artefact is not the model — it is the **diff
between two models**.

### Derived from what, exactly

The architecture map from stage 4 is the first input and it is not sufficient.
It tells you what the code *could* reach. It says nothing about whether that
path is exposed, what identity walks it, or whether anything could leave at the
end of it — and those three questions are the difference between a finding and
a fire.

Every one of the answers is already written down somewhere in the estate, as
configuration, in a machine-readable file. The stage's job is to read all of it:

| Input | What only it can tell you |
|---|---|
| **Code analysis** — the stage-4 map | which sinks an entry point reaches |
| **CSPM findings** | that the bucket behind that sink is public, today |
| **Cloud security policy** — security groups, ingress, WAF | whether the entry point is reachable from the internet at all |
| **Entitlement and role access** | what the caller's role may do once it is through |
| **IAM** — trust policies, assume-role chains | who can become that role, and from where |
| **Egress policy** — NetworkPolicy, firewall rules | whether anything can leave once it is in |

Read only the code and you produce a threat model that is identical for two
deployments of the same repository, one of which is behind a private load
balancer with no egress and one of which is not. That model is wrong about both.

The output has to be data — ranked, machine-readable, diffable — because the
next stage prioritises against it and CI gates on the delta.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · The six inputs, and what each one contributes"),
  ("html", D.flow(
    [D.column("code", [
       D.card("&#128269;", "stage-4 map", "entry points, flows, sinks, trust "
              "boundaries", colour=D.DEFEND, note="WHAT COULD BE REACHED"),
     ]),
     D.column("exposure", [
       D.card("&#9729;&#65039;", "cloud security policy", "security groups, "
              "ingress, WAF — is this entry point on the internet",
              colour=D.SECURE),
       D.card("&#128680;", "CSPM findings", "the bucket behind that sink is "
              "public, today", colour=D.BAD),
     ]),
     D.column("identity", [
       D.card("&#128273;", "entitlement and roles", "what the caller may do "
              "once it is through", colour=D.SECURE),
       D.card("&#128100;", "IAM trust policy", "who can assume that role, and "
              "from where", colour=D.SECURE, note="A2.3"),
     ]),
     D.column("exfiltration", [
       D.card("&#128683;", "egress policy", "NetworkPolicy and firewall rules "
              "— can anything leave at the end of the path", colour=D.GOOD,
              note="A3.2"),
     ]),
     D.column("output", [
       D.card("&#128202;", "ranked threats", "scored, machine-readable, and "
              "diffed against the last run", colour=D.DEFEND),
     ])],
    caption="Read only the first column and you get a threat model that is "
            "identical for two deployments of the same repository — one behind "
            "a private load balancer with no egress, one not. It is wrong about "
            "both.")),
  ("md", "## 3 · Stage 5 — derive threats from all six"),
  ("py", '''from collections import defaultdict

# --- input 1: the stage-4 architecture map ---------------------------------
ARCH = {
 "entry_points": [
   {"unit": "get_booking",    "component": "src/api", "auth": "session"},
   {"unit": "upload_voucher", "component": "src/api", "auth": "session"},
   {"unit": "health",         "component": "src/api", "auth": "none"},
 ],
 "flows": [("get_booking", "load_booking"), ("get_booking", "render"),
           ("upload_voucher", "store"), ("load_booking", "execute"),
           ("store", "open")],
 "sinks": [{"unit": "load_booking", "sink": "execute", "resource": "database"},
           {"unit": "store", "sink": "open", "resource": "voucher_bucket"}],
 "assets": {"database":       {"data": ("customer", "financial"), "value": 5},
            "voucher_bucket": {"data": ("documents",),            "value": 3}},
}

# --- inputs 2-6: what the rest of the estate already knows -----------------
CLOUD_POLICY = {           # security groups / ingress: is it on the internet?
 "get_booking":    {"exposed": "internet", "waf": True},
 "upload_voucher": {"exposed": "internet", "waf": False},
 "health":         {"exposed": "vpc-only", "waf": False},
}
CSPM = [                   # live posture findings, not code
 {"resource": "voucher_bucket", "finding": "bucket policy allows public read",
  "severity": 4},
]
ENTITLEMENTS = {           # what the running role may do
 "src/api": {"db:select", "db:update", "s3:GetObject", "s3:PutObject"},
}
IAM = {                    # who can become that role
 "src/api": {"assumable_by": ["ci-deploy-role"], "mfa_required": True},
}
EGRESS = {                 # NetworkPolicy / firewall: can anything leave?
 "src/api": {"default_deny": True, "allowed": ["db.prod:5432"]},
}

VECTOR_FOR = {
 "database":       [("CWE-89", "SQL injection", 5)],
 "voucher_bucket": [("CWE-22", "path traversal", 4),
                    ("CWE-434", "unrestricted upload", 4)],
}

def reachable(entry, flows):
    adj = defaultdict(list)
    for a, b in flows:
        adj[a].append(b)
    seen, stack = set(), [entry]
    while stack:
        for m in adj[stack.pop()]:
            if m not in seen:
                seen.add(m); stack.append(m)
    return seen

def threat_model(arch, cloud, cspm, entitlements, iam, egress):
    threats = []
    cspm_by_resource = defaultdict(int)
    for f in cspm:
        cspm_by_resource[f["resource"]] += f["severity"]
    for ep in arch["entry_points"]:
        reach = reachable(ep["unit"], arch["flows"])
        exposure = cloud.get(ep["unit"], {})
        for sink in arch["sinks"]:
            if sink["unit"] not in reach:
                continue
            asset = arch["assets"][sink["resource"]]
            comp = ep["component"]
            for cwe, name, base in VECTOR_FOR.get(sink["resource"], []):
                why, score = [], base + asset["value"]
                if ep["auth"] == "none":
                    score += 2; why.append("unauthenticated")
                # exposure: the single biggest correction the map cannot make
                if exposure.get("exposed") == "internet":
                    score += 2; why.append("internet-facing")
                else:
                    score -= 3; why.append("vpc-only")
                if exposure.get("exposed") == "internet" and not exposure.get("waf"):
                    score += 1; why.append("no WAF")
                score += cspm_by_resource[sink["resource"]]
                if cspm_by_resource[sink["resource"]]:
                    why.append("live CSPM finding")
                # entitlement: write beats read, and the role decides which
                if {"db:update", "s3:PutObject"} & entitlements.get(comp, set()):
                    score += 1; why.append("role holds write")
                if "*" in iam.get(comp, {}).get("assumable_by", []):
                    score += 2; why.append("role assumable by *")
                if not egress.get(comp, {}).get("default_deny", True):
                    score += 2; why.append("egress open")
                threats.append({
                  "entry": ep["unit"], "sink": sink["unit"], "cwe": cwe,
                  "vector": name, "score": score, "why": why,
                  "path": f"{ep['unit']} -> ... -> {sink['unit']}"})
    # score first, then a full tiebreak, so two machines agree
    return sorted(threats,
                  key=lambda t: (-t["score"], t["cwe"], t["entry"], t["sink"]))

TM = threat_model(ARCH, CLOUD_POLICY, CSPM, ENTITLEMENTS, IAM, EGRESS)
print(f"{'entry':16s}{'sink':14s}{'cwe':9s}{'score':>6}  why")
print("-" * 92)
for t in TM:
    print(f"{t['entry']:16s}{t['sink']:14s}{t['cwe']:9s}{t['score']:>6}  "
          f"{', '.join(t['why'])}")
print(f"\\n{len(TM)} threats. Nobody wrote this; it fell out of six files that")
print("already existed in the estate.")'''),
  ("md", "## 4 · The same code, two estates\n\n"
         "This is the argument for reading past the map. Nothing below changes "
         "a line of the repository — only the configuration around it."),
  ("py", '''# Same repository. Private load balancer, default-deny egress, no wildcard
# trust policy, and the CSPM finding remediated.
HARDENED = threat_model(
  ARCH,
  {k: {"exposed": "vpc-only", "waf": True} for k in CLOUD_POLICY},
  [],                                                        # CSPM clean
  {"src/api": {"db:select", "s3:GetObject"}},                # read-only role
  {"src/api": {"assumable_by": ["ci-deploy-role"], "mfa_required": True}},
  {"src/api": {"default_deny": True, "allowed": ["db.prod:5432"]}},
)

print(f"{'threat':38s}{'as deployed':>13}{'hardened':>11}")
print("-" * 62)
by_key = {(t["entry"], t["sink"], t["cwe"]): t["score"] for t in HARDENED}
for t in TM:
    k = (t["entry"], t["sink"], t["cwe"])
    print(f"{t['cwe'] + '  ' + t['path']:38s}{t['score']:>13}{by_key[k]:>11}")

print(f"\\nmax severity  {max(t['score'] for t in TM)} -> "
      f"{max(t['score'] for t in HARDENED)}")
print()
print("Identical code. A model derived from the map alone would have scored")
print("these two deployments the same, and it would have been wrong about the")
print("first by understating it and wrong about the second by crying wolf.")
assert max(t["score"] for t in HARDENED) < max(t["score"] for t in TM)'''),
  ("md", "## 5 · Where it breaks — the model that was true last quarter\n\n"
         "Add one entry point. The hand-written threat model does not change, "
         "because documents do not change themselves."),
  ("py", '''ARCH_V2 = {**ARCH,
 "entry_points": ARCH["entry_points"] + [
   {"unit": "admin_export", "component": "src/api", "auth": "none"}],
 "flows": ARCH["flows"] + [("admin_export", "load_booking"),
                           ("admin_export", "store")]}
CLOUD_V2 = {**CLOUD_POLICY,
            "admin_export": {"exposed": "internet", "waf": False}}

TM2 = threat_model(ARCH_V2, CLOUD_V2, CSPM, ENTITLEMENTS, IAM, EGRESS)

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
print(f"threats before {len(TM)} -> after {len(TM2)}")
print(f"max severity   {d['max_before']} -> {d['max_after']}")
print("\\nNEW THREATS:")
for t in sorted(d["new"], key=lambda t: (-t["score"], t["cwe"], t["entry"])):
    print(f"   [{t['score']:>2}] {t['cwe']:9s}{t['path']:38s}{', '.join(t['why'])}")
assert d["new"] and d["max_after"] >= d["max_before"]'''),
  ("md", "## 6 · The control — and the gate that is not enough\n\n"
         "Regenerate on every change to *any* input, and gate on the delta. "
         "The obvious gate counts new threats. Watch what it does with a pull "
         "request that adds none."),
  ("py", '''def gate_new_only(before, after, critical_at=16):
    """The obvious gate: refuse a pull request that introduces a new critical."""
    d = diff(before, after)
    crit = [t for t in d["new"] if t["score"] >= critical_at]
    return not crit, {"new": len(d["new"]), "new_critical": len(crit)}

ok, info = gate_new_only(TM, TM2)
print(f"PR 1 - adds an unauthenticated handler   -> "
      f"{'PASS' if ok else 'FAIL'}  {info}")

# PR 2 touches no application code at all. It widens the IAM trust policy and
# removes the default-deny egress rule - two lines of terraform.
TM_TF = threat_model(ARCH, CLOUD_POLICY, CSPM, ENTITLEMENTS,
                     {"src/api": {"assumable_by": ["ci-deploy-role", "*"],
                                  "mfa_required": False}},
                     {"src/api": {"default_deny": False,
                                  "allowed": ["0.0.0.0/0"]}})
ok2, info2 = gate_new_only(TM, TM_TF)
print(f"PR 2 - two lines of terraform            -> "
      f"{'PASS' if ok2 else 'FAIL'}  {info2}")
print()
print("PR 2 introduced no new threat, so a gate that counts new threats waves")
print("it through. Every existing threat got worse:")
by_key = {(t["entry"], t["sink"], t["cwe"]): t["score"] for t in TM_TF}
for t in TM:
    k = (t["entry"], t["sink"], t["cwe"])
    print(f"   {t['cwe']:9s}{t['path']:38s}{t['score']:>3} -> {by_key[k]}")'''),
  ("md", "## 7 · The gate that is\n\nCount escalation as well as arrival. A "
         "threat that was medium and is now critical is a regression, and the "
         "pull request that caused it did not touch a line of application code."),
  ("py", '''def threat_gate(before, after, critical_at=16, max_escalation=2):
    d = diff(before, after)
    prev = {(t["entry"], t["sink"], t["cwe"]): t["score"] for t in before}
    new_crit = [t for t in d["new"] if t["score"] >= critical_at]
    escalated = [t for t in after
                 if (k := (t["entry"], t["sink"], t["cwe"])) in prev
                 and t["score"] - prev[k] > max_escalation]
    return (not new_crit and not escalated,
            {"new_critical": len(new_crit), "escalated": len(escalated),
             "detail": [f"{t['cwe']} via {t['path']}: "
                        f"{prev[(t['entry'], t['sink'], t['cwe'])]} -> {t['score']}"
                        for t in escalated]})

for label, model in (("PR 1 - unauthenticated handler", TM2),
                     ("PR 2 - two lines of terraform ", TM_TF)):
    ok, info = threat_gate(TM, model)
    print(f"{label} -> {'PASS' if ok else 'FAIL'}")
    print(f"   new_critical={info['new_critical']}  escalated={info['escalated']}")
    for line in info["detail"]:
        print(f"      {line}")

# And the fix for PR 1: require a session and put it behind the WAF.
ARCH_FIXED = {**ARCH_V2, "entry_points": [
  {**e, "auth": "session"} if e["unit"] == "admin_export" else e
  for e in ARCH_V2["entry_points"]]}
CLOUD_FIXED = {**CLOUD_V2, "admin_export": {"exposed": "internet", "waf": True}}
ok_fixed, info_fixed = threat_gate(
    TM, threat_model(ARCH_FIXED, CLOUD_FIXED, CSPM, ENTITLEMENTS, IAM, EGRESS))
print(f"\\nPR 1, after requiring auth and adding the WAF -> "
      f"{'PASS' if ok_fixed else 'FAIL'}  {info_fixed['new_critical']} critical")

print()
print("Nobody wrote a document. The gate compared generated models and refused")
print("two named regressions - and the one it would have missed is the one")
print("that changed no code, which is the majority of how estates get worse.")
assert gate_new_only(TM, TM_TF)[0]          # v1 waves the terraform PR through
assert not threat_gate(TM, TM_TF)[0]       # v2 does not
assert not threat_gate(TM, TM2)[0] and ok_fixed'''),
 ],
 "expect": "Six threats are derived from six static inputs, each carrying the "
           "reasons its score moved — internet-facing, no WAF, live CSPM "
           "finding, role holds write, role assumable by `*`, egress open. The "
           "same repository deployed behind a private load balancer with "
           "default-deny egress and a read-only role scores materially lower on "
           "every row. Adding an unauthenticated handler fails the CI gate, and "
           "so does a pull request that changes only terraform.",
 "challenge": "Take one service and write down where each of the six inputs "
              "lives — the repository, the CSPM console, the terraform, the IAM "
              "policy, the NetworkPolicy. If any of them is \"in somebody's "
              "head\", that is the input your threat model is currently "
              "guessing at, and the guess is always the optimistic one.",
},

"B2.3": {
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
  ("model", {
   "title": 'The model backend, and the third generation of SAST',
   "task": 'Is this function vulnerable? Name the CWE if so, and say which value reaches the sink.\n\ndef report(request):\n    q = "SELECT * FROM orders WHERE ref = \'" + request.args[\'ref\'] + "\'"\n    return db.execute(q)',
   "replay": "Yes - CWE-89, SQL injection. request.args['ref'] is concatenated directly into the query string and reaches db.execute unsanitised.",
   "system": 'You are a code reviewer. Answer in at most three lines.',
   "check": '("names the CWE identifier", "CWE-89" in answer.upper() or "SQL INJECT" in answer.upper())'}),
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
  ("md", """## 5 · Generation 2, as the tool you would actually run

The taint engine above is forty lines so it fits in a lesson. In production
generation 2 is Semgrep, CodeQL or OpenGrep, and a rule is a file. This is the
Semgrep rule for the same taint property the engine above implements:

```yaml
rules:
  - id: cybertravels-sql-concat
    languages: [python]
    severity: ERROR
    message: >-
      Traveller-controlled input is concatenated into a SQL string. Use a
      parameterised query.
    mode: taint
    pattern-sources:
      - pattern: $REQ.args[...]
      - pattern: $REQ.files[...]
    pattern-sinks:
      - pattern: $CONN.execute(...)
    pattern-sanitizers:
      - pattern: sqlite3.paramstyle
```

[`labs/tools/semgrep-sast/`](https://github.com/spbreed/cyber-commons/tree/main/labs/tools/semgrep-sast)
installs Semgrep 1.176.0 and runs it against a pull request from the Coding
Agent. Two things came out of that run and both matter here.

**Coverage is a configuration decision, and it is invisible.** The same file,
two ruleset widths:

```
  p/python + p/secrets: 1 finding
    line  17  ERROR   subprocess-shell-true

  seven packs: 4 findings
    line   9  ERROR   sqlalchemy-execute-raw-query
    line  14  WARNING eval-detected
    line  17  ERROR   subprocess-shell-true
    line  20  ERROR   disabled-cert-validation
```

Nothing about the file changed. On the narrow setting three real defects were
simply not looked for, and the scan exits 0 either way.

**And two defects survived both widths:**

```
  line  22  MISSED a live-looking API key on a module-level constant
  line   7  MISSED find_booking performs no authorisation check of any kind
```

The first is lexical — `p/secrets` was enabled and did not fire, because the
string matches no known provider's format. A rule could catch it, once someone
writes that rule. The second cannot be caught by any rule, because the defect is
the **absence** of a call in a function whose caller holds payments scope. That
is the boundary generation 3 exists to cross, and it is why the answer is
"both" rather than "the newer one"."""),
  ("md", """## 6 · An agent drives both, because you cannot afford to run both everywhere

Generation 2 is cheap enough to run over the whole repository. Generation 3 is
not — at four million lines the model pass costs more than the finding is
worth, and a model asked to review everything reviews nothing carefully.

So neither generation is the interesting part. **The allocation is.** An agent
sits above both, and its policy is three rules:

1. run the deterministic scanner everywhere, with the widest ruleset that is
   not noisy, because it is nearly free;
2. spend the model pass only where stage 1 said risk lives **and** the rules
   were silent — silence in a high-risk zone is the signal, not the noise;
3. mark everything the model says as a hypothesis, never a finding, because
   stages 8 to 12 are what turn one into the other."""),
  ("py", '''# What stage 1 said, and what generation 2 found. The agent has both.
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
print(f"\\nmodel pass on {len(reviewed)} of {len(CODE)} files "
      f"(${len(reviewed) * MODEL_COST_PER_FILE:.3f} rather than "
      f"${len(CODE) * MODEL_COST_PER_FILE:.3f})")

print(f"\\nstage 7 emits {len(final)}, {len(suppressed)} suppressed below 0.70")
for f in final:
    print(f"   [{f['src']:5s}] {f['cwe']:9s}{f['file']}:{f['line']:<3} "
          f"conf={f['confidence']:.2f}  {f['status']}")

TRUTH_FULL = TRUTH | {("CWE-863", "authz.py", 4)}
got = {(f["cwe"], f["file"], f["line"]) for f in final}
print(f"\\ntp={len(got & TRUTH_FULL)} fp={len(got - TRUTH_FULL)} "
      f"fn={len(TRUTH_FULL - got)}")
assert not (got - TRUTH_FULL) and not (TRUTH_FULL - got)'''),
  ("py", '''# The allocation is a bet, so measure what it costs when it loses. Move the
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
print("Every model finding above is marked HYPOTHESIS. Stages 8 to 12 decide.")'''),
 ],
 "expect": "Grep produces 6 findings at 50% precision, flagging the parameterised "
           "query, the constant insert and the safe subprocess call. Taint rules "
           "find exactly the 3 real injection bugs at 100% precision and recall "
           "and find nothing in `authz.py`. The model finds the authorization bug "
           "at 0.82 confidence and hallucinates one SQL injection at 0.41. The "
           "audit agent then runs the rules everywhere and spends the model pass "
           "on one file of four — the one where history says risk lives and the "
           "rules were silent — emitting 4 findings with zero false positives, "
           "every model finding marked as a hypothesis. The last cell shows what "
           "the allocation costs when it loses: give `authz.py` no history and "
           "the authorization bug is never reviewed.",
 "challenge": "Two things, and the second is the one people skip. Point the "
              "stand-in at a real GLM-4.6 or Kimi K2 through Ollama and run it on "
              "`authz.py` ten times — the variance in what it reports, and in its "
              "confidence, decides whether you can gate on confidence at all. "
              "Then run Semgrep against one of your own repositories at your "
              "current ruleset and at seven packs, and count the difference. "
              "Whatever that number is, it has been the number all year.",
},

"B2.4": {
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

"B2.5": {
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

  ("md", "## 8 · The same failure, from a real model\n\n"
         "Everything above is constructed. Here is the identical failure "
         "produced by an actual open-weight model — **Moonlight-16B-A3B**, "
         "Moonshot AI's MoE from the Kimi team — run on a Kaggle CPU kernel "
         "against this skill's output contract.\n\n"
         "It was given the contract and two vulnerable functions: an `open()` "
         "on a caller-supplied path, and an `os.system()` on a caller-supplied "
         "argument. Its answer is reproduced verbatim below "
         "([full run](https://github.com/spbreed/cyber-commons/blob/"
         "claude/vulnbench-setup-scheduling-81aqov/labs/kimi/"
         "moonlight-16b-completion-prompt.txt))."),
  ("py", '''# Verbatim output from Moonlight-16B-A3B on Kaggle, 2026-08-17.
# Not a paraphrase and not a stand-in: this is what the model emitted.
MODEL_OUTPUT = \'\'\'{"findings": [{"id": "F-01", "cwe": "CWE-89", "file": "report_api.py",
"line": 22, "unit": "get_report",
"evidence": "open(\'/var/reports/\' + request.args[\'name\'])",
"missing_control": "str", "occurrences": 1, "verdict": "confirmed",
"verdict_reason": "str", "feasible": true, "confidence": 0.0}],
"dropped": [], "counts": {"raw": 0, "deduped": 0, "verified": 0, "feasible": 0}}\'\'\'

model = json.loads(MODEL_OUTPUT)
problems = check(model, contract)
print(f"conformance problems: {len(problems)}")
print()
f = model["findings"][0]
print(f"evidence it cited : {f[\'evidence\']}")
print(f"CWE it assigned   : {f[\'cwe\']}  (SQL injection)")
print(f"CWE it actually is: CWE-22  (path traversal - it is open(), not a query)")
print(f"missing_control   : {f[\'missing_control\']!r}")
print(f"verdict_reason    : {f[\'verdict_reason\']!r}")
print(f"counts            : {model[\'counts\']}  while findings has {len(model[\'findings\'])}")
assert not problems, "the real model's output conforms - that is the point"
'''),

  ("md", "## 9 · Read that output again\n\n"
         "It passes the contract with zero problems, and almost nothing in it "
         "is true."),
  ("py", '''print("What a schema check can see:")
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
      f"{model[\'counts\'][\'verified\'] == len(model[\'findings\'])}  <- catches it")
print()
print("Three defects, zero schema violations. That is what a headline of")
print("'100% schema-valid' actually means as a quality metric, and it is why")
print("accuracy has to be measured against a key the model never sees.")
assert model["counts"]["verified"] != len(model["findings"])
assert f["cwe"] != "CWE-22", "the model got the weakness class wrong"
assert f["missing_control"] == "str", "the model copied the type placeholder"
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
