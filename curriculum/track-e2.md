# Track E2 — Detect — the Lake, and Rules Mapped to MITRE

**Function E · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** Detection Engineer, SOC Engineer, Security Data Engineer

**What changes:** The lake the rules are written against, then detections for two different subjects — the agent and the platform running it — mapped to ATT&CK and ATLAS, plus the loop that writes rules, the corpus that decides whether they ship, and the one detector that needs no threshold. 6 lessons.

**Autonomy focus:** Rules are written at L3 and shipped by a human, because the cost that decides deployment is analyst trust and the telemetry does not contain it.

**Deliverable:** A detection pack for agent behaviour, every rule carrying a MITRE technique and a measured false-positive rate.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### E2.1 — The detection data lake — where agent telemetry lands

- **Risk** — Everything is indexed hot because nobody priced it, so retention is cut across the board and the traces go first.
- **Control** — A tiering decision per source, driven by the queries the SOC actually runs, with the cost of each tier stated.
- **Lab** — Tier six sources against the queries that need them and compare the bill with index-everything.
- **Tools** — `OpenSearch`, `OpenTelemetry`

**Run it** — Tier six sources against the queries that need them and compare the bill with index-everything.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E2.1

# --- 3 · in your agent, open this folder and pick the skill:
#         e2-1-the-detection-data-lake
#         (Claude Code and Copilot: /e2-1-the-detection-data-lake · Cursor: type / and
#         search · Codex: $e2-1-the-detection-data-lake). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E2.1
```

---

### E2.2 — Detections whose subject is the agent — mapped to ATT&CK and ATLAS

- **Risk** — Scope drift, unusual tool sequencing, off-hours autonomous action.
- **Control** — Detections whose subject is a non-human principal.
- **Lab** — Write five detections for agent misbehaviour and fire each one.
- **Tools** — `Falco`, `Sigma`

**Run it** — Write five detections for agent misbehaviour and fire each one.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E2.2

# --- 3 · in your agent, open this folder and pick the skill:
#         e2-2-detections-whose-subject-is-the-agent
#         (Claude Code and Copilot: /e2-2-detections-whose-subject-is-the-agent · Cursor: type / and
#         search · Codex: $e2-2-detections-whose-subject-is-the-agent). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E2.2
```

---

### E2.3 — Detections whose subject is the agent platform

- **Risk** — Platform-layer compromise is invisible to workload-layer detection. The escape, the poisoned cache entry and the silently expired exemption all look like normal operation from inside.
- **Control** — Named escape primitives rather than anomaly scoring (C1.4), cache integrity diffing against a manifest (C5.4), upload scanning (C3.4), secret scanning wired to automated revocation (C4.1), and exemption-state reconciliation (C6.3).
- **Lab** — Run four platform detectors over one day of events and see which of them a generic anomaly score would have missed.
- **Tools** — `Falco`, `Gitleaks`, `Sigstore`

**Run it** — Run four platform detectors over one day of events and see which of them a generic anomaly score would have missed.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E2.3

# --- 3 · in your agent, open this folder and pick the skill:
#         e2-3-detections-whose-subject-is-the-agent
#         (Claude Code and Copilot: /e2-3-detections-whose-subject-is-the-agent · Cursor: type / and
#         search · Codex: $e2-3-detections-whose-subject-is-the-agent). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E2.3
```

---

### E2.4 — Agent-assisted detection engineering — written by a loop, shipped by a human

- **Risk** — Coverage gaps nobody mapped.
- **Control** — Detection-as-code with agents inside the CI loop.
- **Lab** — Generate and unit-test Sigma rules in CI; map coverage to ATT&CK.
- **Tools** — `Sigma`, `Wazuh`
- **Open-weight models** — `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Generate and unit-test Sigma rules in CI; map coverage to ATT&CK.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E2.4

# --- 3 · in your agent, open this folder and pick the skill:
#         e2-4-agent-assisted-detection-engineering
#         (Claude Code and Copilot: /e2-4-agent-assisted-detection-engineering · Cursor: type / and
#         search · Codex: $e2-4-agent-assisted-detection-engineering). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E2.4
```

---

### E2.5 — Rules generated from an incident — and the benign corpus that decides them

- **Risk** — A rule generated from one incident matches that incident and nothing else, or matches everything and buries the queue.
- **Control** — Generate, then measure against a benign corpus. A rule with no measured false-positive rate is not a rule, it is a guess.
- **Lab** — Generate a rule from a trace, then score it against benign traffic and report the false-positive rate before deployment.
- **Tools** — `Sigma`

**Run it** — Generate a rule from a trace, then score it against benign traffic and report the false-positive rate before deployment.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E2.5

# --- 3 · in your agent, open this folder and pick the skill:
#         e2-5-rules-generated-from-an-incident
#         (Claude Code and Copilot: /e2-5-rules-generated-from-an-incident · Cursor: type / and
#         search · Codex: $e2-5-rules-generated-from-an-incident). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E2.5
```

---

### E2.6 — Honeypots, canaries and deception — the detector with no threshold

- **Risk** — Every other detector needs a threshold, and every threshold is a trade. Deception needs neither — but only if the bait is placed where the agent actually looks, and rotated before it is learned.
- **Control** — Canary tokens in config, environment and artifact metadata (C4.4), and honeypot tasks salted into the benchmark whose cheat path is logged rather than rewarded (C10.3).
- **Lab** — Authenticate with a canary and watch a zero-threshold alert fire; then salt a benchmark and read the cheat-attempt rate as a leading indicator.
- **Tools** — `Canarytokens`, `Inspect`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Authenticate with a canary and watch a zero-threshold alert fire; then salt a benchmark and read the cheat-attempt rate as a leading indicator.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E2.6

# --- 3 · in your agent, open this folder and pick the skill:
#         e2-6-honeypots
#         (Claude Code and Copilot: /e2-6-honeypots · Cursor: type / and
#         search · Codex: $e2-6-honeypots). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E2.6
```

---
