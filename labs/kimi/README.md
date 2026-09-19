# Running the skills against a Kimi-family model on a CPU

What actually happened when the AppSec skills were pointed at a Kimi-family
open-weight model with no GPU, including the parts that did not work. Every
number here came from a run; nothing is estimated.

> **Provenance, stated once.** This run predates the move to local-only
> execution and happened on a free hosted CPU notebook — 4 cores, 31 GiB RAM, no
> accelerator. That is recorded because the timings only make sense against it,
> not because it is a route this commons offers. Everything the curriculum runs
> today runs on your own machine; see [MODELS.md](../../MODELS.md).

## The short version

**A Kimi-family model runs on a CPU with 31 GiB of RAM.** Prompted as a chat
model it ignored the skill entirely, because the only Kimi-family model within
reach is a **base** model and base models complete text rather than obey
instructions. Prompted as a base model — priming the output shape — it produced
**contract-conforming output that is substantively wrong**: the right JSON, the
wrong CWE, and the contract's own type placeholders copied in as values. That
second result is now teaching material in C2.5.

## Which Kimi model, and why

Kimi K2 and K3 are 1T and 2.78T parameters and cannot run on a CPU at any
quantisation, so the only candidate is **Moonlight-16B-A3B** — Moonshot AI's
open-weight MoE from the Kimi team, 16B total with **3B active**. The MoE ratio
is exactly what makes CPU inference arithmetically possible.

It loads, and that is not obvious: 29.73 GiB of bf16 weights into 31 GiB of RAM.

```
model_type: deepseek_v3 | had auto_map: True
loaded with the native DeepseekV3 implementation
model loaded in 87s
parameters: 16.0B
```

Three things had to be true for that to work, each found by a failed run, and
all three will bite anyone loading these weights anywhere:

1. **The weights directory was named `Moonlight 16B`, with a space.** That is
   not a valid Python module name, so `trust_remote_code` cannot import the
   bundled modelling code from it. Symlink to a path without a space — do not
   copy, the weights are larger than most scratch volumes.
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

That is textbook base-model behaviour, and the instance is indeed the base
checkpoint: its own documentation says *"the default configuration loads
Moonlight-16B-A3B; to use the chat-optimized model, change the model path to
Moonlight-16B-A3B-Instruct"* — but only the base weights are present (29.73 GiB
is one model, not two).

Full output: [`moonlight-16b-chat-prompt.txt`](moonlight-16b-chat-prompt.txt).

## Second run: prompted the way a base model is meant to be used

A base model completes; it does not obey. So the fair test primes the shape and
lets it continue — the contract, the two vulnerable functions, and an opening
`{"findings": [{"id": "F-01", "cwe": "`.

**It worked, and the result is the most useful thing in this whole exercise.**

```json
{"findings": [{"id": "F-01", "cwe": "CWE-89", "file": "report_api.py",
"line": 22, "unit": "get_report",
"evidence": "open('/var/reports/' + request.args['name'])",
"missing_control": "str", "occurrences": 1, "verdict": "confirmed",
"verdict_reason": "str", "feasible": true, "confidence": 0.0}],
"dropped": [], "counts": {"raw": 0, "deduped": 0, "verified": 0, "feasible": 0}}
```

Checked against `appsec-vuln-audit`'s output contract: **zero problems.** Every
required field present, every type correct.

Now read it:

1. **The CWE is wrong.** `open()` on a caller-supplied path is **CWE-22**, path
   traversal — not CWE-89, SQL injection. There is no query here. It gave the
   second sink, `os.system()`, CWE-89 as well; that one is **CWE-78**.
2. **`missing_control` and `verdict_reason` are the literal string `"str"`.**
   The model copied the contract's *type placeholder* into the value. A schema
   requiring a string is perfectly satisfied by the word `str`.
3. **`counts` says zero findings** while the findings array holds one.

Three defects, zero schema violations. This is **conformance ≠ accuracy** —
the thesis the curriculum keeps asserting — demonstrated by a real open-weight
model on real hardware rather than by a constructed example. It is now the
closing section of
[C2.5](https://cybercommons.ai/lessons/C2.5.html), quoted verbatim.

Worth noting which invariant catches it. Monotonicity passes: `[0,0,0,0]` is
non-increasing. The check that fires is `counts.verified == len(findings)`, and
it costs one comparison.

Full output:
[`moonlight-16b-completion-prompt.txt`](moonlight-16b-completion-prompt.txt).

## Speed, and what it costs

```
GENERATED 256 tokens in 4269s (0.06  tok/s)    # chat-style, 831-token prompt
GENERATED 200 tokens in 1274s (0.157 tok/s)    # completion-style, 305-token prompt
```

**0.06 to 0.16 tokens per second**, depending on how much context it carries —
between six and seventeen seconds per token. Either way a short answer takes 20
to 70 minutes, so a CPU at this size is a place to prove a model *loads and
runs*, not a place to evaluate one. Any real evaluation of these skills against
Kimi needs a GPU or a hosted endpoint.

That is the reason the commons standardises on **Qwen2.5-7B-Instruct** for the
acceptance criteria: it is the largest model that answers in seconds rather than
hours on the hardware most readers have.

## Reproducing it

The scripts are not committed, because they carry no lesson content and would be
dead weight in the curriculum. The three fixes above are the whole trick, and
the weights are `moonshotai/Moonlight-16B-A3B` on Hugging Face.
