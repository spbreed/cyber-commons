# Track B2 — The Security Automation / Harness Engineer

**Function B · Product & Application Security**  
*Closest to the developers, and therefore first to meet agents at scale — usually before anyone approved it.*

**Job titles:** Security Automation Engineer, Detection & Response Engineer (platform side), Security Tooling Lead — and the role most orgs haven't created yet

**What changes:** This is a new job. You build the loops every other track runs. SRE for the security function's agents.

**Autonomy focus:** You are the person who builds the L2.5 boundary everyone else operates inside.

**Deliverable:** A reusable harness scaffold adopted by at least two other tracks.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

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

### B2.10 — Evaluating a security harness

`AI for Security`  ·  **flagship lab**

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

> Lab source: [`labs/b2.10-eval-harness`](../labs/b2.10-eval-harness)

---
