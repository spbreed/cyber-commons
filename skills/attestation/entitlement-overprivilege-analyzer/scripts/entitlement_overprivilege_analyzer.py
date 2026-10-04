#!/usr/bin/env python3
"""Bind a grant to one scope, one resource and one task, and show what it refuses once the task closes.

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
    python3 skills/attestation/entitlement-overprivilege-analyzer/scripts/entitlement_overprivilege_analyzer.py

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
# The authorisation graph for CyberTravels' four agents. `required` is the
# denominator from the code-surface analyzer — what the declared tools genuinely
# need — and `granted` is what the deployment actually handed out. The gap
# between the two columns is the whole report.
#
# `expires: None` is standing privilege: a grant that is permanent rather than
# issued per task. It is the row step 5 exists to flag, and three of these have
# it. This dict was empty for one release, so the analyzer diffed nothing
# against nothing and said so in the right shape.
GRANTS = {
 "spiffe://cybertravels.local/agent/workflow": {
   "granted":  ["bookings:read", "bookings:write", "payments:refund",
                "payments:write", "invoices:write", "db:admin"],
   "required": ["bookings:read", "bookings:write", "payments:refund"],
   "expires":  None},

 "spiffe://cybertravels.local/agent/rag-advisor": {
   # Reads documents. Was given booking writes because it shares a role with the
   # workflow agent — the commonest shape of this finding in a real estate.
   "granted":  ["knowledge:search", "bookings:read", "bookings:write"],
   "required": ["knowledge:search"],
   "expires":  None},

 "spiffe://cybertravels.local/agent/coding": {
   "granted":  ["repo:read", "repo:write"],
   "required": ["repo:read", "repo:write"],
   "expires":  1400},

 "spiffe://cybertravels.local/agent/file": {
   "granted":  ["vendor-docs:read"],
   "required": ["vendor-docs:read"],
   "expires":  None},
}

# Step 3 — stored provider scopes, which are wider than the tool needs because
# the consent screen offered a bundle and somebody clicked it.
OAUTH = [
 {"provider": "stripe", "granted_scope": "charges:write,refunds:write,payouts:write",
  "used_by": "agent/workflow"},
 {"provider": "google-drive", "granted_scope": "drive.readonly,drive.file",
  "used_by": "agent/file"},
]

CLOCK = {"now": 1000}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"GRANTS": GRANTS, "OAUTH": OAUTH, "CLOCK": CLOCK}


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
