#!/usr/bin/env python3
"""Tier each telemetry source by the queries that actually need it, and price the result.

The procedure this runs is **not in this file**. It is in the `SKILL.md` beside
it, and the model is what carries it out: this script assembles the fixture,
hands the model the skill's own documentation and output contract, and checks
the reply against that same contract.

That is the point. A procedure written in one place and implemented in another
is two things that can disagree, and only one of them runs. Here they are the
same bytes.

The fixture below is committed input, carried over unchanged. Edit it and
re-run — every number in the output is derived from it.

    export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
    export OPENAI_API_KEY=ollama
    export MODEL=qwen2.5:1.5b-instruct
    python3 skills/detection/telemetry-tiering-cost/scripts/telemetry_tiering_cost.py

With no endpoint configured this exits 2 and says so. Nothing is substituted
for a model's answer.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "_runtime"))

from cyber_commons_skill_runtime import (  # noqa: E402
    announce_backend, jsonable, run_with_model)

SKILL = pathlib.Path(__file__).resolve().parents[1] / "SKILL.md"

# ---------------------------------------------------------------- the fixture
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
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"TIER_COST": TIER_COST, "TIER_LATENCY": TIER_LATENCY, "SOURCES": SOURCES, "QUERIES": QUERIES, "SPEED": SPEED, "TIER_FOR": TIER_FOR}


def main() -> int:
    announce_backend()

    print("the fixture this run is derived from")
    for name, value in FIXTURE.items():
        n = len(value) if isinstance(value, (list, dict, tuple, set)) else 1
        print(f"   {name:<28} {n} item(s)")
    print()

    instance, problems, kind, model = run_with_model(SKILL.read_text(), task())

    print(f"answered by   : {model}  ({kind})")
    print(f"violations    : {len(problems)}")
    for p in problems:
        print(f"   {p}")
    print()
    print(json.dumps(instance, indent=2, sort_keys=True, default=str))
    print()
    # The violations are printed, not raised, and they are also the exit code's
    # reason: what the model actually said is the evidence a reader needs, and
    # hiding it behind a traceback removes the only thing worth looking at.
    print(f"contract: {'held' if not problems else 'BROKEN in ' + str(len(problems)) + ' place(s)'}"
          f" — this is one model's answer, not the answer")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
