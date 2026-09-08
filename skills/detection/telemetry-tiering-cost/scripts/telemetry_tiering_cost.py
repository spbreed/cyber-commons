#!/usr/bin/env python3
"""Tier each telemetry source by the queries that actually need it, and price the result.

This is the executable half of the `telemetry-tiering-cost` skill: the check the
SKILL.md next to it describes, run against the CyberTravels estate so two runs
can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle kernel with the
internet switched off.
"""

# Indicative monthly cost per GB, per storage tier. The absolute numbers vary by
# platform; the RATIOS between them are what the decision turns on, and those are
# stable across OpenSearch, S3+Athena and every managed SIEM.
TIER_COST = {"hot": 2.20, "warm": 0.55, "cold": 0.023, "drop": 0.0}
# How fast each tier answers. A cold tier is not "slow storage" — it is storage
# you cannot run an interactive hunt against.
TIER_LATENCY = {"hot": "seconds", "warm": "minutes", "cold": "hours", "drop": "never"}

SOURCES = [
    # name,                       GB/month, retention days, needed_within
    ("agent traces: prompts",         410,  30,  "hours"),
    ("agent traces: tool calls",       88, 400,  "seconds"),
    ("agent traces: decisions",        31, 400,  "seconds"),
    ("model gateway access log",       64, 400,  "seconds"),
    ("host EDR (Wazuh)",              950,  90,  "minutes"),
    ("cloud audit (CloudTrail-like)", 220, 400,  "seconds"),
]

# The queries the SOC actually runs. Each names the sources it reads and how
# fast it has to come back. This is the input the tiering decision is derived
# from — not a retention policy somebody wrote once.
QUERIES = [
    ("triage: what did this agent do in the last hour",
     ["agent traces: tool calls", "agent traces: decisions",
      "model gateway access log"], "seconds"),
    ("scope: everything this identity touched, 90 days",
     ["cloud audit (CloudTrail-like)", "agent traces: tool calls"], "seconds"),
    ("hunt: unexplained tool use across a fortnight",
     ["agent traces: tool calls", "agent traces: decisions"], "minutes"),
    ("forensics: reproduce one run, any time in a year",
     ["agent traces: prompts", "agent traces: tool calls"], "hours"),
    ("host: process lineage for one alert",
     ["host EDR (Wazuh)"], "minutes"),
]

SPEED = {"seconds": 3, "minutes": 2, "hours": 1, "never": 0}
TIER_FOR = {3: "hot", 2: "warm", 1: "cold", 0: "drop"}


def main() -> int:
    # A source is tiered by the FASTEST query that reads it. Nothing else about
    # it matters — not its volume, not how interesting it feels.
    need = {name: 0 for name, *_ in SOURCES}
    driver = {}
    for q, reads, speed in QUERIES:
        for src in reads:
            if SPEED[speed] > need[src]:
                need[src], driver[src] = SPEED[speed], q

    print("what the SOC actually asks, and how fast it needs an answer\n")
    for q, reads, speed in QUERIES:
        print(f"  [{speed:>7}]  {q}")
        for r in reads:
            print(f"              reads  {r}")

    print("\ntiering, derived from the fastest query that reads each source\n")
    print(f"  {'source':<32} {'GB/mo':>6} {'days':>5}  {'tier':<5} "
          f"{'answers in':<10} driven by")
    index_all = tiered = 0.0
    for name, gb, days, _ in SOURCES:
        tier = TIER_FOR[need[name]]
        months = days / 30
        index_all += gb * months * TIER_COST["hot"]
        tiered += gb * months * TIER_COST[tier]
        why = driver.get(name, "nothing reads it")
        print(f"  {name:<32} {gb:>6} {days:>5}  {tier:<5} "
              f"{TIER_LATENCY[tier]:<10} {why.split(':')[0]}")

    print(f"\n  index everything hot   ${index_all:>10,.0f} / month")
    print(f"  tiered by query        ${tiered:>10,.0f} / month")
    print(f"  difference             ${index_all - tiered:>10,.0f} / month  "
          f"({1 - tiered / index_all:.0%})")

    hot = [n for n, *_ in SOURCES if need[n] == 3]
    orphan = [n for n, *_ in SOURCES if need[n] == 0]
    print(f"\n  hot ({len(hot)}): {', '.join(hot)}")
    print(f"  read by no query: {', '.join(orphan) or 'none'}")

    # The point of the exercise, and the reason it is not a cost lesson.
    prompts, p_gb, _, _ = next(r for r in SOURCES if r[0].endswith("prompts"))
    share = p_gb / sum(gb for _, gb, *_ in SOURCES)
    readers = sum(1 for _, reads, _ in QUERIES if prompts in reads)
    ratio = TIER_COST["cold"] / TIER_COST["hot"]
    print(f"\n'{prompts}' is {share:.0%} of the volume and is read by "
          f"{readers} query,")
    print("which can wait hours. Priced hot it is the line that gets cut when the")
    print("bill arrives, and cutting it removes the only source D5.1 can replay a")
    print(f"run from. Tiered cold it survives at {ratio:.0%} of the hot cost.")

    assert tiered < index_all, "tiering that costs more has been done backwards"
    assert not orphan, "a source no query reads should have been dropped, not tiered"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
