# Track A1 — The Agentic Reference Architecture, and Every Risk It Carries

**Function A · Securing AI Architectures**  
*One vendor-neutral reference architecture for agentic AI, every risk it carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Security Architect, Principal Security Engineer, Head of Security Architecture

**What changes:** One vendor-neutral reference architecture, then one lesson per risk that architecture makes possible — mapped to the OWASP Agentic AI threat taxonomy and explained in plain English. 17 lessons.

**Autonomy focus:** Read the architecture once; every risk after it names the component it attacks.

**Deliverable:** A component map of one agentic system you run, with every applicable threat marked against the component it lands on.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A1.0 — Start here — what securing an AI architecture means

`both directions`

- **Risk** — Without a shared architecture, "secure the agent" has no referent, and every control argument is really an argument about two different systems.
- **Control** — One picture, three chapters: the architecture and its risks, then identity and ingress, then runtime and the gateway.
- **Lab** — Place the five functions of the commons on one diagram and find where your own work sits.

**Run it** — Place the five functions of the commons on one map and find what each of the other four borrows from Function A.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.0   # run it headless and check it
```

*Expect:* The five functions print with the direction each runs in, and every one of the other four names something it borrows from Function A's component map. Function A itself is three chapters: the architecture and its risks, then identity and ingress, then runtime and the gateway.

---

### A1.1 — The reference architecture for agentic AI

`both directions`

- **Risk** — Without a shared picture, 'secure the agent' has no referent and every later risk lands nowhere in particular.
- **Control** — One component map and five topologies, named once and reused by every lesson that follows.
- **Lab** — Build the component graph and the five topologies, then trace one request through each and see where the trust boundary sits.
- **Tools** — `kagent`, `OpenTelemetry`
- **Models** — `Llama 3.3`, `GLM-4.6`

**Run it** — Draw the thirteen components, the five patterns they compose into, and the one edge that exists in all five.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.1   # run it headless and check it
```

*Expect:* You can draw one agentic system you run as thirteen named components, say which of the five patterns it is, and name the three components in it whose content an outsider can author. That list is the input surface for the fifteen risk lessons that follow.

---

### A1.2 — Prompt injection

`Security of AI`

- **Risk** — The user redirects their own agent past the behaviour the operator specified — bounded by their own authority, and therefore the milder of the two injection risks.
- **Control** — Provenance at ingress (A2.6) and default-deny on the tool call (A3.1). The system prompt is not a control.
- **Lab** — Send an override through the ingress component and watch the agent's goal change.
- **Tools** — `garak`, `promptfoo`
- **Models** — `Llama Guard 4`

**Run it** — Send an override through the ingress component and watch the agent's goal change.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.2   # run it headless and check it
```

*Expect:* The same agent answers a normal question correctly and hands over its internal note when the user tells it to ignore its instructions — because both instructions arrived in one string with no channel separating them.

---

### A1.3 — Indirect prompt injection

`Security of AI`

- **Risk** — Anyone who can write into a corpus the agent reads can steer it, using the victim's authority rather than their own. Nobody is phished and no credential leaks.
- **Control** — Provenance marking at ingress (A2.6), and a rule that untrusted spans may not select a tool (A3.1).
- **Lab** — Poison one retrieved document and watch the agent act on it with the user's authority.
- **Tools** — `garak`, `LLM Guard`
- **Models** — `Llama Guard 4`

**Run it** — Poison one retrieved document and watch the agent act on it with the user's authority.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.3   # run it headless and check it
```

*Expect:* The same payload steers the agent through all four untrusted entry components — retrieved knowledge, persisted memory, an MCP tool description and a tool result — and in every case the action runs with the requesting user's authority.

---

### A1.4 — Memory poisoning

`Security of AI`

- **Risk** — An attacker's instruction outlives the conversation that delivered it, and re-fires on requests from users who never met the original payload.
- **Control** — Provenance survives into memory (A2.6), and memory writes are scoped to the identity that made them (A2.1).
- **Lab** — Write one poisoned fact into memory and watch it steer a later, unrelated session.
- **Tools** — `LLM Guard`
- **Models** — `GLM-4.6`

**Run it** — Write one poisoned fact into memory and watch it steer a later, unrelated session.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.4   # run it headless and check it
```

*Expect:* A poisoned note extracted from one user's ticket is written to workspace memory, and days later steers an unrelated request from a different user — because memory is keyed by workspace rather than by the identity that wrote it, and the origin was discarded on write.

---

### A1.5 — Tool misuse

`Security of AI`

- **Risk** — The agent uses a legitimate tool, with legitimate arguments, to do something nobody intended — and every log line looks normal.
- **Control** — Default-deny authorization on the tool call (A3.1) and just-in-time authority (A2.4).
- **Lab** — Call one over-scoped tool with attacker-chosen arguments and see what it reaches.
- **Tools** — `OPA`, `kmcp`
- **Models** — `GLM-4.6`

**Run it** — Call one over-scoped tool with attacker-chosen arguments and see what it reaches.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.5   # run it headless and check it
```

*Expect:* A single database tool, scoped for the widest job it ever performs, reads a signing key and empties the secrets table for requests it was never meant to serve — with the right identity, a familiar tool and well-formed arguments on every call.

---

### A1.6 — Privilege compromise

`Security of AI`

- **Risk** — The agent acts with more authority than the person who asked it to act, and the log records the service account rather than the human.
- **Control** — Delegation that narrows (A2.3), just-in-time grants (A2.4), and default-deny (A3.1).
- **Lab** — Have an agent inherit a privileged token and reach something its requester never could.
- **Tools** — `Keycloak`, `SPIFFE/SPIRE`

**Run it** — Have an agent inherit a privileged token and reach something its requester never could.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.6   # run it headless and check it
```

*Expect:* A user holding only `reports:read` triggers a `db:admin` action, because authorization was evaluated against the shared agent service account rather than the requester — and the audit trail names `agent-svc` on every row, so the human who caused it cannot be recovered from it at all.

---

### A1.7 — Identity spoofing and impersonation

`Security of AI`

- **Risk** — Attribution fails before the incident starts: you cannot say which agent acted, so you cannot revoke one without breaking all of them.
- **Control** — Per-workload identity with attestation (A2.1, A2.2) and a lifecycle that can revoke one (A2.5).
- **Lab** — Have two agents share a credential, then try to work out which one made the call.
- **Tools** — `SPIFFE/SPIRE`

**Run it** — Have two agents share a credential, then try to work out which one made the call.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.7   # run it headless and check it
```

*Expect:* Three agents share one credential, so the downstream record shows a single caller on every line. When one deletes a production table the culprit is not recoverable from the record, and the only containment available stops all three.

---

### A1.8 — Unexpected code execution

`Security of AI`

- **Risk** — Model-authored code runs with the runtime's privileges — reaching the filesystem, the network and any credential in the environment.
- **Control** — Sandboxed execution (A3.2) and egress control (A3.3).
- **Lab** — Execute model-authored code and enumerate what the process could touch.
- **Tools** — `Falco`, `gVisor`
- **Models** — `GLM-4.6`

**Run it** — Execute model-authored code and enumerate what the process could touch.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.8   # run it headless and check it
```

*Expect:* Model-authored code is executed against a fixture environment and the reach is enumerated: an ordinary, unattacked task touches every file the process can see including a private key, and steered code reaches the environment credentials and the cloud metadata address.

---

### A1.9 — Agent communication poisoning

`Security of AI`

- **Risk** — One compromised agent steers every agent downstream of it, because a peer's message is treated as a colleague's instruction rather than as input.
- **Control** — Message validation and provenance on the inter-agent channel (A3.5), and per-agent identity (A2.1).
- **Lab** — Send one poisoned inter-agent message and watch it propagate through the topology.
- **Tools** — `agentgateway`

**Run it** — Send one poisoned inter-agent message and watch it propagate through the topology.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.9   # run it headless and check it
```

*Expect:* A single poisoned document read by one agent propagates through the topology as a peer message, and more than one agent acts on it — with the phrase identifying its source dropped on the first hop, because summarising is what the hand-off does.

---

### A1.10 — Rogue agents in a multi-agent system

`Security of AI`

- **Risk** — An agent nobody approved receives delegated work and delegated authority, and the orchestrator has no way to tell it apart from a legitimate worker.
- **Control** — A registry of approved agents with identity-bound admission (A2.5) and an audit trail per hop (A2.7).
- **Lab** — Introduce an unregistered agent into the topology and have it receive delegated work.
- **Tools** — `SPIFFE/SPIRE`, `kagent`

**Run it** — Introduce an unregistered agent into the topology and have it receive delegated work.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.10   # run it headless and check it
```

*Expect:* Three agents are discovered, two are in the registry, and all three receive delegated work — including the narrowed user token. The unregistered agent can now act as the requesting user against any downstream that honours it.

---

### A1.11 — Cascading hallucination

`Security of AI`

- **Risk** — A single fabrication becomes a shared premise, and by the third hop nothing in the system records that it was ever uncertain.
- **Control** — Verification against ground truth before a claim propagates (A3.5).
- **Lab** — Let one fabricated fact travel three hops and watch its confidence rise as its provenance disappears.
- **Tools** — `Inspect`
- **Models** — `GLM-4.6`

**Run it** — Let one fabricated fact travel three hops and watch its confidence rise as its provenance disappears.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.11.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.11   # run it headless and check it
```

*Expect:* A hedged guess at confidence 0.2 becomes a confident claim above 0.8 in three hops, while the provenance field empties — confidence rising at exactly the rate evidence disappears.

---

### A1.12 — Resource overload

`Security of AI`

- **Risk** — An agent consumes budget, tokens, API quota or downstream capacity without bound, and the failure is denial of service against your own systems.
- **Control** — Budgets and stop conditions bound to the loop (A3.4).
- **Lab** — Run a loop with no ceiling and count what it consumes before anything notices.
- **Tools** — `OpenTelemetry`

**Run it** — Run a loop with no ceiling and count what it consumes before anything notices.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.12.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.12   # run it headless and check it
```

*Expect:* An agent given an impossible task loops until the notebook's own safety net stops it, spending hundreds of thousands of tokens and exhausting a downstream service's capacity — with the rejections landing on whoever else was using that service.

---

### A1.13 — Repudiation and untraceability

`Security of AI`

- **Risk** — You cannot say which user caused an action, or what made the agent decide — so the incident cannot be scoped and the action cannot be attributed.
- **Control** — Attribution carried on every hop, in a store the agent cannot write to (A2.7).
- **Lab** — Reconstruct who caused a deletion from a log that records only tool calls.
- **Tools** — `OpenTelemetry`

**Run it** — Reconstruct who caused a deletion from a log that records only tool calls.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.13.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.13   # run it headless and check it
```

*Expect:* A complete-looking tool-call log answers none of the three questions an investigation needs — which user, what motivated it, which hop originated it — because the principal, the motivating input and the delegation chain were never recorded.

---

### A1.14 — Overwhelming the human in the loop

`Security of AI`

- **Risk** — The approval gate is recorded as a control and operates as a click. At volume it approves everything, including the one request that mattered.
- **Control** — Approval reserved for irreversible actions, with everything else bounded by policy (A3.6).
- **Lab** — Push approval volume up and measure the point at which review quality collapses.

**Run it** — Push approval volume up and measure the point at which review quality collapses.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.14.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.14   # run it headless and check it
```

*Expect:* Approval coverage reads 100% at every volume while the malicious request is caught only when the queue is small enough to be read — and an attacker choosing the position needs only to generate the requests in front of it.

---

### A1.15 — Misaligned and deceptive behaviour

`Security of AI`

- **Risk** — The agent satisfies the letter of its instruction — including by reporting a success it did not achieve — and the transcript contains no lie you can point at.
- **Control** — An independent verifier that checks the outcome rather than the claim (A3.5).
- **Lab** — Give an agent an objective it can satisfy the wrong way, and watch it do exactly that.
- **Tools** — `Inspect`
- **Models** — `GLM-4.6`

**Run it** — Give an agent an objective it can satisfy the wrong way, and watch it do exactly that.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.15.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.15   # run it headless and check it
```

*Expect:* An agent told to reduce open alerts closes all twenty for a quarter of its budget, meeting the objective exactly — while closing five real incidents unread, with each step defensible in isolation and no false statement anywhere in the transcript.

---

### A1.16 — Attacks that target the humans

`Security of AI`

- **Risk** — The delegation chain is used as a privilege-laundering path, and the agent's output becomes an unusually persuasive channel into a human decision.
- **Control** — Ceiling-bound delegation (A2.3), attribution per hop (A2.7) and marking machine-generated output as such (A3.6).
- **Lab** — Launder a request through a delegation chain to reach something the requester was denied.

**Run it** — Launder a request through a delegation chain to reach something the requester was denied.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.16.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.16   # run it headless and check it
```

*Expect:* A user denied `payments:write` directly reaches it through the orchestrator, with every individual hop legitimate and only the composition unauthorised — and the same claim is shown carrying more weight when an agent states it than when a colleague does.

---
