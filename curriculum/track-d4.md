# Track D4 — The Agentic SOC — Respond

**Function D · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** 

**What changes:** 

**Autonomy focus:** 

**Deliverable:** 

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### D4.1 — Remediation policy — what may be done without asking

- **Risk** — Automation scope is decided per runbook by whoever wrote it, so the blast radius of the response is unknown until it fires.
- **Control** — One remediation policy keyed on blast radius and reversibility, from which each runbook's tier is derived rather than chosen.
- **Lab** — Classify a set of remediation actions against the policy and see which tier each lands in, and why.
- **Tools** — `OPA`

**Run it** — Classify a set of remediation actions against the policy and see which tier each lands in, and why.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D4.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D4.1   # run it headless and check it
```

*Expect:* Classify a set of remediation actions against the policy and see which tier each lands in, and why.

---

### D4.2 — Runbook tiers: fully automated, human in the loop, manual

- **Risk** — Everything is written as fully automated because that is the impressive demo, and the first wrong action is unrecoverable.
- **Control** — Tier assigned from the remediation policy, with the human-in-the-loop tier carrying a real decision point rather than a confirmation dialog.
- **Lab** — Take one incident and run its response at all three tiers, comparing what each costs and what each risks.
- **Tools** — `kagent`

**Run it** — Take one incident and run its response at all three tiers, comparing what each costs and what each risks.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D4.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D4.2   # run it headless and check it
```

*Expect:* Take one incident and run its response at all three tiers, comparing what each costs and what each risks.

---

### D4.3 — Containment at machine speed

- **Risk** — Mass revocation takes down the business.
- **Control** — Throttle → scope-reduce → reroute → force HITL → revoke → hard stop, in order.
- **Lab** — Exercise the ladder against a live misbehaving agent.
- **Tools** — `agentgateway`, `Keycloak`

**Run it** — Exercise the ladder against a live misbehaving agent.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D4.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D4.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
./misbehave.sh &                    # start the runaway agent
./contain.sh --lever throttle && ./contain.sh --lever scope-reduce
./contain.sh --lever revoke --agent reviewer   # one agent only
```

*Expect:* Each lever is timed; revocation hits one agent without collateral (the A2.4 deliverable, proven here).

---

### D4.4 — Stop authority

- **Risk** — Nobody has rehearsed halting an autonomous workflow.
- **Control** — Named holder, measured time-to-stop, tested.
- **Lab** — Time your own stop authority end to end.
- **Tools** — `kagent`

**Run it** — Time your own stop authority end to end.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D4.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D4.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d2-ir
./misbehave.sh & echo $! > runaway.pid
time ./stop.sh --workflow patch-agent --authority oncall
python3 assert_stopped.py --within 60s
```

*Expect:* A number in seconds, and a named holder. Untested stop authority is a diagram.

---

### D4.5 — The fleet kill switch

- **Risk** — Terminating agents while their tokens stay valid leaves the persistence in place. In the incident, third-party access ended when the third party revoked keys — not when the agents stopped.
- **Control** — A tested kill path independent of the agent execution path, snapshot before terminate, revocation in the same action, a measured activation target and named authority to pull it (C8.3).
- **Lab** — Kill a fleet, then check what the revoked-credential step changes about what an attacker still holds afterwards.
- **Tools** — `Vault`, `Kubernetes`

**Run it** — Kill a fleet, then check what the revoked-credential step changes about what an attacker still holds afterwards.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D4.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D4.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
./killswitch --selector experiment=exploitgym --snapshot --revoke
./killswitch --test --partial-failure revocation-api
```

*Expect:* Terminating eight agents without revoking leaves all eight tokens valid for up to 72 hours; terminating and revoking together leaves none. Preserving before terminating keeps the incident reconstructable and terminating first does not. Only one of three plausible activation paths survives the fleet being compromised, and of four quarterly tests one was never run and one ran 6.8 minutes against a five-minute target, with the revocation step the part that slowed.

---
