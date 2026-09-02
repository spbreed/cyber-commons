# Track B2 — Trusting the Harness that Tests CyberTravels

**Function B · Application Security with an AI SDLC**  
*The secure development lifecycle rebuilt around agents — and the harnesses that test CyberTravels' own agentic platform: SAST, DAST, triage, code fix, skills and harness evaluation.*

**Job titles:** Security Automation Engineer, Detection & Response Engineer (platform side), Security Tooling Lead — and the role most orgs haven't created yet

**What changes:** Build the loop once, then the SAST, DAST, triage, code-fix, skills and harness evaluations CyberTravels needs — in the order each one becomes possible. 14 lessons.

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
- **Open-weight models** — `Llama 3.3`, `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Build a minimal working harness from scratch, naming each component as it appears, then show what breaks when the verifier is removed.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.0   # run it headless and check it
```

*Expect:* The minimal harness runs and reports success while the tests still fail. Adding one component — a verifier that reads ground truth rather than the agent's own claim — flips `verified` to False on the same run and to True only when the fix genuinely works. A four-step budget stops a looping model. The harness then scores itself as a non-human identity holding repo:write and running unattended.

---

### B2.1 — Evaluating a security harness

`AI for Security`

- **Risk** — A single successful run hides how unreliable an agent really is; a hallucinated finding looks exactly like a real one.
- **Control** — Ground truth + blind protocol + execution-verified scoring; report reliability (pass^k) not just capability (pass@k); never quote schema conformance as accuracy.
- **Lab** — The full Cyber Commons eval harness: build 552-row ground truth from SecLLMHolmes + TerraGoat/Checkov, run a blind model audit, score with expert-proxy + dual judges, and compare Llama / GLM / Kimi as the backing model.
- **Tools** — `Cyber Commons eval harness`, `Checkov`, `CyberGym`, `Inspect`
- **Open-weight models** — `Llama 3.3`, `GLM-4.6`, `Kimi K2`
- **Frontier models** — `Claude Sonnet 5`  ·  *every lab runs on either, and offline on neither*

**Run it** — The full eval harness: ground truth, blind protocol, execution-verified scoring, model comparison.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.1   # run it headless and check it

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

### B2.2 — Reliability and cost under non-determinism

`AI for Security`

- **Risk** — A single lucky run published as a result, and cost per finding never computed at all, so nobody notices the tool moved work instead of removing it.
- **Control** — pass^k alongside pass@k on a seeded corpus, plus cost per confirmed finding and analyst minutes per accepted finding, tracked as first-class metrics beside accuracy.
- **Lab** — Run one task k times, compute pass@k and pass^k from the same runs, then price the result.
- **Tools** — `Inspect`, `promptfoo`, `CyberGym`
- **Open-weight models** — `GLM-4.6`
- **Frontier models** — `Claude Haiku 4.5`  ·  *every lab runs on either, and offline on neither*

**Run it** — Compute pass@k and pass^k from the same runs, then price the harness in dollars per confirmed finding and analyst minutes per accepted one.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B2.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B2.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/b2.10-eval-harness
python3 reliability.py --task fix-cwe-89 --k 5 --repeat 200
python3 cost.py --corpus seeded --analyst-minutes 9
```

*Expect:* pass@5 and pass^5 are computed from the same 2000 trials and diverge sharply: at 80% per-run reliability the harness is 99.9% reliable with a human picking the good answer and 33% reliable unattended. Twelve single-run demos of a 60% harness return a mix of passes and failures, and a change worth 1.5 findings is shown to be invisible against a standard deviation of 3. On the same seeded corpus of 40 units with 10 planted defects, raising sensitivity from 0.70 to 0.95 lifts recall from 60% to 90% and pushes the review queue from 'saves time' to 180 analyst minutes against 160 for reading the code by hand.

---
