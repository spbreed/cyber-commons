# Getting the models — open weight, frontier, or neither

Every lab runs **three ways from one code path**, and the choice is one
environment variable:

| Backend | How | What it costs |
|---|---|---|
| **offline** (the default) | nothing to set | nothing — a deterministic stand-in, labelled as one everywhere it appears |
| **open weight** | `OPENAI_BASE_URL` | nothing, on your own hardware — Ollama, vLLM, or a free hosted tier |
| **frontier** | `ANTHROPIC_API_KEY` | cents per lesson on the cheapest model |

Every lab is designed to reach its acceptance criteria on **open-weight models
you can download or call for free**. A frontier model is a supported option,
never a requirement — which is what keeps the commons usable by a two-person NGO
and a global bank alike.

```bash
# open weight, local
ollama pull glm-4.6
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6

# frontier — cheapest current Claude model
export ANTHROPIC_API_KEY=...            # MODEL defaults to claude-haiku-4-5-20251001
```

The adapter is standard library only (`urllib`), so a notebook stays
self-contained and still runs on a Kaggle kernel with the internet switched off.
If a backend is configured and the call fails, the lesson **says so and falls
back to the replay, labelled as a replay** — it never reports a model's answer
when no model answered.

**Keys never go in this repository.** Put them in your environment or in a file
outside the working tree; `scripts/check_secrets.py` blocks anything
credential-shaped from being committed, and it runs as a pre-commit hook and in
CI.

> **Check current terms.** Free tiers, rate limits and even licences change.
> Everything below was accurate when written; verify before you depend on it.

---

## The three families we standardise on

| Family | Why it's here | Weights licence | Good for |
|--------|---------------|-----------------|----------|
| **Llama** (Meta) — Llama 3.3 70B, Llama 4, **Llama Guard 4** | The most widely hosted open family; Guard variants are purpose-built safety classifiers used in the guardrail labs | Llama Community Licence (open weights, some use restrictions — read it) | General agent work, and Guard for B2/E1 guardrail labs |
| **Kimi** (Moonshot AI) — Kimi K2 | Strong agentic/tool-use behaviour, which is exactly what the harness tracks exercise | Modified MIT | Harness loops, offensive planning, long-horizon tasks |
| **GLM** (Z.ai / Zhipu) — GLM-4.6, GLM-4.5-Air | Strong code reasoning at a size that self-hosts comfortably | MIT | Code review, SAST triage, SOC triage |

All labs read one env var set, so **no lab hard-codes a provider**:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1   # or any OpenAI-compatible endpoint
export OPENAI_API_KEY=ollama                        # any non-empty string for local
export MODEL=glm-4.6
```

---

## Option 1 — Local, offline, genuinely $0 (the default)

**[Ollama](https://ollama.com)** is the fastest path and works on a laptop.

```bash
# install (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# pull an open-weight model — quantised variants fit in consumer RAM
ollama pull llama3.3            # ~40GB at Q4; use llama3.2 (3B) on a small laptop
ollama pull glm-4.6             # or a GLM-Air variant for lower RAM
ollama pull llama-guard3        # safety classifier for the guardrail labs

# Ollama serves an OpenAI-compatible API on :11434
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=llama3.3
```

**Sizing honestly, and measured rather than asserted.** A 70B model at 4-bit
needs ~40GB RAM. If your laptop has 16GB, use the small variants
(`llama3.2:3b`, `glm-4-9b`, `qwen2.5:7b`) — every lab's *mechanics* work on a
small model.

The seven model-facing lessons were run against two sizes on 4 CPUs with no
GPU, on weights pulled from Kaggle Models. Each of them calls the model from
inside its **skill's own script** — there is no adapter in a lesson — so what is
being tested here is the same file `scripts/test_skills.py` runs offline. The
difference between the sizes is worth knowing before you pick:

| | reached the model | acceptance property held |
|---|---|---|
| Qwen2.5-**1.5B**-Instruct | 7/7 | **5/7** — B2.9 and C1.1 fail |
| Qwen2.5-**7B**-Instruct | 7/7 | **7/7** |

At 1.5B, B2.9 hands back the SQL injection unfixed and C1.1 ranks TLS 1.0 above
an unauthenticated endpoint. Both clear at 7B. So **7B is the floor for the
acceptance criteria**; below it the lessons still run and still teach, but two
of them will not hit their numbers.

The exception is the one worth reading: **B2.0 holds at 1.5B**, on the same SQL
task B2.9 fails at that size — because it asks for one line and checks the
answer with an independent verifier rather than asking for a corrected function
and trusting what comes back. Full transcripts in
[`labs/notebooks/_live_model.json`](labs/notebooks/_live_model.json) and the
write-up in [`labs/tools/EVIDENCE.md`](labs/tools/EVIDENCE.md).

**[llama.cpp](https://github.com/ggml-org/llama.cpp)** if you want GGUF control:

```bash
llama-server -hf unsloth/GLM-4.6-GGUF --port 11434 -c 8192
```

### Weights from Kaggle, if you already have a Kaggle account

Kaggle hosts the open-weight families as **Models**, including GGUF builds, and
the API will serve a single file rather than the whole instance — which matters,
because a GGUF instance bundles every quantisation and the Qwen2.5-1.5B one is
13 GB for what you actually want at 1.1 GB.

```bash
# list what a family ships, with sizes
curl -sH "authorization: Bearer $KAGGLE_KEY" \
  https://www.kaggle.com/api/v1/models/qwen-lm/qwen2.5/gguf/1.5b-instruct/1/files

# pull exactly one quantisation
curl -sSL -H "authorization: Bearer $KAGGLE_KEY" -o qwen2.5-1.5b-instruct-q4_k_m.gguf \
  https://www.kaggle.com/api/v1/models/qwen-lm/qwen2.5/gguf/1.5b-instruct/1/download/qwen2.5-1.5b-instruct-q4_k_m.gguf

# serve it OpenAI-compatibly, CPU only
python3 -m llama_cpp.server --model qwen2.5-1.5b-instruct-q4_k_m.gguf --port 11434
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=none MODEL=qwen2.5-1.5b-instruct
```

The `framework` segment is lower-case in the API path (`gguf`) and capitalised
in the web URL (`Gguf`); the API returns 404 for the capitalised form, which
reads like the model does not exist.

For 7B — the size the acceptance criteria need — the q4_k_m build is **split
across two shards**. Download both, then point llama.cpp at the first; it opens
the rest itself:

```bash
for p in 1 2; do
  curl -sSL -H "authorization: Bearer $KAGGLE_KEY" \
    -o qwen2.5-7b-instruct-q4_k_m-0000$p-of-00002.gguf \
    https://www.kaggle.com/api/v1/models/qwen-lm/qwen2.5/gguf/7b-instruct/1/download/qwen2.5-7b-instruct-q4_k_m-0000$p-of-00002.gguf
done
python3 -m llama_cpp.server --model qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf \
  --model_alias qwen2.5-7b-instruct --port 11434 --n_ctx 4096 --chat_format qwen
```

`--chat_format qwen` matters: without it the server falls back to a generic
template and the model's answers arrive wrapped in prose the lessons' checks
do not expect.

## Option 2 — Free hosted tiers (when your laptop can't hold it)

Several providers host **open-weight** models on rate-limited free tiers. They
are OpenAI-compatible, so only the two env vars change:

```bash
export OPENAI_BASE_URL=https://<provider>/v1
export OPENAI_API_KEY=<your-free-key>
export MODEL=<their-id-for-llama-or-glm-or-kimi>
```

Places that have offered free access to open-weight models (verify current
limits — they move):

- **OpenRouter** — aggregates many providers; some open models are exposed with
  a `:free` suffix on a shared rate limit. One key, many models — handy for the
  C2.6 multi-backbone benchmarking lab.
- **Groq / Cerebras** — very fast inference for Llama-family models on a free
  developer tier.
- **Together AI** — free credits and some always-free open endpoints.
- **Z.ai** — first-party GLM access, including lighter GLM variants on a free tier.
- **Moonshot** — first-party Kimi access with starter credits.
- **Hugging Face** — weights for all three families are downloadable free, and
  Inference Providers give a small monthly credit allowance.

**Rate limits are a feature here.** The labs are built around small corpora
(30–50 files) precisely so a free tier can finish them.

## Option 3 — Self-host for a class or a team

One borrowed GPU serves a whole cohort:

```bash
pip install vllm
vllm serve zai-org/GLM-4.6 --port 8000 --api-key commons
export OPENAI_BASE_URL=http://your-host:8000/v1 OPENAI_API_KEY=commons MODEL=zai-org/GLM-4.6
```

Put **[LiteLLM](https://github.com/BerriAI/litellm)** in front to give everyone
one endpoint, per-user keys and spend attribution. `labs/tools/litellm-gateway/`
stands one up and tests what it does and does not enforce — the model allow-list
holds on a config file alone; the key checks need the database:

```bash
pip install 'litellm[proxy]'
litellm --config labs/shared/litellm.config.yaml   # routes llama/glm/kimi behind one URL
```

---

## Which model for which lab

Two columns, because the honest answer depends on what you already have. The
open-weight column is what the lab was designed against; the frontier column is
what to reach for if you have a key and want the ceiling.

| Lab type | Open weight | Frontier | Why |
|---|---|---|---|
| Code review / SAST triage (B1) | **GLM-4.6** | Claude Sonnet 5 | strongest code reasoning per unit of RAM |
| Harness loops, tool use (B2) | **Kimi K2** | Claude Sonnet 5 | built for agentic tool sequences |
| Offensive planning (C1) | **Kimi K2** or GLM-4.6 | Claude Sonnet 5 | multi-step planning |
| Guardrails / classification | **Llama Guard** | Claude Haiku 4.5 | purpose-built, and cheap at volume |
| SOC triage (D1) | **GLM-4.6** or Llama 3.3 | Claude Haiku 4.5 | cheap, high volume |
| Exploit chaining, research (B2.8, C2) | Kimi K2 | Claude Opus 5 | multi-file adversarial reasoning |
| Multi-backbone benchmarking (C2.6) | **all three** | any | separating model effects from harness effects *is* the lab |

Start with **Claude Haiku 4.5** on the frontier side. It is the cheapest current
Claude model, it is what `MODEL` defaults to, and for most of these lessons the
difference a larger model makes is smaller than the difference a better prompt
makes.

Nine lessons carry a live section that calls a real model through the adapter.
To run them all against a backend and record what came back:

```bash
python3 scripts/live_model_test.py --backend frontier --save
python3 scripts/live_model_test.py --backend open-weight --model glm-4.6 --save
```

## A note on "open"

These are **open-weight**, not all strictly OSI-open-source. Kimi K2 (modified
MIT) and GLM (MIT) are permissive; Llama ships under Meta's community licence
with use restrictions. For the control plane we deliberately use **CNCF and
Linux Foundation** projects (SPIFFE/SPIRE, OPA, Falco, Kyverno, Cilium,
OpenTelemetry, Keycloak, Sigstore, in-toto, kagent, kmcp, agentgateway) —
genuinely open governance, no vendor lock, and the thing you'd actually deploy.

If a lab ever *requires* a closed model to pass, that's a bug in the lab —
the frontier path is an option, and `live_model_test.py` runs the same
assertions on both sides. [Open an issue](../../issues).
