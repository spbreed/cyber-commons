# Control-intent attestation for agents and MCP servers

Eleven skills that turn "we enforce least privilege" from a sentence in a
document into a signed statement about a specific deployment — plus a working
analyser for the part of it that can be done from source alone, and the results
of running that analyser against ten widely-deployed open-source repositories.

Taught in **[B2.13](../notebooks/B2.13.ipynb)**.

## The distinction the whole thing rests on

**Control intent** is what a codebase shows its authors meant to build: an
imported sandbox, a validated audience claim, a provenance tag. It is
establishable from source.

**Control enforcement** is whether the control holds at runtime. It is not.

So the analyser here never emits `PASS`. Its strongest verdict is
`INTENT_EVIDENCED`, and two controls are capped lower still.

## The eleven skills

In [`skills/attestation/`](../../skills/attestation). One resolver, nine
collectors split along evidence-source boundaries, one signer.

| Skill | Control | Confidence |
|---|---|---|
| `deployment-inventory-resolver` | all — produces the join key | — |
| `agent-code-surface-analyzer` | static basis for 1, 2, 5 | static |
| `iam-least-privilege-verifier` | 1 default-deny | **HIGH** |
| `aws-runtime-posture-collector` | 1, 2 runtime posture | evidence only |
| `sandbox-egress-verifier` | 2 no-egress sandbox | **PARTIAL, capped** |
| `identity-chain-verifier` | 3 identity and OBO | **HIGH** |
| `llm-gateway-guardrail-verifier` | 4 gateway and guardrails | HIGH *if* egress is enforced below the app |
| `input-injection-screening-verifier` | 5 injection screening | **PARTIAL, capped** |
| `risk-registry-integrator` | cross-cutting inherited risk | — |
| `entitlement-overprivilege-analyzer` | 1, 3 over-privilege | — |
| `attestation-signer-lifecycle` | all — the artefact | — |

They are separate because each needs different API clients, and because a single
mega-skill produces context bloat and verdicts nobody reads. `deployment_id` is
the join key that stitches repo, image, role, workload identity, gateway route,
guardrail and downstream services into one evaluable unit.

### Why two controls are capped

**C2, no-egress sandbox.** You can prove a sandbox is misconfigured. You cannot
prove the negative — network isolation has documented bypass paths, DNS being
the one that has actually been used for interactive command-and-control against
a major managed sandbox. `PASS` is not a permitted value.

**C5, injection screening.** You can verify a detector exists on the path and
record its class. Published defences that hold static attacks below a few
percent have been driven back above 95% success by adaptive, search-based
attacks. Record the detector class; do not assert protection.

A tool that reports `PASS` on either is not being generous, it is being wrong —
and a signed overstatement is worse than no attestation at all.

## Running it

```bash
python3 labs/attestation/control_intent.py <repo> [<repo> ...]
python3 labs/attestation/control_intent.py --corpus ~/clones --out results.json
```

Standard library only, deterministic: the same commit produces the same
attestation byte for byte, which is what makes drift detection mean anything.

## What it found on ten real repositories

Cloned at HEAD: the five most-deployed open-source MCP repositories and five
most-used agent frameworks. Full output in
[`oss-corpus-results.json`](oss-corpus-results.json).

```
repository                          kind    files  tools sinks  C1   C2   C3   C4   C5
awslabs_mcp                         mcp      2616    140     5  INT PART  INT  INT PART
crewAIInc_crewAI                    agent    2105     35     5  INT PART  INT  INT PART
github_github-mcp-server            mcp       258     41     3  INT PART  INT  INT PART
langchain-ai_langchain              agent    2673     99     5  INT PART  INT  INT PART
langchain-ai_langgraph              agent     538     20     4  INT    -  INT  INT PART
microsoft_autogen                   agent     707     49     5  INT PART  INT  INT PART
modelcontextprotocol_python-sdk     mcp       894    710     4  INT PART  INT  INT PART
modelcontextprotocol_servers        mcp       100      9     3  INT    -  INT  INT    -
modelcontextprotocol_typescript-sdk mcp       957     58     2  INT    -  INT  INT PART
openai_openai-agents-python         agent     998    182     5  INT PART  INT  INT PART
```

50 control evaluations: **30 INTENT_EVIDENCED, 16 PARTIAL, 4 NO_INTENT_FOUND,
0 PASS.**

Three findings worth more than the table:

1. **`github/github-mcp-server` ships no MCP tool annotations at all**, across
   41 tool declaration sites. The specification says annotations are hints
   rather than guarantees, and that an *unannotated* tool must be assumed
   `destructiveHint: true` and `openWorldHint: true`. Every one of those sites
   inherits that pessimistic default. Four of the five MCP repositories do use
   annotations — which is what makes the exception legible.

2. **The reference server collection has no sandbox and no injection-screening
   intent.** `modelcontextprotocol/servers` is what people copy from, and
   neither control appears in it. That is a reasonable choice for reference
   code and a bad inheritance for whatever is built on top.

3. **Every C2 and C5 verdict is capped**, not because the evidence was thin but
   because those claims are not provable. Sixteen of fifty evaluations are
   PARTIAL by rule.

## What this does not do

The analyser covers the **static** half. Seven of the eleven skills need a live
deployment — IAM usage data, network reachability, SPIFFE registration entries,
guardrail attachment, the risk register. Those emit `UNKNOWN` here rather than a
guess, which is the same discipline the skills themselves require: a missing
verdict is not a pass, and a relying party must **fail closed** on a missing
attestation, because a signed file can be deleted and absence is not evidence.
