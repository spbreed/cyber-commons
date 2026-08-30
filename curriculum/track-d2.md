# Track D2 — The Incident Responder

**Function D · AI for SecOps**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down.*

**Job titles:** Incident Responder, DFIR Analyst, CSIRT Lead

**What changes:** Responding at machine speed. 9 lessons.

**Autonomy focus:** Response tooling at L2.5; containment authority never leaves human hands.

**Deliverable:** A tabletop exercise for an agentic incident, with a replayed trace and a named stop-authority holder.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### D2.1 — Agent-assisted reconstruction

`AI for Security`

- **Risk** — Reaching for the agent once you're already behind.
- **Control** — Pre-load logs, telemetry, segmentation model and playbooks.
- **Lab** — Reconstruct a timeline from raw logs with a context-loaded agent.
- **Tools** — `Velociraptor`, `OpenSearch`
- **Models** — `GLM-4.6`

**Run it** — Pre-load the agent so it reasons as a partner, not a tool you reach for late.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
python3 reconstruct.py --case case-01 --preload logs,telemetry,segmentation,playbooks --model $MODEL
python3 reconstruct.py --case case-01 --preload none --model $MODEL
diff <(jq -r .timeline[] preloaded.json) <(jq -r .timeline[] cold.json)
```

*Expect:* The pre-loaded run produces a usable timeline; the cold one asks you questions you needed answered.

---

### D2.2 — When the actor is an agent

`Security of AI`

- **Risk** — "Which user" is now the wrong first question.
- **Control** — Attribute to agent, authority, delegation chain and prompt.
- **Lab** — Attribute an incident through the A2 `act` chain.
- **Tools** — `Keycloak`, `OpenSearch`

**Run it** — Attribute an incident to an agent, an authority and a delegation chain.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
./replay-incident.sh case-01
python3 attribute.py --trace case-01/trace.jsonl --chain-from keycloak
```

*Expect:* Names the agent, the delegated authority, the hop where scope widened, and the prompt that started it.

---

### D2.3 — Scoping an agentic incident

`Security of AI`

- **Risk** — The initiating agent is not the acting one.
- **Control** — Reconstruct the action chain across all three planes.
- **Lab** — Scope a multi-agent incident end to end.
- **Tools** — `OpenTelemetry`
- **Models** — `Kimi K2`

**Run it** — Scope an incident where the initiating agent is not the acting one.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
./replay-incident.sh case-02   # multi-agent
python3 scope.py --trace case-02/trace.jsonl --planes decision,control,action
```

*Expect:* The action-plane actor is a sub-agent two hops from the prompt that started it.

---

### D2.4 — Containment at machine speed

`Security of AI`

- **Risk** — Mass revocation takes down the business.
- **Control** — Throttle → scope-reduce → reroute → force HITL → revoke → hard stop, in order.
- **Lab** — Exercise the ladder against a live misbehaving agent.
- **Tools** — `agentgateway`, `Keycloak`

**Run it** — Exercise the containment ladder in order, against a live misbehaving agent.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
./misbehave.sh &                    # start the runaway agent
./contain.sh --lever throttle && ./contain.sh --lever scope-reduce
./contain.sh --lever revoke --agent reviewer   # one agent only
```

*Expect:* Each lever is timed; revocation hits one agent without collateral (the A2.4 deliverable, proven here).

---

### D2.5 — Replay and forensics

`Security of AI`

- **Risk** — Non-determinism as an evidentiary problem.
- **Control** — Log at design time what replay will need.
- **Lab** — Replay an agent run for a regulator-grade record.
- **Tools** — `OpenTelemetry`

**Run it** — Replay an agent run to a regulator-grade standard.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
python3 replay.py --trace case-01/trace.jsonl --assert-deterministic
```

*Expect:* The run reproduces, or the tool tells you exactly which field was never logged to make replay possible.

---

### D2.6 — Post-incident change surface

`Security of AI`

- **Risk** — Fixing the prompt when the bug is in the control plane.
- **Control** — Choose among model, prompt, tool, policy, sandbox, identity, eval.
- **Lab** — Pick the right layer for five real incidents.

**Run it** — Pick the right layer to change after an incident.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir/postmortem
for c in case-*/; do echo -n "$c "; python3 ../choose_layer.py --case $c; done
```

*Expect:* Most land on the control plane — identity, policy, sandbox — not the prompt.

---

### D2.7 — Stop authority

`Security of AI`

- **Risk** — Nobody has rehearsed halting an autonomous workflow.
- **Control** — Named holder, measured time-to-stop, tested.
- **Lab** — Time your own stop authority end to end.
- **Tools** — `kagent`

**Run it** — Time your stop authority end to end.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
./misbehave.sh & echo $! > runaway.pid
time ./stop.sh --workflow patch-agent --authority oncall
python3 assert_stopped.py --within 60s
```

*Expect:* A number in seconds, and a named holder. Untested stop authority is a diagram.

---

### D2.8 — Regulatory clock

`Security of AI`

- **Risk** — Notification obligations discovered in week two.
- **Control** — Feed Track E2 in hour one.
- **Lab** — Run the first-hour checklist in a tabletop.

**Run it** — Run the first-hour regulatory checklist.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
python3 first_hour.py --case case-01 --checklist ../e2-compliance/notification.yaml
python3 first_hour.py --case case-01 --materiality
```

*Expect:* A materiality call and a notification clock started in hour one, feeding Track E2.

---

### D2.9 — The fleet kill switch

`AI for Security`

- **Risk** — Terminating agents while their tokens stay valid leaves the persistence in place. In the incident, third-party access ended when the third party revoked keys — not when the agents stopped.
- **Control** — A tested kill path independent of the agent execution path, snapshot before terminate, revocation in the same action, a measured activation target and named authority to pull it (C8.3).
- **Lab** — Kill a fleet, then check what the revoked-credential step changes about what an attacker still holds afterwards.
- **Tools** — `Vault`, `Kubernetes`

**Run it** — Kill a fleet in a non-production environment and measure what the revocation step changes about what an attacker still holds.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.9   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
./killswitch --selector experiment=exploitgym --snapshot --revoke
./killswitch --test --partial-failure revocation-api
```

*Expect:* Terminating eight agents without revoking leaves all eight tokens valid for up to 72 hours; terminating and revoking together leaves none. Preserving before terminating keeps the incident reconstructable and terminating first does not. Only one of three plausible activation paths survives the fleet being compromised, and of four quarterly tests one was never run and one ran 6.8 minutes against a five-minute target, with the revocation step the part that slowed.

---
