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

**Run it** — Answer 'who is calling?' for every principal in the lab.

```bash
cd labs/a2-delegation
python3 classify.py --scan-spire --scan-keycloak --out taxonomy.csv
column -s, -t taxonomy.csv
```

*Expect:* Each agent labelled user-agent vs workload, sandboxed vs not, managed vs personal — with the evidence for each claim.

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

**Run it** — Find agents running on inherited human credentials.

```bash
cd labs/a2-delegation
python3 delegate.py impersonate   # what the audit log says vs what happened
python3 shadow_autonomy.py --logs sample-auth.log --baseline human-baseline.json
```

*Expect:* Flags credentials used with machine timing/sequencing. Every hit is an audit trail that is currently wrong.

---

### A2.4 — The NHI governance gap

`Security of AI`

- **Risk** — Revoking one misbehaving agent breaks forty others.
- **Control** — Enrolment, ownership, scope, expiry, attribution — an agent registry with honest enforcement limits.
- **Lab** — Build the registry, then revoke exactly one agent and prove no collateral.
- **Tools** — `Keycloak`, `SPIRE`

**Run it** — Revoke exactly one agent without collateral.

```bash
cd labs/a2-delegation
python3 delegate.py revoke reviewer-agent   # revoke exactly one actor
python3 registry.py --enrol reviewer --owner appsec --scope repo:read --expires 30d
```

*Expect:* reviewer's tokens fail immediately; patcher keeps working. If both die, your scoping was shared.

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
# no-infra variant — stdlib only, runs anywhere:
python3 delegate.py chain && python3 delegate.py verify
python3 delegate.py escalate      # widening refused by the token
python3 delegate.py impersonate   # the anti-pattern (A2.3 Shadow Autonomy)
python3 delegate.py revoke reviewer-agent   # one actor dies, others live (A2.4)

# full variant against real Keycloak (RFC 8693 token exchange):
docker compose up -d keycloak && ./setup-realm.sh && ./delegate.sh
python3 decode_chain.py token.jwt
```

*Expect:* Each hop shows a nested `act` claim and a strictly smaller scope; escalation is refused by the token, not by an app check. Attenuation is visible in the token, not asserted in a doc.

---

### A2.6 — The agentic gateway

`Security of AI`

- **Risk** — Secrets end up in agent code because there was nowhere else to put them.
- **Control** — Gateway-side credential exchange: virtual keys, JWKS validation, identity mapping.
- **Lab** — Put agentgateway in front of an MCP server and move every credential out of the agent.
- **Tools** — `agentgateway`, `kmcp`
- **Models** — `GLM-4.6`

**Run it** — Move every credential out of the agent and into the gateway.

```bash
cd labs/a2-delegation
docker compose up -d agentgateway kmcp
grep -r 'API_KEY\|token' agent/ || echo 'no secrets in agent code'
curl -s localhost:8080/mcp/tools -H "Authorization: Bearer $(cat svid.jwt)" | jq '.tools[].name'
```

*Expect:* The agent holds only its SVID; the gateway exchanges it for the downstream credential.

---

### A2.7 — Systems that don't understand agents

`Security of AI`

- **Risk** — Legacy services see only the human's token and grant everything.
- **Control** — Token translation plus action-class blocking at the boundary.
- **Lab** — Allow reads, deny protected-branch merges by token type, at the gateway.
- **Tools** — `agentgateway`, `OPA`

**Run it** — Teach a legacy service to refuse agent writes it cannot understand.

```bash
cd labs/a2-delegation
python3 action_class.py --allow read --deny protected-branch-merge --by-token-type agent
./try.sh --as agent --action read      # 200
./try.sh --as agent --action merge     # 403 at the gateway, not the app
```

*Expect:* The legacy app is unchanged; the boundary does the work.

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

**Run it** — Reproduce the four classic identity failures, then close them.

```bash
cd labs/a2-delegation/classic-failures
./confused_deputy.sh && ./token_replay.sh && ./shared_creds.sh && ./overbroad_scope.sh
./harden.sh && ./rerun-all.sh
```

*Expect:* All four succeed pre-hardening and fail after. The diff between the runs is your control set.

---

**Adjacency requirement:** also complete A3.1–A3.2 — the failures happen in the seams.
