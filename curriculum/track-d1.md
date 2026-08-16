# Track D1 — The SOC Analyst & Detection Engineer

**Function D · Security Operations**  
*Machine-speed decisions were already the problem here. Agents make it both worse and tractable.*

**Job titles:** SOC Analyst (T1–T3), Detection Engineer, Threat Hunter, Threat Intelligence Analyst

**What changes:** You stop reading alerts and start compressing signal. And you acquire a new detection domain: agents behaving badly.

**Autonomy focus:** Triage and enrichment reach L2.5 quickly; containment actions stay L2.

**Deliverable:** A triage loop in production plus five detections covering agent misbehaviour.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### D1.1 — From alert queue to loop operator

`AI for Security`

- **Risk** — Supervising by re-reading everything the loop did.
- **Control** — Know what the loop must escalate and sample the rest.
- **Lab** — Run a triage loop over Wazuh alerts and supervise by exception.
- **Tools** — `Wazuh`, `OpenSearch`
- **Models** — `GLM-4.6`

**Run it** — Supervise a triage loop by exception rather than by re-reading.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
docker compose up -d wazuh opensearch
./seed-alerts.sh                       # replayable alert corpus
python3 triage_loop.py --model $MODEL --escalate-on high
```

*Expect:* The loop clears the known-benign and escalates the rest with its reasoning attached.

---

### D1.2 — Context that makes triage work

`AI for Security`

- **Risk** — Generic triage agents underperform your worst analyst.
- **Control** — Feed the baseline, known FPs, crown-jewel map and prior decisions.
- **Lab** — A/B a generic prompt vs a context-loaded one on the same alert set.
- **Tools** — `Wazuh`
- **Models** — `GLM-4.6`, `Llama 3.3`

**Run it** — Show a context-loaded triage loop beating a generic one.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
python3 triage_loop.py --context none     --alerts alerts.jsonl --score
python3 triage_loop.py --context loaded   --alerts alerts.jsonl --score   # baseline+FPs+crown jewels
python3 compare.py
```

*Expect:* The generic loop underperforms your worst analyst; the loaded one does not. Same model both times.

---

### D1.3 — Agent-assisted detection engineering

`AI for Security`

- **Risk** — Coverage gaps nobody mapped.
- **Control** — Detection-as-code with agents inside the CI loop.
- **Lab** — Generate and unit-test Sigma rules in CI; map coverage to ATT&CK.
- **Tools** — `Sigma`, `Wazuh`
- **Models** — `Kimi K2`

**Run it** — Generate, unit-test and tune detections inside CI.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install sigma-cli && cd labs/d1-soc/detections
python3 gen_rule.py --technique T1059 --model $MODEL --out rules/t1059.yml
sigma check rules/t1059.yml && python3 test_rule.py --rule rules/t1059.yml --positives pos/ --negatives neg/
python3 coverage.py --map-to attack
```

*Expect:* Rules that fail their negative corpus never merge. Coverage map shows the gap you actually have.

---

### D1.4 — Detection engineering *for* agents

`Security of AI`

- **Risk** — Scope drift, unusual tool sequencing, off-hours autonomous action.
- **Control** — Detections whose subject is a non-human principal.
- **Lab** — Write five detections for agent misbehaviour and fire each one.
- **Tools** — `Falco`, `Sigma`

**Run it** — Five detections whose subject is a non-human principal.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc/detections
./install-sigma.sh   # scope drift, tool-sequence anomaly, off-hours autonomy, retrieval anomaly, NHI-at-human-time
./fire-each.sh       # deliberately trigger all five
```

*Expect:* All five fire on synthetic-but-real agent telemetry from the A3/B2 labs.

---

### D1.5 — Agent telemetry as a data source

`Security of AI`

- **Risk** — Prompts, traces, tool calls and approvals never reach the SIEM.
- **Control** — Onboard agent telemetry deliberately; decide retention.
- **Lab** — Ship OTEL agent traces into OpenSearch and query them.
- **Tools** — `OpenTelemetry`, `OpenSearch`

**Run it** — Get agent telemetry into the SIEM and query it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
docker compose up -d opensearch otel-collector
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 python3 ../m0-agent-loop/loop.py --task fix-tests
curl -s localhost:9200/agent-traces/_search -d '{"query":{"match":{"tool":"apply_patch"}}}' | jq '.hits.total'
```

*Expect:* Prompts, tool calls, decisions and spend queryable alongside your other log sources.

---

### D1.6 — Distinguishing agent from human

`Security of AI`

- **Risk** — Your earliest Shadow Autonomy signal is invisible.
- **Control** — Behavioural signatures separating agent from inherited human.
- **Lab** — Build the classifier on timing, sequencing and volume features.
- **Tools** — `OpenSearch`
- **Models** — `Llama 3.3`

**Run it** — Tell an agent apart from the human whose credential it inherited.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
python3 agent_vs_human.py --features timing,sequencing,volume --train baseline.jsonl
python3 agent_vs_human.py --classify live.jsonl
```

*Expect:* A working classifier — your earliest Shadow Autonomy signal.

---

### D1.7 — Drift monitoring

`Security of AI`

- **Risk** — A detection that worked last month is silently degraded.
- **Control** — Watch model updates, prompt changes, index refreshes, tool versions.
- **Lab** — Change the model underneath and catch the detection regression.
- **Tools** — `promptfoo`
- **Models** — `GLM-4.6`

**Run it** — Catch a detection silently degrading after a model change.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
promptfoo eval -c detection-regression.yaml --model llama3.3   # baseline
promptfoo eval -c detection-regression.yaml --model glm-4.6    # after 'upgrade'
python3 drift_report.py
```

*Expect:* A rule that passed last month fails now. Nothing in your code changed.

---

### D1.8 — Threat intel sub-lane

`AI for Security`

- **Risk** — Unsourced confidence in synthesis loops.
- **Control** — Provenance discipline; refuse claims without a source.
- **Lab** — Build a synthesis loop that must cite or abstain.
- **Tools** — `MISP`, `OpenCTI`
- **Models** — `GLM-4.6`

**Run it** — Build a synthesis loop that must cite or abstain.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc/intel
docker compose up -d opencti
python3 synthesise.py --topic 'agentic malware' --require-source --model $MODEL
python3 synthesise.py --topic 'agentic malware' --no-require-source   # watch confidence appear from nowhere
```

*Expect:* With provenance enforced the loop abstains where it has nothing; without it, it confabulates fluently.

---

**Adjacency requirement:** also complete A2.3–A2.4 — the failures happen in the seams.
