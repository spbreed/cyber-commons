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

---

### A1.5 — Multi-agent topology

`Security of AI`

- **Risk** — Fan-out concentrates authority somewhere nobody drew.
- **Control** — Planner/executor/critic splits with delegation-depth limits.
- **Lab** — Build a 3-agent topology in kagent and chart where authority actually accumulates.
- **Tools** — `kagent`
- **Models** — `GLM-4.6`, `Llama 3.3`

---

### A1.6 — Build vs buy

`both directions`

- **Risk** — Outsourcing the control plane to a vendor you cannot audit.
- **Control** — Buy the commodity, build the boundary, never outsource identity or stop authority.
- **Lab** — Score three gateway options against a fixed control checklist.
- **Tools** — `agentgateway`, `Envoy`

---

### A1.7 — Model routing architecture

`both directions`

- **Risk** — The router fails open to a weaker model under load — a silent downgrade of every guardrail.
- **Control** — Treat tier selection as a security decision with explicit fail-closed defaults.
- **Lab** — Route across GLM-4.6 / Llama / Kimi with LiteLLM, then force a failure and watch what it falls back to.
- **Tools** — `LiteLLM`, `vLLM`
- **Models** — `GLM-4.6`, `Llama 3.3`, `Kimi K2`

---
