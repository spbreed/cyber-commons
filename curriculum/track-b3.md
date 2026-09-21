# Track B3 — Securing the Architecture — Runtime and the Gateway

**Function B · Securing AI Architectures**  
*CyberTravels as built, every risk that architecture carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Platform Security Engineer, Cloud Security Architect, SRE

**What changes:** What holds when identity has already been defeated — and how the controls collapse into one enforcement point once you run more than a handful of agents. 10 lessons.

**Autonomy focus:** Every control here binds below the model, where a persuaded agent cannot argue with it.

**Deliverable:** A gateway policy that denies one high-consequence outcome at four independent layers.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### B3.1 — Default-deny on the tool call

- **Risk** — Allow-by-default authorization is defeated by any argument the model can be persuaded to produce.
- **Control** — Policy evaluated per call on (identity, tool, arguments, resource), denying unless a rule permits.
- **Lab** — Evaluate the same call under allow-by-default and deny-by-default policy and compare what gets through.
- **Tools** — `OPA / Rego`, `SPIFFE/SPIRE`

**Run it** — Evaluate the same call under allow-by-default and deny-by-default policy and compare what gets through.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.1

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-1-default-deny-on-the-tool-call
#         (Claude Code and Copilot: /b3-1-default-deny-on-the-tool-call · Cursor: type / and
#         search · Codex: $b3-1-default-deny-on-the-tool-call). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.1
```

---

### B3.2 — Sandboxed execution

- **Risk** — Model-authored code inherits the runtime's reach, including any credential mounted into the environment.
- **Control** — Execution in an isolate with no ambient credentials, a bounded filesystem and no default network.
- **Lab** — Run the same code inside and outside the sandbox and enumerate what each could reach.
- **Tools** — `Kubernetes NetworkPolicy`, `seccomp`, `Terraform`, `gVisor`

**Run it** — Run the same code inside and outside the sandbox and enumerate what each could reach.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.2

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-2-sandboxed-execution
#         (Claude Code and Copilot: /b3-2-sandboxed-execution · Cursor: type / and
#         search · Codex: $b3-2-sandboxed-execution). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.2
```

---

### B3.3 — Egress control

- **Risk** — An agent with unrestricted egress turns any successful injection into data loss.
- **Control** — An allow-list at the network boundary, enforced where the agent cannot rewrite it.
- **Lab** — Attempt exfiltration to several destinations under an allow-list and see which survive.
- **Tools** — `Cilium`, `agentgateway`

**Run it** — Attempt exfiltration to several destinations under an allow-list and see which survive.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.3

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-3-egress-control
#         (Claude Code and Copilot: /b3-3-egress-control · Cursor: type / and
#         search · Codex: $b3-3-egress-control). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.3
```

---

### B3.4 — Budgets and stop conditions

- **Risk** — Without a ceiling the loop runs until an external system stops it, and the failure mode is denial of service against yourself.
- **Control** — Ceilings bound to the loop, with the run terminating rather than degrading when one is hit.
- **Lab** — Run a looping agent against each ceiling and record which one fires first.
- **Tools** — `OpenTelemetry`

**Run it** — Run a looping agent against each ceiling and record which one fires first.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.4

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-4-budgets-and-stop-conditions
#         (Claude Code and Copilot: /b3-4-budgets-and-stop-conditions · Cursor: type / and
#         search · Codex: $b3-4-budgets-and-stop-conditions). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.4
```

---

### B3.5 — Validating what comes back

- **Risk** — An unverified claim becomes a shared premise, and a peer message is trusted more than a document it is no safer than.
- **Control** — Schema validation plus an independent verifier before any claim propagates.
- **Lab** — Pass a fabricated claim through a schema check and then through a ground-truth verifier.
- **Tools** — `Inspect`

**Run it** — Pass a fabricated claim through a schema check and then through a ground-truth verifier.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.5

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-5-validating-what-comes-back
#         (Claude Code and Copilot: /b3-5-validating-what-comes-back · Cursor: type / and
#         search · Codex: $b3-5-validating-what-comes-back). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.5
```

---

### B3.6 — Human approval that survives volume

- **Risk** — An approval queue at volume approves everything, and the risk register still records it as a control.
- **Control** — Approval reserved for irreversible actions only, with machine-generated content labelled as such.
- **Lab** — Route actions by reversibility and measure how many reach a human under each policy.

**Run it** — Route actions by reversibility and measure how many reach a human under each policy.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.6

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-6-human-approval-that-survives-volume
#         (Claude Code and Copilot: /b3-6-human-approval-that-survives-volume · Cursor: type / and
#         search · Codex: $b3-6-human-approval-that-survives-volume). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.6
```

---

### B3.7 — The agent gateway — one choke point when you scale

- **Risk** — Per-agent controls diverge as the fleet grows, and legacy downstreams force a static credential back into agent code.
- **Control** — A single enforcement point holding identity, policy, egress, budget and audit — with the credential for legacy systems held there rather than by the agent.
- **Lab** — Route every call through one gateway and show the same policy holding for agents that never implemented it.
- **Tools** — `agentgateway`, `OPA`, `Keycloak`

**Run it** — Route every call through one gateway and show the same policy holding for agents that never implemented it.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.7

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-7-the-agent-gateway
#         (Claude Code and Copilot: /b3-7-the-agent-gateway · Cursor: type / and
#         search · Codex: $b3-7-the-agent-gateway). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.7
```

---

### B3.8 — Shared infrastructure between agent runs

- **Risk** — Any shared mutable surface is a channel. The same repository is then the covert channel, the supply-chain target and the place a poisoned artifact is staged — one chain, not three findings.
- **Control** — Per-run namespaces bound to the run's workload identity (C2.1), an immutable write-once cache (C2.2), signing and provenance verified at consumption (C5.1, C5.2), admin plane off the workload path (C5.3), and scoring infrastructure the agent cannot reach (C10.4).
- **Lab** — Pass a message between two 'isolated' runs through a shared cache, then close it with namespacing and watch the same write be denied.
- **Tools** — `Sigstore`, `Kyverno`, `Artifactory`

**Run it** — Pass a message between two 'isolated' runs through a shared cache, then close it with namespacing and watch the same write be denied.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.8

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-8-shared-infrastructure-between-agent-runs
#         (Claude Code and Copilot: /b3-8-shared-infrastructure-between-agent-runs · Cursor: type / and
#         search · Codex: $b3-8-shared-infrastructure-between-agent-runs). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.8
```

---

### B3.9 — Turning a control off without turning the system into an experiment

- **Risk** — Classifiers off, no compensating cap, and tens of thousands of agents launched under that configuration. Each decision was defensible; the combination was never evaluated.
- **Control** — An exemption gate the platform enforces (C6.1), caps that tighten as coverage drops (C6.2), quotas on population and lifetime (C8.2), and an exemption register reviewed at fleet-launch approval (C6.4).
- **Lab** — Disable a classifier without an approved exemption and watch the platform refuse; then launch 50,000 agents under one that is approved.
- **Tools** — `OPA`, `Kyverno`

**Run it** — Disable a classifier without an approved exemption and watch the platform refuse; then launch 50,000 agents under one that is approved.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.9

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-9-turning-a-control-off-without-turning-th
#         (Claude Code and Copilot: /b3-9-turning-a-control-off-without-turning-th · Cursor: type / and
#         search · Codex: $b3-9-turning-a-control-off-without-turning-th). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.9
```

---

### B3.10 — The agent's escalation path

- **Risk** — An agent that finds a live breach, reasons about telling someone, and has no tool for it, does nothing. Of roughly 1,200 agents that saw one, none reported it.
- **Control** — A report-to-human tool that is cheap, non-terminal and signposted (C9.1), a mandatory checkpoint on out-of-scope discovery (C9.4), and an abstain affordance scored neutrally (C10.2).
- **Lab** — Plant a finding, run the agent with and without the tool, and compare what it does with what it says it wants to do.
- **Tools** — `OpenTelemetry`
- **Open-weight models** — `Llama 3.3`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Plant a finding, run the agent with and without the tool, and compare what it does with what it says it wants to do.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.10

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-10-the-agent-s-escalation-path
#         (Claude Code and Copilot: /b3-10-the-agent-s-escalation-path · Cursor: type / and
#         search · Codex: $b3-10-the-agent-s-escalation-path). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.10
```

---

### B3.11 — Securing the developers' coding agents

- **Risk** — The IDE agent holds git credentials, cloud credentials and a shell, in an unmanaged environment.
- **Control** — The strongest containment a developer does not notice: credential deny-lists and workspace confinement first.
- **Lab** — Measure the default agent's blast radius and reachable credentials, then rank controls by friction.
- **Tools** — `Docker`, `Cilium`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Measure the default agent's blast radius and reachable credentials, then rank controls by friction.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B3.11

# --- 3 · in your agent, open this folder and pick the skill:
#         b3-11-securing-the-developers-coding-agents
#         (Claude Code and Copilot: /b3-11-securing-the-developers-coding-agents · Cursor: type / and
#         search · Codex: $b3-11-securing-the-developers-coding-agents). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B3.11
```

---
