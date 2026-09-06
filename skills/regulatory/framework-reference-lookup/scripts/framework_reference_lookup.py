#!/usr/bin/env python3
"""Read the commons' own framework mapping and answer which controls a lesson speaks to, and which lessons speak to a control.

This is the executable half of `framework-reference-lookup`. It does not carry
its own copy of the frameworks — it reads `curriculum/frameworks.json`, the file
every lesson page is labelled from, so the reference tables here and the chips
on a lesson can never disagree.

Standard library only, and deterministic.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FW = json.loads((ROOT / "curriculum" / "frameworks.json").read_text())
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())

LESSONS = [(s["id"], t["id"])
           for f in CUR["functions"] for t in f["tracks"] for s in t["sessions"]]


def labels(sid, tid):
    row = FW["lessons"].get(sid) or FW["tracks"].get(tid, {})
    return {k: row.get(k, []) for k in ("owasp", "atlas", "nist", "euai")}


report = {"frameworks": [], "euai_articles": [], "coverage": {},
          "lookup": {"by_lesson": {}, "by_control": {}}}
for name, url, size in (
        ("OWASP LLM Top 10", FW["urls"]["owasp_llm"]["LLM01"], "10 risks"),
        ("OWASP Agentic Top 10", FW["urls"]["owasp_agentic"], "15 threats"),
        ("MITRE ATLAS", FW["urls"]["atlas"], "tactics"),
        ("NIST AI RMF 1.0", FW["urls"]["nist"], "4 functions"),
        ("EU AI Act", FW["urls"]["euai"], f"{len(FW['euai_titles'])} articles")):
    report["frameworks"].append({"name": name, "url": url, "size": size})

print("the four vocabularies this curriculum labels against")
print()
print(f"  {'OWASP LLM Top 10':<26}{len(FW['urls']['owasp_llm'])} risks, LLM01-LLM10")
print(f"  {'OWASP Agentic Top 10':<26}15 threats, T1-T15")
print(f"  {'MITRE ATLAS':<26}adversary tactics against AI systems")
print(f"  {'NIST AI RMF 1.0':<26}4 functions: GOVERN, MAP, MEASURE, MANAGE")
print(f"  {'EU AI Act':<26}{len(FW['euai_titles'])} articles referenced here")
print()

# Reference table 1 — the EU AI Act articles, with what each one is about.
print("EU AI Act articles this curriculum touches")
for art, title in FW["euai_titles"].items():
    n = sum(1 for sid, tid in LESSONS if art in labels(sid, tid)["euai"])
    print(f"   {art:<9}{title:<52}{n:>3} lesson{'s' if n != 1 else ''}")
    report["euai_articles"].append({"article": art, "title": title, "lessons": n})
print()

# Reference table 2 — coverage per vocabulary, so a gap is visible.
print("coverage: how many lessons carry each label")
for kind, title in (("nist", "NIST AI RMF"), ("owasp", "OWASP")):
    counts = {}
    for sid, tid in LESSONS:
        for code in labels(sid, tid)[kind]:
            counts[code] = counts.get(code, 0) + 1
    row = "  ".join(f"{c}:{n}" for c, n in sorted(counts.items()))
    print(f"   {title:<14}{row}")
    report["coverage"][kind] = dict(sorted(counts.items()))
print()

# The lookup itself, both directions.
def for_lesson(sid):
    tid = dict((a, b) for a, b in LESSONS)[sid]
    f = labels(sid, tid)
    return [f"{k.upper()} {c}" for k in ("owasp", "atlas", "nist", "euai") for c in f[k]]

def for_control(kind, code):
    return [sid for sid, tid in LESSONS if code in labels(sid, tid)[kind]]

print("lookup, both directions")
for sid in ("A1.2", "B2.3", "D5.4"):
    report["lookup"]["by_lesson"][sid] = for_lesson(sid)
    print(f"   {sid:<8}{' · '.join(for_lesson(sid))}")
print()
art = "Art. 14"
hits = for_control("euai", art)
report["lookup"]["by_control"][art] = hits
print(f"   {art} ({FW['euai_titles'][art]})")
print(f"      {len(hits)} lessons: {', '.join(hits[:8])}"
      + (" ..." if len(hits) > 8 else ""))
print()
print("Reading it the second way is the one that matters in an audit. Nobody")
print("asks 'what does lesson A1.2 map to'. They ask 'show me where human")
print("oversight is addressed', and the answer has to be a list of things that")
print("exist, not a paragraph saying it is covered.")
print()
print("Every label links to the published source, and those links are fetched in")
print("CI - so a framework that renumbers its pages breaks the build rather than")
print("quietly leaving a lesson pointing at a 404.")

assert len(FW["urls"]["owasp_llm"]) == 10
assert set(FW["tracks"]) >= {"A1", "B2", "D1", "E1"}
assert for_lesson("A1.2"), "A1.2 must carry labels"
assert hits, "no lesson maps to human oversight, which cannot be right"
assert report["frameworks"] and report["euai_articles"] and report["coverage"]
