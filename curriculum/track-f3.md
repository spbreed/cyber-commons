# Track F3 — Running the Programme — the CISO Office

**Function F · AI Governance for Agentic Systems**  
*Governing autonomy rather than approving tools: the register, the obligations and the programme that keep CyberTravels defensible.*

**Job titles:** BISO, Deputy CISO, Head of Security Strategy, CISO

**What changes:** Sequencing, org design, metrics and stop authority for an estate that will not stop at four agents. 8 lessons.

**Autonomy focus:** You hold the authority to move any workflow down a rung — and the obligation to use it.

**Deliverable:** A one-page autonomy governance policy and a board-level narrative for one agentic programme.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### F3.1 — Translating agentic risk upward

- **Risk** — Blast radius explained in engineering terms to a board that needs consequence.
- **Control** — What can happen, how fast, who can stop it.
- **Lab** — Convert one blast-radius measurement into a board paragraph.

**Run it** — Convert one blast-radius measurement into a board paragraph.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F3.1

# --- 3 · in your agent, open this folder and pick the skill:
#         f3-1-translating-agentic-risk-upward
#         (Claude Code and Copilot: /f3-1-translating-agentic-risk-upward · Cursor: type / and
#         search · Codex: $f3-1-translating-agentic-risk-upward). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F3.1
```

---

### F3.2 — Governing autonomy rather than approving tools

- **Risk** — A per-tool review queue becomes a bottleneck and then a bypass.
- **Control** — A policy on delegated authority instead of tool-by-tool approval.
- **Lab** — Write the delegated-authority policy.

**Run it** — Write the delegated-authority policy.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F3.2

# --- 3 · in your agent, open this folder and pick the skill:
#         f3-2-governing-autonomy-rather-than-approving
#         (Claude Code and Copilot: /f3-2-governing-autonomy-rather-than-approving · Cursor: type / and
#         search · Codex: $f3-2-governing-autonomy-rather-than-approving). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F3.2
```

---

### F3.3 — Sequencing the programme

- **Risk** — Starting with the workflow that is most visible rather than most winnable.
- **Control** — Use the maturity model to order investment; choose your first hard "no".
- **Lab** — Sequence your first three workflows and name the no.

**Run it** — Sequence your first three workflows and name the no.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F3.3

# --- 3 · in your agent, open this folder and pick the skill:
#         f3-3-sequencing-the-programme
#         (Claude Code and Copilot: /f3-3-sequencing-the-programme · Cursor: type / and
#         search · Codex: $f3-3-sequencing-the-programme). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F3.3
```

---

### F3.4 — Org design and ownership

- **Risk** — Harness engineering with no home; research as a hobby.
- **Control** — Identity owns the control plane; BUs own grants; security owns stop authority.
- **Lab** — Draw your org's ownership map against the topic matrix.

**Run it** — Draw your org's ownership map against the topic matrix.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F3.4

# --- 3 · in your agent, open this folder and pick the skill:
#         f3-4-org-design-and-ownership
#         (Claude Code and Copilot: /f3-4-org-design-and-ownership · Cursor: type / and
#         search · Codex: $f3-4-org-design-and-ownership). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F3.4
```

---

### F3.5 — The metrics that matter at your level

- **Risk** — Reporting activity instead of exposure.
- **Control** — Inventory coverage, attested-identity share, standing-access reduction, MTT-revoke, blast-radius distribution, eval-gate pass rate.
- **Lab** — Instrument the six metrics from your lab stack.
- **Tools** — `OpenSearch`

**Run it** — Instrument the six metrics from your lab stack.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F3.5

# --- 3 · in your agent, open this folder and pick the skill:
#         f3-5-the-metrics-that-matter-at-your-level
#         (Claude Code and Copilot: /f3-5-the-metrics-that-matter-at-your-level · Cursor: type / and
#         search · Codex: $f3-5-the-metrics-that-matter-at-your-level). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F3.5
```

---

### F3.6 — Saying no, and saying yes with conditions

- **Risk** — Conditional approval that is aspirational rather than enforceable.
- **Control** — Autonomy promotion as an earned event with named evidence.
- **Lab** — Write one enforceable conditional approval.

**Run it** — Write one enforceable conditional approval.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F3.6

# --- 3 · in your agent, open this folder and pick the skill:
#         f3-6-saying-no
#         (Claude Code and Copilot: /f3-6-saying-no · Cursor: type / and
#         search · Codex: $f3-6-saying-no). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F3.6
```

---

### F3.7 — Building the capability

- **Risk** — Hiring for conceptual familiarity instead of practice.
- **Control** — Interview questions that separate the two; internal transition paths.
- **Lab** — Write the interview loop for an agentic security engineer.

**Run it** — Write the interview loop for an agentic security engineer.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F3.7

# --- 3 · in your agent, open this folder and pick the skill:
#         f3-7-building-the-capability
#         (Claude Code and Copilot: /f3-7-building-the-capability · Cursor: type / and
#         search · Codex: $f3-7-building-the-capability). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F3.7
```

---

### F3.8 — Resilience over perfection

- **Risk** — Trying to enumerate every failure mode of a probabilistic system.
- **Control** — Maturity measured by containment, detection and recovery — not prevention.
- **Lab** — Re-score your programme on the resilience axis.

**Run it** — Re-score your programme on the resilience axis.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons F3.8

# --- 3 · in your agent, open this folder and pick the skill:
#         f3-8-resilience-over-perfection
#         (Claude Code and Copilot: /f3-8-resilience-over-perfection · Cursor: type / and
#         search · Codex: $f3-8-resilience-over-perfection). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py F3.8
```

---
