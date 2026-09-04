#!/usr/bin/env python3
"""Report conformance and expert accuracy separately, with control coverage, and rehearse the three openings a regulator uses.

This is the executable half of the `assurance-conversation-prep` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import json, time
from dataclasses import dataclass
now = time.time(); DAY = 86400

@dataclass
class Truth:
    qid: str; cwe: str; file: str

def path_key(p):
    parts = [x for x in p.replace("\\","/").split("/") if x not in ("",".")]
    return "/".join(parts[-2:]) if len(parts) > 1 else (parts[-1] if parts else "")

TRUTHS = {f"q{i}": Truth(f"q{i}", ["CWE-89","CWE-78"][i % 2],
                         f"{['CWE-89','CWE-78'][i % 2]}/{i}.py") for i in range(1, 21)}
ANSWERS = {q: json.dumps({"qid": q, "cwe": "CWE-89", "file": t.file,
                          "rationale": "untrusted input is concatenated"})
           for q, t in TRUTHS.items()}

def evaluate(answers, truths):
    conf = expert = 0
    for q, t in truths.items():
        try: d = json.loads(answers[q])
        except (json.JSONDecodeError, KeyError): continue
        conf += 1
        if path_key(d["file"]) != path_key(t.file): continue
        expert += 1.0 if d["cwe"].upper() == t.cwe else 0.5
    return {"n": len(truths), "conformance": round(conf/len(truths), 4),
            "expert_accuracy": round(expert/len(truths), 4)}

R = evaluate(ANSWERS, TRUTHS)
print(f"n                {R['n']}")
print(f"conformance      {R['conformance']:.4f}")
print(f"expert accuracy  {R['expert_accuracy']:.4f}")

@dataclass
class ControlTest:
    cid: str; passed: bool; tested_at: float; valid_for_days: float
    def state(self, at):
        if (at - self.tested_at)/DAY > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]
TESTS = {t.cid: t for t in [
 ControlTest("AC-1", True,  now -  4*DAY, 30),
 ControlTest("AC-2", True,  now -  9*DAY, 30),
 ControlTest("SB-1", True,  now - 45*DAY, 30),
 ControlTest("EV-1", True,  now -  5*DAY, 60),
 ControlTest("EV-2", True,  now - 12*DAY, 30)]}

rows = [(c, TESTS[c].state(now) if c in TESTS else "NO EVIDENCE") for c in REQUIRED]
evidenced = sum(1 for _, s in rows if s == "PASS")
print(f"{'control':9s}{'state':14s}")
print("-" * 24)
for c, s in rows: print(f"{c:9s}{s:14s}")
print(f"\ncoverage: {evidenced}/{len(REQUIRED)} = {evidenced/len(REQUIRED):.0%}")

def disclosure(evalr, rows, required):
    evidenced = [c for c, s in rows if s == "PASS"]
    stale     = [c for c, s in rows if s == "STALE"]
    missing   = [c for c, s in rows if s == "NO EVIDENCE"]
    failing   = [c for c, s in rows if s == "FAIL"]
    plan = {"SB-1": "re-tested by 2026-08-31 (automation in progress)",
            "DR-1": "drift alerting deployed by 2026-10-15",
            "ST-1": "game day scheduled 2026-09-12"}
    lines = [
      f"1. Two numbers, and they measure different things.",
      f"   conformance {evalr['conformance']:.0%} — schema validity, structural, "
      f"not a quality claim.",
      f"   expert accuracy {evalr['expert_accuracy']:.0%} against a held-out key "
      f"of {evalr['n']} questions. That is the number that means something.",
      f"",
      f"2. Control coverage {len(evidenced)}/{len(required)} = "
      f"{len(evidenced)/len(required):.0%}, counting only controls that are "
      f"currently evidenced.",
      f"   stale: {stale or 'none'}   failing: {failing or 'none'}   "
      f"no evidence: {missing or 'none'}",
      f"",
      f"3. What we have not done, and when we will:",
    ]
    for c in stale + failing + missing:
        lines.append(f"   {c}: {plan.get(c, 'plan to be confirmed')}")
    return "\n".join(lines)

print(disclosure(R, rows, REQUIRED))
print("\nRehearse the second section out loud. If naming your weakest control is")
print("uncomfortable, that discomfort is the reason to say it first.")
assert R["expert_accuracy"] < R["conformance"]
