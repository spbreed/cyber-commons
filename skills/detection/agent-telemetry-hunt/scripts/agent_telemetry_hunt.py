#!/usr/bin/env python3
"""Run three hunt hypotheses over a labelled corpus of agent runs and score each on precision and recall.

This is the executable half of the `agent-telemetry-hunt` skill. The corpus is
synthetic and labelled, which is the point: a hunt can only be scored against
runs whose status is known independently of the hunt that found them.

One hypothesis in here is deliberately bad. It has perfect intuition and no
precision, because the behaviour it describes is most of this estate's normal
work — which is the single most common way a hunt wastes a quarter.

Standard library only, and deterministic.
"""

# fields: agent, hour (24h), tools used, actions in the run, bad (ground truth)
RUNS = []
for i in range(22):                      # daytime interactive work
    RUNS.append({"agent": "workflow" if i % 2 else "advisor",
                 "hour": 9 + (i % 8), "tools": ["booking.read"],
                 "actions": 20 + (i % 30), "bad": False})
for i in range(12):                      # the overnight batch — ordinary, and nightly
    RUNS.append({"agent": "workflow", "hour": (1 + i) % 6,
                 "tools": ["booking.read"], "actions": 40 + i, "bad": False})
RUNS += [
    {"agent": "workflow", "hour": 11, "tools": ["booking.read", "payments.refund"],
     "actions": 44,   "bad": True},     # a tool outside its declared scope
    {"agent": "workflow", "hour": 14, "tools": ["payments.refund"],
     "actions": 51,   "bad": True},
    {"agent": "advisor",  "hour": 16, "tools": ["files.write"],
     "actions": 12,   "bad": True},
    {"agent": "advisor",  "hour": 3,  "tools": ["booking.read"],
     "actions": 31,   "bad": True},     # 3am, but so is the batch
    {"agent": "workflow", "hour": 2,  "tools": ["booking.read"],
     "actions": 900,  "bad": True},     # volume far above any task ceiling
    {"agent": "workflow", "hour": 10, "tools": ["booking.read"],
     "actions": 1200, "bad": True},
]

# Step 2 — the population, stated before anything runs.
SCOPE = {"workflow": {"booking.read", "booking.write"},
         "advisor":  {"booking.read", "knowledge.search"}}
CEILING = 300            # no task in this estate needs more actions than this
HOURS = range(7, 20)

# Step 1 — each hypothesis is a sentence with a subject, as a predicate.
HYPOTHESES = [
    ("tool outside declared scope",
     lambda r: bool(set(r["tools"]) - SCOPE[r["agent"]])),
    ("run outside working hours",
     lambda r: r["hour"] not in HOURS),
    ("volume above task ceiling",
     lambda r: r["actions"] > CEILING),
]

total = len(RUNS)
anomalous = sum(1 for r in RUNS if r["bad"])
print(f"corpus: {total} agent runs, {anomalous} of them labelled anomalous")
print()

report = {"corpus": {"runs": total, "anomalous": anomalous}, "hypotheses": []}
print(f"{'hypothesis':<32}{'matched':>8}{'tp':>4}{'fp':>4}{'precision':>11}{'recall':>8}")
for name, pred in HYPOTHESES:
    hits = [r for r in RUNS if pred(r)]
    tp = sum(1 for r in hits if r["bad"])
    fp = len(hits) - tp
    precision = tp / len(hits) if hits else 0.0
    recall = tp / anomalous
    # Step 4 — the outcome is decided here rather than left to the reader.
    outcome = "promote" if precision >= 0.7 and tp else "tune" if tp else "discard"
    print(f"{name:<32}{len(hits):>8}{tp:>4}{fp:>4}{precision:>11.2f}{recall:>8.2f}")
    report["hypotheses"].append(
        {"name": name, "matched": len(hits), "true_positives": tp,
         "false_positives": fp, "precision": round(precision, 2),
         "recall": round(recall, 2), "outcome": outcome})
print()
for h in report["hypotheses"]:
    print(f"   {h['name']:<32}-> {h['outcome']}")
print()

hours = next(h for h in report["hypotheses"] if h["name"] == "run outside working hours")
batch = sum(1 for r in RUNS if r["hour"] not in HOURS and not r["bad"])
print(f"The working-hours hypothesis is the one to stop on. It matched "
      f"{hours['matched']} runs")
print(f"to find {hours['true_positives']}, because {batch} of the matches are the "
      f"overnight batch doing")
print(f"exactly its job. Precision {hours['precision']:.2f}. That is a tune, not a "
      f"finding, and")
print(f"shipping it would add {hours['false_positives']} alerts a night to a queue "
      f"for {hours['true_positives']} real events.")
print()
print("Note what recall is NOT saying here. No hypothesis reaches 1.00 and none")
print("should: a hunt is one hypothesis about one behaviour, and these six")
print("anomalies are not one behaviour. Recall against every anomaly in the corpus")
print("is the wrong denominator - recall against the behaviour the hypothesis")
print("describes is the right one, and that is why each hypothesis is scored alone.")

assert total == 40 and anomalous == 6
assert any(h["outcome"] == "promote" for h in report["hypotheses"])
assert hours["outcome"] == "tune" and hours["false_positives"] > 0, \
    "the noisy hypothesis must actually be noisy, or the lesson is not taught"
