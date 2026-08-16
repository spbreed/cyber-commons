# Track A1 — The Security Architect

**Function A · Security Architecture & Platform**  
*The people who decide what is structurally possible. If they get it wrong, no amount of downstream diligence recovers it.*

**Job titles:** Security Architect, Principal Security Engineer, Head of Security Architecture

**What changes:** You stop reviewing designs and start designing the control plane other people's agents run inside. Your artefact stops being a document and becomes a runtime.

**Autonomy focus:** Designs must be safe at L3 even when deployed at L2.5.

**Deliverable:** A reference architecture and a blast-radius measurement for one real business workflow.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A1.1 — Architecture review when the system acts

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

### A1.2 — Designing the agent control plane

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

### A1.3 — Authorization models that make bad grants impossible

`Security of AI`

- **Risk** — RBAC has no unit small enough to express the grant you actually meant.
- **Control** — ReBAC/ABAC with time-scoped delegation and attenuation by construction.
- **Lab** — Model the same grant in flat RBAC and in OpenFGA; prove the over-privileged grant is unrepresentable.
- **Tools** — `OpenFGA`, `OPA`

**Run it** — Make the over-privileged grant structurally unrepresentable.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A1.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A1.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
docker run -d -p 8080:8080 openfga/openfga run
cd labs/a1-control-plane/authz
fga model write --file model.fga
python3 prove_unrepresentable.py   # attempts to write the bad grant
```

*Expect:* The bad grant is rejected by the schema, not by a policy check that could be skipped.

---

### A1.4 — Blast radius as a design metric

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

### A1.5 — Multi-agent topology

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

### A1.6 — Build vs buy

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

### A1.7 — Model routing architecture

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
