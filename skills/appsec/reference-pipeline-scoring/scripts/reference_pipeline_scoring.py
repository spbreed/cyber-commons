#!/usr/bin/env python3
"""Map a published pipeline onto the stage model and score its output against a held-out key.

This is the executable half of the `reference-pipeline-scoring` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

STAGES = {
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
print(f"\ncoverage: {dict(c)}")
print(f"→ Mantis is a strong Phase 3 stage-7 implementation with a stage-1 loop.")
print(f"  Phases 4 and 5 remain yours, which is exactly what B2.6-B2.10 built.")

import json

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
print(f"\nconformance: {len(conforming)}/{len(SAMPLE)} = {len(conforming)/len(SAMPLE):.2f}")

def path_key(p):
    parts = [x for x in (p or "").replace("\\","/").split("/") if x not in ("",".")]
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
print(f"\nconformance       {len(conforming)/len(SAMPLE):.4f}   ← structural. NOT quality.")
print(f"expert accuracy   {s['expert_accuracy']:.4f}   ← the adoption number")
assert s["expert_accuracy"] < 1.0

# Close the loop: a learning entry feeds stage 1 of the NEXT run.
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

print("\nstage 1 input for the next run (Phase 5 → Phase 1):")
for path, weight in next_run_risk_zones(learnings, lenient):
    print(f"   {path:26s} weight {weight}")

print("\nADOPTION CHECKLIST")
for item in [
  "map its stages onto your fifteen — know what it does NOT do",
  "score it against YOUR held-out key before trusting a single finding",
  "report conformance and accuracy separately, always",
  "keep Phase 4 — a static reviewer cannot confirm exploitability",
  "feed learning entries back into stage 1, or the loop does not close",
]:
    print(f"   · {item}")
