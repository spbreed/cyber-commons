#!/usr/bin/env python3
"""Execute the same code against three environments and evaluate the network policies that separate them.

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
    python3 skills/runtime/sandbox-containment-probe/scripts/sandbox_containment_probe.py

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
HOST = {"fs": ["/home/agent/work/data.csv", "/home/agent/.ssh/id_ed25519",
                "/etc/passwd"],
        "env": {"AWS_ACCESS_KEY_ID": "AKIA-EXAMPLE-NOT-REAL",
                "DATABASE_URL": "postgres://bookings-db.prod/main"},
        "net": ["bookings-db.prod:5432", "169.254.169.254:80", "0.0.0.0/0"]}

CODE = "import os; d=os.environ; open('/home/agent/.ssh/id_ed25519'); connect('x')"

# The two NetworkPolicy objects above, as data. The point of modelling them
# rather than trusting them is the additive rule: a pod that NO policy selects
# is unrestricted, and policies never deny.
POLICIES = [
 {"name": "default-deny-all",      "selects": "*",              "egress": []},
 {"name": "workflow-agent-egress", "selects": "workflow-agent",
  "egress": [("bookings-db.prod", 5432), ("kube-dns", 53)]},
]

ATTEMPTS = [
 ("workflow-agent", "bookings-db.prod", 5432, "the one it needs"),
 ("workflow-agent", "kube-dns",           53, "resolution, explicitly granted"),
 ("workflow-agent", "169.254.169.254",    80, "cloud metadata - node credentials"),
 ("workflow-agent", "archive.evil.example", 443, "A1.3's exfiltration target"),
 ("coding-agent",   "archive.evil.example", 443, "a pod nobody wrote a policy for"),
]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"HOST": HOST, "CODE": CODE, "POLICIES": POLICIES, "ATTEMPTS": ATTEMPTS}


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
