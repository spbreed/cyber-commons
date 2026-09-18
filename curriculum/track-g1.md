# Track G1 — Build the Agent — From a Loop to a Running Platform

**Function G · Getting Started — Building Agentic AI**  
*Build the system first. A working agentic platform — the loop, MCP tools, identity and delegation, memory, agent-to-agent messaging, a human gate, spans and an audit trail — and the harness that makes it operable. Everything the other four functions attack, defend, detect and govern is built here, by you, before any of it is called a risk.*

**Job titles:** Anyone who will work on or around agentic systems: engineers, AppSec, red teamers, SOC and GRC. It assumes you can read a Python function and have finished A0.0's setup. It assumes no security background at all.

**What changes:** Eight lessons that build one system end to end: the reasoning loop and its verifier, two MCP resource servers, workload identity, per-action delegation, scoped memory, signed agent-to-agent messages, and the human gate with the budget beside it. At the end you are running CyberTravels on your own machine. 8 lessons.

**Autonomy focus:** This chapter is where autonomy is introduced rather than argued about: the agent acts, and you decide which actions it may take unattended.

**Deliverable:** A running agentic platform you built, with every component the rest of the commons refers to.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### G1.0 — What an agent is, and what you are about to build

- **Risk** — Security guidance aimed at people who have never built an agent lands as a list of rules with no mechanism attached, and gets applied as paperwork.
- **Control** — Build it first. Every control in Function A attaches to a component drawn here.
- **Lab** — Map the architecture you are about to build, and mark where trust changes.
- **Tools** — `MCP`, `FastAPI`

**Run it** — Map the architecture you are about to build, and mark where trust changes.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G1.0.
#         Everything taught so far; nothing taught after it. The
#         directory is named cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G1.0 --out work/cybertravels
python3 scripts/checkpoint.py --at G1.0 --diff      # what this lesson added

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/architecture/agentic-architecture-map/scripts/agentic_architecture_map.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all

# --- 5 · and run your copy. 127.0.0.1 only: it is deliberately
#         vulnerable. See cybertravels/LABELS.md. ---
pip install -r work/cybertravels/requirements.txt
cd work && python3 -m cybertravels.tests.smoke_test
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
```

*Expect:* Seven components, the edges between them, and the smaller subset where trust changes — which is the only part worth arguing about.

---

### G1.1 — The loop — model, tools, and the step that turns text into an action

- **Risk** — A loop with no verifier accepts whatever the model says it did, and a demo that 'works' has never been checked.
- **Control** — Plan, act, verify — with the verifier independent of the thing it checks.
- **Lab** — Build the loop and add the independent verifier that decides what it may accept.
- **Tools** — `Anthropic SDK`, `MCP`

**Run it** — Build the loop and add the independent verifier that decides what it may accept.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G1.1.
#         Everything taught so far; nothing taught after it. The
#         directory is named cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G1.1 --out work/cybertravels
python3 scripts/checkpoint.py --at G1.1 --diff      # what this lesson added

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/appsec/agentic-harness-loop/scripts/agentic_harness_loop.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all

# --- 5 · and run your copy. 127.0.0.1 only: it is deliberately
#         vulnerable. See cybertravels/LABELS.md. ---
pip install -r work/cybertravels/requirements.txt
cd work && python3 -m cybertravels.tests.smoke_test
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
```

*Expect:* The loop's three stages named, an exit condition that does not depend on the model agreeing, and the verifier identified as independent or flagged as not being so.

---

### G1.2 — Tools over MCP — a resource server, and why it is a separate process

- **Risk** — Tools called in-process share the agent's authority by default, and there is no place left to put a check.
- **Control** — A resource server per trust domain, each with its own audience.
- **Lab** — Stand up both MCP servers and list their tools from the client.
- **Tools** — `MCP`

**Run it** — Stand up both MCP servers and list their tools from the client.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G1.2.
#         Everything taught so far; nothing taught after it. The
#         directory is named cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G1.2 --out work/cybertravels
python3 scripts/checkpoint.py --at G1.2 --diff      # what this lesson added

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/attestation/agent-code-surface-analyzer/scripts/agent_code_surface_analyzer.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all

# --- 5 · and run your copy. 127.0.0.1 only: it is deliberately
#         vulnerable. See cybertravels/LABELS.md. ---
pip install -r work/cybertravels/requirements.txt
cd work && python3 -m cybertravels.tests.smoke_test
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
```

*Expect:* Both MCP servers' tools enumerated with the audience and scope each requires, and any tool whose declared surface is wider than its implementation.

---

### G1.3 — Identity — the human, the workload, and the call

- **Risk** — A shared service-account key makes every action look identical in the log, and no investigation can name who caused one.
- **Control** — A workload identity per agent, and a session token for the human that grants nothing downstream.
- **Lab** — Mint both tokens and read the claims that make them different.
- **Tools** — `SPIFFE/SPIRE`, `PyJWT`

**Run it** — Mint both tokens and read the claims that make them different.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G1.3.
#         Everything taught so far; nothing taught after it. The
#         directory is named cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G1.3 --out work/cybertravels
python3 scripts/checkpoint.py --at G1.3 --diff      # what this lesson added

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/identity/agent-identity-review/scripts/agent_identity_review.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all

# --- 5 · and run your copy. 127.0.0.1 only: it is deliberately
#         vulnerable. See cybertravels/LABELS.md. ---
pip install -r work/cybertravels/requirements.txt
cd work && python3 -m cybertravels.tests.smoke_test
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
```

*Expect:* Three principals named and separated, the agent's identity distinguished from any credential it holds, and the human's token shown to grant nothing downstream.

---

### G1.4 — Delegation — one token per action

- **Risk** — An agent holding a long-lived token with every scope is one prompt away from using all of them.
- **Control** — Per-action exchange, least privilege keyed to the human's role, enforced at the resource server.
- **Lab** — Exchange a token, then watch a traveller's role refuse to delegate a refund scope.
- **Tools** — `OAuth 2.0 Token Exchange`, `Keycloak`

**Run it** — Exchange a token, then watch a traveller's role refuse to delegate a refund scope.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G1.4.
#         Everything taught so far; nothing taught after it. The
#         directory is named cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G1.4 --out work/cybertravels
python3 scripts/checkpoint.py --at G1.4 --diff      # what this lesson added

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/attestation/identity-chain-verifier/scripts/identity_chain_verifier.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all

# --- 5 · and run your copy. 127.0.0.1 only: it is deliberately
#         vulnerable. See cybertravels/LABELS.md. ---
pip install -r work/cybertravels/requirements.txt
cd work && python3 -m cybertravels.tests.smoke_test
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
```

*Expect:* A delegated token whose subject is the human and whose actor is the agent, addressed to one audience with one scope — and a refusal, with its reason, when a traveller's role is asked to delegate a refund.

---

### G1.5 — Memory — what it remembers, and where that came from

- **Risk** — Text an agent read becomes a fact an agent learned, and one vendor sentence outlives the request that fetched it.
- **Control** — Origin travels with content; recall never crosses an owner boundary; delete and export both exist.
- **Lab** — Write a vendor sentence into memory and watch it come back labelled untrusted.
- **Tools** — `pgvector`

**Run it** — Write a vendor sentence into memory and watch it come back labelled untrusted.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G1.5.
#         Everything taught so far; nothing taught after it. The
#         directory is named cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G1.5 --out work/cybertravels
python3 scripts/checkpoint.py --at G1.5 --diff      # what this lesson added

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/threats/memory-scope-and-origin-audit/scripts/memory_scope_and_origin_audit.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all

# --- 5 · and run your copy. 127.0.0.1 only: it is deliberately
#         vulnerable. See cybertravels/LABELS.md. ---
pip install -r work/cybertravels/requirements.txt
cd work && python3 -m cybertravels.tests.smoke_test
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
```

*Expect:* Entries carrying an origin and a trust flag, recall refusing to cross an owner boundary, and untrusted entries still labelled when rendered for the model.

---

### G1.6 — Agent to agent — handing work over without laundering authority

- **Risk** — A peer's message read as a colleague's instruction turns one injected document into four compromised agents.
- **Control** — Signed envelopes, the human carried through every hop, and a ceiling on hops.
- **Lab** — Forge a peer message and watch verification refuse it.
- **Tools** — `A2A`

**Run it** — Forge a peer message and watch verification refuse it.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G1.6.
#         Everything taught so far; nothing taught after it. The
#         directory is named cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G1.6 --out work/cybertravels
python3 scripts/checkpoint.py --at G1.6 --diff      # what this lesson added

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/threats/peer-message-propagation-trace/scripts/peer_message_propagation_trace.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all

# --- 5 · and run your copy. 127.0.0.1 only: it is deliberately
#         vulnerable. See cybertravels/LABELS.md. ---
pip install -r work/cybertravels/requirements.txt
cd work && python3 -m cybertravels.tests.smoke_test
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
```

*Expect:* A signed envelope naming its sender and the human it acts for, plus refusals on a tampered envelope and on one with no human in the chain.

---

### G1.7 — The human gate, and the budget that stops the loop

- **Risk** — An unbounded loop against an impossible task spends until somebody notices, and a gate nobody can approve fast enough is a gate that gets removed.
- **Control** — High-risk actions gated on a named human; budgets that bind and are recorded when they bind.
- **Lab** — Approve one action, refuse another, then exhaust the budget on purpose.
- **Tools** — `OPA`

**Run it** — Approve one action, refuse another, then exhaust the budget on purpose.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of G1.7.
#         Everything taught so far; nothing taught after it. The
#         directory is named cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at G1.7 --out work/cybertravels
python3 scripts/checkpoint.py --at G1.7 --diff      # what this lesson added

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/runtime/budget-and-stop-condition-audit/scripts/budget_and_stop_condition_audit.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all

# --- 5 · and run your copy. 127.0.0.1 only: it is deliberately
#         vulnerable. See cybertravels/LABELS.md. ---
pip install -r work/cybertravels/requirements.txt
cd work && python3 -m cybertravels.tests.smoke_test
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
```

*Expect:* A high-risk action pausing and naming its scope, an approval and a refusal both recorded, and a budget ceiling returning an incomplete result rather than a summary.

---
