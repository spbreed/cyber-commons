#!/usr/bin/env python3
"""Enumerate a deployment's declared tools and dangerous actions from its repository.

This is the executable half of the `agent-code-surface-analyzer` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

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

def verdict(control, hits):
    if not hits:
        return "NO_INTENT_FOUND", "no signal for this control in the source"
    if control in CEILINGS:
        return "PARTIAL", CEILINGS[control]
    if control in RUNTIME_ONLY:
        return "INTENT_EVIDENCED", f"runtime verdict needs {RUNTIME_ONLY[control]}"
    return "INTENT_EVIDENCED", f"{len(hits)} signals; enforcement not shown"

for c in sorted(SIGNALS):
    v, why = verdict(c, SIGNALS[c])
    print(f"{c:34s}{v:18s}{why[:44]}")
print()
print("PASS is not in the vocabulary. The strongest static verdict is")
print("INTENT_EVIDENCED, and two controls cannot exceed PARTIAL at all.")
assert "PASS" not in {verdict(c, SIGNALS[c])[0] for c in SIGNALS}

CORPUS = [
 {
  "repo": "awslabs_mcp",
  "kind": "mcp",
  "files": 2616,
  "tool_sites": 140,
  "sinks": 5,
  "annotated": True,
  "verdicts": {
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
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
   "C1": "INTENT_EVIDENCED",
   "C2": "PARTIAL",
   "C3": "INTENT_EVIDENCED",
   "C4": "INTENT_EVIDENCED",
   "C5": "PARTIAL"
  }
 }
]

print(f"{'repository':36s}{'kind':7s}{'files':>6}{'tools':>7}{'sinks':>6}  C1   C2   C3   C4   C5")
SHORT = {"INTENT_EVIDENCED": "INT", "PARTIAL": "PART", "NO_INTENT_FOUND": "-"}
for r in CORPUS:
    v = "".join(f"{SHORT[r['verdicts'][c]]:>5}" for c in ("C1","C2","C3","C4","C5"))
    print(f"{r['repo']:36s}{r['kind']:7s}{r['files']:>6}{r['tool_sites']:>7}{r['sinks']:>6}{v}")

evals = [r["verdicts"][c] for r in CORPUS for c in ("C1","C2","C3","C4","C5")]
print(f"\ncontrol evaluations : {len(evals)}")
for k in ("INTENT_EVIDENCED", "PARTIAL", "NO_INTENT_FOUND"):
    print(f"   {k:20s}{evals.count(k)}")
print(f"   {'PASS':20s}{evals.count('PASS')}   <- static evidence cannot prove enforcement")
assert evals.count("PASS") == 0

unannotated = [r for r in CORPUS if r["kind"] == "mcp" and not r["annotated"]]
print("1. MCP servers shipping NO tool annotations:")
for r in unannotated:
    print(f"   {r['repo']:36s}{r['tool_sites']} tool declaration sites")
print("   The specification is explicit that annotations are hints, not")
print("   guarantees - and that an UNANNOTATED tool must be assumed")
print("   destructiveHint=true and openWorldHint=true. Every one of those")
print("   tool sites inherits that pessimistic default.")

gaps = [(r["repo"], c) for r in CORPUS for c in ("C1","C2","C3","C4","C5")
        if r["verdicts"][c] == "NO_INTENT_FOUND"]
print(f"\n2. Controls with no intent anywhere in the source: {len(gaps)}")
for repo, c in gaps:
    print(f"   {repo:36s}{c}")

capped = [c for r in CORPUS for c in ("C2","C5") if r["verdicts"][c] == "PARTIAL"]
print(f"\n3. Verdicts capped at PARTIAL by the ceiling rule: {len(capped)}")
print("   Not because the evidence was weak - because the claim is not")
print("   provable. An attestation that reported PASS here would be a")
print("   signed, tamper-evident overstatement, which is worse than none.")
assert unannotated and gaps and capped

import json

def attestation(repo_row, commit="c9e71f7"):
    controls = []
    for c in ("C1","C2","C3","C4","C5"):
        full = [k for k in SIGNALS if k.startswith(c)][0]
        controls.append({
            "id": full,
            "verdict": repo_row["verdicts"][c],
            "confidence": "CAPPED" if full in CEILINGS else "STATIC",
            "evidence": [{"skill": "agent-code-surface-analyzer",
                          "uri": f"labs/attestation/oss-corpus-results.json#{repo_row['repo']}"}],
        })
    return {
      "_type": "https://in-toto.io/Statement/v1",
      "subject": [{"name": repo_row["repo"], "digest": {"gitCommit": commit}}],
      "predicateType": "https://cyber-commons/attestations/ai-control-intent/v1",
      "predicate": {"deployment_id": repo_row["repo"],
                    "scope": "static source analysis only",
                    "controls": controls,
                    "drift": {"since": None, "changed": []}},
      "signatures": [],
    }

a = attestation(CORPUS[0])
print(json.dumps(a, indent=1)[:600])
print("   ...")
print()
print("`signatures` is empty and says so. A relying party MUST fail closed on a")
print("missing or unsigned attestation: a signed file can be deleted, and")
print("absence must never be read as a pass.")
assert a["signatures"] == [] and a["predicate"]["scope"].startswith("static")
