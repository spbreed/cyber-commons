# Track A2 — Harness Engineering — Making a Demo Into a System

**Function A · Getting Started — Building Agentic AI**  
*Build the system first. A working agentic platform — the loop, MCP tools, identity and delegation, memory, agent-to-agent messaging, a human gate, spans and an audit trail — and the harness that makes it operable. Each of the nine words for an agent — harness, memory and state, RAG, MCP, skills, guardrails, evals, A2A and multi-agent — is a component built here. Everything the other five functions attack, defend, detect and govern is built here, by you, before any of it is called a risk.*

**Job titles:** The same audience, one chapter later. Particularly anyone who has to operate, review or sign off on something an agent does.

**What changes:** Five lessons on the machinery that turns a loop that worked once into a system somebody can run: spans, an audit trail that answers the four investigation questions, an evaluation suite with intervals, and the handover that re-reads everything you built as an attack surface. 5 lessons.

**Autonomy focus:** Autonomy becomes reviewable here. Nothing is granted that cannot be observed, evidenced and stopped.

**Deliverable:** A traced, audited, evaluated agent — and its blast radius, measured.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### A2.0 — From demo to system

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
#         a2-0-from-demo-to-system
#         (Claude Code and Copilot: /a2-0-from-demo-to-system · Cursor: type / and
#         search · Codex: $a2-0-from-demo-to-system). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.0
```

---

### A2.1 — Tracing a run

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
#         a2-1-tracing-a-run
#         (Claude Code and Copilot: /a2-1-tracing-a-run · Cursor: type / and
#         search · Codex: $a2-1-tracing-a-run). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.1
```

---

### A2.2 — The audit log, and four questions it must answer

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
#         a2-2-the-audit-log
#         (Claude Code and Copilot: /a2-2-the-audit-log · Cursor: type / and
#         search · Codex: $a2-2-the-audit-log). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.2
```

---

### A2.3 — Testing the controls

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
#         a2-3-testing-the-controls
#         (Claude Code and Copilot: /a2-3-testing-the-controls · Cursor: type / and
#         search · Codex: $a2-3-testing-the-controls). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.3
```

---

### A2.4 — Scoring the agent's behaviour

- **Risk** — "The agent is 90% accurate" with no denominator, no matcher named and no judge validation. Three different numbers can be quoted from one run, the most flattering is the easiest to compute, and an unvalidated judge is a second unmeasured model grading the first.
- **Control** — Exact-match tool-call accuracy reported with its n and beside the two weaker matchers, output accuracy with unscoreable runs in their own column, and a judge whose agreement with ground truth is published before its verdicts are.
- **Lab** — Score six agent runs three ways, then check the judge against the runs whose answer you already know.
- **Tools** — `pytest`

**Run it** — Score six agent runs three ways, then check the judge against the runs whose answer you already know.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A2.4

# --- 3 · in your agent, open this folder and pick the skill:
#         a2-4-scoring-the-agents-behaviour
#         (Claude Code and Copilot: /a2-4-scoring-the-agents-behaviour · Cursor: type / and
#         search · Codex: $a2-4-scoring-the-agents-behaviour). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.4
```

---

### A2.5 — What you built, and how it can fail

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
python3 scripts/install_skills.py --all --lessons A2.5

# --- 3 · in your agent, open this folder and pick the skill:
#         a2-5-what-you-built
#         (Claude Code and Copilot: /a2-5-what-you-built · Cursor: type / and
#         search · Codex: $a2-5-what-you-built). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A2.5
```

---
