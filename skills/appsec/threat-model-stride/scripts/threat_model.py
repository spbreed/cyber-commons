#!/usr/bin/env python3
"""Derive a STRIDE threat model and a trust-boundary diagram from five inputs.

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
    python3 skills/appsec/threat-model-stride/scripts/threat_model.py

With no endpoint configured this exits 2 and says so. Nothing is substituted
for a model's answer.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "_runtime"))

from cyber_commons_skill_runtime import (  # noqa: E402
    announce_backend, run_with_model)

SKILL = pathlib.Path(__file__).resolve().parents[1] / "SKILL.md"

# ---------------------------------------------------------------- the fixture
# ---------------------------------------------------------------- the fixture
SOURCES = {
 "src/api/bookings.py": '''
def get_booking(request):
    """HTTP GET /bookings/<ref> - request.args is traveller-controlled."""
    return render(load_booking(request.args["ref"], request.args["owner"]))

def upload_voucher(request):
    """HTTP POST /vouchers - the multipart body is traveller-controlled."""
    return store(request.files["doc"], request.args["name"])

def health(request):
    """HTTP GET /health - no session required."""
    return "ok"
''',
 "src/data/reports.py": '''
def load_booking(ref, owner):
    return DB.execute("SELECT * FROM bookings WHERE ref=" + ref)
''',
 "src/data/docs.py": '''
def store(blob, name):
    open("/srv/vouchers/" + name, "wb").write(blob)
''',
 "src/util/render.py": '''
def render(rows):
    return "\\n".join(str(r) for r in rows)
''',
}

TRUST = {"src/api": 0, "src/util": 1, "src/data": 2}   # 0 = the untrusted edge

DANGEROUS = {"execute": "bookings_db", "open": "voucher_bucket"}

UNAUTHENTICATED = {"health"}          # what the router leaves open

ASSETS = {"bookings_db": {"data": ["customer", "financial"], "value": 5},
          "voucher_bucket": {"data": ["documents"], "value": 3}}

CSPM = [
    {"resource": "voucher_bucket", "finding": "bucket policy allows public read",
     "severity": 4},
]

IAM = {"src/api": {"role": "cybertravels-api",
                   "assumable_by": ["ci-deploy-role", "*"],
                   "mfa_required": False}}

NETWORK = {"src/api": {"exposed": "internet", "waf": False,
                       "egress_default_deny": False,
                       "egress_allowed": ["0.0.0.0/0"]}}

ENTITLEMENTS = {"src/api": ["db:select", "db:update",
                            "s3:GetObject", "s3:PutObject"]}

HARDENED = {
    "cspm": [],
    "iam": {"src/api": {"role": "cybertravels-api",
                        "assumable_by": ["ci-deploy-role"], "mfa_required": True}},
    "network": {"src/api": {"exposed": "vpc-only", "waf": True,
                            "egress_default_deny": True,
                            "egress_allowed": ["bookings-db.prod:5432"]}},
    "entitlements": {"src/api": ["db:select", "s3:GetObject"]},
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n{json.dumps(value, indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"SOURCES": SOURCES, "TRUST": TRUST, "DANGEROUS": DANGEROUS, "UNAUTHENTICATED": UNAUTHENTICATED, "ASSETS": ASSETS, "CSPM": CSPM, "IAM": IAM, "NETWORK": NETWORK, "ENTITLEMENTS": ENTITLEMENTS, "HARDENED": HARDENED}


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
