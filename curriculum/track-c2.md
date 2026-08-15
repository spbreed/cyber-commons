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

**Run it** — Write a charter that ends in a deployable control.

```bash
cp curriculum/templates/research-charter.md ./charter.md
$EDITOR charter.md   # problem, control outcome, consuming track, funding ask
```

*Expect:* If you cannot name the track that will consume the output, it is not yet research for a CISO org.

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

**Run it** — Attempt targeted unlearning, then try to get the capability back.

```bash
pip install torch transformers && cd labs/c2-research
python3 orthogonalise.py --model meta-llama/Llama-3.2-3B --concept <target> --out ./erased
python3 elicit.py --model ./erased --strategies paraphrase,encoding,few-shot
```

*Expect:* Elicitation usually recovers some capability. Report what the technique actually guarantees, not what it appears to.

---

### C2.4 — Data-layer research

`Security of AI`

- **Risk** — Memorisation, extraction, embedding inversion, index poisoning.
- **Control** — Measure extraction rates rather than assert privacy.
- **Lab** — Invert embeddings from a local vector store and recover source text.
- **Tools** — `Qdrant`, `sentence-transformers`

**Run it** — Recover source text from embeddings.

```bash
docker run -d -p 6333:6333 qdrant/qdrant && cd labs/c2-research
python3 index.py --corpus sensitive-sample/ --store qdrant
python3 invert.py --store qdrant --top-k 20 --report inversion.md
```

*Expect:* A measured reconstruction rate. 'Embeddings are not the data' is a claim you can now test rather than repeat.

---

### C2.5 — Supply-chain research

`Security of AI`

- **Risk** — Adapter and LoRA provenance, registry tampering, dependency confusion in agent ecosystems.
- **Control** — Verify provenance; sign and attest artefacts.
- **Lab** — Sign a model artefact with Sigstore and detect a tampered adapter.
- **Tools** — `Sigstore`, `in-toto`, `OWASP AIBOM`

**Run it** — Detect a tampered adapter through provenance.

```bash
cd labs/c2-research
cosign sign-blob --bundle model.sig adapter.safetensors
python3 tamper.py --file adapter.safetensors --flip-bytes 8
cosign verify-blob --bundle model.sig adapter.safetensors   # fails
```

*Expect:* Signature verification catches it; an unsigned registry would not have.

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

**Run it** — Contamination-check a public benchmark.

```bash
cd labs/c2-research
python3 contamination.py --benchmark ../b2.10-eval-harness/ground-truth --model $MODEL --method canary
python3 contamination.py --report
```

*Expect:* Overlap evidence between benchmark corpus and plausible training data — the basis for saying 'this score is overstated' defensibly.

---

### C2.8 — From finding to control

`both directions`

- **Risk** — Research output the platform team cannot deploy.
- **Control** — Hand over something deployable and evidenceable; handle disclosure.
- **Lab** — Convert one finding into a Kyverno/OPA policy another track adopts.
- **Tools** — `OPA`, `Kyverno`

**Run it** — Turn a finding into a policy another track deploys.

```bash
cd labs/c2-research
python3 finding_to_policy.py --finding findings/F-07.json --target opa --out policy.rego
opa test policy.rego policy_test.rego
cp policy.rego ../a3-sandbox/policies/
```

*Expect:* A tested Rego policy handed to A3 — research output the platform team can actually deploy.

---

### C2.9 — Research as institutional capital

`both directions`

- **Risk** — Invisible work, uncredited function.
- **Control** — Publication, open-source release, a defensible public record.
- **Lab** — Release one artefact publicly with a reproducibility README.
- **Tools** — `git`

**Run it** — Release one artefact with a reproducibility README.

```bash
cd labs/c2-research
python3 package_artefact.py --finding F-07 --include data,code,traces --out release/
cd release && ./reproduce.sh   # must work on a clean machine
```

*Expect:* Someone else can rerun it. That is what makes it institutional capital rather than a claim.

---
