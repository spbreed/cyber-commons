# Track B1 — The AppSec Engineer / Code Reviewer

**Function B · Product & Application Security**  
*Closest to the developers, and therefore first to meet agents at scale — usually before anyone approved it.*

**Job titles:** AppSec Engineer, Product Security Engineer, Secure Code Reviewer

**What changes:** Your review becomes a 15-stage pipeline rather than a queue: ingest, model the threat, analyse, validate dynamically, report. Judgment becomes the bottleneck, which is a better problem.

**Autonomy focus:** Triage reaches L2.5 early; merge authority stays L2 far longer than people expect.

**Deliverable:** A five-phase AppSec pipeline running as a CI gate, with confirmed-by-exploitation severity and published precision and escape metrics.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### B1.1 — Historical parsing and structural indexing

`AI for Security`

- **Risk** — Review starts at the diff, so the pipeline never learns which parts of the repo keep breaking.
- **Control** — Stages 1–2: mine commit and advisory history for repeat risk zones, then index the codebase into semantic units.
- **Lab** — Parse a repo's vulnerability history into risk zones, then build a function/class index and rank files by prior-defect density.
- **Tools** — `git`, `OpenGrep`, `tree-sitter`
- **Models** — `GLM-4.6`

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

### B1.2 — Component summarisation and architecture synthesis

`AI for Security`

- **Risk** — The model is handed files and asked about a system, so it invents the parts it cannot see.
- **Control** — Stages 3–4: summarise each module, then compile a global map of data flows, entry points and trust boundaries.
- **Lab** — Generate per-directory summaries and synthesise them into an architecture map with entry points and trust boundaries.
- **Tools** — `tree-sitter`, `Graphviz`
- **Models** — `GLM-4.6`, `Kimi K2`

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

### B1.3 — Threat modelling from the architecture map

`Security of AI`

- **Risk** — Threat models are written once, by hand, against a system that has since changed.
- **Control** — Stage 5: derive assets, entry points and attack vectors mechanically from the synthesised map.
- **Lab** — Turn an architecture map into a ranked threat model, then diff it after one entry point is added.
- **Tools** — `OWASP Threat Dragon`
- **Models** — `GLM-4.6`

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

### B1.4 — Strategic planning and agent allocation

`AI for Security`

- **Risk** — Every scanner is pointed at every file, so cost scales with the repo instead of with the risk.
- **Control** — Stage 6: allocate specialised agents and tools to specific trust boundaries, budgeted by threat rank.
- **Lab** — Allocate a fixed analysis budget across boundaries and compare coverage against a uniform sweep.
- **Tools** — `Semgrep OSS`, `CodeQL`
- **Models** — `GLM-4.6`, `Llama 3.3`

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

### B1.5 — Vulnerability auditing: three generations of SAST

`AI for Security`  ·  **flagship lab**

- **Risk** — Pattern matching floods the queue; the false-positive rate is what actually changed.
- **Control** — Stage 7: deterministic rules for what rules do well, model reasoning for what rules cannot express.
- **Lab** — Score grep, taint rules and model review against the same corpus, then combine them behind a confidence gate.
- **Tools** — `OpenGrep`, `Semgrep OSS`, `CodeQL`
- **Models** — `GLM-4.6`, `Kimi K2`

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

### B1.6 — Deduplication and contextual verification

`AI for Security`

- **Risk** — Parallel analysis tracks report the same bug three times, and some of those bugs do not exist.
- **Control** — Stages 8–9: consolidate overlapping findings, then cross-reference each one against syntax and imports to weed out hallucinations.
- **Lab** — Deduplicate findings across three analysis tracks, then verify each against the AST and drop the ones that reference code that is not there.
- **Tools** — `OpenGrep`, `tree-sitter`
- **Models** — `GLM-4.6`

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

### B1.7 — Feasibility filtering and reachability

`AI for Security`

- **Risk** — A finding in dead code costs the same to triage as one on the login path.
- **Control** — Stage 10: decide whether an external caller can actually reach the sink before anyone is paged.
- **Lab** — Build a call graph from entry points and partition findings into reachable, unreachable and unknown.
- **Tools** — `CodeQL`, `tree-sitter`
- **Models** — `GLM-4.6`

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

### B1.8 — Sandbox replication

`Security of AI`

- **Risk** — Dynamic testing is run against staging, so a destructive probe becomes an incident.
- **Control** — Stage 11: replicate the application in an isolated, disposable runtime with no path to production.
- **Lab** — Stand up an isolated replica, prove egress and credential isolation, and show what a destructive probe touches.
- **Tools** — `Docker`, `gVisor`, `Cilium`
- **Models** — `GLM-4.6`

**Run it** — Stand up an isolated replica, prove egress and credential isolation, and show what a destructive probe touches.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.8   # run it headless and check it
```

*Expect:* The replica permits only its own internal hosts and blocks GitHub, the metadata service and private addresses. Staging holds real credentials and a real-shaped customer record while the replica holds synthetic ones. The four isolation checks pass for the replica and fail for staging on credentials, data and lifetime, and destroying the replica clears its state.

---

### B1.9 — Dynamic exploitation (DAST)

`AI for Security`

- **Risk** — A SAST finding is a hypothesis, and hypotheses get argued about instead of fixed.
- **Control** — Stage 12: generate and run an actual exploit against the sandbox, so the finding is confirmed or dropped.
- **Lab** — Turn static findings into executable probes against the replica and separate confirmed from unconfirmed.
- **Tools** — `OWASP ZAP`, `Nuclei`
- **Models** — `GLM-4.6`, `Kimi K2`

**Run it** — Turn static findings into executable probes against the replica and separate confirmed from unconfirmed.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.9   # run it headless and check it
```

*Expect:* The SQL injection probe returns rows for three owners when one was requested, and the traversal probe returns the synthetic token from outside the document root; the control probe returns a single owner and is not flagged. The weak assertion confirms all three including the control. Stage 12 marks two findings CONFIRMED and one UNVALIDATED for having no probe.

---

### B1.10 — Exploit chaining

`AI for Security`

- **Risk** — Three medium findings are triaged as three mediums, and nobody notices they compose.
- **Control** — Stage 13: combine validated findings into multi-step sequences and score the chain, not the links.
- **Lab** — Chain individually-medium findings into a critical path and show the severity the chain earns.
- **Tools** — `OWASP ZAP`
- **Models** — `Kimi K2`

**Run it** — Chain individually-medium findings into a critical path and show the severity the chain earns.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.10   # run it headless and check it
```

*Expect:* Six confirmed findings compose into multiple chains. The highest individual severity is high while the highest chained severity is critical, and at least one critical chain is built entirely from medium-or-lower links — for example SSRF granting internal network access, then the unauthenticated admin endpoint. Remediation ordering puts a medium finding first because it breaks the most chains.

---

### B1.11 — Remediation engineering

`AI for Security`

- **Risk** — A patch that silences the scanner is indistinguishable from a patch that fixes the bug.
- **Control** — Stage 14: generate the fix, re-run the exploit against the patched build, and require a regression test.
- **Lab** — Validate four candidate patches on three axes and show which of them only made the scanner green.
- **Tools** — `Semgrep OSS`, `pytest`
- **Models** — `GLM-4.6`, `Kimi K2`

**Run it** — Validate four candidate patches on three axes and show which of them only made the scanner green.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.11.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.11   # run it headless and check it
```

*Expect:* The vulnerable build passes all four behaviour cases and the exploit returns 3 rows. Candidates A, B and D make the scanner green. Validation rejects B for changed behaviour and C for remaining exploitable, accepting A and D. Proof of fix holds for both accepted patches — the exploit works on the old build and fails on the new.

---

### B1.12 — Severity calibration and reporting

`AI for Security`

- **Risk** — Severity is a label copied from the rule, so the queue is ordered by something that predicts nothing.
- **Control** — Stage 15: calibrate severity from sandbox evidence, then report per-stage economics rather than a finding count.
- **Lab** — Recalculate severity from confirmed exploitation and reachability, then produce the per-stage escape economics.
- **Tools** — `OpenGrep`
- **Models** — `GLM-4.6`

**Run it** — Recalculate severity from confirmed exploitation and reachability, then produce the per-stage escape economics.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.12.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.12   # run it headless and check it
```

*Expect:* Calibration moves several findings off their rule severity: the confirmed reachable CWE-89 that chains into account takeover becomes critical, while the unreachable and unvalidated ones fall. The top-3 by rule severity and by calibration disagree. The stage table shows review with the worst precision and highest minutes per finding, and design carrying the highest escape cost despite only two findings.

---

### B1.13 — Context engineering for the pipeline

`AI for Security`

- **Risk** — The model is given the repository and asked to be thorough, so the relevant line falls out of the window.
- **Control** — Slice on the source-sink path, not on distance: the smallest context that still supports a severity decision.
- **Lab** — Compare four context strategies against one bug and measure which are decidable and at what size.
- **Tools** — `tree-sitter`
- **Models** — `GLM-4.6`, `Llama 3.3`

**Run it** — Compare four context strategies against one bug and measure which are decidable and at what size.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.13.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.13   # run it headless and check it
```

*Expect:* The whole file is roughly 840 characters, the ±2 window about 200 and the path slice about 390. The ±2 window is not decidable because it lacks the signature; the ±6 window and the whole file are decidable but carry unrelated functions. The path slice is the smallest decidable context with zero unrelated functions, about 53% smaller than the whole file.

---

### B1.14 — Injection in your own pipeline

`Security of AI`

- **Risk** — The pipeline reads attacker-controlled code and then takes actions — a confused deputy you built yourself.
- **Control** — Instruction/data provenance: content the pipeline read may never drive a state-changing tool.
- **Lab** — Fire four realistic payloads at the review harness and compare keyword filtering against provenance.
- **Tools** — `OpenGrep`
- **Models** — `GLM-4.6`

**Run it** — Fire four realistic payloads at the review harness and compare keyword filtering against provenance.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.14.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.14   # run it headless and check it
```

*Expect:* The normal run executes all four tools. None of the five carriers contains blocklist vocabulary and all five reach `approve_pr` on the trusting pipeline. With provenance enforced all five are blocked while the principal's own calls still succeed. Deriving privilege from effects shows `post_comment` is privileged because CI listens to comments, and a content-driven comment is then blocked.

---

### B1.15 — Securing the developers' coding agents

`Security of AI`

- **Risk** — The IDE agent holds git credentials, cloud credentials and a shell, in an unmanaged environment.
- **Control** — The strongest containment a developer does not notice: credential deny-lists and workspace confinement first.
- **Lab** — Measure the default agent's blast radius and reachable credentials, then rank controls by friction.
- **Tools** — `Docker`, `Cilium`
- **Models** — `GLM-4.6`

**Run it** — Measure the default agent's blast radius and reachable credentials, then rank controls by friction.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.15.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.15   # run it headless and check it
```

*Expect:* The default developer agent scores a blast radius of 43 and can reach all seven paths including AWS, SSH and gcloud credentials. Containment reduces reachable paths to one source file with zero credentials reachable, and gating `git_push` drops the blast radius to 37 for 0.4 friction. The three lowest-friction controls remove every credential path without touching the inner loop.

---

### B1.16 — Bonus — Google Mantis, the pipeline in production

`AI for Security`  ·  **flagship lab**

- **Risk** — A reference implementation is adopted as a product, and its outputs are trusted without an eval.
- **Control** — Map Mantis's stages onto the pipeline you built, then score it with your own held-out key before trusting it.
- **Lab** — Map Mantis onto the 15 stages, parse its two output shapes, and score a sample against a held-out key.
- **Tools** — `Google Mantis`, `OpenGrep`
- **Models** — `GLM-4.6`, `Kimi K2`

**Run it** — Map Mantis onto the 15 stages, parse its two output shapes, and score a sample against a held-out key.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.16.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.16   # run it headless and check it
```

*Expect:* The stage map shows Mantis covering stage 7 strongly with a stage-1 learning loop, and not covering Phase 4 at all. Three of five sample outputs conform — one learning entry is missing the required `history` field, one finding has a null CWE, and one is prose. Scored against the held-out key, expert accuracy is below 1.0: one correct, one half credit for the null class, and one missed finding Mantis never reported. The learning entry then feeds the next run's risk zones.

---

**Adjacency requirement:** also complete A2.1–A2.2 — the failures happen in the seams.
