#!/usr/bin/env python3
"""Run a plan-act-verify loop with a real model in it, and show what the loop accepts when nothing independent checks the answer.

This is the executable half of the `agentic-harness-loop` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# --- model backend: replay by default, a Kaggle open-weight model when served -
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
    msgs = ([{"role": "system", "content": system}] if system else []) + \
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
    print("   python3 -m llama_cpp.server --model <the .gguf from Kaggle> \\")
    print("           --model_alias qwen2.5-7b-instruct --port 11434 --chat_format qwen")
    print("   export OPENAI_BASE_URL=http://127.0.0.1:11434/v1 \\")
    print("          MODEL=qwen2.5-7b-instruct")
    print()
    print("   MODELS.md has the exact Kaggle download. There is no paid backend:")
    print("   every model result in this repository was produced this way.")


FINDING = """
def load_booking(ref, owner):
    return DB.execute("SELECT * FROM bookings WHERE ref=" + ref)
"""

def plan(task, feedback):
    """PLAN - the model proposes the corrected line.

    Note what the prompt does NOT do: offer a way out. An earlier version of
    this cell let the model reply DONE, and a real model replied DONE on the
    first turn every time. A loop whose exit is easier than the work exits.
    """
    prompt = f"{task}\n\nCode:\n{FINDING}\n"
    if feedback:
        prompt += f"Your previous attempt was rejected: {feedback}\n"
    prompt += "Reply with ONLY the corrected line of code."
    answer, used, _ = ask(
        prompt,
        replay='return DB.execute("SELECT * FROM bookings WHERE ref=?", (ref,))',
        system="You fix security defects. One line of code, no prose, no fences.",
        max_tokens=120)
    # Parsing is the harness's job, not the model's favour. Asked for one
    # line, a 7B model returns the whole function and a frontier model returns
    # a fenced block; both are reasonable readings of the request. Take the
    # line that actually calls the sink.
    lines = [ln.strip() for ln in answer.strip().splitlines()
             if ln.strip() and not ln.strip().startswith("```")]
    sink = [ln for ln in lines if "execute" in ln]
    return ((sink or lines or [""])[0]), used

def act(proposal):
    """ACT - the harness applies it. Here, that is recording what it would do."""
    return {"would_write": proposal}

PLACEHOLDERS = ("?", "%s", ":ref", "$1")

def parameterised(code):
    """VERIFY - independent. Does the line actually use a placeholder?

    The tuple matters more than it looks. An earlier version accepted only "?"
    and a real model returned a perfectly correct psycopg fix using "%s" - so
    the verifier rejected correct work three times and burned the whole budget.
    A verifier that is too narrow does not fail safe; it fails expensively, and
    it looks exactly like a model that cannot do the task.
    """
    after = code.split("execute", 1)[-1]
    return any(p in after for p in PLACEHOLDERS) and "+" not in after

def loop(task, verifier=None, max_steps=3):
    """PLAN -> ACT -> VERIFY -> STOP, with the rejection fed back in."""
    feedback, log, used = "", [], "?"
    for step in range(1, max_steps + 1):              # STOP: the budget
        proposal, used = plan(task, feedback)         # PLAN
        act(proposal)                                 # ACT
        log.append((step, proposal[:70]))
        if verifier is None:                          # no VERIFY: accept it
            return {"ok": None, "steps": step, "answer": proposal,
                    "backend": used, "log": log}
        if verifier(proposal):                        # VERIFY
            return {"ok": True, "steps": step, "answer": proposal,
                    "backend": used, "log": log}
        feedback = "it still concatenates the input into the SQL string"
    return {"ok": False, "steps": max_steps,
            "answer": log[-1][1] if log else None, "backend": used, "log": log}

TASK = "Rewrite the one vulnerable line so the query is parameterised."
print("the loop, wired:", ["plan", "act", "verify", "stop"])

no_check = loop(TASK, verifier=None)
print(f"backend  : {no_check['backend']}")
print(f"steps    : {no_check['steps']}")
print(f"accepted : {no_check['answer']}")
print(f"verified : {no_check['ok']}   <- nothing checked it")
print()
print("The loop stopped because the model produced something, which is not the")
print("same as producing something correct. Whatever came back was accepted.")

checked = loop(TASK, verifier=parameterised)
print(f"accepted : {checked['answer']}")
print(f"verified : {checked['ok']}   <- an independent check said so")
print(f"steps    : {checked['steps']}")

# Two ways a verifier is wrong, and only one of them is loud.
NARROW = lambda c: "?" in c.split("execute", 1)[-1] and "+" not in c
PSYCOPG = 'return DB.execute("SELECT * FROM bookings WHERE ref=%s", (ref,))'
print(f"\na correct psycopg fix: {PSYCOPG}")
print(f"   narrow verifier (only '?') : "
      f"{'accepts' if NARROW(PSYCOPG) else 'REJECTS a correct fix'}")
print(f"   this lesson's verifier     : "
      f"{'accepts' if parameterised(PSYCOPG) else 'rejects'}")

# And the case that matters: a plausible answer that is still vulnerable.
BAD = 'return DB.execute("SELECT * FROM bookings WHERE ref=" + escape(ref))'
print(f"\na plausible-looking answer: {BAD}")
print(f"   would the verifier accept it? {parameterised(BAD)}")
print()
print("It reads like a fix and it is still concatenation. Without the verifier")
print("this loop ships it, reports success, and the trace looks clean.")
assert not parameterised(BAD) and parameterised(PSYCOPG) and not NARROW(PSYCOPG)
