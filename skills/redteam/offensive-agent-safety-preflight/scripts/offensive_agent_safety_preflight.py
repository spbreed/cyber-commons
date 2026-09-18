#!/usr/bin/env python3
"""Refuse to start an offensive-agent engagement until every safety control is present, and tell the SOC what to expect.

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
    python3 skills/redteam/offensive-agent-safety-preflight/scripts/offensive_agent_safety_preflight.py

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
# Seven controls. BLOCKING means the engagement does not start without it — not
# because the control is more important, but because its absence cannot be
# noticed later. A missing egress allowlist is invisible until data has left.
CONTROLS = [
    ("zero_data_retention", True,
     "provider retains no prompts or completions",
     "target data enters a third party's training set or breach"),
    ("sandbox", True,
     "the agent runs in an isolated, disposable workspace",
     "a payload that escapes lands on a corporate host"),
    ("egress_allowlist", True,
     "outbound restricted to the engagement scope",
     "the agent tests something you were not authorised to touch"),
    ("secret_management", True,
     "credentials injected at call time, never in prompt or repo",
     "the tester's own credentials end up in a trace or a report"),
    ("human_in_the_loop", True,
     "a named person approves every destructive action",
     "an exploit runs against production because it looked in scope"),
    ("deterministic_guardrails", True,
     "scope and rate enforced outside the model, not asked of it",
     "the model is argued out of the scope it was told to respect"),
    ("soc_notified", False,
     "the SOC has the window, source addresses and expected signatures",
     "your own detection team runs a real incident against you"),
]

ENGAGEMENTS = {
 "cybertravels-q3-external": {
    "zero_data_retention": True,  "sandbox": True,   "egress_allowlist": True,
    "secret_management": True,    "human_in_the_loop": True,
    "deterministic_guardrails": True, "soc_notified": True,
 },
 "quick-look-before-the-board": {
    "zero_data_retention": False, "sandbox": True,   "egress_allowlist": False,
    "secret_management": True,    "human_in_the_loop": False,
    "deterministic_guardrails": False, "soc_notified": False,
 },
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"CONTROLS": CONTROLS, "ENGAGEMENTS": ENGAGEMENTS}


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
