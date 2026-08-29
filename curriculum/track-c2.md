# Track C2 — The Security Researcher

**Function C · AI for Security Research**  
*Offensive testing and research where the agent is both the instrument and the target, and where a result is only worth what it can be reproduced at.*

**Job titles:** Security Researcher, Applied Research Engineer, Vulnerability Researcher, AI Security Researcher

**What changes:** Turning curiosity into a result somebody else can deploy. 7 lessons.

**Autonomy focus:** You deliberately operate at L3 in isolated environments so the rest of the org never has to.

**Deliverable:** One reproducible research artefact with a named control implication, handed to a platform or AppSec track.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### C2.1 — What research means in a CISO org

`both directions`

- **Risk** — Research with a publication outcome and no control outcome.
- **Control** — Choose problems that end in a deployable control; get funded.
- **Lab** — Write a one-page research charter with a named consuming track.

**Run it** — Write a charter that ends in a deployable control.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C2.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C2.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
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
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C2.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C2.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
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
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C2.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C2.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
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
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C2.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C2.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
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
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C2.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C2.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/c2-research
cosign sign-blob --bundle model.sig adapter.safetensors
python3 tamper.py --file adapter.safetensors --flip-bytes 8
cosign verify-blob --bundle model.sig adapter.safetensors   # fails
```

*Expect:* Signature verification catches it; an unsigned registry would not have.

---

### C2.6 — Benchmarks, reproducibility and the research harness

`AI for Security`

- **Risk** — Model effects and harness effects confounded, and published benchmarks overstating real-world capability.
- **Control** — Multi-backbone runs on fixed seeds and corpora, plus contamination and construct-validity checks before any number is trusted.
- **Lab** — Run one harness across three model families, separate the two effects, then contamination-check a public benchmark against a training window.
- **Tools** — `Inspect`, `Cyber Commons eval harness`
- **Models** — `Llama 3.3`, `GLM-4.6`, `Kimi K2`

**Run it** — Separate the model effect from the harness effect, then check a public benchmark for its majority baseline, its key provenance and its matcher.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C2.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C2.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/c2-research
python3 harness_vs_model.py --models llama3.3,glm-4.6,kimi-k2 --seeds 5
python3 contamination.py --benchmark ../b2.10-eval-harness/ground-truth --report
```

*Expect:* The baseline suite reports per-case rates with intervals. Provenance reduces every injection case to about 0.02 with non-overlapping intervals, while identity and containment are unchanged. Adding 12 trivially-blocked cases cuts aggregate ASR by roughly 60% with no change to the build, and the suite-health check flags that suite as diluted. On the critique side: a skewed key gives a 0.875 floor before anyone answers anything, a leaked key scores a perfect 1.000, and answers naming the wrong directory score 1.000 under basename matching against 0.250 under path matching.

---

### C2.7 — From finding to control, and to institutional capital

`both directions`

- **Risk** — Research output the platform team cannot deploy, and a function whose work stays invisible and uncredited.
- **Control** — Hand over something deployable and evidenceable, handle disclosure, and leave a defensible public record.
- **Lab** — Convert one finding into a policy another track adopts, and release it with a reproducibility README.
- **Tools** — `OPA`, `Kyverno`, `git`

**Run it** — Turn one finding into a control with an eval case that fails on the old build, then score a year of findings by what still holds without you.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/C2.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session C2.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/c2-research
python3 package_artefact.py --finding F-07 --include data,code,traces --out release/
cd release && ./reproduce.sh   # must work on a clean machine
```

*Expect:* The eval case returns False on the old build and True on the new one, covering 12 privileged/source combinations while leaving the principal path working. The control blocks the payload; the detection fires at critical severity on the old build and at info severity on the new one as coverage evidence. The handover package permits closure only when the proof of fix is valid and something shipped. Scored across a year of eight findings the programme lands 20 of a possible 40 durability points, with only three still holding without a person behind them.

---
