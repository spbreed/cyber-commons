# Track B2 — The Harness that Runs the SDLC

**Function B · Application Security with an AI SDLC**  
*The secure development lifecycle rebuilt around agents: they review the code, model the threats, confirm the exploits and file the fix — and the pipeline that does it is itself software you have to secure.*

**Job titles:** Security Automation Engineer, Detection & Response Engineer (platform side), Security Tooling Lead — and the role most orgs haven't created yet

**What changes:** Build the loop once, point it at a discipline, then prove it works. 14 lessons.

**Autonomy focus:** You are the person who builds the L2.5 boundary everyone else operates inside.

**Deliverable:** A reusable harness scaffold adopted by at least two other tracks.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### B2.0 — What an agentic harness actually is

`AI for Security`

- **Risk** — Capability gets attributed to the model when it comes from the scaffold. Two teams handed the identical model routinely differ by an order of magnitude on harness design alone.
- **Control** — Separate model, loop, tools, context, verifier, budgets and orchestrator — and treat the harness itself as an autonomous actor holding credentials, which must be governed like one.
- **Lab** — Build a minimal working harness from scratch, naming each component as it appears, then show what breaks when the verifier is removed.
- **Tools** — `LiteLLM`, `OpenTelemetry`
- **Models** — `Llama 3.3`, `GLM-4.6`

**Run it** — Build a minimal working harness from scratch, naming each component as it appears, then show what breaks when the verifier is removed.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.0   # run it headless and check it
```

*Expect:* The minimal harness runs and reports success while the tests still fail. Adding one component — a verifier that reads ground truth rather than the agent's own claim — flips `verified` to False on the same run and to True only when the fix genuinely works. A four-step budget stops a looping model. The harness then scores itself as a non-human identity holding repo:write and running unattended.

---

### B2.1 — Plan–act–verify

`AI for Security`

- **Risk** — Writing the code instead of writing the loop.
- **Control** — The minimum viable security harness: context, toolset, verifier, budget.
- **Lab** — Build the scaffold; swap the model underneath without touching the loop.
- **Tools** — `Python`, `LiteLLM`
- **Models** — `GLM-4.6`, `Llama 3.3`, `Kimi K2`

**Run it** — One scaffold, swappable model, unchanged loop.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
MODEL=llama3.3 python3 loop.py --task fix-tests
MODEL=glm-4.6  python3 loop.py --task fix-tests
MODEL=kimi-k2  python3 loop.py --task fix-tests
```

*Expect:* Identical loop code, three backbones, comparable traces — the prerequisite for C2.6 multi-backbone benchmarking.

---

### B2.2 — Verify signals that don't lie

`AI for Security`

- **Risk** — LLM-as-judge from the same family as the generator — the loop grades its own homework.
- **Control** — Deterministic oracles: compilers, tests, scanners. Judges only where no oracle exists.
- **Lab** — Score the same findings with a compiler oracle and with a same-family judge; show the gap.
- **Tools** — `pytest`, `Checkov`
- **Models** — `GLM-4.6`

**Run it** — Show a same-family judge grading its own homework.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b2.10-eval-harness
./scripts/vulnbench.sh score --findings data/mantis_findings.sample.jsonl \
  --gt-source secllmholmes-handcrafted   # deterministic oracle
# then compare with a judge drawn from the same family as the generator
```

*Expect:* The oracle and the same-family judge disagree in a specific, reproducible direction.

---

### B2.3 — Tool design

`Security of AI`

- **Risk** — The dangerous call exists and is merely blocked.
- **Control** — Read-only defaults, structured output contracts, allowlisted actions — design it out.
- **Lab** — Refactor a shell tool into three narrow, structured tools.
- **Tools** — `kmcp`

**Run it** — Refactor a shell tool into three narrow, structured tools.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 loop.py --tools shell   --task fix-tests   # can do anything
python3 loop.py --tools narrow  --task fix-tests   # read_file/list_dir/apply_patch only
python3 tool_audit.py --compare shell narrow
```

*Expect:* Same task completed; the arbitrary-execution capability is absent rather than blocked.

---

### B2.4 — Model tiering and routing inside the loop

`AI for Security`

- **Risk** — Paying frontier prices for executor-grade steps.
- **Control** — Cheap executor, escalated reasoner, advisor at decision points.
- **Lab** — Route Llama-executor → GLM-reasoner with LiteLLM and attribute spend per run.
- **Tools** — `LiteLLM`, `vLLM`
- **Models** — `Llama 3.3`, `GLM-4.6`, `Kimi K2`

**Run it** — Route cheap executor to escalated reasoner and attribute spend.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install 'litellm[proxy]' && cd labs/shared
litellm --config litellm.config.yaml &   # llama executor, glm reasoner, kimi advisor
cd ../m0-agent-loop && MODEL=router python3 loop.py --task fix-tests --json | jq '.tokens'
python3 ../shared/spend_report.py --by-run
```

*Expect:* Per-run, per-tier spend attribution. Escalation happens only at decision points.

---

### B2.5 — Sub-agents and delegation depth

`Security of AI`

- **Risk** — Authority inherited silently from parent to child agent.
- **Control** — Fan-out control, recursion budgets, explicit authority inheritance.
- **Lab** — Cap delegation depth and prove a grandchild agent cannot exceed its parent.
- **Tools** — `kagent`, `SPIRE`

**Run it** — Prove a grandchild agent cannot exceed its parent.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a2-delegation
python3 subagent.py --depth 3 --parent-scope repo:read
python3 subagent.py --depth 3 --parent-scope repo:read --attempt-escalate
```

*Expect:* Recursion budget caps depth; the escalation attempt is refused by the token, not by a check.

---

### B2.6 — Failure taxonomy

`AI for Security`

- **Risk** — Loop divergence, objective drift, reward hacking, silent truncation, tool thrash.
- **Control** — Recognise each from a trace.
- **Lab** — Read five real traces and name the failure in each.
- **Tools** — `OpenTelemetry`

**Run it** — Name the failure from the trace alone.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop/traces
python3 ../classify_failure.py --trace divergence.jsonl
for t in *.jsonl; do echo -n "$t: "; python3 ../classify_failure.py --trace $t --quiet; done
```

*Expect:* Loop divergence, objective drift, reward hacking, silent truncation, tool thrash — one per trace.

---

### B2.7 — Self-improving scaffolds

`Security of AI`

- **Risk** — A harness that rewrites its own config makes the fitness function the security control.
- **Control** — Sandbox the mutation, keep only measured gains, pin the fitness function.
- **Lab** — Let a scaffold mutate itself in a sandbox and keep only what the oracle confirms.
- **Tools** — `Python`, `Docker`
- **Models** — `Kimi K2`

**Run it** — Let a scaffold mutate itself, and keep only measured gains.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 evolve.py --generations 5 --sandbox docker --fitness pytest-pass-rate
python3 evolve.py --show-lineage   # what changed, what was kept, what was reverted
```

*Expect:* Only mutations the deterministic oracle confirms survive. Pin the fitness function — it is now the security control.

---

### B2.8 — Idempotency, replay and rollback

`AI for Security`

- **Risk** — Any agent action you cannot replay you cannot investigate.
- **Control** — Design requirements, not afterthoughts.
- **Lab** — Replay a full agent run from the trace and reproduce its decision.
- **Tools** — `OpenTelemetry`

**Run it** — Replay an agent run from its trace.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 loop.py --task fix-tests --json > run.json
python3 replay.py --trace run.json --assert-identical
```

*Expect:* Either it reproduces, or the tool names the field you failed to log. Anything you cannot replay you cannot investigate.

---

### B2.9 — Building a domain harness: one skeleton, four oracles

`AI for Security`

- **Risk** — Four teams build four harnesses, each re-deciding loop control, budgets and verification — and each getting the oracle wrong in its own way.
- **Control** — One skeleton with a pluggable oracle and a declared blast radius. The domain supplies the oracle, not a new loop.
- **Lab** — Run one skeleton across four domains and watch the oracle, not the loop, decide what the harness is worth.
- **Tools** — `OpenGrep`, `OWASP ZAP`, `OWASP Threat Dragon`, `CAI`
- **Models** — `GLM-4.6`, `Kimi K2`

**Run it** — Run one plan-act-verify skeleton across four domains, swapping only the oracle and the blast radius.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.9   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b2-harness
python3 domain_harness.py --domain sast   --oracle reachability+test
python3 domain_harness.py --domain pentest --require-signed-scope
```

*Expect:* One skeleton runs all four domains unchanged. With each domain's own oracle every confirmed finding is real — precision 1.00 across sast, threat model, dast and pentest — and the pentest run refuses outright without a signed scope, because its blast radius is live action. Swapping in the model's own confidence as the oracle confirms all 12 candidates, 8 of which are real: precision 0.67 in every domain, invisible from inside the harness.

---

### B2.10 — Choosing the model backbone

`AI for Security`

- **Risk** — A backbone chosen on a vendor chart, then wired in so deeply that substituting it means rewriting the harness.
- **Control** — Evaluate candidates on your own corpus, and above all design for backbone substitution — any list of best models is stale within a quarter.
- **Lab** — Score two backbones on the same corpus, then swap one for the other behind an unchanged harness interface.
- **Tools** — `LiteLLM`, `vLLM`, `Ollama`
- **Models** — `Kimi K2.7-Code`, `GLM-5.2`, `Llama 4`

**Run it** — Score two backbones on the same corpus, then swap one for the other behind an unchanged harness interface.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.10   # run it headless and check it
```

*Expect:* Three stand-in backbones are scored on the same corpus: the one with the best recall is not the one with the best cost per finding. A harness that couples to vendor output shapes fails outright on the third backbone, while the interface version substitutes in a single line and reports the recall, precision and cost deltas. A data-sovereignty column then removes the closed-weights option entirely.

---

### B2.11 — Evaluating a security harness

`AI for Security`

- **Risk** — A single successful run hides how unreliable an agent really is; a hallucinated finding looks exactly like a real one.
- **Control** — Ground truth + blind protocol + execution-verified scoring; report reliability (pass^k) not just capability (pass@k); never quote schema conformance as accuracy.
- **Lab** — The full Cyber Commons eval harness: build 552-row ground truth from SecLLMHolmes + TerraGoat/Checkov, run a blind model audit, score with expert-proxy + dual judges, and compare Llama / GLM / Kimi as the backing model.
- **Tools** — `Cyber Commons eval harness`, `Checkov`, `CyberGym`, `Inspect`
- **Models** — `Llama 3.3`, `GLM-4.6`, `Kimi K2`

**Run it** — The full eval harness: ground truth, blind protocol, execution-verified scoring, model comparison.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.11.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.11   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b2.10-eval-harness
./scripts/vulnbench.sh doctor && ./scripts/vulnbench.sh setup
./scripts/vulnbench.sh build      # 552-row ground truth: SecLLMHolmes + TerraGoat/Checkov
./scripts/vulnbench.sh verify     # regression fingerprint, expect Expert Accuracy 0.9479
./scripts/vulnbench.sh compare    # blind model comparison across backbones
./scripts/vulnbench.sh cybergym-preflight   # can this host run execution benchmarks?
```

*Expect:* Real numbers with committed evidence: per-model precision/recall/F1/Expert Accuracy, plus the failing-question list. This lab is fully built and tested — see its README for the recorded results.

---

### B2.12 — Reliability and cost under non-determinism

`AI for Security`

- **Risk** — A single lucky run published as a result, and cost per finding never computed at all, so nobody notices the tool moved work instead of removing it.
- **Control** — pass^k alongside pass@k on a seeded corpus, plus cost per confirmed finding and analyst minutes per accepted finding, tracked as first-class metrics beside accuracy.
- **Lab** — Run one task k times, compute pass@k and pass^k from the same runs, then price the result.
- **Tools** — `Inspect`, `promptfoo`, `CyberGym`
- **Models** — `GLM-4.6`

**Run it** — Compute pass@k and pass^k from the same runs, then price the harness in dollars per confirmed finding and analyst minutes per accepted one.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.12.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.12   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b2.10-eval-harness
python3 reliability.py --task fix-cwe-89 --k 5 --repeat 200
python3 cost.py --corpus seeded --analyst-minutes 9
```

*Expect:* pass@5 and pass^5 are computed from the same 2000 trials and diverge sharply: at 80% per-run reliability the harness is 99.9% reliable with a human picking the good answer and 33% reliable unattended. Twelve single-run demos of a 60% harness return a mix of passes and failures, and a change worth 1.5 findings is shown to be invisible against a standard deviation of 3. On the same seeded corpus of 40 units with 10 planted defects, raising sensitivity from 0.70 to 0.95 lifts recall from 60% to 90% and pushes the review queue from 'saves time' to 180 analyst minutes against 160 for reading the code by hand.

---

### B2.13 — Honeypots, canaries and deception in the agent's environment

`AI for Security`

- **Risk** — Every other detector needs a threshold, and every threshold is a trade. Deception needs neither — but only if the bait is placed where the agent actually looks, and rotated before it is learned.
- **Control** — Canary tokens in config, environment and artifact metadata (C4.4), and honeypot tasks salted into the benchmark whose cheat path is logged rather than rewarded (C10.3).
- **Lab** — Authenticate with a canary and watch a zero-threshold alert fire; then salt a benchmark and read the cheat-attempt rate as a leading indicator.
- **Tools** — `Canarytokens`, `Inspect`
- **Models** — `GLM-4.6`

**Run it** — Fire a canary and watch a zero-threshold alert carry attribution; then salt a benchmark with honeypot tasks and read the cheat-attempt rate as a leading indicator.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.13.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.13   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
python3 canary.py --place worker-env,docs,artifact-metadata
python3 honeypot.py --salt benchmark/ --ratio 0.15 --rotate-days 21
```

*Expect:* Two canary authentications out of four events are confirmed compromises with source IP and user agent attached, and no false positive is structurally possible. Both honeypot tasks log a cheat attempt and score zero for it. An unrotated canary's detection rate falls to 0% once learned — reporting a clean environment that is only well-mapped — while rotation holds it at 100%. Deception finds fewer things than the volume detectors and finds them at precision 1.00.

---
