#!/usr/bin/env python3
"""Map each control failure in a published incident to the control that would have closed it, and count preventive against detective.

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
    python3 skills/research/incident-control-mapping/scripts/incident_control_mapping.py

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
# The incident's control register, embedded verbatim. It is the same list
# `labs/incident-register/register.json` holds and `check_register.py`
# keeps in step, so the mapping below is against real rows rather than
# an illustration.
REGISTER = [
 # id      name                                     type   NIST     owning lesson
 ("B2.10",  "out-of-band telemetry capture",         "P/D", "AU-9",  "A2.8"),
 ("C1.2",  "hash-chained WORM transcript store",    "P",   "AU-10", "A2.8"),
 ("C1.3",  "logging-plane isolation",               "P",   "SC-39", "A2.8"),
 ("C1.4",  "escape detection",                      "D",   "SI-7",  "D2.3"),
 ("C2.1",  "per-run namespace isolation",           "P",   "SC-4",  "A3.8"),
 ("C2.2",  "immutable / write-once artifact cache", "P",   "AC-4",  "A3.8"),
 ("C2.3",  "covert channel analysis",               "D",   "SC-31", "D3.8"),
 ("C2.4",  "write-pattern anomaly detection",       "D",   "SI-4",  "D3.8"),
 ("C3.1",  "parser sandboxing",                     "P",   "SI-3",  "A3.2"),
 ("C3.2",  "credential removal from workers",       "P",   "AC-6",  "A2.4"),
 ("C3.3",  "micro-segmentation, default-deny egress","P",  "SC-7",  "A3.3"),
 ("C3.4",  "dataset and upload content scanning",   "D",   "SI-10", "D2.3"),
 ("C4.1",  "secret scanning, automated revocation", "D/C", "IA-5",  "D2.3"),
 ("C4.2",  "short-lived workload credentials",      "P",   "IA-5",  "A2.4"),
 ("C4.3",  "scope minimisation",                    "P",   "AC-6",  "A2.3"),
 ("C4.4",  "credential canaries",                   "D",   "SI-4",  "D2.6"),
 ("C5.1",  "artifact signing verified at pull",     "P",   "SR-11", "A3.8"),
 ("C5.2",  "provenance attestation",                "P",   "SR-4",  "A3.8"),
 ("C5.3",  "admin-plane separation, JIT elevation", "P/D", "AC-6",  "A3.8"),
 ("C5.4",  "cache integrity diffing",               "D",   "SI-7",  "D2.3"),
 ("C6.1",  "control-exemption gate",                "P",   "CM-3",  "A3.9"),
 ("C6.2",  "mandatory blast-radius caps",           "P",   "RA-3",  "A3.9"),
 ("C6.3",  "continuous exemption-state monitoring", "D/C", "CA-7",  "D2.3"),
 ("C6.4",  "exemption register at launch approval", "P",   "PM-9",  "A3.9"),
 ("C7.1",  "authenticated principal hierarchy",     "P",   "IA-9",  "A2.6"),
 ("C7.2",  "channel separation",                    "P",   "AC-3",  "A2.6"),
 ("C7.3",  "prompt-injection filtering",            "P/D", "SI-10", "A2.6"),
 ("C7.4",  "authorisation-decision logging",        "D",   "AU-2",  "D3.8"),
 ("C8.1",  "cross-trajectory correlation analytics","D",   "SI-4",  "D3.8"),
 ("C8.2",  "population and lifetime quotas",        "P",   "SC-6",  "A3.9"),
 ("C8.3",  "fleet kill switch",                     "C",   "IR-4",  "D4.5"),
 ("C8.4",  "coordination-signature detection",      "D",   "SI-4",  "D3.8"),
 ("C9.1",  "first-class report-to-human tool",      "P",   "IR-6",  "A3.10"),
 ("C9.2",  "escalation-path testing",               "D",   "IR-3",  "D3.8"),
 ("C9.3",  "non-use telemetry",                     "D",   "SI-4",  "D3.8"),
 ("C9.4",  "mandatory HITL checkpoint on discovery","P",   "AC-3",  "A3.10"),
 ("C10.1", "cheat-surface red team",                "P",   "SA-11", "C1.2"),
 ("C10.2", "explicit abstain affordance",           "P",   "SA-8",  "A3.10"),
 ("C10.3", "honeypot and canary tasks",             "D",   "RA-5",  "D2.6"),
 ("C10.4", "scorer integrity separation",           "P",   "SC-7",  "A3.8"),
]

SURFACE_USED_BY = {
 "artifact repository": [1, 2, 5],
 "agent container":     [1],
 "third-party upload":  [3],
 "public internet":     [4],
 "eval configuration":  [6],
 "peer channel":        [7, 8],
 "harness tooling":     [9],
 "benchmark scoring":   [10],
}

FUNCTION = {"A": "securing the architecture", "C": "red teaming and research",
            "D": "the agentic SOC"}

PRECONDITIONS = {
 "parallel agents on one task":        ("present", "R8"),
 "shared mutable surface between runs":("present", "R4, R7"),
 "agents read each other's output":    ("present", "R3"),
 "workload-writable transcript":       ("present", "R10, R11"),
 "credentials reachable from workload":("present", "R5"),
 "reachable third party":              ("present", "R4, R9"),
 "no agent-to-human escalation path":  ("present", "-"),
 "detective control switched off":     ("present", "R2"),
 "tens of thousands of agents at once":("not yet",  "-"),
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"REGISTER": REGISTER, "SURFACE_USED_BY": SURFACE_USED_BY, "FUNCTION": FUNCTION, "PRECONDITIONS": PRECONDITIONS}


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
