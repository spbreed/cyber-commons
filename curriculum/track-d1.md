# Track D1 — One Red-Team Lifecycle, End to End

**Function D · Agentic Evaluation and Red Teaming**  
*Red-team CyberTravels as a non-deterministic actor: one lifecycle from the ingestion and elicitation surfaces an attacker reaches first, through emergent multi-agent behaviour, to the telemetry, containment and forensic governance every finding must end in.*

**Job titles:** Red Team Operator, AI Security Researcher, Offensive ML Engineer

**What changes:** A single lifecycle: from the ingestion and elicitation surfaces an attacker reaches first, through emergent multi-agent behaviour, into the telemetry, detection, triage, containment and forensic replay a researcher hands the defender, and out to institutional governance. 12 lessons.

**Autonomy focus:** You red-team at L3 the systems deployed at L2.5, and every finding leaves as a control the SOC can run.

**Deliverable:** One finding carried the whole distance — reproduced, turned into a detection, and handed over with an eval case that fails on the old build.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### D1.0 — Start here — the evolution of non-deterministic threat simulation

- **Risk** — Offensive work that produces anecdotes: a result that worked once, on one target, with no rate and no reproduction.
- **Control** — A campaign with a stated criterion, a harness that separates the model effect from the harness effect, and a handoff that ends in a control.
- **Lab** — Take one published agentic attack and list what you would need to reproduce it.

**Run it** — Take one published agentic attack and list what you would need to reproduce it.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of D1.0:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D1.0 --out work/cybertravels
python3 scripts/checkpoint.py --at D1.0 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · a reading lesson: no skill to run. When you reach one
#         that does, this links them all into your agent. ---
python3 scripts/install_skills.py --all
```

*Expect:* The three attack surfaces of an agent print with what each covers, and the same claim scores as anecdote, measurement, result or evidence depending on whether it carries a rate, a control comparison and an independent reproduction.

---

### D1.1 — Platform ingestion and supply-chain risks

- **Lab** — Score a deployment's packages, hosted models and datasets for supply-chain risk, weighted by the authority the agent that loads them runs with.
- **Tools** — `Sigstore`, `OSV`

---

### D1.2 — Weaponizing the ingestion path

- **Lab** — Build a provenance manifest for the ingestion path, and find the record whose origin nothing can vouch for.
- **Tools** — `OpenTelemetry`

**Run it** — Build a provenance manifest for the ingestion path, and find the record whose origin nothing can vouch for.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of D1.2:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D1.2 --out work/cybertravels
python3 scripts/checkpoint.py --at D1.2 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/research/training-data-provenance-manifest/scripts/training_data_provenance_manifest.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* No defence gives ASR 1.00. The keyword filter gives ASR 0.67 with false alarms on 2 of 4 benign security-writing cases. Provenance gives ASR 0.00 with no false alarms — until the payload is delivered through the principal channel, where ASR returns to 1.00. The same two numbers then score all three surfaces in one table.

---

### D1.3 — Cognitive vulnerability and elicitation scaling

- **Lab** — Measure an elicitation technique's reproduction rate with its denominator, then attack the corpus it was scored against.
- **Tools** — `Inspect`

**Run it** — Measure an elicitation technique's reproduction rate with its denominator, then attack the corpus it was scored against.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of D1.3:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D1.3 --out work/cybertravels
python3 scripts/checkpoint.py --at D1.3 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/research/technique-reproducibility-test/scripts/technique_reproducibility_test.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* You reproduce an inflated score, then patch the harness so the same trick fails.

---

### D1.4 — Establishing telemetry and detecting the actor

- **Lab** — Score actors on behavioural signals to separate agents from people, and pick the threshold by expected cost rather than accuracy.
- **Tools** — `OpenTelemetry`, `OpenSearch`

**Run it** — Score actors on behavioural signals to separate agents from people, and pick the threshold by expected cost rather than accuracy.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of D1.4:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D1.4 --out work/cybertravels
python3 scripts/checkpoint.py --at D1.4 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/agent-versus-human-scoring/scripts/agent_versus_human_scoring.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* A finding with a reproduction rate (e.g. 7/10), not a claim of determinism the system cannot offer.

---

### D1.5 — Emergent swarms and multi-agent proliferation

- **Lab** — Resolve each behaviour in a swarm incident to a named control, and list the ones with nothing behind them.
- **Tools** — `MITRE ATLAS`

---

### D1.6 — High-concurrency detection engineering

- **Lab** — Score candidate detection rules on precision, recall and the queue volume each one would add.
- **Tools** — `Sigma`

---

### D1.7 — Triaging the non-deterministic swarm

- **Lab** — Run a triage loop with a severity floor, and sample its auto-closures so the false-negative rate is measured rather than assumed.
- **Tools** — `TheHive`

---

### D1.8 — Defensive deception and threshold failures

- **Lab** — Place canaries outside every legitimate path, and flag the one sited close enough to real work to fire on it.
- **Tools** — `Canarytokens`

---

### D1.9 — Machine-speed containment and fleet revocation

- **Lab** — Fire a fleet-wide kill switch and measure what survives it: tokens, processes, and the runs that should have been preserved.
- **Tools** — `SPIFFE`

---

### D1.10 — Forensic replay and control architecture

- **Lab** — Audit a run for the four fields a replay needs, and find the one whose absence turns a demonstration into a description.
- **Tools** — `Velociraptor`

---

### D1.11 — Institutional governance and compliance

- **Lab** — Hand a finding over as three artefacts: a named control, an owner, and an eval case that fails on the unfixed build.
- **Tools** — `NIST AI RMF`

---
