#!/usr/bin/env python3
"""Run a technique enough times to know whether it reproduces, and compute the sample size the comparison actually needed.

This is the executable half of the `technique-reproducibility-test` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import random

def trial(effect, n=200, seed=7):
    """Run a stochastic effect n times; report the rate with a 95% interval."""
    rng = random.Random(seed)
    hits = sum(effect(rng) for _ in range(n))
    rate = hits / n
    half = 1.96 * ((rate * (1 - rate) / n) ** 0.5) if n else 0.0
    lo, hi = round(max(rate - half, 0), 3), round(min(rate + half, 1), 3)
    verdict = ("reproducible" if lo > 0.5 else
               "flaky" if hi > 0.05 else "not reproduced")
    return {"n": n, "hits": hits, "rate": round(rate, 3), "ci95": (lo, hi),
            "verdict": verdict}

# ground-truth landing probabilities for three injection techniques
TECHNIQUES = {"direct override": 0.05, "context reframe": 0.35, "task nesting": 0.62}

print(f"{'technique':20s}{'rate':>7}{'ci95':>18}  verdict")
print("-" * 60)
for name, p in TECHNIQUES.items():
    r = trial(lambda rng, p=p: rng.random() < p, n=200)
    print(f"{name:20s}{r['rate']:>7.3f}{str(r['ci95']):>18}  {r['verdict']}")
print("\n'It worked' is true for all three. Only one is reproducible.")

def compare(before_p, after_p, n, seed=11):
    b = trial(lambda rng: rng.random() < before_p, n=n, seed=seed)
    a = trial(lambda rng: rng.random() < after_p,  n=n, seed=seed + 1)
    overlap = a["ci95"][1] >= b["ci95"][0]
    return b, a, overlap

print(f"{'n':>6}{'before':>18}{'after':>18}  conclusion")
print("-" * 68)
for n in (20, 100, 1000):
    b, a, overlap = compare(0.62, 0.48, n)
    concl = "NOT demonstrated" if overlap else "improvement holds"
    print(f"{n:>6}{str(b['ci95']):>18}{str(a['ci95']):>18}  {concl}")
print("\nThe true effect is identical in all three rows. Only sample size changed.")
print("At n=20 you would report a 23% reduction you cannot support.")

def required_n(p_before, p_after, power_z=1.96):
    """Rough two-proportion sample size for a 95% interval that separates."""
    p = (p_before + p_after) / 2
    diff = abs(p_before - p_after)
    if diff == 0: return float("inf")
    return int((2 * power_z ** 2 * p * (1 - p)) / (diff ** 2)) + 1

print(f"{'effect you want to detect':34s}{'n required':>11}")
print("-" * 47)
for before, after in ((0.62, 0.10), (0.62, 0.31), (0.62, 0.48), (0.62, 0.58)):
    print(f"{f'{before:.0%} → {after:.0%}':34s}{required_n(before, after):>11}")
print("\nDetecting a halving is cheap. Detecting a 14-point move is not, and")
print("detecting a 4-point move is a research project in itself.")

n_needed = required_n(0.62, 0.48)
b, a, overlap = compare(0.62, 0.48, n_needed)
print(f"\nre-run at the computed n={n_needed}: "
      f"before {b['ci95']}, after {a['ci95']}, overlap={overlap}")

# Verify: the honest reporting template.
def report(technique, before, after, n):
    b, a, overlap = compare(before, after, n)
    return (f"{technique}\n"
            f"   before  {b['rate']:.2f} (95% CI {b['ci95']}, n={n})\n"
            f"   after   {a['rate']:.2f} (95% CI {a['ci95']}, n={n})\n"
            f"   verdict {'no demonstrated change — intervals overlap' if overlap else 'reduction demonstrated'}")

print(report("task nesting, after provenance mitigation", 0.62, 0.48, 20))
print()
print(report("task nesting, after provenance mitigation", 0.62, 0.48, 1000))
