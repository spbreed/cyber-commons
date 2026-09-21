#!/usr/bin/env python3
"""Enumerate a deployment's declared tools and dangerous actions from its repository.

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
    python3 skills/attestation/agent-code-surface-analyzer/scripts/agent_code_surface_analyzer.py

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
SIGNALS = {
 "C1_default_deny_least_privilege": ["default_deny", "allowlist", "policy engine",
                                     "authorisation check"],
 "C2_sandbox_no_egress":            ["isolation runtime", "kernel confinement",
                                     "network mode control"],
 "C3_identity_chain_obo":           ["workload identity", "delegation claim",
                                     "audience validation", "token exchange"],
 "C4_gateway_guardrails":           ["gateway", "guardrail", "egress policy"],
 "C5_injection_screening":          ["injection detector", "sanitisation",
                                     "provenance tagging"],
}

CEILINGS = {
 "C2_sandbox_no_egress": "absence of a covert channel is not provable from source",
 "C5_injection_screening": "detector presence is verifiable; robustness is not",
}

RUNTIME_ONLY = {
 "C1_default_deny_least_privilege": "observed usage and the effective role policy",
 "C4_gateway_guardrails": "reachability testing from the deployment network",
}

CORPUS = [
 {
  "repo": "awslabs_mcp",
  "kind": "mcp",
  "files": 2616,
  "tool_sites": 140,
  "sinks": 5,
  "annotated": True,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "crewAIInc_crewAI",
  "kind": "agent",
  "files": 2105,
  "tool_sites": 35,
  "sinks": 5,
  "annotated": False,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "github_github-mcp-server",
  "kind": "mcp",
  "files": 258,
  "tool_sites": 41,
  "sinks": 3,
  "annotated": False,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "langchain-ai_langchain",
  "kind": "agent",
  "files": 2673,
  "tool_sites": 99,
  "sinks": 5,
  "annotated": False,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "langchain-ai_langgraph",
  "kind": "agent",
  "files": 538,
  "tool_sites": 20,
  "sinks": 4,
  "annotated": False,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "NO_INTENT_FOUND",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "microsoft_autogen",
  "kind": "agent",
  "files": 707,
  "tool_sites": 49,
  "sinks": 5,
  "annotated": True,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "modelcontextprotocol_python-sdk",
  "kind": "mcp",
  "files": 894,
  "tool_sites": 710,
  "sinks": 4,
  "annotated": True,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "modelcontextprotocol_servers",
  "kind": "mcp",
  "files": 100,
  "tool_sites": 9,
  "sinks": 3,
  "annotated": True,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "NO_INTENT_FOUND",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "NO_INTENT_FOUND"
  }
 },
 {
  "repo": "modelcontextprotocol_typescript-sdk",
  "kind": "mcp",
  "files": 957,
  "tool_sites": 58,
  "sinks": 2,
  "annotated": True,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "NO_INTENT_FOUND",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 },
 {
  "repo": "openai_openai-agents-python",
  "kind": "agent",
  "files": 998,
  "tool_sites": 182,
  "sinks": 5,
  "annotated": False,
  "verdicts": {
   "D1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 }
]

SHORT = {"INTENT_EVIDENCED": "INT", "PARTIAL": "PART", "NO_INTENT_FOUND": "-"}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\n\n".join(
        f"### {name}\n\n```json\n"
        f"{json.dumps(jsonable(value), indent=2, default=str)}\n```"
        for name, value in FIXTURE.items())


FIXTURE = {"SIGNALS": SIGNALS, "CEILINGS": CEILINGS, "RUNTIME_ONLY": RUNTIME_ONLY, "CORPUS": CORPUS, "SHORT": SHORT}


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
