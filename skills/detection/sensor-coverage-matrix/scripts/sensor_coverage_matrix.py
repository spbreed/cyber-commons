#!/usr/bin/env python3
"""Score the sensor classes an estate already owns against what an agent actually does.

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
    python3 skills/detection/sensor-coverage-matrix/scripts/sensor_coverage_matrix.py

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
# Four sensor classes almost every estate has bought, with an open-source
# reference product so the claim is checkable rather than vendor-shaped.
SENSORS = [
    ("EDR",   "Wazuh agent",          "process, file and network activity on a host"),
    ("DLP",   "regex + Wazuh FIM",    "sensitive content leaving a monitored channel"),
    ("CSPM",  "Prowler / ScoutSuite", "cloud configuration, evaluated periodically"),
    ("CNAPP", "Falco + Trivy",        "container runtime syscalls and image contents"),
]

# What CyberTravels' agents do in an ordinary day. Each row records, per sensor,
# whether it sees the action at all — not whether it would alert on it.
#   full    the action is visible with enough fidelity to reason about
#   partial something is visible, but not the part that decides
#   none    the sensor is not in the path
ACTIONS = [
    ("write a file into the agent workdir",        {"EDR": "full",    "DLP": "none",    "CSPM": "none",    "CNAPP": "full"}),
    ("open an outbound TLS session to a model API", {"EDR": "partial", "DLP": "none",    "CSPM": "none",    "CNAPP": "partial"}),
    ("read a customer record through an internal API", {"EDR": "none", "DLP": "none",    "CSPM": "none",    "CNAPP": "none"}),
    ("place 900 tokens of that record in a prompt", {"EDR": "none",    "DLP": "none",    "CSPM": "none",    "CNAPP": "none"}),
    ("call a vendor MCP tool",                     {"EDR": "none",     "DLP": "none",    "CSPM": "none",    "CNAPP": "none"}),
    ("issue a refund through the payments API",    {"EDR": "none",     "DLP": "none",    "CSPM": "none",    "CNAPP": "none"}),
    ("assume a wider IAM role",                    {"EDR": "none",     "DLP": "none",    "CSPM": "partial", "CNAPP": "none"}),
    ("spawn a child agent process",                {"EDR": "full",     "DLP": "none",    "CSPM": "none",    "CNAPP": "full"}),
    ("exfiltrate to an allowed SaaS domain",       {"EDR": "partial",  "DLP": "partial", "CSPM": "none",    "CNAPP": "partial"}),
]

WEIGHT = {"full": 1.0, "partial": 0.5, "none": 0.0}

MARK = {"full": "##", "partial": "..", "none": "  "}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"SENSORS": SENSORS, "ACTIONS": ACTIONS, "WEIGHT": WEIGHT, "MARK": MARK}


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
