# Track B2 — The AI SDLC: an Agentic AppSec Pipeline, Before and After Deploy

**Function B · Application Security with an AI SDLC**  
*The secure development lifecycle rebuilt around agents — and the harnesses that test CyberTravels' own agentic platform: SAST, DAST, triage, code fix, skills and harness evaluation.*

**Job titles:** AppSec Engineer, Product Security Engineer, Secure Code Reviewer

**What changes:** The SDLC split into what runs before a deploy and what runs after, then one lesson per stage of an agentic AppSec pipeline — audit, supply chain, dynamic validation, triage, remediation, attestation. 15 lessons.

**Autonomy focus:** Triage reaches L2.5 early; merge authority stays L2 far longer than people expect.

**Deliverable:** A five-phase AppSec pipeline running as a CI gate, with confirmed-by-exploitation severity and published precision and escape metrics.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### B2.0 — The AI SDLC — what runs before a deploy, and what runs after

`both directions`

- **Risk** — A security pipeline built as if it were exempt from the risks it exists to find.
- **Control** — Build the pipeline and the harness as one system, and hold both to the same evidence standard.
- **Lab** — Run a real LLM loop against a CyberTravels finding, then add the verifier and watch the same loop refuse what it just accepted.
- **Tools** — `Claude Haiku 4.5`, `Qwen2.5-7B`

**Run it** — Run a real LLM loop against a CyberTravels finding, then add the verifier and watch the same loop refuse what it just accepted.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.0   # run it headless and check it
```

*Expect:* The loop runs with a real model behind `ask()` — a labelled replay offline, a frontier or open-weight call when one is configured. Without a verifier it accepts whatever came back and reports `verified: None`. With the verifier the same model and prompt produce an accepted, parameterised line — and a plausible-looking answer that wraps the input in `escape()` is refused, because it is still concatenation.

---

### B2.1 — What building a harness means in security engineering

`both directions`

- **Risk** — A harness whose verifier is the model agreeing with itself does not fail loudly. It succeeds incorrectly, files a clean trace, and the bug is found by whoever merged the patch.
- **Control** — An independent verifier, and a budget that stops the loop when it cannot pass.
- **Lab** — Run the same loop twice — once with no verifier, once with one.

**Run it** — Run the same loop twice — once with no verifier, once with one.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.1   # run it headless and check it
```

*Expect:* Without a verifier the loop accepts whatever the model returned and reports verified: None. With one, the same model and prompt produce an accepted parameterised line, a too-narrow verifier is shown rejecting a correct fix, and an answer that wraps the input in escape() is refused because it is still concatenation.

---

### B2.2 — Threat modelling from what the estate already knows

`Security of AI`

- **Risk** — Threat models are written once, by hand, against a system that has since changed.
- **Control** — Stage 5: derive assets, entry points and attack vectors mechanically from the synthesised map.
- **Lab** — Turn an architecture map into a ranked threat model, then diff it after one entry point is added.
- **Tools** — `OWASP Threat Dragon`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Turn an architecture map into a ranked threat model, then diff it after one entry point is added.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.2   # run it headless and check it
```

*Expect:* The skill loads with its routing description and procedure, then derives twelve threats across all six STRIDE categories from five synthetic inputs, each carrying the evidence line that set its score. It emits a mermaid diagram marking the two trust-boundary crossings. Re-running against a hardened estate — same code, four different evidence inputs — keeps every row and drops the maximum severity from 11 to 1.

---

### B2.3 — Vulnerability auditing — deterministic Semgrep, then the model pass

`AI for Security`

- **Risk** — Pattern matching floods the queue; the false-positive rate is what actually changed.
- **Control** — Stage 7: deterministic rules for what rules do well, model reasoning for what rules cannot express.
- **Lab** — Score grep, taint rules and model review against the same corpus, then combine them behind a confidence gate.
- **Tools** — `OpenGrep`, `Semgrep OSS`, `CodeQL`
- **Open-weight models** — `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Score grep, taint rules and model review against the same corpus, then combine them behind a confidence gate.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b1-appsec
git apply injected-pr.diff       # a PR containing an instruction to the reviewer
python3 triage.py --candidates candidates.json --model $MODEL   # obeys it
python3 triage.py --candidates candidates.json --model $MODEL --tag-untrusted   # ignores it
```

*Expect:* The unprotected run emits the attacker's verdict; the tagged run does not.

---

### B2.4 — Deduplication and contextual verification

`AI for Security`

- **Risk** — Parallel analysis tracks report the same bug three times, and some of those bugs do not exist.
- **Control** — Stages 8–9: consolidate overlapping findings, then cross-reference each one against syntax and imports to weed out hallucinations.
- **Lab** — Deduplicate findings across three analysis tracks, then verify each against the AST and drop the ones that reference code that is not there.
- **Tools** — `OpenGrep`, `tree-sitter`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Deduplicate findings across three analysis tracks, then verify each against the AST and drop the ones that reference code that is not there.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install 'litellm[proxy]' && cd labs/shared
litellm --config litellm.config.yaml &   # llama executor, glm reasoner, kimi advisor
cd ../m0-agent-loop && MODEL=router python3 loop.py --task fix-tests --json | jq '.tokens'
python3 ../shared/spend_report.py --by-run
```

*Expect:* Per-run, per-tier spend attribution. Escalation happens only at decision points.

---

### B2.5 — Feasibility filtering, reachability and dead code

`AI for Security`

- **Risk** — A finding in dead code costs the same to triage as one on the login path.
- **Control** — Stage 10: decide whether an external caller can actually reach the sink before anyone is paged.
- **Lab** — Build a call graph from entry points and partition findings into reachable, unreachable and unknown.
- **Tools** — `CodeQL`, `tree-sitter`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Build a call graph from entry points and partition findings into reachable, unreachable and unknown.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a2-delegation
python3 subagent.py --depth 3 --parent-scope repo:read
python3 subagent.py --depth 3 --parent-scope repo:read --attempt-escalate
```

*Expect:* Recursion budget caps depth; the escalation attempt is refused by the token, not by a check.

---

### B2.6 — Sandbox replication

`Security of AI`

- **Risk** — Dynamic testing is run against staging, so a destructive probe becomes an incident.
- **Control** — Stage 11: replicate the application in an isolated, disposable runtime with no path to production.
- **Lab** — Stand up an isolated replica, prove egress and credential isolation, and show what a destructive probe touches.
- **Tools** — `Docker`, `gVisor`, `Cilium`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Stand up an isolated replica, prove egress and credential isolation, and show what a destructive probe touches.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop/traces
python3 ../classify_failure.py --trace divergence.jsonl
for t in *.jsonl; do echo -n "$t: "; python3 ../classify_failure.py --trace $t --quiet; done
```

*Expect:* Loop divergence, objective drift, reward hacking, silent truncation, tool thrash — one per trace.

---

### B2.7 — Supply chain — SBOM, dependency vulnerabilities, and decompiling the libraries

`both directions`

- **Risk** — A clean dependency scan on an estate carrying an undeclared third-party binary reads as evidence of safety, and is evidence of nothing but the manifest's contents.
- **Control** — Reconcile the SBOM against what is on disk, then recover strings, imports and egress from the compiled artefact that no SBOM entry covers.
- **Lab** — Scan an SBOM, then decompile the closed-source library it never mentions.

**Run it** — Scan an SBOM, then decompile the closed-source library it never mentions.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.7   # run it headless and check it

# --- the artefact is a real compiled class; this is how it was built ---
javac -d /tmp/vt skills/appsec/supply-chain-decompile/evidence/provenance/VendorTelemetry.java
```

*Expect:* Three of five declared components carry advisories, including Text4Shell in commons-text 1.9 — which only appears because the version comparison is numeric. Reconciliation finds one artefact on disk in no manifest; decompiling its constant pool recovers a hardcoded telemetry endpoint with the licence key folded into the same literal, an AES/ECB cipher spec, and network-egress and cryptography capabilities. unassessable_by_sbom: 1.

---

### B2.8 — Dynamic exploitation (DAST)

`AI for Security`

- **Risk** — A SAST finding is a hypothesis, and hypotheses get argued about instead of fixed.
- **Control** — Stage 12: generate and run an actual exploit against the sandbox, so the finding is confirmed or dropped.
- **Lab** — Turn static findings into executable probes against the replica and separate confirmed from unconfirmed.
- **Tools** — `OWASP ZAP`, `Nuclei`
- **Open-weight models** — `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Turn static findings into executable probes against the replica and separate confirmed from unconfirmed.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 evolve.py --generations 5 --sandbox docker --fitness pytest-pass-rate
python3 evolve.py --show-lineage   # what changed, what was kept, what was reverted
```

*Expect:* Only mutations the deterministic oracle confirms survive. Pin the fitness function — it is now the security control.

---

### B2.9 — Exploit chaining

`AI for Security`

- **Risk** — Three medium findings are triaged as three mediums, and nobody notices they compose.
- **Control** — Stage 13: combine validated findings into multi-step sequences and score the chain, not the links.
- **Lab** — Chain individually-medium findings into a critical path and show the severity the chain earns.
- **Tools** — `OWASP ZAP`
- **Open-weight models** — `Kimi K2`
- **Frontier models** — `Claude Opus 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Chain individually-medium findings into a critical path and show the severity the chain earns.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.9   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 loop.py --task fix-tests --json > run.json
python3 replay.py --trace run.json --assert-identical
```

*Expect:* Either it reproduces, or the tool names the field you failed to log. Anything you cannot replay you cannot investigate.

---

### B2.10 — Severity calibration, triaging and reporting

`AI for Security`

- **Risk** — Severity is a label copied from the rule, so the queue is ordered by something that predicts nothing.
- **Control** — Stage 15: calibrate severity from sandbox evidence, then report per-stage economics rather than a finding count.
- **Lab** — Recalculate severity from confirmed exploitation and reachability, then produce the per-stage escape economics.
- **Tools** — `OpenGrep`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Recalculate severity from confirmed exploitation and reachability, then produce the per-stage escape economics.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.10   # run it headless and check it
```

*Expect:* Three stand-in backbones are scored on the same corpus: the one with the best recall is not the one with the best cost per finding. A harness that couples to vendor output shapes fails outright on the third backbone, while the interface version substitutes in a single line and reports the recall, precision and cost deltas. A data-sovereignty column then removes the closed-weights option entirely.

---

### B2.11 — Remediation engineering — proven in a sandbox before the merge request

`AI for Security`

- **Risk** — A patch that silences the scanner is indistinguishable from a patch that fixes the bug.
- **Control** — Stage 14: generate the fix, re-run the exploit against the patched build, and require a regression test.
- **Lab** — Validate four candidate patches on three axes and show which of them only made the scanner green.
- **Tools** — `Semgrep OSS`, `pytest`
- **Open-weight models** — `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Validate four candidate patches on three axes and show which of them only made the scanner green.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.11.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.11   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b2-harness
python3 domain_harness.py --domain sast   --oracle reachability+test
python3 domain_harness.py --domain pentest --require-signed-scope
```

*Expect:* One skeleton runs all four domains unchanged. With each domain's own oracle every confirmed finding is real — precision 1.00 across sast, threat model, dast and pentest — and the pentest run refuses outright without a signed scope, because its blast radius is live action. Swapping in the model's own confidence as the oracle confirms all 12 candidates, 8 of which are real: precision 0.67 in every domain, invisible from inside the harness.

---

### B2.12 — Context engineering — cutting the false positives

`AI for Security`

- **Risk** — The model is given the repository and asked to be thorough, so the relevant line falls out of the window.
- **Control** — Slice on the source-sink path, not on distance: the smallest context that still supports a severity decision.
- **Lab** — Compare four context strategies against one bug and measure which are decidable and at what size.
- **Tools** — `tree-sitter`
- **Open-weight models** — `GLM-4.6`, `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Compare four context strategies against one bug and measure which are decidable and at what size.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.12.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.12   # run it headless and check it
```

*Expect:* The whole file is roughly 840 characters, the ±2 window about 200 and the path slice about 390. The ±2 window is not decidable because it lacks the signature; the ±6 window and the whole file are decidable but carry unrelated functions. The path slice is the smallest decidable context with zero unrelated functions, about 53% smaller than the whole file.

---

### B2.13 — Agentic AI in the pipeline — attesting control intent for agents and MCP servers

`Security of AI`

- **Risk** — Control claims are asserted in a spreadsheet and never bound to a deployment. Nobody can say which repo, image, role, identity, gateway and guardrail the claim was about, so it cannot be re-checked when any of them change.
- **Control** — Eleven skills scoped to one deployment_id, emitting an in-toto/DSSE attestation whose predicate carries per-control verdicts, evidence URIs, framework mappings and drift — with sandbox-egress and injection-screening capped at PARTIAL because their claims are not provable.
- **Lab** — Run the control-intent analyser over ten real agent and MCP repositories and read the attestation it produces for each.
- **Tools** — `in-toto`, `Sigstore`, `OSCAL`, `OPA`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Run the control-intent analyser over ten real agent and MCP repositories and read the attestation it produces for each.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.13.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.13   # run it headless and check it

# --- the full variant, against real repositories ---
python3 labs/attestation/control_intent.py --corpus /path/to/clones --out results.json
```

*Expect:* Five controls resolve to INTENT_EVIDENCED, PARTIAL or NO_INTENT_FOUND and never to PASS. Across ten real repositories and fifty control evaluations the analyser returns 30 INTENT_EVIDENCED, 16 PARTIAL, 4 NO_INTENT_FOUND and zero PASS — with one widely-deployed MCP server shipping no tool annotations at all, so all of its tool sites inherit the specification's destructive, open-world default.

---

### B2.14 — Bonus — Google Mantis, the pipeline in production

`AI for Security`

- **Risk** — A reference implementation is adopted as a product, and its outputs are trusted without an eval.
- **Control** — Map Mantis's stages onto the pipeline you built, then score it with your own held-out key before trusting it.
- **Lab** — Map Mantis onto the 15 stages, parse its two output shapes, and score a sample against a held-out key.
- **Tools** — `Google Mantis`, `OpenGrep`
- **Open-weight models** — `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Map Mantis onto the 15 stages, parse its two output shapes, and score a sample against a held-out key.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.13.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.13   # run it headless and check it
```

*Expect:* The stage map shows Mantis covering stage 7 strongly with a stage-1 learning loop, and not covering Phase 4 at all. Three of five sample outputs conform — one learning entry is missing the required `history` field, one finding has a null CWE, and one is prose. Scored against the held-out key, expert accuracy is below 1.0: one correct, one half credit for the null class, and one missed finding Mantis never reported. The learning entry then feeds the next run's risk zones.

---
