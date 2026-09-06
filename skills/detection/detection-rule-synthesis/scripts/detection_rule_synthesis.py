#!/usr/bin/env python3
"""Generate a detection rule from one incident trace, then score it against benign traffic before it ships.

This is the executable half of `detection-rule-synthesis`. Generating the rule
is the easy half and the half everyone demos. The half that decides whether it
can be deployed is the benign corpus: a rule with no measured false-positive
rate is a guess with syntax.

Standard library only, and deterministic.
"""

# The incident, reconstructed. One agent, one sequence, one outcome.
INCIDENT = [
    {"agent": "workflow", "tool": "booking.read",    "arg": "BK-771"},
    {"agent": "workflow", "tool": "booking.read",    "arg": "BK-772"},
    {"agent": "workflow", "tool": "payments.refund", "arg": "BK-772"},
]

# Benign traffic. Real refunds happen; that is the whole difficulty.
BENIGN = []
for i in range(60):
    BENIGN.append([{"agent": "workflow", "tool": "booking.read", "arg": f"BK-{i:03d}"}])
for i in range(18):                        # legitimate refunds, with an approval
    BENIGN.append([
        {"agent": "workflow", "tool": "booking.read",     "arg": f"BK-9{i:02d}"},
        {"agent": "workflow", "tool": "approval.request", "arg": f"BK-9{i:02d}"},
        {"agent": "workflow", "tool": "payments.refund",  "arg": f"BK-9{i:02d}"},
    ])
for i in range(6):                         # advisor doing advisor things
    BENIGN.append([{"agent": "advisor", "tool": "knowledge.search", "arg": "policy"}])

CANDIDATES = {
    # Step 2 — the naive generalisation: the tool that appeared in the incident.
    "any refund":
        lambda run: any(e["tool"] == "payments.refund" for e in run),
    # Step 3 — the sequence, which is what actually distinguished it.
    "refund with no approval in the run":
        lambda run: (any(e["tool"] == "payments.refund" for e in run)
                     and not any(e["tool"] == "approval.request" for e in run)),
    # Over-fitted to this incident: matches it and nothing else, ever.
    "refund on BK-772":
        lambda run: any(e["tool"] == "payments.refund" and e["arg"] == "BK-772"
                        for e in run),
}

print(f"incident: {len(INCIDENT)} steps · benign corpus: {len(BENIGN)} runs")
print()
report = {"benign_runs": len(BENIGN), "candidates": []}
print(f"{'candidate rule':<38}{'fires on':>10}{'FP':>5}{'FP rate':>9}  verdict")
for name, rule in CANDIDATES.items():
    catches = rule(INCIDENT)
    fp = sum(1 for run in BENIGN if rule(run))
    rate = fp / len(BENIGN)
    if not catches:
        verdict = "REJECT — misses the incident"
    elif rate > 0.05:
        verdict = "REJECT — buries the queue"
    elif name.endswith("BK-772"):
        verdict = "REJECT — matches this incident only"
    else:
        verdict = "ship"
    print(f"{name:<38}{str(catches):>10}{fp:>5}{rate:>8.0%}  {verdict}")
    report["candidates"].append({"rule": name, "catches_incident": catches,
                                 "false_positives": fp, "fp_rate": round(rate, 3),
                                 "verdict": verdict.split(" —")[0]})
print()
print("All three rules catch the incident. That is the trap: catching the thing")
print("that already happened is the one property every candidate has, so it")
print("cannot be the property you select on.")
print()
naive = next(c for c in report["candidates"] if c["rule"] == "any refund")
print(f"'any refund' fires on {naive['false_positives']} legitimate refunds - a "
      f"{naive['fp_rate']:.0%} false-positive")
print("rate, and refunds are the business. 'refund on BK-772' is perfect on this")
print("corpus and worthless tomorrow, because the booking id will be different.")
print("Only the sequence rule generalises AND stays quiet.")

ship = [c for c in report["candidates"] if c["verdict"] == "ship"]
assert len(ship) == 1 and ship[0]["rule"].startswith("refund with no approval")
assert all(c["catches_incident"] for c in report["candidates"]), \
    "every candidate must catch the incident, or the selection lesson is lost"
