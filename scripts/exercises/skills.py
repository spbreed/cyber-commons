"""Agent skills as lesson material.

A skill is a markdown file with YAML frontmatter that tells an agent *when* to
load it and *what procedure* to follow. The real files live in `skills/` and are
the single source of truth; `build_notebooks.py` embeds them verbatim into the
notebooks, so a lesson can never drift from the skill it teaches.

This module holds the small runtime the lessons use to work with them. It is
emitted into the notebooks as literal source — notebooks carry every line they
run — so it must stay standard library only, and deterministic.
"""

# The parser, router and contract checker, emitted verbatim into any lesson that
# works with skills. Roughly sixty lines, no dependencies: a SKILL.md is a plain
# format on purpose, and being able to read one in sixty lines is the point.
SKILL_RUNTIME = '''
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
    m = re.search(r"## Output contract\\b.*?```json\\n(.*?)```", body, re.S)
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
'''.strip()


def runtime_step() -> tuple[str, str]:
    """The `("py", ...)` step that puts the skill runtime into a notebook."""
    return ("py", SKILL_RUNTIME)
