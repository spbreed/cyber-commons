# Track E1 — The GRC Practitioner (Risk & Control)

**Function E · AI for GRC**  
*Governing autonomy instead of approving tools — a list of approved products does not survive a thousand agents.*

**Job titles:** GRC Analyst, Risk Manager, Control Owner, Third-Party Risk Analyst, Internal Audit liaison

**What changes:** Trustworthy AI, and the five functions that have to deliver it. 13 lessons.

**Autonomy focus:** You define the promotion criteria that let a workflow move from L2 to L2.5 — and the conditions that force it back down.

**Deliverable:** A risk-tiered agent register with mapped controls and one fully evidenced control assertion.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### E1.0 — Start here — what AI governance means

`both directions`

- **Risk** — A trustworthy-AI statement with no owner per property, so every property is somebody else's job.
- **Control** — One register, risk-tiered, with each property mapped to a control, an owner and evidence that can be re-checked.
- **Lab** — Take the seven properties and assign each an owner in your own organisation. The gaps are the programme.

**Run it** — Assign each of the seven trustworthy-AI properties to a named owner, and count how many of them security holds outright.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.0   # run it headless and check it
```

*Expect:* Seven trustworthy-AI properties print with a typical owner each. Security owns exactly one outright and contributes evidence to the other six — which is the reason this function exists as more than a security document.

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

`Security of AI`

- **Risk** — Accepting a vendor's best-of-k demo as assurance; mistaking schema conformance for accuracy.
- **Control** — Read an eval report properly: execution-verified results, reliability across all attempts, trajectory scoring, judge independence.
- **Lab** — Take the B2.11 harness output and turn it into an evidence pack — then find the three ways the same numbers could mislead you.
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

---

### E1.6 — Operating vs outcome guardrails

`Security of AI`

- **Risk** — Frameworks specify how the system works; regulators care what it produced.
- **Control** — Constrain both, and know which evidence answers which question.
- **Lab** — Classify your own guardrails into the two buckets.
- **Tools** — `NeMo Guardrails`, `LLM Guard`
- **Open-weight models** — `Llama Guard 4`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

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
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

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

### E1.10 — The stakeholder map: who owns what

`Security of AI`

- **Risk** — Legal, compliance, privacy, cyber and model risk each hold part of the AI control estate and none holds all of it. The programme fails at the seams between them, not inside any one.
- **Control** — A stakeholder operating model naming who decides, who tests, who signs — and where the handoffs leave gaps nobody is watching.
- **Lab** — Map five stakeholders to the controls each operates, then locate the four classic seam failures in your own estate.
- **Tools** — `NIST AI RMF`, `ISO 42001`

**Run it** — Map five stakeholders to the controls each operates, then locate the four classic seam failures in your own estate.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.10   # run it headless and check it
```

*Expect:* Five stakeholder functions print with the question each is asking and the controls each operates — 22 controls in total. Four seam failures are shown as pairs of individually reasonable assumptions, and every function still self-reports green while all four gaps are open. Naming one accountable owner per handoff closes them, and a use case with all five control functions and no business owner is shown to be ungoverned.

---

### E1.11 — Model risk management for AI systems

`Security of AI`

- **Risk** — The classical model-risk playbook silently breaks once the model can act: conceptual soundness was validated, and then the agent was granted write access nobody validated.
- **Control** — Extend the SR 11-7 lineage — conceptual soundness, ongoing monitoring, independent validation — to non-deterministic, tool-using systems, and name where it still holds.
- **Lab** — Take a validated model, add one tool, and show which parts of the validation are now void.
- **Tools** — `Inspect`

**Run it** — Take a validated model, add one tool, and show which parts of the validation are now void.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.11.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.11   # run it headless and check it
```

*Expect:* The three SR 11-7 pillars print with the assumption each makes. A system validated with no tools at L1 is shown deployed with three tools at L3 — same model, same version — and the validation no longer covers it. Monitoring reports 200 clean runs of summarisation accuracy while four action-level metrics have no threshold at all, and four revalidation triggers classical MRM would miss are named.

---

### E1.12 — Working the seams

`Security of AI`

- **Risk** — The handoffs fail, not the functions: privacy assessment into control design, legal position into system prompt, MRM validation into security evidence.
- **Control** — Joint runbooks for the seams — one artefact, many consumers, one owner.
- **Lab** — Trace one artefact across three functions and find the consumer who never received it.
- **Tools** — `ISO 42001`

**Run it** — Trace one artefact across three functions and find the consumer who never received it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/E1.12.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session E1.12   # run it headless and check it
```

*Expect:* Three joint runbooks are traced from owner to consumer, and three handoffs turn out never to have been delivered — model risk never receives the privacy assessment, and neither security nor internal audit receives the validation report. Each undelivered handoff is a control that was built, works, and is invisible to the function whose decision depends on it. A four-property check runs over the seams and goes from several problems to zero.

---

**Adjacency requirement:** also complete B2.1–B2.2 — the failures happen in the seams.
