"""One model adapter, emitted into every lesson that involves a model.

The commons has always run offline against deterministic replays, which is what
lets a notebook execute on a Kaggle kernel with the internet switched off and
what makes the determinism gate meaningful. That property is kept. What is added
here is a second and third way to run exactly the same lesson:

    offline (default)   a deterministic replay, labelled as a replay everywhere
    open weight         any OpenAI-compatible endpoint — Ollama, vLLM, a hosted
                        open-weight provider
    frontier            the Anthropic Messages API

The default is the replay, so nothing about CI, determinism or the offline
Kaggle run changes. The other two are opt-in through environment variables and
are never configured in CI.

Three rules the adapter follows, because each of them is a way this kind of
code usually goes wrong:

* **It never prints a key**, and it never writes one anywhere.
* **It never silently substitutes.** If a backend is configured and the call
  fails, it says so, loudly, and then uses the replay — labelled as a replay.
  A lesson that quietly falls back is a lesson that reports a model's answer
  when no model answered.
* **It is standard library only.** `urllib.request` and `json`, so the
  self-contained property survives.
"""

# The block emitted verbatim into any lesson carrying a ("model", ...) step.
MODEL_RUNTIME = '''# --- model backend: replay by default, real model when you configure one ----
# Nothing here is Anthropic- or vendor-specific beyond one URL and one header
# shape. Standard library only, so the notebook stays self-contained.
import json, os, urllib.error, urllib.request

# The cheapest current model on each side, which is what a lesson needs.
FRONTIER_DEFAULT   = "claude-haiku-4-5-20251001"
OPEN_WEIGHT_DEFAULT = "glm-4.6"
TIMEOUT = 60

def _kaggle_secret(name):
    """On Kaggle, a key lives in Add-ons -> Secrets rather than the environment.

    kaggle_secrets is pre-installed in the Kaggle image and absent everywhere
    else, so the import is guarded and the notebook needs no dependency. It also
    requires the notebook to have internet enabled, which on Kaggle requires a
    phone-verified account - see the note printed below.
    """
    try:
        from kaggle_secrets import UserSecretsClient
        return UserSecretsClient().get_secret(name)
    except Exception:
        return None

def backend():
    """(kind, model). Configuration comes from the environment, never a literal."""
    if os.environ.get("ANTHROPIC_API_KEY") or _kaggle_secret("ANTHROPIC_API_KEY"):
        os.environ.setdefault("ANTHROPIC_API_KEY",
                              os.environ.get("ANTHROPIC_API_KEY")
                              or _kaggle_secret("ANTHROPIC_API_KEY") or "")
        return "frontier", os.environ.get("MODEL", FRONTIER_DEFAULT)
    if os.environ.get("OPENAI_BASE_URL"):
        return "open-weight", os.environ.get("MODEL", OPEN_WEIGHT_DEFAULT)
    return "replay", "deterministic stand-in (no backend configured)"

def _post(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())

def _anthropic(prompt, system, model, max_tokens, temperature):
    body = {"model": model, "max_tokens": max_tokens, "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    headers = {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
               "anthropic-version": "2023-06-01"}
    # An identity-linked key is scoped to a workspace and the API refuses the
    # call without being told which one. A plain organisation key needs nothing
    # here, so the header is only sent when it is set.
    ws = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    if ws:
        headers["anthropic-workspace-id"] = ws
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    out = _post(f"{base}/v1/messages", body, headers)
    return "".join(b.get("text", "") for b in out.get("content", [])).strip()

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
        fn = _anthropic if kind == "frontier" else _openai_compatible
        return fn(prompt, system, model, max_tokens, temperature), kind, model
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as e:
        # Print what the API actually said. "failed: 400" costs whoever hits
        # this an hour; the body usually names the exact missing header or
        # parameter, and it never contains the key.
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
    print("identical code against a real model, set one of:")
    print()
    print("   frontier     export ANTHROPIC_API_KEY=...   # cheapest: " + FRONTIER_DEFAULT)
    print("                (an identity-linked key also needs")
    print("                 ANTHROPIC_WORKSPACE_ID=...)")
    print("   open weight  export OPENAI_BASE_URL=http://localhost:11434/v1 \\\\")
    print("                       OPENAI_API_KEY=ollama MODEL=glm-4.6")
    print()
    print("   On Kaggle: Add-ons -> Secrets, add ANTHROPIC_API_KEY, and switch")
    print("   Internet on in the notebook settings. Internet requires a")
    print("   phone-verified Kaggle account; without it DNS fails in the kernel")
    print("   and this lesson correctly stays on the replay.")
'''

# The section appended to a model lesson: the same task, run for real.
LIVE_MD = """## 2 · The same lesson, against a real model

Everything below this point runs identically on three backends. Offline it uses
a deterministic replay that is labelled as a replay wherever it appears — never
presented as a model's output. With `ANTHROPIC_API_KEY` set it calls a frontier
model; with `OPENAI_BASE_URL` set it calls any OpenAI-compatible endpoint,
which covers Ollama, vLLM and the hosted open-weight providers.

The point of running it both ways is not that the answers match. It is that
**the lesson's assertion holds either way** — if it only holds against the
replay, the lesson was testing the replay."""


def live_cell(task: str, replay: str, system: str | None, check: str) -> str:
    """The per-lesson live round-trip, as a code cell.

    `check` is a (label, expression) pair describing the property the lesson
    cares about. It is *reported*, not asserted: a frontier model failing to
    name a CWE is a finding about the model, not a broken notebook. The only
    hard assertions are the two that must hold on every backend — an answer
    came back, and offline it is the replay the source shows you.
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
print("Same code, same assertions, three possible backends. Offline the answer")
print("is the replay and is labelled as one; with a key it is the model's.")
'''
