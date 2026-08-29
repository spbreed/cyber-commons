# Track C1 — The Pentester / Red Teamer

**Function C · AI for Security Research**  
*Offensive testing and research where the agent is both the instrument and the target, and where a result is only worth what it can be reproduced at.*

**Job titles:** Penetration Tester, Red Team Operator, Offensive Security Engineer

**What changes:** Three surfaces, one adversary mindset — and a campaign that reports a rate. 5 lessons.

**Autonomy focus:** You test at L3 the systems deployed at L2.5, because that's where they'll be next quarter.

**Deliverable:** A full agent red-team engagement report against an internal agentic workflow, with reproducible traces.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### C1.0 — Start here — what AI security research means

`both directions`

- **Risk** — Offensive work that produces anecdotes: a result that worked once, on one target, with no rate and no reproduction.
- **Control** — A campaign with a stated criterion, a harness that separates the model effect from the harness effect, and a handoff that ends in a control.
- **Lab** — Take one published agentic attack and list what you would need to reproduce it.

**Run it** — Score the same claim at four standards of proof and find where the line between an anecdote and a result actually sits.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C1.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C1.0   # run it headless and check it
```

*Expect:* The three attack surfaces of an agent print with what each covers, and the same claim scores as anecdote, measurement, result or evidence depending on whether it carries a rate, a control comparison and an independent reproduction.

---

### C1.1 — The agentic offensive workflow, and containing it

`both directions`

- **Risk** — Payload suggestions instead of attack chains — and an offensive loop with no hard scope enforcement, which is an incident with a project plan.
- **Control** — Full target context before it swings, and scope enforced at the network layer rather than by a politeness clause in the prompt.
- **Lab** — Drive a planner/executor pair against a local target and watch the scope guard refuse an out-of-scope host before the request leaves.
- **Tools** — `CAI`, `Metasploit`, `Firecracker`
- **Models** — `Kimi K2`, `GLM-4.6`

**Run it** — Drive a planner/executor pair against a target you own, and watch scope refuse an out-of-scope host in the harness and again in the sandbox.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C1.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/c1-redteam
./airgap.sh up   # isolated docker network, no default route
./scope-test.sh --in-scope http://target.local --out-of-scope https://example.com
```

*Expect:* Severity sorting puts 2 of 3 exploitable findings in the top 3; model triage puts 3 of 3, and correctly reasons that the partner CDN is out of scope. With the model adversarially convinced that the out-of-scope host is critical, the unenforced harness acts on it and the enforced harness refuses. Underneath the harness the sandbox refuses three requests for three different reasons — rate limit, engagement boundary, and cloud metadata — without consulting the model at all.

---

### C1.2 — Red-teaming an agent: designing the campaign

`Security of AI`

- **Risk** — A red-team result nobody can act on, because "it worked once" is not a rate.
- **Control** — Systematic campaigns across all three surfaces, with measured success rates and a criterion agreed before the first payload.
- **Lab** — Run a campaign across the three surfaces and report a rate with its sample size, not an anecdote.
- **Tools** — `garak`, `promptfoo`, `SPIRE`, `Falco`
- **Models** — `Llama 3.3`

**Run it** — Run one campaign across the injection, identity and containment surfaces and report a rate with its sample size for each.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C1.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/c1-redteam
python3 campaign.py --surfaces injection,identity,containment --n 200
python3 campaign.py --report --include-benign-controls
```

*Expect:* No defence gives ASR 1.00. The keyword filter gives ASR 0.67 with false alarms on 2 of 4 benign security-writing cases. Provenance gives ASR 0.00 with no false alarms — until the payload is delivered through the principal channel, where ASR returns to 1.00. The same two numbers then score all three surfaces in one table.

---

### C1.3 — Attacking evaluation itself

`Security of AI`

- **Risk** — If the eval can be fooled, the assurance is theatre.
- **Control** — Eval gaming, sandbagging, contamination and judge manipulation as test cases.
- **Lab** — Game the B2.11 harness deliberately, then close the hole you used.
- **Tools** — `Cyber Commons eval harness`
- **Models** — `Kimi K2`

**Run it** — Game the eval deliberately, then close the hole you used.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C1.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C1.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b2.10-eval-harness
python3 ../c1-redteam/game_eval.py --strategy sandbag
python3 ../c1-redteam/game_eval.py --strategy judge-manipulation
./scripts/vulnbench.sh compare   # see the inflated number
```

*Expect:* You reproduce an inflated score, then patch the harness so the same trick fails.

---

### C1.4 — Reporting agentic findings

`both directions`

- **Risk** — The vulnerability is emergent behaviour, not a line of code.
- **Control** — Reproducibility requirements for probabilistic systems.
- **Lab** — Write a finding a CISO can act on, with a replayable trace.
- **Tools** — `OpenTelemetry`

**Run it** — Write a finding for an emergent behaviour, not a line of code.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C1.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C1.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/c1-redteam
python3 report.py --from-trace engagement/trace.jsonl --template agentic-finding.md
python3 report.py --verify-reproducible --runs 10
```

*Expect:* A finding with a reproduction rate (e.g. 7/10), not a claim of determinism the system cannot offer.

---
