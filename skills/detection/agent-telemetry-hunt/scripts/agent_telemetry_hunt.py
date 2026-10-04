#!/usr/bin/env python3
"""Run three hunt hypotheses over a labelled corpus of agent runs and score each on precision and recall.

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
    export MODEL=<the model name your endpoint serves>
    python3 skills/detection/agent-telemetry-hunt/scripts/agent_telemetry_hunt.py

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
# fields: agent, hour (24h), tools used, actions in the run, bad (ground truth)
#
# Twenty runs, four of them anomalous, and the ground truth is in the row so
# precision and recall are computable rather than asserted. This list was empty
# for one release: the hunt then ran over nothing and every hypothesis scored
# 0/0, which the contract accepts.
#
# The hunt is meant to be hard. Runs 5 and 12 are out-of-scope tool use, which a
# scope rule catches. Run 17 is over the action ceiling. Run 9 is the one that
# matters: in scope, under the ceiling, at 03:00 — so only an off-hours
# hypothesis finds it, and that hypothesis also flags runs 6 and 14, which are
# benign. That trade is the lesson.
RUNS = [
 {"agent": "workflow", "hour": 9,  "tools": {"booking.read", "booking.write"},   "actions": 12,  "bad": False},
 {"agent": "workflow", "hour": 10, "tools": {"booking.read"},                    "actions": 4,   "bad": False},
 {"agent": "advisor",  "hour": 10, "tools": {"knowledge.search"},                "actions": 7,   "bad": False},
 {"agent": "workflow", "hour": 11, "tools": {"booking.read", "booking.write"},   "actions": 31,  "bad": False},
 {"agent": "advisor",  "hour": 11, "tools": {"knowledge.search", "booking.write"}, "actions": 9, "bad": True},
 {"agent": "workflow", "hour": 2,  "tools": {"booking.read"},                    "actions": 3,   "bad": False},
 {"agent": "advisor",  "hour": 13, "tools": {"booking.read", "knowledge.search"}, "actions": 15, "bad": False},
 {"agent": "workflow", "hour": 14, "tools": {"booking.read", "booking.write"},   "actions": 22,  "bad": False},
 {"agent": "workflow", "hour": 3,  "tools": {"booking.read", "booking.write"},   "actions": 18,  "bad": True},
 {"agent": "advisor",  "hour": 15, "tools": {"knowledge.search"},                "actions": 5,   "bad": False},
 {"agent": "workflow", "hour": 15, "tools": {"booking.read"},                    "actions": 8,   "bad": False},
 {"agent": "workflow", "hour": 16, "tools": {"booking.read", "payments.refund"}, "actions": 11,  "bad": True},
 {"agent": "advisor",  "hour": 16, "tools": {"knowledge.search", "booking.read"}, "actions": 19, "bad": False},
 {"agent": "advisor",  "hour": 4,  "tools": {"knowledge.search"},                "actions": 6,   "bad": False},
 {"agent": "workflow", "hour": 17, "tools": {"booking.read", "booking.write"},   "actions": 27,  "bad": False},
 {"agent": "advisor",  "hour": 17, "tools": {"knowledge.search"},                "actions": 12,  "bad": False},
 {"agent": "workflow", "hour": 18, "tools": {"booking.read", "booking.write"},   "actions": 418, "bad": True},
 {"agent": "workflow", "hour": 18, "tools": {"booking.read"},                    "actions": 9,   "bad": False},
 {"agent": "advisor",  "hour": 19, "tools": {"knowledge.search", "booking.read"}, "actions": 14, "bad": False},
 {"agent": "workflow", "hour": 20, "tools": {"booking.read", "booking.write"},   "actions": 16,  "bad": False},
]

# Off-hours, for the hypothesis that finds run 9. Stated here rather than left to
# the model, so the hypothesis is testable against the same boundary every run.
OFF_HOURS = range(0, 6)

# Step 2 — the population, stated before anything runs.
SCOPE = {"workflow": {"booking.read", "booking.write"},
         "advisor":  {"booking.read", "knowledge.search"}}

CEILING = 300            # no task in this estate needs more actions than this
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"RUNS": RUNS, "SCOPE": SCOPE, "CEILING": CEILING,
           "OFF_HOURS": list(OFF_HOURS)}


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
