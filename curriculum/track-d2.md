# Track D2 — Detect — the Lake, and Rules Mapped to MITRE

**Function D · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** Detection Engineer, SOC Engineer, Security Data Engineer

**What changes:** The lake the rules are written against, then detections for two different subjects — the agent and the platform running it — mapped to ATT&CK and ATLAS, plus the loop that writes rules, the corpus that decides whether they ship, and the one detector that needs no threshold. 6 lessons.

**Autonomy focus:** Rules are written at L3 and shipped by a human, because the cost that decides deployment is analyst trust and the telemetry does not contain it.

**Deliverable:** A detection pack for agent behaviour, every rule carrying a MITRE technique and a measured false-positive rate.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### D2.1 — The detection data lake — where agent telemetry lands

- **Risk** — Everything is indexed hot because nobody priced it, so retention is cut across the board and the traces go first.
- **Control** — A tiering decision per source, driven by the queries the SOC actually runs, with the cost of each tier stated.
- **Lab** — Tier six sources against the queries that need them and compare the bill with index-everything.
- **Tools** — `OpenSearch`, `OpenTelemetry`

---

### D2.2 — Detections whose subject is the agent — mapped to ATT&CK and ATLAS

- **Risk** — Scope drift, unusual tool sequencing, off-hours autonomous action.
- **Control** — Detections whose subject is a non-human principal.
- **Lab** — Write five detections for agent misbehaviour and fire each one.
- **Tools** — `Falco`, `Sigma`

**Run it** — Write five detections for agent misbehaviour and fire each one.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of D2.2:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D2.2 --out work/cybertravels
python3 scripts/checkpoint.py --at D2.2 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/agent-aware-rule-review/scripts/agent_aware_rule_review.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* All five fire on synthetic-but-real agent telemetry from the A3/B2 labs.

---

### D2.3 — Detections whose subject is the agent platform

- **Risk** — Platform-layer compromise is invisible to workload-layer detection. The escape, the poisoned cache entry and the silently expired exemption all look like normal operation from inside.
- **Control** — Named escape primitives rather than anomaly scoring (C1.4), cache integrity diffing against a manifest (C5.4), upload scanning (C3.4), secret scanning wired to automated revocation (C4.1), and exemption-state reconciliation (C6.3).
- **Lab** — Run four platform detectors over one day of events and see which of them a generic anomaly score would have missed.
- **Tools** — `Falco`, `Gitleaks`, `Sigstore`

**Run it** — Run four platform detectors over one day of events and see which of them a generic anomaly score would have missed.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of D2.3:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D2.3 --out work/cybertravels
python3 scripts/checkpoint.py --at D2.3 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/agent-platform-detections/scripts/agent_platform_detections.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Four named rules fire on a seven-event escape sequence that scores 0.07 on a generic volume anomaly. The orphaned-process rule isolates the one background process that outlived its tool call. The cache diff reports one modified, one unexpected and one missing artifact; automated revocation closes a credential in 2 minutes against 240 with a human in the loop; and exemption reconciliation raises a P1 for both an expired exemption and an unapproved one.

---

### D2.4 — Agent-assisted detection engineering — written by a loop, shipped by a human

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

# --- 2 · your copy of CyberTravels as it stood at the END of D2.4:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D2.4 --out work/cybertravels
python3 scripts/checkpoint.py --at D2.4 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/detection-rule-deployability/scripts/detection_rule_deployability.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Rules that fail their negative corpus never merge. Coverage map shows the gap you actually have.

---

### D2.5 — Rules generated from an incident — and the benign corpus that decides them

- **Risk** — A rule generated from one incident matches that incident and nothing else, or matches everything and buries the queue.
- **Control** — Generate, then measure against a benign corpus. A rule with no measured false-positive rate is not a rule, it is a guess.
- **Lab** — Generate a rule from a trace, then score it against benign traffic and report the false-positive rate before deployment.
- **Tools** — `Sigma`

**Run it** — Generate a rule from a trace, then score it against benign traffic and report the false-positive rate before deployment.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of D2.5:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D2.5 --out work/cybertravels
python3 scripts/checkpoint.py --at D2.5 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/detection-rule-synthesis/scripts/detection_rule_synthesis.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Generate a rule from a trace, then score it against benign traffic and report the false-positive rate before deployment.

---

### D2.6 — Honeypots, canaries and deception — the detector with no threshold

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

# --- 2 · your copy of CyberTravels as it stood at the END of D2.6:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at D2.6 --out work/cybertravels
python3 scripts/checkpoint.py --at D2.6 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/detection/canary-and-honeypot-design/scripts/canary_and_honeypot_design.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* Two canary authentications out of four events are confirmed compromises with source IP and user agent attached, and no false positive is structurally possible. Both honeypot tasks log a cheat attempt and score zero for it. An unrotated canary's detection rate falls to 0% once learned — reporting a clean environment that is only well-mapped — while rotation holds it at 100%. Deception finds fewer things than the volume detectors and finds them at precision 1.00.

---
