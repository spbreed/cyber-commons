#!/usr/bin/env python3
"""Enumerate what local weights grant that a hosted API does not, and turn a rate limit into an attempt budget.

This is the executable half of the `weight-access-capability-delta` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

def attempts_available(rate_limit_per_min, hours, parallel=1):
    if rate_limit_per_min is None:                     # local: bounded by hardware
        return hours * 3600 * 8 * parallel             # ~8 inferences/sec/GPU
    return rate_limit_per_min * 60 * hours * parallel

print(f"{'setting':34s}{'attempts in 24h':>18}")
print("-" * 54)
for label, rl, par in (("hosted API, 20 req/min", 20, 1),
                       ("hosted API, 20 req/min, 5 keys", 20, 5),
                       ("local open weights, 1 GPU", None, 1),
                       ("local open weights, 8 GPUs", None, 8)):
    print(f"{label:34s}{attempts_available(rl, 24, par):>18,}")

hosted = attempts_available(20, 24, 1)
local  = attempts_available(None, 24, 8)
print(f"\nratio: {local/hosted:,.0f}× more attempts, with no abuse signal reaching anyone.")
print("A 0.5%-success technique becomes reliable when you can try it 5 million times.")

def expected_successes(rate, attempts):
    return rate * attempts
for rate in (0.005, 0.05):
    print(f"   technique landing {rate:.1%} of the time → "
          f"{expected_successes(rate, hosted):,.0f} successes hosted, "
          f"{expected_successes(rate, local):,.0f} local")

REPLACEMENTS = {
 "rate limiting":            ("A2.7 choke point / A3.6 runtime levers",
                              "bound attempts per identity per window"),
 "abuse monitoring":         ("D1.4 detection for agents",
                              "your telemetry is the only signal now"),
 "refusal behaviour":        ("A3.5 tool policy + C1.2 provenance",
                              "do not rely on the model refusing; refuse at the tool"),
 "immutable logging":        ("A2.5 act chains + D2.5 replay",
                              "you own retention and integrity"),
 "model version stability":  ("D1.7 drift monitoring",
                              "you now own upgrades AND their behavioural changes"),
}
print(f"{'provider control lost':26s}{'your replacement':44s}")
print("-" * 96)
for lost, (where, what) in REPLACEMENTS.items():
    print(f"{lost:26s}{where:44s}{what}")

def readiness(has):
    missing = [k for k in REPLACEMENTS if k not in has]
    return round(len(has) / len(REPLACEMENTS), 2), missing

for label, has in (("typical first local deployment", {"rate limiting"}),
                   ("after this curriculum", set(REPLACEMENTS))):
    score, missing = readiness(has)
    print(f"\n{label}: {score:.0%} covered")
    for m in missing: print(f"   ✗ {m}")

# Verify: an agent on local weights, with and without the replacements.
SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s] * (1 if rev else 2)
               for n, s, rev in tools if n not in gated)

TOOLS = [("read_file", "self", True), ("write_file", "project", True),
         ("run_shell", "tenant", False)]
print("local open-weight agent, no replacements:", blast(TOOLS))
print("with tool policy + gating (A3.5):        ",
      blast(TOOLS, gated={"run_shell"}))
print("\nThe model has no refusal training you can rely on. The tool policy")
print("does not care what the model was persuaded to want.")
assert blast(TOOLS, gated={"run_shell"}) < blast(TOOLS)
