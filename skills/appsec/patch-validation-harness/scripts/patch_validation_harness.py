#!/usr/bin/env python3
"""Accept a patch only when behaviour is unchanged, the exploit stops working, and the fix is proved against the old build.

This is the executable half of the `patch-validation-harness` skill: the check the
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


import re, sqlite3

VULNERABLE = '''
def get_user(conn, name):
    return conn.execute("SELECT id, name FROM users WHERE name = '" + name + "'").fetchall()
'''

def build_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users(id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?,?)",
                     [(1,"dana"),(2,"sam"),(3,"o'brien")])
    return conn

def load(src):
    ns = {}; exec(compile(src, "<patch>", "exec"), ns); return ns["get_user"]

BEHAVIOUR = [("dana",[(1,"dana")]), ("sam",[(2,"sam")]),
             ("nobody",[]), ("o'brien",[(3,"o'brien")])]

def behaviour_ok(fn):
    conn = build_db(); rows = []
    for name, expected in BEHAVIOUR:
        try: got = fn(conn, name)
        except Exception as e: rows.append((name, f"raised {type(e).__name__}", False)); continue
        rows.append((name, got, got == expected))
    return rows

def exploit_works(fn):
    """The stage-12 probe, reused as the acceptance test."""
    conn = build_db()
    try: rows = fn(conn, "x' OR '1'='1")
    except Exception: return False, "probe raised — not exploitable this way"
    return len(rows) > 1, f"probe returned {len(rows)} rows"

def scanner_fires(src):
    return bool(re.search(r"execute\(\s*[\"\'][^\"\']*[\"\']\s*\+", src))

fn = load(VULNERABLE)
print("behaviour of the vulnerable build:")
for name, got, ok in behaviour_ok(fn):
    print(f"   get_user({name!r:10s}) → {str(got):18s} {'ok' if ok else 'FAILS'}")
ex, why = exploit_works(fn)
print(f"\nexploit works: {ex} — {why}")
print(f"scanner fires: {scanner_fires(VULNERABLE)}")

CANDIDATES = {
 "A · parameterise (the real fix)": '''
def get_user(conn, name):
    return conn.execute("SELECT id, name FROM users WHERE name = ?", (name,)).fetchall()
''',
 "B · delete the feature": '''
def get_user(conn, name):
    return []
''',
 "C · evade the scanner": '''
def get_user(conn, name):
    q = "SELECT id, name FROM users WHERE name = '%s'" % name
    return conn.execute(q).fetchall()
''',
 "D · escape by hand": '''
def get_user(conn, name):
    safe = name.replace("'", "''")
    return conn.execute("SELECT id, name FROM users WHERE name = '" + safe + "'").fetchall()
''',
}
print(f"{'candidate':34s}{'scanner green':>15}")
print("-" * 50)
for name, src in CANDIDATES.items():
    print(f"{name:34s}{str(not scanner_fires(src)):>15}")
print("\nThree of four are green. Only one of those is a fix.")

def validate(src):
    fn = load(src)
    green = not scanner_fires(src)
    beh = behaviour_ok(fn)
    preserved = all(ok for _, _, ok in beh)
    still_exploitable, _ = exploit_works(fn)
    reasons = []
    if not green:            reasons.append("scanner still fires")
    if not preserved:        reasons.append("behaviour changed")
    if still_exploitable:    reasons.append("STILL EXPLOITABLE (stage-12 probe passes)")
    return (not reasons), green, preserved, still_exploitable, reasons

print(f"{'candidate':34s}{'scan':6s}{'behaviour':11s}{'exploitable':13s}verdict")
print("-" * 84)
accepted = []
for name, src in CANDIDATES.items():
    ok, g, b, x, reasons = validate(src)
    if ok: accepted.append(name)
    print(f"{name:34s}{str(g):6s}{str(b):11s}{str(x):13s}"
          f"{'ACCEPT' if ok else 'REJECT — ' + ', '.join(reasons)}")
print(f"\naccepted: {accepted}")
assert "A · parameterise (the real fix)" in accepted
assert "B · delete the feature" not in accepted
assert "C · evade the scanner" not in accepted

# The proof-of-fix clause: the exploit must fail on the new build and
# succeed on the old one. Without both halves, "fixed" is a claim.
def proof_of_fix(old_src, new_src):
    old_ex, _ = exploit_works(load(old_src))
    new_ex, _ = exploit_works(load(new_src))
    return (old_ex and not new_ex), f"exploit on old={old_ex}, on new={new_ex}"

for name in accepted:
    ok, detail = proof_of_fix(VULNERABLE, CANDIDATES[name])
    print(f"{name:34s} proof of fix: {ok}  ({detail})")

print("\nCandidate D passes every automated check and is still the wrong answer:")
print("it reimplements the driver's escaping and will be wrong for the next")
print("input class or the next database. Nothing except a rule about MECHANISM")
print("catches that — which is the part of remediation that does not automate.")

# ------------------------------------ the same task, against a real model
# Offline this is a labelled replay; with an open-weight model served
# from Kaggle it is the same code calling a real one.

TASK = 'Fix this without changing the function\'s behaviour for valid input. Return only the patched function.\n\ndef report(request):\n    q = "SELECT * FROM orders WHERE ref = \'" + request.args[\'ref\'] + "\'"\n    return db.execute(q)'

REPLAY = 'def report(request):\n    q = "SELECT * FROM orders WHERE ref = ?"\n    return db.execute(q, (request.args[\'ref\'],))'

answer, used, model = ask(TASK, replay=REPLAY,
            system='You are a remediation engineer. Output code only, no explanation.',
            max_tokens=300)

print(f"backend used : {used}")
print(f"model        : {model}")
print(f"prompt       : {TASK[:66]}...")
print()
print("answer:")
for line in (answer.splitlines() or [answer]):
    print(f"   {line}")

# Two assertions that must hold on every backend, and one property that is
# reported rather than asserted - a real model failing it is a finding about
# the model, not a broken notebook.
assert answer.strip(), "the configured backend returned nothing"
if used == "replay":
    assert answer == REPLAY, "the offline path must return the replay verbatim"

label, held = ("parameterises the query", "?" in answer or "%s" in answer or ":ref" in answer)
print()
print(f"property checked : {label}")
print(f"held on {used:12s} : {held}")
print()
print("Same code, same assertions, two possible backends. Offline the answer is")
print("the replay and is labelled as one; with a served model it is the model's.")
