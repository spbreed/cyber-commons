#!/usr/bin/env python3
"""Compare a build order that produces coverage against one that produces demos, quarter by quarter.

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
    python3 skills/programme/capability-build-order/scripts/capability_build_order.py

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
DAY = 86400

REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]

DEMOABLE = {"AC-1": False, "AC-2": False, "SB-1": False, "SB-2": False,
            "EV-1": False, "EV-2": True, "DR-1": True, "ST-1": True}

INVERTED = {
 "Q1 · evaluation + dashboard": ["EV-2","DR-1"],
 "Q2 · more evaluation":        ["EV-2","DR-1"],
 "Q3 · identity (finally)":     ["EV-2","DR-1","AC-1","AC-2"],
 "Q4 · containment":            ["EV-2","DR-1","AC-1","AC-2","SB-1","SB-2"],
}

CAPABILITY_AT = {
 "can revoke one agent":            {"AC-1"},
 "can attribute an action":         {"AC-1","EV-1"},
 "can bound a compromised agent":   {"SB-1","SB-2"},
 "can halt the fleet":              {"ST-1"},
 "can defend an accuracy number":   {"EV-2"},
}

ROLES = {
 "harness engineer":   ("C2", {"EV-2"},                 "loop, verifier, eval"),
 "identity engineer":  ("B2", {"AC-1","AC-2","EV-1"},   "identity, delegation, act chains"),
 "detection engineer": ("E1", {"DR-1"},                 "agent telemetry and drift"),
 "GRC practitioner":   ("F1", {"SB-2","ST-1"},          "tiering, evidence, verification"),
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"DAY": DAY, "REQUIRED": REQUIRED, "DEMOABLE": DEMOABLE, "INVERTED": INVERTED, "CAPABILITY_AT": CAPABILITY_AT, "ROLES": ROLES}


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
