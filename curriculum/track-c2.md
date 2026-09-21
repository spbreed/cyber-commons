# Track C2 — The AI SDLC — an Agentic AppSec Pipeline, Before and After Deploy

**Function C · Application Security with an AI SDLC**  
*The secure development lifecycle rebuilt around agents — and the harnesses that test CyberTravels' own agentic platform: SAST, DAST, triage, code fix, skills and harness evaluation.*

**Job titles:** AppSec Engineer, Product Security Engineer, Secure Code Reviewer

**What changes:** The SDLC split into what runs before a deploy and what runs after, then one lesson per stage of an agentic AppSec pipeline — audit, supply chain, dynamic validation, triage, remediation, attestation. 15 lessons.

**Autonomy focus:** Triage reaches L2.5 early; merge authority stays L2 far longer than people expect.

**Deliverable:** A five-phase AppSec pipeline running as a CI gate, with confirmed-by-exploitation severity and published precision and escape metrics.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### C2.0 — The AI SDLC — what runs before a deploy, and what runs after

- **Risk** — A security pipeline built as if it were exempt from the risks it exists to find.
- **Control** — Build the pipeline and the harness as one system, and hold both to the same evidence standard.
- **Lab** — Run a real LLM loop against a CyberTravels finding, then add the verifier and watch the same loop refuse what it just accepted.
- **Tools** — `Claude Haiku 4.5`, `Qwen2.5-7B`

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

### C2.1 — What building a harness means in security engineering

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
#         c2-1-what-building-a-harness-means-in
#         (Claude Code and Copilot: /c2-1-what-building-a-harness-means-in · Cursor: type / and
#         search · Codex: $c2-1-what-building-a-harness-means-in). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.1
```

---

### C2.2 — Threat modelling from what the estate already knows

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
#         c2-2-threat-modelling-from-what-the-estate
#         (Claude Code and Copilot: /c2-2-threat-modelling-from-what-the-estate · Cursor: type / and
#         search · Codex: $c2-2-threat-modelling-from-what-the-estate). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.2
```

---

### C2.3 — SAST for agentic code — deterministic Semgrep, then the model pass

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
#         c2-3-sast-for-agentic-code
#         (Claude Code and Copilot: /c2-3-sast-for-agentic-code · Cursor: type / and
#         search · Codex: $c2-3-sast-for-agentic-code). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.3
```

---

### C2.4 — Deduplication and contextual verification

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
#         c2-4-deduplication-and-contextual
#         (Claude Code and Copilot: /c2-4-deduplication-and-contextual · Cursor: type / and
#         search · Codex: $c2-4-deduplication-and-contextual). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.4
```

---

### C2.5 — Feasibility filtering, reachability and dead code

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
#         c2-5-feasibility-filtering
#         (Claude Code and Copilot: /c2-5-feasibility-filtering · Cursor: type / and
#         search · Codex: $c2-5-feasibility-filtering). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.5
```

---

### C2.6 — Sandbox replication

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
#         c2-6-sandbox-replication
#         (Claude Code and Copilot: /c2-6-sandbox-replication · Cursor: type / and
#         search · Codex: $c2-6-sandbox-replication). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.6
```

---

### C2.7 — Supply chain — SBOM, dependency vulnerabilities, and decompiling the libraries

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
#         c2-7-supply-chain
#         (Claude Code and Copilot: /c2-7-supply-chain · Cursor: type / and
#         search · Codex: $c2-7-supply-chain). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.7
```

---

### C2.8 — Dynamic exploitation (DAST)

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
#         c2-8-dynamic-exploitation-dast
#         (Claude Code and Copilot: /c2-8-dynamic-exploitation-dast · Cursor: type / and
#         search · Codex: $c2-8-dynamic-exploitation-dast). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.8
```

---

### C2.9 — Exploit chaining

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
#         c2-9-exploit-chaining
#         (Claude Code and Copilot: /c2-9-exploit-chaining · Cursor: type / and
#         search · Codex: $c2-9-exploit-chaining). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.9
```

---

### C2.10 — Agentic penetration testing — the loop, and who runs each turn

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
#         c2-10-agentic-penetration-testing
#         (Claude Code and Copilot: /c2-10-agentic-penetration-testing · Cursor: type / and
#         search · Codex: $c2-10-agentic-penetration-testing). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.10
```

---

### C2.11 — White-box agentic pentest — the source, and what it lets you prove

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
#         c2-11-white-box-agentic-pentest
#         (Claude Code and Copilot: /c2-11-white-box-agentic-pentest · Cursor: type / and
#         search · Codex: $c2-11-white-box-agentic-pentest). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.11
```

---

### C2.12 — Black-box agentic pentest — inference, and refusing to report it as fact

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
#         c2-12-black-box-agentic-pentest
#         (Claude Code and Copilot: /c2-12-black-box-agentic-pentest · Cursor: type / and
#         search · Codex: $c2-12-black-box-agentic-pentest). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.12
```

---

### C2.13 — Grey-box agentic pentest — one credential per role, and the matrix it fills

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
#         c2-13-grey-box-agentic-pentest
#         (Claude Code and Copilot: /c2-13-grey-box-agentic-pentest · Cursor: type / and
#         search · Codex: $c2-13-grey-box-agentic-pentest). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.13
```

---

### C2.14 — Bonus — testing safely: the controls an offensive agent runs inside

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
#         c2-14-bonus
#         (Claude Code and Copilot: /c2-14-bonus · Cursor: type / and
#         search · Codex: $c2-14-bonus). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.14
```

---

### C2.15 — Severity calibration, triaging and reporting

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
#         c2-15-severity-calibration
#         (Claude Code and Copilot: /c2-15-severity-calibration · Cursor: type / and
#         search · Codex: $c2-15-severity-calibration). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.15
```

---

### C2.16 — Remediation engineering — proven in a sandbox before the merge request

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
#         c2-16-remediation-engineering
#         (Claude Code and Copilot: /c2-16-remediation-engineering · Cursor: type / and
#         search · Codex: $c2-16-remediation-engineering). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.16
```

---

### C2.17 — Context engineering — cutting the false positives

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
#         c2-17-context-engineering
#         (Claude Code and Copilot: /c2-17-context-engineering · Cursor: type / and
#         search · Codex: $c2-17-context-engineering). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.17
```

---

### C2.18 — Agentic AI in the pipeline — attesting control intent for agents and MCP servers

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
#         c2-18-agentic-ai-in-the-pipeline
#         (Claude Code and Copilot: /c2-18-agentic-ai-in-the-pipeline · Cursor: type / and
#         search · Codex: $c2-18-agentic-ai-in-the-pipeline). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.18
```

---

### C2.19 — Bonus — Google Mantis, the pipeline in production

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
#         c2-19-bonus
#         (Claude Code and Copilot: /c2-19-bonus · Cursor: type / and
#         search · Codex: $c2-19-bonus). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py C2.19
```

---
