# Track C2 — The AI SDLC — an Agentic AppSec Pipeline, Before and After Deploy

**Function C · Application Security with an AI SDLC**  
*The secure development lifecycle rebuilt around agents — and the harnesses that test CyberTravels' own agentic platform: SAST, DAST, triage, code fix, skills and harness evaluation.*

**Job titles:** AppSec Engineer, Product Security Engineer, Secure Code Reviewer

**What changes:** The SDLC split into what runs before a deploy and what runs after, then one lesson per stage of an agentic AppSec pipeline — audit, supply chain, dynamic validation, triage, remediation, attestation. 15 lessons.

**Autonomy focus:** Triage reaches L2.5 early; merge authority stays L2 far longer than people expect.

**Deliverable:** A five-phase AppSec pipeline running as a CI gate, with confirmed-by-exploitation severity and published precision and escape metrics.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### C2.0 — The AI SDLC: before and after deploy

- **Risk** — A security pipeline built as if it were exempt from the risks it exists to find.
- **Control** — Build the pipeline and the harness as one system, and hold both to the same evidence standard.
- **Lab** — Run a real LLM loop against a CyberTravels finding, then add the verifier and watch the same loop refuse what it just accepted.
- **Tools** — `Claude Haiku 4.5`

**Run it** — Run a real LLM loop against a CyberTravels finding, then add the verifier and watch the same loop refuse what it just accepted.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.0

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-0-the-ai-sdlc
#         (Claude Code and Copilot: /c2-0-the-ai-sdlc · Cursor: type / and
#         search · Codex: $c2-0-the-ai-sdlc). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.0
```

---

### C2.1 — Building a security harness

- **Risk** — A harness whose verifier is the model agreeing with itself does not fail loudly. It succeeds incorrectly, files a clean trace, and the bug is found by whoever merged the patch.
- **Control** — An independent verifier, and a budget that stops the loop when it cannot pass.
- **Lab** — Run the same loop twice — once with no verifier, once with one.

**Run it** — Run the same loop twice — once with no verifier, once with one.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.1

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-1-building-a-security-harness
#         (Claude Code and Copilot: /c2-1-building-a-security-harness · Cursor: type / and
#         search · Codex: $c2-1-building-a-security-harness). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.1
```

---

### C2.2 — Threat modelling

- **Risk** — Threat models are written once, by hand, against a system that has since changed.
- **Control** — Stage 5: derive assets, entry points and attack vectors mechanically from the synthesised map.
- **Lab** — Turn an architecture map into a ranked threat model, then diff it after one entry point is added.
- **Tools** — `OWASP Threat Dragon`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Turn an architecture map into a ranked threat model, then diff it after one entry point is added.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.2

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-2-threat-modelling
#         (Claude Code and Copilot: /c2-2-threat-modelling · Cursor: type / and
#         search · Codex: $c2-2-threat-modelling). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.2
```

---

### C2.3 — SAST: rules, then a model

- **Risk** — Pattern matching floods the queue; the false-positive rate is what actually changed.
- **Control** — Stage 7: deterministic rules for what rules do well, model reasoning for what rules cannot express.
- **Lab** — Score grep, taint rules and model review against the same corpus, then combine them behind a confidence gate.
- **Tools** — `OpenGrep`, `Semgrep OSS`, `CodeQL`
- **Open-weight models** — `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Score grep, taint rules and model review against the same corpus, then combine them behind a confidence gate.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.3

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-3-sast
#         (Claude Code and Copilot: /c2-3-sast · Cursor: type / and
#         search · Codex: $c2-3-sast). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.3
```

---

### C2.4 — Removing duplicates and checking findings

- **Risk** — Parallel analysis tracks report the same bug three times, and some of those bugs do not exist.
- **Control** — Stages 8–9: consolidate overlapping findings, then cross-reference each one against syntax and imports to weed out hallucinations.
- **Lab** — Deduplicate findings across three analysis tracks, then verify each against the AST and drop the ones that reference code that is not there.
- **Tools** — `OpenGrep`, `tree-sitter`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Deduplicate findings across three analysis tracks, then verify each against the AST and drop the ones that reference code that is not there.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.4

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-4-removing-duplicates-and-checking
#         (Claude Code and Copilot: /c2-4-removing-duplicates-and-checking · Cursor: type / and
#         search · Codex: $c2-4-removing-duplicates-and-checking). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.4
```

---

### C2.5 — Reachability and dead code

- **Risk** — A finding in dead code costs the same to triage as one on the login path.
- **Control** — Stage 10: decide whether an external caller can actually reach the sink before anyone is paged.
- **Lab** — Build a call graph from entry points and partition findings into reachable, unreachable and unknown.
- **Tools** — `CodeQL`, `tree-sitter`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Build a call graph from entry points and partition findings into reachable, unreachable and unknown.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.5

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-5-reachability-and-dead-code
#         (Claude Code and Copilot: /c2-5-reachability-and-dead-code · Cursor: type / and
#         search · Codex: $c2-5-reachability-and-dead-code). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.5
```

---

### C2.6 — A safe copy to test in

- **Risk** — Dynamic testing is run against staging, so a destructive probe becomes an incident.
- **Control** — Stage 11: replicate the application in an isolated, disposable runtime with no path to production.
- **Lab** — Stand up an isolated replica, prove egress and credential isolation, and show what a destructive probe touches.
- **Tools** — `Docker`, `gVisor`, `Cilium`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Stand up an isolated replica, prove egress and credential isolation, and show what a destructive probe touches.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.6

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-6-a-safe-copy-to-test-in
#         (Claude Code and Copilot: /c2-6-a-safe-copy-to-test-in · Cursor: type / and
#         search · Codex: $c2-6-a-safe-copy-to-test-in). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.6
```

---

### C2.7 — Supply chain and dependencies

- **Risk** — A clean dependency scan on an estate carrying an undeclared third-party binary reads as evidence of safety, and is evidence of nothing but the manifest's contents.
- **Control** — Reconcile the SBOM against what is on disk, then recover strings, imports and egress from the compiled artefact that no SBOM entry covers.
- **Lab** — Scan an SBOM, then decompile the closed-source library it never mentions.

**Run it** — Scan an SBOM, then decompile the closed-source library it never mentions.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.7

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-7-supply-chain-and-dependencies
#         (Claude Code and Copilot: /c2-7-supply-chain-and-dependencies · Cursor: type / and
#         search · Codex: $c2-7-supply-chain-and-dependencies). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.7
```

---

### C2.8 — Dynamic testing (DAST)

- **Risk** — A SAST finding is a hypothesis, and hypotheses get argued about instead of fixed.
- **Control** — Stage 12: generate and run an actual exploit against the sandbox, so the finding is confirmed or dropped.
- **Lab** — Turn static findings into executable probes against the replica and separate confirmed from unconfirmed.
- **Tools** — `OWASP ZAP`, `Nuclei`
- **Open-weight models** — `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Turn static findings into executable probes against the replica and separate confirmed from unconfirmed.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.8

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-8-dynamic-testing-dast
#         (Claude Code and Copilot: /c2-8-dynamic-testing-dast · Cursor: type / and
#         search · Codex: $c2-8-dynamic-testing-dast). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.8
```

---

### C2.9 — Chaining exploits

- **Risk** — Three medium findings are triaged as three mediums, and nobody notices they compose.
- **Control** — Stage 13: combine validated findings into multi-step sequences and score the chain, not the links.
- **Lab** — Chain individually-medium findings into a critical path and show the severity the chain earns.
- **Tools** — `OWASP ZAP`
- **Open-weight models** — `Kimi K2`
- **Frontier models** — `Claude Opus 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Chain individually-medium findings into a critical path and show the severity the chain earns.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.9

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-9-chaining-exploits
#         (Claude Code and Copilot: /c2-9-chaining-exploits · Cursor: type / and
#         search · Codex: $c2-9-chaining-exploits). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.9
```

---

### C2.10 — Pentesting with agents

- **Risk** — Payload suggestions instead of attack chains — and an offensive loop with no hard scope enforcement, which is an incident with a project plan.
- **Control** — Full target context before it swings, and scope enforced at the network layer rather than by a politeness clause in the prompt.
- **Lab** — Drive a planner/executor pair against a local target and watch the scope guard refuse an out-of-scope host before the request leaves.
- **Tools** — `CAI`, `Metasploit`, `Firecracker`
- **Open-weight models** — `Kimi K2`, `GLM-4.6`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Drive a planner/executor pair against a local target and watch the scope guard refuse an out-of-scope host before the request leaves.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.10

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-10-pentesting-with-agents
#         (Claude Code and Copilot: /c2-10-pentesting-with-agents · Cursor: type / and
#         search · Codex: $c2-10-pentesting-with-agents). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.10
```

---

### C2.11 — White-box pentest

- **Risk** — Full source produces a finding list nobody can act on, because presence is reported where reachability was needed.
- **Control** — Every candidate carries the path that reaches it and the authorisation predicate on that path; unreachable sinks are reported as unreachable rather than dropped.
- **Lab** — Enumerate paths from four entry points in the CyberTravels tree and separate reachable sinks from present ones.
- **Tools** — `Semgrep`

**Run it** — Enumerate paths from four entry points in the CyberTravels tree and separate reachable sinks from present ones.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.11

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-11-white-box-pentest
#         (Claude Code and Copilot: /c2-11-white-box-pentest · Cursor: type / and
#         search · Codex: $c2-11-white-box-pentest). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.11
```

---

### C2.12 — Black-box pentest

- **Risk** — An agent narrates a confident architecture from status codes, and the report is fiction that reads like findings.
- **Control** — Every claim is labelled observed or inferred, with the evidence that supports it, and inferences never carry a severity.
- **Lab** — Score twelve claims from an external probe run and see which survive the observed/inferred split.
- **Tools** — `Nuclei`

**Run it** — Score twelve claims from an external probe run and see which survive the observed/inferred split.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.12

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-12-black-box-pentest
#         (Claude Code and Copilot: /c2-12-black-box-pentest · Cursor: type / and
#         search · Codex: $c2-12-black-box-pentest). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.12
```

---

### C2.13 — Grey-box pentest

- **Risk** — Object-level authorisation is assumed correct because the endpoint list was covered, and BOLA lives in the cells nobody enumerated.
- **Control** — A roles-by-objects-by-verbs matrix with every cell marked tested, assumed or unreachable, and the assumed cells ranked by blast radius.
- **Lab** — Fill the matrix for CyberTravels with three roles and find the untested cells that matter.
- **Tools** — `OpenAPI`

**Run it** — Fill the matrix for CyberTravels with three roles and find the untested cells that matter.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.13

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-13-grey-box-pentest
#         (Claude Code and Copilot: /c2-13-grey-box-pentest · Cursor: type / and
#         search · Codex: $c2-13-grey-box-pentest). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.13
```

---

### C2.14 — Bonus: safety controls for an attacking agent

- **Risk** — The offensive agent is the least supervised and most capable thing in the estate, and its own traffic looks exactly like an attack.
- **Control** — A preflight that refuses to start the engagement until every control is present, and tells the SOC what to expect.
- **Lab** — Run the preflight against two engagement configurations and read why one of them cannot start.

**Run it** — Run the preflight against two engagement configurations and read why one of them cannot start.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.14

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-14-safety-controls-for-an-attacking-agent
#         (Claude Code and Copilot: /c2-14-safety-controls-for-an-attacking-agent · Cursor: type / and
#         search · Codex: $c2-14-safety-controls-for-an-attacking-agent). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.14
```

---

### C2.15 — Severity, triage and reports

- **Risk** — Severity is a label copied from the rule, so the queue is ordered by something that predicts nothing.
- **Control** — Stage 15: calibrate severity from sandbox evidence, then report per-stage economics rather than a finding count.
- **Lab** — Recalculate severity from confirmed exploitation and reachability, then produce the per-stage escape economics.
- **Tools** — `OpenGrep`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Recalculate severity from confirmed exploitation and reachability, then produce the per-stage escape economics.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.15

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-15-severity
#         (Claude Code and Copilot: /c2-15-severity · Cursor: type / and
#         search · Codex: $c2-15-severity). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.15
```

---

### C2.16 — Proving a fix before merge

- **Risk** — A patch that silences the scanner is indistinguishable from a patch that fixes the bug.
- **Control** — Stage 14: generate the fix, re-run the exploit against the patched build, and require a regression test.
- **Lab** — Validate four candidate patches on three axes and show which of them only made the scanner green.
- **Tools** — `Semgrep OSS`, `pytest`
- **Open-weight models** — `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Validate four candidate patches on three axes and show which of them only made the scanner green.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.16

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-16-proving-a-fix-before-merge
#         (Claude Code and Copilot: /c2-16-proving-a-fix-before-merge · Cursor: type / and
#         search · Codex: $c2-16-proving-a-fix-before-merge). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.16
```

---

### C2.17 — Cutting false positives with context

- **Risk** — The model is given the repository and asked to be thorough, so the relevant line falls out of the window.
- **Control** — Slice on the source-sink path, not on distance: the smallest context that still supports a severity decision.
- **Lab** — Compare four context strategies against one bug and measure which are decidable and at what size.
- **Tools** — `tree-sitter`
- **Open-weight models** — `GLM-4.6`, `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Compare four context strategies against one bug and measure which are decidable and at what size.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.17

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-17-cutting-false-positives-with-context
#         (Claude Code and Copilot: /c2-17-cutting-false-positives-with-context · Cursor: type / and
#         search · Codex: $c2-17-cutting-false-positives-with-context). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.17
```

---

### C2.18 — Attesting agents and MCP servers

- **Risk** — Control claims are asserted in a spreadsheet and never bound to a deployment. Nobody can say which repo, image, role, identity, gateway and guardrail the claim was about, so it cannot be re-checked when any of them change.
- **Control** — Eleven skills scoped to one deployment_id, emitting an in-toto/DSSE attestation whose predicate carries per-control verdicts, evidence URIs, framework mappings and drift — with sandbox-egress and injection-screening capped at PARTIAL because their claims are not provable.
- **Lab** — Run the control-intent analyser over ten real agent and MCP repositories and read the attestation it produces for each.
- **Tools** — `in-toto`, `Sigstore`, `OSCAL`, `OPA`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Run the control-intent analyser over ten real agent and MCP repositories and read the attestation it produces for each.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.18

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-18-attesting-agents-and-mcp-servers
#         (Claude Code and Copilot: /c2-18-attesting-agents-and-mcp-servers · Cursor: type / and
#         search · Codex: $c2-18-attesting-agents-and-mcp-servers). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.18
```

---

### C2.19 — Bonus: Google Mantis in production

- **Risk** — A reference implementation is adopted as a product, and its outputs are trusted without an eval.
- **Control** — Map Mantis's stages onto the pipeline you built, then score it with your own held-out key before trusting it.
- **Lab** — Map Mantis onto the 15 stages, parse its two output shapes, and score a sample against a held-out key.
- **Tools** — `Google Mantis`, `OpenGrep`
- **Open-weight models** — `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Map Mantis onto the 15 stages, parse its two output shapes, and score a sample against a held-out key.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons C2.19

# --- 3 · in your agent, open this folder and pick the skill:
#         c2-19-google-mantis-in-production
#         (Claude Code and Copilot: /c2-19-google-mantis-in-production · Cursor: type / and
#         search · Codex: $c2-19-google-mantis-in-production). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.19
```

---
