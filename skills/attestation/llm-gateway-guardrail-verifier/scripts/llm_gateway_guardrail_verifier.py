#!/usr/bin/env python3
"""Send five calls through one gateway and record which check refuses each one.

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
    python3 skills/attestation/llm-gateway-guardrail-verifier/scripts/llm_gateway_guardrail_verifier.py

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
LEGACY_DB_CREDENTIAL = "static-service-password"     # never leaves the gateway

REGISTRY = {"spiffe://corp/reports-agent": {"owner": "sam@corp", "expires": 9000}}

POLICY = {("reports-agent", "run_query", "table:reports"): {"SELECT"}}

EGRESS_ALLOW = {"reports-db.corp.example"}

# What the gateway recorded for the calls it has already handled. The verifier's
# job is to check that each decision was made at the gateway and not merely
# noted by it, so every row carries the component that decided — and row 4 is the
# finding: `decided_by: "agent"` means the agent screened itself.
#
# Row 5 is the second one: an allowed egress to a destination not in
# EGRESS_ALLOW, logged as permitted. A gateway that records a decision it did not
# make is a description, not a control.
#
# This list was empty for one release, so there were no decisions to verify.
AUDIT = [
 {"seq": 1, "principal": "dana@corp", "tool": "run_query", "verb": "SELECT",
  "resource": "table:reports", "destination": "reports-db.corp.example",
  "decision": "allow", "decided_by": "gateway", "policy_hit": "reports:SELECT"},
 {"seq": 2, "principal": "dana@corp", "tool": "run_query", "verb": "DELETE",
  "resource": "table:reports", "destination": "reports-db.corp.example",
  "decision": "deny", "decided_by": "gateway", "policy_hit": "no rule for DELETE"},
 {"seq": 3, "principal": "dana@corp", "tool": "run_query", "verb": "SELECT",
  "resource": "table:payroll", "destination": "reports-db.corp.example",
  "decision": "deny", "decided_by": "gateway", "policy_hit": "resource not in policy"},
 {"seq": 4, "principal": "dana@corp", "tool": "run_query", "verb": "SELECT",
  "resource": "table:reports", "destination": "reports-db.corp.example",
  "decision": "allow", "decided_by": "agent", "policy_hit": None},
 {"seq": 5, "principal": "dana@corp", "tool": "send_email", "verb": "POST",
  "resource": "mail", "destination": "archive@evil.example",
  "decision": "allow", "decided_by": "gateway", "policy_hit": None},
]

BASE = {"identity": "spiffe://corp/reports-agent", "agent": "reports-agent",
        "principal": "dana@corp", "tool": "run_query", "resource": "table:reports",
        "verb": "SELECT", "destination": "reports-db.corp.example", "calls_so_far": 0}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"LEGACY_DB_CREDENTIAL": LEGACY_DB_CREDENTIAL, "REGISTRY": REGISTRY, "POLICY": POLICY, "EGRESS_ALLOW": EGRESS_ALLOW, "AUDIT": AUDIT, "BASE": BASE}


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
