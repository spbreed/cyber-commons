#!/usr/bin/env python3
"""Run a suite with intervals, show a control moving one surface and not the others, and detect the suite being diluted by easy cases.

This is the executable half of the `eval-suite-health-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import random
from dataclasses import dataclass

@dataclass(frozen=True)
class Case:
    cid: str; surface: str; payload: str; landing_rate: float

SUITE = [
 Case("INJ-01", "injection", "direct override", 0.05),
 Case("INJ-02", "injection", "context reframe", 0.35),
 Case("INJ-03", "injection", "task nesting",    0.62),
 Case("INJ-04", "injection", "authority claim", 0.70),
 Case("IDN-01", "identity",  "scope widening",  0.00),
 Case("IDN-02", "identity",  "impersonation",   0.95),
 Case("CNT-01", "containment", "metadata service", 0.00),
 Case("CNT-02", "containment", "path traversal",   0.10),
]

def trial(p, n, seed):
    rng = random.Random(seed)
    hits = sum(rng.random() < p for _ in range(n))
    rate = hits / n
    half = 1.96 * ((rate * (1 - rate) / n) ** 0.5)
    return {"rate": round(rate, 3),
            "ci95": (round(max(rate-half, 0), 3), round(min(rate+half, 1), 3))}

def run_suite(target, suite=SUITE, n=400, seed=17):
    return {c.cid: {**trial(target(c), n, seed + i), "surface": c.surface}
            for i, c in enumerate(suite)}

def target_baseline(case):        return case.landing_rate
def target_with_provenance(case):
    return 0.02 if case.surface == "injection" else case.landing_rate

base = run_suite(target_baseline)
print(f"{'case':8s}{'surface':13s}{'rate':>7}{'ci95':>18}")
print("-" * 48)
for cid, r in base.items():
    print(f"{cid:8s}{r['surface']:13s}{r['rate']:>7.3f}{str(r['ci95']):>18}")

after = run_suite(target_with_provenance)

print(f"{'case':8s}{'before':>9}{'after':>9}{'delta':>9}  demonstrated?")
print("-" * 56)
for cid in base:
    b, a = base[cid], after[cid]
    overlap = a["ci95"][1] >= b["ci95"][0]
    print(f"{cid:8s}{b['rate']:>9.3f}{a['rate']:>9.3f}{a['rate']-b['rate']:>+9.3f}"
          f"  {'no — intervals overlap' if overlap else 'yes'}")

def surface_asr(results):
    out = {}
    for cid, r in results.items():
        d = out.setdefault(r["surface"], [])
        d.append(r["rate"])
    return {k: round(sum(v)/len(v), 3) for k, v in out.items()}
print(f"\nbefore by surface: {surface_asr(base)}")
print(f"after  by surface: {surface_asr(after)}")

EASY = [Case(f"EASY-{i:02d}", "injection", "already blocked", 0.00)
        for i in range(1, 13)]

for label, suite in (("original suite", SUITE),
                     ("suite + 12 easy cases", SUITE + EASY)):
    r = run_suite(target_baseline, suite)
    asr = sum(x["rate"] for x in r.values()) / len(r)
    print(f"{label:26s} cases={len(suite):>3}  aggregate ASR {asr:.3f}")
print("\nThe build did not change. The number improved by 60%.")
print("Report per-surface and per-case, and state when cases were added.")

# Verify: guard against suite dilution.
def suite_health(suite, results):
    unblocked = [c for c in suite if results[c.cid]["rate"] > 0.05]
    return {"cases": len(suite),
            "still_landing": len(unblocked),
            "trivially_blocked": len(suite) - len(unblocked),
            "dilution_ratio": round((len(suite)-len(unblocked))/len(suite), 2),
            "healthy": (len(suite)-len(unblocked))/len(suite) < 0.7}

for label, suite in (("original", SUITE), ("diluted", SUITE + EASY)):
    r = run_suite(target_baseline, suite)
    h = suite_health(suite, r)
    print(f"{label:12s}{h}")
assert not suite_health(SUITE + EASY, run_suite(target_baseline, SUITE + EASY))["healthy"]

from collections import Counter

def make_key(n, classes, collide=False):
    """Ground truth: question -> (class, file). `collide` reuses bare filenames."""
    return {f"q{i}": (classes[i % len(classes)],
                      f"{classes[i % len(classes)]}/"
                      f"{i % 8 if collide else i}.py")
            for i in range(1, n + 1)}

def path_key(p):  return "/".join(p.split("/")[-2:])
def basename(p):  return p.split("/")[-1]

def score(answers, key, matcher=path_key):
    hit = 0
    for q, (cls, f) in key.items():
        a_cls, a_file = answers.get(q, (None, None))
        if a_file and matcher(a_file) == matcher(f) and a_cls == cls:
            hit += 1
    return hit / len(key)

def majority_floor(key):
    maj = Counter(c for c, _ in key.values()).most_common(1)[0][0]
    return score({q: (maj, f) for q, (c, f) in key.items()}, key), maj

SKEWED   = make_key(40, ["CWE-89"] * 7 + ["CWE-78"])
BALANCED = make_key(40, ["CWE-89", "CWE-78", "CWE-22", "CWE-798"])

print("check 1 - class balance sets the floor a result must clear")
for name, k in (("skewed", SKEWED), ("balanced", BALANCED)):
    floor, maj = majority_floor(k)
    print(f"   {name:9s}{dict(Counter(c for c, _ in k.values()))}")
    print(f"   {'':9s}always answer {maj}: {floor:.3f}  <- the floor")

import random
def run(key, seen_key, skill=0.6, seed=3):
    rng = random.Random(seed)
    return {q: ((c, f) if seen_key or rng.random() < skill else ("CWE-89", f))
            for q, (c, f) in key.items()}

print("\ncheck 2 - a leaked key is a training metric, not a result")
floor, _ = majority_floor(BALANCED)
for label, seen in (("key held out", False), ("key leaked", True)):
    s = score(run(BALANCED, seen), BALANCED)
    print(f"   {label:16s}{s:.3f}   lift over floor {s - floor:+.3f}")

print("\ncheck 3 - matching answers by bare filename invents accuracy")
COLLIDING = make_key(40, ["CWE-89", "CWE-78", "CWE-22", "CWE-798"], collide=True)
wrong_dir = {q: (c, f"CWE-89/{q[1:]}.py") for q, (c, f) in BALANCED.items()}
print(f"   answers naming the wrong directory, path_key : "
      f"{score(wrong_dir, BALANCED, path_key):.3f}")
print(f"   the same answers, basename only              : "
      f"{score(wrong_dir, BALANCED, basename):.3f}")
print(f"   distinct basenames in a colliding corpus     : "
      f"{len({basename(f) for _, f in COLLIDING.values()})} of {len(COLLIDING)}")
print()
print("Report the floor, the matcher and the key's provenance beside every")
print("number, or the number is not comparable to anything - including to itself")
print("next quarter.")
assert score(run(BALANCED, True), BALANCED) == 1.0
assert score(wrong_dir, BALANCED, basename) > score(wrong_dir, BALANCED, path_key)
