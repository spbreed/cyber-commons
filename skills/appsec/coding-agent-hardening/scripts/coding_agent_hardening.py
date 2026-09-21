#!/usr/bin/env python3
"""Audit a coding agent's own configuration, tool list and MCP servers.

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
    python3 skills/appsec/coding-agent-hardening/scripts/coding_agent_hardening.py

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
SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}

DEV_TOOLS = [
 # (name, writes, scope, reversible, needed in the inner loop)
 ("read_file",  False,"self",   True,  True),
 ("write_file", True, "project",True,  True),
 ("run_tests",  True, "self",   True,  True),
 ("run_shell",  True, "tenant", False, True),
 ("git_commit", True, "project",True,  True),
 ("git_push",   True, "project",False, False),
 ("read_env",   False,"org",    True,  False),
 ("http_get",   False,"self",   True,  True),
]

HOME = [
 "/home/dana/work/monorepo/src/app.py",
 "/home/dana/work/monorepo/.env",
 "/home/dana/work/other-team-repo/secrets.yaml",
 "/home/dana/.aws/credentials",
 "/home/dana/.ssh/id_ed25519",
 "/home/dana/.config/gcloud/application_default_credentials.json",
 "/home/dana/Downloads/customer-export-2026.csv",
]

DENY = ("*/.ssh/*","*/.aws/*","*/.config/gcloud/*","*.pem","*/.env","*/Downloads/*")

# What actually reaches a coding agent's context in a normal repository.
SURFACE = [
 ("AGENTS.md",             "operator", True),
 (".claude/settings.json", "operator", True),
 ("README.md",             "content",  True),
 ("docs/CONTRIBUTING.md",  "content",  True),
 ("package.json",          "content",  True),   # a hook may execute its scripts
 ("vendor/lib/README.md",  "content",  False),
]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"SCOPE_WEIGHT": SCOPE_WEIGHT, "DEV_TOOLS": DEV_TOOLS, "HOME": HOME, "DENY": DENY, "SURFACE": SURFACE}


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
