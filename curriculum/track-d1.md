# Track D1 — The Agentic SOC — Discover

**Function D · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** 

**What changes:** 

**Autonomy focus:** 

**Deliverable:** 

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### D1.0 — Start here — what AI for security operations means

- **Risk** — A detection stack tuned for human tempo, watching an actor that acts a thousand times an hour and never repeats a session.
- **Control** — Agent telemetry as a first-class data source, detections written for agent behaviour, and a stop lever that a human can actually pull in time.
- **Lab** — Put one agent trace and one human session side by side and list what separates them.

**Run it** — Put one agent trace and one human session side by side and list what separates them.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.0   # run it headless and check it
```

*Expect:* Five behavioural signals print for a person and an agent over the same hour, with ratios in the hundreds. A volume rule tuned for human tempo does fire on the agent — roughly 150 seconds in, by which point the actor has finished.

---

### D1.1 — Threat intel sub-lane

- **Risk** — Unsourced confidence in synthesis loops.
- **Control** — Provenance discipline; refuse claims without a source.
- **Lab** — Build a synthesis loop that must cite or abstain.
- **Tools** — `MISP`, `OpenCTI`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Build a synthesis loop that must cite or abstain.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc/intel
docker compose up -d opencti
python3 synthesise.py --topic 'agentic malware' --require-source --model $MODEL
python3 synthesise.py --topic 'agentic malware' --no-require-source   # watch confidence appear from nowhere
```

*Expect:* With provenance enforced the loop abstains where it has nothing; without it, it confabulates fluently.

---

### D1.2 — Agent telemetry as a data source

- **Risk** — Prompts, traces, tool calls and approvals never reach the SIEM.
- **Control** — Onboard agent telemetry deliberately; decide retention.
- **Lab** — Ship OTEL agent traces into OpenSearch and query them.
- **Tools** — `OpenTelemetry`, `OpenSearch`

**Run it** — Ship OTEL agent traces into OpenSearch and query them.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
docker compose up -d opensearch otel-collector
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 python3 ../m0-agent-loop/loop.py --task fix-tests
curl -s localhost:9200/agent-traces/_search -d '{"query":{"match":{"tool":"apply_patch"}}}' | jq '.hits.total'
```

*Expect:* Prompts, tool calls, decisions and spend queryable alongside your other log sources.

---

### D1.3 — Drift monitoring

- **Risk** — A detection that worked last month is silently degraded.
- **Control** — Watch model updates, prompt changes, index refreshes, tool versions.
- **Lab** — Change the model underneath and catch the detection regression.
- **Tools** — `promptfoo`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Change the model underneath and catch the detection regression.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
promptfoo eval -c detection-regression.yaml --model llama3.3   # baseline
promptfoo eval -c detection-regression.yaml --model glm-4.6    # after 'upgrade'
python3 drift_report.py
```

*Expect:* A rule that passed last month fails now. Nothing in your code changed.

---

### D1.4 — Distinguishing agent from human

- **Risk** — Your earliest Shadow Autonomy signal is invisible.
- **Control** — Behavioural signatures separating agent from inherited human.
- **Lab** — Build the classifier on timing, sequencing and volume features.
- **Tools** — `OpenSearch`
- **Open-weight models** — `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Build the classifier on timing, sequencing and volume features.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
python3 agent_vs_human.py --features timing,sequencing,volume --train baseline.jsonl
python3 agent_vs_human.py --classify live.jsonl
```

*Expect:* A working classifier — your earliest Shadow Autonomy signal.

---

### D1.5 — Hunting in agent telemetry

- **Risk** — Everything not covered by a rule is invisible, and the rules were written against last quarter's agent behaviour.
- **Control** — A standing hunt over agent traces, hypothesis-first, whose confirmed findings graduate into detections rather than staying in a notebook.
- **Lab** — Run three hypotheses over a labelled trace corpus and score what each one catches and misses.
- **Tools** — `OpenTelemetry`

**Run it** — Run three hypotheses over a labelled trace corpus and score what each one catches and misses.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.5   # run it headless and check it
```

*Expect:* Run three hypotheses over a labelled trace corpus and score what each one catches and misses.

---

**Adjacency requirement:** also complete A2.3–A2.4 — the failures happen in the seams.
