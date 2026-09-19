#!/usr/bin/env python3
"""Assemble the context a triage decision needs, and show what the same alert looks like without it.

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
    python3 skills/secops/detection-triage/scripts/detection_triage.py

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
TRUTH = {"patch-agent": "tp", "rotator-agent": "fp"}

FIELDS = {
 "acting identity":  "which agent — not the human whose token it borrowed",
 "principal":        "who the action was for",
 "delegation chain": "who caused the task; where to look for the trigger",
 "scopes held":      "THE decisive field — is this action within its remit?",
 "tool + target":    "what it did",
 "session/trace id": "so the analyst can pull the whole run (E1.3)",
}

ALERTS = [("A-1", "patch-agent"), ("A-2", "rotator-agent"), ("A-3", "patch-agent"),
          ("A-4", "rotator-agent"), ("A-5", "patch-agent"), ("A-6", "rotator-agent")]

SAMPLE_RATE = 0.34
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"TRUTH": TRUTH, "FIELDS": FIELDS, "ALERTS": ALERTS, "SAMPLE_RATE": SAMPLE_RATE}


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
