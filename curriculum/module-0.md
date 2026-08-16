# Module 0 — The Shared Core

### Everyone. Five sessions. No exceptions, no substitutions.

A common language, so that when the IAM engineer says "attenuated delegation" the GRC analyst knows what evidence to ask for.

**Shared vocabulary used by every track:**

- **Three planes** — decision — the model infers; control — identity, routing, policy decide what is permitted; action — tools and APIs change state. Autonomy does not live in the model; it lives in what you let the model's output trigger.
- **Autonomy ladder** — L1 human-triggered; L2 human-in-the-loop; L2.5 semi-autonomous (bounded self-execution on low-risk actions); L3 bounded autonomous. Most of your org will live at L2.5 for years. That is a destination, not a stopover.
- **A.G.E.N.T maturity** — Awareness → Governance → Engineering → Navigation → Trust.

---

### M0.1 — What an agent actually is

`both directions`

- **Risk** — "The model did it" is treated as a root cause, so the real control gap is never found.
- **Control** — Separate the three planes; locate autonomy in what the model's output is allowed to trigger.
- **Lab** — Run the same prompt through a bare model, a copilot loop and a tool-enabled harness on local GLM-4.6 — watch which one can actually change state.
- **Tools** — `Ollama`, `llama.cpp`
- **Models** — `GLM-4.6`, `Llama 3.3`

**Run it** — Show that autonomy lives in the action plane, not the model.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/M0.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session M0.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
ollama pull llama3.3 && ollama pull nomic-embed-text
cd labs/m0-agent-loop && python3 planes_demo.py --model llama3.3
# same prompt, three configurations: bare model / read-only tools / write tools
```

*Expect:* Identical model output; only configuration 3 changes state on disk. Prints a PASS/FAIL table.

---

### M0.2 — The loop

`both directions`

- **Risk** — A harness with no verifier converges on plausible-looking garbage.
- **Control** — Every loop has a context, a toolset, a verifier and a budget — the verifier is the security control.
- **Lab** — Build a 40-line plan→act→verify→stop loop; break the verifier and watch the loop confidently finish wrong.
- **Tools** — `Python`, `Ollama`
- **Models** — `Kimi K2`, `GLM-4.6`

**Run it** — Build the minimum loop and prove the verifier is the security control.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/M0.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session M0.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 loop.py --task fix-tests --verifier pytest      # honest oracle
python3 loop.py --task fix-tests --verifier llm-judge   # self-grading
python3 loop.py --task fix-tests --verifier none        # no stop signal
```

*Expect:* pytest verifier converges or stops; llm-judge declares success on broken code; none diverges until the budget kills it.

---

### M0.3 — The autonomy ladder

`both directions`

- **Risk** — Workflows are promoted to autonomy on vibes, then can't be demoted.
- **Control** — L1→L2→L2.5→L3 with named promotion evidence and a named demotion authority.
- **Lab** — Walk one real workflow up all four rungs; write the promotion criteria that gate each step.
- **Tools** — `kagent`

**Run it** — Walk one workflow up the autonomy ladder with named promotion evidence.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/M0.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session M0.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/m0-agent-loop
python3 ladder.py --workflow dependency-bump --rung L1
python3 ladder.py --workflow dependency-bump --rung L2.5 --require-evidence
```

*Expect:* L2.5 refuses to run until the promotion evidence file exists — autonomy as an earned event.

---

### M0.4 — Prompt injection, once, properly

`Security of AI`

- **Risk** — Untrusted text in retrieval, tool output and scanner responses hijacks intent — everywhere, not just chat.
- **Control** — Treat it as a control-plane problem: untrusted-content tagging, output allowlisting, no shell from untrusted context.
- **Lab** — Poison a retrieved document and a tool response against a local model; then re-run with content tagging and measure the drop.
- **Tools** — `garak`, `promptfoo`
- **Models** — `Llama 3.3`, `Llama Guard 4`

**Run it** — Reproduce direct and indirect injection, then measure a real defense.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/M0.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session M0.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
pip install garak promptfoo
cd labs/m0-injection && python3 poison.py --target rag   # plant in a retrieved doc
garak --model_type openai.OpenAICompatible --model_name $MODEL --probes promptinject
python3 poison.py --target rag --defense tagging   # re-run with untrusted-content tagging
```

*Expect:* Attack success rate drops measurably with tagging; the number, not the vibe, is the deliverable.

---

### M0.5 — Who owns what

`both directions`

- **Risk** — Nobody holds stop authority, so nobody exercises it.
- **Control** — Identity owns the control plane; business units own the grants; security owns stop authority and the evidence.
- **Lab** — Fill in the ownership map for your own org and find your row.

**Run it** — Locate yourself on the ownership map.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/M0.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session M0.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cp curriculum/templates/ownership-map.csv ./my-org-ownership.csv
$EDITOR my-org-ownership.csv   # fill Owns / Builds / Uses for your function
```

*Expect:* Every topic cluster has exactly one owner. Any row with zero or two owners is your first finding.

---

**Exit test:** Given a one-paragraph description of an agentic workflow, name its autonomy level, its blast radius, and the one control you would add first.
