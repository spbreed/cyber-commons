# Track E2 — Building the Governance Platform — Regulatory and Compliance

**Function E · AI Governance for Agentic Systems**  
*Governing autonomy rather than approving tools: the register, the obligations and the programme that keep CyberTravels defensible.*

**Job titles:** Compliance Manager, Regulatory Affairs (Tech), Privacy Engineer, AI Governance Lead

**What changes:** What a travel company holding passports, payment and health data owes, to whom, and how to evidence it once rather than per regulator. 9 lessons.

**Autonomy focus:** You determine which action classes are legally prohibited from ever reaching L2.5, irrespective of measured performance.

**Deliverable:** One control set mapped to three regimes, plus an evidence pack for a single high-risk agentic workflow.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### E2.1 — The regulatory map

`Security of AI`

- **Risk** — One programme per regime; four times the work, none of it joined up.
- **Control** — One control set that satisfies several regimes. Verify current status before relying on any date.
- **Lab** — Build the crosswalk for your own sector.
- **Tools** — `OSCAL`

**Run it** — Build one control set that answers several regimes.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e2-compliance
python3 crosswalk.py --regimes horizontal-ai,privacy,sector --controls ../e1-grc/control-library.yaml
python3 crosswalk.py --show-orphans   # obligations no control answers
```

*Expect:* One spine, several overlays. Orphans are your programme backlog.

---

### E2.2 — Horizontal AI regulation

`Security of AI`

- **Risk** — "We only deployed it, we didn't build it" — sometimes true, often not.
- **Control** — Risk classification, GPAI obligations, transparency duties, and how agentic deployment changes classification.
- **Lab** — Classify three workflows and defend the boundary cases.

**Run it** — Classify three workflows and defend the boundary cases.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e2-compliance
python3 classify_risk.py --workflows ../e1-grc/workflows.yaml --explain
python3 classify_risk.py --deployer-vs-provider
```

*Expect:* Shows where 'we only deployed it' holds and where agentic deployment pulls you into provider obligations.

---

### E2.3 — Voluntary frameworks as your spine

`Security of AI`

- **Risk** — Regime-specific mappings with nothing to hang off.
- **Control** — AI RMF / management-system standards as the structure; regulator mappings as overlays.
- **Lab** — Hang two regulator mappings off one framework spine.
- **Tools** — `NIST AI RMF`, `OSCAL`

**Run it** — Hang two regulator mappings off one framework spine.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e2-compliance
python3 spine.py --framework nist-ai-rmf --overlay regime-a --overlay regime-b --out oscal/
oscal-cli validate oscal/system-security-plan.json
```

*Expect:* Valid OSCAL, one spine, two overlays — instead of two disconnected programmes.

---

### E2.4 — Sector overlays

`Security of AI`

- **Risk** — An agent is already a "model" under model-risk rules you already comply with.
- **Control** — Find the regime you're already in before inventing a new one.
- **Lab** — Map one agent to existing model-risk obligations.

**Run it** — Find the regime you are already in.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e2-compliance
python3 sector_overlay.py --agent patch-agent --sector financial-services --check model-risk
```

*Expect:* The agent is often already a 'model' under rules you already comply with. Cheaper than inventing a new programme.

---

### E2.5 — Privacy and data protection

`Security of AI`

- **Risk** — Deletion when the data is in weights, not a database.
- **Control** — Lawful basis, ADM rights, residency in inference and retrieval paths, retention of traces.
- **Lab** — Run PII redaction inside the trust boundary with Presidio before anything crosses out.
- **Tools** — `Presidio`, `GLiNER-PII`

**Run it** — Redact inside the trust boundary before anything crosses out.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install presidio-analyzer presidio-anonymizer
cd labs/e2-compliance
python3 redact_gateway.py --listen 8088 --upstream $OPENAI_BASE_URL
curl -s localhost:8088/v1/chat/completions -d @with-pii.json | jq
```

*Expect:* PII is removed before egress; the redaction decision is logged as evidence for E2.7.

---

### E2.6 — Incident and disclosure obligations

`Security of AI`

- **Risk** — Materiality assessed for an autonomous actor with a human-actor playbook.
- **Control** — Coordinate with D2 in hour one.
- **Lab** — Draft the notification for an agentic incident.

**Run it** — Draft the notification for an autonomous actor.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e2-compliance
python3 notify.py --incident ../d2-ir/case-01 --regime <your-regime> --draft
python3 notify.py --incident ../d2-ir/case-01 --materiality-worksheet
```

*Expect:* A draft that names the agent, the authority and the containment — the questions a supervisor asks first.

---

### E2.7 — Documentation that survives supervision

`Security of AI`

- **Risk** — "Explainability" for a system with no deterministic reasoning.
- **Control** — System documentation, data lineage, eval records, oversight evidence, decision logs.
- **Lab** — Assemble the pack for one high-risk workflow.
- **Tools** — `OSCAL`, `Model Cards`

**Run it** — Assemble a pack that survives supervision.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e2-compliance
python3 evidence_pack.py --workflow patch-agent \
  --include system-doc,data-lineage,eval-records,oversight,decision-logs --out pack/
python3 evidence_pack.py --audit-self pack/   # what a supervisor would find missing
```

*Expect:* A pack with a self-audit attached, including an honest statement of what 'explainability' can mean here.

---

### E2.8 — Auditability of autonomous action

`Security of AI`

- **Risk** — No trail showing under whose authority the agent acted.
- **Control** — The delegation chain *is* the audit trail.
- **Lab** — Produce an audit trail from the A2 chain that names authority at every hop.
- **Tools** — `Keycloak`

**Run it** — Build the audit trail out of the delegation chain itself.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e2-compliance
python3 audit_trail.py --from-keycloak --workflow patch-agent --out trail.json
```

*Expect:* Which agent, under whose authority, in what scope, verified by which control, reviewable by whom — all from the `act` chain.

---

### E2.9 — Regulator and auditor conversations

`Security of AI`

- **Risk** — Overclaiming control, or triggering a moratorium.
- **Control** — Explain bounded autonomy with evidence, and anticipate the real questions.
- **Lab** — Defend one workflow in a mock supervisory conversation.

**Run it** — Defend one workflow in a mock supervisory conversation.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E2.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E2.9   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e2-compliance
python3 mock_supervisor.py --workflow patch-agent --pack pack/ --model $MODEL --adversarial
```

*Expect:* You get asked the real questions. Overclaiming control is scored as harshly as underclaiming.

---
