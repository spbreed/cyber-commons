# Track A1 — The Security Architect

**Function A · Security Architecture & Platform**  
*The people who decide what is structurally possible. If they get it wrong, no amount of downstream diligence recovers it.*

**Job titles:** Security Architect, Principal Security Engineer, Head of Security Architecture

**What changes:** Designing systems that act — and defending them at every layer. 12 lessons.

**Autonomy focus:** Designs must be safe at L3 even when deployed at L2.5.

**Deliverable:** A reference architecture and a blast-radius measurement for one real business workflow.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A1.1 — What an agentic system is actually made of

`both directions`

- **Risk** — "Secure the agent" has no referent until you can name the parts. Every control in this curriculum attaches to one specific component or one boundary between two.
- **Control** — Draw the system as it really runs: app, model, agent loop, tools and APIs, MCP servers, retrieval, memory — and mark which boundaries untrusted data crosses.
- **Lab** — Build the component graph for a working agent, then trace one user request through every hop and mark where trust changes.
- **Tools** — `kagent`, `OpenTelemetry`
- **Models** — `Llama 3.3`, `GLM-4.6`

**Run it** — Name the seven parts of an agentic system, then find the two boundaries every later control binds to.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.1   # run it headless and check it
```

*Expect:* The component graph prints with trust levels, one request traces to a tool call, and a poisoned document steers the naive loop 134 times in 400 while the provenance-aware loop fires zero times.

---

### A1.2 — The controls, and where each one binds

`Security of AI`

- **Risk** — Controls chosen as a checklist land in the wrong layer — a prompt rule where an authorization rule was needed, and nothing to point at when asked what stops it.
- **Control** — One map: identity, default-deny authorization, sandboxed execution, tool and MCP trust, egress, containment, audit — each bound to the component it constrains.
- **Lab** — Place seven controls on the component graph from A1.1, then remove one at a time and count which attacks stop being stopped.
- **Tools** — `OPA`, `SPIFFE/SPIRE`, `Falco`, `agentgateway`
- **Models** — `GLM-4.6`

**Run it** — Map seven controls onto the components they bind to, then measure what each one alone is holding up.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.2   # run it headless and check it
```

*Expect:* Removing each control in turn shows which attacks it alone was stopping; audit newly unstops nothing, because audit explains rather than prevents.

---

### A1.3 — Architecture review when the system acts

`Security of AI`

- **Risk** — PDF threat models go stale the moment the agent's tools change.
- **Control** — Living, continuously re-evaluated threat models over the three planes separately.
- **Lab** — Generate a threat model from a running agent's actual tool manifest, then diff it after adding one tool.
- **Tools** — `OWASP Threat Dragon`, `kagent`
- **Models** — `GLM-4.6`

**Run it** — Make the threat model a living artefact that moves when the tools move.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a1-control-plane
python3 tm_from_manifest.py --manifest agent-tools.json --out tm-before.md
jq '.tools += [{"name":"http_post","scope":"any-host"}]' agent-tools.json > t && mv t agent-tools.json
python3 tm_from_manifest.py --manifest agent-tools.json --out tm-after.md
diff tm-before.md tm-after.md
```

*Expect:* One added tool changes the trust boundaries section. A PDF threat model would not have moved.

---

### A1.4 — Designing the agent control plane

`Security of AI`

- **Risk** — Controls assumed to live 'in the agent' are advisory, not enforced.
- **Control** — Identity fabric → agentic gateway → policy decision point → sandboxed runtime → audited action plane.
- **Lab** — Stand the whole reference stack up on kind: SPIRE + agentgateway + OPA + a sandboxed runner.
- **Tools** — `kind`, `SPIRE`, `agentgateway`, `OPA`
- **Models** — `Llama 3.3`

**Run it** — Stand up the whole reference control plane locally.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a1-control-plane
kind create cluster --config kind.yaml
kubectl apply -k spire/     # identity fabric
kubectl apply -k gateway/   # agentgateway
kubectl apply -k opa/       # policy decision point
./verify.sh                 # asserts each layer actually enforces
```

*Expect:* verify.sh fails loudly if any layer is advisory rather than enforcing.

---

### A1.5 — Blast radius as a design metric

`Security of AI`

- **Risk** — Blast radius is asserted in review, never measured.
- **Control** — Make it a number that appears in the design review.
- **Lab** — Measure reachable actions under flat RBAC vs attenuated delegation while an injection fires.
- **Tools** — `OpenFGA`, `SPIRE`
- **Models** — `Kimi K2`

**Run it** — Put a blast-radius number in the design review.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a1-control-plane
python3 blast_radius.py --model flat-rbac    --scenario injection
python3 blast_radius.py --model attenuated   --scenario injection
python3 blast_radius.py --compare flat-rbac attenuated --out blast.md
```

*Expect:* Reachable-action counts for both models, side by side. The delta is what attenuation bought you.

---

### A1.6 — Multi-agent topology

`Security of AI`

- **Risk** — Fan-out concentrates authority somewhere nobody drew.
- **Control** — Planner/executor/critic splits with delegation-depth limits.
- **Lab** — Build a 3-agent topology in kagent and chart where authority actually accumulates.
- **Tools** — `kagent`
- **Models** — `GLM-4.6`, `Llama 3.3`

**Run it** — Find where authority actually concentrates in a multi-agent topology.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a1-control-plane
kubectl apply -f topology/planner-executor-critic.yaml
python3 authority_map.py --namespace agents --max-depth 3
```

*Expect:* A graph showing the node holding the union of all scopes — usually not the one you expected.

---

### A1.7 — Build vs buy

`both directions`

- **Risk** — Outsourcing the control plane to a vendor you cannot audit.
- **Control** — Buy the commodity, build the boundary, never outsource identity or stop authority.
- **Lab** — Score three gateway options against a fixed control checklist.
- **Tools** — `agentgateway`, `Envoy`

**Run it** — Score gateways against a fixed control checklist instead of a feature matrix.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a1-control-plane
python3 score_option.py --option agentgateway --checklist controls.yaml
python3 score_option.py --option envoy-ext-authz --checklist controls.yaml
python3 score_option.py --report
```

*Expect:* Each option scored on: identity mapping, per-tool RBAC, output scanning, audit, stop lever. Gaps are explicit.

---

### A1.8 — Model routing architecture

`both directions`

- **Risk** — The router fails open to a weaker model under load — a silent downgrade of every guardrail.
- **Control** — Treat tier selection as a security decision with explicit fail-closed defaults.
- **Lab** — Route across GLM-4.6 / Llama / Kimi with LiteLLM, then force a failure and watch what it falls back to.
- **Tools** — `LiteLLM`, `vLLM`
- **Models** — `GLM-4.6`, `Llama 3.3`, `Kimi K2`

**Run it** — Prove the router fails closed, not open.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install 'litellm[proxy]'
cd labs/a1-control-plane && litellm --config router.yaml &
python3 force_failure.py --kill primary   # take the reasoner offline mid-request
python3 assert_failclosed.py
```

*Expect:* The router refuses rather than silently downgrading to a weaker model with weaker guardrails.

---

### A1.9 — The injection surface: direct and indirect prompt injection

`Security of AI`

- **Risk** — Attacker text arrives inside a document, ticket, web page, email or code comment, and the agent obeys it. Every untrusted-content path into the context window is an unauthenticated code path nobody enumerated.
- **Control** — Map every untrusted-content path into the context window and treat each as unauthenticated input: provenance tagging, source allow-listing, and no tool selection from an untrusted span.
- **Lab** — Enumerate the untrusted-content paths into one agent's context, land the same payload through each, then show provenance enforcement refusing all of them.
- **Tools** — `garak`, `promptfoo`, `LLM Guard`
- **Models** — `Llama Guard 4`, `GLM-4.6`

**Run it** — Enumerate the untrusted-content paths into one agent's context, land the same payload through each, then show provenance enforcement refusing all of them.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.9   # run it headless and check it
```

*Expect:* Six untrusted-content paths are enumerated, four of them reviewed by nobody. The same payload steers the naive agent through all six. A denylist catches one of four rewrites of the identical instruction, while the provenance rule refuses all six paths and every rewrite — and still lets the user's own request through.

---

### A1.10 — Jailbreaks, model inversion and extraction

`Security of AI`

- **Risk** — The whole model-layer attack taxonomy gets called "jailbreaks". Inversion, membership inference, prompt extraction and embedding inversion each recover something different and are blunted by different controls.
- **Control** — Name what each attack actually recovers, then bind the architectural control that genuinely blunts it — most of which do not sit at the model layer.
- **Lab** — Run each attack class against a deterministic stand-in, record what it recovered, and map each to the layer that can stop it.
- **Tools** — `garak`, `Presidio`
- **Models** — `Llama Guard 4`

**Run it** — Run each attack class against a deterministic stand-in, record what it recovered, and map each to the layer that can stop it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.10   # run it headless and check it
```

*Expect:* Five distinct attacks run against a deterministic stand-in and each prints what it recovered: behaviour, context data, one membership bit, the system prompt, and the source text pulled back out of the vector store. Four of the five are shown to be stoppable at runtime by architecture, and only membership inference requires a decision made before the model existed.

---

### A1.11 — Building outcome-driven guardrails, layer by layer

`Security of AI`

- **Risk** — Guardrails specified by the input string you hope to block. Attackers rewrite strings freely; they cannot rewrite consequences.
- **Control** — Specify each guardrail by the outcome you refuse to permit, then place it at a layer that can actually enforce it — and know that any single-layer defence is a demo.
- **Lab** — Take one refused outcome, place it across all ten enforcement layers, and measure which placements actually deny it.
- **Tools** — `OPA`, `agentgateway`, `Cilium`
- **Models** — `GLM-4.6`

**Run it** — Take one refused outcome, place it across all ten enforcement layers, and measure which placements actually deny it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.11.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.11   # run it headless and check it
```

*Expect:* The ten layers print with what each can and cannot enforce. One refused outcome placed across all ten is denied only at layers 4, 6, 7, 8 and 9 — and layer 9 is then shown degrading to a rubber stamp above about twenty approvals a day. A layered below-the-model configuration refuses the attack and keeps refusing with any single layer removed, while four rephrasings defeat string matching and none defeat the outcome rule.

---

### A1.12 — Proving guardrails work

`Security of AI`

- **Risk** — A guardrail claim with no bypass testing behind it. A control that fails three times in a hundred is not a control against an attacker who can retry.
- **Control** — Adversarial suites and bypass economics that convert a guardrail claim into evidence a red team or an auditor will accept.
- **Lab** — Run a bypass suite against a guardrail and compute the attacker's expected cost per success.
- **Tools** — `garak`, `promptfoo`
- **Models** — `GLM-4.6`

**Run it** — Run a bypass suite against a guardrail and compute the attacker's expected cost per success.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.12.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.12   # run it headless and check it
```

*Expect:* The retry arithmetic prints: a 97% guardrail is defeated within 98 attempts 19 times out of 20, for about twenty cents. Twenty single-run tests of the same control return a mix of passes and failures, and the Wilson interval at n=10 is wide enough to contain both 'strong control' and 'no control'. The lesson ends with a reproducible evidence record carrying a seed, an interval and an attacker cost per success.

---
