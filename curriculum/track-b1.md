# Track B1 — What Runs the Pipeline

**Function B · Application Security with an AI SDLC**  
*The secure development lifecycle rebuilt around agents — and the harnesses that test CyberTravels' own agentic platform: SAST, DAST, triage, code fix, skills and harness evaluation.*

**Job titles:** 

**What changes:** 

**Autonomy focus:** 

**Deliverable:** 

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### B1.0 — What a harness is, and the loop it runs

`both directions`

- **Lab** — Build the smallest thing that is still a harness, then add the one component that was missing.
- **Tools** — `OpenTelemetry`

**Run it** — Build the smallest thing that is still a harness, then add the one component that was missing.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.0.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.0   # run it headless and check it
```

*Expect:* The minimal harness reports success while the tests still fail. Adding one component — a verifier that reads ground truth rather than the agent's claim — reports the same run as unverified, and verifies the run where the patch genuinely works. A budget of four stops a model that never emits `done`. Against a finding whose rationale contradicts the finding itself, the shape check and the LLM judge both accept it. The pipeline's own identity holds `repo:comment` and not `repo:write`.

---

### B1.1 — Who chooses the next tool call — you, the model, or a server

`both directions`

- **Lab** — Enumerate every path a deterministic graph can take, then watch an MCP server edit an instruction into your context overnight.
- **Tools** — `LangGraph`, `MCP`, `Claude Haiku 4.5`, `Qwen2.5-7B`

**Run it** — Enumerate every path a deterministic graph can take, then watch an MCP server edit an instruction into your context overnight.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/B1.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session B1.1   # run it headless and check it
```

*Expect:* The deterministic graph runs two different inputs down two different paths, and then enumerates every path it can ever take — two. The same four capabilities under model-chosen tool calling reach over 50,000 sequences at eight calls and are unbounded in principle, so blast radius replaces path review. An MCP server CyberTravels does not operate then edits one tool description overnight and injects an instruction into the model's context with no client change; pinning the digest of the whole surface — description included — refuses it.

---

**Adjacency requirement:** also complete A2.1–A2.2 — the failures happen in the seams.
