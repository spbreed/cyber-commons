# Track E1 — The GRC Practitioner (Risk & Control)

**Function E · Governance, Risk, Compliance & the CISO Office**  
*The function that has to make all of the above defensible to a board, an auditor and a regulator — usually in that order.*

**Job titles:** GRC Analyst, Risk Manager, Control Owner, Third-Party Risk Analyst, Internal Audit liaison

**What changes:** Point-in-time assessment stops working entirely. Models change through fine-tuning, prompt updates and index refreshes without a single code change. You move from assessing to continuously evidencing.

**Autonomy focus:** You define the promotion criteria that let a workflow move from L2 to L2.5 — and the conditions that force it back down.

**Deliverable:** A risk-tiered agent register with mapped controls and one fully evidenced control assertion.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### E1.1 — Why point-in-time control testing fails for AI

`Security of AI`

- **Risk** — An annual review certifies nothing about a system that changed on Tuesday.
- **Control** — Continuous assurance; control effectiveness redefined for probabilistic systems.
- **Lab** — Change a prompt and show the control evidence going stale in real time.
- **Tools** — `promptfoo`

**Run it** — Watch control evidence go stale without a code change.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e1-grc
python3 assert_control.py --control AI-GUARD-02 --evidence-date today   # PASS
sed -i 's/refuse/consider/' ../m0-agent-loop/system-prompt.txt
python3 assert_control.py --control AI-GUARD-02 --evidence-date today   # now FAIL
```

*Expect:* One prompt edit invalidated an annual assessment. That is why point-in-time testing fails for AI.

---

### E1.2 — Building the AI and agent inventory

`Security of AI`

- **Risk** — Shadow AI and shadow agents — the inventory is the control most orgs still lack.
- **Control** — Discovery, registration, ownership, risk tiering.
- **Lab** — Discover agents from gateway and identity telemetry; build the register.
- **Tools** — `agentgateway`, `SPIRE`

**Run it** — Discover agents you did not know you had.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e1-grc
python3 discover.py --from-gateway http://localhost:15000/stats --from-spire
python3 register.py --out agent-register.csv
```

*Expect:* A register built from telemetry rather than from a survey nobody answered.

---

### E1.3 — Risk tiering agentic use cases

`Security of AI`

- **Risk** — Tiering by model name instead of by what the thing can do.
- **Control** — Autonomy level × action class × data sensitivity.
- **Lab** — Tier ten real workflows and assign approval authority.

**Run it** — Tier by what the thing can do, not by model name.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e1-grc
python3 tier.py --workflows workflows.yaml --axes autonomy,action-class,data-sensitivity
python3 tier.py --show-approvers
```

*Expect:* Two workflows on the same model land in different tiers — which is the point.

---

### E1.4 — Control mapping for agents

`Security of AI`

- **Risk** — Inventing new controls where an existing one applied to a new principal type.
- **Control** — Map identity, secrets, sandbox, eval and telemetry onto the existing library.
- **Lab** — Map the A2/A3 controls onto your control library.
- **Tools** — `OSCAL`

**Run it** — Map agent controls onto the library you already have.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e1-grc
python3 map_controls.py --new agent-controls.yaml --existing control-library.yaml --out gap.md
```

*Expect:* Most map to an existing control applied to a new principal type. The genuinely new ones are few — and named.

---

### E1.5 — Evaluation output as audit evidence

`Security of AI`  ·  **flagship lab**

- **Risk** — Accepting a vendor's best-of-k demo as assurance; mistaking schema conformance for accuracy.
- **Control** — Read an eval report properly: execution-verified results, reliability across all attempts, trajectory scoring, judge independence.
- **Lab** — Take the B2.10 harness output and turn it into an evidence pack — then find the three ways the same numbers could mislead you.
- **Tools** — `Cyber Commons eval harness`, `OSCAL`

**Run it** — Turn an eval report into audit evidence — and find how it could mislead you.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b2.10-eval-harness
./scripts/vulnbench.sh compare > evidence/raw-results.txt
python3 ../e1-grc/evidence_pack.py --results evidence/raw-results.txt --control AI-EVAL-01
python3 ../e1-grc/challenge.py --pack evidence/AI-EVAL-01.json   # the three ways this misleads
```

*Expect:* An OSCAL-shaped evidence pack, plus a written challenge: best-of-k reporting, conformance-as-accuracy, and judge dependence.

> Lab source: [`labs/b2.10-eval-harness`](../labs/b2.10-eval-harness)

---

### E1.6 — Operating vs outcome guardrails

`Security of AI`

- **Risk** — Frameworks specify how the system works; regulators care what it produced.
- **Control** — Constrain both, and know which evidence answers which question.
- **Lab** — Classify your own guardrails into the two buckets.
- **Tools** — `NeMo Guardrails`, `LLM Guard`
- **Models** — `Llama Guard 4`

**Run it** — Sort your guardrails into operating vs outcome.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e1-grc
python3 classify_guardrails.py --config ../m0-agent-loop/guardrails.yaml
python3 classify_guardrails.py --gap-analysis   # which regulator question is unanswered
```

*Expect:* Frameworks specify how the system works; regulators ask what it produced. Most orgs are long on the first.

---

### E1.7 — Continuous control verification

`Security of AI`

- **Risk** — Automating judgment instead of evidence collection.
- **Control** — Agent-assisted evidence collection, drift detection, exception tracking.
- **Lab** — Automate one evidence package on a schedule.
- **Tools** — `OPA`, `OSCAL`
- **Models** — `GLM-4.6`

**Run it** — Automate the evidence package, not the judgment.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e1-grc
python3 collect_evidence.py --control-set controls.yaml --schedule daily
python3 drift.py --baseline evidence/2026-08-01 --current evidence/today
```

*Expect:* Control drift surfaces as a diff; a human still decides what it means.

---

### E1.8 — Third-party and model supply chain risk

`Security of AI`

- **Risk** — Vendor AI features enabled by default; sub-processor chains you never mapped.
- **Control** — Questions that actually discriminate between vendors.
- **Lab** — Run a real AIBOM against a vendor model artefact.
- **Tools** — `OWASP AIBOM`, `Sigstore`

**Run it** — Run a real AIBOM against a model artefact.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e1-grc
python3 aibom.py --model-dir ~/.ollama/models --out aibom.json
cosign verify-blob --bundle model.sig model.gguf   # provenance where signed
```

*Expect:* An artefact inventory with provenance status per component — and an honest 'unsigned' where that is the truth.

---

### E1.9 — Model and agent lifecycle governance

`Security of AI`

- **Risk** — Re-indexing treated as maintenance, not change.
- **Control** — Retraining, fine-tuning and re-indexing as change-management events.
- **Lab** — Write the gate that a re-index has to pass.

**Run it** — Write the gate a re-index has to pass.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.9   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/e1-grc
python3 lifecycle_gate.py --event reindex --require eval-pass,owner-approval,rollback-plan
python3 lifecycle_gate.py --simulate reindex --without rollback-plan   # blocked
```

*Expect:* Re-indexing is a change-management event with a gate, not maintenance.

---

**Adjacency requirement:** also complete B2.1–B2.2 — the failures happen in the seams.
