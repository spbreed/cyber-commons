# Track E3 — Running the Programme — the CISO Office

**Function E · AI Governance for Agentic Systems**  
*Governing autonomy rather than approving tools: the register, the obligations and the programme that keep CyberTravels defensible.*

**Job titles:** BISO, Deputy CISO, Head of Security Strategy, CISO

**What changes:** Sequencing, org design, metrics and stop authority for an estate that will not stop at four agents. 8 lessons.

**Autonomy focus:** You hold the authority to move any workflow down a rung — and the obligation to use it.

**Deliverable:** A one-page autonomy governance policy and a board-level narrative for one agentic programme.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### E3.1 — Translating agentic risk upward

- **Risk** — Blast radius explained in engineering terms to a board that needs consequence.
- **Control** — What can happen, how fast, who can stop it.
- **Lab** — Convert one blast-radius measurement into a board paragraph.

**Run it** — Convert one blast-radius measurement into a board paragraph.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/programme/risk-translation-upward/scripts/risk_translation_upward.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* What can happen, how fast, who can stop it — with the engineering vocabulary stripped out.

---

### E3.2 — Governing autonomy rather than approving tools

- **Risk** — A per-tool review queue becomes a bottleneck and then a bypass.
- **Control** — A policy on delegated authority instead of tool-by-tool approval.
- **Lab** — Write the delegated-authority policy.

**Run it** — Write the delegated-authority policy.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/programme/autonomy-ladder-decisions/scripts/autonomy_ladder_decisions.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* The linter rejects aspirational language and demands named authority.

---

### E3.3 — Sequencing the programme

- **Risk** — Starting with the workflow that is most visible rather than most winnable.
- **Control** — Use the maturity model to order investment; choose your first hard "no".
- **Lab** — Sequence your first three workflows and name the no.

**Run it** — Sequence your first three workflows and name the no.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/programme/programme-sequencing/scripts/programme_sequencing.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Ordered by winnability × risk retired, with one explicit refusal. A programme without a 'no' has no policy.

---

### E3.4 — Org design and ownership

- **Risk** — Harness engineering with no home; research as a hobby.
- **Control** — Identity owns the control plane; BUs own grants; security owns stop authority.
- **Lab** — Draw your org's ownership map against the topic matrix.

**Run it** — Draw your org's ownership map against the topic matrix.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/programme/ownership-seam-audit/scripts/ownership_seam_audit.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Every topic cluster with zero owners or two owners is a finding — usually harness engineering and research.

---

### E3.5 — The metrics that matter at your level

- **Risk** — Reporting activity instead of exposure.
- **Control** — Inventory coverage, attested-identity share, standing-access reduction, MTT-revoke, blast-radius distribution, eval-gate pass rate.
- **Lab** — Instrument the six metrics from your lab stack.
- **Tools** — `OpenSearch`

**Run it** — Instrument the six metrics from your lab stack.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/programme/programme-metrics-selection/scripts/programme_metrics_selection.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Inventory coverage, attested-identity share, standing-access reduction, MTT-revoke, blast-radius distribution, eval-gate pass rate.

---

### E3.6 — Saying no, and saying yes with conditions

- **Risk** — Conditional approval that is aspirational rather than enforceable.
- **Control** — Autonomy promotion as an earned event with named evidence.
- **Lab** — Write one enforceable conditional approval.

**Run it** — Write one enforceable conditional approval.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/programme/conditional-approval-design/scripts/conditional_approval_design.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Any condition that cannot be automatically verified is flagged. 'They'll be careful' does not compile.

---

### E3.7 — Building the capability

- **Risk** — Hiring for conceptual familiarity instead of practice.
- **Control** — Interview questions that separate the two; internal transition paths.
- **Lab** — Write the interview loop for an agentic security engineer.

**Run it** — Write the interview loop for an agentic security engineer.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/programme/capability-build-order/scripts/capability_build_order.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Questions with artefacts attached. Handing a candidate a real eval report separates the two groups fast.

---

### E3.8 — Resilience over perfection

- **Risk** — Trying to enumerate every failure mode of a probabilistic system.
- **Control** — Maturity measured by containment, detection and recovery — not prevention.
- **Lab** — Re-score your programme on the resilience axis.

**Run it** — Re-score your programme on the resilience axis.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 3 · run the skill against its committed fixture ---
python3 skills/programme/resilience-readiness-check/scripts/resilience_readiness_check.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Prevention-only scoring flatters you. The resilience axes are where a probabilistic system is actually judged.

---
