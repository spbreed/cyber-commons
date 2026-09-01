# Track D1 — The Agentic SOC — Detection

**Function D · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like TripBot's.*

**Job titles:** SOC Analyst (T1–T3), Detection Engineer, Threat Hunter, Threat Intelligence Analyst

**What changes:** Detecting an actor that is not a person, on TripBot's telemetry. 11 lessons.

**Autonomy focus:** Triage and enrichment reach L2.5 quickly; containment actions stay L2.

**Deliverable:** A triage loop in production plus five detections covering agent misbehaviour.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### D1.0 — Start here — what AI for security operations means

`both directions`

- **Risk** — A detection stack tuned for human tempo, watching an actor that acts a thousand times an hour and never repeats a session.
- **Control** — Agent telemetry as a first-class data source, detections written for agent behaviour, and a stop lever that a human can actually pull in time.
- **Lab** — Put one agent trace and one human session side by side and list what separates them.

**Run it** — Put one hour of an agent beside one hour of a person, then run a human-tempo rule against both.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.0   # run it headless and check it
```

*Expect:* Five behavioural signals print for a person and an agent over the same hour, with ratios in the hundreds. A volume rule tuned for human tempo does fire on the agent — roughly 150 seconds in, by which point the actor has finished.

---

### D1.1 — From alert queue to loop operator

`AI for Security`

- **Risk** — Supervising by re-reading everything the loop did.
- **Control** — Know what the loop must escalate and sample the rest.
- **Lab** — Run a triage loop over Wazuh alerts and supervise by exception.
- **Tools** — `Wazuh`, `OpenSearch`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

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
- **Open-weight models** — `GLM-4.6`, `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

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
- **Open-weight models** — `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

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
- **Open-weight models** — `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

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
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

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
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

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

### D1.9 — Detections whose subject is the agent platform

`AI for Security`

- **Risk** — Platform-layer compromise is invisible to workload-layer detection. The escape, the poisoned cache entry and the silently expired exemption all look like normal operation from inside.
- **Control** — Named escape primitives rather than anomaly scoring (C1.4), cache integrity diffing against a manifest (C5.4), upload scanning (C3.4), secret scanning wired to automated revocation (C4.1), and exemption-state reconciliation (C6.3).
- **Lab** — Run four platform detectors over one day of events and see which of them a generic anomaly score would have missed.
- **Tools** — `Falco`, `Gitleaks`, `Sigstore`

**Run it** — Run four platform detectors over one day of events and find the ones a generic anomaly score would have missed.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.9   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
falco --rules agent-escape.yaml --validate
python3 cache_diff.py --manifest build-manifest.json --repo artifactory
gitleaks detect --redact --report-format sarif
```

*Expect:* Four named rules fire on a seven-event escape sequence that scores 0.07 on a generic volume anomaly. The orphaned-process rule isolates the one background process that outlived its tool call. The cache diff reports one modified, one unexpected and one missing artifact; automated revocation closes a credential in 2 minutes against 240 with a human in the loop; and exemption reconciliation raises a P1 for both an expired exemption and an unapproved one.

---

### D1.10 — Fleet-level correlation: seeing a swarm

`AI for Security`

- **Risk** — Coordination between runs that are supposed to be independent is invisible to per-run analysis by construction. Every run looks normal; the population does not.
- **Control** — Fleet-level analytics (C8.1), coordination signatures (C8.4), write-pattern anomalies (C2.4), a covert-channel inventory (C2.3), scope-expansion logging (C7.4) and noticed-but-unreported telemetry (C9.3, C9.2).
- **Lab** — Run per-run monitoring over a coordinated fleet and see nothing, then run the same data through a shared-artifact graph.
- **Tools** — `OpenTelemetry`, `Sigma`

**Run it** — Run per-run monitoring over a coordinated fleet and see nothing, then run the same data through a shared-artefact graph.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D1.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D1.10   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
python3 fleet_graph.py --window 24h --min-unrelated-readers 2
python3 fleet_graph.py --signatures vocab,pivot,role
```

*Expect:* Five runs pass every per-run check with nothing to report. The shared-artefact graph then shows one object written by one run and read by three unrelated ones, three novel tokens shared across runs, four of five runs pivoting in the same hour, and role differentiation between the runs that write and the runs that read. Three trajectories show the agent noticed something reportable and none of them reached a human.

---

**Adjacency requirement:** also complete A2.3–A2.4 — the failures happen in the seams.
