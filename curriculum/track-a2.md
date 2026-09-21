# Track A2 — Harness Engineering — Making a Demo Into a System

**Function A · Getting Started — Building Agentic AI**  
*Build the system first. A working agentic platform — the loop, MCP tools, identity and delegation, memory, agent-to-agent messaging, a human gate, spans and an audit trail — and the harness that makes it operable. Everything the other four functions attack, defend, detect and govern is built here, by you, before any of it is called a risk.*

**Job titles:** The same audience, one chapter later. Particularly anyone who has to operate, review or sign off on something an agent does.

**What changes:** Five lessons on the machinery that turns a loop that worked once into a system somebody can run: spans, an audit trail that answers the four investigation questions, an evaluation suite with intervals, and the handover that re-reads everything you built as an attack surface. 5 lessons.

**Autonomy focus:** Autonomy becomes reviewable here. Nothing is granted that cannot be observed, evidenced and stopped.

**Deliverable:** A traced, audited, evaluated agent — and its blast radius, measured.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### A2.0 — Why a demo is not a system — the harness around the loop

- **Risk** — A demo promoted to production carries none of the machinery an incident needs, and the first investigation discovers that at the worst moment.
- **Control** — Spans, an audit trail, an evaluation, and a stop — built before they are needed.
- **Lab** — List what your run currently cannot tell an operator.
- **Tools** — `OpenTelemetry`

**Run it** — List what your run currently cannot tell an operator.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A2.0

# --- 3 · in your agent, open this folder and pick the skill:
#         a2-0-why-a-demo-is-not-a-system
#         (Claude Code and Copilot: /a2-0-why-a-demo-is-not-a-system · Cursor: type / and
#         search · Codex: $a2-0-why-a-demo-is-not-a-system). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.0
```

---

### A2.1 — Observability — the run as spans

- **Risk** — A trace holding only successful calls hides exactly the events worth alerting on, and a token pasted into a span is a credential in the log pipeline.
- **Control** — One trace id joining the reasoning to the audit row; refusals as first-class spans.
- **Lab** — Emit a run's spans and join them to the audit log by trace id.
- **Tools** — `OpenTelemetry`, `Grafana`

**Run it** — Emit a run's spans and join them to the audit log by trace id.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A2.1

# --- 3 · in your agent, open this folder and pick the skill:
#         a2-1-observability
#         (Claude Code and Copilot: /a2-1-observability · Cursor: type / and
#         search · Codex: $a2-1-observability). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.1
```

---

### A2.2 — The audit trail, and the four questions it has to answer

- **Risk** — An append-only log the workload can still edit proves nothing, and one that records only successes cannot show what was attempted.
- **Control** — Append-only storage, the delegation chain on every row, and refusals recorded alongside actions.
- **Lab** — Put the four questions to your own audit rows and record which one fails.
- **Tools** — `in-toto`, `Sigstore`

**Run it** — Put the four questions to your own audit rows and record which one fails.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A2.2

# --- 3 · in your agent, open this folder and pick the skill:
#         a2-2-the-audit-trail
#         (Claude Code and Copilot: /a2-2-the-audit-trail · Cursor: type / and
#         search · Codex: $a2-2-the-audit-trail). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.2
```

---

### A2.3 — Evaluating what you built, before anybody attacks it

- **Risk** — A suite everything passes measures nothing, and a score with no interval is a number that will move next week and nobody will know why.
- **Control** — Cases that fail on the old build and pass on the new one, scored with intervals.
- **Lab** — Run the suite, then dilute it with easy cases and watch the score rise.
- **Tools** — `promptfoo`, `Inspect`

**Run it** — Run the suite, then dilute it with easy cases and watch the score rise.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A2.3

# --- 3 · in your agent, open this folder and pick the skill:
#         a2-3-evaluating-what-you-built
#         (Claude Code and Copilot: /a2-3-evaluating-what-you-built · Cursor: type / and
#         search · Codex: $a2-3-evaluating-what-you-built). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.3
```

---

### A2.4 — What you have built — and every way it can now go wrong

- **Risk** — Builders who never see their own system described adversarially ship the same defect in the next one.
- **Control** — The same architecture map, annotated with what an attacker reaches for at each edge.
- **Lab** — Compute the blast radius of the agent you just built.
- **Tools** — `MITRE ATLAS`

**Run it** — Compute the blast radius of the agent you just built.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A2.4

# --- 3 · in your agent, open this folder and pick the skill:
#         a2-4-what-you-have-built
#         (Claude Code and Copilot: /a2-4-what-you-have-built · Cursor: type / and
#         search · Codex: $a2-4-what-you-have-built). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.4
```

---
