# Track B2 — Securing the Architecture — Identity and Ingress

**Function B · Securing AI Architectures**  
*CyberTravels as built, every risk that architecture carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** IAM Engineer, Non-Human Identity Engineer, Platform Security Engineer

**What changes:** The two controls that close the most risks: knowing who is calling, and marking what came in from outside. Each lesson names the threats it closes. 8 lessons.

**Autonomy focus:** Identity first: every later control is a predicate that takes a caller as its argument.

**Deliverable:** A delegation chain for one agent that an auditor can follow from human to action.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### B2.1 — Agent identity — user, workload, agent

- **Risk** — A shared service account answers 'what ran' and destroys 'for whom' — so no later control can be conditioned on the caller.
- **Control** — A distinct identity per workload, carrying the human principal alongside it, asserted on every call.
- **Lab** — Separate the three identities and show a downstream service authorising on the agent while attributing to the human.
- **Tools** — `SPIFFE/SPIRE`, `Keycloak`

**Run it** — Separate the three identities and show a downstream service authorising on the agent while attributing to the human.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B2.1

# --- 3 · in your agent, open this folder and pick the skill:
#         b2-1-agent-identity
#         (Claude Code and Copilot: /b2-1-agent-identity · Cursor: type / and
#         search · Codex: $b2-1-agent-identity). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B2.1
```

---

### B2.2 — Bootstrapping the first credential

- **Risk** — A pre-shared secret in an image or an environment variable is copyable, so possession stops being proof of identity.
- **Control** — Platform attestation exchanged for a short-lived, workload-bound credential.
- **Lab** — Exchange an attestation for a credential, then show a copied secret failing the same exchange.
- **Tools** — `SPIFFE/SPIRE`

**Run it** — Exchange an attestation for a credential, then show a copied secret failing the same exchange.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B2.2

# --- 3 · in your agent, open this folder and pick the skill:
#         b2-2-bootstrapping-the-first-credential
#         (Claude Code and Copilot: /b2-2-bootstrapping-the-first-credential · Cursor: type / and
#         search · Codex: $b2-2-bootstrapping-the-first-credential). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B2.2
```

---

### B2.3 — Delegation that narrows, and survives audit

- **Risk** — Subset-only lets a privileged user hand an agent authority it must never hold; ceiling-only lets the agent exceed the person who asked.
- **Control** — Token exchange that intersects presented scope with the actor's ceiling, and records the chain.
- **Lab** — Run both narrowing rules against a request that passes one and fails the other.
- **Tools** — `SPIFFE/SPIRE`, `Keycloak`, `RFC 8693 token exchange`, `RFC 8705 mTLS binding`

**Run it** — Run both narrowing rules against a request that passes one and fails the other.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B2.3

# --- 3 · in your agent, open this folder and pick the skill:
#         b2-3-delegation-that-narrows
#         (Claude Code and Copilot: /b2-3-delegation-that-narrows · Cursor: type / and
#         search · Codex: $b2-3-delegation-that-narrows). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B2.3
```

---

### B2.4 — Just-in-time authority

- **Risk** — Permanent scope makes every injection a successful one, because the authority is always there when the attacker arrives.
- **Control** — Short-lived, purpose-bound grants issued per task and expiring with it.
- **Lab** — Issue a scoped grant, use it, then replay it after expiry and after the task closed.
- **Tools** — `Keycloak`, `OPA`

**Run it** — Issue a scoped grant, use it, then replay it after expiry and after the task closed.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B2.4

# --- 3 · in your agent, open this folder and pick the skill:
#         b2-4-just-in-time-authority
#         (Claude Code and Copilot: /b2-4-just-in-time-authority · Cursor: type / and
#         search · Codex: $b2-4-just-in-time-authority). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B2.4
```

---

### B2.5 — The non-human identity lifecycle

- **Risk** — Agents accumulate with no owner and no expiry, and an unregistered agent joins a topology as a peer.
- **Control** — A registry with a named owner, an expiry, and admission bound to a registered identity.
- **Lab** — Admit agents against a registry and show an unregistered one refused at the door.
- **Tools** — `SCIM 2.0 (RFC 7643/7644)`, `Keycloak`, `SPIFFE/SPIRE`

**Run it** — Admit agents against a registry and show an unregistered one refused at the door.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B2.5

# --- 3 · in your agent, open this folder and pick the skill:
#         b2-5-the-non-human-identity-lifecycle
#         (Claude Code and Copilot: /b2-5-the-non-human-identity-lifecycle · Cursor: type / and
#         search · Codex: $b2-5-the-non-human-identity-lifecycle). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B2.5
```

---

### B2.6 — Ingress: marking untrusted content at the door

- **Risk** — Concatenation destroys the one fact that separates an operator instruction from an attacker's: where it came from.
- **Control** — Provenance tagging at every ingress point, and a rule that only trusted origins may select a tool.
- **Lab** — Tag every span at ingress, then show the same payload refused through six different entry paths.
- **Tools** — `LLM Guard`, `agentgateway`
- **Open-weight models** — `Llama Guard 4`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Tag every span at ingress, then show the same payload refused through six different entry paths.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B2.6

# --- 3 · in your agent, open this folder and pick the skill:
#         b2-6-ingress-marking-untrusted-content-at-the
#         (Claude Code and Copilot: /b2-6-ingress-marking-untrusted-content-at-the · Cursor: type / and
#         search · Codex: $b2-6-ingress-marking-untrusted-content-at-the). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B2.6
```

---

### B2.7 — Attribution: an audit trail that answers "who"

- **Risk** — Without the motivating input, root cause cannot be established at all; without the principal, nothing can be attributed.
- **Control** — Per-hop attribution written to an append-only store outside the agent's reach.
- **Lab** — Answer 'which user caused this deletion' from the trace, then try the same on a trace missing one field.
- **Tools** — `OpenTelemetry`, `Sigstore`

**Run it** — Answer 'which user caused this deletion' from the trace, then try the same on a trace missing one field.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B2.7

# --- 3 · in your agent, open this folder and pick the skill:
#         b2-7-attribution-an-audit-trail-that-answers
#         (Claude Code and Copilot: /b2-7-attribution-an-audit-trail-that-answers · Cursor: type / and
#         search · Codex: $b2-7-attribution-an-audit-trail-that-answers). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B2.7
```

---

### B2.8 — An audit trail the workload cannot forge

- **Risk** — An agent that escapes its container can rewrite the record of what it did — and every detective control downstream is then reporting on data the subject controls.
- **Control** — Out-of-band capture (C2.10), a hash-chained WORM transcript store (C1.2) and logging-plane isolation (C1.3). Reconcile the two streams; divergence is the signal.
- **Lab** — Spoof a transcript, watch the in-band check pass it, then watch the hash chain and the host-syscall reconciliation both refuse it.
- **Tools** — `Falco`, `Tetragon`, `Sigstore`

**Run it** — Spoof a transcript, watch the in-band check pass it, then watch the hash chain and the host-syscall reconciliation both refuse it.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B2.8

# --- 3 · in your agent, open this folder and pick the skill:
#         b2-8-an-audit-trail-the-workload-cannot-forge
#         (Claude Code and Copilot: /b2-8-an-audit-trail-the-workload-cannot-forge · Cursor: type / and
#         search · Codex: $b2-8-an-audit-trail-the-workload-cannot-forge). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B2.8
```

---

**Adjacency requirement:** also complete B3.1–B3.2 — the failures happen in the seams.
