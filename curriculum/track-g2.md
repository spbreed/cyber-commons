# Track G2 — Harness Engineering — Making a Demo Into a System

**Function G · Getting Started — Building Agentic AI**  
*Build the system first. A working agentic platform — the loop, MCP tools, identity and delegation, memory, agent-to-agent messaging, a human gate, spans and an audit trail — and the harness that makes it operable. Everything the other four functions attack, defend, detect and govern is built here, by you, before any of it is called a risk.*

**Job titles:** The same audience, one chapter later. Particularly anyone who has to operate, review or sign off on something an agent does.

**What changes:** Five lessons on the machinery that turns a loop that worked once into a system somebody can run: spans, an audit trail that answers the four investigation questions, an evaluation suite with intervals, and the handover that re-reads everything you built as an attack surface. 5 lessons.

**Autonomy focus:** Autonomy becomes reviewable here. Nothing is granted that cannot be observed, evidenced and stopped.

**Deliverable:** A traced, audited, evaluated agent — and its blast radius, measured.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### G2.0 — Why a demo is not a system — the harness around the loop

- **Risk** — A demo promoted to production carries none of the machinery an incident needs, and the first investigation discovers that at the worst moment.
- **Control** — Spans, an audit trail, an evaluation, and a stop — built before they are needed.
- **Lab** — List what your run currently cannot tell an operator.
- **Tools** — `OpenTelemetry`

**Run it** — List what your run currently cannot tell an operator.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G2.0:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G2.0 --out work/cybertravels
python3 scripts/checkpoint.py --at G2.0 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/threats/audit-answerability-check/scripts/audit_answerability_check.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* An investigation's questions put to what the run currently emits, and a named list of the ones it cannot answer. Expect most of them — that is why this runs first.

---

### G2.1 — Observability — the run as spans

- **Risk** — A trace holding only successful calls hides exactly the events worth alerting on, and a token pasted into a span is a credential in the log pipeline.
- **Control** — One trace id joining the reasoning to the audit row; refusals as first-class spans.
- **Lab** — Emit a run's spans and join them to the audit log by trace id.
- **Tools** — `OpenTelemetry`, `Grafana`

**Run it** — Emit a run's spans and join them to the audit log by trace id.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G2.1:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G2.1 --out work/cybertravels
python3 scripts/checkpoint.py --at G2.1 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/response/run-replayability-audit/scripts/run_replayability_audit.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* A run's spans in order, each carrying the trace id, tokens present only as summarised claims, and every refusal appearing with the boundary that produced it.

---

### G2.2 — The audit trail, and the four questions it has to answer

- **Risk** — An append-only log the workload can still edit proves nothing, and one that records only successes cannot show what was attempted.
- **Control** — Append-only storage, the delegation chain on every row, and refusals recorded alongside actions.
- **Lab** — Put the four questions to your own audit rows and record which one fails.
- **Tools** — `in-toto`, `Sigstore`

**Run it** — Put the four questions to your own audit rows and record which one fails.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G2.2:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G2.2 --out work/cybertravels
python3 scripts/checkpoint.py --at G2.2 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/identity/attribution-ledger-check/scripts/attribution_ledger_check.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Each of the four questions answered or explicitly not, from real audit rows — with the fourth likely failing, which is the finding to carry into Function D.

---

### G2.3 — Evaluating what you built, before anybody attacks it

- **Risk** — A suite everything passes measures nothing, and a score with no interval is a number that will move next week and nobody will know why.
- **Control** — Cases that fail on the old build and pass on the new one, scored with intervals.
- **Lab** — Run the suite, then dilute it with easy cases and watch the score rise.
- **Tools** — `promptfoo`, `Inspect`

**Run it** — Run the suite, then dilute it with easy cases and watch the score rise.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G2.3:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G2.3 --out work/cybertravels
python3 scripts/checkpoint.py --at G2.3 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/research/eval-suite-health-check/scripts/eval_suite_health_check.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* A score with a confidence interval, a control shown to move one surface and not the others, and the same suite scoring higher once easy cases are added.

---

### G2.4 — What you have built — and every way it can now go wrong

- **Risk** — Builders who never see their own system described adversarially ship the same defect in the next one.
- **Control** — The same architecture map, annotated with what an attacker reaches for at each edge.
- **Lab** — Compute the blast radius of the agent you just built.
- **Tools** — `MITRE ATLAS`

**Run it** — Compute the blast radius of the agent you just built.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G2.4:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G2.4 --out work/cybertravels
python3 scripts/checkpoint.py --at G2.4 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/architecture/blast-radius-review/scripts/blast_radius_review.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Objects one run can reach, the subset it can change, the irreversible actions among those, and the autonomy level that radius supports.

---
