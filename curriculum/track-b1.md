# Track B1 — The AppSec Engineer / Code Reviewer

**Function B · Product & Application Security**  
*Closest to the developers, and therefore first to meet agents at scale — usually before anyone approved it.*

**Job titles:** AppSec Engineer, Product Security Engineer, Secure Code Reviewer

**What changes:** Your review moves left of the PR and your throughput stops being the bottleneck. Judgment becomes the bottleneck, which is a better problem.

**Autonomy focus:** Triage reaches L2.5 early; merge authority stays L2 far longer than people expect.

**Deliverable:** An agentic review workflow running as a CI gate with published precision and escape metrics.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### B1.1 — Agentic SAST

`AI for Security`

- **Risk** — Pattern matching floods the queue; the false-positive rate is what actually changed.
- **Control** — Reachability, exploitability and cross-file reasoning on top of deterministic rules.
- **Lab** — Run OpenGrep for candidates, then have a local model reason about reachability — measure FP drop.
- **Tools** — `OpenGrep`, `Semgrep OSS`, `CodeQL`
- **Models** — `GLM-4.6`, `Kimi K2`

**Run it** — Cut the false-positive rate with reachability reasoning, and measure it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install semgrep
cd labs/b1-appsec
opengrep --config auto --json target/ > candidates.json
python3 triage.py --candidates candidates.json --model $MODEL
python3 score.py --against ground-truth.json
```

*Expect:* Prints precision before/after triage. The FP rate — not the detection rate — is the number that moved.

---

### B1.2 — Context engineering for code review

`AI for Security`

- **Risk** — Context stuffing blows the budget and buries the sink.
- **Control** — Repo maps, prompt caching, tool-mediated retrieval over stuffing.
- **Lab** — Build the canonical triage bundle and compare accuracy vs a stuffed context.
- **Tools** — `ripgrep`, `tree-sitter`
- **Models** — `GLM-4.6`

**Run it** — Beat context stuffing with tool-mediated retrieval.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b1-appsec
python3 triage.py --strategy stuff  --finding F-102 --model $MODEL
python3 triage.py --strategy bundle --finding F-102 --model $MODEL   # canonical triage bundle
python3 compare_strategies.py
```

*Expect:* The bundle wins on accuracy and costs fewer tokens. Both numbers printed.

---

### B1.3 — Patch generation and local validation

`AI for Security`

- **Risk** — Unverified agent patches destroy trust faster than missed findings.
- **Control** — Build and test the fix locally *before* raising the PR.
- **Lab** — Generate → compile → test → only then open the PR; measure acceptance rate.
- **Tools** — `Semgrep Autofix`, `pytest`
- **Models** — `Kimi K2`

**Run it** — Never raise a PR for a patch you did not build and test.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b1-appsec
python3 patch.py --finding F-102 --model $MODEL --validate-locally
# generates -> compiles -> runs tests -> only then writes patch.diff
```

*Expect:* Patches failing the local build are discarded before a human ever sees them; acceptance rate is printed.

---

### B1.4 — What frontier SAST makes redundant, and what it doesn't

`AI for Security`

- **Risk** — Over-claiming replacement of pentest and business-logic testing.
- **Control** — Honest scoping of where static reasoning substitutes and where it cannot.
- **Lab** — Run the same target through SAST agent and DAST; chart what only one of them found.
- **Tools** — `OWASP ZAP`, `OpenGrep`
- **Models** — `Llama 3.3`

**Run it** — Chart honestly what only SAST found, and what only DAST found.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b1-appsec
docker compose up -d juice-shop
python3 triage.py --all > sast.json
zap-cli quick-scan http://localhost:3000 -o dast.json
python3 venn.py --sast sast.json --dast dast.json
```

*Expect:* Three buckets: SAST-only, DAST-only, both. The DAST-only bucket is why pentest is not redundant.

---

### B1.5 — Injection in your own harness

`Security of AI`

- **Risk** — Your harness ingests untrusted PR code, dependencies and scanner output.
- **Control** — Untrusted-content tagging, output allowlisting, never shell or write to the target app.
- **Lab** — Plant an injection in a PR diff and watch your reviewer obey it — then close it.
- **Tools** — `garak`, `Llama Guard 4`
- **Models** — `Llama Guard 4`

**Run it** — Watch your own review harness obey an injected instruction, then close it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b1-appsec
git apply injected-pr.diff       # a PR containing an instruction to the reviewer
python3 triage.py --candidates candidates.json --model $MODEL   # obeys it
python3 triage.py --candidates candidates.json --model $MODEL --tag-untrusted   # ignores it
```

*Expect:* The unprotected run emits the attacker's verdict; the tagged run does not.

---

### B1.6 — Securing the developers' agents

`Security of AI`

- **Risk** — Secrets in prompts and transcripts; CI credentials reachable from an agent session.
- **Control** — Scan the agent footprint the way you scan the repo.
- **Lab** — Grep an agent transcript and memory files for live secrets; add a pre-commit gate.
- **Tools** — `gitleaks`, `TruffleHog`

**Run it** — Find live secrets in your own agent's footprint.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install detect-secrets && cd labs/b1-appsec
gitleaks detect --source ~/.claude --no-git --report-path agent-secrets.json || true
python3 scan_transcripts.py --dir ~/.claude/projects --report
cp hooks/pre-commit .git/hooks/ && chmod +x .git/hooks/pre-commit
```

*Expect:* Secrets in prompts/transcripts/memory files surface, and the pre-commit hook stops the next one.

---

### B1.7 — Metrics per SDLC stage

`AI for Security`

- **Risk** — A workflow is promoted without numbers to justify it.
- **Control** — Precision, time-to-triage, patch acceptance rate, escape rate.
- **Lab** — Publish the four numbers for your own review agent.
- **Tools** — `Cyber Commons eval harness`

**Run it** — Publish the four numbers that let a review workflow earn its next rung.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b1-appsec
python3 metrics.py --precision --time-to-triage --patch-acceptance --escape-rate \
  --runs runs/ --out metrics.json && cat metrics.json
```

*Expect:* Four numbers with denominators. Without these, promotion to L2.5 is a vibe.

---

**Adjacency requirement:** also complete A2.1–A2.2 — the failures happen in the seams.
