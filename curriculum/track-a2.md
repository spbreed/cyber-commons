# Track A2 — Securing the Architecture — Identity and Ingress

**Function A · Securing AI Architectures**  
*One vendor-neutral reference architecture for agentic AI, every risk it carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** IAM Engineer, Non-Human Identity Engineer, Platform Security Engineer

**What changes:** The two controls that close the most risks: knowing who is calling, and marking what came in from outside. Each lesson names the threats it closes. 7 lessons.

**Autonomy focus:** Identity first: every later control is a predicate that takes a caller as its argument.

**Deliverable:** A delegation chain for one agent that an auditor can follow from human to action.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A2.1 — Agent identity: user, workload, agent

`Security of AI`

- **Risk** — A shared service account answers 'what ran' and destroys 'for whom' — so no later control can be conditioned on the caller.
- **Control** — A distinct identity per workload, carrying the human principal alongside it, asserted on every call.
- **Lab** — Separate the three identities and show a downstream service authorising on the agent while attributing to the human.
- **Tools** — `SPIFFE/SPIRE`, `Keycloak`

**Run it** — Separate the three identities and show a downstream service authorising on the agent while attributing to the human.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A2.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A2.1   # run it headless and check it
```

*Expect:* Authorization resolves against the workload ceiling and refuses `db:admin` no matter who asks, attribution names the human on every action, and memory keys differ per user so a note written in one session cannot be read back in another's.

---

### A2.2 — Bootstrapping the first credential

`Security of AI`

- **Risk** — A pre-shared secret in an image or an environment variable is copyable, so possession stops being proof of identity.
- **Control** — Platform attestation exchanged for a short-lived, workload-bound credential.
- **Lab** — Exchange an attestation for a credential, then show a copied secret failing the same exchange.
- **Tools** — `SPIFFE/SPIRE`

**Run it** — Exchange an attestation for a credential, then show a copied secret failing the same exchange.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A2.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A2.2   # run it headless and check it
```

*Expect:* An unattested process receives no credential, a genuine but unregistered image receives none either, and a credential issued to a real workload is refused when presented from another node or after its five-minute expiry.

---

### A2.3 — Delegation that narrows, and survives audit

`Security of AI`

- **Risk** — Subset-only lets a privileged user hand an agent authority it must never hold; ceiling-only lets the agent exceed the person who asked.
- **Control** — Token exchange that intersects presented scope with the actor's ceiling, and records the chain.
- **Lab** — Run both narrowing rules against a request that passes one and fails the other.
- **Tools** — `Keycloak`

**Run it** — Run both narrowing rules against a request that passes one and fails the other.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A2.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A2.3   # run it headless and check it
```

*Expect:* A two-hop delegation narrows to `reports:read` and records the chain `dana → orchestrator → patch-agent`. A privileged user's request for `db:admin` passes subset-of-presented and still issues nothing, because the receiving agent's ceiling is empty of it.

---

### A2.4 — Just-in-time authority

`Security of AI`

- **Risk** — Permanent scope makes every injection a successful one, because the authority is always there when the attacker arrives.
- **Control** — Short-lived, purpose-bound grants issued per task and expiring with it.
- **Lab** — Issue a scoped grant, use it, then replay it after expiry and after the task closed.
- **Tools** — `Keycloak`, `OPA`

**Run it** — Issue a scoped grant, use it, then replay it after expiry and after the task closed.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A2.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A2.4   # run it headless and check it
```

*Expect:* A grant bound to one scope, one resource and one task permits only the task's own write — refusing a different report, a different scope, any use after the task closes, and any use after the TTL expires.

---

### A2.5 — The non-human identity lifecycle

`Security of AI`

- **Risk** — Agents accumulate with no owner and no expiry, and an unregistered agent joins a topology as a peer.
- **Control** — A registry with a named owner, an expiry, and admission bound to a registered identity.
- **Lab** — Admit agents against a registry and show an unregistered one refused at the door.
- **Tools** — `SPIFFE/SPIRE`, `kagent`

**Run it** — Admit agents against a registry and show an unregistered one refused at the door.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A2.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A2.5   # run it headless and check it
```

*Expect:* Four agents present identities and one is admitted: the unregistered one is refused, the lapsed registration is refused, and the orphaned entry with no owner is refused. Revoking a single agent then leaves the others running.

---

### A2.6 — Ingress: marking untrusted content at the door

`Security of AI`

- **Risk** — Concatenation destroys the one fact that separates an operator instruction from an attacker's: where it came from.
- **Control** — Provenance tagging at every ingress point, and a rule that only trusted origins may select a tool.
- **Lab** — Tag every span at ingress, then show the same payload refused through six different entry paths.
- **Tools** — `LLM Guard`, `agentgateway`
- **Models** — `Llama Guard 4`

**Run it** — Tag every span at ingress, then show the same payload refused through six different entry paths.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A2.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A2.6   # run it headless and check it
```

*Expect:* The same payload is refused through all five untrusted ingress components and through two rewordings, the user's own request still reaches the tool, and a memory record written from an untrusted document is still refused a week later because the origin was stored with it.

---

### A2.7 — Attribution: an audit trail that answers "who"

`Security of AI`

- **Risk** — Without the motivating input, root cause cannot be established at all; without the principal, nothing can be attributed.
- **Control** — Per-hop attribution written to an append-only store outside the agent's reach.
- **Lab** — Answer 'which user caused this deletion' from the trace, then try the same on a trace missing one field.
- **Tools** — `OpenTelemetry`, `Sigstore`

**Run it** — Answer 'which user caused this deletion' from the trace, then try the same on a trace missing one field.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A2.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A2.7   # run it headless and check it
```

*Expect:* One ledger entry answers all four investigation questions — the human principal, the attested workload and run, the delegation chain, and the motivating input with its origin — and the agent's attempt to amend the record is refused.

---

**Adjacency requirement:** also complete A3.1–A3.2 — the failures happen in the seams.
