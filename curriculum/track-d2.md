# Track D2 — The Agentic SOC — Detect

**Function D · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** 

**What changes:** 

**Autonomy focus:** 

**Deliverable:** 

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### D2.1 — Agent-assisted detection engineering

- **Risk** — Coverage gaps nobody mapped.
- **Control** — Detection-as-code with agents inside the CI loop.
- **Lab** — Generate and unit-test Sigma rules in CI; map coverage to ATT&CK.
- **Tools** — `Sigma`, `Wazuh`
- **Open-weight models** — `Kimi K2`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Generate and unit-test Sigma rules in CI; map coverage to ATT&CK.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install sigma-cli && cd labs/d1-soc/detections
python3 gen_rule.py --technique T1059 --model $MODEL --out rules/t1059.yml
sigma check rules/t1059.yml && python3 test_rule.py --rule rules/t1059.yml --positives pos/ --negatives neg/
python3 coverage.py --map-to attack
```

*Expect:* Rules that fail their negative corpus never merge. Coverage map shows the gap you actually have.

---

### D2.2 — Generating detection rules from an incident

- **Risk** — A rule generated from one incident matches that incident and nothing else, or matches everything and buries the queue.
- **Control** — Generate, then measure against a benign corpus. A rule with no measured false-positive rate is not a rule, it is a guess.
- **Lab** — Generate a rule from a trace, then score it against benign traffic and report the false-positive rate before deployment.
- **Tools** — `Sigma`

**Run it** — Generate a rule from a trace, then score it against benign traffic and report the false-positive rate before deployment.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.2   # run it headless and check it
```

*Expect:* Generate a rule from a trace, then score it against benign traffic and report the false-positive rate before deployment.

---

### D2.3 — Detection engineering *for* agents

- **Risk** — Scope drift, unusual tool sequencing, off-hours autonomous action.
- **Control** — Detections whose subject is a non-human principal.
- **Lab** — Write five detections for agent misbehaviour and fire each one.
- **Tools** — `Falco`, `Sigma`

**Run it** — Write five detections for agent misbehaviour and fire each one.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/d1-soc/detections
./install-sigma.sh   # scope drift, tool-sequence anomaly, off-hours autonomy, retrieval anomaly, NHI-at-human-time
./fire-each.sh       # deliberately trigger all five
```

*Expect:* All five fire on synthetic-but-real agent telemetry from the A3/B2 labs.

---

### D2.4 — Detections whose subject is the agent platform

- **Risk** — Platform-layer compromise is invisible to workload-layer detection. The escape, the poisoned cache entry and the silently expired exemption all look like normal operation from inside.
- **Control** — Named escape primitives rather than anomaly scoring (C1.4), cache integrity diffing against a manifest (C5.4), upload scanning (C3.4), secret scanning wired to automated revocation (C4.1), and exemption-state reconciliation (C6.3).
- **Lab** — Run four platform detectors over one day of events and see which of them a generic anomaly score would have missed.
- **Tools** — `Falco`, `Gitleaks`, `Sigstore`

**Run it** — Run four platform detectors over one day of events and see which of them a generic anomaly score would have missed.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
falco --rules agent-escape.yaml --validate
python3 cache_diff.py --manifest build-manifest.json --repo artifactory
gitleaks detect --redact --report-format sarif
```

*Expect:* Four named rules fire on a seven-event escape sequence that scores 0.07 on a generic volume anomaly. The orphaned-process rule isolates the one background process that outlived its tool call. The cache diff reports one modified, one unexpected and one missing artifact; automated revocation closes a credential in 2 minutes against 240 with a human in the loop; and exemption reconciliation raises a P1 for both an expired exemption and an unapproved one.

---

### D2.5 — Honeypots, canaries and deception in the agent's environment

- **Risk** — Every other detector needs a threshold, and every threshold is a trade. Deception needs neither — but only if the bait is placed where the agent actually looks, and rotated before it is learned.
- **Control** — Canary tokens in config, environment and artifact metadata (C4.4), and honeypot tasks salted into the benchmark whose cheat path is logged rather than rewarded (C10.3).
- **Lab** — Authenticate with a canary and watch a zero-threshold alert fire; then salt a benchmark and read the cheat-attempt rate as a leading indicator.
- **Tools** — `Canarytokens`, `Inspect`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Authenticate with a canary and watch a zero-threshold alert fire; then salt a benchmark and read the cheat-attempt rate as a leading indicator.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/D2.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session D2.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
python3 canary.py --place worker-env,docs,artifact-metadata
python3 honeypot.py --salt benchmark/ --ratio 0.15 --rotate-days 21
```

*Expect:* Two canary authentications out of four events are confirmed compromises with source IP and user agent attached, and no false positive is structurally possible. Both honeypot tasks log a cheat attempt and score zero for it. An unrotated canary's detection rate falls to 0% once learned — reporting a clean environment that is only well-mapped — while rotation holds it at 100%. Deception finds fewer things than the volume detectors and finds them at precision 1.00.

---
