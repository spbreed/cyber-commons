# Track C1 — The Pentester / Red Teamer

**Function C · Offensive Security & Research**  
*The function that finds out what is actually true, as opposed to what the architecture diagram claims.*

**Job titles:** Penetration Tester, Red Team Operator, Offensive Security Engineer

**What changes:** You become a scenario architect rather than a tool runner. And you acquire an entirely new target class: the agent itself.

**Autonomy focus:** You test at L3 the systems deployed at L2.5, because that's where they'll be next quarter.

**Deliverable:** A full agent red-team engagement report against an internal agentic workflow, with reproducible traces.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### C1.1 — Agentic offensive workflow

`AI for Security`

- **Risk** — Payload suggestions instead of attack chains.
- **Control** — Feed the harness full target context before it swings.
- **Lab** — Drive a planner/executor pair against a local vulnerable target — never the open internet.
- **Tools** — `CAI`, `Metasploit`, `InterCode-CTF`
- **Models** — `Kimi K2`, `GLM-4.6`

**Run it** — Drive a planner/executor pair against a local target you own.

```bash
cd labs/c1-redteam
docker compose up -d dvwa juice-shop     # local targets only
python3 offensive_loop.py --target http://localhost:3000 --model $MODEL --scope scope.yaml
```

*Expect:* Attack chains, not payload suggestions. scope.yaml is enforced by the harness — out-of-scope hosts are refused.

---

### C1.2 — Sandboxing the offensive harness

`Security of AI`

- **Risk** — Your harness is the most dangerous one in the building.
- **Control** — Exploit isolation, target scoping, authorization and legal guardrails.
- **Lab** — Air-gap the offensive lab and prove no route to anything you don't own.
- **Tools** — `Firecracker`, `Squid`

**Run it** — Prove the offensive harness cannot reach anything you don't own.

```bash
cd labs/c1-redteam
./airgap.sh up   # isolated docker network, no default route
./scope-test.sh --in-scope http://target.local --out-of-scope https://example.com
```

*Expect:* In-scope succeeds, out-of-scope fails at the network layer — not at a politeness check in the prompt.

---

### C1.3 — Red-teaming agents: the injection surface

`Security of AI`

- **Risk** — Retrieval poisoning, tool-output poisoning, multi-turn manipulation.
- **Control** — Systematic injection campaigns with measured success rates.
- **Lab** — Run garak + promptfoo campaigns against your own production agent.
- **Tools** — `garak`, `promptfoo`
- **Models** — `Llama 3.3`

**Run it** — Run a real injection campaign and get a success rate.

```bash
pip install garak promptfoo
cd labs/c1-redteam
garak --model_type openai.OpenAICompatible --model_name $MODEL --probes promptinject,dan,encoding
promptfoo eval -c redteam.yaml
```

*Expect:* A measured attack-success-rate per probe family, per model — comparable across Llama / GLM / Kimi.

---

### C1.4 — Red-teaming agents: the identity surface

`Security of AI`

- **Risk** — Confused deputy, token replay, scope escalation through delegation chains.
- **Control** — Test whether revocation actually revokes.
- **Lab** — Attack the A2 delegation chain; prove or disprove attenuation.
- **Tools** — `Keycloak`, `SPIRE`

**Run it** — Attack the delegation chain and see if attenuation holds.

```bash
cd labs/c1-redteam
python3 attack_identity.py --target ../a2-delegation --technique confused-deputy
python3 attack_identity.py --target ../a2-delegation --technique token-replay
python3 attack_identity.py --target ../a2-delegation --technique scope-escalation
python3 attack_identity.py --verify-revocation
```

*Expect:* A pass/fail per technique against A2's chain — including whether revocation actually revokes.

---

### C1.5 — Red-teaming agents: the containment surface

`Security of AI`

- **Risk** — Sandbox escape, egress bypass, path-guard evasion.
- **Control** — Prove the stop lever fires under load.
- **Lab** — Attack the A3 sandbox from inside; measure what leaves.
- **Tools** — `Falco`, `gVisor`

**Run it** — Attack the sandbox from inside and measure what leaves.

```bash
cd labs/c1-redteam
python3 escape.py --target ../a3-sandbox --techniques mount,egress,path-guard,mcp
python3 escape.py --measure-exfil --bytes-out
```

*Expect:* Blast radius in bytes and reachable hosts. A3's deliverable is zero outside the sandbox.

---

### C1.6 — Attacking evaluation itself

`Security of AI`

- **Risk** — If the eval can be fooled, the assurance is theatre.
- **Control** — Eval gaming, sandbagging, contamination and judge manipulation as test cases.
- **Lab** — Game the B2.10 harness deliberately, then close the hole you used.
- **Tools** — `Cyber Commons eval harness`
- **Models** — `Kimi K2`

**Run it** — Game the eval deliberately, then close the hole you used.

```bash
cd labs/b2.10-eval-harness
python3 ../c1-redteam/game_eval.py --strategy sandbag
python3 ../c1-redteam/game_eval.py --strategy judge-manipulation
scripts/vulnbench.sh compare   # see the inflated number
```

*Expect:* You reproduce an inflated score, then patch the harness so the same trick fails.

---

### C1.7 — Reporting agentic findings

`both directions`

- **Risk** — The vulnerability is emergent behaviour, not a line of code.
- **Control** — Reproducibility requirements for probabilistic systems.
- **Lab** — Write a finding a CISO can act on, with a replayable trace.
- **Tools** — `OpenTelemetry`

**Run it** — Write a finding for an emergent behaviour, not a line of code.

```bash
cd labs/c1-redteam
python3 report.py --from-trace engagement/trace.jsonl --template agentic-finding.md
python3 report.py --verify-reproducible --runs 10
```

*Expect:* A finding with a reproduction rate (e.g. 7/10), not a claim of determinism the system cannot offer.

---
