# Running the skills against a Kimi model on Kaggle

What actually happened when the AppSec skills were pointed at a Kimi-family
model on Kaggle, including the parts that did not work. Every number here came
from a run; nothing is estimated.

## The short version

**A Kimi-family model runs on a Kaggle CPU kernel, and it did not follow the
skill.** Not because the skill is wrong — because the only Kimi-family model
reachable from this account is a **base** model, and base models complete text
rather than obey instructions.

## What is reachable, and what is not

| Path | Result |
|---|---|
| Kaggle **GPU** | **Unavailable.** `enableGpu: true` and `acceleratorType: nvidiaTeslaT4` are both *stored* by the API, and the kernel still comes up on `torch 2.10.0+cpu` with `cuda_available False`. |
| Kaggle **internet** | **Unavailable.** `enableInternet: true` is stored; DNS fails inside the kernel (`Temporary failure in name resolution`), so nothing can be fetched from HuggingFace. |
| Kaggle **Models** | **Works.** Model data sources mount read-only at `/kaggle/input` with no internet, which is the only way weights get in. |
| Downloading weights locally | **Impractical here.** ~140 KiB/s to HuggingFace, and parallel range requests share that budget rather than multiplying it — about 20 hours for a 9.8 GiB quantised model. |

Both Kaggle limits are the account's phone-verification gate. Note that unlike
the public-notebook case, which fails loudly with
`403 Phone verification is required`, **these two fail silently**: the setting
is accepted, stored, and then not honoured at run time. Code that trusts the
stored value will believe it has a GPU.

## Which Kimi model, and why

Kaggle hosts `helium990/kimi-k3` (2.78T MoE) and
`manojkumarcs28/moonlight-16b-series`. Kimi K2 and K3 are 1T and 2.78T
parameters and cannot run on a CPU kernel at any quantisation, so the only
candidate is **Moonlight-16B-A3B** — Moonshot AI's open-weight MoE from the
Kimi team, 16B total with **3B active**. The MoE ratio is exactly what makes
CPU inference arithmetically possible.

It loads, and that is not obvious: 29.73 GiB of bf16 weights into a kernel with
31 GiB of RAM.

```
model_type: deepseek_v3 | had auto_map: True
loaded with the native DeepseekV3 implementation
model loaded in 87s
parameters: 16.0B
```

Three things had to be true for that to work, each found by a failed run:

1. **The mount is named `Moonlight 16B`, with a space.** That is not a valid
   Python module name, so `trust_remote_code` cannot import the bundled
   modelling code from it. Symlink to a path without a space — do not copy,
   the weights are larger than `/kaggle/working`.
2. **The bundled `modeling_deepseek.py` targets transformers 4.x.** It imports
   `is_torch_fx_available`, which v5 removed. Transformers 5 ships DeepseekV3
   natively, so dropping `auto_map` from a local copy of `config.json` is
   cleaner than patching the vendored code.
3. **The custom tokenizer breaks `tokenizer(...)`.** It returns no
   `attention_mask`, so the padding path sees `None`. Encode with
   `tok.encode()` and build the tensors directly.

## The result

Prompted as a chat model with the `appsec-vuln-audit` skill and a vulnerable
file, it produced no JSON at all. It continued the *pattern of the input* —
inventing more vulnerable handlers in the same shape:

```
def run_import(request):
    fmt = request.args["fmt"]
    os.system("importer --format " + fmt)         # sink: subprocess
```

`=== DOES THE MODEL'S OUTPUT SATISFY THE SKILL CONTRACT? === no JSON object in
the output`

That is textbook base-model behaviour, and the uploaded instance is indeed the
base checkpoint: its own documentation says *"the default configuration loads
Moonlight-16B-A3B; to use the chat-optimized model, change the model path to
Moonlight-16B-A3B-Instruct"* — but only the base weights are in the instance
(29.73 GiB is one model, not two).

Full output: [`moonlight-16b-chat-prompt.txt`](moonlight-16b-chat-prompt.txt).

## Speed, and what it costs

```
prompt tokens: 831
GENERATED 256 tokens in 4269s (0.06 tok/s)
TOTAL 4383s
```

**0.06 tokens per second.** Roughly one token every seventeen seconds. A short
answer takes an hour, so a Kaggle CPU kernel is a place to prove a model
*loads and runs*, not a place to evaluate one. Any real evaluation of these
skills against Kimi needs either a GPU (a phone-verified Kaggle account, or
anywhere else) or a hosted endpoint.

## Reproducing it

The scripts are not committed, because they carry no lesson content and would
be dead weight in the curriculum. The three fixes above are the whole trick,
and the mount reference is:

```
manojkumarcs28/moonlight-16b-series/pyTorch/moonlight-16b-a3b/1
```

Credentials come from `~/.kaggle/kaggle.json` and never from this repository.
