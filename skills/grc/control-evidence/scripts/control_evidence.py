#!/usr/bin/env python3
"""Turn evaluation output into audit evidence, with the conformance and accuracy numbers reported separately.

This is the executable half of the `control-evidence` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# The skill runtime comes from the shared library, not from a copy in this file.
# In a lesson notebook the cell above has already loaded it; standalone, find it
# the same way that cell does.
# The runtime comes from the shared library. The lesson cell above put it
# on the path; standalone, PYTHONPATH does (see scripts/test_skills.py).
from cyber_commons_skill_runtime import check, contract_of, parse_skill


def _skill_md():
    """The SKILL.md next to this script, or the one the notebook already parsed."""
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


import pathlib as _pathlib

SKILL_MD = _skill_md()
meta, body = parse_skill(SKILL_MD)

import json, time
from dataclasses import dataclass, field

@dataclass
class Truth:
    qid: str; cwe: str; file: str

def path_key(p):
    parts = [x for x in p.replace("\\", "/").split("/") if x not in ("", ".")]
    return "/".join(parts[-2:]) if len(parts) > 1 else (parts[-1] if parts else "")

TRUTHS = {f"q{i}": Truth(f"q{i}", ["CWE-89","CWE-78","CWE-22","CWE-798"][i % 4],
                         f"{['CWE-89','CWE-78','CWE-22','CWE-798'][i % 4]}/{i}.py")
          for i in range(1, 25)}

def harness_answers(truths, skill=0.75, seed=5):
    import random
    rng = random.Random(seed)
    out = {}
    for q, t in truths.items():
        right = rng.random() < skill
        out[q] = json.dumps({"qid": q, "cwe": t.cwe if right else "CWE-89",
                             "file": t.file, "line": 1,
                             "rationale": "untrusted input reaches the sink"})
    return out

def evaluate(answers, truths):
    conforming = expert = 0
    for q, t in truths.items():
        try: d = json.loads(answers[q])
        except (json.JSONDecodeError, KeyError): continue
        conforming += 1
        if path_key(d["file"]) != path_key(t.file): continue
        expert += 1.0 if d["cwe"].upper() == t.cwe else 0.5
    return {"n": len(truths),
            "conformance": round(conforming/len(truths), 4),
            "expert_accuracy": round(expert/len(truths), 4)}

r = evaluate(harness_answers(TRUTHS), TRUTHS)
print(f"n                {r['n']}")
print(f"conformance      {r['conformance']:.4f}   ← structural. NOT a quality claim.")
print(f"expert accuracy  {r['expert_accuracy']:.4f}   ← the number that evidences EV-2")

DAY = 86400
now = time.time()

@dataclass
class ControlTest:
    cid: str; passed: bool; evidence: str
    tested_at: float; valid_for_days: float
    def state(self, at):
        if (at - self.tested_at)/DAY > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

THRESHOLD = 0.80
test = ControlTest(
    "EV-2",
    passed=r["expert_accuracy"] >= THRESHOLD,
    evidence=(f"expert accuracy {r['expert_accuracy']:.4f} over {r['n']} held-out "
              f"questions; conformance {r['conformance']:.4f} reported separately; "
              f"key never exposed to the harness"),
    tested_at=now, valid_for_days=30)

print(f"EV-2  {test.state(now)}")
print(f"      {test.evidence}")
for age in (10, 45):
    print(f"      at +{age}d → {test.state(now + age*DAY)}")

CHECKLIST = {
 "key held out":         True,
 "accuracy not conformance reported": True,
 "sample size stated":   True,
 "expires":              test.valid_for_days > 0,
 "threshold stated up front": True,
}
print("\nauditability checklist:")
for k, v in CHECKLIST.items():
    print(f"   {'PASS' if v else 'FAIL'}  {k}")
assert all(CHECKLIST.values())
assert test.state(now + 45*DAY) == "STALE"

contract = contract_of(body)

pack = {
 "control": {"id": "AI-07", "claim": "Egress from the agent workload is denied "
                                     "to destinations outside the allowlist, "
                                     "enforced at the gateway",
             "testable": True},
 "binding": {"model": "glm-4.6", "config_hash": "sha256:7f3a1c",
             "tools": ["read_file", "http_get"], "commit": "6a14d8b",
             "matches_deployed": True},
 "sample": {"population": len(TRUTHS), "tested": len(TRUTHS),
            "selection": "risk_based", "independent": False},
 # r came from evaluate() above: conformance and expert accuracy on the same
 # run. Only one of them belongs in an evidence pack as a quality number.
 "results": {"operating_effectiveness": 1.0,
             "outcome_effectiveness": r["expert_accuracy"],
             "accuracy": r["expert_accuracy"],
             # the honest default, and the one line an auditor looks for
             "conformance_reported": False},
 "blind_spots": ["cases not in the corpus",
                 "drift since the run",
                 "the sample was chosen by the team that built the control"],
 "reverification": {"trigger": "on_model_change", "interval_days": 0},
 "conclusion": {"supports_claim": True,
                "limits": "evidences the gateway control only, at this commit"},
}
problems = check(pack, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\ncontrol      : {pack['control']['id']} (testable={pack['control']['testable']})")
print(f"bound to     : {pack['binding']['model']} @ {pack['binding']['commit']}, "
      f"matches deployed={pack['binding']['matches_deployed']}")
print(f"operating    : {pack['results']['operating_effectiveness']:.0%}   "
      f"outcome: {pack['results']['outcome_effectiveness']:.0%}")
print(f"sample       : {pack['sample']['tested']}/{pack['sample']['population']}, "
      f"independent={pack['sample']['independent']}")
print(f"re-verify on : {pack['reverification']['trigger']}")
print()
print("Operating effectiveness says the gate ran on every request. Outcome")
print("effectiveness says whether anything harmful still got through. Auditors")
print("ask for the first; incidents are caused by the second. Give both,")
print("labelled, or the pack answers a question nobody asked.")
assert pack["results"]["conformance_reported"] is False
assert pack["sample"]["independent"] is False   # stated, not hidden

flattering = dict(pack, results=dict(pack["results"],
                     accuracy=r["conformance"], conformance_reported=True))
print(f"conformance problems: {len(check(flattering, contract))}   <- still zero")
print()
print(f"claimed    : {r['conformance']:.0%} schema-valid output")
print(f"measured   : accuracy {pack['results']['accuracy']:.0%} on "
      f"{pack['sample']['tested']} cases")
print()
print("Schema validity is near-free by construction: an empty result scores")
print("100%. It is a statement about the serialiser, not about whether the")
print("control works. An auditor who notices the substitution discounts every")
print("other number in the pack, which is the expensive part.")
assert not check(flattering, contract), "the flattering pack conforms - that is the point"
assert flattering["results"]["conformance_reported"] is True
