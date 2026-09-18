#!/usr/bin/env python3
"""Score three real Semgrep runs against a hand-written key, and report recall per ruleset width.

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
    python3 skills/appsec/sast-semgrep-deterministic/scripts/sast_semgrep_deterministic.py

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
# Step 1 — the key, from cybertravels/LABELS.md, written by reading the tree
# before any scan. `expressible` is the question that decides what a scanner
# could ever do, and it has three values rather than two.
#   yes      a pattern matches it
#   library  a pattern matches it in a library the rule knows about
#   no       the defect is the absence of a call; there is nothing to match
KEY = [
    ("tools/bookings_api.py",  20, "get_booking",      "CWE-639", "no",
     "returns the row a caller names, no owner comparison"),
    ("tools/bookings_api.py",  34, "cancel_booking",   "CWE-639", "no",
     "cancels the booking a caller names, and it writes"),
    ("tools/bookings_api.py",  41, "search_bookings",  "CWE-89",  "yes",
     "reference concatenated into the query"),
    ("tools/payments_api.py",   8, "issue_refund",     "CWE-639", "no",
     "refunds against any booking id, on the money path"),
    ("tools/payments_api.py",  23, "download_invoice", "CWE-22",  "yes",
     "vendor filename joined to a root"),
    ("agents/coding_agent.py", 13, "_open_branch",     "CWE-78",  "yes",
     "branch name reaches a shell"),
    ("agents/coding_agent.py", 18, "sync_vendor",      "CWE-295", "library",
     "verify=False, on the house HTTP wrapper rather than requests"),
    ("agents/file_agent.py",   11, "render_template",  "CWE-95",  "yes",
     "customer template evaluated"),
]

ORDER = ["narrow", "wide", "taint"]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"KEY": KEY, "ORDER": ORDER}


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
