# Track D1 — Discover — the Sensors, and the Agent-Shaped Hole in Them

**Function D · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** SOC Analyst, Security Engineer, Cloud Security Engineer, Security Data Engineer

**What changes:** What already watches the estate — EDR, DLP, CSPM, CNAPP — what each sees when the actor is an agent, the drift that arrives without a code change, and a bonus on finding the agents nobody registered. 4 lessons.

**Autonomy focus:** You watch an L2.5 fleet with four products bought for L0 humans, and the uncovered column gets named rather than assumed.

**Deliverable:** A sensor coverage matrix for your own estate, with the agent actions no sensor class covers listed by name.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### D1.0 — Start here — the agentic SOC, and the stack that runs it

- **Risk** — A detection stack tuned for human tempo, watching an actor that acts a thousand times an hour and never repeats a session.
- **Control** — Agent telemetry as a first-class data source, detections written for agent behaviour, and a stop lever that a human can actually pull in time.
- **Lab** — Put one agent trace and one human session side by side and list what separates them.

**Run it** — Put one agent trace and one human session side by side and list what separates them.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/detection/agent-tempo-baseline/scripts/agent_tempo_baseline.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Five behavioural signals print for a person and an agent over the same hour, with ratios in the hundreds. A volume rule tuned for human tempo does fire on the agent — roughly 150 seconds in, by which point the actor has finished.

---

### D1.1 — The sensor estate — EDR, DLP, CSPM and CNAPP against an agent

- **Risk** — Four products are bought, the estate is assumed covered, and the agent's whole working day falls between them.
- **Control** — A coverage matrix computed per sensor and per agent action, with the uncovered actions named rather than counted.
- **Lab** — Score four sensor classes against nine real agent actions and read the column none of them covers.
- **Tools** — `Wazuh`, `Prowler`, `Falco`

---

### D1.2 — Drift monitoring — behaviour that changes without a code change

- **Risk** — A detection that worked last month is silently degraded.
- **Control** — Watch model updates, prompt changes, index refreshes, tool versions.
- **Lab** — Change the model underneath and catch the detection regression.
- **Tools** — `promptfoo`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Change the model underneath and catch the detection regression.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/detection/behavioural-drift-monitor/scripts/behavioural_drift_monitor.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* A rule that passed last month fails now. Nothing in your code changed.

---

### D1.3 — Bonus — finding the agents, and keeping what they emit

- **Risk** — Prompts, traces, tool calls and approvals never reach the SIEM.
- **Control** — Onboard agent telemetry deliberately; decide retention.
- **Lab** — Ship OTEL agent traces into OpenSearch and query them.
- **Tools** — `OpenTelemetry`, `OpenSearch`

**Run it** — Ship OTEL agent traces into OpenSearch and query them.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/detection/agent-versus-human-scoring/scripts/agent_versus_human_scoring.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* A working classifier — your earliest Shadow Autonomy signal.

---

**Adjacency requirement:** also complete A2.3–A2.4 — the failures happen in the seams.
