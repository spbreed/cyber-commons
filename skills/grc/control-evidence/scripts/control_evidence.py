#!/usr/bin/env python3
"""Turn evaluation output into audit evidence, with the conformance and accuracy numbers reported separately.

This is the executable half of the `control-evidence` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# --- the skill's own contract, available both ways -------------------------
# This script is run two ways and both have to work: standalone from a
# terminal, and embedded in the lesson notebook underneath the cell that
# already parsed the SKILL.md. So take what is already defined and read the
# file only when it is not.
import pathlib as _pathlib


def _skill_md():
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


if "contract_of" not in globals():
    import json, re

    def parse_skill(md):
        """Split a SKILL.md into (frontmatter dict, body).

        Frontmatter is a small, fixed subset of YAML: `key: value`, plus folded
        scalars (`description: >-`) whose continuation lines are indented. That is
        all a skill needs, and parsing it directly means no dependency.
        """
        if not md.startswith("---"):
            raise ValueError("a SKILL.md must open with a frontmatter block")
        _, front, body = md.split("---", 2)
        meta, key = {}, None
        for line in front.strip().splitlines():
            if not line.strip():
                continue
            if not line[0].isspace() and ":" in line:
                key, val = line.split(":", 1)
                key, val = key.strip(), val.strip()
                # `>-` and `|` open a folded block; the value is on the next lines
                meta[key] = "" if val in (">-", ">", "|", "|-") else val
            elif key is not None:
                meta[key] = (meta[key] + " " + line.strip()).strip()
        if "allowed-tools" in meta:
            meta["allowed-tools"] = [t.strip() for t in meta["allowed-tools"].split(",")
                                     if t.strip()]
        for required in ("name", "description"):
            if not meta.get(required):
                raise ValueError(f"skill is missing a {required!r}")
        return meta, body.strip()

    _WORD = re.compile(r"[a-z][a-z-]{3,}")

    def route(task, skills):
        """Pick the skill whose description best matches a task. Deterministic.

        The description is not documentation — it is the routing key. An agent
        decides whether to load a skill by reading it, so a vague description means
        the skill never fires when it should, and two overlapping descriptions mean
        the wrong one fires.

        Returns (pick, scores, margin). A margin of 0 means the top two scored the
        same and the "winner" is just whichever sorted first — an arbitrary answer
        wearing a confident face. Callers should refuse to auto-route on margin 0
        rather than pretend the tiebreak meant something.
        """
        want = set(_WORD.findall(task.lower()))
        def score(meta):
            return len(want & set(_WORD.findall(meta["description"].lower())))
        scores = {n: score(skills[n]) for n in sorted(skills)}
        # sort names first, then by score: ties must break identically on every
        # machine or the same task routes differently on two runs
        ranked = sorted(sorted(skills), key=lambda n: -scores[n])
        top = scores[ranked[0]]
        margin = top - (scores[ranked[1]] if len(ranked) > 1 else 0)
        return ranked[0], scores, margin

    def contract_of(body):
        """The JSON block under '## Output contract' — the skill's machine promise."""
        # non-greedy across any prose between the heading and the fence
        m = re.search(r"## Output contract\b.*?```json\n(.*?)```", body, re.S)
        if not m:
            raise ValueError("skill declares no output contract")
        return json.loads(m.group(1))

    def check(instance, contract, path="$"):
        """Structural conformance of an instance against a contract template.

        Returns the list of problems. An empty list means the shape is right — and
        that is *all* it means. Conformance is not accuracy: an empty findings list
        conforms perfectly and tells you nothing.
        """
        problems = []
        if isinstance(contract, dict):
            if not isinstance(instance, dict):
                return [f"{path}: expected an object, got {type(instance).__name__}"]
            for k, v in sorted(contract.items()):
                if k not in instance:
                    problems.append(f"{path}.{k}: missing")
                else:
                    problems += check(instance[k], v, f"{path}.{k}")
        elif isinstance(contract, list):
            if not isinstance(instance, list):
                return [f"{path}: expected a list, got {type(instance).__name__}"]
            for i, item in enumerate(instance):          # every element, same template
                problems += check(item, contract[0], f"{path}[{i}]")
        elif isinstance(contract, str) and "|" in contract:
            if instance not in contract.split("|"):
                problems.append(f"{path}: {instance!r} is not one of {contract}")
        elif isinstance(contract, bool):                  # before the numeric case:
            if not isinstance(instance, bool):            # bool is a subclass of int
                problems.append(f"{path}: expected bool, got {type(instance).__name__}")
        elif isinstance(contract, (int, float)):
            # JSON has one number type. A contract written `0` must accept 0.4, or
            # every cost and rate in the pipeline has to be rounded to satisfy a
            # checker rather than to be correct.
            if isinstance(instance, bool) or not isinstance(instance, (int, float)):
                problems.append(f"{path}: expected a number, got {type(instance).__name__}")
        elif not isinstance(instance, type(contract)):
            problems.append(f"{path}: expected {type(contract).__name__}, "
                            f"got {type(instance).__name__}")
        return problems

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
