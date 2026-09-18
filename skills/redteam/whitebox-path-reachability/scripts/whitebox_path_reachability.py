#!/usr/bin/env python3
"""Separate reachable sinks from present ones, and name the authorisation predicate on each path.

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
    python3 skills/redteam/whitebox-path-reachability/scripts/whitebox_path_reachability.py

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
# What a white-box engagement is actually handed. Naming the source per fact is
# the difference between a finding and an assertion — a reader can go and check
# any row of this.
DATA_SOURCES = [
    ("repository at a pinned commit", "entry points, call graph, sinks"),
    ("dependency lock file",          "the versions really resolved"),
    ("IaC plan",                      "what is exposed, and to whom"),
    ("tool / MCP manifests",          "what each agent may call"),
    ("IAM policy + role bindings",    "the authority behind each caller"),
    ("API schema (OpenAPI)",          "the objects and verbs that exist"),
    ("prior findings",                "what has already been refuted"),
]

# entry point -> ordered hops -> sink. `guard` is the authorisation predicate
# actually present on that hop, or None where there is none.
PATHS = [
    ("POST /bookings",            [("handler", "session"), ("svc.book", "owner==caller")], "db.bookings.write",   True),
    ("POST /refunds",             [("handler", "session"), ("svc.refund", None)],          "payments.refund",     True),
    ("GET  /bookings/{id}",       [("handler", "session"), ("svc.get", None)],             "db.bookings.read",    True),
    ("MCP  vendor.itinerary",     [("tool_router", None), ("svc.book", "owner==caller")],  "db.bookings.write",   True),
    ("cron nightly_reconcile",    [("job", "service_account")],                            "payments.refund",     True),
    ("(none)",                    [],                                                      "admin.reset_all",     False),
    ("(none)",                    [],                                                      "db.audit.purge",      False),
]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"DATA_SOURCES": DATA_SOURCES, "PATHS": PATHS}


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
