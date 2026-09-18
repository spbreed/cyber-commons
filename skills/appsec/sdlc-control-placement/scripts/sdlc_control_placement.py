#!/usr/bin/env python3
"""Place CyberTravels' security techniques on the pre/post-deploy line and count the risks covered only on the side that cannot act.

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
    python3 skills/appsec/sdlc-control-placement/scripts/sdlc_control_placement.py

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
# (technique, side, what the OTHER side sees that this cannot, can it block a merge)
TECHNIQUES = [
    ("SAST / code analysis",        "pre",  "whether the vulnerable path is reached with real traffic", True),
    ("SCA and SBOM scanning",       "pre",  "what actually loaded, versus what the manifest pinned", True),
    ("IaC and policy-as-code",      "pre",  "the identity and network the workload really got", True),
    ("threat modelling",            "pre",  "entry points added by a config change, not a commit", False),
    ("tool-schema / MCP review",    "both", "a description edited by the server after review", True),
    ("DAST / attack simulation",    "post", "the commit that introduced it", False),
    ("egress enforcement",          "post", "the config change that widened the allowlist", False),
    ("runtime posture and drift",   "post", "the plan the drift departed from", False),
    ("detection and canaries",      "post", "anything at all before it happens", False),
    ("attestation",                 "both", "nothing - it signs on the left and re-checks on the right", False),
]

# CyberTravels' risk classes, and which side each technique above actually
# covers them from. Sides, not tool names: two products on the same side of the
# line do not add coverage, they add invoices.
RISKS = [
    ("injection in application code",            ["pre", "post"]),
    ("vulnerable declared dependency",           ["pre"]),
    ("undeclared vendored binary",               []),
    ("over-broad IAM role at runtime",           ["post"]),
    ("prompt injection through retrieved text",  ["post"]),
    ("tool schema edited after review",          ["pre", "post"]),
    ("guardrail switched off after the demo",    ["post"]),
    ("secret committed to the repository",       ["pre"]),
]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"TECHNIQUES": TECHNIQUES, "RISKS": RISKS}


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
