# Track E3 — Understand — Correlation, Intel and the Hunt

**Function E · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** Incident Responder, SOC Analyst, DFIR Lead, Threat Hunter, Threat Intelligence Analyst

**What changes:** Understanding what happened and who is doing it: an investigation bounded before it starts, a trace where the first theory was abandoned in the open, scope along the delegation graph, correlation across the population, third-party intel that names the tactic, and a hunt for what no rule covers. 10 lessons.

**Autonomy focus:** The investigating agent runs at L2.5 — broad read, bounded per investigation class, every refusal logged with its query.

**Deliverable:** One agentic incident understood end to end, plus one scored hunt with its hypothesis and population stated up front.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### E3.1 — From alert queue to loop operator

- **Risk** — Supervising by re-reading everything the loop did.
- **Control** — Know what the loop must escalate and sample the rest.
- **Lab** — Run a triage loop over Wazuh alerts and supervise by exception.
- **Tools** — `Wazuh`, `OpenSearch`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Run a triage loop over Wazuh alerts and supervise by exception.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.1:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.1 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.1 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/triage-loop-with-floor/scripts/triage_loop_with_floor.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.2 — Admission rules — what the investigating agent may touch

- **Risk** — The investigation is itself the breach: an agent granted broad read to 'find the problem' exfiltrates more than the incident did.
- **Control** — A declared admission set per investigation class, enforced at the tool boundary and logged, with anything outside it requiring a human grant.
- **Lab** — Run an investigation against an admission set and watch the out-of-scope queries get refused and recorded.
- **Tools** — `OPA`

**Run it** — Run an investigation against an admission set and watch the out-of-scope queries get refused and recorded.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.2:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.2 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.2 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/secops/investigation-admission-rules/scripts/investigation_admission_rules.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.3 — The context that makes agent triage work

- **Risk** — Generic triage agents underperform your worst analyst.
- **Control** — Feed the baseline, known FPs, crown-jewel map and prior decisions.
- **Lab** — A/B a generic prompt vs a context-loaded one on the same alert set.
- **Tools** — `Wazuh`
- **Open-weight models** — `GLM-4.6`, `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — A/B a generic prompt vs a context-loaded one on the same alert set.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.3:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.3 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.3 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/secops/detection-triage/scripts/detection_triage.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.4 — When the actor is an agent — three instincts that misfire

- **Risk** — "Which user" is now the wrong first question.
- **Control** — Attribute to agent, authority, delegation chain and prompt.
- **Lab** — Attribute an incident through the B2 `act` chain.
- **Tools** — `Keycloak`, `OpenSearch`

**Run it** — Attribute an incident through the B2 `act` chain.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.4:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.4 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.4 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/response/agent-actor-containment/scripts/agent_actor_containment.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.5 — Agent-assisted reconstruction — a timeline you can challenge

- **Risk** — Reaching for the agent once you're already behind.
- **Control** — Pre-load logs, telemetry, segmentation model and playbooks.
- **Lab** — Reconstruct a timeline from raw logs with a context-loaded agent.
- **Tools** — `Velociraptor`, `OpenSearch`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Reconstruct a timeline from raw logs with a context-loaded agent.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.5:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.5 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.5 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/response/incident-reconstruction-check/scripts/incident_reconstruction_check.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.6 — Plan, then replan — an investigation that changes its mind

- **Risk** — The agent anchors on its first hypothesis and spends the whole incident gathering evidence for it.
- **Control** — An explicit plan record with a replan trigger, so an abandoned branch is visible in the trace rather than silently dropped.
- **Lab** — Feed contradicting evidence mid-investigation and check the plan actually changes, and that the abandoned branch is recorded.
- **Tools** — `OpenTelemetry`

**Run it** — Feed contradicting evidence mid-investigation and check the plan actually changes, and that the abandoned branch is recorded.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.6:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.6 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.6 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/secops/investigation-replan-trace/scripts/investigation_replan_trace.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.7 — Scoping an agentic incident — following the delegation graph

- **Risk** — The initiating agent is not the acting one.
- **Control** — Reconstruct the action chain across all three planes.
- **Lab** — Scope a multi-agent incident end to end.
- **Tools** — `OpenTelemetry`
- **Open-weight models** — `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Scope a multi-agent incident end to end.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.7:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.7 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.7 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/secops/incident-scoping/scripts/incident_scoping.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.8 — Fleet-level correlation — seeing a swarm

- **Risk** — Coordination between runs that are supposed to be independent is invisible to per-run analysis by construction. Every run looks normal; the population does not.
- **Control** — Fleet-level analytics (C8.1), coordination signatures (C8.4), write-pattern anomalies (C2.4), a covert-channel inventory (C2.3), scope-expansion logging (C7.4) and noticed-but-unreported telemetry (C9.3, C9.2).
- **Lab** — Run per-run monitoring over a coordinated fleet and see nothing, then run the same data through a shared-artifact graph.
- **Tools** — `OpenTelemetry`, `Sigma`

**Run it** — Run per-run monitoring over a coordinated fleet and see nothing, then run the same data through a shared-artifact graph.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.8:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.8 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.8 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/fleet-correlation-analysis/scripts/fleet_correlation_analysis.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.9 — Third-party threat intelligence, and the tactics it names

- **Risk** — Unsourced confidence in synthesis loops.
- **Control** — Provenance discipline; refuse claims without a source.
- **Lab** — Build a synthesis loop that must cite or abstain.
- **Tools** — `MISP`, `OpenCTI`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Build a synthesis loop that must cite or abstain.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.9:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.9 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.9 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/threat-intel-to-rules/scripts/threat_intel_to_rules.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---

### E3.10 — Hunting in agent telemetry

- **Risk** — Everything not covered by a rule is invisible, and the rules were written against last quarter's agent behaviour.
- **Control** — A standing hunt over agent traces, hypothesis-first, whose confirmed findings graduate into detections rather than staying in a notebook.
- **Lab** — Run three hypotheses over a labelled trace corpus and score what each one catches and misses.
- **Tools** — `OpenTelemetry`

**Run it** — Run three hypotheses over a labelled trace corpus and score what each one catches and misses.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of E3.10:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at E3.10 --out work/cybertravels
python3 scripts/checkpoint.py --at E3.10 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/agent-telemetry-hunt/scripts/agent_telemetry_hunt.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---
