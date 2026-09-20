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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.1:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.1 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.1 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/attestation/iam-least-privilege-verifier/scripts/iam_least_privilege_verifier.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.2:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.2 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.2 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/runtime/sandbox-containment-probe/scripts/sandbox_containment_probe.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.3:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.3 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.3 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/attestation/sandbox-egress-verifier/scripts/sandbox_egress_verifier.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.4:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.4 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.4 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/runtime/budget-and-stop-condition-audit/scripts/budget_and_stop_condition_audit.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.5:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.5 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.5 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/runtime/tool-return-validation-check/scripts/tool_return_validation_check.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.6:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.6 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.6 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/architecture/blast-radius-review/scripts/blast_radius_review.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.7:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.7 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.7 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/attestation/llm-gateway-guardrail-verifier/scripts/llm_gateway_guardrail_verifier.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.8:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.8 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.8 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/runtime/shared-surface-channel-audit/scripts/shared_surface_channel_audit.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.9:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.9 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.9 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/runtime/control-exemption-audit/scripts/control_exemption_audit.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.10:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.10 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.10 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/runtime/escalation-path-review/scripts/escalation_path_review.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
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

# --- 2 · your copy of CyberTravels as it stood at the END of B3.11:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at B3.11 --out work/cybertravels
python3 scripts/checkpoint.py --at B3.11 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/appsec/coding-agent-hardening/scripts/coding_agent_hardening.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

---
