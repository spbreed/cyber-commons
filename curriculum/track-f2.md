# Track F2 — Building the Governance Platform — Regulatory and Compliance

**Function F · AI Governance for Agentic Systems**  
*Governing autonomy rather than approving tools: the register, the obligations and the programme that keep CyberTravels defensible.*

**Job titles:** Compliance Manager, Regulatory Affairs (Tech), Privacy Engineer, AI Governance Lead

**What changes:** What a travel company holding passports, payment and health data owes, to whom, and how to evidence it once rather than per regulator. 9 lessons.

**Autonomy focus:** You determine which action classes are legally prohibited from ever reaching L2.5, irrespective of measured performance.

**Deliverable:** One control set mapped to three regimes, plus an evidence pack for a single high-risk agentic workflow.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### F2.1 — The regulatory map

- **Risk** — One programme per regime; four times the work, none of it joined up.
- **Control** — One control set that satisfies several regimes. Verify current status before relying on any date.
- **Lab** — Build the crosswalk for your own sector.
- **Tools** — `OSCAL`

**Run it** — Build the crosswalk for your own sector.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.1:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.1 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.1 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/obligation-mapping/scripts/obligation_mapping.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* One spine, several overlays. Orphans are your programme backlog.

---

### F2.2 — Horizontal AI regulation

- **Risk** — "We only deployed it, we didn't build it" — sometimes true, often not.
- **Control** — Risk classification, GPAI obligations, transparency duties, and how agentic deployment changes classification.
- **Lab** — Classify three workflows and defend the boundary cases.

**Run it** — Classify three workflows and defend the boundary cases.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.2:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.2 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.2 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/horizontal-requirement-to-control/scripts/horizontal_requirement_to_control.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Shows where 'we only deployed it' holds and where agentic deployment pulls you into provider obligations.

---

### F2.3 — Voluntary frameworks as your spine

- **Risk** — Regime-specific mappings with nothing to hang off.
- **Control** — AI RMF / management-system standards as the structure; regulator mappings as overlays.
- **Lab** — Hang two regulator mappings off one framework spine.
- **Tools** — `NIST AI RMF`, `OSCAL`

**Run it** — Hang two regulator mappings off one framework spine.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.3:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.3 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.3 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/framework-spine-selection/scripts/framework_spine_selection.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Valid OSCAL, one spine, two overlays — instead of two disconnected programmes.

---

### F2.4 — Sector overlays

- **Risk** — An agent is already a "model" under model-risk rules you already comply with.
- **Control** — Find the regime you're already in before inventing a new one.
- **Lab** — Map one agent to existing model-risk obligations.

**Run it** — Map one agent to existing model-risk obligations.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.4:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.4 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.4 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/sector-overlay-assessment/scripts/sector_overlay_assessment.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* The agent is often already a 'model' under rules you already comply with. Cheaper than inventing a new programme.

---

### F2.5 — Privacy and data protection

- **Risk** — Deletion when the data is in weights, not a database.
- **Control** — Lawful basis, ADM rights, residency in inference and retrieval paths, retention of traces.
- **Lab** — Run PII redaction inside the trust boundary with Presidio before anything crosses out.
- **Tools** — `Presidio`, `GLiNER-PII`

**Run it** — Run PII redaction inside the trust boundary with Presidio before anything crosses out.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.5:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.5 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.5 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/trace-personal-data-audit/scripts/trace_personal_data_audit.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* PII is removed before egress; the redaction decision is logged as evidence for F2.7.

---

### F2.6 — Incident and disclosure obligations

- **Risk** — Materiality assessed for an autonomous actor with a human-actor playbook.
- **Control** — Coordinate with E2 in hour one.
- **Lab** — Draft the notification for an agentic incident.

**Run it** — Draft the notification for an agentic incident.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.6:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.6 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.6 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/disclosure-phase-breakdown/scripts/disclosure_phase_breakdown.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* A draft that names the agent, the authority and the containment — the questions a supervisor asks first.

---

### F2.7 — Documentation that survives supervision

- **Risk** — "Explainability" for a system with no deterministic reasoning.
- **Control** — System documentation, data lineage, eval records, oversight evidence, decision logs.
- **Lab** — Assemble the pack for one high-risk workflow.
- **Tools** — `OSCAL`, `Model Cards`

**Run it** — Assemble the pack for one high-risk workflow.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.7:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.7 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.7 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/supervisory-documentation-score/scripts/supervisory_documentation_score.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* A pack with a self-audit attached, including an honest statement of what 'explainability' can mean here.

---

### F2.8 — Auditability of autonomous action

- **Risk** — No trail showing under whose authority the agent acted.
- **Control** — The delegation chain *is* the audit trail.
- **Lab** — Produce an audit trail from the B2 chain that names authority at every hop.
- **Tools** — `Keycloak`

**Run it** — Produce an audit trail from the B2 chain that names authority at every hop.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.8:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.8 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.8 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/autonomous-action-auditability/scripts/autonomous_action_auditability.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Which agent, under whose authority, in what scope, verified by which control, reviewable by whom — all from the `act` chain.

---

### F2.9 — Regulator and auditor conversations

- **Risk** — Overclaiming control, or triggering a moratorium.
- **Control** — Explain bounded autonomy with evidence, and anticipate the real questions.
- **Lab** — Defend one workflow in a mock supervisory conversation.

**Run it** — Defend one workflow in a mock supervisory conversation.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of F2.9:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at F2.9 --out work/cybertravels
python3 scripts/checkpoint.py --at F2.9 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/regulatory/assurance-conversation-prep/scripts/assurance_conversation_prep.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* You get asked the real questions. Overclaiming control is scored as harshly as underclaiming.

---
