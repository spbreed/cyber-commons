#!/usr/bin/env python3
"""Find the missing ownership checks in the CyberTravels repository, and score both detectors on recall.

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
    python3 skills/appsec/idor-detection-recall/scripts/idor_detection_recall.py

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
# The key, from cybertravels/LABELS.md — the five units missing an ownership
# check. Two of them carry a second defect as well: search_bookings also
# concatenates SQL and download_invoice also traverses a path. Semgrep finds
# those two and cannot see the authorisation defect in the same function, which
# is the most useful row in the key.
IDOR = {"get_booking", "cancel_booking", "issue_refund",
        "search_bookings", "download_invoice"}

# Also found by a ruleset, for a *different* defect in the same function.
ALSO_FOUND_BY_RULES = {"search_bookings": "CWE-89 at the widest width",
                       "download_invoice": "CWE-22, had a rule been enabled"}

# The safe twins. A corpus where everything is broken cannot measure precision.
AUTHORISED = {"get_my_booking", "get_receipt", "list_my_bookings"}

# What counts as comparing an owner. Traced through the helper, because a check
# inside require_owner is still a check.
OWNERSHIP = {"require_owner"}

SESSION_SCOPED = {"user_id"}

# Step 5 — severity from the authority the caller holds, not from the CWE.
AUTHORITY = {
    "get_booking":      ("Workflow Agent · booking.*", "high",
                         "any traveller's itinerary, on an agent-invoked tool"),
    "cancel_booking":   ("Workflow Agent · booking.*", "high",
                         "and it writes: cancels a booking that is not theirs"),
    "issue_refund":     ("Workflow Agent · payments.refund", "critical",
                         "money moves, against an id the model proposed"),
    "search_bookings":  ("Workflow Agent · booking.*", "high",
                         "returns every owner's bookings for a reference"),
    "download_invoice": ("File System Agent", "high",
                         "reads an invoice belonging to somebody else"),
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"IDOR": IDOR, "ALSO_FOUND_BY_RULES": ALSO_FOUND_BY_RULES, "AUTHORISED": AUTHORISED, "OWNERSHIP": OWNERSHIP, "SESSION_SCOPED": SESSION_SCOPED, "AUTHORITY": AUTHORITY}


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
