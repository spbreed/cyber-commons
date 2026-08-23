# Track B2 — The Security Automation / Harness Engineer

**Function B · Product & Application Security**  
*Closest to developers, so first to meet agents at scale — and the ones who build the pipeline rather than buy it.*

**Job titles:** Security Automation Engineer, Detection & Response Engineer (platform side), Security Tooling Lead — and the role most orgs haven't created yet

**What changes:** Build the loop, point it at a discipline, then prove it works. 18 lessons.

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

### B2.4 — Budgets and stop conditions

`AI for Security`

- **Risk** — Every loop needs a reason to stop that isn't "it finished".
- **Control** — Step limits, goal timeouts, token ceilings, spend circuit breakers.
- **Lab** — Make a loop diverge, then bound it four different ways.
- **Tools** — `Python`
- **Models** — `Llama 3.3`

**Run it** — Bound a divergent loop four different ways.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 loop.py --task impossible --max-steps 5
python3 loop.py --task impossible --timeout 60
python3 loop.py --task impossible --token-ceiling 20000
python3 loop.py --task impossible --spend-cap 0.50
```

*Expect:* Four different stop reasons, all recorded in the trace. 'It finished' is never one of them.

---

### B2.5 — Model tiering and routing inside the loop

`AI for Security`

- **Risk** — Paying frontier prices for executor-grade steps.
- **Control** — Cheap executor, escalated reasoner, advisor at decision points.
- **Lab** — Route Llama-executor → GLM-reasoner with LiteLLM and attribute spend per run.
- **Tools** — `LiteLLM`, `vLLM`
- **Models** — `Llama 3.3`, `GLM-4.6`, `Kimi K2`

**Run it** — Route cheap executor to escalated reasoner and attribute spend.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install 'litellm[proxy]' && cd labs/shared
litellm --config litellm.config.yaml &   # llama executor, glm reasoner, kimi advisor
cd ../m0-agent-loop && MODEL=router python3 loop.py --task fix-tests --json | jq '.tokens'
python3 ../shared/spend_report.py --by-run
```

*Expect:* Per-run, per-tier spend attribution. Escalation happens only at decision points.

---

### B2.6 — Sub-agents and delegation depth

`Security of AI`

- **Risk** — Authority inherited silently from parent to child agent.
- **Control** — Fan-out control, recursion budgets, explicit authority inheritance.
- **Lab** — Cap delegation depth and prove a grandchild agent cannot exceed its parent.
- **Tools** — `kagent`, `SPIRE`

**Run it** — Prove a grandchild agent cannot exceed its parent.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a2-delegation
python3 subagent.py --depth 3 --parent-scope repo:read
python3 subagent.py --depth 3 --parent-scope repo:read --attempt-escalate
```

*Expect:* Recursion budget caps depth; the escalation attempt is refused by the token, not by a check.

---

### B2.7 — Failure taxonomy

`AI for Security`

- **Risk** — Loop divergence, objective drift, reward hacking, silent truncation, tool thrash.
- **Control** — Recognise each from a trace.
- **Lab** — Read five real traces and name the failure in each.
- **Tools** — `OpenTelemetry`

**Run it** — Name the failure from the trace alone.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop/traces
python3 ../classify_failure.py --trace divergence.jsonl
for t in *.jsonl; do echo -n "$t: "; python3 ../classify_failure.py --trace $t --quiet; done
```

*Expect:* Loop divergence, objective drift, reward hacking, silent truncation, tool thrash — one per trace.

---

### B2.8 — Self-improving scaffolds

`Security of AI`

- **Risk** — A harness that rewrites its own config makes the fitness function the security control.
- **Control** — Sandbox the mutation, keep only measured gains, pin the fitness function.
- **Lab** — Let a scaffold mutate itself in a sandbox and keep only what the oracle confirms.
- **Tools** — `Python`, `Docker`
- **Models** — `Kimi K2`

**Run it** — Let a scaffold mutate itself, and keep only measured gains.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 evolve.py --generations 5 --sandbox docker --fitness pytest-pass-rate
python3 evolve.py --show-lineage   # what changed, what was kept, what was reverted
```

*Expect:* Only mutations the deterministic oracle confirms survive. Pin the fitness function — it is now the security control.

---

### B2.9 — Idempotency, replay and rollback

`AI for Security`

- **Risk** — Any agent action you cannot replay you cannot investigate.
- **Control** — Design requirements, not afterthoughts.
- **Lab** — Replay a full agent run from the trace and reproduce its decision.
- **Tools** — `OpenTelemetry`

**Run it** — Replay an agent run from its trace.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.9.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.9   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 loop.py --task fix-tests --json > run.json
python3 replay.py --trace run.json --assert-identical
```

*Expect:* Either it reproduces, or the tool names the field you failed to log. Anything you cannot replay you cannot investigate.

---

### B2.11 — Building the SAST harness

`AI for Security`

- **Risk** — A SAST loop that matches patterns instead of reasoning about semantics, and cannot explain why anything is a vulnerability.
- **Control** — Index → summarise → hypothesise → verify, with per-file context budgets, reachability gating and a deduplication stage that decides whether the output is a queue or a landfill.
- **Lab** — Run the four-stage loop over a seeded corpus and measure how much of the output survives reachability gating.
- **Tools** — `OpenGrep`, `Trivy`
- **Models** — `Kimi K2.6`, `GLM-5.2`

**Run it** — Run the four-stage loop over a seeded corpus and measure how much of the output survives reachability gating.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.11.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.11   # run it headless and check it
```

*Expect:* The four-stage loop runs over a seeded corpus of eight units with five planted defects. Shrinking the per-file context budget removes the facts verification depends on: below 25 tokens reachability is unknown and everything survives, which reads as higher recall and is actually less verification. Deduplicating three analysers' output collapses a 3x inflated queue back to the real defect count.

---

### B2.12 — Building the DAST and exploitation harness

`AI for Security`

- **Risk** — A model opinion recorded as a confirmed exploit. Without a deterministic oracle the harness reports whatever it believes.
- **Control** — Drive a running target, generate payloads, observe behaviour, and confirm only on a deterministic oracle — inside sandbox replication with blast-radius limits and evidence capture.
- **Lab** — Confirm one vulnerability empirically against a replica, and show the same finding failing to confirm when the oracle is the model's own judgement.
- **Tools** — `OWASP ZAP`, `Metasploit`, `CAI`
- **Models** — `GLM-5.2`

**Run it** — Confirm one vulnerability empirically against a replica, and show the same finding failing to confirm when the oracle is the model's own judgement.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.12.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.12   # run it headless and check it
```

*Expect:* Six payloads are driven at a sandboxed replica. The deterministic oracle — the target's own execution log — confirms the injections and refuses the benign requests, while a stub standing in for model self-assessment confirms every request that returned HTTP 200, including the ones that prove nothing. The destructive payload is refused before it is sent, and each surviving finding carries the observable that proves it.

---

### B2.13 — Building the threat-modelling harness

`AI for Security`

- **Risk** — A threat model produced once a year for a system that changes every release. By the second sprint it describes something that no longer exists.
- **Control** — Turn architecture, IaC, code and data flows into trust boundaries, assets, entry points and abuse cases repeatably — with model diffing between versions and human review as a checkpoint, not the bottleneck.
- **Lab** — Generate a threat model from source, change one component, and diff the two models to see exactly what the change introduced.
- **Tools** — `OWASP Threat Dragon`, `Trivy`
- **Models** — `GLM-5.2`

**Run it** — Generate a threat model from source, change one component, and diff the two models to see exactly what the change introduced.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.13.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.13   # run it headless and check it
```

*Expect:* A threat model derived from architecture yields threats sorted deterministically. Two lines of infrastructure change introduce three new threats, one from a component the pull request description never mentions. An unstable generator produces a diff full of churn on unchanged input, and the deterministic one regenerates identically five times — turning a whole-model workshop into a review of only what changed.

---

### B2.14 — Building the pentest harness

`AI for Security`

- **Risk** — An offensive loop with no hard scope enforcement is an incident with a project plan.
- **Control** — Recon, enumeration, exploitation and lateral movement as a bounded, auditable agent loop — hard scope enforcement, destructive-action gating, credential handling and named operator handoff points.
- **Lab** — Run the loop against an owned target and show the scope guard refusing an out-of-scope host before the request is made.
- **Tools** — `Metasploit`, `CAI`
- **Models** — `Kimi K2.6`

**Run it** — Run the loop against an owned target and show the scope guard refusing an out-of-scope host before the request is made.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.14.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.14   # run it headless and check it
```

*Expect:* Six of seven targets are classified against scope, with the cloud metadata address and the production host both refused before any request is made. The bounded loop refuses three actions, holds the destructive one for an operator, and completes the rest — and an attention-based gate is shown matching the structural check only at 100% attention. The run ends with a reconstructable audit trail.

---

### B2.15 — Choosing the model backbone

`AI for Security`

- **Risk** — A backbone chosen on a vendor chart, then wired in so deeply that substituting it means rewriting the harness.
- **Control** — Evaluate candidates on your own corpus, and above all design for backbone substitution — any list of best models is stale within a quarter.
- **Lab** — Score two backbones on the same corpus, then swap one for the other behind an unchanged harness interface.
- **Tools** — `LiteLLM`, `vLLM`, `Ollama`
- **Models** — `Kimi K2.7-Code`, `GLM-5.2`, `Llama 4`

**Run it** — Score two backbones on the same corpus, then swap one for the other behind an unchanged harness interface.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.15.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.15   # run it headless and check it
```

*Expect:* Three stand-in backbones are scored on the same corpus: the one with the best recall is not the one with the best cost per finding. A harness that couples to vendor output shapes fails outright on the third backbone, while the interface version substitutes in a single line and reports the recall, precision and cost deltas. A data-sovereignty column then removes the closed-weights option entirely.

---

### B2.10 — Evaluating a security harness

`AI for Security`

- **Risk** — A single successful run hides how unreliable an agent really is; a hallucinated finding looks exactly like a real one.
- **Control** — Ground truth + blind protocol + execution-verified scoring; report reliability (pass^k) not just capability (pass@k); never quote schema conformance as accuracy.
- **Lab** — The full Cyber Commons eval harness: build 552-row ground truth from SecLLMHolmes + TerraGoat/Checkov, run a blind model audit, score with expert-proxy + dual judges, and compare Llama / GLM / Kimi as the backing model.
- **Tools** — `Cyber Commons eval harness`, `Checkov`, `CyberGym`, `Inspect`
- **Models** — `Llama 3.3`, `GLM-4.6`, `Kimi K2`

**Run it** — The full eval harness: ground truth, blind protocol, execution-verified scoring, model comparison.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.10.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.10   # run it headless and check it

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

### B2.16 — Performance testing: reliability under non-determinism

`AI for Security`

- **Risk** — A single lucky run published as a result. One run tells you almost nothing about a stochastic system.
- **Control** — Measure pass^k — succeeds k times out of k — alongside pass@k, plus run-to-run variance on a fixed corpus, so harness failure can be separated from model failure before either is changed.
- **Lab** — Run one task k times, compute pass@k and pass^k from the same runs, and watch the two numbers disagree.
- **Tools** — `Inspect`, `promptfoo`
- **Models** — `GLM-5.2`

**Run it** — Run one task k times, compute pass@k and pass^k from the same runs, and watch the two numbers disagree.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.16.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.16   # run it headless and check it
```

*Expect:* pass@5 and pass^5 are computed from the same 2000 trials and diverge sharply: at 80% per-run reliability the harness is 99.9% reliable with a human picking the good answer and 33% reliable unattended. Twelve single-run demos of a 60% harness return a mix of passes and failures, and a change worth 1.5 findings is shown to be invisible against a standard deviation of 3.

---

### B2.17 — Regression suites, cost curves and the economics of autonomy

`AI for Security`

- **Risk** — Accuracy asserted rather than measured, and cost per finding never computed at all — so nobody notices the tool moved work instead of removing it.
- **Control** — A seeded corpus with planted known-answer vulnerabilities, plus cost per confirmed finding, time-to-first-finding and human-review load tracked as first-class metrics beside accuracy.
- **Lab** — Score a harness against a seeded corpus and compute its cost per confirmed finding and analyst minutes per accepted finding.
- **Tools** — `Inspect`, `CyberGym`
- **Models** — `GLM-5.2`

**Run it** — Score a harness against a seeded corpus and compute its cost per confirmed finding and analyst minutes per accepted finding.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.17.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.17   # run it headless and check it
```

*Expect:* A forty-unit corpus with ten planted defects gives recall a real denominator. Raising sensitivity improves recall while pushing the analyst review queue past the cost of reading the code by hand — the accuracy metric improves as the tool gets worse. A regression suite then shows a net-positive change that still lost findings it used to catch.

---
