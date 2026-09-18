#!/usr/bin/env python3
"""Approve or refuse an autonomy request against the rung its blast radius and gating actually support.

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
    python3 skills/programme/autonomy-ladder-decisions/scripts/autonomy_ladder_decisions.py

With no endpoint configured this exits 2 and says so. Nothing is substituted
for a model's answer.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "_runtime"))

from cyber_commons_skill_runtime import (  # noqa: E402
    announce_backend, run_with_model)

SKILL = pathlib.Path(__file__).resolve().parents[1] / "SKILL.md"

# ---------------------------------------------------------------- the fixture
# ---------------------------------------------------------------- the fixture
SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}

LADDER = {
 "L1":  "Assist — model proposes, a human performs every action.",
 "L2":  "Act with approval — model calls tools, a human approves each call.",
 "L2.5":"Act within a blast radius — pre-approved tools, bounded scope, review after.",
 "L3":  "Autonomous — model acts and self-verifies; humans see aggregates.",
}

POLICY = {
 "L1":   ("self-service", "register it; no further review", 0),
 "L2":   ("lightweight",  "named owner + approval gate on every writer", 0),
 "L2.5": ("governed",     "risk tier + blast budget + drift monitoring + tested stop", 20),
 "L3":   ("board",        "all of L2.5 + held-out eval per release + board sign-off", 60),
}

REQUESTS = [
 ("doc-summariser", [("read_file","self",True)], set(), "L1"),
 ("triage-bot", [("read_file","self",True), ("post_comment","project",True),
                 ("close_ticket","project",True)], set(), "L2"),
 ("refund-agent", [("read_file","self",True),
                   ("issue_refund","tenant",False)], set(), "L2.5"),
 ("refund-agent (gated)", [("read_file","self",True),
                           ("issue_refund","tenant",False)], {"issue_refund"}, "L2.5"),
]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n{json.dumps(value, indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"SCOPE_WEIGHT": SCOPE_WEIGHT, "LADDER": LADDER, "POLICY": POLICY, "REQUESTS": REQUESTS}


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
