#!/usr/bin/env python3
"""Assess AI components of a supply chain for silent change and agent authority, and invalidate the control tests taken before a model changed.

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
    python3 skills/grc/third-party-ai-assessment/scripts/third_party_ai_assessment.py

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

QUESTIONS = [
 ("Can this component change without notifying us?",
  "if yes, every control test has an implicit expiry tied to the vendor"),
 ("Does it execute with our agent's authority?",
  "if yes, assess it as code, not as a dependency"),
 ("Can we pin a digest, and do we?",
  "the difference between a supply chain and a subscription"),
 ("What is our exit if we stop using it?",
  "DORA Art.11 asks this directly; most AI contracts have no answer"),
]

SIGNALS = {
 "library":      {"signature": True, "downloads": True, "pinning": True, "lineage": True},
 "hosted model": {"signature": False, "downloads": False, "pinning": False, "lineage": False},
 "weights":      {"signature": True, "downloads": False, "pinning": True, "lineage": False},
 "tool package": {"signature": False, "downloads": False, "pinning": True, "lineage": False},
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"DAY": DAY, "QUESTIONS": QUESTIONS, "SIGNALS": SIGNALS}


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
