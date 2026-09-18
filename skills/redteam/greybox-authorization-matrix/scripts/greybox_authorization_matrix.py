#!/usr/bin/env python3
"""Fill a roles-by-objects-by-verbs matrix from real credentials, and rank the cells nobody tested.

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
    python3 skills/redteam/greybox-authorization-matrix/scripts/greybox_authorization_matrix.py

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
# Grey box is defined by what you are given, and this is the list. One
# credential per role is the entire reason the mode can find BOLA at all.
DATA_SOURCES = [
    ("one credential per role",   "traveller, agent-svc, finance — the minimum"),
    ("API schema (OpenAPI)",      "every object and verb that exists"),
    ("object id samples per role", "two ids you own, two you must not"),
    ("the role matrix as designed", "what the team BELIEVES is enforced"),
    ("rate limits and scope",     "so the run does not become an incident"),
]

ROLES = ["traveller", "agent-svc", "finance"]

OBJECTS = ["booking(own)", "booking(other)", "refund", "profile(other)", "audit_log"]

VERBS = ["read", "write"]

# (role, object, verb) -> "allow" | "deny"  : what the design says.
DESIGN = {
    ("traveller", "booking(own)", "read"): "allow",
    ("traveller", "booking(own)", "write"): "allow",
    ("traveller", "booking(other)", "read"): "deny",
    ("traveller", "booking(other)", "write"): "deny",
    ("traveller", "refund", "read"): "allow",
    ("traveller", "refund", "write"): "deny",
    ("traveller", "profile(other)", "read"): "deny",
    ("traveller", "profile(other)", "write"): "deny",
    ("traveller", "audit_log", "read"): "deny",
    ("traveller", "audit_log", "write"): "deny",
    ("agent-svc", "booking(own)", "read"): "allow",
    ("agent-svc", "booking(own)", "write"): "allow",
    ("agent-svc", "booking(other)", "read"): "deny",
    ("agent-svc", "booking(other)", "write"): "deny",
    ("agent-svc", "refund", "read"): "allow",
    ("agent-svc", "refund", "write"): "allow",
    ("agent-svc", "profile(other)", "read"): "deny",
    ("agent-svc", "profile(other)", "write"): "deny",
    ("agent-svc", "audit_log", "read"): "deny",
    ("agent-svc", "audit_log", "write"): "deny",
    ("finance", "booking(own)", "read"): "allow",
    ("finance", "booking(own)", "write"): "deny",
    ("finance", "booking(other)", "read"): "allow",
    ("finance", "booking(other)", "write"): "deny",
    ("finance", "refund", "read"): "allow",
    ("finance", "refund", "write"): "allow",
    ("finance", "profile(other)", "read"): "deny",
    ("finance", "profile(other)", "write"): "deny",
    ("finance", "audit_log", "read"): "allow",
    ("finance", "audit_log", "write"): "deny",
}

# What the engagement actually exercised, and what came back. Everything absent
# from this dict is an UNTESTED cell — which is the output of the skill.
TESTED = {
    ("traveller", "booking(own)", "read"): "allow",
    ("traveller", "booking(own)", "write"): "allow",
    ("traveller", "booking(other)", "read"): "allow",     # <- mismatch
    ("traveller", "refund", "read"): "allow",
    ("traveller", "refund", "write"): "deny",
    ("traveller", "audit_log", "read"): "deny",
    ("agent-svc", "booking(own)", "read"): "allow",
    ("agent-svc", "booking(other)", "write"): "allow",    # <- mismatch
    ("agent-svc", "refund", "write"): "allow",
    ("finance", "booking(other)", "read"): "allow",
    ("finance", "refund", "write"): "allow",
    ("finance", "audit_log", "read"): "allow",
}

# How much a wrong answer in this cell costs, so the untested list is ranked by
# something other than the order the endpoints appear in the schema.
BLAST = {"booking(other)": 3, "refund": 4, "profile(other)": 4, "audit_log": 5,
         "booking(own)": 1}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n{json.dumps(value, indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"DATA_SOURCES": DATA_SOURCES, "ROLES": ROLES, "OBJECTS": OBJECTS, "VERBS": VERBS, "DESIGN": DESIGN, "TESTED": TESTED, "BLAST": BLAST}


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
