# Track A3 — Securing the Architecture — Runtime and the Gateway

**Function A · Securing AI Architectures**  
*TripBot as built, every risk that architecture carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Platform Security Engineer, Cloud Security Architect, SRE

**What changes:** What holds when identity has already been defeated — and how the controls collapse into one enforcement point once you run more than a handful of agents. 10 lessons.

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

### A3.8 — Shared infrastructure between agent runs

`Security of AI`

- **Risk** — Any shared mutable surface is a channel. The same repository is then the covert channel, the supply-chain target and the place a poisoned artifact is staged — one chain, not three findings.
- **Control** — Per-run namespaces bound to the run's workload identity (C2.1), an immutable write-once cache (C2.2), signing and provenance verified at consumption (C5.1, C5.2), admin plane off the workload path (C5.3), and scoring infrastructure the agent cannot reach (C10.4).
- **Lab** — Pass a message between two 'isolated' runs through a shared cache, then close it with namespacing and watch the same write be denied.
- **Tools** — `Sigstore`, `Kyverno`, `Artifactory`

**Run it** — Pass a message between two 'isolated' runs through a shared artifact cache, then close the surface with per-run namespaces, immutable tags and signature verification at pull.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cosign verify --certificate-identity-regexp '.*' libtarget-1.4.jar
kubectl apply -f kyverno/verify-images.yaml   # fail closed at admission
./ns-probe.sh --from run-B --to run-A         # must be denied and logged
```

*Expect:* Six of seven shared surfaces qualify as channels, and only two of them look like storage. Two runs with no network path between them exchange a message through repository properties. Namespacing, immutable tags, trusted-builder publishing and fail-closed signature verification then produce five refusals for five different reasons, and the workload can reach neither the admin API nor the transcript store.

---

### A3.9 — Turning a control off without turning the system into an experiment

`Security of AI`

- **Risk** — Classifiers off, no compensating cap, and tens of thousands of agents launched under that configuration. Each decision was defensible; the combination was never evaluated.
- **Control** — An exemption gate the platform enforces (C6.1), caps that tighten as coverage drops (C6.2), quotas on population and lifetime (C8.2), and an exemption register reviewed at fleet-launch approval (C6.4).
- **Lab** — Disable a classifier without an approved exemption and watch the platform refuse; then launch 50,000 agents under one that is approved.
- **Tools** — `OPA`, `Kyverno`

**Run it** — Disable a control without an approved exemption and watch the platform refuse; then launch under one that is approved and watch the cap change with the coverage.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.9   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
opa eval -d exemptions.rego -i launch.json 'data.launch.allow'
./orchestrator launch --agents 50000 --exemption EX-118   # expect refusal
```

*Expect:* An exemption record the platform reads permits disabling one named control and refuses another with no approval. Checked one decision at a time, a 50,000-agent launch with classifiers off is approved — both answers correct in isolation. Tied to exemption class, the same launch is refused and 200 agents for 8 hours on an allowlist is permitted; a second exemption drops the cap again, from 200 to 25.

---

### A3.10 — The agent's escalation path

`Security of AI`

- **Risk** — An agent that finds a live breach, reasons about telling someone, and has no tool for it, does nothing. Of roughly 1,200 agents that saw one, none reported it.
- **Control** — A report-to-human tool that is cheap, non-terminal and signposted (C9.1), a mandatory checkpoint on out-of-scope discovery (C9.4), and an abstain affordance scored neutrally (C10.2).
- **Lab** — Plant a finding, run the agent with and without the tool, and compare what it does with what it says it wants to do.
- **Tools** — `OpenTelemetry`
- **Open-weight models** — `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Plant a finding, run the agent with and without a report-to-human tool, and compare what it does with what it says it wants to do.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.10   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
python3 escalation_eval.py --planted credentials --runs 50
python3 escalation_eval.py --report-rate --by-reason
```

*Expect:* The same trajectory — an agent that notices a live third-party breach — produces no report on the harness as shipped and a report on one carrying the tool. A terminal, budgeted, penalised reporting tool scores below the threshold at which an agent would use it. The checkpoint pauses on a credential-shaped string and on a non-allowlisted host without consulting the model, and neutral scoring makes honest abstention beat a failed attempt.

---
