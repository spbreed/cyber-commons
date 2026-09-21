#!/usr/bin/env python3
"""Query an exposed data API as an anonymous caller with row-level security off and on, and count what a leaked key returns.

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
    python3 skills/research/row-level-policy-check/scripts/row_level_policy_check.py

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
AGENTS = [
 {"id": "a-0001", "owner": "dana@example",  "handle": "@researchbot",
  "provider_key": "sk-REDACTED-openai",     "claim_token": "clm_8fA2"},
 {"id": "a-0002", "owner": "sam@example",   "handle": "@newsdigest",
  "provider_key": "sk-ant-REDACTED",        "claim_token": "clm_2bQ7"},
 {"id": "a-0003", "owner": "kim@example",   "handle": "@dealfinder",
  "provider_key": "AKIA-REDACTED-aws",      "claim_token": "clm_9zR1"},
]

REPORTED_SCALE = {"Treblle": 770_000, "Wiz-sourced reporting": 1_500_000}

PROVIDERS = ["OpenAI", "Anthropic", "AWS", "GitHub", "Google Cloud"]

# Who can actually revoke each thing that leaked.
REVOCABLE_BY = {
 "the Moltbook session token": "Moltbook",
 "the claim token":            "Moltbook",
 "the agent's provider key":   "the individual who created the agent",
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"AGENTS": AGENTS, "REPORTED_SCALE": REPORTED_SCALE, "PROVIDERS": PROVIDERS, "REVOCABLE_BY": REVOCABLE_BY}


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
