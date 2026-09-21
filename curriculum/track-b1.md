# Track B1 — CyberTravels' Architecture, and Every Risk It Carries

**Function B · Securing AI Architectures**  
*CyberTravels as built, every risk that architecture carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Security Architect, Principal Security Engineer, Head of Security Architecture

**What changes:** CyberTravels as built, then one lesson per risk that architecture makes possible — mapped to the OWASP Agentic AI threat taxonomy and closed by a register. 18 lessons.

**Autonomy focus:** Read the architecture once; every risk after it names the component it attacks.

**Deliverable:** A component map of one agentic system you run, with every applicable threat marked against the component it lands on.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### B1.0 — Start here — what securing an AI architecture means

- **Lab** — Place the six functions of the commons on one diagram and find where your own work sits.

**Run it** — Place the six functions of the commons on one diagram and find where your own work sits.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.0

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-0-start-here
#         (Claude Code and Copilot: /b1-0-start-here · Cursor: type / and
#         search · Codex: $b1-0-start-here). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.0
```

---

### B1.1 — The reference architecture for agentic AI

- **Risk** — Without a shared picture, 'secure the agent' has no referent and every later risk lands nowhere in particular.
- **Control** — One component map and five topologies, named once and reused by every lesson that follows.
- **Lab** — Build the component graph and the five topologies, then trace one request through each and see where the trust boundary sits.

**Run it** — Build the component graph and the five topologies, then trace one request through each and see where the trust boundary sits.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.1

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-1-the-reference-architecture-for-agentic-a
#         (Claude Code and Copilot: /b1-1-the-reference-architecture-for-agentic-a · Cursor: type / and
#         search · Codex: $b1-1-the-reference-architecture-for-agentic-a). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.1
```

---

### B1.2 — Prompt injection

- **Risk** — The user redirects their own agent past the behaviour the operator specified — bounded by their own authority, and therefore the milder of the two injection risks.
- **Control** — Provenance at ingress (B2.6) and default-deny on the tool call (B3.1). The system prompt is not a control.
- **Lab** — Send an override through the ingress component and watch the agent's goal change.
- **Tools** — `garak`, `promptfoo`
- **Open-weight models** — `Llama Guard 4`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Send an override through the ingress component and watch the agent's goal change.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.2

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-2-prompt-injection
#         (Claude Code and Copilot: /b1-2-prompt-injection · Cursor: type / and
#         search · Codex: $b1-2-prompt-injection). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.2
```

---

### B1.3 — Indirect prompt injection

- **Risk** — Anyone who can write into a corpus the agent reads can steer it, using the victim's authority rather than their own. Nobody is phished and no credential leaks.
- **Control** — Provenance marking at ingress (B2.6), and a rule that untrusted spans may not select a tool (B3.1).
- **Lab** — Poison one retrieved document and watch the agent act on it with the user's authority.
- **Tools** — `garak`, `LLM Guard`
- **Open-weight models** — `Llama Guard 4`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Poison one retrieved document and watch the agent act on it with the user's authority.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.3

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-3-indirect-prompt-injection
#         (Claude Code and Copilot: /b1-3-indirect-prompt-injection · Cursor: type / and
#         search · Codex: $b1-3-indirect-prompt-injection). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.3
```

---

### B1.4 — Memory poisoning

- **Risk** — An attacker's instruction outlives the conversation that delivered it, and re-fires on requests from users who never met the original payload.
- **Control** — Provenance survives into memory (B2.6), and memory writes are scoped to the identity that made them (B2.1).
- **Lab** — Write one poisoned fact into memory and watch it steer a later, unrelated session.
- **Tools** — `LLM Guard`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Write one poisoned fact into memory and watch it steer a later, unrelated session.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.4

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-4-memory-poisoning
#         (Claude Code and Copilot: /b1-4-memory-poisoning · Cursor: type / and
#         search · Codex: $b1-4-memory-poisoning). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.4
```

---

### B1.5 — Tool misuse

- **Risk** — The agent uses a legitimate tool, with legitimate arguments, to do something nobody intended — and every log line looks normal.
- **Control** — Default-deny authorization on the tool call (B3.1) and just-in-time authority (B2.4).
- **Lab** — Call one over-scoped tool with attacker-chosen arguments and see what it reaches.
- **Tools** — `OPA`, `kmcp`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Call one over-scoped tool with attacker-chosen arguments and see what it reaches.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.5

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-5-tool-misuse
#         (Claude Code and Copilot: /b1-5-tool-misuse · Cursor: type / and
#         search · Codex: $b1-5-tool-misuse). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.5
```

---

### B1.6 — Privilege compromise

- **Risk** — The agent acts with more authority than the person who asked it to act, and the log records the service account rather than the human.
- **Control** — Delegation that narrows (B2.3), just-in-time grants (B2.4), and default-deny (B3.1).
- **Lab** — Have an agent inherit a privileged token and reach something its requester never could.
- **Tools** — `Keycloak`, `SPIFFE/SPIRE`

**Run it** — Have an agent inherit a privileged token and reach something its requester never could.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.6

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-6-privilege-compromise
#         (Claude Code and Copilot: /b1-6-privilege-compromise · Cursor: type / and
#         search · Codex: $b1-6-privilege-compromise). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.6
```

---

### B1.7 — Identity spoofing and impersonation

- **Risk** — Attribution fails before the incident starts: you cannot say which agent acted, so you cannot revoke one without breaking all of them.
- **Control** — Per-workload identity with attestation (B2.1, B2.2) and a lifecycle that can revoke one (B2.5).
- **Lab** — Have two agents share a credential, then try to work out which one made the call.
- **Tools** — `SPIFFE/SPIRE`

**Run it** — Have two agents share a credential, then try to work out which one made the call.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.7

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-7-identity-spoofing-and-impersonation
#         (Claude Code and Copilot: /b1-7-identity-spoofing-and-impersonation · Cursor: type / and
#         search · Codex: $b1-7-identity-spoofing-and-impersonation). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.7
```

---

### B1.8 — Malicious code execution

- **Risk** — Model-authored code runs with the runtime's privileges — reaching the filesystem, the network and any credential in the environment.
- **Control** — Sandboxed execution (B3.2) and egress control (B3.3).
- **Lab** — Execute model-authored code and enumerate what the process could touch.
- **Tools** — `Falco`, `gVisor`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Execute model-authored code and enumerate what the process could touch.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.8

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-8-malicious-code-execution
#         (Claude Code and Copilot: /b1-8-malicious-code-execution · Cursor: type / and
#         search · Codex: $b1-8-malicious-code-execution). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.8
```

---

### B1.9 — Injection through content the agent was asked to read

- **Risk** — The pipeline reads attacker-controlled code and then takes actions — a confused deputy you built yourself.
- **Control** — Instruction/data provenance: content the pipeline read may never drive a state-changing tool.
- **Lab** — Fire four realistic payloads at the review harness and compare keyword filtering against provenance.
- **Tools** — `OpenGrep`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Fire four realistic payloads at the review harness and compare keyword filtering against provenance.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.9

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-9-injection-through-content-the-agent-was
#         (Claude Code and Copilot: /b1-9-injection-through-content-the-agent-was · Cursor: type / and
#         search · Codex: $b1-9-injection-through-content-the-agent-was). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.9
```

---

### B1.10 — Agent communication poisoning

- **Risk** — One compromised agent steers every agent downstream of it, because a peer's message is treated as a colleague's instruction rather than as input.
- **Control** — Message validation and provenance on the inter-agent channel (B3.5), and per-agent identity (B2.1).
- **Lab** — Send one poisoned inter-agent message and watch it propagate through the topology.
- **Tools** — `agentgateway`

**Run it** — Send one poisoned inter-agent message and watch it propagate through the topology.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.10

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-10-agent-communication-poisoning
#         (Claude Code and Copilot: /b1-10-agent-communication-poisoning · Cursor: type / and
#         search · Codex: $b1-10-agent-communication-poisoning). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.10
```

---

### B1.11 — Rogue agents in a multi-agent system

- **Risk** — An agent nobody approved receives delegated work and delegated authority, and the orchestrator has no way to tell it apart from a legitimate worker.
- **Control** — A registry of approved agents with identity-bound admission (B2.5) and an audit trail per hop (B2.7).
- **Lab** — Introduce an unregistered agent into the topology and have it receive delegated work.
- **Tools** — `SPIFFE/SPIRE`, `kagent`

**Run it** — Introduce an unregistered agent into the topology and have it receive delegated work.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.11

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-11-rogue-agents-in-a-multi-agent-system
#         (Claude Code and Copilot: /b1-11-rogue-agents-in-a-multi-agent-system · Cursor: type / and
#         search · Codex: $b1-11-rogue-agents-in-a-multi-agent-system). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.11
```

---

### B1.12 — Cascading hallucination

- **Risk** — A single fabrication becomes a shared premise, and by the third hop nothing in the system records that it was ever uncertain.
- **Control** — Verification against ground truth before a claim propagates (B3.5).
- **Lab** — Let one fabricated fact travel three hops and watch its confidence rise as its provenance disappears.
- **Tools** — `Inspect`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Let one fabricated fact travel three hops and watch its confidence rise as its provenance disappears.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.12

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-12-cascading-hallucination
#         (Claude Code and Copilot: /b1-12-cascading-hallucination · Cursor: type / and
#         search · Codex: $b1-12-cascading-hallucination). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.12
```

---

### B1.13 — Resource overload

- **Risk** — An agent consumes budget, tokens, API quota or downstream capacity without bound, and the failure is denial of service against your own systems.
- **Control** — Budgets and stop conditions bound to the loop (B3.4).
- **Lab** — Run a loop with no ceiling and count what it consumes before anything notices.
- **Tools** — `OpenTelemetry`

**Run it** — Run a loop with no ceiling and count what it consumes before anything notices.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.13

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-13-resource-overload
#         (Claude Code and Copilot: /b1-13-resource-overload · Cursor: type / and
#         search · Codex: $b1-13-resource-overload). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.13
```

---

### B1.14 — Repudiation and untraceability

- **Risk** — You cannot say which user caused an action, or what made the agent decide — so the incident cannot be scoped and the action cannot be attributed.
- **Control** — Attribution carried on every hop, in a store the agent cannot write to (B2.7).
- **Lab** — Reconstruct who caused a deletion from a log that records only tool calls.
- **Tools** — `OpenTelemetry`

**Run it** — Reconstruct who caused a deletion from a log that records only tool calls.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.14

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-14-repudiation-and-untraceability
#         (Claude Code and Copilot: /b1-14-repudiation-and-untraceability · Cursor: type / and
#         search · Codex: $b1-14-repudiation-and-untraceability). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.14
```

---

### B1.15 — Overwhelming the human in the loop

- **Risk** — The approval gate is recorded as a control and operates as a click. At volume it approves everything, including the one request that mattered.
- **Control** — Approval reserved for irreversible actions, with everything else bounded by policy (B3.6).
- **Lab** — Push approval volume up and measure the point at which review quality collapses.

**Run it** — Push approval volume up and measure the point at which review quality collapses.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.15

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-15-overwhelming-the-human-in-the-loop
#         (Claude Code and Copilot: /b1-15-overwhelming-the-human-in-the-loop · Cursor: type / and
#         search · Codex: $b1-15-overwhelming-the-human-in-the-loop). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.15
```

---

### B1.16 — Misaligned and deceptive behaviour

- **Risk** — The agent satisfies the letter of its instruction — including by reporting a success it did not achieve — and the transcript contains no lie you can point at.
- **Control** — An independent verifier that checks the outcome rather than the claim (B3.5).
- **Lab** — Give an agent an objective it can satisfy the wrong way, and watch it do exactly that.
- **Tools** — `Inspect`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Give an agent an objective it can satisfy the wrong way, and watch it do exactly that.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.16

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-16-misaligned-and-deceptive-behaviour
#         (Claude Code and Copilot: /b1-16-misaligned-and-deceptive-behaviour · Cursor: type / and
#         search · Codex: $b1-16-misaligned-and-deceptive-behaviour). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.16
```

---

### B1.17 — Attacks that target the humans

- **Risk** — The delegation chain is used as a privilege-laundering path, and the agent's output becomes an unusually persuasive channel into a human decision.
- **Control** — Ceiling-bound delegation (B2.3), attribution per hop (B2.7) and marking machine-generated output as such (B3.6).
- **Lab** — Launder a request through a delegation chain to reach something the requester was denied.

**Run it** — Launder a request through a delegation chain to reach something the requester was denied.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.17

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-17-attacks-that-target-the-humans
#         (Claude Code and Copilot: /b1-17-attacks-that-target-the-humans · Cursor: type / and
#         search · Codex: $b1-17-attacks-that-target-the-humans). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.17
```

---

### B1.18 — The CyberTravels risk register

- **Risk** — A list of risks is read once. Without a component, a control and an owner against each row, nothing in it is actionable and nothing in it is re-checkable when CyberTravels grows a fifth agent.
- **Control** — Four columns — scene, component, control, owning lesson — and a rule that no row ships without the fourth.
- **Lab** — Roll the twelve risks up into families, find which agent carries each, and check that every row has an owner.

**Run it** — Roll the twelve risks up into families, find which agent carries each, and check that every row has an owner.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.18

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-18-the-cybertravels-risk-register
#         (Claude Code and Copilot: /b1-18-the-cybertravels-risk-register · Cursor: type / and
#         search · Codex: $b1-18-the-cybertravels-risk-register). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.18
```

---

### B1.19 — The control index — every control CyberTravels needs, not only the new ones

- **Risk** — A team that has just shipped agents writes an agentic control list. Every row is right, and it reports coverage against the wrong denominator — saying nothing about the older, more reachable controls an attacker will actually start from.
- **Control** — One index carrying both eras, a three-valued status measured against what runs rather than what is documented, an owner per row, and coverage reported per era rather than blended.
- **Lab** — Score the twenty-two controls and read the two coverage lines separately — the gap between them is the finding.

**Run it** — Score the twenty-two controls and read the two coverage lines separately — the gap between them is the finding.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons B1.19

# --- 3 · in your agent, open this folder and pick the skill:
#         b1-19-the-control-index
#         (Claude Code and Copilot: /b1-19-the-control-index · Cursor: type / and
#         search · Codex: $b1-19-the-control-index). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py B1.19
```

---

**Adjacency requirement:** also complete B2.1–B2.2 — the failures happen in the seams.
