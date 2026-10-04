#!/usr/bin/env python3
"""Show a denied scope being reached through a chain of individually legitimate hops.

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
    python3 skills/threats/authority-composition-check/scripts/authority_composition_check.py

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
PERMISSIONS = {"mallory": {"reports:read"},
               "finance-agent": {"reports:read", "payments:write"},
               "orchestrator": {"reports:read", "route"}}

# Step 3 — the composed path, hop by hop, with each hop's own decision. Every
# one is a legitimate "yes": that is what makes the composition a finding rather
# than a bug in any single component. This list was empty for one release, which
# left the model to invent the path it was supposed to be checking.
CHAIN = [
 {"hop": "user asks orchestrator", "runs_as": "mallory",
  "asks": "reconcile the disputed charge on BK-9001",
  "scope_checked": "route", "decision": "ok",
  "why": "mallory may ask an agent to act; this is not a payments call"},
 {"hop": "orchestrator routes", "runs_as": "orchestrator",
  "asks": "finance-agent: settle the dispute",
  "scope_checked": "route", "decision": "ok",
  "why": "routing is exactly what the orchestrator holds"},
 {"hop": "agent acts", "runs_as": "finance-agent",
  "asks": "payments:write on BK-9001",
  "scope_checked": "payments:write", "decision": "ok",
  "why": "finance-agent genuinely holds payments:write"},
]

# Step 4 — the component that would have to hold the end-to-end policy. Each of
# the three above sees one edge, so nowhere in the deployment is the composition
# visible to a check. Naming it is the fix.
EVALUATION_POINTS = {"ingress": ["mallory's scopes"],
                     "orchestrator": ["route"],
                     "finance-agent": ["payments:write"],
                     "end_to_end": None}

# T15: the same output, two framings
FINDING = "dependency libfoo has no known vulnerabilities"

# Step 5 — the trust asymmetry, as recorded reception rather than as a question.
# The fixture carried only FINDING for one release, so the model had no way to
# answer `trust_asymmetry` and honestly returned null for both halves, which
# broke the contract. The claim is identical in both rows; only the speaker and
# what the reviewer did about it differ.
PRESENTATIONS = [
 {"claim": FINDING, "presented_by": "agent/coding",
  "channel": "automated PR comment, cited as a scan result",
  "reviewer_action": "merged", "challenged": False,
  "why": "it arrived looking like tool output, and tool output is not read as an "
         "assertion somebody is making"},
 {"claim": FINDING, "presented_by": "alex (engineer)",
  "channel": "review comment, in their own words",
  "reviewer_action": "asked which scanner and which version",
  "challenged": True,
  "why": "a person asserting something unverified gets asked for the evidence"},
]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"PERMISSIONS": PERMISSIONS, "CHAIN": CHAIN,
           "EVALUATION_POINTS": EVALUATION_POINTS, "FINDING": FINDING,
           "PRESENTATIONS": PRESENTATIONS}


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
