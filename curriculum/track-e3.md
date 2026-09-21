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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.1

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-1-from-alert-queue-to-loop-operator
#         (Claude Code and Copilot: /e3-1-from-alert-queue-to-loop-operator · Cursor: type / and
#         search · Codex: $e3-1-from-alert-queue-to-loop-operator). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.1
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.2

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-2-admission-rules
#         (Claude Code and Copilot: /e3-2-admission-rules · Cursor: type / and
#         search · Codex: $e3-2-admission-rules). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.2
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.3

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-3-the-context-that-makes-agent-triage-work
#         (Claude Code and Copilot: /e3-3-the-context-that-makes-agent-triage-work · Cursor: type / and
#         search · Codex: $e3-3-the-context-that-makes-agent-triage-work). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.3
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.4

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-4-when-the-actor-is-an-agent
#         (Claude Code and Copilot: /e3-4-when-the-actor-is-an-agent · Cursor: type / and
#         search · Codex: $e3-4-when-the-actor-is-an-agent). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.4
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.5

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-5-agent-assisted-reconstruction
#         (Claude Code and Copilot: /e3-5-agent-assisted-reconstruction · Cursor: type / and
#         search · Codex: $e3-5-agent-assisted-reconstruction). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.5
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.6

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-6-plan
#         (Claude Code and Copilot: /e3-6-plan · Cursor: type / and
#         search · Codex: $e3-6-plan). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.6
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.7

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-7-scoping-an-agentic-incident
#         (Claude Code and Copilot: /e3-7-scoping-an-agentic-incident · Cursor: type / and
#         search · Codex: $e3-7-scoping-an-agentic-incident). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.7
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.8

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-8-fleet-level-correlation
#         (Claude Code and Copilot: /e3-8-fleet-level-correlation · Cursor: type / and
#         search · Codex: $e3-8-fleet-level-correlation). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.8
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.9

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-9-third-party-threat-intelligence
#         (Claude Code and Copilot: /e3-9-third-party-threat-intelligence · Cursor: type / and
#         search · Codex: $e3-9-third-party-threat-intelligence). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.9
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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E3.10

# --- 3 · in your agent, open this folder and pick the skill:
#         e3-10-hunting-in-agent-telemetry
#         (Claude Code and Copilot: /e3-10-hunting-in-agent-telemetry · Cursor: type / and
#         search · Codex: $e3-10-hunting-in-agent-telemetry). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E3.10
```

---
