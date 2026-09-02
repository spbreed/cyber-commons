# Track B1 — The Agentic Harness

**Function B · Application Security with an AI SDLC**  
*The secure development lifecycle rebuilt around agents — and the harnesses that test CyberTravels' own agentic platform: SAST, DAST, triage, code fix, skills and harness evaluation.*

**Job titles:** 

**What changes:** 

**Autonomy focus:** 

**Deliverable:** 

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### B1.0 — What an agentic harness is

`both directions`

- **Lab** — Name the eight components, then name which one just failed.
- **Tools** — `OpenTelemetry`

**Run it** — Name the eight components, then name which one just failed.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.0   # run it headless and check it
```

*Expect:* The smallest harness that is still a harness runs its loop, and then the same loop with a verifier added refuses the work it previously accepted. The budget stops a looping model. The harness's own identity, scopes and logging show it is an actor like any other. Eight incidents then classify into seven failure classes, and the two that look identical from outside — capability and verification — separate on one rule: did the harness accept it.

---

### B1.1 — The loop, and the verifier that decides what it may conclude

`both directions`

- **Lab** — Same model, same proposals, opposite outcomes — the verifier is the difference.
- **Tools** — `pytest`

**Run it** — Same model, same proposals, opposite outcomes — the verifier is the difference.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.1   # run it headless and check it
```

*Expect:* The loop fixes a refund-eligibility check in two attempts and stops when the behavioural verifier is satisfied. The identical model and proposals, with only the verifier swapped for one that asks the model whether it is done, accept the off-by-one on the first attempt and report success with a clean trace. Four verifiers are then run against one malformed output: the shape check and the judge both approve it, the exact-match oracle is itself wrong, and a correct verifier reading stale bytecode passes code that is no longer on disk.

---

### B1.2 — What the loop may touch: tools, depth and doing it twice

`both directions`

- **Lab** — Signatures bound what can be asked for, depth bounds how far it travels, keys bound how often it lands.
- **Tools** — `JSON Schema`

**Run it** — Signatures bound what can be asked for, depth bounds how far it travels, keys bound how often it lands.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.2   # run it headless and check it
```

*Expect:* The same capability behind three signatures: the free-text one presents a traversal surface the enumerated one cannot express, and introducing one bug in the shared guard breaks only the tools that expose the argument. A depth-3 delegation chain narrows correctly, then the same chain widens when the check lives in the compromised orchestrator rather than at the issuer. Finally the same action is classified three ways, and an idempotency key containing a timestamp makes every retry a new refund.

---

### B1.3 — Which model runs it, and who checks the checker

`both directions`

- **Lab** — Routing inside the loop, the backbone behind an interface, and a signal the scaffold cannot see.
- **Tools** — `Ollama`, `vLLM`, `Claude Haiku 4.5`, `GLM-4.6`

**Run it** — Routing inside the loop, the backbone behind an interface, and a signal the scaffold cannot see.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.3   # run it headless and check it
```

*Expect:* Tiered routing sends trivial steps to the small model and escalates the hard one, then the same router is driven onto the largest model for every task by an attacker who can cause verification failures — carrying more authority with it. The backbone is scored on CyberTravels' own corpus rather than a vendor chart, and substituted behind an unchanged interface. A self-improving scaffold's own metric then climbs monotonically while its held-out accuracy falls.

---

### B1.4 — One skeleton, four oracles — and whether any of it is true

`both directions`

- **Lab** — Conformance is not accuracy, pass@k is not pass^k, and cost per run is not cost per finding.
- **Tools** — `Semgrep`

**Run it** — Conformance is not accuracy, pass@k is not pass^k, and cost per run is not cost per finding.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.4   # run it headless and check it
```

*Expect:* Four security domains run through one skeleton, differing only in the oracle and the blast radius, and the oracle everyone reaches for — the model's own agreement — is the one that cannot gate an action. Evaluation then separates conformance from accuracy: a harness scoring 100% on schema validity scores far lower on correctness, and matching findings on bare filename rather than parent-plus-filename silently randomises the result. Finally a harness at 80% per-run reliability shows pass@5 of 99.97% and pass^5 of 33%, and the cost per confirmed finding lands well above the cost per run.

---

**Adjacency requirement:** also complete A2.1–A2.2 — the failures happen in the seams.
