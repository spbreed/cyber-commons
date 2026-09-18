#!/usr/bin/env python3
"""Compute the metrics that degrade under neglect and separate them from the comfortable ones that do not.

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
    python3 skills/programme/programme-metrics-selection/scripts/programme_metrics_selection.py

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
# ---------------------------------------------------------------- the fixture
# ---------------------------------------------------------------- the fixture
SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}

DAY = 86400

FLEET = {"pr-remediation": [("read_file","self",True),("write_file","project",True),
                            ("deploy","org",False)],
         "claims-triage":  [("read_file","self",True),("issue_refund","tenant",False)],
         "doc-summariser": [("read_file","self",True)]}

GATED = {"pr-remediation": set(), "claims-triage": {"issue_refund"},
         "doc-summariser": set()}

ATTACKS = [("metadata",False),("traversal",False),("unlisted egress",True),("denied tool",False)]

WINDOW = {"AC-1":30,"AC-2":30,"SB-1":30,"EV-1":60,"EV-2":30}

REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]

TIME_TO_STOP = 12

COMFORTABLE = {
 "findings closed this quarter": "goes up with activity; says nothing about posture",
 "training completion %":        "reaches 98% and stays there forever",
 "number of AI policies":        "monotonically increasing by construction",
 "tools evaluated":              "measures procurement, not risk",
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"SCOPE_WEIGHT": SCOPE_WEIGHT, "DAY": DAY, "FLEET": FLEET, "GATED": GATED, "ATTACKS": ATTACKS, "WINDOW": WINDOW, "REQUIRED": REQUIRED, "TIME_TO_STOP": TIME_TO_STOP, "COMFORTABLE": COMFORTABLE}


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
