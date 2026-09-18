#!/usr/bin/env python3
"""Split an external probe's claims into what was observed and what was inferred, and refuse a severity on the second kind.

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
    python3 skills/redteam/blackbox-claim-provenance/scripts/blackbox_claim_provenance.py

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
# Everything a black-box engagement is allowed to look at. The list is short on
# purpose: that is the whole constraint of the mode.
DATA_SOURCES = [
    ("DNS and certificate transparency", "names that exist"),
    ("TLS handshake",                    "the terminator, and its config"),
    ("HTTP status, headers, body",       "what the app chose to return"),
    ("error strings",                    "occasionally a stack, usually a template"),
    ("response timing",                  "a signal, and a noisy one"),
    ("public artefacts (JS, sitemaps)",  "routes the front end knows about"),
    ("the scope document",               "what you are permitted to touch"),
]

# claim, the evidence behind it, and whether the evidence ENTAILS it.
CLAIMS = [
    ("host api.cybertravels.example resolves and serves TLS 1.3",
     "handshake completed, cert chain read", True),
    ("/bookings/{id} exists",
     "200 on a known id, 404 on a random one", True),
    ("/bookings/{id} returns another tenant's booking",
     "404 on a random id", False),
    ("the app runs on Django",
     "X-Frame-Options and a csrftoken cookie name", False),
    ("an admin surface exists at /admin",
     "302 to a login form, distinct from the 404 template", True),
    ("the database is PostgreSQL",
     "an error string containing 'duplicate key value'", False),
    ("rate limiting is applied per IP",
     "429 after 61 requests in 60s from one address", True),
    ("rate limiting is NOT applied per account",
     "not tested; no second address available", False),
    ("refunds are processed synchronously",
     "response time 1.9s vs 120ms on reads", False),
    ("the refund endpoint accepts a booking id it does not own",
     "not tested; would require a second account", False),
    ("a vendor MCP server is in the request path",
     "a Server header naming a proxy", False),
    ("passport numbers are returned by /profile",
     "observed in a response to our own account", True),
]
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"DATA_SOURCES": DATA_SOURCES, "CLAIMS": CLAIMS}


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
