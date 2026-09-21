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

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.0

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-0-start-here
#         (Claude Code and Copilot: /d1-0-start-here · Cursor: type / and
#         search · Codex: $d1-0-start-here). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.0
```

---

### D1.1 — Platform ingestion and supply-chain risks

- **Lab** — Score a deployment's packages, hosted models and datasets for supply-chain risk, weighted by the authority the agent that loads them runs with.
- **Tools** — `Sigstore`, `OSV`

**Run it** — Score a deployment's packages, hosted models and datasets for supply-chain risk, weighted by the authority the agent that loads them runs with.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.1

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-1-platform-ingestion-and-supply-chain
#         (Claude Code and Copilot: /d1-1-platform-ingestion-and-supply-chain · Cursor: type / and
#         search · Codex: $d1-1-platform-ingestion-and-supply-chain). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.1
```

---

### D1.2 — Weaponizing the ingestion path

- **Lab** — Build a provenance manifest for the ingestion path, and find the record whose origin nothing can vouch for.
- **Tools** — `OpenTelemetry`

**Run it** — Build a provenance manifest for the ingestion path, and find the record whose origin nothing can vouch for.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.2

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-2-weaponizing-the-ingestion-path
#         (Claude Code and Copilot: /d1-2-weaponizing-the-ingestion-path · Cursor: type / and
#         search · Codex: $d1-2-weaponizing-the-ingestion-path). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.2
```

---

### D1.3 — Cognitive vulnerability and elicitation scaling

- **Lab** — Measure an elicitation technique's reproduction rate with its denominator, then attack the corpus it was scored against.
- **Tools** — `Inspect`

**Run it** — Measure an elicitation technique's reproduction rate with its denominator, then attack the corpus it was scored against.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.3

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-3-cognitive-vulnerability-and-elicitation
#         (Claude Code and Copilot: /d1-3-cognitive-vulnerability-and-elicitation · Cursor: type / and
#         search · Codex: $d1-3-cognitive-vulnerability-and-elicitation). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.3
```

---

### D1.4 — Establishing telemetry and detecting the actor

- **Lab** — Score actors on behavioural signals to separate agents from people, and pick the threshold by expected cost rather than accuracy.
- **Tools** — `OpenTelemetry`, `OpenSearch`

**Run it** — Score actors on behavioural signals to separate agents from people, and pick the threshold by expected cost rather than accuracy.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.4

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-4-establishing-telemetry-and-detecting-the
#         (Claude Code and Copilot: /d1-4-establishing-telemetry-and-detecting-the · Cursor: type / and
#         search · Codex: $d1-4-establishing-telemetry-and-detecting-the). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.4
```

---

### D1.5 — Emergent swarms and multi-agent proliferation

- **Lab** — Resolve each behaviour in a swarm incident to a named control, and list the ones with nothing behind them.
- **Tools** — `MITRE ATLAS`

**Run it** — Resolve each behaviour in a swarm incident to a named control, and list the ones with nothing behind them.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.5

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-5-emergent-swarms-and-multi-agent
#         (Claude Code and Copilot: /d1-5-emergent-swarms-and-multi-agent · Cursor: type / and
#         search · Codex: $d1-5-emergent-swarms-and-multi-agent). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.5
```

---

### D1.6 — High-concurrency detection engineering

- **Lab** — Score candidate detection rules on precision, recall and the queue volume each one would add.
- **Tools** — `Sigma`

**Run it** — Score candidate detection rules on precision, recall and the queue volume each one would add.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.6

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-6-high-concurrency-detection-engineering
#         (Claude Code and Copilot: /d1-6-high-concurrency-detection-engineering · Cursor: type / and
#         search · Codex: $d1-6-high-concurrency-detection-engineering). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.6
```

---

### D1.7 — Triaging the non-deterministic swarm

- **Lab** — Run a triage loop with a severity floor, and sample its auto-closures so the false-negative rate is measured rather than assumed.
- **Tools** — `TheHive`

**Run it** — Run a triage loop with a severity floor, and sample its auto-closures so the false-negative rate is measured rather than assumed.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.7

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-7-triaging-the-non-deterministic-swarm
#         (Claude Code and Copilot: /d1-7-triaging-the-non-deterministic-swarm · Cursor: type / and
#         search · Codex: $d1-7-triaging-the-non-deterministic-swarm). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.7
```

---

### D1.8 — Defensive deception and threshold failures

- **Lab** — Place canaries outside every legitimate path, and flag the one sited close enough to real work to fire on it.
- **Tools** — `Canarytokens`

**Run it** — Place canaries outside every legitimate path, and flag the one sited close enough to real work to fire on it.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.8

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-8-defensive-deception-and-threshold
#         (Claude Code and Copilot: /d1-8-defensive-deception-and-threshold · Cursor: type / and
#         search · Codex: $d1-8-defensive-deception-and-threshold). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.8
```

---

### D1.9 — Machine-speed containment and fleet revocation

- **Lab** — Fire a fleet-wide kill switch and measure what survives it: tokens, processes, and the runs that should have been preserved.
- **Tools** — `SPIFFE`

**Run it** — Fire a fleet-wide kill switch and measure what survives it: tokens, processes, and the runs that should have been preserved.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.9

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-9-machine-speed-containment-and-fleet
#         (Claude Code and Copilot: /d1-9-machine-speed-containment-and-fleet · Cursor: type / and
#         search · Codex: $d1-9-machine-speed-containment-and-fleet). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.9
```

---

### D1.10 — Forensic replay and control architecture

- **Lab** — Audit a run for the four fields a replay needs, and find the one whose absence turns a demonstration into a description.
- **Tools** — `Velociraptor`

**Run it** — Audit a run for the four fields a replay needs, and find the one whose absence turns a demonstration into a description.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.10

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-10-forensic-replay-and-control-architecture
#         (Claude Code and Copilot: /d1-10-forensic-replay-and-control-architecture · Cursor: type / and
#         search · Codex: $d1-10-forensic-replay-and-control-architecture). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.10
```

---

### D1.11 — Institutional governance and compliance

- **Lab** — Hand a finding over as three artefacts: a named control, an owner, and an eval case that fails on the unfixed build.
- **Tools** — `NIST AI RMF`

**Run it** — Hand a finding over as three artefacts: a named control, an owner, and an eval case that fails on the unfixed build.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons D1.11

# --- 3 · in your agent, open this folder and pick the skill:
#         d1-11-institutional-governance-and-compliance
#         (Claude Code and Copilot: /d1-11-institutional-governance-and-compliance · Cursor: type / and
#         search · Codex: $d1-11-institutional-governance-and-compliance). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py D1.11
```

---
