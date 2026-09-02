"""B1 (part 2) — The AppSec pipeline, phases 4 and 5, plus the bonus.

    Phase 4 · Dynamic Validation & Remediation
       11 sandbox replication                                      → B2.6
       12 dynamic exploitation (DAST)                              → B2.7
       13 exploit chaining                                         → B2.8
       14 remediation engineering                                  → B2.9
    Phase 5 · Governance & Reporting
       15 severity calibration and reporting                       → B2.10

    Cross-cutting
       context engineering for the pipeline                        → B2.11
       injection in your own pipeline                              → A1.9
       securing the developers' coding agents                      → B2.12
       attesting control intent for agents and MCP servers         → B2.13

    Bonus
       Google Mantis — the pipeline in production                  → B2.14
"""

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
> To run the identical stage against a real open-weight model:
>
> ```bash
> ollama pull glm-4.6            # or kimi-k2, llama3.3
> export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
> ```
"""

from .skills import SKILL_RUNTIME

from . import diagrams as D

EXERCISES: dict[str, dict] = {

"B2.6": {
 "concept": """
Phase 4 turns hypotheses into facts by running the application. That is only
safe if the thing you run it against cannot hurt anyone.

**Stage 11 — Sandbox replication.** Deploy the application in an isolated,
disposable runtime: its own container, its own synthetic data, no route to
production, no real credentials.

The reason this is a *stage* rather than a footnote is that the obvious shortcut
— point the dynamic tests at staging — converts every destructive probe into an
incident. Staging usually shares an identity provider, a message bus, sometimes
a database replica, and always someone's on-call rota.

Four isolation properties, and you need all four:

- **network** — no egress except to the replica itself,
- **credentials** — synthetic secrets, so a leak is worthless,
- **data** — synthetic records, so an exfiltration test exfiltrates nothing,
- **lifetime** — destroyed after the run, so state cannot leak between tests.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 11 — model the replica and its isolation"),
  ("py", '''import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

PRIVATE = [re.compile(p) for p in (r"^127\\.", r"^10\\.", r"^169\\.254\\.",
                                   r"^192\\.168\\.", r"^localhost$")]

@dataclass
class Sandbox:
    name: str
    allow_hosts: set = field(default_factory=set)
    credentials: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    ephemeral: bool = True
    destroyed: bool = False
    log: list = field(default_factory=list)

    def egress(self, url):
        host = (urlparse(url).hostname or "").lower()
        if host in self.allow_hosts:
            d = (True, "replica-internal")
        elif any(p.match(host) for p in PRIVATE):
            d = (False, "private address outside the replica — blocked")
        else:
            d = (False, "not on the replica allowlist")
        self.log.append((url, d[0], d[1])); return d

    def destroy(self):
        self.credentials.clear(); self.data.clear(); self.destroyed = True
        return "replica destroyed; state cannot leak into the next run"

REPLICA = Sandbox("appsec-replica-8812",
                  allow_hosts={"replica.local", "db.replica.local"},
                  credentials={"DB_PASSWORD": "synthetic-not-real-0000",
                               "API_TOKEN": "synthetic-not-real-1111"},
                  data={"users": [{"id": 1, "name": "test-user-a",
                                   "card": "4000000000000000"}]})

for url in ["http://replica.local/reports",
            "http://db.replica.local:5432/",
            "https://api.github.com/",
            "http://169.254.169.254/latest/meta-data/",
            "http://10.0.3.14:9200/_search"]:
    ok, why = REPLICA.egress(url)
    print(f"{'ALLOW' if ok else 'DENY ':5s} {url[:44]:46s} {why}")
'''),
  ("md", "## 3 · Where it breaks — the same probes against staging"),
  ("py", '''STAGING = Sandbox("staging",
                  allow_hosts={"staging.internal", "db.staging.internal",
                               "sso.corp", "bus.corp", "api.github.com"},
                  credentials={"DB_PASSWORD": "real-staging-password",
                               "API_TOKEN": "ghp_real_staging_token"},
                  data={"users": [{"id": 4471, "name": "dana@corp",
                                   "card": "4111111111111111"}]},
                  ephemeral=False)

DESTRUCTIVE_PROBES = [
 ("drop a table",        "db.staging.internal", "db.replica.local"),
 ("exfiltrate user rows","api.github.com",      "replica.local"),
 ("brute-force login",   "sso.corp",            "replica.local"),
]
print(f"{'probe':24s}{'on staging':>14}{'on replica':>14}")
print("-" * 56)
for probe, staging_target, replica_target in DESTRUCTIVE_PROBES:
    s_ok, _ = STAGING.egress(f"http://{staging_target}/")
    r_ok, _ = REPLICA.egress(f"http://{replica_target}/")
    print(f"{probe:24s}{'REACHES':>14}{'contained':>14}" if s_ok
          else f"{probe:24s}{'blocked':>14}{'contained':>14}")

print("\\nwhat a leaked credential is worth:")
for name, box in (("staging", STAGING), ("replica", REPLICA)):
    creds = list(box.credentials.values())
    synthetic = all("synthetic" in c for c in creds)
    print(f"   {name:10s}{'worthless — synthetic' if synthetic else 'REAL — usable against real systems'}")

print("\\nwhat an exfiltrated record is worth:")
for name, box in (("staging", STAGING), ("replica", REPLICA)):
    rec = box.data["users"][0]
    real = not rec["name"].startswith("test-")
    print(f"   {name:10s}{'REAL customer data' if real else 'synthetic'}  {rec['name']}")
'''),
  ("md", "## 4 · The control — the four isolation properties, checked"),
  ("py", '''def isolation_report(box):
    checks = {
      "network": all(not ok for url, ok, _ in box.log
                     if urlparse(url).hostname not in box.allow_hosts),
      "credentials": all("synthetic" in v for v in box.credentials.values()) if box.credentials else True,
      "data": all(u["name"].startswith("test-") for u in box.data.get("users", [])),
      "lifetime": box.ephemeral,
    }
    return checks, all(checks.values())

for box in (REPLICA, STAGING):
    checks, ok = isolation_report(box)
    print(f"{box.name}")
    for k, v in checks.items():
        print(f"   {'PASS' if v else 'FAIL':5s} {k}")
    print(f"   → suitable for dynamic testing: {ok}\\n")

_, replica_ok = isolation_report(REPLICA)
_, staging_ok = isolation_report(STAGING)
assert replica_ok and not staging_ok

print(REPLICA.destroy())
print(f"credentials after destroy: {REPLICA.credentials or 'cleared'}")
print(f"data after destroy:        {REPLICA.data or 'cleared'}")
assert REPLICA.destroyed and not REPLICA.credentials
'''),
 ],
 "expect": "The replica permits only its own internal hosts and blocks GitHub, "
           "the metadata service and private addresses. Staging holds real "
           "credentials and a real-shaped customer record while the replica holds "
           "synthetic ones. The four isolation checks pass for the replica and "
           "fail for staging on credentials, data and lifetime, and destroying "
           "the replica clears its state.",
 "challenge": "Check whether your dynamic testing currently runs against staging. "
              "If it does, list what staging shares with production — identity "
              "provider, message bus, data replica. Each shared component is a "
              "path from a test probe to a real incident.",
},

"B2.7": {
 "concept": """
**Stage 12 — Dynamic exploitation.** The stage that converts an argument into a
fact.

Everything Phase 3 produced is a hypothesis: the code *looks* vulnerable and the
sink *appears* reachable. Hypotheses get argued about in triage meetings. An
executed exploit does not — either the probe achieved the effect or it did not.

Two things this stage produces that static analysis cannot:

- **Confirmation.** A finding that survives an exploit attempt is real,
  regardless of how the model felt about it.
- **Refutation.** A finding that fails is either not exploitable in this
  configuration or not real, and both are useful answers.

The discipline that makes it trustworthy is that the probe must assert a
**concrete effect** — rows returned that should not be, a file read outside the
root — not merely that the request did not error. "No exception" is the DAST
equivalent of a shape check, and B2.0 already established what those are worth.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · The replica application, running"),
  ("py", '''import sqlite3
from dataclasses import dataclass, field

def build_app():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE reports(id INTEGER, owner TEXT, amount INT)")
    conn.executemany("INSERT INTO reports VALUES (?,?,?)",
                     [(1,"test-user-a",100),(2,"test-user-a",250),
                      (3,"test-user-b",900),(4,"test-user-c",50)])
    return conn

FILES = {"/srv/docs/readme.txt": "public readme",
         "/srv/secrets/token": "synthetic-not-real-9999"}

class App:
    """The replica under test. Two handlers, one of each bug class."""
    def __init__(self): self.conn = build_app()
    def list_reports(self, owner):
        q = "SELECT id, owner, amount FROM reports WHERE owner = '" + owner + "'"
        return self.conn.execute(q).fetchall()
    def fetch_doc(self, name):
        path = "/srv/docs/" + name
        parts = []
        for seg in path.split("/"):
            if seg in ("", "."): continue
            if seg == "..":
                if parts: parts.pop()
                continue
            parts.append(seg)
        real = "/" + "/".join(parts)
        return FILES.get(real, "not found")

app = App()
print("normal use:")
print("   list_reports('test-user-a') →", app.list_reports("test-user-a"))
print("   fetch_doc('readme.txt')     →", app.fetch_doc("readme.txt"))
'''),
  ("md", "## 3 · Stage 12 — probes that assert a concrete effect"),
  ("py", '''@dataclass
class Probe:
    pid: str; cwe: str; target: str; payload: str
    effect: str                     # what must be TRUE for this to be exploitation

PROBES = [
 Probe("P-01","CWE-89","list_reports","x' OR '1'='1",
       "returns rows belonging to owners other than the one requested"),
 Probe("P-02","CWE-22","fetch_doc","../secrets/token",
       "returns file content from outside /srv/docs"),
 Probe("P-03","CWE-89","list_reports","test-user-a",
       "control probe — must NOT be flagged as exploitation"),
]

def run_probe(app, probe):
    if probe.target == "list_reports":
        rows = app.list_reports(probe.payload)
        owners = {r[1] for r in rows}
        exploited = len(owners) > 1
        return exploited, f"{len(rows)} rows, owners={sorted(owners)}"
    content = app.fetch_doc(probe.payload)
    exploited = content not in ("not found",) and "secrets" in probe.payload
    return exploited, f"returned {content!r}"

print(f"{'probe':7s}{'cwe':9s}{'exploited':11s}observation")
print("-" * 74)
results = {}
for p in PROBES:
    ok, obs = run_probe(app, p)
    results[p.pid] = ok
    print(f"{p.pid:7s}{p.cwe:9s}{str(ok):11s}{obs}")
assert results["P-01"] and results["P-02"] and not results["P-03"]
'''),
  ("md", "## 4 · Where it breaks — the probe that asserts nothing\n\n"
         "The most common DAST bug: treating \"the request succeeded\" as "
         "confirmation. Both probes below hit the app and return 200-equivalents; "
         "only one of them proves anything."),
  ("py", '''def weak_probe(app, probe):
    """Asserts only that nothing blew up."""
    try:
        if probe.target == "list_reports": app.list_reports(probe.payload)
        else: app.fetch_doc(probe.payload)
        return True, "request completed without error"
    except Exception as e:
        return False, f"raised {type(e).__name__}"

print(f"{'probe':7s}{'weak assertion':17s}{'effect assertion':18s}agreement")
print("-" * 66)
for p in PROBES:
    w, _ = weak_probe(app, p)
    s, _ = run_probe(app, p)
    print(f"{p.pid:7s}{str(w):17s}{str(s):18s}{'' if w == s else '← DISAGREE'}")
print("\\nThe weak assertion confirms all three, including the control probe.")
print("A pipeline built on it reports 100% confirmation and means nothing by it.")
'''),
  ("py", '''# Stage 12 output: findings promoted from hypothesis to confirmed, or dropped.
HYPOTHESES = [
 {"id":"F-01","cwe":"CWE-89","unit":"list_reports","status":"HYPOTHESIS","probe":"P-01"},
 {"id":"F-02","cwe":"CWE-22","unit":"fetch_doc",  "status":"HYPOTHESIS","probe":"P-02"},
 {"id":"F-03","cwe":"CWE-89","unit":"total",      "status":"HYPOTHESIS","probe":None},
]
def stage12(hypotheses, results):
    out = []
    for h in hypotheses:
        if h["probe"] is None:
            out.append({**h, "status": "UNVALIDATED",
                        "note": "no probe generated — cannot confirm or refute"})
        elif results.get(h["probe"]):
            out.append({**h, "status": "CONFIRMED",
                        "note": "exploit achieved the asserted effect on the replica"})
        else:
            out.append({**h, "status": "REFUTED",
                        "note": "probe ran; asserted effect did not occur"})
    return out

for f in stage12(HYPOTHESES, results):
    print(f"{f['id']}  {f['cwe']:9s}{f['status']:12s}{f['note']}")
confirmed = [f for f in stage12(HYPOTHESES, results) if f["status"] == "CONFIRMED"]
print(f"\\n{len(confirmed)} confirmed by execution — these go to stages 13-15.")
print("UNVALIDATED is not a pass. It is a gap in probe generation, and it should")
print("appear in the report as one.")
'''),
 ],
 "expect": "The SQL injection probe returns rows for three owners when one was "
           "requested, and the traversal probe returns the synthetic token from "
           "outside the document root; the control probe returns a single owner "
           "and is not flagged. The weak assertion confirms all three including "
           "the control. Stage 12 marks two findings CONFIRMED and one "
           "UNVALIDATED for having no probe.",
 "challenge": "Look at your DAST assertions. If any of them checks only for a "
              "non-error response, it is confirming findings it has not tested — "
              "and the control probe above is how you prove that in five minutes.",
},

"B2.8": {
 "concept": """
**Stage 13 — Exploit chaining.** Individual findings are triaged individually,
and that is how three mediums become a critical nobody noticed.

The arithmetic of severity is not additive. A read-only information disclosure
is a medium. A CSRF is a medium. An unauthenticated internal endpoint is a
medium. Chained — leak an ID, forge a request using it, hit the internal
endpoint with the forged session — the outcome is account takeover, which is
not a medium.

The pipeline can find these mechanically because Phase 4 already produced
confirmed findings with known **preconditions** and **effects**. If one
finding's effect satisfies another's precondition, they compose, and the chain's
severity is the severity of its final effect.

This is the stage that most often changes what gets fixed first.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 13 — findings as preconditions and effects"),
  ("py", '''from dataclasses import dataclass, field
from itertools import permutations

@dataclass(frozen=True)
class Confirmed:
    fid: str; cwe: str; name: str
    requires: frozenset       # preconditions
    grants: frozenset         # effects
    severity: str

FINDINGS = [
 Confirmed("F-01","CWE-200","report id disclosed in an error message",
           frozenset({"unauthenticated"}), frozenset({"valid_report_id"}), "low"),
 Confirmed("F-02","CWE-639","report fetch does not check ownership (IDOR)",
           frozenset({"valid_report_id","authenticated"}),
           frozenset({"other_users_report_data"}), "medium"),
 Confirmed("F-03","CWE-352","password change endpoint lacks CSRF protection",
           frozenset({"authenticated"}), frozenset({"password_reset_for_victim"}), "medium"),
 Confirmed("F-04","CWE-89","SQL injection in the report filter",
           frozenset({"authenticated"}), frozenset({"database_read"}), "high"),
 Confirmed("F-05","CWE-306","internal admin endpoint has no authentication",
           frozenset({"internal_network"}), frozenset({"admin_actions"}), "medium"),
 Confirmed("F-06","CWE-918","report export fetches a user-supplied URL (SSRF)",
           frozenset({"authenticated"}), frozenset({"internal_network"}), "medium"),
]
SEV_RANK = {"low":1,"medium":2,"high":3,"critical":4}
START = frozenset({"unauthenticated","authenticated"})

print(f"{'id':7s}{'cwe':10s}{'sev':9s}{'requires':38s}grants")
print("-" * 96)
for f in FINDINGS:
    print(f"{f.fid:7s}{f.cwe:10s}{f.severity:9s}{str(sorted(f.requires)):38s}"
          f"{sorted(f.grants)}")
'''),
  ("md", "## 3 · Compose them — an effect that satisfies the next precondition"),
  ("py", '''EFFECT_SEVERITY = {
 "other_users_report_data": "high",
 "password_reset_for_victim": "critical",
 "admin_actions": "critical",
 "database_read": "high",
 "internal_network": "medium",
 "valid_report_id": "low",
}

def chains(findings, start, max_len=4):
    found = []
    def walk(path, state):
        if len(path) >= max_len: return
        for f in findings:
            if f in path: continue
            if not f.requires <= state: continue
            new_state = state | f.grants
            new_path = path + [f]
            if len(new_path) > 1:
                worst = max((EFFECT_SEVERITY.get(g, "low") for g in f.grants),
                            key=lambda s: SEV_RANK[s])
                found.append({"chain": new_path, "final_effect": sorted(f.grants),
                              "severity": worst})
            walk(new_path, new_state)
    walk([], start)
    return found

ALL = chains(FINDINGS, START)
best = {}
for c in ALL:
    key = tuple(f.fid for f in c["chain"])
    best[key] = c
ranked = sorted(best.values(), key=lambda c: (-SEV_RANK[c["severity"]], len(c["chain"])))

print(f"{len(ranked)} composable chains found\\n")
for c in ranked[:6]:
    ids = " → ".join(f.fid for f in c["chain"])
    links = ", ".join(f"{f.severity}" for f in c["chain"])
    print(f"[{c['severity']:8s}] {ids:26s} links: {links}")
    print(f"{'':11s} final effect: {c['final_effect']}")
'''),
  ("md", "## 4 · Where it breaks — triage the links, miss the chain"),
  ("py", '''individual = max(SEV_RANK[f.severity] for f in FINDINGS)
chained = max(SEV_RANK[c["severity"]] for c in ranked)
inv = {v: k for k, v in SEV_RANK.items()}
print(f"highest individual finding severity : {inv[individual]}")
print(f"highest chained severity            : {inv[chained]}")

critical_chains = [c for c in ranked if c["severity"] == "critical"]
print(f"\\ncritical chains built entirely from non-critical findings:")
for c in critical_chains[:3]:
    ids = " → ".join(f"{f.fid}({f.severity})" for f in c["chain"])
    print(f"   {ids}")
    print(f"      → {c['final_effect']}")

all_links_medium_or_below = [c for c in critical_chains
                             if all(SEV_RANK[f.severity] <= 2 for f in c["chain"])]
print(f"\\n{len(all_links_medium_or_below)} critical chain(s) whose every link is "
      f"medium or lower.")
print("Triaged individually, none of those findings would be worked this sprint.")
assert all_links_medium_or_below
'''),
  ("py", '''# The control: rank by chain severity, and report the chain, not the link.
def remediation_order(findings, chains_):
    """Fixing one link breaks every chain through it. Rank by chains broken."""
    impact = {}
    for f in findings:
        broken = [c for c in chains_ if f in c["chain"]]
        worst = max((SEV_RANK[c["severity"]] for c in broken), default=0)
        impact[f.fid] = {"chains_broken": len(broken), "worst_chain": inv.get(worst, "—"),
                         "own_severity": f.severity}
    return sorted(impact.items(),
                  key=lambda kv: (-SEV_RANK.get(kv[1]["worst_chain"], 0),
                                  -kv[1]["chains_broken"]))

print(f"{'finding':9s}{'own sev':10s}{'chains broken':>15}{'worst chain':>14}")
print("-" * 50)
for fid, i in remediation_order(FINDINGS, ranked):
    print(f"{fid:9s}{i['own_severity']:10s}{i['chains_broken']:>15}{i['worst_chain']:>14}")
top = remediation_order(FINDINGS, ranked)[0]
print(f"\\nfix first: {top[0]} — own severity {top[1]['own_severity']}, but it "
      f"breaks {top[1]['chains_broken']} chains including a {top[1]['worst_chain']}")
'''),

  ("md", "## 6 · Phase 4 as a skill — and the preconditions that gate it\n\n"
         "Dynamic validation is the one phase that *acts*. Everything before it "
         "reads; this one sends input to a running system. The skill therefore "
         "opens with safety preconditions rather than a procedure, and a "
         "refusal is a first-class output.\n\n"
         "The contract also insists that `reproduced: false` be reported rather "
         "than dropped. A finding that survived Phase 3 and then failed to "
         "reproduce is the most useful signal the pipeline produces about its "
         "own false-positive rate — and it is the one a tidy report deletes."),
  ("py", SKILL_RUNTIME),
  ("skill", "appsec/appsec-exploit-validate"),

  ("py", '''contract = contract_of(body)

def validation_of(f):
    """One confirmed finding, expressed as the skill's validation record."""
    return {
      "finding_id": f.fid, "reproduced": True,
      "sandbox": {"commit": "a1fcf68", "fixture": f"minimal app exposing {f.fid}",
                  "isolated": True},
      "input": f"crafted request exercising {f.cwe}",
      # the observable is the claim; an exit code is not
      "observable": f.name,
      "chain": [{"primitive": f.name, "leads_to": g,
                 "stopped_because": "next step needs a real credential"}
                for g in sorted(f.grants)],
      "remediation": {"layer": "query" if f.cwe == "CWE-89" else "api",
                      "change": f"eliminate the class behind {f.cwe}",
                      "cost": "low", "retested": True, "still_reproduces": False},
    }

phase4 = {
 "validations": [validation_of(f) for f in FINDINGS],
 # the safety gate, exercised rather than described
 "refused": [{"finding_id": "F-99", "precondition_failed": 1,
              "why": "target is a production host, not a sandbox"}],
}
problems = check(phase4, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\\nvalidated {len(phase4['validations'])} findings, "
      f"refused {len(phase4['refused'])}")
for v in phase4["validations"][:3]:
    print(f"   {v['finding_id']}  chains to: "
          f"{', '.join(c['leads_to'] for c in v['chain']) or '—'}")
print()
print("Refusing is an output, not an error. A validation harness that quietly")
print("skips the production target reports the same thing as one that never")
print("saw it, and those are very different states to be in.")
assert phase4["refused"], "the safety gate must be visible in the output"
'''),

  ("md", "## 7 · Where it breaks — the tidy report\n\n"
         "Now suppose two of these findings do not reproduce, and the pipeline "
         "does the natural thing with them."),
  ("py", '''mixed = [dict(validation_of(f), reproduced=(i % 3 != 0))
         for i, f in enumerate(FINDINGS)]
failed = [v for v in mixed if not v["reproduced"]]

tidy = {"validations": [v for v in mixed if v["reproduced"]], "refused": []}
honest = {"validations": mixed, "refused": phase4["refused"]}

print(f"conformance, tidy report  : {len(check(tidy, contract))}")
print(f"conformance, honest report: {len(check(honest, contract))}")
print(f"\\nvalidations attempted : {len(mixed)}")
print(f"reproduced            : {len(mixed) - len(failed)}")
print(f"failed to reproduce   : {len(failed)}  ({', '.join(v['finding_id'] for v in failed)})")
fpr = len(failed) / len(mixed)
print(f"measured false-positive rate of Phase 3: {fpr:.0%}")
print()
print("Both conform. The tidy one drops the non-reproductions, and with them")
print("the only number that says how good the earlier phases actually are.")
print("Its reader sees a pipeline that is right every time.")
assert not check(tidy, contract), "dropping the failures is schema-valid - that is the point"
assert failed, "the demo needs at least one non-reproduction"
'''),
 ],
 "expect": "Six confirmed findings compose into multiple chains. The highest "
           "individual severity is high while the highest chained severity is "
           "critical, and at least one critical chain is built entirely from "
           "medium-or-lower links — for example SSRF granting internal network "
           "access, then the unauthenticated admin endpoint. Remediation ordering "
           "puts a medium finding first because it breaks the most chains.",
 "challenge": "Take your current open findings and write down each one's "
              "preconditions and effects. The chaining falls out mechanically, "
              "and the finding you should fix first is usually not the one at the "
              "top of the severity-sorted queue.",
},

"B2.9": {
 "concept": """
**Stage 14 — Remediation engineering.** Generate the fix, then prove it.

A model that finds bugs is useful. A model that fixes them is only useful if you
can tell a real fix from a plausible one, and plausible is exactly what language
models are optimised to produce.

There are three ways to make a finding stop firing:

1. **Fix the vulnerability** — behaviour preserved, bug gone.
2. **Remove the code** — finding gone, so is the feature.
3. **Evade the detector** — rewrite until the pattern misses.

All three make the scanner green, and an autonomous loop optimising for a green
scan will find options 2 and 3 on its own because they are cheaper.

The pipeline has an advantage a static workflow does not: Phase 4 already built
a working exploit. So the acceptance test is not "does the scanner still fire?"
It is **"does the exploit still work against the patched build?"** — which is
the only question that cannot be gamed by editing the code around the detector.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("model", {
   "title": 'The model backend, and the patch it proposes',
   "task": 'Fix this without changing the function\'s behaviour for valid input. Return only the patched function.\n\ndef report(request):\n    q = "SELECT * FROM orders WHERE ref = \'" + request.args[\'ref\'] + "\'"\n    return db.execute(q)',
   "replay": 'def report(request):\n    q = "SELECT * FROM orders WHERE ref = ?"\n    return db.execute(q, (request.args[\'ref\'],))',
   "system": 'You are a remediation engineer. Output code only, no explanation.',
   "check": '("parameterises the query", "?" in answer or "%s" in answer or ":ref" in answer)'}),
  ("md", "## 2 · The confirmed finding, with its working exploit"),
  ("py", '''import re, sqlite3

VULNERABLE = \'\'\'
def get_user(conn, name):
    return conn.execute("SELECT id, name FROM users WHERE name = '" + name + "'").fetchall()
\'\'\'

def build_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users(id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?,?)",
                     [(1,"dana"),(2,"sam"),(3,"o'brien")])
    return conn

def load(src):
    ns = {}; exec(compile(src, "<patch>", "exec"), ns); return ns["get_user"]

BEHAVIOUR = [("dana",[(1,"dana")]), ("sam",[(2,"sam")]),
             ("nobody",[]), ("o'brien",[(3,"o'brien")])]

def behaviour_ok(fn):
    conn = build_db(); rows = []
    for name, expected in BEHAVIOUR:
        try: got = fn(conn, name)
        except Exception as e: rows.append((name, f"raised {type(e).__name__}", False)); continue
        rows.append((name, got, got == expected))
    return rows

def exploit_works(fn):
    """The stage-12 probe, reused as the acceptance test."""
    conn = build_db()
    try: rows = fn(conn, "x' OR '1'='1")
    except Exception: return False, "probe raised — not exploitable this way"
    return len(rows) > 1, f"probe returned {len(rows)} rows"

def scanner_fires(src):
    return bool(re.search(r"execute\\(\\s*[\\"\\'][^\\"\\']*[\\"\\']\\s*\\+", src))

fn = load(VULNERABLE)
print("behaviour of the vulnerable build:")
for name, got, ok in behaviour_ok(fn):
    print(f"   get_user({name!r:10s}) → {str(got):18s} {'ok' if ok else 'FAILS'}")
ex, why = exploit_works(fn)
print(f"\\nexploit works: {ex} — {why}")
print(f"scanner fires: {scanner_fires(VULNERABLE)}")
'''),
  ("md", "## 3 · Four candidate patches, three of which make CI green"),
  ("py", '''CANDIDATES = {
 "A · parameterise (the real fix)": \'\'\'
def get_user(conn, name):
    return conn.execute("SELECT id, name FROM users WHERE name = ?", (name,)).fetchall()
\'\'\',
 "B · delete the feature": \'\'\'
def get_user(conn, name):
    return []
\'\'\',
 "C · evade the scanner": \'\'\'
def get_user(conn, name):
    q = "SELECT id, name FROM users WHERE name = '%s'" % name
    return conn.execute(q).fetchall()
\'\'\',
 "D · escape by hand": \'\'\'
def get_user(conn, name):
    safe = name.replace("'", "''")
    return conn.execute("SELECT id, name FROM users WHERE name = '" + safe + "'").fetchall()
\'\'\',
}
print(f"{'candidate':34s}{'scanner green':>15}")
print("-" * 50)
for name, src in CANDIDATES.items():
    print(f"{name:34s}{str(not scanner_fires(src)):>15}")
print("\\nThree of four are green. Only one of those is a fix.")
'''),
  ("md", "## 4 · The control — validate on three axes, exploit first"),
  ("py", '''def validate(src):
    fn = load(src)
    green = not scanner_fires(src)
    beh = behaviour_ok(fn)
    preserved = all(ok for _, _, ok in beh)
    still_exploitable, _ = exploit_works(fn)
    reasons = []
    if not green:            reasons.append("scanner still fires")
    if not preserved:        reasons.append("behaviour changed")
    if still_exploitable:    reasons.append("STILL EXPLOITABLE (stage-12 probe passes)")
    return (not reasons), green, preserved, still_exploitable, reasons

print(f"{'candidate':34s}{'scan':6s}{'behaviour':11s}{'exploitable':13s}verdict")
print("-" * 84)
accepted = []
for name, src in CANDIDATES.items():
    ok, g, b, x, reasons = validate(src)
    if ok: accepted.append(name)
    print(f"{name:34s}{str(g):6s}{str(b):11s}{str(x):13s}"
          f"{'ACCEPT' if ok else 'REJECT — ' + ', '.join(reasons)}")
print(f"\\naccepted: {accepted}")
assert "A · parameterise (the real fix)" in accepted
assert "B · delete the feature" not in accepted
assert "C · evade the scanner" not in accepted
'''),
  ("py", '''# The proof-of-fix clause: the exploit must fail on the new build and
# succeed on the old one. Without both halves, "fixed" is a claim.
def proof_of_fix(old_src, new_src):
    old_ex, _ = exploit_works(load(old_src))
    new_ex, _ = exploit_works(load(new_src))
    return (old_ex and not new_ex), f"exploit on old={old_ex}, on new={new_ex}"

for name in accepted:
    ok, detail = proof_of_fix(VULNERABLE, CANDIDATES[name])
    print(f"{name:34s} proof of fix: {ok}  ({detail})")

print("\\nCandidate D passes every automated check and is still the wrong answer:")
print("it reimplements the driver's escaping and will be wrong for the next")
print("input class or the next database. Nothing except a rule about MECHANISM")
print("catches that — which is the part of remediation that does not automate.")
'''),
 ],
 "expect": "The vulnerable build passes all four behaviour cases and the exploit "
           "returns 3 rows. Candidates A, B and D make the scanner green. "
           "Validation rejects B for changed behaviour and C for remaining "
           "exploitable, accepting A and D. Proof of fix holds for both accepted "
           "patches — the exploit works on the old build and fails on the new.",
 "challenge": "Candidate D passes every automated gate and is still wrong. Write "
              "the rule that rejects it. You will find it has to be about which "
              "*mechanism* is acceptable, not about outcomes — and that rule "
              "belongs in your secure coding standard, not in the pipeline.",
},

"B2.10": {
 "concept": """
**Stage 15 — Severity calibration and reporting.** The pipeline's output, and
the stage where its credibility is won or lost.

Most severity is a label copied from the rule that fired: this is a CWE-89, so
it is high. That number predicts nothing, because it ignores everything the
pipeline has just learned:

- did stage 12 **confirm it by execution**?
- is it **reachable** from an untrusted entry point (stage 10)?
- what does it **chain into** (stage 13)?
- does it sit in a **historical risk zone** (stage 1)?

Calibrated severity uses all four. A confirmed, reachable finding that chains
into account takeover is not the same as an unvalidated finding in dead code,
even when both are CWE-89.

The second half of this stage is the report, and the useful report is not a
finding count. It is **per-stage economics**: where bugs are caught, where they
escape, and what each escape costs — because that is what decides next
quarter's budget.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 15 — calibrate severity from what the pipeline learned"),
  ("py", '''from dataclasses import dataclass

@dataclass
class Finding:
    fid: str; cwe: str; rule_severity: str
    confirmed: bool; reachable: str        # reachable | unknown | unreachable
    chains_into: str                       # "" if none
    historical_risk: float

RULE_SEV = {"low":1,"medium":2,"high":3,"critical":4}
INV = {v:k for k,v in RULE_SEV.items()}
CHAIN_SEV = {"": 0, "data_exposure": 3, "account_takeover": 4, "admin_actions": 4}

FINDINGS = [
 Finding("F-01","CWE-89","high",  True,  "reachable",   "account_takeover", 0.82),
 Finding("F-02","CWE-89","high",  False, "unreachable", "", 0.10),
 Finding("F-03","CWE-22","medium",True,  "reachable",   "data_exposure", 0.91),
 Finding("F-04","CWE-798","high", False, "unknown",     "", 0.05),
 Finding("F-05","CWE-352","medium",True, "reachable",   "account_takeover", 0.30),
 Finding("F-06","CWE-89","high",  False, "unknown",     "", 0.40),
]

def calibrate(f):
    base = RULE_SEV[f.rule_severity]
    score = base
    why = [f"rule severity {f.rule_severity} ({base})"]
    if f.confirmed:            score += 2; why.append("confirmed by execution (+2)")
    else:                      score -= 1; why.append("not confirmed (-1)")
    if f.reachable == "reachable":     score += 1; why.append("reachable from an entry point (+1)")
    elif f.reachable == "unreachable": score -= 2; why.append("unreachable (-2)")
    else:                              why.append("reachability unknown (0)")
    if f.chains_into:
        score = max(score, CHAIN_SEV[f.chains_into] + 2)
        why.append(f"chains into {f.chains_into} (floor raised)")
    if f.historical_risk > 0.6: score += 1; why.append("in a historical risk zone (+1)")
    band = ("critical" if score >= 6 else "high" if score >= 4
            else "medium" if score >= 2 else "low")
    return {"fid": f.fid, "rule": f.rule_severity, "calibrated": band,
            "score": score, "why": why}

rows = [calibrate(f) for f in FINDINGS]
print(f"{'id':7s}{'rule sev':10s}{'calibrated':12s}{'score':>6}")
print("-" * 40)
for r in rows:
    moved = "" if r["rule"] == r["calibrated"] else "   ← moved"
    print(f"{r['fid']:7s}{r['rule']:10s}{r['calibrated']:12s}{r['score']:>6}{moved}")
'''),
  ("md", "## 3 · Where it breaks — rule severity as the queue order"),
  ("py", '''by_rule = sorted(FINDINGS, key=lambda f: -RULE_SEV[f.rule_severity])
by_cal  = sorted(rows, key=lambda r: -r["score"])

print(f"{'rank':6s}{'by rule severity':22s}{'by calibrated severity':24s}")
print("-" * 56)
for i, (a, b) in enumerate(zip(by_rule, by_cal), 1):
    print(f"{i:<6}{a.fid + ' (' + a.rule_severity + ')':22s}"
          f"{b['fid'] + ' (' + b['calibrated'] + ')':24s}")

top_rule = {f.fid for f in by_rule[:3]}
top_cal  = {r["fid"] for r in by_cal[:3]}
print(f"\\ntop-3 by rule       : {sorted(top_rule)}")
print(f"top-3 by calibration: {sorted(top_cal)}")
print(f"disagreement        : {sorted(top_rule ^ top_cal)}")
for r in rows:
    f = next(x for x in FINDINGS if x.fid == r["fid"])
    if r["fid"] in top_rule - top_cal:
        print(f"\\n{r['fid']} is high by rule and {r['calibrated']} calibrated because:")
        for w in r["why"]: print(f"   · {w}")
assert top_rule != top_cal
'''),
  ("md", "## 4 · The report — per-stage economics, not a finding count"),
  ("py", '''from dataclasses import dataclass as dc

@dc
class Stage:
    name: str; found: int; escaped: int; false_positives: int; minutes: float

PIPELINE_STAGES = [
 Stage("design",   2,  9,  1,  40),
 Stage("code",    14,  6,  9,  70),
 Stage("review",   9,  4, 22, 110),
 Stage("test",     4,  2,  3,  50),
 Stage("deploy",   1,  1,  1,  20),
 Stage("runtime",  1,  0,  0, 180),
]
ESCAPE_MULTIPLIER = 6.0

print(f"{'stage':9s}{'found':>6}{'escaped':>9}{'FP':>5}{'precision':>11}{'min/find':>10}")
print("-" * 51)
for s in PIPELINE_STAGES:
    total = s.found + s.false_positives
    prec = s.found/total if total else 0
    per = s.minutes/s.found if s.found else 0
    print(f"{s.name:9s}{s.found:>6}{s.escaped:>9}{s.false_positives:>5}{prec:>11.2f}{per:>10.1f}")

def escape_cost(stages, m=ESCAPE_MULTIPLIER):
    n = len(stages)
    return {s.name: round(s.escaped * (m ** (n-i-1)) / 1000, 2)
            for i, s in enumerate(stages)}

costs = escape_cost(PIPELINE_STAGES)
print(f"\\n{'stage':9s}{'escaped':>9}{'relative escape cost':>22}")
print("-" * 42)
for s in PIPELINE_STAGES:
    bar = "█" * min(int(costs[s.name] * 2), 34)
    print(f"{s.name:9s}{s.escaped:>9}{costs[s.name]:>14}  {bar}")
'''),
  ("py", '''# The one-page report the pipeline actually emits.
def report(findings, calibrated, stages, costs):
    crit = [r for r in calibrated if r["calibrated"] == "critical"]
    confirmed = [f for f in findings if f.confirmed]
    unvalidated = [f for f in findings if not f.confirmed and f.reachable == "unknown"]
    worst_stage = max(costs, key=costs.get)
    return f"""APPSEC PIPELINE REPORT

  findings emitted            {len(findings)}
  confirmed by execution      {len(confirmed)}   (stage 12)
  unvalidated + unknown reach {len(unvalidated)}   ← a gap in probe generation, not a pass
  calibrated critical         {len(crit)}   {[r['fid'] for r in crit]}

  severity is calibrated from: confirmation, reachability, chaining and
  historical risk — not from the rule that fired.

  highest escape cost at stage: {worst_stage} ({costs[worst_stage]})
  → that is where the next analyser should be pointed, not where the
    most findings currently are."""

print(report(FINDINGS, rows, PIPELINE_STAGES, costs))
assert max(costs, key=costs.get) == "design"
'''),

  ("md", "## 6 · Stage 15 as a skill — severity you can argue with\n\n"
         "The reporting skill carries one rule that decides most of the "
         "credibility of a security report: **a finding that did not reproduce "
         "may not be Critical.** Cap it at Medium and say so in the same "
         "sentence, so the reader never has to cross-reference an appendix to "
         "learn that the headline finding is theoretical.\n\n"
         "The contract enforces the habit by requiring `severity_inputs` next "
         "to every severity. One overclaimed Critical costs more trust than ten "
         "honest Lows."),
  ("py", SKILL_RUNTIME),
  ("skill", "appsec/appsec-triage-report"),

  ("py", '''contract = contract_of(body)
RANK = ["informational", "low", "medium", "high", "critical"]

def calibrated(f):
    """Severity from evidence, capped when nothing was reproduced."""
    base = f.rule_severity
    if not f.confirmed and RANK.index(base) > RANK.index("medium"):
        return "medium", f"capped from {base}: not reproduced"
    return base, "as assessed"

demonstrated, asserted = [], []
for f in FINDINGS:
    sev, why = calibrated(f)
    if f.confirmed:
        demonstrated.append({
          "finding_id": f.fid, "severity": sev,
          "severity_inputs": {"reproduced": f.confirmed,
                              "auth": "user", "sink": f.cwe},
          "title": f"{f.cwe} in {f.fid}", "impact": f.chains_into or "no demonstrated impact",
          "observable": f"{f.reachable} path exercised in the sandbox",
          "fix": f"remove the {f.cwe} class at the query layer",
          "fix_cost": "low"})
    else:
        asserted.append({"finding_id": f.fid, "severity": sev,
                         "why_not_demonstrated": f"{f.reachable}; {why}"})

summary = {k: 0 for k in RANK}
for d in demonstrated: summary[d["severity"]] += 1
for a_ in asserted:    summary[a_["severity"]] += 1

rep = {"report": {
  "summary": summary,
  "demonstrated": demonstrated,
  "asserted": asserted,
  "scope": {"analysed": [f.fid for f in FINDINGS],
            "deferred": ["dependencies not in scope"],
            "blind_spots": ["dynamic dispatch not resolved statically"]},
  "quality": {"validated": len(demonstrated),
              "failed_to_reproduce": len(asserted),
              "false_positive_rate": round(len(asserted) / len(FINDINGS), 2)},
}}
problems = check(rep, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\\ndemonstrated {len(demonstrated)} · asserted {len(asserted)}")
for a_ in asserted:
    print(f"   {a_['finding_id']}  {a_['severity']:8s} {a_['why_not_demonstrated']}")
print(f"\\nmeasured false-positive rate: {rep['report']['quality']['false_positive_rate']:.0%}")
'''),

  ("md", "## 7 · Where it breaks — the uncalibrated headline\n\n"
         "Now report the same findings without the cap."),
  ("py", '''raw_summary = {k: 0 for k in RANK}
for f in FINDINGS: raw_summary[f.rule_severity] += 1

print(f"{'severity':14s}{'uncalibrated':>14s}{'calibrated':>12s}")
for k in reversed(RANK):
    print(f"{k:14s}{raw_summary[k]:>14d}{summary[k]:>12d}")

inflated = [f.fid for f in FINDINGS
            if not f.confirmed and RANK.index(f.rule_severity) > RANK.index("medium")]
print(f"\\nfindings reported above Medium on no evidence: {inflated}")
print()
print("Both versions are schema-valid; only one of them is defensible. The")
print("uncalibrated table leads with Highs that were never reproduced, and the")
print("reader cannot tell which. The first time one of them turns out to be a")
print("false positive, every other number in the report is discounted too.")
assert inflated, "the demo needs at least one finding the cap catches"
assert summary["high"] < raw_summary["high"]
'''),
 ],
 "expect": "Calibration moves several findings off their rule severity: the "
           "confirmed reachable CWE-89 that chains into account takeover becomes "
           "critical, while the unreachable and unvalidated ones fall. The top-3 "
           "by rule severity and by calibration disagree. The stage table shows "
           "review with the worst precision and highest minutes per finding, and "
           "design carrying the highest escape cost despite only two findings.",
 "challenge": "Recalculate severity for your current open findings using "
              "confirmation and reachability alone — you do not need chaining to "
              "see the effect. The queue reorders, and the items that fall are "
              "usually the ones people have been arguing about.",
},

"B2.11": {
 "concept": """
Cross-cutting, and it applies to every stage that calls a model: stages 3, 4, 5,
7 and 14.

The instinct when a model misses something is to give it more context. Usually
the opposite is correct.

To find a vulnerability, a model needs three things: the **sink**, the
**source**, and the **path** between them. Everything else competes for
attention and for window. A repository dumped into a prompt does not produce a
thorough review — it produces a review of whatever survived truncation, and you
cannot tell which parts those were.

So context engineering is mostly subtraction, with one exception you must not
subtract: the **enclosing signature**, because that is where reachability is
decided. The identical concatenation is critical inside an HTTP handler and
irrelevant inside a migration script that takes a constant.
""",
 "steps": [
  ("md", "## 2 · Demo — four strategies over one bug"),
  ("py", '''SOURCE = \'\'\'"""Reporting service."""
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
\'\'\'
lines = SOURCE.splitlines()
BUG_LINE = next(i for i, l in enumerate(lines, 1) if "SELECT * FROM reports" in l)
print(f"the bug is on line {BUG_LINE}")

def whole_file(_):     return SOURCE
def window(n, radius): return "\\n".join(lines[max(n-radius-1,0):n+radius])

STRATEGIES = {"whole file": whole_file(BUG_LINE),
              "±2 line window": window(BUG_LINE, 2),
              "±6 line window": window(BUG_LINE, 6)}
for name, ctx in STRATEGIES.items():
    print(f"{name:20s}{len(ctx):>6} chars{len(ctx.splitlines()):>5} lines")
'''),
  ("py", '''def decidable(ctx):
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
print("\\nThe ±2 window has the sink and the concatenation but not the signature,")
print("so you cannot tell whether owner is user-controlled — which is the")
print("difference between critical and won't-fix.")
'''),
  ("md", "## 3 · The control — slice on the source-sink path"),
  ("py", '''def path_slice(source, bug_line):
    ls = source.splitlines()
    start = max(i for i in range(bug_line) if ls[i-1].startswith("def "))
    end = next((i for i in range(start, len(ls)) if i > start and ls[i].startswith("def ")),
               len(ls))
    return "\\n".join(ls[start-1:end])

sliced = path_slice(SOURCE, BUG_LINE)
print(sliced)
d = decidable(sliced)
print(f"\\n{len(sliced)} chars ({len(sliced)/len(SOURCE):.0%} of the file), "
      f"decidable={d['sink'] and d['concatenation'] and d['source (signature)']}")
'''),
  ("py", '''def evaluate(name, ctx):
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
print(f"\\nsmallest decidable context: {best['strategy']} "
      f"({best['share']:.0%} of the file, {best['noise_fns']} unrelated functions)")
print(f"vs whole file: {1 - best['chars']/whole['chars']:.0%} smaller, "
      f"{whole['noise_fns']}→{best['noise_fns']} unrelated functions")
assert best["strategy"] == "path slice"
'''),
 ],
 "expect": "The whole file is roughly 840 characters, the ±2 window about 200 and "
           "the path slice about 390. The ±2 window is not decidable because it "
           "lacks the signature; the ±6 window and the whole file are decidable "
           "but carry unrelated functions. The path slice is the smallest "
           "decidable context with zero unrelated functions, about 53% smaller "
           "than the whole file.",
 "challenge": "Apply the path-slice rule where the source is three functions away "
              "from the sink. That is the case where text windows break down "
              "entirely and the call graph from B2.1 earns its keep.",
},

"B2.12": {
 "concept": """
The coding agent in a developer's IDE is the most privileged agent in most
organisations and the least governed. It sits upstream of everything this track
has built: it writes the code the pipeline later analyses.

What it holds by default:

- the developer's **git credentials** — push access to everything they can push to,
- the **whole monorepo** on disk, including files they never open,
- a **shell**, usually unrestricted,
- their **cloud credentials** in `~/.aws` or `~/.config/gcloud`,
- whatever **MCP servers** they connected, each with its own authority.

That is a production identity in an unmanaged environment, driven by a model
reading code from the internet.

The binding constraint here is not technical feasibility — it is **developer
tolerance**. A containment scheme that adds friction to the inner loop is
disabled within a week, and a disabled control protects nothing. So the design
goal is the strongest containment a developer does not notice.
""",
 "steps": [
  ("md", "## 2 · Demo — measure the default configuration"),
  ("py", '''SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}
DEV_TOOLS = [
 # (name, writes, scope, reversible, needed in the inner loop)
 ("read_file",  False,"self",   True,  True),
 ("write_file", True, "project",True,  True),
 ("run_tests",  True, "self",   True,  True),
 ("run_shell",  True, "tenant", False, True),
 ("git_commit", True, "project",True,  True),
 ("git_push",   True, "project",False, False),
 ("read_env",   False,"org",    True,  False),
 ("http_get",   False,"self",   True,  True),
]
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2)
               for n,w,s,rev,_ in tools if w and n not in gated)

print(f"{'tool':14s}{'writes':8s}{'scope':9s}{'reversible':12s}inner loop?")
print("-" * 58)
for n,w,s,rev,need in DEV_TOOLS:
    print(f"{n:14s}{str(w):8s}{s:9s}{str(rev):12s}{need}")
print(f"\\ndefault blast radius: {blast(DEV_TOOLS)}")
'''),
  ("py", '''import fnmatch
HOME = [
 "/home/dana/work/monorepo/src/app.py",
 "/home/dana/work/monorepo/.env",
 "/home/dana/work/other-team-repo/secrets.yaml",
 "/home/dana/.aws/credentials",
 "/home/dana/.ssh/id_ed25519",
 "/home/dana/.config/gcloud/application_default_credentials.json",
 "/home/dana/Downloads/customer-export-2026.csv",
]
def normalise(p):
    parts = []
    for seg in p.split("/"):
        if seg in ("", "."): continue
        if seg == "..":
            if parts: parts.pop()
            continue
        parts.append(seg)
    return "/" + "/".join(parts)

DENY = ("*/.ssh/*","*/.aws/*","*/.config/gcloud/*","*.pem","*/.env","*/Downloads/*")
def contained(p, workspace="/home/dana/work/monorepo"):
    real = normalise(p)
    if any(fnmatch.fnmatch(real, g) for g in DENY): return False
    return real.startswith(workspace + "/")

print(f"{'path':64s}{'default':9s}contained")
print("-" * 84)
for p in HOME:
    print(f"{p:64s}{'True':9s}{contained(p)}")
creds = [p for p in HOME if any(k in p for k in (".aws",".ssh","gcloud",".env"))]
print(f"\\ncredential files reachable by default: {len(creds)}")
print(f"credential files reachable when contained: "
      f"{sum(1 for p in creds if contained(p))}")
'''),
  ("md", "## 3 · The control — rank by friction, ship the invisible ones first"),
  ("html", D.table(
    ["control", "friction", "what developers actually experience"],
    [["deny-list credential paths", "0.0",
      "the agent cannot read ~/.aws, ~/.ssh, ~/.env. Developers never noticed."],
     ["workspace confinement", "0.1",
      "the agent sees the open repo only. Occasionally annoying for monorepo hops."],
     ["egress allowlist", "0.2",
      "package registries and your VCS. Breaks the odd curl in a generated script."],
     ["gate <code>git_push</code>", "0.4",
      "one confirmation before code leaves the machine. Noticed, usually accepted."],
     ["gate every write", "0.9",
      "<b>confirmation per file write. Abandoned within a week, every time.</b>"],
     ["no shell at all", "1.0",
      "<b>removes the inner loop. Nobody will use the agent.</b>"]],
    emphasise=1,
    caption="The first four ship today and cost nothing anyone will complain "
            "about. The last two are the ones people propose in meetings, and "
            "they are uninstalled by Friday — a control that gets turned off is "
            "worth less than a weaker one that stays on.")),
  ("py", '''gated = {"git_push"}
print(f"blast radius     {blast(DEV_TOOLS):>3} → {blast(DEV_TOOLS, gated):>3}")
print(f"reachable files  {len(HOME):>3} → {sum(1 for p in HOME if contained(p)):>3}")
print(f"credentials      {len(creds):>3} → {sum(1 for p in creds if contained(p)):>3}")
print(f"friction added   0.4 of 1.0 — one confirmation before a push")
assert not any(contained(p) for p in creds)
print("\\nNo cloud or SSH credential is reachable, the inner loop is unchanged,")
print("and the only thing a developer notices is a prompt before pushing.")
'''),

  ("md", "## 6 · The audit, as a skill an agent runs on itself\n\n"
         "Everything in this lesson is a review someone has to remember to do. "
         "Written as a skill, it is a review that fires whenever an agent opens "
         "a repository — including this one.\n\n"
         "The skill's central instruction is easy to miss and decides the "
         "outcome: **rate an injection finding by what the allowlist permits, "
         "not by the text of the injection.** The payload is the attacker's "
         "choice and costs nothing to change; the allowlist is yours."),
  ("py", SKILL_RUNTIME),
  ("skill", "appsec/coding-agent-hardening"),

  ("py", '''contract = contract_of(body)

# What actually reaches a coding agent's context in a normal repository.
SURFACE = [
 ("AGENTS.md",             "operator", True),
 (".claude/settings.json", "operator", True),
 ("README.md",             "content",  True),
 ("docs/CONTRIBUTING.md",  "content",  True),
 ("package.json",          "content",  True),   # a hook may execute its scripts
 ("vendor/lib/README.md",  "content",  False),
]

worst = max(DEV_TOOLS, key=lambda t: SCOPE_WEIGHT[t[2]] * (1 if t[3] else 2))
audit = {
 "surface": [{"path": p, "control": c, "auto_loaded": a} for p, c, a in SURFACE],
 "findings": [
   {"kind": "prompt_injection", "path": "README.md", "grade": "directive",
    # severity is whatever the most powerful pre-approved tool can do
    "worst_case": f"content-controlled text triggers {worst[0]} at {worst[2]} scope",
    "severity": "critical" if not worst[3] else "high",
    "fix": "quote repository content as data; never as instruction"},
   {"kind": "unsafe_hook", "path": "package.json", "grade": "directive",
    "worst_case": "a hook runs a repo-supplied script the moment the repo opens",
    "severity": "critical",
    "fix": "pin the hook command; never take it from repository content"},
   {"kind": "overbroad_tool", "path": ".claude/settings.json", "grade": "advisory",
    "worst_case": f"{worst[0]} pre-approved with unrestricted arguments",
    "severity": "high", "fix": "split into narrow tools, or require approval"},
 ],
 "allowlist_review": [
   {"tool": name, "worst_single_call": f"{scope} scope, "
                                       f"{'reversible' if rev else 'IRREVERSIBLE'}",
    "bounded": scope in ("self", "project") and rev}
   for name, writes, scope, rev, _ in DEV_TOOLS if writes],
}
problems = check(audit, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\\nauto-loaded, content-controlled inputs: "
      f"{[s['path'] for s in audit['surface'] if s['control']=='content' and s['auto_loaded']]}")
print(f"most powerful pre-approved tool      : {worst[0]} ({worst[2]} scope)")
print("\\nallowlist:")
for r in audit["allowlist_review"]:
    print(f"   {r['tool']:12s}{r['worst_single_call']:34s}bounded={r['bounded']}")
unbounded = [r["tool"] for r in audit["allowlist_review"] if not r["bounded"]]
print(f"\\nunbounded pre-approved tools: {unbounded}")
print()
print("The injection finding is Critical not because the README says anything")
print("clever, but because a directive path exists to a tool that cannot be")
print("undone. Rewrite the payload and the severity does not move.")
assert unbounded, "an unbounded pre-approved tool should be visible here"
'''),
 ],
 "expect": "The default developer agent scores a blast radius of 43 and can reach "
           "all seven paths including AWS, SSH and gcloud credentials. Containment "
           "reduces reachable paths to one source file with zero credentials "
           "reachable, and gating `git_push` drops the blast radius to 37 for 0.4 "
           "friction. The three lowest-friction controls remove every credential "
           "path without touching the inner loop.",
 "challenge": "Ship the credential deny-list first — it is a config file, it takes "
              "an afternoon, and no developer will notice. Then find out how many "
              "agents in your organisation could read `~/.aws/credentials` "
              "yesterday.",
},

"B2.13": {
 "concept": """
Every control claim in this pipeline has the same weakness: it is a sentence in
a document, and nothing binds it to a running system. "We enforce least
privilege" is true of some deployment, at some time, and there is no way to
re-check it when the image, the role or the tool surface changes.

An **attestation** fixes the binding. It is a signed statement about a specific
deployment, carrying per-control verdicts and the evidence behind each one, that
can be re-issued whenever anything it describes changes.

Two design decisions carry the whole idea.

**A `deployment_id` is the join key.** It resolves to a manifest of
content-addressed artefacts — repo at a commit, image by digest, IAM role,
workload identity, gateway route, guardrail ID, downstream services. Without it
an IAM finding, an identity entry and a gateway policy are three unrelated facts
about three things that may not be the same system.

**Eleven skills, not one.** One resolver, nine collectors split along
evidence-source boundaries (code, IAM, network, sandbox, identity, gateway,
ingestion, risk register, entitlements), and one signer. They split there
because each needs different API clients — and they stay separate because a
single mega-skill produces context bloat and verdicts nobody can read.

Then the part that makes it honest. **Not every control is equally verifiable:**

| Control | Confidence | Why |
|---|---|---|
| C1 default-deny / least privilege | HIGH | policy documents plus observed usage are readable |
| C3 identity chain / OBO | HIGH | delegation is impossible without an actor token, so its presence is proof |
| C4 gateway routing | HIGH **if** egress is enforced below the application | otherwise an agent opens a socket and bypasses it |
| C2 sandbox / no egress | **PARTIAL, capped** | absence of a covert channel is not provable; DNS and object-storage bypasses are documented |
| C5 injection screening | **PARTIAL, capped** | detector presence is verifiable; adaptive attacks drive published defences back above 95% success |

A tool that reports PASS on C2 or C5 is wrong, and the cap belongs in the
artefact rather than in a footnote.
""",
 "steps": [
  ("md", "## 2 · The skill that does the static half"),
  ("py", SKILL_RUNTIME),
  ("skill", "attestation/agent-code-surface-analyzer"),

  ("md", "## 3 · Control intent, and why it is the honest static claim\\n\\n"
         "Static analysis cannot show that a control **holds**. It can show "
         "that somebody **intended** it — an imported sandbox, a validated "
         "audience claim, a provenance tag. That is a smaller claim and a true "
         "one, so the analyser never emits PASS."),
  ("py", '''SIGNALS = {
 "C1_default_deny_least_privilege": ["default_deny", "allowlist", "policy engine",
                                     "authorisation check"],
 "C2_sandbox_no_egress":            ["isolation runtime", "kernel confinement",
                                     "network mode control"],
 "C3_identity_chain_obo":           ["workload identity", "delegation claim",
                                     "audience validation", "token exchange"],
 "C4_gateway_guardrails":           ["gateway", "guardrail", "egress policy"],
 "C5_injection_screening":          ["injection detector", "sanitisation",
                                     "provenance tagging"],
}
CEILINGS = {
 "C2_sandbox_no_egress": "absence of a covert channel is not provable from source",
 "C5_injection_screening": "detector presence is verifiable; robustness is not",
}
RUNTIME_ONLY = {
 "C1_default_deny_least_privilege": "observed usage and the effective role policy",
 "C4_gateway_guardrails": "reachability testing from the deployment network",
}

def verdict(control, hits):
    if not hits:
        return "NO_INTENT_FOUND", "no signal for this control in the source"
    if control in CEILINGS:
        return "PARTIAL", CEILINGS[control]
    if control in RUNTIME_ONLY:
        return "INTENT_EVIDENCED", f"runtime verdict needs {RUNTIME_ONLY[control]}"
    return "INTENT_EVIDENCED", f"{len(hits)} signals; enforcement not shown"

for c in sorted(SIGNALS):
    v, why = verdict(c, SIGNALS[c])
    print(f"{c:34s}{v:18s}{why[:44]}")
print()
print("PASS is not in the vocabulary. The strongest static verdict is")
print("INTENT_EVIDENCED, and two controls cannot exceed PARTIAL at all.")
assert "PASS" not in {verdict(c, SIGNALS[c])[0] for c in SIGNALS}
'''),

  ("md", "## 4 · Run against ten real repositories\\n\\n"
         "These are the verdicts the analyser in `labs/attestation/control_intent.py` "
         "produced against the five most-deployed open-source MCP repositories and "
         "five most-used agent frameworks, cloned at HEAD. Not a simulation — the "
         "counts below are what the scan returned."),
  ("py", '''CORPUS = [
 {
  "repo": "awslabs_mcp",
  "kind": "mcp",
  "files": 2616,
  "tool_sites": 140,
  "sinks": 5,
  "annotated": True,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "crewAIInc_crewAI",
  "kind": "agent",
  "files": 2105,
  "tool_sites": 35,
  "sinks": 5,
  "annotated": False,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "github_github-mcp-server",
  "kind": "mcp",
  "files": 258,
  "tool_sites": 41,
  "sinks": 3,
  "annotated": False,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "langchain-ai_langchain",
  "kind": "agent",
  "files": 2673,
  "tool_sites": 99,
  "sinks": 5,
  "annotated": False,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "langchain-ai_langgraph",
  "kind": "agent",
  "files": 538,
  "tool_sites": 20,
  "sinks": 4,
  "annotated": False,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "NO_INTENT_FOUND",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "microsoft_autogen",
  "kind": "agent",
  "files": 707,
  "tool_sites": 49,
  "sinks": 5,
  "annotated": True,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "modelcontextprotocol_python-sdk",
  "kind": "mcp",
  "files": 894,
  "tool_sites": 710,
  "sinks": 4,
  "annotated": True,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "modelcontextprotocol_servers",
  "kind": "mcp",
  "files": 100,
  "tool_sites": 9,
  "sinks": 3,
  "annotated": True,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "NO_INTENT_FOUND",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "NO_INTENT_FOUND"
  }
 },
 {
  "repo": "modelcontextprotocol_typescript-sdk",
  "kind": "mcp",
  "files": 957,
  "tool_sites": 58,
  "sinks": 2,
  "annotated": True,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "NO_INTENT_FOUND",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "openai_openai-agents-python",
  "kind": "agent",
  "files": 998,
  "tool_sites": 182,
  "sinks": 5,
  "annotated": False,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 }
]

print(f"{'repository':36s}{'kind':7s}{'files':>6}{'tools':>7}{'sinks':>6}  C1   C2   C3   C4   C5")
SHORT = {"INTENT_EVIDENCED": "INT", "PARTIAL": "PART", "NO_INTENT_FOUND": "-"}
for r in CORPUS:
    v = "".join(f"{SHORT[r['verdicts'][c]]:>5}" for c in ("C1","C2","C3","C4","C5"))
    print(f"{r['repo']:36s}{r['kind']:7s}{r['files']:>6}{r['tool_sites']:>7}{r['sinks']:>6}{v}")

evals = [r["verdicts"][c] for r in CORPUS for c in ("C1","C2","C3","C4","C5")]
print(f"\\ncontrol evaluations : {len(evals)}")
for k in ("INTENT_EVIDENCED", "PARTIAL", "NO_INTENT_FOUND"):
    print(f"   {k:20s}{evals.count(k)}")
print(f"   {'PASS':20s}{evals.count('PASS')}   <- static evidence cannot prove enforcement")
assert evals.count("PASS") == 0
'''),

  ("md", "## 5 · What the scan actually found\\n\\n"
         "Three findings worth more than the table."),
  ("py", '''unannotated = [r for r in CORPUS if r["kind"] == "mcp" and not r["annotated"]]
print("1. MCP servers shipping NO tool annotations:")
for r in unannotated:
    print(f"   {r['repo']:36s}{r['tool_sites']} tool declaration sites")
print("   The specification is explicit that annotations are hints, not")
print("   guarantees - and that an UNANNOTATED tool must be assumed")
print("   destructiveHint=true and openWorldHint=true. Every one of those")
print("   tool sites inherits that pessimistic default.")

gaps = [(r["repo"], c) for r in CORPUS for c in ("C1","C2","C3","C4","C5")
        if r["verdicts"][c] == "NO_INTENT_FOUND"]
print(f"\\n2. Controls with no intent anywhere in the source: {len(gaps)}")
for repo, c in gaps:
    print(f"   {repo:36s}{c}")

capped = [c for r in CORPUS for c in ("C2","C5") if r["verdicts"][c] == "PARTIAL"]
print(f"\\n3. Verdicts capped at PARTIAL by the ceiling rule: {len(capped)}")
print("   Not because the evidence was weak - because the claim is not")
print("   provable. An attestation that reported PASS here would be a")
print("   signed, tamper-evident overstatement, which is worse than none.")
assert unannotated and gaps and capped
'''),

  ("md", "## 6 · The artefact\\n\\n"
         "An in-toto statement, subject-bound to the deployment, predicate in "
         "assessment-results vocabulary. The signer is a separate skill and a "
         "separate role — an attester that also decides whether it passed is not "
         "an attestation."),
  ("py", '''import json

def attestation(repo_row, commit="c9e71f7"):
    controls = []
    for c in ("C1","C2","C3","C4","C5"):
        full = [k for k in SIGNALS if k.startswith(c)][0]
        controls.append({
            "id": full,
            "verdict": repo_row["verdicts"][c],
            "confidence": "CAPPED" if full in CEILINGS else "STATIC",
            "evidence": [{"skill": "agent-code-surface-analyzer",
                          "uri": f"labs/attestation/oss-corpus-results.json#{repo_row['repo']}"}],
        })
    return {
      "_type": "https://in-toto.io/Statement/v1",
      "subject": [{"name": repo_row["repo"], "digest": {"gitCommit": commit}}],
      "predicateType": "https://cyber-commons/attestations/ai-control-intent/v1",
      "predicate": {"deployment_id": repo_row["repo"],
                    "scope": "static source analysis only",
                    "controls": controls,
                    "drift": {"since": None, "changed": []}},
      "signatures": [],
    }

a = attestation(CORPUS[0])
print(json.dumps(a, indent=1)[:600])
print("   ...")
print()
print("`signatures` is empty and says so. A relying party MUST fail closed on a")
print("missing or unsigned attestation: a signed file can be deleted, and")
print("absence must never be read as a pass.")
assert a["signatures"] == [] and a["predicate"]["scope"].startswith("static")
'''),
 ],
 "expect": "Five controls resolve to INTENT_EVIDENCED, PARTIAL or NO_INTENT_FOUND "
           "and never to PASS. Across ten real repositories and fifty control "
           "evaluations the analyser returns 30 INTENT_EVIDENCED, 16 PARTIAL, 4 "
           "NO_INTENT_FOUND and zero PASS — with one widely-deployed MCP server "
           "shipping no tool annotations at all, so all of its tool sites inherit "
           "the specification's destructive, open-world default.",
 "challenge": "Run the analyser against one agent or MCP server you actually "
              "deploy. The interesting output is not the verdicts — it is the "
              "controls that come back NO_INTENT_FOUND, because those are the "
              "ones nobody has started.",
},

"B2.14": {
 "concept": """
**Bonus.** You have now built all fifteen stages. This lesson looks at a real
implementation of the same pipeline — **[Google Mantis](https://github.com/google/mantis)**
— and does the one thing that matters before adopting any of them: maps its
stages onto yours, then **scores it with your own held-out key.**

Two things are worth understanding about Mantis specifically.

**It is model-agnostic.** Mantis ships security-review *skills* for coding
agents rather than a bundled model. That is the same architecture as this track:
the pipeline is the product, the model is a component. It means you can run it
on open weights — GLM-4.6, Kimi K2 — which is what makes it usable without a
frontier account.

**It has two output shapes**, and they serve different stages:

- a **`learning_entry`** — appended to a historical learnings file, feeding
  stage 1 (historical parsing) on the next run;
- a **`finding`** object — a vulnerability report, feeding stages 8–10.

That first shape is the interesting one. It closes the loop from Phase 5 back to
Phase 1, which is the property that turns a pipeline into something that
improves.

The bonus framing is deliberate: a reference implementation is a **starting
point you evaluate**, not a product you trust. B2.1 and C2.6 gave you the tools;
this is where you point them at someone else's pipeline.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Map Mantis onto the fifteen stages\n\n"
         "Adoption starts with the coverage question: which stages does it do, "
         "which does it assume you already have, and which are still yours?"),
  ("py", '''STAGES = {
 1:  "historical parsing",        2:  "structural indexing",
 3:  "component summarisation",   4:  "architecture synthesis",
 5:  "threat modelling",          6:  "strategic planning",
 7:  "vulnerability auditing",    8:  "deduplication",
 9:  "contextual verification",  10:  "feasibility filtering",
 11: "sandbox replication",      12:  "dynamic exploitation",
 13: "exploit chaining",         14:  "remediation engineering",
 15: "severity calibration and reporting",
}
# Coverage as observed from the project's own documented outputs and skills.
MANTIS = {
 1:  ("yes",     "historical_learnings.jsonl is read on subsequent runs"),
 2:  ("partial", "operates over the agent's code-reading tools"),
 3:  ("partial", "context assembled per review target"),
 4:  ("no",      "assumes you supply the architecture context"),
 5:  ("partial", "review skills encode threat patterns rather than deriving them"),
 6:  ("no",      "you decide what to point it at"),
 7:  ("yes",     "the core: security-review skills emitting finding objects"),
 8:  ("partial", "findings are structured, so dedup is possible downstream"),
 9:  ("partial", "structured output aids verification; you still run the checks"),
 10: ("no",      "reachability is yours"),
 11: ("no",      "no sandbox — it is a review harness, not a DAST"),
 12: ("no",      "static review only"),
 13: ("no",      "no chaining"),
 14: ("partial", "can propose fixes; validation is yours (B2.9)"),
 15: ("partial", "emits severity; calibration against confirmation is yours"),
}
print(f"{'stage':>3}  {'name':34s}{'mantis':10s}note")
print("-" * 96)
for n, name in STAGES.items():
    cov, note = MANTIS[n]
    print(f"{n:>3}  {name:34s}{cov:10s}{note}")
from collections import Counter
c = Counter(v[0] for v in MANTIS.values())
print(f"\\ncoverage: {dict(c)}")
print(f"→ Mantis is a strong Phase 3 stage-7 implementation with a stage-1 loop.")
print(f"  Phases 4 and 5 remain yours, which is exactly what B2.6-B2.10 built.")
'''),
  ("md", "## 3 · Parse the two output shapes\n\n"
         "Before scoring anything you have to ingest it. Both shapes are JSON; "
         "the `history` field on a learning entry is required and is the one most "
         "commonly missing in a first integration."),
  ("py", '''import json

LEARNING_REQUIRED = ("title", "description", "history")
FINDING_REQUIRED  = ("title", "description", "severity", "file", "cwe")

SAMPLE = [
 # learning_entry — feeds stage 1 on the next run
 '{"type":"learning_entry","title":"owner filter built by concatenation",'
 '"description":"reports queries interpolate the owner parameter",'
 '"history":"introduced in c3d4e5f, fixed once in 2025 and reintroduced"}',
 # finding — feeds stages 8-10
 '{"type":"finding","title":"SQL injection in list_reports","severity":"high",'
 '"file":"src/data/reports.py","cwe":"CWE-89",'
 '"description":"owner is concatenated into the query string"}',
 # a learning entry missing the required history field
 '{"type":"learning_entry","title":"path join in docs",'
 '"description":"docs fetch joins user input"}',
 # a finding with a null field
 '{"type":"finding","title":"traversal","severity":"medium",'
 '"file":"src/data/docs.py","cwe":null,'
 '"description":"name is joined onto the base path"}',
 # not JSON at all
 'I found a SQL injection in the reports module.',
]

def ingest(raw):
    try:
        d = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"non-conforming: not JSON ({e.msg})"
    kind = d.get("type")
    required = (LEARNING_REQUIRED if kind == "learning_entry"
                else FINDING_REQUIRED if kind == "finding" else None)
    if required is None:
        return None, f"non-conforming: unknown type {kind!r}"
    missing = [k for k in required if not d.get(k)]
    if missing:
        return None, f"non-conforming: {kind} missing {missing}"
    return d, "conforming"

conforming = []
for raw in SAMPLE:
    obj, note = ingest(raw)
    if obj: conforming.append(obj)
    print(f"{note:58s}{raw[:44]}…")
print(f"\\nconformance: {len(conforming)}/{len(SAMPLE)} = {len(conforming)/len(SAMPLE):.2f}")
'''),
  ("md", "## 4 · Score it against a held-out key\n\n"
         "This is the whole point of the bonus. Conformance is structural — with "
         "structured output it goes to 1.00 and says nothing about quality. The "
         "number that decides adoption is expert accuracy against a key the tool "
         "never saw, matched on **parent directory plus filename** (B2.1)."),
  ("py", '''def path_key(p):
    parts = [x for x in (p or "").replace("\\\\","/").split("/") if x not in ("",".")]
    return "/".join(parts[-2:]) if len(parts) > 1 else (parts[-1] if parts else "")

HELD_OUT = {
 "src/data/reports.py": "CWE-89",
 "src/data/docs.py":    "CWE-22",
 "src/web/handlers.py": "CWE-306",     # a finding Mantis did not report
}

def score(findings, truth):
    expert, rows = 0.0, []
    reported = {}
    for f in findings:
        if f.get("type") != "finding": continue
        reported[path_key(f["file"])] = f
    for path, cwe in truth.items():
        f = reported.get(path_key(path))
        if f is None:
            rows.append((path, "MISSED", 0.0)); continue
        if (f.get("cwe") or "").upper() == cwe:
            rows.append((path, "correct", 1.0)); expert += 1.0
        else:
            rows.append((path, f"right file, wrong class ({f.get('cwe')})", 0.5))
            expert += 0.5
    return {"expert_accuracy": round(expert/len(truth), 4), "rows": rows}

# include the null-cwe finding, re-ingested leniently, to show the half-credit case
lenient = [json.loads(r) for r in SAMPLE if r.startswith("{")]
s = score(lenient, HELD_OUT)
print(f"{'file':26s}{'result':38s}score")
print("-" * 74)
for path, result, pts in s["rows"]:
    print(f"{path:26s}{result:38s}{pts}")
print(f"\\nconformance       {len(conforming)/len(SAMPLE):.4f}   ← structural. NOT quality.")
print(f"expert accuracy   {s['expert_accuracy']:.4f}   ← the adoption number")
assert s["expert_accuracy"] < 1.0
'''),
  ("py", '''# Close the loop: a learning entry feeds stage 1 of the NEXT run.
learnings = [d for d in conforming if d["type"] == "learning_entry"]
print(f"{len(learnings)} learning entry/entries carried into the next run:")
for l in learnings:
    print(f"   {l['title']}")
    print(f"      history: {l['history']}")

def next_run_risk_zones(learnings, findings):
    zones = {}
    for f in findings:
        if f.get("type") == "finding":
            zones[f["file"]] = zones.get(f["file"], 0) + 1
    for l in learnings:
        if "reintroduced" in l.get("history", ""):
            for f in findings:
                if f.get("type") == "finding" and l["title"].split()[0] in f["description"]:
                    zones[f["file"]] = zones.get(f["file"], 0) + 2
    return sorted(zones.items(), key=lambda kv: -kv[1])

print("\\nstage 1 input for the next run (Phase 5 → Phase 1):")
for path, weight in next_run_risk_zones(learnings, lenient):
    print(f"   {path:26s} weight {weight}")

print("\\nADOPTION CHECKLIST")
for item in [
  "map its stages onto your fifteen — know what it does NOT do",
  "score it against YOUR held-out key before trusting a single finding",
  "report conformance and accuracy separately, always",
  "keep Phase 4 — a static reviewer cannot confirm exploitability",
  "feed learning entries back into stage 1, or the loop does not close",
]:
    print(f"   · {item}")
'''),
 ],
 "expect": "The stage map shows Mantis covering stage 7 strongly with a stage-1 "
           "learning loop, and not covering Phase 4 at all. Three of five sample "
           "outputs conform — one learning entry is missing the required "
           "`history` field, one finding has a null CWE, and one is prose. "
           "Scored against the held-out key, expert accuracy is below 1.0: one "
           "correct, one half credit for the null class, and one missed finding "
           "Mantis never reported. The learning entry then feeds the next run's "
           "risk zones.",
 "challenge": "Run the real thing: clone `google/mantis`, point it at a "
              "repository you have ground truth for, and score its output with "
              "the harness from B2.1. The gap between its conformance and its "
              "expert accuracy on *your* code is the only number that should "
              "decide whether you adopt it.",
},
}
