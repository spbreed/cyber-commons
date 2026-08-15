# Track C2 — The Security Researcher

**Function C · Offensive Security & Research**  
*The function that finds out what is actually true, as opposed to what the architecture diagram claims.*

**Job titles:** Security Researcher, Applied Research Engineer, Vulnerability Researcher, AI Security Researcher

**What changes:** A research function that used to sit adjacent to the CISO org becomes central to it. This track produces the primitives the other eleven consume.

**Autonomy focus:** You deliberately operate at L3 in isolated environments so the rest of the org never has to.

**Deliverable:** One reproducible research artefact with a named control implication, handed to a platform or AppSec track.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### C2.1 — What research means in a CISO org

`both directions`

- **Risk** — Research with a publication outcome and no control outcome.
- **Control** — Choose problems that end in a deployable control; get funded.
- **Lab** — Write a one-page research charter with a named consuming track.

---

### C2.2 — Model-layer research

`Security of AI`

- **Risk** — Model cards read credulously.
- **Control** — Adversarial robustness, jailbreak taxonomy, refusal analysis, capability elicitation.
- **Lab** — Run a jailbreak taxonomy across Llama, GLM and Kimi and chart where they differ.
- **Tools** — `garak`
- **Models** — `Llama 3.3`, `GLM-4.6`, `Kimi K2`

**Run it** — Chart jailbreak taxonomy differences across three open-weight families.

```bash
cd labs/c2-research
for M in llama3.3 glm-4.6 kimi-k2; do garak --model_type openai.OpenAICompatible --model_name $M --probes dan,encoding,malwaregen --report_prefix $M; done
python3 compare_reports.py
```

*Expect:* Per-family refusal and elicitation profiles. Model effects separated from harness effects.

---

### C2.3 — Weight-level techniques

`Security of AI`

- **Risk** — Claiming a capability was removed when it was only hidden.
- **Control** — Concept erasure and orthogonalisation on open weights — with honest claims.
- **Lab** — Attempt targeted unlearning on an open-weight model and try to elicit the capability back.
- **Tools** — `TransformerLens`, `PyTorch`
- **Models** — `Llama 3.3`

---

### C2.4 — Data-layer research

`Security of AI`

- **Risk** — Memorisation, extraction, embedding inversion, index poisoning.
- **Control** — Measure extraction rates rather than assert privacy.
- **Lab** — Invert embeddings from a local vector store and recover source text.
- **Tools** — `Qdrant`, `sentence-transformers`

---

### C2.5 — Supply-chain research

`Security of AI`

- **Risk** — Adapter and LoRA provenance, registry tampering, dependency confusion in agent ecosystems.
- **Control** — Verify provenance; sign and attest artefacts.
- **Lab** — Sign a model artefact with Sigstore and detect a tampered adapter.
- **Tools** — `Sigstore`, `in-toto`, `OWASP AIBOM`

---

### C2.6 — Building the research harness

`AI for Security`

- **Risk** — Model effects and harness effects confounded.
- **Control** — Multi-backbone benchmarking with statistical honesty.
- **Lab** — Run one harness across three model families and separate the two effects.
- **Tools** — `Inspect`, `Cyber Commons eval harness`
- **Models** — `Llama 3.3`, `GLM-4.6`, `Kimi K2`

**Run it** — Separate model effects from harness effects.

```bash
cd labs/b2.10-eval-harness
for M in llama3.3 glm-4.6 kimi-k2; do MODEL=$M scripts/vulnbench.sh compare; done
python3 work_mantis/compare_models.py
```

*Expect:* Same harness, three backbones — the delta is the model. This is exactly how the committed comparison table was produced.

---

### C2.7 — Benchmark design and critique

`AI for Security`

- **Risk** — Most published security benchmarks overstate real-world capability.
- **Control** — Contamination checks; adapt methodology to your own corpus.
- **Lab** — Contamination-check a public benchmark against a model's training window.
- **Tools** — `Cyber Commons eval harness`

---

### C2.8 — From finding to control

`both directions`

- **Risk** — Research output the platform team cannot deploy.
- **Control** — Hand over something deployable and evidenceable; handle disclosure.
- **Lab** — Convert one finding into a Kyverno/OPA policy another track adopts.
- **Tools** — `OPA`, `Kyverno`

---

### C2.9 — Research as institutional capital

`both directions`

- **Risk** — Invisible work, uncredited function.
- **Control** — Publication, open-source release, a defensible public record.
- **Lab** — Release one artefact publicly with a reproducibility README.
- **Tools** — `git`

---
