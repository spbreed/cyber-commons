# Track D3 — Investigate — From an Alert to a Conclusion

**Function D · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** Incident Responder, SOC Analyst, DFIR Lead

**What changes:** An investigation an agent can run: bounded before it starts, given the fields an agent alert needs, willing to abandon its first theory in the open, scoped along the delegation graph, and finally widened to the population. 8 lessons.

**Autonomy focus:** The investigating agent runs at L2.5 — broad read, bounded per investigation class, every refusal logged with its query.

**Deliverable:** One agentic incident scoped end to end, with the abandoned branch still visible in the trace.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### D3.1 — From alert queue to loop operator

- **Risk** — Supervising by re-reading everything the loop did.
- **Control** — Know what the loop must escalate and sample the rest.
- **Lab** — Run a triage loop over Wazuh alerts and supervise by exception.
- **Tools** — `Wazuh`, `OpenSearch`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Run a triage loop over Wazuh alerts and supervise by exception.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D3.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D3.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
docker compose up -d wazuh opensearch
./seed-alerts.sh                       # replayable alert corpus
python3 triage_loop.py --model $MODEL --escalate-on high
```

*Expect:* The loop clears the known-benign and escalates the rest with its reasoning attached.

---

### D3.2 — Admission rules — what the investigating agent may touch

- **Risk** — The investigation is itself the breach: an agent granted broad read to 'find the problem' exfiltrates more than the incident did.
- **Control** — A declared admission set per investigation class, enforced at the tool boundary and logged, with anything outside it requiring a human grant.
- **Lab** — Run an investigation against an admission set and watch the out-of-scope queries get refused and recorded.
- **Tools** — `OPA`

**Run it** — Run an investigation against an admission set and watch the out-of-scope queries get refused and recorded.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D3.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D3.2   # run it headless and check it
```

*Expect:* Run an investigation against an admission set and watch the out-of-scope queries get refused and recorded.

---

### D3.3 — The context that makes agent triage work

- **Risk** — Generic triage agents underperform your worst analyst.
- **Control** — Feed the baseline, known FPs, crown-jewel map and prior decisions.
- **Lab** — A/B a generic prompt vs a context-loaded one on the same alert set.
- **Tools** — `Wazuh`
- **Open-weight models** — `GLM-4.6`, `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — A/B a generic prompt vs a context-loaded one on the same alert set.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D3.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D3.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc
python3 triage_loop.py --context none     --alerts alerts.jsonl --score
python3 triage_loop.py --context loaded   --alerts alerts.jsonl --score   # baseline+FPs+crown jewels
python3 compare.py
```

*Expect:* The generic loop underperforms your worst analyst; the loaded one does not. Same model both times.

---

### D3.4 — When the actor is an agent — three instincts that misfire

- **Risk** — "Which user" is now the wrong first question.
- **Control** — Attribute to agent, authority, delegation chain and prompt.
- **Lab** — Attribute an incident through the A2 `act` chain.
- **Tools** — `Keycloak`, `OpenSearch`

**Run it** — Attribute an incident through the A2 `act` chain.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D3.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D3.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
./replay-incident.sh case-01
python3 attribute.py --trace case-01/trace.jsonl --chain-from keycloak
```

*Expect:* Names the agent, the delegated authority, the hop where scope widened, and the prompt that started it.

---

### D3.5 — Agent-assisted reconstruction — a timeline you can challenge

- **Risk** — Reaching for the agent once you're already behind.
- **Control** — Pre-load logs, telemetry, segmentation model and playbooks.
- **Lab** — Reconstruct a timeline from raw logs with a context-loaded agent.
- **Tools** — `Velociraptor`, `OpenSearch`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Reconstruct a timeline from raw logs with a context-loaded agent.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D3.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D3.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
python3 reconstruct.py --case case-01 --preload logs,telemetry,segmentation,playbooks --model $MODEL
python3 reconstruct.py --case case-01 --preload none --model $MODEL
diff <(jq -r .timeline[] preloaded.json) <(jq -r .timeline[] cold.json)
```

*Expect:* The pre-loaded run produces a usable timeline; the cold one asks you questions you needed answered.

---

### D3.6 — Plan, then replan — an investigation that changes its mind

- **Risk** — The agent anchors on its first hypothesis and spends the whole incident gathering evidence for it.
- **Control** — An explicit plan record with a replan trigger, so an abandoned branch is visible in the trace rather than silently dropped.
- **Lab** — Feed contradicting evidence mid-investigation and check the plan actually changes, and that the abandoned branch is recorded.
- **Tools** — `OpenTelemetry`

**Run it** — Feed contradicting evidence mid-investigation and check the plan actually changes, and that the abandoned branch is recorded.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D3.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D3.6   # run it headless and check it
```

*Expect:* Feed contradicting evidence mid-investigation and check the plan actually changes, and that the abandoned branch is recorded.

---

### D3.7 — Scoping an agentic incident — following the delegation graph

- **Risk** — The initiating agent is not the acting one.
- **Control** — Reconstruct the action chain across all three planes.
- **Lab** — Scope a multi-agent incident end to end.
- **Tools** — `OpenTelemetry`
- **Open-weight models** — `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Scope a multi-agent incident end to end.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D3.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D3.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
./replay-incident.sh case-02   # multi-agent
python3 scope.py --trace case-02/trace.jsonl --planes decision,control,action
```

*Expect:* The action-plane actor is a sub-agent two hops from the prompt that started it.

---

### D3.8 — Fleet-level correlation — seeing a swarm

- **Risk** — Coordination between runs that are supposed to be independent is invisible to per-run analysis by construction. Every run looks normal; the population does not.
- **Control** — Fleet-level analytics (C8.1), coordination signatures (C8.4), write-pattern anomalies (C2.4), a covert-channel inventory (C2.3), scope-expansion logging (C7.4) and noticed-but-unreported telemetry (C9.3, C9.2).
- **Lab** — Run per-run monitoring over a coordinated fleet and see nothing, then run the same data through a shared-artifact graph.
- **Tools** — `OpenTelemetry`, `Sigma`

**Run it** — Run per-run monitoring over a coordinated fleet and see nothing, then run the same data through a shared-artifact graph.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D3.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D3.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
python3 fleet_graph.py --window 24h --min-unrelated-readers 2
python3 fleet_graph.py --signatures vocab,pivot,role
```

*Expect:* Five runs pass every per-run check with nothing to report. The shared-artefact graph then shows one object written by one run and read by three unrelated ones, three novel tokens shared across runs, four of five runs pivoting in the same hour, and role differentiation between the runs that write and the runs that read. Three trajectories show the agent noticed something reportable and none of them reached a human.

---
