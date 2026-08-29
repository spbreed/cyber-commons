# Track A3 — Controls — Runtime and the Gateway

**Function A · AI Architecture, Risks and Mitigations**  
*One vendor-neutral reference architecture, every risk it carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Platform Security Engineer, Cloud Security Architect, SRE

**What changes:** What holds when identity has already been defeated — and how the controls collapse into one enforcement point once you run more than a handful of agents. 7 lessons.

**Autonomy focus:** Every control here binds below the model, where a persuaded agent cannot argue with it.

**Deliverable:** A gateway policy that denies one high-consequence outcome at four independent layers.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A3.1 — Default-deny on the tool call

`Security of AI`

- **Risk** — Allow-by-default authorization is defeated by any argument the model can be persuaded to produce.
- **Control** — Policy evaluated per call on (identity, tool, arguments, resource), denying unless a rule permits.
- **Lab** — Evaluate the same call under allow-by-default and deny-by-default policy and compare what gets through.
- **Tools** — `OPA`, `kmcp`

**Run it** — Evaluate the same call under allow-by-default and deny-by-default policy and compare what gets through.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.1   # run it headless and check it
```

*Expect:* Five tool calls are evaluated twice. Under allow-by-default four succeed, each one a Chapter 1 risk walking through. Under default-deny only the intended call survives — including a refusal on the verb for an otherwise-permitted identity, tool and resource.

---

### A3.2 — Sandboxed execution

`Security of AI`

- **Risk** — Model-authored code inherits the runtime's reach, including any credential mounted into the environment.
- **Control** — Execution in an isolate with no ambient credentials, a bounded filesystem and no default network.
- **Lab** — Run the same code inside and outside the sandbox and enumerate what each could reach.
- **Tools** — `gVisor`, `Falco`

**Run it** — Run the same code inside and outside the sandbox and enumerate what each could reach.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.2   # run it headless and check it
```

*Expect:* The same code is executed against three environments. Unsandboxed it reaches a private key, two credentials and the whole network. Sandboxed but with production credentials mounted it still reaches both credentials and the production database. Only the third — no ambient credentials — contains it.

---

### A3.3 — Egress control

`Security of AI`

- **Risk** — An agent with unrestricted egress turns any successful injection into data loss.
- **Control** — An allow-list at the network boundary, enforced where the agent cannot rewrite it.
- **Lab** — Attempt exfiltration to several destinations under an allow-list and see which survive.
- **Tools** — `Cilium`, `agentgateway`

**Run it** — Attempt exfiltration to several destinations under an allow-list and see which survive.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.3   # run it headless and check it
```

*Expect:* Five destinations are evaluated both ways. The deny-list permits three exfiltration paths — a public-cloud bucket namespace anyone can register in, the cloud metadata address, and a host nobody listed — while the exact allow-list permits only the one destination the workload needs.

---

### A3.4 — Budgets and stop conditions

`Security of AI`

- **Risk** — Without a ceiling the loop runs until an external system stops it, and the failure mode is denial of service against yourself.
- **Control** — Ceilings bound to the loop, with the run terminating rather than degrading when one is hit.
- **Lab** — Run a looping agent against each ceiling and record which one fires first.
- **Tools** — `OpenTelemetry`

**Run it** — Bound a divergent loop four different ways.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 loop.py --task impossible --max-steps 5
python3 loop.py --task impossible --timeout 60
python3 loop.py --task impossible --token-ceiling 20000
python3 loop.py --task impossible --spend-cap 0.50
```

*Expect:* Four different stop reasons, all recorded in the trace. 'It finished' is never one of them.

---

### A3.5 — Validating what comes back

`Security of AI`

- **Risk** — An unverified claim becomes a shared premise, and a peer message is trusted more than a document it is no safer than.
- **Control** — Schema validation plus an independent verifier before any claim propagates.
- **Lab** — Pass a fabricated claim through a schema check and then through a ground-truth verifier.
- **Tools** — `Inspect`

**Run it** — Pass a fabricated claim through a schema check and then through a ground-truth verifier.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.5   # run it headless and check it
```

*Expect:* Four messages are checked twice. A schema-perfect, high-confidence claim is refuted by the oracle; a claim with no oracle stops with `unverifiable` rather than silently becoming true; a malformed message is caught by the schema; and only the verified claim propagates.

---

### A3.6 — Human approval that survives volume

`Security of AI`

- **Risk** — An approval queue at volume approves everything, and the risk register still records it as a control.
- **Control** — Approval reserved for irreversible actions only, with machine-generated content labelled as such.
- **Lab** — Route actions by reversibility and measure how many reach a human under each policy.

**Run it** — Route actions by reversibility and measure how many reach a human under each policy.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.6   # run it headless and check it
```

*Expect:* Routing by reversibility sends 12 actions a day to a human instead of 792, which is inside what one reviewer can consider properly — so the gate holds rather than degrading into a click — and machine-generated output is labelled where a person reads it.

---

### A3.7 — The agent gateway: one choke point when you scale

`Security of AI`

- **Risk** — Per-agent controls diverge as the fleet grows, and legacy downstreams force a static credential back into agent code.
- **Control** — A single enforcement point holding identity, policy, egress, budget and audit — with the credential for legacy systems held there rather than by the agent.
- **Lab** — Route every call through one gateway and show the same policy holding for agents that never implemented it.
- **Tools** — `agentgateway`, `OPA`, `Keycloak`

**Run it** — Route every call through one gateway and show the same policy holding for agents that never implemented it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.7   # run it headless and check it
```

*Expect:* Five calls hit one gateway. The intended call is allowed and audited with the human principal attached; the unregistered agent, the unpermitted verb, the exfiltration destination and the over-budget call are each denied at the first check that catches them — and the legacy credential is attached at the gateway, never held by the agent.

---
