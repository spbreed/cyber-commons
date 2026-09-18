#!/usr/bin/env python3
"""Run the model over the one defect Semgrep structurally cannot reach, and record it as a hypothesis.

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
    python3 skills/appsec/sast-model-pass/scripts/sast_model_pass.py

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
# The format names its own tokens. An earlier version wrote the first field as
# "VERDICT", and a served Qwen2.5-7B returned the literal string VERDICT — it
# read the placeholder as the answer. The ask is the part you own, and that is
# B2.1's whole point arriving here as a bug.
QUESTION = ("Does this function verify that the caller is entitled to the rows "
            "it returns?\n"
            "Reply on ONE line, four fields separated by |:\n"
            "  field 1: exactly MISSING or PRESENT\n"
            "  field 2: a CWE id, e.g. CWE-862\n"
            "  field 3: your confidence, 0.00 to 1.00\n"
            "  field 4: one line copied exactly from the code above, or NONE\n"
            "Example of the shape: PRESENT|CWE-862|0.90|require_owner(x)")

# The replays are labelled and visible in the source, per the adapter's
# contract. They are what a correct answer looks like: the defect found on the
# function that has one, and no defect claimed on the function that does not.
# The fabrication that the verifier catches is demonstrated separately, below,
# so the rejection path is exercised on every run rather than only when a model
# happens to invent something.
REPLAY = {
    "get_booking":    "MISSING|CWE-639|0.82|def get_booking(session, booking_id):",
    "get_my_booking": "PRESENT|CWE-639|0.77|    require_owner(session, row[\"owner_id\"] if row else None)",
}

VERDICTS = {}

# Step 3, as a check of the check. The rejection must be demonstrated on every
# run, and it cannot be demonstrated by *waiting for the model to be wrong*: a
# capable model gets the already-authorised control function right, which is
# the outcome you want and would leave the verifier untested. So the verifier
# is tested directly, against a quote known not to be in the file.
# A real fabrication, recorded from a run of this skill against a smaller model:
# a confident CWE-89 on a function whose query is already parameterised, quoting
# a concatenation that does not appear anywhere in the slice.
FABRICATED = 'cur.execute("SELECT * FROM bookings WHERE owner = \'" + user)'
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"QUESTION": QUESTION, "REPLAY": REPLAY, "VERDICTS": VERDICTS, "FABRICATED": FABRICATED}


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
