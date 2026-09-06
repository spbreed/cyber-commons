# Track D5 — The Agentic SOC — Recover and Root Cause

**Function D · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** 

**What changes:** 

**Autonomy focus:** 

**Deliverable:** 

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### D5.1 — Replay and forensics

- **Risk** — Non-determinism as an evidentiary problem.
- **Control** — Log at design time what replay will need.
- **Lab** — Replay an agent run for a regulator-grade record.
- **Tools** — `OpenTelemetry`

**Run it** — Replay an agent run for a regulator-grade record.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D5.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D5.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
python3 replay.py --trace case-01/trace.jsonl --assert-deterministic
```

*Expect:* The run reproduces, or the tool tells you exactly which field was never logged to make replay possible.

---

### D5.2 — The root cause record

- **Risk** — The incident closes with a narrative, so the same control gap produces the same incident two quarters later.
- **Control** — A structured root cause record naming the failed control, the detection that should have fired, and the specific change proposed.
- **Lab** — Build a root cause record from a reconstructed incident and check it names a control rather than a person.

**Run it** — Build a root cause record from a reconstructed incident and check it names a control rather than a person.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D5.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D5.2   # run it headless and check it
```

*Expect:* Build a root cause record from a reconstructed incident and check it names a control rather than a person.

---

### D5.3 — Validating the fix against the KCIs

- **Risk** — The remediation is marked done because the ticket closed, not because the control it restored was measured.
- **Control** — Automatic re-measurement of the affected KCIs after a fix, with the before-and-after attached to the incident record.
- **Lab** — Re-run the KCI measurement against a fixed estate and show which indicators recovered and which did not.
- **Tools** — `OPA`

**Run it** — Re-run the KCI measurement against a fixed estate and show which indicators recovered and which did not.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D5.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D5.3   # run it headless and check it
```

*Expect:* Re-run the KCI measurement against a fixed estate and show which indicators recovered and which did not.

---

### D5.4 — Post-incident change surface

- **Risk** — Fixing the prompt when the bug is in the control plane.
- **Control** — Choose among model, prompt, tool, policy, sandbox, identity, eval.
- **Lab** — Pick the right layer for five real incidents.

**Run it** — Pick the right layer for five real incidents.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D5.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D5.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir/postmortem
for c in case-*/; do echo -n "$c "; python3 ../choose_layer.py --case $c; done
```

*Expect:* Most land on the control plane — identity, policy, sandbox — not the prompt.

---

### D5.5 — Proposing the policy change

- **Risk** — The lesson from the incident lives in a postmortem document nobody reads, and the policy that permitted it is unchanged.
- **Control** — A policy change proposal generated from the root cause record, as a diff with the incident as its evidence.
- **Lab** — Generate a policy diff from a root cause record and review what it would have prevented.
- **Tools** — `OPA`

**Run it** — Generate a policy diff from a root cause record and review what it would have prevented.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D5.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D5.5   # run it headless and check it
```

*Expect:* Generate a policy diff from a root cause record and review what it would have prevented.

---

### D5.6 — Regulatory clock

- **Risk** — Notification obligations discovered in week two.
- **Control** — Feed Track E2 in hour one.
- **Lab** — Run the first-hour checklist in a tabletop.

**Run it** — Run the first-hour checklist in a tabletop.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D5.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D5.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
python3 first_hour.py --case case-01 --checklist ../e2-compliance/notification.yaml
python3 first_hour.py --case case-01 --materiality
```

*Expect:* A materiality call and a notification clock started in hour one, feeding Track E2.

---
