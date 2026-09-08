# Track C1 — One Red-Team Lifecycle, End to End

**Function C · Agentic Evaluation and Red Teaming**  
*Red-team CyberTravels as a non-deterministic actor: one lifecycle from the ingestion and elicitation surfaces an attacker reaches first, through emergent multi-agent behaviour, to the telemetry, containment and forensic governance every finding must end in.*

**Job titles:** Red Team Operator, AI Security Researcher, Offensive ML Engineer

**What changes:** A single lifecycle: from the ingestion and elicitation surfaces an attacker reaches first, through emergent multi-agent behaviour, into the telemetry, detection, triage, containment and forensic replay a researcher hands the defender, and out to institutional governance. 12 lessons.

**Autonomy focus:** You red-team at L3 the systems deployed at L2.5, and every finding leaves as a control the SOC can run.

**Deliverable:** One finding carried the whole distance — reproduced, turned into a detection, and handed over with an eval case that fails on the old build.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### C1.0 — Start here — the evolution of non-deterministic threat simulation

- **Risk** — Offensive work that produces anecdotes: a result that worked once, on one target, with no rate and no reproduction.
- **Control** — A campaign with a stated criterion, a harness that separates the model effect from the harness effect, and a handoff that ends in a control.
- **Lab** — Take one published agentic attack and list what you would need to reproduce it.

**Run it** — Take one published agentic attack and list what you would need to reproduce it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C1.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C1.0   # run it headless and check it
```

*Expect:* The three attack surfaces of an agent print with what each covers, and the same claim scores as anecdote, measurement, result or evidence depending on whether it carries a rate, a control comparison and an independent reproduction.

---

### C1.1 — Platform ingestion and supply-chain risks

- **Lab** — Dependency-squatting and malicious uploads to model hubs, and the ingress filters that should catch them.
- **Tools** — `Sigstore`, `OSV`

---

### C1.2 — Weaponizing the ingestion path

- **Lab** — Data-layer payloads that exploit parsers to reach code execution during automated embedding generation.
- **Tools** — `OpenTelemetry`

**Run it** — Data-layer payloads that exploit parsers to reach code execution during automated embedding generation.

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

### C1.3 — Cognitive vulnerability and elicitation scaling

- **Lab** — Cross-prompt attention degradation and jailbreaks that strip safety while retaining tool use, scored on reproduction.
- **Tools** — `Inspect`

**Run it** — Cross-prompt attention degradation and jailbreaks that strip safety while retaining tool use, scored on reproduction.

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

### C1.4 — Establishing telemetry and detecting the actor

- **Lab** — JSON-wrapped model-gateway trace logging, and scoring actors to tell agent tool calls from human behaviour.
- **Tools** — `OpenTelemetry`, `OpenSearch`

**Run it** — JSON-wrapped model-gateway trace logging, and scoring actors to tell agent tool calls from human behaviour.

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

### C1.5 — Emergent swarms and multi-agent proliferation

- **Lab** — Case studies where agents bridge sandboxes via shared mounts or spawn child nodes without attribution.
- **Tools** — `MITRE ATLAS`

---

### C1.6 — High-concurrency detection engineering

- **Lab** — Semantic drift and runtime-objective anomalies, and choosing rules by the queue volume they add.
- **Tools** — `Sigma`

---

### C1.7 — Triaging the non-deterministic swarm

- **Lab** — Multi-threaded delegation graphs and triage loops defended against deceptive self-correction.
- **Tools** — `TheHive`

---

### C1.8 — Defensive deception and threshold failures

- **Lab** — Canary files and weaponised tokens inside data indexes, catching harvesters with no threshold.
- **Tools** — `Canarytokens`

---

### C1.9 — Machine-speed containment and fleet revocation

- **Lab** — Zero-trust runtime gatekeepers and dynamic token revocation that isolate a fleet at machine speed.
- **Tools** — `SPIFFE`

---

### C1.10 — Forensic replay and control architecture

- **Lab** — Deterministic runtime constraints that reproduce, replay and document an agentic exploit path.
- **Tools** — `Velociraptor`

---

### C1.11 — Institutional governance and compliance

- **Lab** — Findings translated into engineering policies, change-surface patches and reporting timelines.
- **Tools** — `NIST AI RMF`

---
