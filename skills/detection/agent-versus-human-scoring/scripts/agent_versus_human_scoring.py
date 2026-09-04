#!/usr/bin/env python3
"""Score actors on behavioural signals, sweep the threshold, and choose it by expected cost rather than by accuracy.

This is the executable half of the `agent-versus-human-scoring` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import statistics, time
from dataclasses import dataclass

@dataclass
class Event:
    ts: float; actor: str; action: str = "read"

def agent_score(events, actor):
    ev = sorted((e for e in events if e.actor == actor), key=lambda e: e.ts)
    if len(ev) < 3:
        return {"actor": actor, "score": 0.0, "verdict": "insufficient data"}
    gaps = [b.ts - a.ts for a, b in zip(ev, ev[1:])]
    mean = statistics.fmean(gaps)
    cv = (statistics.pstdev(gaps) / mean) if mean else 0.0
    regularity  = max(0.0, 1.0 - min(cv, 1.0))
    rate        = len(ev) / max(ev[-1].ts - ev[0].ts, 1e-9)
    rate_signal = min(rate / 5.0, 1.0)
    span_hours  = (ev[-1].ts - ev[0].ts) / 3600
    continuity  = min(span_hours / 8.0, 1.0)
    score = round(0.5*regularity + 0.3*rate_signal + 0.2*continuity, 3)
    return {"actor": actor, "score": score, "cv": round(cv, 2),
            "rate_per_s": round(rate, 2), "span_h": round(span_hours, 2)}

now = time.time()
POP = {
 "svc-indexer":        ([Event(now + i*0.05, "svc-indexer") for i in range(500)], "agent"),
 "dana@corp":          ([Event(now + t, "dana@corp") for t in
                         (0, 5, 13, 14, 60, 140, 320, 900, 1800, 4000)], "human"),
 "unknown-token-7f3c": ([Event(now + i*1.0, "unknown-token-7f3c") for i in range(400)], "agent"),
 "sam@corp-ide":       ([Event(now + i*2.0, "sam@corp-ide") for i in range(180)], "human"),
 "polite-agent":       ([Event(now + t, "polite-agent") for t in
                         (0, 7, 19, 44, 90, 210, 480, 900, 1700, 3000)], "agent"),
}
print(f"{'actor':22s}{'score':>7}{'cv':>7}{'rate/s':>9}{'span_h':>9}  truth")
print("-" * 62)
for actor, (ev, truth) in POP.items():
    r = agent_score(ev, actor)
    print(f"{actor:22s}{r['score']:>7.3f}{r.get('cv',0):>7}{r.get('rate_per_s',0):>9}"
          f"{r.get('span_h',0):>9}  {truth}")

def evaluate(threshold):
    fp = fn = 0
    for actor, (ev, truth) in POP.items():
        s = agent_score(ev, actor)["score"]
        pred = "agent" if s >= threshold else "human"
        if pred == "agent" and truth == "human": fp += 1
        if pred == "human" and truth == "agent": fn += 1
    return fp, fn

print(f"{'threshold':>10}{'humans flagged':>16}{'agents MISSED':>16}")
print("-" * 44)
for t in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
    fp, fn = evaluate(t)
    flag = "   ← invisible agents" if fn else ""
    print(f"{t:>10.1f}{fp:>16}{fn:>16}{flag}")

print("\nThe two errors cost differently:")
print("   human flagged as agent  → one investigation, ~30 min, self-correcting")
print("   agent flagged as human  → it stays out of your NHI inventory entirely")

COST_FP = 0.5      # analyst-hours per false investigation
COST_FN = 40.0     # expected hours if an unmanaged agent is missed

def expected_cost(threshold):
    fp, fn = evaluate(threshold)
    return fp * COST_FP + fn * COST_FN, fp, fn

print(f"{'threshold':>10}{'FP':>5}{'FN':>5}{'expected cost (hrs)':>22}")
print("-" * 44)
best = None
for t in [x/20 for x in range(4, 19)]:
    c, fp, fn = expected_cost(t)
    if best is None or c < best[1]: best = (t, c)
    if abs(t*20 - round(t*20)) < 1e-9 and (t*10) % 1 == 0:
        print(f"{t:>10.2f}{fp:>5}{fn:>5}{c:>22.1f}")
print(f"\ncost-minimising threshold: {best[0]:.2f} (expected {best[1]:.1f} hrs)")
print("Accuracy-maximising would sit higher and let the polite agent through.")

fp, fn = evaluate(best[0])
print(f"at that threshold: {fp} humans investigated, {fn} agents missed")

# Verify: join against the registry — the score alone is not the finding.
REGISTERED = {"svc-indexer", "dana@corp", "sam@corp-ide"}
threshold = best[0]
findings = []
for actor, (ev, truth) in POP.items():
    s = agent_score(ev, actor)["score"]
    if s >= threshold and actor not in REGISTERED:
        findings.append((actor, s))
print("shadow agents (behaves like software, not in the inventory):")
for a, s in findings:
    print(f"   {a:22s} score={s:.3f}")
assert findings
