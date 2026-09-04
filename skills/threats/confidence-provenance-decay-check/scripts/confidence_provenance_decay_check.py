#!/usr/bin/env python3
"""Track how a hedged claim's confidence and provenance move in opposite directions across summarisation hops.

This is the executable half of the `confidence-provenance-decay-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

def summarise(claim, confidence):
    """Each hop compresses. Compression removes qualifiers first - they are the
    least information-dense part of a sentence."""
    for hedge in ("I could not find", "probably", "appears to", "it seems"):
        if hedge in claim:
            claim = " ".join(claim.replace(hedge, "").split())
            confidence = min(1.0, confidence + 0.3)     # certainty is what survives
    return claim.strip(", "), round(confidence, 2)

ORIGINAL = "I could not find a CVE for libfoo, it is probably fine"
claim, conf = ORIGINAL, 0.2
provenance = ["model guess, unverified"]

print(f"{'hop':>4}  {'confidence':>11}  claim")
print(f"{0:>4}  {conf:>11.2f}  {claim}")
for hop in (1, 2, 3):
    claim, conf = summarise(claim, conf)
    if hop >= 2:
        provenance = []                       # the source field is not carried on
    print(f"{hop:>4}  {conf:>11.2f}  {claim}")

print(f"\nprovenance recorded at hop 3: {provenance or 'none'}")
print(f"confidence at hop 0: 0.20   at hop 3: {conf}")
print()
print("Nothing lied. Every hop did its job. The claim gained certainty at the")
print("exact rate it lost evidence, and by hop three it reads like a finding")
print("someone verified.")
print()
print("An attacker who lands one plausible claim early gets it laundered into")
print("an established fact by your own pipeline - for free.")
assert conf >= 0.8 and not provenance
