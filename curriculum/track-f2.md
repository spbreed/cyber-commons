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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.1

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-1-the-regulatory-map
#         (Claude Code and Copilot: /f2-1-the-regulatory-map · Cursor: type / and
#         search · Codex: $f2-1-the-regulatory-map). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.1
```

---

### F2.2 — AI laws that apply across sectors

- **Risk** — "We only deployed it, we didn't build it" — sometimes true, often not.
- **Control** — Risk classification, GPAI obligations, transparency duties, and how agentic deployment changes classification.
- **Lab** — Classify three workflows and defend the boundary cases.

**Run it** — Classify three workflows and defend the boundary cases.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.2

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-2-ai-laws-that-apply-across-sectors
#         (Claude Code and Copilot: /f2-2-ai-laws-that-apply-across-sectors · Cursor: type / and
#         search · Codex: $f2-2-ai-laws-that-apply-across-sectors). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.2
```

---

### F2.3 — Voluntary frameworks

- **Risk** — Regime-specific mappings with nothing to hang off.
- **Control** — AI RMF / management-system standards as the structure; regulator mappings as overlays.
- **Lab** — Hang two regulator mappings off one framework spine.
- **Tools** — `NIST AI RMF`, `OSCAL`

**Run it** — Hang two regulator mappings off one framework spine.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.3

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-3-voluntary-frameworks
#         (Claude Code and Copilot: /f2-3-voluntary-frameworks · Cursor: type / and
#         search · Codex: $f2-3-voluntary-frameworks). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.3
```

---

### F2.4 — Sector rules

- **Risk** — An agent is already a "model" under model-risk rules you already comply with.
- **Control** — Find the regime you're already in before inventing a new one.
- **Lab** — Map one agent to existing model-risk obligations.

**Run it** — Map one agent to existing model-risk obligations.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.4

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-4-sector-rules
#         (Claude Code and Copilot: /f2-4-sector-rules · Cursor: type / and
#         search · Codex: $f2-4-sector-rules). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.4
```

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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.5

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-5-privacy-and-data-protection
#         (Claude Code and Copilot: /f2-5-privacy-and-data-protection · Cursor: type / and
#         search · Codex: $f2-5-privacy-and-data-protection). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.5
```

---

### F2.6 — Incident reporting duties

- **Risk** — Materiality assessed for an autonomous actor with a human-actor playbook.
- **Control** — Coordinate with E2 in hour one.
- **Lab** — Draft the notification for an agentic incident.

**Run it** — Draft the notification for an agentic incident.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.6

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-6-incident-reporting-duties
#         (Claude Code and Copilot: /f2-6-incident-reporting-duties · Cursor: type / and
#         search · Codex: $f2-6-incident-reporting-duties). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.6
```

---

### F2.7 — Documentation for supervisors

- **Risk** — "Explainability" for a system with no deterministic reasoning.
- **Control** — System documentation, data lineage, eval records, oversight evidence, decision logs.
- **Lab** — Assemble the pack for one high-risk workflow.
- **Tools** — `OSCAL`, `Model Cards`

**Run it** — Assemble the pack for one high-risk workflow.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.7

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-7-documentation-for-supervisors
#         (Claude Code and Copilot: /f2-7-documentation-for-supervisors · Cursor: type / and
#         search · Codex: $f2-7-documentation-for-supervisors). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.7
```

---

### F2.8 — Auditing autonomous actions

- **Risk** — No trail showing under whose authority the agent acted.
- **Control** — The delegation chain *is* the audit trail.
- **Lab** — Produce an audit trail from the B2 chain that names authority at every hop.
- **Tools** — `Keycloak`

**Run it** — Produce an audit trail from the B2 chain that names authority at every hop.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.8

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-8-auditing-autonomous-actions
#         (Claude Code and Copilot: /f2-8-auditing-autonomous-actions · Cursor: type / and
#         search · Codex: $f2-8-auditing-autonomous-actions). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.8
```

---

### F2.9 — Talking to regulators and auditors

- **Risk** — Overclaiming control, or triggering a moratorium.
- **Control** — Explain bounded autonomy with evidence, and anticipate the real questions.
- **Lab** — Defend one workflow in a mock supervisory conversation.

**Run it** — Defend one workflow in a mock supervisory conversation.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F2.9

# --- 3 · in your agent, open this folder and pick the skill:
#         f2-9-talking-to-regulators-and-auditors
#         (Claude Code and Copilot: /f2-9-talking-to-regulators-and-auditors · Cursor: type / and
#         search · Codex: $f2-9-talking-to-regulators-and-auditors). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F2.9
```

---
