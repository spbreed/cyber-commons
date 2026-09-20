# Track F1 — Building the Governance Framework — Risk and Control

**Function F · AI Governance for Agentic Systems**  
*Governing autonomy rather than approving tools: the register, the obligations and the programme that keep CyberTravels defensible.*

**Job titles:** GRC Analyst, Risk Manager, Control Owner, Third-Party Risk Analyst, Internal Audit liaison

**What changes:** The register of every agent CyberTravels runs, risk-tiered by autonomy, data and blast radius, mapped to controls, with evidence that can be re-checked. 13 lessons.

**Autonomy focus:** You define the promotion criteria that let a workflow move from L2 to L2.5 — and the conditions that force it back down.

**Deliverable:** A risk-tiered agent register with mapped controls and one fully evidenced control assertion.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### F1.0 — Start here — what AI governance means

- **Risk** — A trustworthy-AI statement with no owner per property, so every property is somebody else's job.
- **Control** — One register, risk-tiered, with each property mapped to a control, an owner and evidence that can be re-checked.
- **Lab** — Take the seven properties and assign each an owner in your own organisation. The gaps are the programme.

**Run it** — Take the seven properties and assign each an owner in your own organisation. The gaps are the programme.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.0:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.0 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.0 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · a reading lesson: no skill to run. When you reach one
#         that does, this links them all into your agent. ---
python3 scripts/install_skills.py --all
```

---

### F1.1 — From framework control to key control indicator

- **Risk** — An annual review certifies nothing about a system that changed the week after it.
- **Control** — Continuous assurance; control effectiveness redefined for probabilistic systems.
- **Lab** — Change a prompt and show the control evidence going stale in real time.
- **Tools** — `promptfoo`

**Run it** — Change a prompt and show the control evidence going stale in real time.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.1:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.1 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.1 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/attestation/attestation-signer-lifecycle/scripts/attestation_signer_lifecycle.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.2 — Building the AI and agent inventory

- **Risk** — Shadow AI and shadow agents — the inventory is the control most orgs still lack.
- **Control** — Discovery, registration, ownership, risk tiering.
- **Lab** — Discover agents from gateway and identity telemetry; build the register.
- **Tools** — `agentgateway`, `SPIRE`

**Run it** — Discover agents from gateway and identity telemetry; build the register.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.2:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.2 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.2 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/attestation/deployment-inventory-resolver/scripts/deployment_inventory_resolver.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.3 — Risk tiering agentic use cases

- **Risk** — Tiering by model name instead of by what the thing can do.
- **Control** — Autonomy level × action class × data sensitivity.
- **Lab** — Tier ten real workflows and assign approval authority.

**Run it** — Tier ten real workflows and assign approval authority.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.3:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.3 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.3 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/grc/agentic-risk-tiering/scripts/agentic_risk_tiering.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.4 — Control mapping for agents

- **Risk** — Inventing new controls where an existing one applied to a new principal type.
- **Control** — Map identity, secrets, sandbox, eval and telemetry onto the existing library.
- **Lab** — Map the B2/B3 controls onto your control library.
- **Tools** — `OSCAL`

**Run it** — Map the B2/B3 controls onto your control library.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.4:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.4 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.4 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/grc/control-to-framework-mapping/scripts/control_to_framework_mapping.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.5 — Evaluation output as audit evidence

- **Risk** — Accepting a vendor's best-of-k demo as assurance; mistaking schema conformance for accuracy.
- **Control** — Read an eval report properly: execution-verified results, reliability across all attempts, trajectory scoring, judge independence.
- **Lab** — Take the C2.19 scoring output and turn it into an evidence pack — then find the three ways the same numbers could mislead you.
- **Tools** — `Cyber Commons eval harness`, `OSCAL`

**Run it** — Take the C2.19 scoring output and turn it into an evidence pack — then find the three ways the same numbers could mislead you.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.5:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.5 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.5 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/grc/control-evidence/scripts/control_evidence.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.6 — Operating vs outcome guardrails

- **Risk** — Frameworks specify how the system works; regulators care what it produced.
- **Control** — Constrain both, and know which evidence answers which question.
- **Lab** — Classify your own guardrails into the two buckets.
- **Tools** — `NeMo Guardrails`, `LLM Guard`
- **Open-weight models** — `Llama Guard 4`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Classify your own guardrails into the two buckets.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.6:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.6 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.6 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/grc/guardrail-specification/scripts/guardrail_specification.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.7 — Continuous control verification

- **Risk** — Automating judgment instead of evidence collection.
- **Control** — Agent-assisted evidence collection, drift detection, exception tracking.
- **Lab** — Automate one evidence package on a schedule.
- **Tools** — `OPA`, `OSCAL`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Automate one evidence package on a schedule.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.7:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.7 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.7 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/attestation/aws-runtime-posture-collector/scripts/aws_runtime_posture_collector.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.8 — Third-party and model supply chain risk

- **Risk** — Vendor AI features enabled by default; sub-processor chains you never mapped.
- **Control** — Questions that actually discriminate between vendors.
- **Lab** — Run a real AIBOM against a vendor model artefact.
- **Tools** — `OWASP AIBOM`, `Sigstore`

**Run it** — Run a real AIBOM against a vendor model artefact.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.8:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.8 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.8 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/grc/third-party-ai-assessment/scripts/third_party_ai_assessment.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.9 — Model and agent lifecycle governance

- **Risk** — Re-indexing treated as maintenance, not change.
- **Control** — Retraining, fine-tuning and re-indexing as change-management events.
- **Lab** — Write the gate that a re-index has to pass.

**Run it** — Write the gate that a re-index has to pass.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.9:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.9 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.9 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/grc/agent-lifecycle-governance/scripts/agent_lifecycle_governance.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.10 — The stakeholder map — who owns what

- **Risk** — Legal, compliance, privacy, cyber and model risk each hold part of the AI control estate and none holds all of it. The programme fails at the seams between them, not inside any one.
- **Control** — A stakeholder operating model naming who decides, who tests, who signs — and where the handoffs leave gaps nobody is watching.
- **Lab** — Map five stakeholders to the controls each operates, then locate the four classic seam failures in your own estate.
- **Tools** — `NIST AI RMF`, `ISO 42001`

**Run it** — Map five stakeholders to the controls each operates, then locate the four classic seam failures in your own estate.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.10:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.10 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.10 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/programme/stakeholder-seam-map/scripts/stakeholder_seam_map.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.11 — Model risk management for AI systems

- **Risk** — The classical model-risk playbook silently breaks once the model can act: conceptual soundness was validated, and then the agent was granted write access nobody validated.
- **Control** — Extend the SR 11-7 lineage — conceptual soundness, ongoing monitoring, independent validation — to non-deterministic, tool-using systems, and name where it still holds.
- **Lab** — Take a validated model, add one tool, and show which parts of the validation are now void.
- **Tools** — `Inspect`

**Run it** — Take a validated model, add one tool, and show which parts of the validation are now void.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.11:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.11 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.11 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/grc/model-risk-validation-scope/scripts/model_risk_validation_scope.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.12 — Working the seams

- **Risk** — The handoffs fail, not the functions: privacy assessment into control design, legal position into system prompt, MRM validation into security evidence.
- **Control** — Joint runbooks for the seams — one artefact, many consumers, one owner.
- **Lab** — Trace one artefact across three functions and find the consumer who never received it.
- **Tools** — `ISO 42001`

**Run it** — Trace one artefact across three functions and find the consumer who never received it.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.12:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.12 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.12 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/programme/handoff-delivery-check/scripts/handoff_delivery_check.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### F1.13 — Measuring the controls on CyberTravels — gaps and mitigations

- **Risk** — Controls are asserted in a register and never measured, so the first evidence that one was missing is the incident.
- **Control** — Key control indicators computed from source on every change, each gap carrying a named mitigation.
- **Lab** — Measure six indicators against the CyberTravels tree and read the five gaps it reports.

**Run it** — Measure six indicators against the CyberTravels tree and read the five gaps it reports.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F1.13:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F1.13 --out work/cybertravels
python3 scripts/checkpoint.py --at F1.13 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/grc/kci-control-measurement/scripts/kci_control_measurement.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

**Adjacency requirement:** also complete C2.0–C2.2 — the failures happen in the seams.
