#!/usr/bin/env python3
"""Provision an agent as a SCIM resource whose owner is a reference, then run a leaver event and see which agents survive it.

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
    python3 skills/identity/nhi-lifecycle-audit/scripts/nhi_lifecycle_audit.py

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
# A SCIM resource for an agent. The protocol is RFC 7644; the schema URN is
# your own extension, in exactly the way the enterprise extension declares
# "manager" for users. Note what "owner" is: a REFERENCE, not a name.
AGENT_SCHEMA = "urn:cybertravels:params:scim:schemas:extension:agent:2.0:Agent"

NOW = 5000

USERS = {                       # what SCIM /Users says about the humans
 "sam-2291":  {"userName": "sam@cybertravels.com",  "active": True},
 "dana-4417": {"userName": "dana@cybertravels.com", "active": True},
}

REGISTRY = {                    # what SCIM /Agents says about the agents
 "spiffe://cybertravels.com/ns/prod/sa/pricing-agent":
    {"active": True, "owner": "sam-2291",  "expires": 9000},
 "spiffe://cybertravels.com/ns/prod/sa/billing-agent":
    {"active": True, "owner": "dana-4417", "expires": 4000},   # lapsed
 "spiffe://cybertravels.com/ns/prod/sa/legacy-agent":
    {"active": True, "owner": None,        "expires": 9000},   # orphan
}

PRESENTING = [
 "spiffe://cybertravels.com/ns/prod/sa/pricing-agent",
 "spiffe://cybertravels.com/ns/prod/sa/billing-agent",
 "spiffe://cybertravels.com/ns/prod/sa/legacy-agent",
 "spiffe://cybertravels.com/ns/prod/sa/reporting-agent-v2",
]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"AGENT_SCHEMA": AGENT_SCHEMA, "NOW": NOW, "USERS": USERS, "REGISTRY": REGISTRY, "PRESENTING": PRESENTING}


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
