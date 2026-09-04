"""One model adapter, emitted into every lesson that involves a model.

The commons runs offline against deterministic replays, which is what lets a
notebook execute on a Kaggle kernel with the internet switched off and what
makes the determinism gate meaningful. That property is kept. What is added
here is one — and only one — way to run exactly the same lesson for real:

    offline (default)   a deterministic replay, labelled as a replay everywhere
    open weight         a Kaggle model, served through any OpenAI-compatible
                        server (llama.cpp, vLLM, Ollama)

There is no frontier path. It was removed deliberately: a curriculum that is
free to run should not have a backend that requires a paid account, and the
open-weight route is the one every result in this repository was actually
established on. `MODELS.md` has the Kaggle download and the serving command.

Three rules the adapter follows, because each is a way this kind of code
usually goes wrong:

* **It never prints a key**, and it never writes one anywhere.
* **It never silently substitutes.** If a backend is configured and the call
  fails, it says so, loudly, and then uses the replay — labelled as a replay.
  A lesson that quietly falls back is a lesson that reports a model's answer
  when no model answered.
* **It is standard library only.** `urllib.request` and `json`, so the
  self-contained property survives.
"""

# The block emitted verbatim into any lesson carrying a ("model", ...) step.
MODEL_RUNTIME = '''# --- model backend: replay by default, a Kaggle open-weight model when served -
# One URL and one header shape, no vendor SDK. Standard library only, so the
# notebook stays self-contained.
import json, os, urllib.error, urllib.request

# Qwen2.5-7B-Instruct is the floor established in MODELS.md: below it two of
# the lessons' acceptance properties stop holding.
OPEN_WEIGHT_DEFAULT = "qwen2.5-7b-instruct"
TIMEOUT = 60

def backend():
    """(kind, model). Configuration comes from the environment, never a literal."""
    if os.environ.get("OPENAI_BASE_URL"):
        return "open-weight", os.environ.get("MODEL", OPEN_WEIGHT_DEFAULT)
    return "replay", "deterministic stand-in (no backend configured)"

def _post(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())

def _openai_compatible(prompt, system, model, max_tokens, temperature):
    msgs = ([{"role": "system", "content": system}] if system else []) + \\
           [{"role": "user", "content": prompt}]
    base = os.environ["OPENAI_BASE_URL"].rstrip("/")
    key = os.environ.get("OPENAI_API_KEY", "not-needed")
    out = _post(f"{base}/chat/completions",
                {"model": model, "messages": msgs, "max_tokens": max_tokens,
                 "temperature": temperature},
                {"authorization": f"Bearer {key}"})
    return out["choices"][0]["message"]["content"].strip()

def ask(prompt, *, replay, system=None, max_tokens=512, temperature=0.0):
    """Answer `prompt` with the configured backend, or return `replay`.

    `replay` is required, not optional: a lesson must be able to run offline,
    and the answer it falls back to has to be visible in the source rather than
    invented at runtime.
    """
    kind, model = backend()
    if kind == "replay":
        return replay, kind, model
    try:
        return _openai_compatible(prompt, system, model, max_tokens,
                                  temperature), kind, model
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as e:
        # Print what the server actually said. "failed: 400" costs whoever hits
        # this an hour; the body usually names the exact missing parameter, and
        # it never contains a key.
        detail = getattr(e, "code", None) or type(e).__name__
        why = ""
        if hasattr(e, "read"):
            try:
                why = json.loads(e.read().decode()).get("error", {}).get("message", "")
            except Exception:
                why = ""
        print(f"   !! {kind} backend ({model}) failed: {detail}"
              f"{' - ' + why if why else ''}")
        print("      Using the replay, which is labelled as one. No model answered.")
        return replay, "replay", f"{model} unreachable"

_kind, _model = backend()
print(f"model backend : {_kind}")
print(f"model         : {_model}")
if _kind == "replay":
    print()
    print("This lesson runs offline against a deterministic replay, which is why")
    print("it works on a Kaggle kernel with the internet switched off. To run the")
    print("identical code against a real model, serve an open-weight model from")
    print("Kaggle Models and point the adapter at it:")
    print()
    print("   python3 -m llama_cpp.server --model <the .gguf from Kaggle> \\\\")
    print("           --model_alias qwen2.5-7b-instruct --port 11434 --chat_format qwen")
    print("   export OPENAI_BASE_URL=http://127.0.0.1:11434/v1 \\\\")
    print("          MODEL=qwen2.5-7b-instruct")
    print()
    print("   MODELS.md has the exact Kaggle download. There is no paid backend:")
    print("   every model result in this repository was produced this way.")
'''

# The section appended to a model lesson: the same task, run for real.
LIVE_MD = """## 2 · The same lesson, against a real model

Everything below this point runs identically on two backends. Offline it uses a
deterministic replay that is labelled as a replay wherever it appears — never
presented as a model's output. With `OPENAI_BASE_URL` set it calls an
OpenAI-compatible server, which is how the open-weight models on Kaggle are
served — and how every model result in this repository was produced.

The point of running it both ways is not that the answers match. It is that
**the lesson's assertion holds either way** — if it only holds against the
replay, the lesson was testing the replay."""


def live_cell(task: str, replay: str, system: str | None, check: str) -> str:
    """The per-lesson live round-trip, as a code cell.

    `check` is a (label, expression) pair describing the property the lesson
    cares about. It is *reported*, not asserted: a model failing to name a CWE
    is a finding about the model, not a broken notebook. The only hard
    assertions are the two that must hold on every backend — an answer came
    back, and offline it is the replay the source shows you.
    """
    sys_arg = f"\n            system={system!r}," if system else ""
    return f'''TASK = {task!r}

REPLAY = {replay!r}

answer, used, model = ask(TASK, replay=REPLAY,{sys_arg}
            max_tokens=300)

print(f"backend used : {{used}}")
print(f"model        : {{model}}")
print(f"prompt       : {{TASK[:66]}}...")
print()
print("answer:")
for line in (answer.splitlines() or [answer]):
    print(f"   {{line}}")

# Two assertions that must hold on every backend, and one property that is
# reported rather than asserted - a real model failing it is a finding about
# the model, not a broken notebook.
assert answer.strip(), "the configured backend returned nothing"
if used == "replay":
    assert answer == REPLAY, "the offline path must return the replay verbatim"

label, held = {check}
print()
print(f"property checked : {{label}}")
print(f"held on {{used:12s}} : {{held}}")
print()
print("Same code, same assertions, two possible backends. Offline the answer is")
print("the replay and is labelled as one; with a served model it is the model's.")
'''
