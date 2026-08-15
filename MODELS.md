# Getting the models — free, open-weight, no frontier-lab account

Every lab in Cyber Commons is designed to reach its acceptance criteria on
**open-weight models you can download or call for free**. Commercial frontier
models are named where relevant but **never required**. This is what keeps the
commons usable by a two-person NGO and a global bank alike.

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

**Sizing honestly:** a 70B model at 4-bit needs ~40GB RAM. If your laptop has
16GB, use the small variants (`llama3.2:3b`, `glm-4-9b`, `qwen2.5:7b`) — every
lab's *mechanics* work on a small model. Where a lab genuinely needs a bigger
model to hit its acceptance number, the lab README says so and gives you the
hosted fallback below.

**[llama.cpp](https://github.com/ggml-org/llama.cpp)** if you want GGUF control:

```bash
llama-server -hf unsloth/GLM-4.6-GGUF --port 11434 -c 8192
```

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
one endpoint, per-user keys and spend attribution (used directly in labs A1.7
and B2.5, where routing is itself the security topic):

```bash
pip install 'litellm[proxy]'
litellm --config labs/shared/litellm.config.yaml   # routes llama/glm/kimi behind one URL
```

---

## Which model for which lab

| Lab type | Recommended | Why |
|----------|-------------|-----|
| Code review / SAST triage (B1) | **GLM-4.6** | strongest code reasoning per unit of RAM |
| Harness loops, tool use (B2, M0) | **Kimi K2** | built for agentic tool sequences |
| Offensive planning (C1) | **Kimi K2** or GLM-4.6 | multi-step planning |
| Guardrails / classification (B2.3, E1.6) | **Llama Guard** | purpose-built safety classifier |
| SOC triage (D1) | **GLM-4.6** or Llama 3.3 | cheap, high volume |
| Multi-backbone benchmarking (C2.6) | **all three** | separating model effects from harness effects *is* the lab |

## A note on "open"

These are **open-weight**, not all strictly OSI-open-source. Kimi K2 (modified
MIT) and GLM (MIT) are permissive; Llama ships under Meta's community licence
with use restrictions. For the control plane we deliberately use **CNCF and
Linux Foundation** projects (SPIFFE/SPIRE, OPA, Falco, Kyverno, Cilium,
OpenTelemetry, Keycloak, Sigstore, in-toto, kagent, kmcp, agentgateway) —
genuinely open governance, no vendor lock, and the thing you'd actually deploy.

If a lab ever *requires* a closed model to pass, that's a bug in the lab.
[Open an issue](../../issues).
