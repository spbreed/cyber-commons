#!/usr/bin/env python3
"""Filter findings by whether the vulnerable path is reachable, and record what reachability analysis cannot decide.

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
    python3 skills/appsec/appsec-vuln-audit/scripts/appsec_vuln_audit.py

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
SOURCE = '''
import handlers_registry

def http_get_report(request):
    """ENTRY: GET /reports"""
    return load_report(request.args["id"])

def http_health(request):
    """ENTRY: GET /health"""
    return "ok"

def load_report(report_id):
    return DB.execute("SELECT * FROM reports WHERE id=" + report_id)

def legacy_export(report_id):
    # nothing calls this any more; kept for a migration that finished in 2023
    return DB.execute("SELECT * FROM reports WHERE id=" + report_id)

def debug_dump(name):
    return open("/tmp/" + name).read()

def dispatch(request):
    """ENTRY: dynamic dispatch — the framework resolves the handler at runtime"""
    handler = handlers_registry.lookup(request.path)
    return handler(request)
'''

SINKS = {"load_report": ("CWE-89", "DB.execute"),
         "legacy_export": ("CWE-89", "DB.execute"),
         "debug_dump":   ("CWE-22", "open")}

ROUTING = {
 "reachable":   ("page / block the merge", "confirmed exploit path — goes to Phase 4"),
 "unknown":     ("queue for dynamic validation", "Phase 4 decides it empirically"),
 "unreachable": ("record, do not page", "revisit only if an entry point is added"),
}

FILE_OF = {"load_report": "src/data/reports.py", "legacy_export": "src/data/legacy.py",
           "debug_dump": "src/util/debug.py"}

MISSING = {"CWE-89": "parameterised query", "CWE-22": "path normalisation"}

# The same three defects, as three analysers actually report them.
ANALYSER_WORDING = {
 "grep rules":  "possible {cwe} near {unit}",
 "taint rules": "tainted input reaches {unit} ({cwe})",
 "model review":"{unit} appears to pass user input to a dangerous sink; likely {cwe}",
}

# Verbatim output from Moonlight-16B-A3B on Kaggle, 2026-08-17.
# Not a paraphrase and not a stand-in: this is what the model emitted.
MODEL_OUTPUT = '''{"findings": [{"id": "F-01", "cwe": "CWE-89", "file": "report_api.py",
"line": 22, "unit": "get_report",
"evidence": "open('/var/reports/' + request.args['name'])",
"missing_control": "str", "occurrences": 1, "verdict": "confirmed",
"verdict_reason": "str", "feasible": true, "confidence": 0.0}],
"dropped": [], "counts": {"raw": 0, "deduped": 0, "verified": 0, "feasible": 0}}'''
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n{json.dumps(value, indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"SOURCE": SOURCE, "SINKS": SINKS, "ROUTING": ROUTING, "FILE_OF": FILE_OF, "MISSING": MISSING, "ANALYSER_WORDING": ANALYSER_WORDING, "MODEL_OUTPUT": MODEL_OUTPUT}


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
