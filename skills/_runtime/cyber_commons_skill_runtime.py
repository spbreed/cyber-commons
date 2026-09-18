"""The Cyber Commons skill runtime — one library, used by every lesson.

Every lesson in the commons executes an agent skill, and each skill script once
carried its own copy of the sixty lines that parse a `SKILL.md` and the sixty
that call a model. That was 9,730 lines of identical code, and a fix to any of
it meant editing 139 files and hoping.

So it lives here once, and every skill script reaches it through `PYTHONPATH`:

    from cyber_commons_skill_runtime import run_skill
    meta, body = run_skill(SKILL_MD)

Standard library only — nothing to install. The model is the one prerequisite;
this file fetches nothing else.

Two halves:

  * **the skill runtime** — parse a SKILL.md, route between skills by
    description, read and check an output contract;
  * **the model adapter** — two backends and no paid path. A signed-in Claude
    Code CLI answers with **no API key and no endpoint**, which is the shortest
    route for anyone already using an agentic editor; an OpenAI-compatible URL
    covers everything else, local or hosted. With neither, a skill refuses.
"""

import json, re, shutil, subprocess, time

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

# Placeholder names a contract may use where a literal would be meaningless.
# These are the repository's own convention, already used for values; the
# checker now honours them for keys and in alternations too.
TYPE_NAMES = {"str", "int", "float", "bool", "null"}
_TYPES = {"str": str, "int": int, "float": (int, float), "bool": bool}


def _matches_any_type(value, options):
    for o in options:
        if o == "null" and value is None:
            return True
        if o == "bool" and isinstance(value, bool):
            return True
        if o in ("int", "float") and not isinstance(value, bool) \
                and isinstance(value, _TYPES[o]):
            return True
        if o == "str" and isinstance(value, str):
            return True
        if o not in TYPE_NAMES and value == o:
            return True
    return False


def check(instance, contract, path="$"):
    """Structural conformance of an instance against a contract template.

    Returns the list of problems. An empty list means the shape is right — and
    that is *all* it means. Conformance is not accuracy: an empty findings list
    conforms perfectly and tells you nothing.
    """
    problems = []

    # A `null` in a contract example means "unspecified or nullable", not "this
    # must always be null". Read literally it demanded NoneType forever, so a
    # skill whose example had `"verified": null` counted a real boolean as a
    # violation — the model was right and the checker was wrong.
    if contract is None:
        return []

    if isinstance(contract, dict):
        if not isinstance(instance, dict):
            return [f"{path}: expected an object, got {type(instance).__name__}"]
        # `{"str": 0}` is this repository's way of writing "a mapping from
        # string to int" — the same placeholder convention the contracts
        # already use for values (`"kind": "str"`). Read literally it demanded
        # a key spelled "str". Check every key's value against the template
        # instead.
        if len(contract) == 1 and next(iter(contract)) in TYPE_NAMES:
            template = next(iter(contract.values()))
            for k in sorted(instance):
                problems += check(instance[k], template, f"{path}.{k}")
            return problems
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
        options = contract.split("|")
        # An alternation may name types rather than literals — "bool|null" is
        # how a contract says "a boolean, or absent". Without this, a field
        # that is legitimately unknown (an MCP tool that declares no
        # annotations) could only be filled in by inventing a value.
        if any(o in TYPE_NAMES for o in options):
            if not _matches_any_type(instance, options):
                problems.append(f"{path}: {type(instance).__name__} is not one "
                                f"of {contract}")
        elif instance not in options:
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
# The CLI starts a whole agent session, so it is slower to first
# token than a raw completions call. 300s is generous on purpose:
# a timeout here reads as a broken skill rather than a slow model.
CLI_TIMEOUT = 300

class ModelUnavailable(RuntimeError):
    """The model could not answer for a reason that is not about the skill.

    A usage limit, a rate limit or an overloaded backend says **nothing** about
    the skill that happened to be running when it hit. Conflating the two is
    how a sweep reports 121 broken skills that are all fine: the calls came
    back in two seconds each, which is a quota rejection wearing the shape of a
    model reply, and the harness recorded them as contract failures.

    So it is a distinct exception. A caller sweeping many skills must stop when
    it sees this, not record a result.
    """


class NoModelConfigured(RuntimeError):
    """Raised when a skill is run with no model endpoint configured.

    Every skill in this commons runs on a model. There is no offline path and
    no stand-in: a stand-in that is allowed to answer is a stand-in somebody
    eventually quotes as a model result. If nothing is configured, the skill
    refuses rather than producing something that looks like an answer.

    A0.0 is the lesson that sets this up, start to finish, on free tiers.
    """


def claude_cli():
    """The path to a logged-in `claude` CLI, or None.

    This is the backend that needs **no API key and no endpoint**. If you have
    Claude Code installed and signed in, the CLI answers in headless mode
    (`claude -p`) on your existing subscription — the same authentication the
    editor uses. For anybody already working in Claude Code, Cursor or Copilot
    that is the cheapest and shortest path to running every skill here, and it
    was missing from the first version of this runtime, which assumed an HTTP
    endpoint was the only way to reach a model.

    Set CLAUDE_CLI=0 to skip it and force the HTTP path.
    """
    if os.environ.get("CLAUDE_CLI") == "0":
        return None
    return shutil.which(os.environ.get("CLAUDE_CLI_BIN", "claude"))


def backend():
    """(kind, model). Configuration comes from the environment, never a literal.

    Order matters, and it is: an explicitly configured endpoint first, because
    somebody who set OPENAI_BASE_URL meant it; then the local Claude CLI, which
    needs nothing at all; then a refusal.

    Raises NoModelConfigured when there is nothing to call.
    """
    if os.environ.get("OPENAI_BASE_URL"):
        return "open-weight", os.environ.get("MODEL", OPEN_WEIGHT_DEFAULT)
    if claude_cli():
        return "claude-cli", os.environ.get("MODEL", "claude (Claude Code CLI)")
    raise NoModelConfigured(
        "No model is available, and every skill here needs one. Two ways, and\n"
        "the first needs no key and no endpoint:\n"
        "\n"
        "  1. Claude Code, already signed in — nothing to configure. Install it\n"
        "     and run `claude` once to sign in; skills then use that session.\n"
        "\n"
        "  2. Any OpenAI-compatible endpoint, local or hosted:\n"
        "       export OPENAI_BASE_URL=http://127.0.0.1:11434/v1\n"
        "       export OPENAI_API_KEY=ollama      # any non-empty value locally\n"
        "       export MODEL=qwen2.5:1.5b-instruct\n"
        "\n"
        "Lesson A0.0 sets both up end to end. MODELS.md lists which model suits\n"
        "which lab.")

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

def _claude_cli_call(prompt, system, timeout=CLI_TIMEOUT):
    """Headless `claude -p`, on the signed-in session. No key, no endpoint.

    The prompt goes on **stdin**, not in argv: a skill's prompt is its whole
    SKILL.md and routinely runs to several kilobytes, which is past the
    argument-length limit on some systems and would fail as a confusing
    "argument list too long" rather than as anything about models.
    """
    # No tools. The harness has already put the fixture in the prompt, so there
    # is nothing on disk for the model to go and find — and an agent left with
    # Bash and Read will go looking anyway, which turns a one-shot completion
    # into a multi-minute session and makes the answer depend on what it
    # happened to read. Restricting the tool set is what makes this a model
    # call rather than an agent run.
    cmd = [claude_cli(), "-p",
           "--disallowed-tools", "Bash", "Read", "Write", "Edit", "Glob",
           "Grep", "WebFetch", "WebSearch", "Task", "NotebookEdit"]
    if system:
        cmd += ["--append-system-prompt", system]
    started = time.monotonic()
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                       timeout=timeout)
    elapsed = time.monotonic() - started
    blob = f"{p.stdout}\n{p.stderr}".lower()

    # A quota rejection is fast and it is not an answer. Both halves matter:
    # the wording varies between "usage limit", "rate limit" and "overloaded",
    # and a genuine short reply is possible — but a reply that arrives in under
    # five seconds *and* carries none of a JSON object is a rejection, because
    # a real call to this backend takes tens of seconds.
    quota = any(s in blob for s in ("usage limit", "rate limit", "quota",
                                    "too many requests", "overloaded",
                                    "429", "limit reached"))
    if quota or (elapsed < 5 and "{" not in p.stdout):
        raise ModelUnavailable(
            f"the model did not answer, and this is not about the skill: "
            f"{(p.stderr or p.stdout).strip()[:300] or 'empty reply'} "
            f"(after {elapsed:.1f}s). Wait for the limit to reset and run it "
            f"again — do not record this as a result.")

    if p.returncode != 0:
        raise RuntimeError(
            f"the claude CLI exited {p.returncode}: "
            f"{(p.stderr or p.stdout).strip()[-400:]}\n"
            f"If it is not signed in, run `claude` once interactively. Nothing "
            f"is substituted for a model answer.")
    return p.stdout.strip()


def ask(prompt, *, system=None, max_tokens=512, temperature=0.0):
    """Answer `prompt` with the configured model. Returns (answer, kind, model).

    There is no fallback. A failed call raises, because the alternative — a
    canned answer returned in a model's place — is the one failure mode that
    cannot be detected downstream: it has the right shape, it validates against
    the contract, and it is not a model result.

    `temperature` defaults to 0 so two runs are as close as a model gets. That
    is not determinism and nothing here pretends it is; see WHAT_CHANGED.md.
    """
    kind, model = backend()
    if kind == "claude-cli":
        return _claude_cli_call(prompt, system), kind, model
    try:
        return _openai_compatible(prompt, system, model, max_tokens,
                                  temperature), kind, model
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
            TimeoutError) as e:
        # Say what the server actually said. "failed: 400" costs whoever hits
        # this an hour; the body usually names the exact missing parameter, and
        # it never contains a key.
        detail = getattr(e, "code", None) or type(e).__name__
        why = ""
        if hasattr(e, "read"):
            try:
                why = json.loads(e.read().decode()).get("error", {}).get("message", "")
            except Exception:
                why = ""
        raise RuntimeError(
            f"the model backend ({model}) failed: {detail}"
            f"{' - ' + why if why else ''}\n"
            f"Endpoint: {os.environ.get('OPENAI_BASE_URL')}\n"
            f"Nothing is substituted for a model answer. Fix the endpoint and "
            f"run it again; A0.0 walks through the free options.") from e

def announce_backend():
    """Say which model is about to answer, where a lesson can see it.

    A library must not print at import: 134 notebooks importing this file would
    each open with a banner nobody asked for. Every skill calls this as its
    first line, so the reader always knows which model produced what follows —
    and, when nothing is configured, gets the setup instructions instead of a
    traceback.
    """
    try:
        kind, model = backend()
    except NoModelConfigured as e:
        print("no model configured\n")
        print(e)
        raise SystemExit(2)
    print(f"model backend : {kind}")
    print(f"model         : {model}")
    # "endpoint: None" on the CLI path reads as something failing to resolve.
    # Say which mechanism is answering instead.
    print(f"endpoint      : "
          f"{os.environ.get('OPENAI_BASE_URL') or claude_cli() + ' (no API key)'}")
    print()
    print("Everything below is this model's output, validated against the")
    print("skill's contract. Another model will answer differently; that is the")
    print("point of the lesson, not a defect in it.")
    print()
    return kind, model


# ------------------------------------------------------- the generic run path
#
# Every skill is the same shape: a procedure written in SKILL.md, an output
# contract under `## Output contract`, and some input to apply it to. So the
# model gets the skill's own text rather than a prompt written twice, and the
# answer is validated against the skill's own contract. One implementation, 139
# skills, and a skill's prompt cannot drift from its documentation because they
# are the same bytes.

def jsonable(obj):
    """A structure json.dumps will accept, preserving what the keys meant.

    `default=str` handles unserialisable *values* and does nothing for keys, so
    a fixture keyed by tuples — `{("agent", "db"): "allow"}`, which is the
    natural shape for a permission matrix — died with "keys must be str, int,
    float, bool or None, not tuple" before any model was called. Three skills
    had exactly that. Tuple keys become "a | b", which is what they read as in
    the source anyway.
    """
    if isinstance(obj, dict):
        return {(" | ".join(map(str, k)) if isinstance(k, tuple) else
                 k if isinstance(k, (str, int, float, bool)) or k is None
                 else str(k)): jsonable(v)
                for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [jsonable(v) for v in obj]
    return obj


JSON_BLOCK = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def _first_json(text):
    """The first JSON object in a model's reply, fenced or bare.

    Models wrap JSON in prose and in fences, inconsistently and regardless of
    instructions. Refusing anything but a bare object turns a good answer into
    a failed run.
    """
    for candidate in ([m.group(1) for m in JSON_BLOCK.finditer(text)] + [text]):
        candidate = candidate.strip()
        start = candidate.find("{")
        if start < 0:
            continue
        depth, in_str, esc = 0, False, False
        for i, ch in enumerate(candidate[start:], start):
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(candidate[start:i + 1])
                    except json.JSONDecodeError:
                        break
    raise ValueError("the model returned no parseable JSON object:\n"
                     + text[:800])


def run_with_model(skill_md, task, *, max_tokens=1500, temperature=0.0):
    """Run a skill by giving its own procedure and contract to the model.

    `skill_md` is the text of the skill's SKILL.md; `task` is the input to
    apply it to. Returns (instance, problems, kind, model) — the parsed answer,
    the contract violations found in it, and which model answered.

    The problems are returned rather than raised because an answer that misses
    the contract is a finding a lesson should print, not an error that hides
    what the model actually said.
    """
    meta, body = parse_skill(skill_md)
    contract = contract_of(body)
    system = ("You are executing a documented procedure exactly as written. "
              "Follow the skill below. Reply with one JSON object matching the "
              "output contract and nothing else — no prose, no explanation.")
    prompt = (f"{body}\n\n"
              f"---\n\n## The input to apply the procedure to\n\n{task}\n\n"
              f"---\n\nReturn one JSON object matching the output contract "
              f"above. Use the contract's exact keys.")
    answer, kind, model = ask(prompt, system=system, max_tokens=max_tokens,
                              temperature=temperature)
    instance = _first_json(answer)
    return instance, check(instance, contract), kind, model


# ---------------------------------------------------------------- diagrams
# A skill that produces a graph should emit it in a language a real renderer
# reads, not only as ASCII. These build **source** — DOT for Graphviz, PlantUML
# for PlantUML — which is text, so it stays standard library only and runs on a
# kernel with nothing installed. `scripts/render_diagrams.py` renders and
# validates it with the actual binaries and commits the SVG.
#
# Deterministic by construction: every emitter sorts its inputs, so two runs of
# the same skill produce byte-identical source and the committed SVG only
# changes when the graph does.

def _dot_id(name):
    r"""A DOT-safe quoted identifier.

    `\n`, `\l` and `\r` are DOT's own line breaks and must survive; every other
    backslash is dropped rather than escaped, because a stray one in a label is
    always a mistake. Stripping all of them turned "ingress\ntrust 0" into
    "ingressntrust 0" on every node of the architecture map.
    """
    s = str(name).replace('"', "'")
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\":
            if i + 1 < len(s) and s[i + 1] in "nlr":
                out.append(s[i:i + 2])
                i += 2
                continue
            i += 1
            continue
        out.append(s[i])
        i += 1
    return '"' + "".join(out) + '"'


# The shared vocabulary. Same kind, same colour, in every diagram the commons
# renders — and `dead` is dashed as well as dim, because two greys a shade apart
# are not a distinction anyone reads at a glance. The fourth field is the
# fallback legend text; a diagram passes its own via `legend_labels`.
KINDS = {
    "entry":   ("#E05C4B", "#2a1614", "solid",  "untrusted entry point"),
    "unit":    ("#8A93A6", "#1a1e28", "solid",  "reachable"),
    "sink":    ("#E0912F", "#2a2114", "solid",  "acts on something"),
    "dead":    ("#525a6e", "#15171d", "dashed", "unreachable"),
    "unknown": ("#4D9BFF", "#141c2a", "solid",  "undecided"),
    "control": ("#3FA06B", "#14231b", "solid",  "a control"),
}


def dot_graph(name, nodes, edges, *, rankdir="LR", clusters=None,
              legend=True, legend_labels=None):
    """Graphviz DOT source for a directed graph.

    nodes:    {id: {"label": str, "kind": str}}   kind picks the palette
    edges:    [(src, dst, label)]
    clusters: {cluster_label: [node_id, ...]}     optional grouping
    legend:   emit a key for the kinds actually used

    The palette is by *kind* rather than per node, so the same vocabulary means
    the same thing everywhere, and the legend is generated from the kinds this
    particular graph uses rather than listing all of them.
    """
    style = {k: (v[0], v[1]) for k, v in KINDS.items()}
    out = [f"digraph {_dot_id(name)} {{",
           f"  rankdir={rankdir};",
           '  bgcolor="transparent";',
           '  node [shape=box style="rounded,filled" fontname="Helvetica" '
           'fontsize=11 penwidth=1.2];',
           '  edge [fontname="Helvetica" fontsize=9 color="#8A93A6" '
           # Edge labels default to black, which is invisible on the dark
           # page the lesson renders on.
           'fontcolor="#A8B2C6" penwidth=1.1];']
    for nid in sorted(nodes):
        meta = nodes[nid]
        kind = meta.get("kind", "unit")
        pen, fill, line, _ = KINDS.get(kind, KINDS["unit"])
        dash = ',dashed' if line == "dashed" else ''
        fg = "#9aa3b5" if kind == "dead" else "#E9EDF6"
        out.append(f'  {_dot_id(nid)} [label={_dot_id(meta.get("label", nid))} '
                   f'color="{pen}" fillcolor="{fill}" fontcolor="{fg}" '
                   f'style="rounded,filled{dash}"];')
    for i, (label, members) in enumerate(sorted((clusters or {}).items())):
        out.append(f"  subgraph cluster_{i} {{")
        out.append(f'    label={_dot_id(label)}; color="#26314b"; '
                   'fontcolor="#96A0B8"; fontname="Helvetica"; fontsize=10;')
        for m in sorted(members):
            out.append(f"    {_dot_id(m)};")
        out.append("  }")
    for src, dst, label in sorted(edges):
        attr = f' [label={_dot_id(label)}]' if label else ""
        out.append(f"  {_dot_id(src)} -> {_dot_id(dst)}{attr};")

    # A key, built from the kinds this graph actually uses. A diagram whose
    # colours mean something and does not say what is a diagram the reader
    # decodes by guessing.
    used = sorted({n.get("kind", "unit") for n in nodes.values()},
                  key=lambda k: list(KINDS).index(k))
    # Each diagram names its own vocabulary. "reachable"/"unreachable" is the
    # call graph's language and means nothing on an architecture map, so the
    # shared text in KINDS is only a fallback.
    words = dict(legend_labels or {})
    if legend and used:
        out.append("  subgraph cluster_legend {")
        out.append('    label="key"; color="#26314b"; fontcolor="#96A0B8"; '
                   'fontname="Helvetica"; fontsize=10; rank=sink;')
        prev = None
        for kind in used:
            pen, fill, line, default = KINDS[kind]
            text = words.get(kind, default)
            dash = ',dashed' if line == "dashed" else ''
            nid = f"legend_{kind}"
            fg = "#9aa3b5" if kind == "dead" else "#E9EDF6"
            out.append(f'    {_dot_id(nid)} [label={_dot_id(text)} '
                       f'color="{pen}" fillcolor="{fill}" fontcolor="{fg}" '
                       f'fontsize=9 style="rounded,filled{dash}"];')
            if prev:
                out.append(f"    {_dot_id(prev)} -> {_dot_id(nid)} "
                           f'[style=invis];')
            prev = nid
        out.append("  }")
    out.append("}")
    return "\n".join(out) + "\n"


def puml_sequence(title, participants, messages, *, notes=()):
    """PlantUML sequence source — the right shape for a flow over time.

    participants: [(alias, label, kind)]   kind as in dot_graph
    messages:     [(src, dst, text, style)]  style: "" | "danger" | "control"
    notes:        [(alias, text)]           real newlines, not "\\n"

    The skin is set explicitly for a dark page. PlantUML's defaults are black
    text on white, and dropping that onto the lesson background produced a
    title nobody could read and participant boxes in colours that belong to no
    palette — which is exactly the kind of thing a renderer will not tell you
    about, because it exited 0.
    """
    fill = {k: v[1] for k, v in KINDS.items()}
    pen = {k: v[0] for k, v in KINDS.items()}
    out = ["@startuml",
           "skinparam backgroundColor transparent",
           "skinparam shadowing false",
           "skinparam defaultFontName Helvetica",
           "skinparam defaultFontColor #E9EDF6",
           "skinparam titleFontColor #E9EDF6",
           "skinparam titleFontSize 14",
           "skinparam sequenceMessageAlign center",
           "skinparam sequence {",
           "  ArrowColor #8A93A6",
           "  ArrowFontColor #C7CEDC",
           "  LifeLineBorderColor #3a4258",
           "  LifeLineBackgroundColor transparent",
           "  ParticipantFontColor #E9EDF6",
           "  ParticipantBorderThickness 1.4",
           "  BoxBorderColor #26314b",
           "  ParticipantBorderColor #4a5468",
           "}",
           "skinparam noteBackgroundColor #1a1e28",
           "skinparam noteBorderColor #4D9BFF",
           "skinparam noteFontColor #C7CEDC",
           f"title {title}"]
    for alias, label, kind in participants:
        # Fill only. The `##[bold]#RRGGBB` per-participant border syntax is a
        # newer PlantUML dialect and 1.x reports "Some diagram description
        # contains errors" for it — while still exiting 0, which is the reason
        # render_diagrams.py checks the output rather than the return code.
        out.append(f'participant "{label}" as {alias} {fill.get(kind, "#1a1e28")}')
    for src, dst, text, kind in messages:
        arrow = "-[#E05C4B]>" if kind == "danger" else (
            "-[#3FA06B]>" if kind == "control" else "-[#8A93A6]>")
        out.append(f"{src} {arrow} {dst}: {text}")
    for alias, text in notes:
        # A real newline. "\\n" in a note renders as the two characters, and
        # the reader sees a backslash in the middle of a sentence.
        #
        # And a leading apostrophe is PlantUML's line comment. A note line that
        # opens on a quoted phrase is silently deleted from the diagram — the
        # render succeeds, the SVG is valid, and the sentence is simply gone.
        # One leading space is enough to stop it being a comment.
        # A leading space does not help: PlantUML trims before testing. Swap
        # the ASCII apostrophe for the typographic one, which reads identically
        # and is not a comment marker.
        safe = "\n".join("\u2019" + ln.lstrip()[1:] if ln.lstrip().startswith("'")
                         else ln for ln in str(text).splitlines())
        out.append(f"note over {alias}\n{safe}\nend note")
    out.append("@enduml")
    return "\n".join(out) + "\n"


def emit_diagram(stem, *, dot=None, puml=None):
    """Print the source and say where the rendered copy lives.

    A notebook prints text; the lesson page shows the SVG that
    `scripts/render_diagrams.py` produced from exactly this source.
    """
    if dot:
        print(f"[diagram:dot:{stem}]")
        print(dot, end="")
    if puml:
        print(f"[diagram:puml:{stem}]")
        print(puml, end="")
    return {"stem": stem, "dot": bool(dot), "puml": bool(puml)}
