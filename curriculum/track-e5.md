# Track E5 — Recover and Root Cause — From Stopped to Back at Target

**Function E · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** Incident Responder, DFIR Lead, Security Programme Manager, Regulatory Liaison

**What changes:** The part after containment: a run you can reproduce, a root cause that names a control, the fix placed at the layer it belongs in, the indicators re-measured, the policy changed as a diff — and a regulatory clock that started before anyone knew. 6 lessons.

**Autonomy focus:** Returning a fleet to the autonomy level the incident interrupted is an earned event, evidenced by an indicator back at target.

**Deliverable:** A closed incident record: root cause, layer, policy diff, and the indicators that did and did not come back.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### E5.1 — Replay and forensics — reproducing a run you can defend

- **Risk** — Non-determinism as an evidentiary problem.
- **Control** — Log at design time what replay will need.
- **Lab** — Replay an agent run for a regulator-grade record.
- **Tools** — `OpenTelemetry`

**Run it** — Replay an agent run for a regulator-grade record.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E5.1

# --- 3 · in your agent, open this folder and pick the skill:
#         e5-1-replay-and-forensics
#         (Claude Code and Copilot: /e5-1-replay-and-forensics · Cursor: type / and
#         search · Codex: $e5-1-replay-and-forensics). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E5.1
```

---

### E5.2 — The root cause record — naming a control, not a person

- **Risk** — The incident closes with a narrative, so the same control gap produces the same incident two quarters later.
- **Control** — A structured root cause record naming the failed control, the detection that should have fired, and the specific change proposed.
- **Lab** — Build a root cause record from a reconstructed incident and check it names a control rather than a person.

**Run it** — Build a root cause record from a reconstructed incident and check it names a control rather than a person.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E5.2

# --- 3 · in your agent, open this folder and pick the skill:
#         e5-2-the-root-cause-record
#         (Claude Code and Copilot: /e5-2-the-root-cause-record · Cursor: type / and
#         search · Codex: $e5-2-the-root-cause-record). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E5.2
```

---

### E5.3 — Post-incident change surface — picking the layer the fix belongs in

- **Risk** — Fixing the prompt when the bug is in the control plane.
- **Control** — Choose among model, prompt, tool, policy, sandbox, identity, eval.
- **Lab** — Pick the right layer for five real incidents.

**Run it** — Pick the right layer for five real incidents.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E5.3

# --- 3 · in your agent, open this folder and pick the skill:
#         e5-3-post-incident-change-surface
#         (Claude Code and Copilot: /e5-3-post-incident-change-surface · Cursor: type / and
#         search · Codex: $e5-3-post-incident-change-surface). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E5.3
```

---

### E5.4 — Validating the fix — re-measuring the indicators the incident moved

- **Risk** — The remediation is marked done because the ticket closed, not because the control it restored was measured.
- **Control** — Automatic re-measurement of the affected KCIs after a fix, with the before-and-after attached to the incident record.
- **Lab** — Re-run the KCI measurement against a fixed estate and show which indicators recovered and which did not.
- **Tools** — `OPA`

**Run it** — Re-run the KCI measurement against a fixed estate and show which indicators recovered and which did not.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E5.4

# --- 3 · in your agent, open this folder and pick the skill:
#         e5-4-validating-the-fix
#         (Claude Code and Copilot: /e5-4-validating-the-fix · Cursor: type / and
#         search · Codex: $e5-4-validating-the-fix). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E5.4
```

---

### E5.5 — Proposing the policy change — the diff, and what it does not fix

- **Risk** — The lesson from the incident lives in a postmortem document nobody reads, and the policy that permitted it is unchanged.
- **Control** — A policy change proposal generated from the root cause record, as a diff with the incident as its evidence.
- **Lab** — Generate a policy diff from a root cause record and review what it would have prevented.
- **Tools** — `OPA`

**Run it** — Generate a policy diff from a root cause record and review what it would have prevented.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E5.5

# --- 3 · in your agent, open this folder and pick the skill:
#         e5-5-proposing-the-policy-change
#         (Claude Code and Copilot: /e5-5-proposing-the-policy-change · Cursor: type / and
#         search · Codex: $e5-5-proposing-the-policy-change). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E5.5
```

---

### E5.6 — The regulatory clock — awareness, not confirmation

- **Risk** — Notification obligations discovered in week two.
- **Control** — Feed Track F2 in hour one.
- **Lab** — Run the first-hour checklist in a tabletop.

**Run it** — Run the first-hour checklist in a tabletop.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E5.6

# --- 3 · in your agent, open this folder and pick the skill:
#         e5-6-the-regulatory-clock
#         (Claude Code and Copilot: /e5-6-the-regulatory-clock · Cursor: type / and
#         search · Codex: $e5-6-the-regulatory-clock). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E5.6
```

---
