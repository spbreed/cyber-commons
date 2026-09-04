#!/usr/bin/env python3
"""Score a zero-capability harness against a skewed corpus and again against a balanced one, and watch the number collapse.

This is the executable half of the `eval-corpus-integrity-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import json
from dataclasses import dataclass

@dataclass
class Truth:
    qid: str; cwe: str; file: str

def make_corpus(n=40, skew=0.8):
    """A corpus where `skew` of the answers are one class — very common."""
    truths = {}
    n_major = int(n * skew)
    for i in range(1, n + 1):
        cwe = "CWE-89" if i <= n_major else ["CWE-78", "CWE-22", "CWE-798"][i % 3]
        truths[f"q{i}"] = Truth(f"q{i}", cwe, f"{cwe}/{i}.py")
    return truths

SKEWED = make_corpus(40, skew=0.8)
from collections import Counter
print("class balance:", Counter(t.cwe for t in SKEWED.values()))

class NullHarness:
    """No capability whatsoever. Emits perfect JSON and always guesses CWE-89."""
    def answer(self, qid, truth):
        return json.dumps({"qid": qid, "cwe": "CWE-89", "file": truth.file,
                           "line": 1, "rationale": "user input is concatenated"})

null = NullHarness()
ANSWERS = {q: null.answer(q, t) for q, t in SKEWED.items()}

def path_key(p):
    parts = [x for x in p.replace("\\", "/").split("/") if x not in ("", ".")]
    return "/".join(parts[-2:]) if len(parts) > 1 else (parts[-1] if parts else "")
def basename(p): return p.replace("\\", "/").split("/")[-1]

def evaluate(answers, truths, matcher=path_key):
    conforming = expert = 0
    for qid, t in truths.items():
        try:
            d = json.loads(answers[qid])
        except json.JSONDecodeError:
            continue
        conforming += 1
        if matcher(d["file"]) != matcher(t.file):
            continue
        expert += 1.0 if d["cwe"].upper() == t.cwe else 0.5
    return {"conformance": conforming / len(truths),
            "expert_accuracy": expert / len(truths)}

r = evaluate(ANSWERS, SKEWED)
print("the null harness, scored on the skewed corpus:")
print(f"   conformance      {r['conformance']:.2f}   ← quotable as '100%'")
print(f"   expert accuracy  {r['expert_accuracy']:.2f}")
print("\nZero capability. Both numbers look like a working product.")

BALANCED = {}
for i in range(1, 41):
    cwe = ["CWE-89", "CWE-78", "CWE-22", "CWE-798"][i % 4]
    BALANCED[f"q{i}"] = Truth(f"q{i}", cwe, f"{cwe}/{i}.py")
ANS_B = {q: null.answer(q, t) for q, t in BALANCED.items()}

print("same null harness:")
for label, truths, ans in (("skewed corpus (80% CWE-89)", SKEWED, ANSWERS),
                           ("balanced corpus", BALANCED, ANS_B)):
    r = evaluate(ans, truths)
    print(f"   {label:28s} conformance {r['conformance']:.2f}  "
          f"expert accuracy {r['expert_accuracy']:.2f}")
print("\nBalancing the corpus removed most of the fake score. Nothing about the")
print("harness changed.")

# exploit 3: a matcher that compares bare filenames.
# Build answers that point at the WRONG directory but the right filename.
WRONG_DIR = {}
for q, t in BALANCED.items():
    n = q[1:]
    WRONG_DIR[q] = json.dumps({"qid": q, "cwe": t.cwe,
                               "file": f"CWE-89/{n}.py",     # wrong dir, right basename
                               "line": 1, "rationale": "untrusted input"})

for matcher, name in ((path_key, "path_key (parent + filename)"),
                      (basename, "basename only (the bug)")):
    r = evaluate(WRONG_DIR, BALANCED, matcher)
    print(f"{name:34s} expert accuracy {r['expert_accuracy']:.2f}")
print("\nEvery answer names the wrong file. The basename matcher scores them")
print("as correct, because the corpus reuses numeric filenames across directories.")

def audit_benchmark(truths, answers, matcher):
    from collections import Counter
    counts = Counter(t.cwe for t in truths.values())
    majority_share = max(counts.values()) / len(truths)
    always_majority = {q: json.dumps({"qid": q, "cwe": counts.most_common(1)[0][0],
                                      "file": t.file, "line": 1, "rationale": "x"})
                       for q, t in truths.items()}
    floor = evaluate(always_majority, truths, matcher)["expert_accuracy"]
    real  = evaluate(answers, truths, matcher)
    collisions = len(truths) - len({matcher(t.file) for t in truths.values()})
    return {
      "majority_class_share": round(majority_share, 2),
      "score_of_always_guessing_majority": round(floor, 2),
      "reported_expert_accuracy": round(real["expert_accuracy"], 2),
      "lift_over_trivial_baseline": round(real["expert_accuracy"] - floor, 2),
      "matcher_collisions": collisions,
      "conformance_reported_as_quality": real["expert_accuracy"] < real["conformance"] - 0.2,
    }

print("audit of the skewed benchmark with a basename matcher:")
for k, v in audit_benchmark(SKEWED, ANSWERS, basename).items():
    print(f"   {k:38s} {v}")
print("\naudit of the balanced benchmark with path_key:")
for k, v in audit_benchmark(BALANCED, ANS_B, path_key).items():
    print(f"   {k:38s} {v}")

a = audit_benchmark(BALANCED, ANS_B, path_key)
assert a["lift_over_trivial_baseline"] <= 0.01
print("\nThe null harness has ~zero lift over the trivial baseline, which is the")
print("only honest way to describe it.")
