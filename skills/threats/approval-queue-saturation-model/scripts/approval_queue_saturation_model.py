#!/usr/bin/env python3
"""Model what approval coverage and actual review both do as the queue grows.

This is the executable half of the `approval-queue-saturation-model` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

def review(queue, careful_capacity=25):
    """A reviewer considers the first `careful_capacity` properly. The rest are
    approved to keep the queue moving - which is what actually happens."""
    considered = queue[:careful_capacity]
    rubber_stamped = queue[careful_capacity:]
    caught = [r for r in considered if r["malicious"]]
    missed = [r for r in rubber_stamped if r["malicious"]]
    return {"considered": len(considered), "rubber_stamped": len(rubber_stamped),
            "caught": len(caught), "missed": len(missed)}

def build_queue(volume, malicious_at):
    return [{"id": i, "malicious": i == malicious_at} for i in range(volume)]

print(f"{'daily volume':>13}{'considered':>12}{'stamped':>9}{'caught':>8}{'missed':>8}")
for volume in (10, 25, 100, 500):
    q = build_queue(volume, malicious_at=volume - 1)     # attacker picks the position
    r = review(q)
    print(f"{volume:>13}{r['considered']:>12}{r['rubber_stamped']:>9}"
          f"{r['caught']:>8}{r['missed']:>8}")

print()
print("At every volume the audit trail shows a human approval on 100% of")
print("actions. The control reports full coverage in all four rows.")
print()
print("The attacker does not need to defeat the reviewer. They need to arrive")
print("at position 173 of 200, and generating positions 1 to 172 is free.")
r = review(build_queue(500, malicious_at=499))
assert r["missed"] == 1 and r["caught"] == 0
