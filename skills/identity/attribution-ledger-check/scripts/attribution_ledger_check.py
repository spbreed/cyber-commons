#!/usr/bin/env python3
"""Put the four investigation questions to one ledger entry, and try to amend the record as the agent.

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
    python3 skills/identity/attribution-ledger-check/scripts/attribution_ledger_check.py

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
# The same incident A2.0's audit-answerability-check reads as a three-line tool
# log, where it answers none of the four questions. Here it answers all four,
# and the ids are deliberately identical so the two records can be read side by
# side: the difference is the design, not the incident.
#
# This list was empty for one release. The skill still ran, the model still
# answered, and the contract still held — it reported on nothing, in the right
# shape. That is the failure this file exists to not repeat, and the reason
# check_skills.py now fails an empty fixture.
LEDGER = [
 # Append-only, and the agent holds no credential for the destination: `writer`
 # is the collector, never the acting workload. That is the fifth procedure step.
 {"seq": 1, "ts": "09:14:07",
  "principal": "dana@cybertravels.example",
  "workload": "spiffe://cybertravels.local/agent/workflow",
  "instance": "run-8812",
  "chain": ["dana@cybertravels.example", "orchestrator", "agent/workflow"],
  "tool": "fetch_doc", "audience": "vendor-server", "scope": "documents:read",
  "args": {"id": "wiki/473"},
  "motivating_input": {"ref": "traveller asked why she was charged twice",
                       "origin": "user"},
  "writer": "collector@audit", "trace_id": "tr-4417"},

 # The row question 4 exists for. Without `motivating_input` this reads as an
 # agent deciding on its own to retire an invoice; with it, the vendor document
 # fetched one second earlier is visibly the cause.
 {"seq": 2, "ts": "09:14:11",
  "principal": "dana@cybertravels.example",
  "workload": "spiffe://cybertravels.local/agent/workflow",
  "instance": "run-8812",
  "chain": ["dana@cybertravels.example", "orchestrator", "agent/workflow"],
  "tool": "run_query", "audience": "internal-server", "scope": "invoices:write",
  "args": {"sql": "DELETE FROM invoices WHERE id=8812"},
  "motivating_input": {"ref": "wiki/473: retire invoice 8812 when the customer "
                              "disputes a duplicate charge",
                       "origin": "knowledge"},
  "writer": "collector@audit", "trace_id": "tr-4417"},

 {"seq": 3, "ts": "09:14:12",
  "principal": "dana@cybertravels.example",
  "workload": "spiffe://cybertravels.local/agent/workflow",
  "instance": "run-8812",
  "chain": ["dana@cybertravels.example", "orchestrator", "agent/workflow"],
  "tool": "send_email", "audience": "internal-server", "scope": "mail:send",
  "args": {"to": "ops@cybertravels.example"},
  "motivating_input": {"ref": "wiki/473: notify operations after retiring",
                       "origin": "knowledge"},
  "writer": "collector@audit", "trace_id": "tr-4417"},
]

# Step 4 and 5 need something to attempt the amendment *against*. Without this
# the model has to guess whether the store refuses, and a guess about the
# control is the one thing this skill is for.
STORE = {"kind": "append-only table, separate database",
         "writer_identity": "collector@audit",
         "agent_roles_with_write": [],          # the acting workload has none
         "grants_to_agent": ["SELECT"],
         "supports": ["INSERT"],                # no UPDATE, no DELETE, no reorder
         "retention": "400 days, then archived to object storage"}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"LEDGER": LEDGER, "STORE": STORE}


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
