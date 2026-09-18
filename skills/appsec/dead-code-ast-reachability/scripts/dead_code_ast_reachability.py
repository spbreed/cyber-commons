#!/usr/bin/env python3
"""Parse CyberTravels' booking service to an AST, build the call graph, and split the finding queue on it.

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
    python3 skills/appsec/dead-code-ast-reachability/scripts/dead_code_ast_reachability.py

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
# Findings from the audit stage, each naming the unit it landed in. These are
# the rows of cybertravels/LABELS.md that this stage receives.
FINDINGS = [
    ("F1", "search_bookings",  "CWE-89",  9),
    ("F2", "render_template",  "CWE-95",  8),
    ("F3", "_open_branch",     "CWE-78",  9),
    ("F4", "download_invoice", "CWE-22",  6),
    ("F5", "sync_vendor",      "CWE-295", 5),
    ("F6", "receive",          "CWE-940", 4),
]

ENTRY_DECORATORS = {"route"}

# The graph, in a language a renderer reads. The buckets are what the reader
# needs to see at a glance and a three-colour picture carries that faster than
# the table above does. scripts/render_diagrams.py turns this into the SVG on
# the lesson page, with real Graphviz.
KIND = {"reachable": "unit", "unreachable": "dead", "unknown": "unknown"}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"FINDINGS": FINDINGS, "ENTRY_DECORATORS": ENTRY_DECORATORS, "KIND": KIND}


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
