# Track A2 — The Identity & Non-Human Identity Engineer

**Function A · Security Architecture & Platform**  
*The people who decide what is structurally possible. If they get it wrong, no amount of downstream diligence recovers it.*

**Job titles:** IAM Engineer, NHI Lead, Identity Architect, Workload Identity Engineer

**What changes:** You have a new population of principals that outnumbers your humans, changes hourly, and inherits credentials nobody granted it. The most genuinely new material in the programme.

**Autonomy focus:** Identity is the control that makes L2.5 defensible; without it you are running L3 and calling it L2.

**Deliverable:** A working three-hop delegation chain with proven attenuation, and a rollback of one agent's access without collateral.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A2.1 — "Who is calling?"

`Security of AI`

- **Risk** — You cannot answer the first question of every investigation.
- **Control** — A taxonomy: user-agent vs workload identity, sandboxed vs not, managed vs personal.
- **Lab** — Classify every agent in your lab and record what proves each claim.
- **Tools** — `SPIRE`

---

### A2.2 — The bootstrap problem

`Security of AI`

- **Risk** — Proving identity before you hold a credential — usually solved with a long-lived secret in a file.
- **Control** — Workload attestation: SPIFFE SVIDs, instance identity documents, projected SA tokens, re-attestation on rotation.
- **Lab** — Issue an SVID to a workload with SPIRE and watch it re-attest after rotation — zero static secrets.
- **Tools** — `SPIFFE/SPIRE`, `kind`

**Run it** — Issue a workload identity with zero static secrets.

```bash
cd labs/a2-delegation
kind create cluster --name a2
kubectl apply -f spire/
kubectl exec -n spire spire-server-0 -- /opt/spire/bin/spire-server entry create \
  -spiffeID spiffe://cybercommons/agent/reviewer \
  -parentID spiffe://cybercommons/node -selector k8s:pod-label:app:reviewer
./show-svid.sh   # fetch and decode the SVID from inside the workload
```

*Expect:* A short-lived SVID appears with no secret ever written to disk; re-attests automatically after rotation.

---

### A2.3 — Shadow Autonomy

`Security of AI`

- **Risk** — Agents executing under inherited human credentials — your audit trail is already wrong.
- **Control** — Detect it first, then separate the principal; revocation is impossible until you can name the actor.
- **Lab** — Find agent-vs-human credential use in logs by behavioural signature; then split the principal.
- **Tools** — `Keycloak`, `SPIRE`
- **Models** — `Llama 3.3`

---

### A2.4 — The NHI governance gap

`Security of AI`

- **Risk** — Revoking one misbehaving agent breaks forty others.
- **Control** — Enrolment, ownership, scope, expiry, attribution — an agent registry with honest enforcement limits.
- **Lab** — Build the registry, then revoke exactly one agent and prove no collateral.
- **Tools** — `Keycloak`, `SPIRE`

---

### A2.5 — Delegation that survives audit

`Security of AI`

- **Risk** — On-behalf-of implemented as impersonation — the chain is unprovable afterwards.
- **Control** — RFC 8693 token exchange with the `act` claim as a real delegation chain.
- **Lab** — Build a three-hop chain in Keycloak; decode the `act` claims and show attenuation at each hop.
- **Tools** — `Keycloak`, `RFC 8693`

**Run it** — A three-hop delegation chain that survives audit.

```bash
cd labs/a2-delegation
docker compose up -d keycloak
./setup-realm.sh                 # clients: user-app -> reviewer-agent -> patch-agent
./delegate.sh                    # RFC 8693 token exchange, 3 hops
python3 decode_chain.py token.jwt  # prints the nested act claim chain
```

*Expect:* Each hop shows a nested `act` claim and a strictly smaller scope. Attenuation is visible in the token, not asserted in a doc.

---

### A2.6 — The agentic gateway

`Security of AI`

- **Risk** — Secrets end up in agent code because there was nowhere else to put them.
- **Control** — Gateway-side credential exchange: virtual keys, JWKS validation, identity mapping.
- **Lab** — Put agentgateway in front of an MCP server and move every credential out of the agent.
- **Tools** — `agentgateway`, `kmcp`
- **Models** — `GLM-4.6`

---

### A2.7 — Systems that don't understand agents

`Security of AI`

- **Risk** — Legacy services see only the human's token and grant everything.
- **Control** — Token translation plus action-class blocking at the boundary.
- **Lab** — Allow reads, deny protected-branch merges by token type, at the gateway.
- **Tools** — `agentgateway`, `OPA`

---

### A2.8 — Just-in-time authority

`Security of AI`

- **Risk** — Standing access means an injection always has something to spend.
- **Control** — Human-initiated credential release, change-window binding, maker/checker under agent attribution.
- **Lab** — Cut standing access to zero and issue authority only inside a change window.
- **Tools** — `Keycloak`, `Vault (OSS)`

**Run it** — Cut standing access to zero so an injection has nothing to spend.

```bash
cd labs/a2-delegation
./jit.sh --request deploy --window 15m --approver alice
./jit.sh --status    # authority exists only inside the window
sleep 900 && ./jit.sh --status
```

*Expect:* Authority is absent before and after the window; the agent literally cannot spend what it does not hold.

---

### A2.9 — The classic failures

`Security of AI`

- **Risk** — Confused deputy, token replay, shared static credentials, over-broad scope.
- **Control** — Reproduce each one, then close it.
- **Lab** — Exploit all four in the lab, then re-run against the hardened chain.
- **Tools** — `SPIRE`, `Keycloak`
- **Models** — `Kimi K2`

---

**Adjacency requirement:** also complete A3.1–A3.2 — the failures happen in the seams.
