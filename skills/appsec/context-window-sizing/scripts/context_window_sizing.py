#!/usr/bin/env python3
"""Find the smallest slice of a file in which a defect is decidable, and measure what larger contexts add.

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
    python3 skills/appsec/context-window-sizing/scripts/context_window_sizing.py

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
SOURCE = '''"""Reporting service."""
import logging, os, json, datetime

log = logging.getLogger(__name__)
DEFAULT_LIMIT = 100
CACHE = {}

def _format_row(row):
    return {"id": row[0], "name": row[1], "created": str(row[2])}

def _cache_key(*parts):
    return ":".join(str(p) for p in parts)

def healthcheck():
    return {"status": "ok", "ts": datetime.datetime.utcnow().isoformat()}

def list_reports(conn, owner, limit=DEFAULT_LIMIT):
    """Called from GET /reports?owner=... — owner is user-controlled."""
    key = _cache_key("reports", owner, limit)
    if key in CACHE:
        return CACHE[key]
    rows = conn.execute("SELECT * FROM reports WHERE owner = '" + owner + "' LIMIT " + str(limit))
    out = [_format_row(r) for r in rows]
    CACHE[key] = out
    return out

def purge_cache():
    CACHE.clear()
    log.info("cache purged")
'''

COSTS = {
    "whole file":     "reviews whatever survived truncation; you cannot tell which parts",
    "±2 line window": "cannot see the signature, so it GUESSES whether owner is tainted",
    "±6 line window": "decidable, and carrying one function the defect does not depend on",
    "path slice":     "decidable, nothing unrelated - the answer is checkable",
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"SOURCE": SOURCE, "COSTS": COSTS}


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
