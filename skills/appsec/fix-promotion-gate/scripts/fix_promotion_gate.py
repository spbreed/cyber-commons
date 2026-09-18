#!/usr/bin/env python3
"""Promote four candidate patches from the sandbox replica through QA to a merge request, and count how many CI alone would have merged.

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
    python3 skills/appsec/fix-promotion-gate/scripts/fix_promotion_gate.py

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
# (id, patch, ci_green, exploit_blocked_in_replica, behaviour_preserved_in_qa,
#  new_findings, what it actually did)
CANDIDATES = [
    ("A", 'execute("... ref = ?", (ref,))',       True,  True,  True,  0,
     "parameterised and bound - the fix"),
    ("B", 'execute("... ref = ?", (ref[:8],))',   True,  True,  False, 0,
     "parameterised, and silently truncates the reference"),
    ("C", 'execute("... ref = " + escape(ref))',  True,  False, True,  0,
     "still concatenation; escape() moved the pattern past the rule"),
    ("D", 'return []',                            True,  True,  True,  0,
     "closes the finding by removing partial-reference search"),
]

# Step 2 — the control. Without it a probe that stopped asserting reports every
# patch as a success, and this is the run that proves the probe still works.
EXPLOIT_ON_UNPATCHED = True
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n{json.dumps(value, indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"CANDIDATES": CANDIDATES, "EXPLOIT_ON_UNPATCHED": EXPLOIT_ON_UNPATCHED}


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
