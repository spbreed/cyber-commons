#!/usr/bin/env python3
"""Map a published pipeline onto the stage model and score its output against a held-out key.

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
    python3 skills/appsec/reference-pipeline-scoring/scripts/reference_pipeline_scoring.py

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
STAGES = {
 1:  "historical parsing",        2:  "structural indexing",
 3:  "component summarisation",   4:  "architecture synthesis",
 5:  "threat modelling",          6:  "strategic planning",
 7:  "vulnerability auditing",    8:  "deduplication",
 9:  "contextual verification",  10:  "feasibility filtering",
 11: "sandbox replication",      12:  "dynamic exploitation",
 13: "exploit chaining",         14:  "remediation engineering",
 15: "severity calibration and reporting",
}

# Coverage as observed from the project's own documented outputs and skills.
MANTIS = {
 1:  ("yes",     "historical_learnings.jsonl is read on subsequent runs"),
 2:  ("partial", "operates over the agent's code-reading tools"),
 3:  ("partial", "context assembled per review target"),
 4:  ("no",      "assumes you supply the architecture context"),
 5:  ("partial", "review skills encode threat patterns rather than deriving them"),
 6:  ("no",      "you decide what to point it at"),
 7:  ("yes",     "the core: security-review skills emitting finding objects"),
 8:  ("partial", "findings are structured, so dedup is possible downstream"),
 9:  ("partial", "structured output aids verification; you still run the checks"),
 10: ("no",      "reachability is yours"),
 11: ("no",      "no sandbox — it is a review harness, not a DAST"),
 12: ("no",      "static review only"),
 13: ("no",      "no chaining"),
 14: ("partial", "can propose fixes; validation is yours (C2.9)"),
 15: ("partial", "emits severity; calibration against confirmation is yours"),
}

LEARNING_REQUIRED = ("title", "description", "history")

FINDING_REQUIRED  = ("title", "description", "severity", "file", "cwe")

SAMPLE = [
 # learning_entry — feeds stage 1 on the next run
 '{"type":"learning_entry","title":"owner filter built by concatenation",'
 '"description":"reports queries interpolate the owner parameter",'
 '"history":"introduced in c3d4e5f, fixed once in 2025 and reintroduced"}',
 # finding — feeds stages 8-10
 '{"type":"finding","title":"SQL injection in list_reports","severity":"high",'
 '"file":"src/data/reports.py","cwe":"CWE-89",'
 '"description":"owner is concatenated into the query string"}',
 # a learning entry missing the required history field
 '{"type":"learning_entry","title":"path join in docs",'
 '"description":"docs fetch joins user input"}',
 # a finding with a null field
 '{"type":"finding","title":"traversal","severity":"medium",'
 '"file":"src/data/docs.py","cwe":null,'
 '"description":"name is joined onto the base path"}',
 # not JSON at all
 'I found a SQL injection in the reports module.',
]

HELD_OUT = {
 "src/data/reports.py": "CWE-89",
 "src/data/docs.py":    "CWE-22",
 "src/web/handlers.py": "CWE-306",     # a finding Mantis did not report
}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"STAGES": STAGES, "MANTIS": MANTIS, "LEARNING_REQUIRED": LEARNING_REQUIRED, "FINDING_REQUIRED": FINDING_REQUIRED, "SAMPLE": SAMPLE, "HELD_OUT": HELD_OUT}


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
