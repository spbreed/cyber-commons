#!/usr/bin/env python3
"""Rewrite every skill's script so the **model** performs the procedure.

Before this, a skill's script computed its own answer: the procedure was
documented in `SKILL.md` and separately implemented in Python, and the Python
was what actually ran. That is two copies of one thing, and only one of them
executed — which meant a skill could be beautifully documented and do something
else entirely.

After this, the script is a **harness**, not the procedure:

    fixture  ->  the model, given this skill's own SKILL.md  ->  JSON
                                                                 |
                                            validated against the same
                                            SKILL.md's output contract

The prompt is the skill's documentation, so a skill's instructions cannot drift
from what it runs — they are the same bytes. What the script keeps is the
**fixture**: the committed input every `## Example` section already points at
("the fixture committed at the top of scripts/…"). That data is the lesson's
substance and is carried across verbatim, line for line, from the original
source.

Fixtures are found by AST rather than by regex: module-level assignments to an
UPPERCASE name whose value is a literal. 135 of 140 skills match that shape;
the rest are listed and left alone, because a converter that guesses produces
139 working skills and one that silently does nothing.

    python3 scripts/convert_skills_to_model.py --dry-run   # what would change
    python3 scripts/convert_skills_to_model.py             # rewrite them
    python3 scripts/convert_skills_to_model.py --only threats/tool-scope-abuse-probe
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LITERAL = (ast.List, ast.Dict, ast.Tuple, ast.Constant, ast.Set)

TEMPLATE = '''#!/usr/bin/env python3
"""{title}

The procedure this runs is **not in this file**. It is in the `SKILL.md` beside
it, and the model is what carries it out: this script assembles the fixture,
hands the model the skill's own documentation and output contract, and checks
the reply against that same contract.

That is the point. A procedure written in one place and implemented in another
is two things that can disagree, and only one of them runs. Here they are the
same bytes.

The fixture below is committed input, carried over unchanged. Edit it and
re-run — every number in the output is derived from it.

    export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
    export OPENAI_API_KEY=ollama
    export MODEL=qwen2.5:1.5b-instruct
    python3 {rel}

With no endpoint configured this exits 2 and says so. Nothing is substituted
for a model's answer.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "_runtime"))

from cyber_commons_skill_runtime import (  # noqa: E402
    announce_backend, jsonable, run_with_model)

SKILL = pathlib.Path(__file__).resolve().parents[1] / "SKILL.md"

# ---------------------------------------------------------------- the fixture
{fixture}
# ------------------------------------------------------------------------ run

def task() -> str:
    """The fixture, as the model sees it."""
    return "\\n\\n".join(
        f"### {{name}}\\n\\n```json\\n"
        f"{{json.dumps(jsonable(value), indent=2, default=str)}}\\n```"
        for name, value in FIXTURE.items())


FIXTURE = {{{fixture_map}}}


def main() -> int:
    announce_backend()

    print("the fixture this run is derived from")
    for name, value in FIXTURE.items():
        n = len(value) if isinstance(value, (list, dict, tuple, set)) else 1
        print(f"   {{name:<28}} {{n}} item(s)")
    print()

    instance, problems, kind, model = run_with_model(SKILL.read_text(), task())

    print(f"answered by   : {{model}}  ({{kind}})")
    print(f"violations    : {{len(problems)}}")
    for p in problems:
        print(f"   {{p}}")
    print()
    print(json.dumps(instance, indent=2, sort_keys=True, default=str))
    print()
    # The violations are printed, not raised, and they are also the exit code's
    # reason: what the model actually said is the evidence a reader needs, and
    # hiding it behind a traceback removes the only thing worth looking at.
    print(f"contract: {{'held' if not problems else 'BROKEN in ' + str(len(problems)) + ' place(s)'}}"
          f" — this is one model's answer, not the answer")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
'''


def fixtures_of(src: str) -> list[tuple[str, str]]:
    """(name, source lines) for every module-level UPPERCASE literal constant."""
    tree = ast.parse(src)
    lines = src.splitlines()
    out = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, LITERAL):
            continue
        # Literal-*shaped* is not the same as constant. A dict whose values are
        # expressions — `{"expires": test.valid_for_days > 0}` — parses as
        # ast.Dict and then fails at import with NameError, because the name it
        # closes over is gone. literal_eval is the only honest test.
        try:
            ast.literal_eval(node.value)
        except (ValueError, SyntaxError, TypeError):
            continue
        names = [t.id for t in node.targets
                 if isinstance(t, ast.Name) and t.id.isupper()]
        if len(names) != 1:
            continue
        # Take any comment block immediately above: it says what the fixture is
        # and why it has the values it has, which is exactly what a reader of
        # the converted script needs and what a plain slice would throw away.
        # Walk up over the comment block that explains the fixture — but stop
        # at this template's own banner rule. Converting an already-converted
        # file otherwise swallows the banner into the fixture and re-emits it
        # above the new one, so every re-run adds another copy. Three had
        # accumulated before anybody looked.
        start = node.lineno - 1
        while start > 0:
            above = lines[start - 1].lstrip()
            if not above.startswith("#") or set(above) <= set("#- "):
                break
            start -= 1
        # Drop this template's own banner rules wherever they appear in the
        # captured block. Stopping the walk-up at one was not enough: earlier
        # runs had already baked copies *into* the fixture comment, so they
        # were no longer the adjacent line and survived. Filtering is
        # idempotent — converting a converted file is a no-op.
        block = "\n".join(l for l in lines[start:node.end_lineno]
                          if not (l.lstrip().startswith("#")
                                  and l.rstrip().endswith("the fixture")
                                  and set(l.split("#", 1)[1].split("the")[0])
                                  <= set("- ")))

        # A source slice keeps the original formatting and the comment above
        # it, which is worth having — but only when the slice is *exactly* this
        # assignment. `now = time.time(); DAY = 86400` puts two statements on
        # one line, and slicing carried `time.time()` into a file that no
        # longer imports time, so it died at import with NameError. Parse the
        # slice back: if it is not one Assign, fall back to unparsing the node,
        # which cannot pick up a neighbour.
        try:
            reparsed = [n for n in ast.parse(block).body]
            usable = len(reparsed) == 1 and isinstance(reparsed[0], ast.Assign)
        except SyntaxError:
            usable = False
        out.append((names[0], block if usable else ast.unparse(node)))
    return out


def title_of(src: str) -> str:
    """The original module docstring's first line, kept as the new one's."""
    try:
        doc = ast.get_docstring(ast.parse(src)) or ""
    except SyntaxError:
        doc = ""
    first = (doc.strip().splitlines() or ["Run this skill against its fixture."])[0]
    return first.strip()


def convert(script: Path) -> str | None:
    src = script.read_text()
    fx = fixtures_of(src)
    if not fx:
        return None
    rel = script.relative_to(ROOT).as_posix()
    return TEMPLATE.format(
        title=title_of(src),
        rel=rel,
        fixture="\n\n".join(body for _, body in fx),
        fixture_map=", ".join(f'"{name}": {name}' for name, _ in fx))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="one skill, e.g. grc/control-evidence")
    a = ap.parse_args()

    scripts = sorted((ROOT / "skills").glob("*/*/scripts/*.py"))
    if a.only:
        scripts = [s for s in scripts
                   if f"{s.parents[2].name}/{s.parents[1].name}" == a.only]

    done, skipped = [], []
    for s in scripts:
        ref = f"{s.parents[2].name}/{s.parents[1].name}"
        new = convert(s)
        if new is None:
            skipped.append(ref)
            continue
        try:
            ast.parse(new)          # never write a file that will not parse
        except SyntaxError as e:
            skipped.append(f"{ref} (generated source invalid: {e})")
            continue
        if not a.dry_run:
            s.write_text(new)
        done.append(ref)

    print(f"{len(done)} script(s) {'would be ' if a.dry_run else ''}rewritten "
          f"as model harnesses")
    if skipped:
        print(f"\n{len(skipped)} left alone — no module-level literal fixture, "
              f"so there is nothing to carry across safely:")
        for r in skipped:
            print(f"   {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
