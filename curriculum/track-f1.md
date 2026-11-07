# Track F1 — Building the Governance Framework — Risk and Control

**Function F · AI Governance for Agentic Systems**  
*Governing autonomy rather than approving tools: the register, the obligations and the programme that keep CyberTravels defensible.*

**Job titles:** GRC Analyst, Risk Manager, Control Owner, Third-Party Risk Analyst, Internal Audit liaison

**What changes:** The register of every agent CyberTravels runs, risk-tiered by autonomy, data and blast radius, mapped to controls, with evidence that can be re-checked. 13 lessons.

**Autonomy focus:** You define the promotion criteria that let a workflow move from L2 to L2.5 — and the conditions that force it back down.

**Deliverable:** A risk-tiered agent register with mapped controls and one fully evidenced control assertion.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### F1.0 — Start here: AI governance

- **Risk** — A trustworthy-AI statement with no owner per property, so every property is somebody else's job.
- **Control** — One register, risk-tiered, with each property mapped to a control, an owner and evidence that can be re-checked.
- **Lab** — Take the seven properties and assign each an owner in your own organisation. The gaps are the programme.

**Run it** — Take the seven properties and assign each an owner in your own organisation. The gaps are the programme.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.0

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-0-ai-governance
#         (Claude Code and Copilot: /f1-0-ai-governance · Cursor: type / and
#         search · Codex: $f1-0-ai-governance). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.0
```

---

### F1.1 — From control to measurable indicator

- **Risk** — An annual review certifies nothing about a system that changed the week after it.
- **Control** — Continuous assurance; control effectiveness redefined for probabilistic systems.
- **Lab** — Change a prompt and show the control evidence going stale in real time.
- **Tools** — `promptfoo`

**Run it** — Change a prompt and show the control evidence going stale in real time.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.1

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-1-from-control-to-measurable-indicator
#         (Claude Code and Copilot: /f1-1-from-control-to-measurable-indicator · Cursor: type / and
#         search · Codex: $f1-1-from-control-to-measurable-indicator). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.1
```

---

### F1.2 — The AI and agent inventory

- **Risk** — Shadow AI and shadow agents — the inventory is the control most orgs still lack.
- **Control** — Discovery, registration, ownership, risk tiering.
- **Lab** — Discover agents from gateway and identity telemetry; build the register.
- **Tools** — `agentgateway`, `SPIRE`

**Run it** — Discover agents from gateway and identity telemetry; build the register.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.2

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-2-the-ai-and-agent-inventory
#         (Claude Code and Copilot: /f1-2-the-ai-and-agent-inventory · Cursor: type / and
#         search · Codex: $f1-2-the-ai-and-agent-inventory). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.2
```

---

### F1.3 — Risk tiers for agent use

- **Risk** — Tiering by model name instead of by what the thing can do.
- **Control** — Autonomy level × action class × data sensitivity.
- **Lab** — Tier ten real workflows and assign approval authority.

**Run it** — Tier ten real workflows and assign approval authority.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.3

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-3-risk-tiers-for-agent-use
#         (Claude Code and Copilot: /f1-3-risk-tiers-for-agent-use · Cursor: type / and
#         search · Codex: $f1-3-risk-tiers-for-agent-use). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.3
```

---

### F1.4 — Mapping controls to agents

- **Risk** — Inventing new controls where an existing one applied to a new principal type.
- **Control** — Map identity, secrets, sandbox, eval and telemetry onto the existing library.
- **Lab** — Map the B2/B3 controls onto your control library.
- **Tools** — `OSCAL`

**Run it** — Map the B2/B3 controls onto your control library.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.4

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-4-mapping-controls-to-agents
#         (Claude Code and Copilot: /f1-4-mapping-controls-to-agents · Cursor: type / and
#         search · Codex: $f1-4-mapping-controls-to-agents). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.4
```

---

### F1.5 — Eval results as audit evidence

- **Risk** — Accepting a vendor's best-of-k demo as assurance; mistaking schema conformance for accuracy.
- **Control** — Read an eval report properly: execution-verified results, reliability across all attempts, trajectory scoring, judge independence.
- **Lab** — Take the C2.19 scoring output and turn it into an evidence pack — then find the three ways the same numbers could mislead you.
- **Tools** — `Cyber Commons eval harness`, `OSCAL`

**Run it** — Take the C2.19 scoring output and turn it into an evidence pack — then find the three ways the same numbers could mislead you.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.5

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-5-eval-results-as-audit-evidence
#         (Claude Code and Copilot: /f1-5-eval-results-as-audit-evidence · Cursor: type / and
#         search · Codex: $f1-5-eval-results-as-audit-evidence). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.5
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.6

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-6-operating-vs-outcome-guardrails
#         (Claude Code and Copilot: /f1-6-operating-vs-outcome-guardrails · Cursor: type / and
#         search · Codex: $f1-6-operating-vs-outcome-guardrails). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.6
```

---

### F1.7 — Checking controls continuously

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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.7

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-7-checking-controls-continuously
#         (Claude Code and Copilot: /f1-7-checking-controls-continuously · Cursor: type / and
#         search · Codex: $f1-7-checking-controls-continuously). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.7
```

---

### F1.8 — Third-party and model risk

- **Risk** — Vendor AI features enabled by default; sub-processor chains you never mapped.
- **Control** — Questions that actually discriminate between vendors.
- **Lab** — Run a real AIBOM against a vendor model artefact.
- **Tools** — `OWASP AIBOM`, `Sigstore`

**Run it** — Run a real AIBOM against a vendor model artefact.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.8

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-8-third-party-and-model-risk
#         (Claude Code and Copilot: /f1-8-third-party-and-model-risk · Cursor: type / and
#         search · Codex: $f1-8-third-party-and-model-risk). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.8
```

---

### F1.9 — Agent lifecycle governance

- **Risk** — Re-indexing treated as maintenance, not change.
- **Control** — Retraining, fine-tuning and re-indexing as change-management events.
- **Lab** — Write the gate that a re-index has to pass.

**Run it** — Write the gate that a re-index has to pass.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.9

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-9-agent-lifecycle-governance
#         (Claude Code and Copilot: /f1-9-agent-lifecycle-governance · Cursor: type / and
#         search · Codex: $f1-9-agent-lifecycle-governance). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.9
```

---

### F1.10 — Who owns what

- **Risk** — Legal, compliance, privacy, cyber and model risk each hold part of the AI control estate and none holds all of it. The programme fails at the seams between them, not inside any one.
- **Control** — A stakeholder operating model naming who decides, who tests, who signs — and where the handoffs leave gaps nobody is watching.
- **Lab** — Map five stakeholders to the controls each operates, then locate the four classic seam failures in your own estate.
- **Tools** — `NIST AI RMF`, `ISO 42001`

**Run it** — Map five stakeholders to the controls each operates, then locate the four classic seam failures in your own estate.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.10

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-10-who-owns-what
#         (Claude Code and Copilot: /f1-10-who-owns-what · Cursor: type / and
#         search · Codex: $f1-10-who-owns-what). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.10
```

---

### F1.11 — Model risk management

- **Risk** — The classical model-risk playbook silently breaks once the model can act: conceptual soundness was validated, and then the agent was granted write access nobody validated.
- **Control** — Extend the SR 11-7 lineage — conceptual soundness, ongoing monitoring, independent validation — to non-deterministic, tool-using systems, and name where it still holds.
- **Lab** — Take a validated model, add one tool, and show which parts of the validation are now void.
- **Tools** — `Inspect`

**Run it** — Take a validated model, add one tool, and show which parts of the validation are now void.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.11

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-11-model-risk-management
#         (Claude Code and Copilot: /f1-11-model-risk-management · Cursor: type / and
#         search · Codex: $f1-11-model-risk-management). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.11
```

---

### F1.12 — Gaps between teams

- **Risk** — The handoffs fail, not the functions: privacy assessment into control design, legal position into system prompt, MRM validation into security evidence.
- **Control** — Joint runbooks for the seams — one artefact, many consumers, one owner.
- **Lab** — Trace one artefact across three functions and find the consumer who never received it.
- **Tools** — `ISO 42001`

**Run it** — Trace one artefact across three functions and find the consumer who never received it.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.12

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-12-gaps-between-teams
#         (Claude Code and Copilot: /f1-12-gaps-between-teams · Cursor: type / and
#         search · Codex: $f1-12-gaps-between-teams). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.12
```

---

### F1.13 — Measuring CyberTravels' controls

- **Risk** — Controls are asserted in a register and never measured, so the first evidence that one was missing is the incident.
- **Control** — Key control indicators computed from source on every change, each gap carrying a named mitigation.
- **Lab** — Measure six indicators against the CyberTravels tree and read the five gaps it reports.

**Run it** — Measure six indicators against the CyberTravels tree and read the five gaps it reports.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F1.13

# --- 3 · in your agent, open this folder and pick the skill:
#         f1-13-measuring-cybertravels-controls
#         (Claude Code and Copilot: /f1-13-measuring-cybertravels-controls · Cursor: type / and
#         search · Codex: $f1-13-measuring-cybertravels-controls). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F1.13
```

---

**Adjacency requirement:** also complete C2.0–C2.2 — the failures happen in the seams.
