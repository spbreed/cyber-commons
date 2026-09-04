"""The Cyber Commons skill runtime — one library, used by every lesson.

Every lesson in the commons executes an agent skill, and until this file existed
each of the 117 notebooks carried its own copy of the sixty lines that parse a
`SKILL.md` and the sixty that call a model. That was 9,730 lines of identical
code — 34,112 lines of notebook code before this file existed, 24,382 after —
and a fix to any of it meant rebuilding everything and hoping.

So it lives here once. On Kaggle it is attached to each notebook as a **utility
script**, which is Kaggle's mechanism for exactly this; locally it is on the
path. Either way a lesson's own cell is two lines:

    from cyber_commons_skill_runtime import run_skill
    meta, body = run_skill(SKILL_MD)

Standard library only, and deterministic, because the notebooks that import it
run on a CPU kernel with the internet switched off.

Two halves:

  * **the skill runtime** — parse a SKILL.md, route between skills by
    description, read and check an output contract;
  * **the model adapter** — one OpenAI-compatible backend, plus the labelled
    offline replay that is the default. There is no paid path.
"""

import json, re

def parse_skill(md):
    """Split a SKILL.md into (frontmatter dict, body).

    Frontmatter is a small, fixed subset of YAML: `key: value`, plus folded
    scalars (`description: >-`) whose continuation lines are indented. That is
    all a skill needs, and parsing it directly means no dependency.
    """
    if not md.startswith("---"):
        raise ValueError("a SKILL.md must open with a frontmatter block")
    _, front, body = md.split("---", 2)
    meta, key = {}, None
    for line in front.strip().splitlines():
        if not line.strip():
            continue
        if not line[0].isspace() and ":" in line:
            key, val = line.split(":", 1)
            key, val = key.strip(), val.strip()
            # `>-` and `|` open a folded block; the value is on the next lines
            meta[key] = "" if val in (">-", ">", "|", "|-") else val
        elif key is not None:
            meta[key] = (meta[key] + " " + line.strip()).strip()
    if "allowed-tools" in meta:
        meta["allowed-tools"] = [t.strip() for t in meta["allowed-tools"].split(",")
                                 if t.strip()]
    for required in ("name", "description"):
        if not meta.get(required):
            raise ValueError(f"skill is missing a {required!r}")
    return meta, body.strip()

_WORD = re.compile(r"[a-z][a-z-]{3,}")

def route(task, skills):
    """Pick the skill whose description best matches a task. Deterministic.

    The description is not documentation — it is the routing key. An agent
    decides whether to load a skill by reading it, so a vague description means
    the skill never fires when it should, and two overlapping descriptions mean
    the wrong one fires.

    Returns (pick, scores, margin). A margin of 0 means the top two scored the
    same and the "winner" is just whichever sorted first — an arbitrary answer
    wearing a confident face. Callers should refuse to auto-route on margin 0
    rather than pretend the tiebreak meant something.
    """
    want = set(_WORD.findall(task.lower()))
    def score(meta):
        return len(want & set(_WORD.findall(meta["description"].lower())))
    scores = {n: score(skills[n]) for n in sorted(skills)}
    # sort names first, then by score: ties must break identically on every
    # machine or the same task routes differently on two runs
    ranked = sorted(sorted(skills), key=lambda n: -scores[n])
    top = scores[ranked[0]]
    margin = top - (scores[ranked[1]] if len(ranked) > 1 else 0)
    return ranked[0], scores, margin

def contract_of(body):
    """The JSON block under '## Output contract' — the skill's machine promise."""
    # non-greedy across any prose between the heading and the fence
    m = re.search(r"## Output contract\b.*?```json\n(.*?)```", body, re.S)
    if not m:
        raise ValueError("skill declares no output contract")
    return json.loads(m.group(1))

def check(instance, contract, path="$"):
    """Structural conformance of an instance against a contract template.

    Returns the list of problems. An empty list means the shape is right — and
    that is *all* it means. Conformance is not accuracy: an empty findings list
    conforms perfectly and tells you nothing.
    """
    problems = []
    if isinstance(contract, dict):
        if not isinstance(instance, dict):
            return [f"{path}: expected an object, got {type(instance).__name__}"]
        for k, v in sorted(contract.items()):
            if k not in instance:
                problems.append(f"{path}.{k}: missing")
            else:
                problems += check(instance[k], v, f"{path}.{k}")
    elif isinstance(contract, list):
        if not isinstance(instance, list):
            return [f"{path}: expected a list, got {type(instance).__name__}"]
        for i, item in enumerate(instance):          # every element, same template
            problems += check(item, contract[0], f"{path}[{i}]")
    elif isinstance(contract, str) and "|" in contract:
        if instance not in contract.split("|"):
            problems.append(f"{path}: {instance!r} is not one of {contract}")
    elif isinstance(contract, bool):                  # before the numeric case:
        if not isinstance(instance, bool):            # bool is a subclass of int
            problems.append(f"{path}: expected bool, got {type(instance).__name__}")
    elif isinstance(contract, (int, float)):
        # JSON has one number type. A contract written `0` must accept 0.4, or
        # every cost and rate in the pipeline has to be rounded to satisfy a
        # checker rather than to be correct.
        if isinstance(instance, bool) or not isinstance(instance, (int, float)):
            problems.append(f"{path}: expected a number, got {type(instance).__name__}")
    elif not isinstance(instance, type(contract)):
        problems.append(f"{path}: expected {type(contract).__name__}, "
                        f"got {type(instance).__name__}")
    return problems



def run_skill(md):
    """Parse a SKILL.md and report what was loaded. Returns (meta, body).

    The four lines it prints are what a lesson shows: the name an agent routes
    on, the tools the skill is bounded to, how long its routing description is,
    and how long its procedure is. Printing them from one function rather than
    from 117 copies is the point of this file.
    """
    meta, body = parse_skill(md)
    print(f"loaded skill: {meta['name']}")
    print(f"  tools it may use: {', '.join(meta.get('allowed-tools', [])) or '-'}")
    print(f"  routing description: {len(meta['description'].split())} words")
    print(f"  procedure: {len(body.splitlines())} lines")
    return meta, body


# ----------------------------------------------------------- the model adapter
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

def announce_backend():
    """Say which backend is configured, where a lesson can see it.

    A library must not print at import: 117 notebooks importing this file
    would each open with a banner nobody asked for. The skills that call a
    model call this; the rest never see it.
    """
    kind, model = backend()
    print(f"model backend : {kind}")
    print(f"model         : {model}")
    if kind == "replay":
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
    return kind, model
