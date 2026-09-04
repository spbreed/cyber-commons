#!/usr/bin/env python3
"""Generate one self-contained Jupyter notebook per lesson.

    labs/notebooks/<ID>.ipynb      one per session, 99 of them

Inputs (the same single source of truth the site builds from):
    site/data/curriculum.json     structure, risk, control, tools, models
    curriculum/labs.json          the goal and expected-output line
    scripts/exercises/            the per-session exercise body (code + prose)

**Self-contained by design.** A notebook carries every line of code it runs —
there is no shared library to import and nothing to clone. That is what makes
it work on a Kaggle kernel with the internet switched off, and it means a
reader can copy one cell into their own repository without inheriting a
dependency. Standard library only.

**One concept, in one order.** Each lesson is built the same way and only that
way — see LESSON_DESIGN.md for the authoring contract:

    1. The hook           why this matters, in three sentences
    2. The framework      the diagram first, then the idea it names
    3..n Practical        the concept working, where it breaks, the control
    What you just proved  the expected output, stated before you run it
    Your turn             the same thing against a system you own
    Where this leaves you the bridge, on the last lesson of a chapter

Leading with the risk teaches people to fear a mechanism they cannot yet
describe, and leading with a terminal teaches the "how" before the "why". Both
orders are enforced structurally: `hook`, `diagram` and `concept` are required
fields, the framework is rendered before any code cell, and the build fails
without them.

    python3 scripts/build_notebooks.py           # write them all
    python3 scripts/build_notebooks.py --check   # CI: fail if any is stale
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
LABS = json.loads((ROOT / "curriculum" / "labs.json").read_text())["labs"]
OUT = ROOT / "labs" / "notebooks"
REPO = "https://github.com/spbreed/cyber-commons"
BRANCH = "claude/vulnbench-setup-scheduling-81aqov"
SITE = "https://spbreed.github.io/cyber-commons"

from exercises import EXERCISES  # noqa: E402
from exercises.about import ABOUT
from exercises.cybertravels import GROUNDING  # noqa: E402
from exercises.framing import BRIDGES  # noqa: E402
from exercises.models import LIVE_MD, MODEL_RUNTIME, live_cell  # noqa: E402

SKILLS = ROOT / "skills"


def skill_source(ref: str) -> str:
    """Embed a real SKILL.md as a Python string, verbatim.

    The file in `skills/` is the single source of truth. Embedding it at build
    time keeps the notebook self-contained *and* makes drift impossible: change
    the skill and the notebook is stale until it is rebuilt, which CI checks.
    """
    path = SKILLS / ref / "SKILL.md"
    if not path.is_file():
        raise FileNotFoundError(f"no such skill: skills/{ref}/SKILL.md")
    text = path.read_text()
    # r"""…""" keeps the markdown readable in the notebook, but only if the
    # content cannot terminate the literal or escape it.
    if '"""' in text:
        raise ValueError(f"skills/{ref}/SKILL.md contains a triple quote")
    if text.rstrip().endswith("\\"):
        raise ValueError(f"skills/{ref}/SKILL.md ends with a backslash")
    return (f'# skills/{ref}/SKILL.md — embedded verbatim from the repository.\n'
            f'# This is the file itself, not a paraphrase of it.\n'
            f'SKILL_MD = r"""{text}"""\n\n'
            f'meta, body = parse_skill(SKILL_MD)\n'
            f'print(f"loaded skill: {{meta[\'name\']}}")\n'
            f'print(f"  tools it may use: {{\', \'.join(meta.get(\'allowed-tools\', [])) or \'—\'}}")\n'
            f'print(f"  routing description: {{len(meta[\'description\'].split())}} words")\n'
            f'print(f"  procedure: {{len(body.splitlines())}} lines")')

def skill_script(ref: str) -> str:
    """Embed a skill's own script verbatim, so the notebook runs the real file.

    A lesson that reimplements what the skill does teaches the reimplementation.
    Embedding the script keeps the notebook self-contained and makes drift
    impossible: edit the skill and the notebook is stale until rebuilt.
    """
    path = SKILLS / ref
    if not path.is_file():
        raise FileNotFoundError(f"no such skill script: skills/{ref}")
    src = path.read_text()
    # The notebook executes it as a module body rather than a subprocess, so
    # strip the CLI entry point and keep the callables.
    src = src.split('if __name__ == "__main__":')[0].rstrip()
    # `from __future__` is only legal at the top of a file, and this lands in
    # the middle of a notebook. Drop it — every construct these scripts use is
    # available without it on the Python the notebooks target.
    src = "\n".join(ln for ln in src.splitlines()
                    if not ln.startswith("from __future__ import"))
    return (f"# skills/{ref} — embedded verbatim from the repository.\n"
            f"# This is the skill's own script, not a paraphrase of it.\n"
            f"{src}")


DIRECTION = {"defend": "AI for Security", "secure": "Security of AI",
             "both": "Both directions"}


# ------------------------------------------------------------------ ipynb bits
def md(source: str) -> dict:
    # Several exercises were authored with "\\n" inside a normal (non-raw) string,
    # which reaches the notebook as the two characters \ and n and renders as
    # literal text. Markdown never wants that sequence, so normalise it here.
    return {"cell_type": "markdown", "metadata": {},
            "source": _lines(source.replace("\\n", "\n"))}


def code(source: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _lines(source)}


def _lines(text: str) -> list[str]:
    """nbformat stores source as a list of lines, each keeping its newline."""
    text = text.strip("\n")
    parts = text.split("\n")
    return [ln + "\n" for ln in parts[:-1]] + [parts[-1]]


# ------------------------------------------------------------------ assembly
def flatten() -> list[dict]:
    seq = []
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            for i, s in enumerate(tr["sessions"]):
                seq.append({"s": s, "track_id": tr["id"], "track": tr["title"],
                            "last_in_track": i == len(tr["sessions"]) - 1,
                            "fn": f"Function {fn['id']} — {fn['title']}"})
    return seq


SECTION = re.compile(r"^## \d+ · ", re.M)


def renumber(source: str, counter: list[int]) -> str:
    """Rewrite '## 7 · Title' to the next section number in the assembled lesson.

    Exercises carry their own numbering, written when the lesson had a different
    shape. Renumbering here means adding a section to the template never
    requires editing 121 exercise files.
    """
    def one(_m):
        counter[0] += 1
        return f"## {counter[0]} · "
    # Normalise the escaped newline first: a heading that is not at the start
    # of a real line is invisible to the anchor, and several steps were
    # authored with "\\n" inside a non-raw string.
    return SECTION.sub(one, source.replace("\\n", "\n"))


def notebook(entry: dict, prev: dict | None, nxt: dict | None) -> dict:
    s = entry["s"]
    sid = s["id"]
    lab = LABS.get(sid, {})
    ex = EXERCISES.get(sid)
    if ex is None:
        raise KeyError(f"no exercise defined for {sid} — add it to scripts/exercises/")
    for field, why in (
        ("hook", "every lesson opens on why it matters, in three sentences"),
        ("diagram", "the framework is taught as a picture before any terminal"),
        ("concept", "every lesson introduces the idea before it raises the risk"),
    ):
        if not ex.get(field):
            raise KeyError(f"{sid} has no {field!r} — {why}")

    # One line, not three. A reader opening a lesson wants to know what it puts
    # in front of them — open-source packages and models together, in the order
    # they appear. Splitting them across "tooling", "open-weight" and "frontier"
    # rows made the same short list look like three separate prerequisites.
    used = list(dict.fromkeys(
        [*s.get("tools", []), *s.get("open_weight", []), *s.get("frontier", [])]
    ))
    tools_used = ", ".join(used) or "standard library only"

    # ---- header ----------------------------------------------------------
    where = f"**{entry['fn']} → {entry['track']}**  ·  " \
            f"*{DIRECTION.get(s.get('track', 'both'), 'Both directions')}*"
    if prev:
        where += (f"\n\nBuilds on **[{prev['s']['id']} · {prev['s']['title']}]"
                  f"({SITE}/lessons/{prev['s']['id']}.html)**.")
    cells = [md(
        f"# {sid} · {s['title']}\n\n{where}\n\n"
        f"| | |\n|---|---|\n"
        f"| Tools used | {tools_used} |"
    )]

    # ---- 0. what this lesson is, and why a security engineer needs it -----
    # Before the hook, which is a consequence rather than an orientation. A
    # reader landing on one lesson from a search result has no idea what they
    # are looking at until something says so plainly.
    about = ABOUT.get(sid)
    if not about:
        raise KeyError(f"{sid} has no ABOUT entry — every lesson opens by saying "
                       f"what it is and why it matters in a security context; "
                       f"add one to scripts/exercises/about.py")
    cells.append(md(f"## What this lesson is\n\n{about.strip()}"))

    # ---- 1. the hook, and what it looks like at CyberTravels --------------
    hook = f"## 1 · The hook\n\n{ex['hook'].strip()}"
    ground = GROUNDING.get(sid)
    if not ground:
        raise KeyError(f"{sid} has no CyberTravels grounding — every lesson says "
                       f"what its idea looks like in the system the reader has "
                       f"been following")
    hook += (f"\n\n> **At CyberTravels.** {ground.strip()}")
    cells.append(md(hook))

    # ---- 2. the framework: the picture first, then the idea it names ------
    diagram = ex["diagram"].strip("\n")
    cells.append(md(f"## 2 · The framework\n\n```\n{diagram}\n```\n\n"
                    f"{ex['concept'].strip()}"))

    # ---- 3..n the practical application, renumbered from here -------------
    # A markdown step that ends on a bare "## N · Title" was written to
    # introduce a code cell. Once a lesson carries no code, that heading
    # promises something that never arrives, so it is dropped — the callout
    # above it, which is the part that teaches, is kept.
    RUNS = {"py", "skill", "skill_script", "model"}
    steps, n = [], len(ex["steps"])
    for i, (kind, source) in enumerate(ex["steps"]):
        if kind == "md" and isinstance(source, str):
            follows = ex["steps"][i + 1][0] if i + 1 < n else None
            if follows not in RUNS:
                body = source.replace("\\n", "\n").rstrip()
                lines = body.splitlines()
                if lines and lines[-1].lstrip().startswith("## "):
                    body = "\n".join(lines[:-1]).rstrip()
                    if not body:
                        continue
                    source = body
        steps.append((kind, source))

    counter = [2]
    for kind, source in steps:
        if kind == "skill":
            cells.append(code(skill_source(source)))
        elif kind == "skill_script":
            cells.append(code(skill_script(source)))
        elif kind == "model":
            # One adapter, then the same task run for real. The lesson keeps its
            # deterministic replay as the offline default, so CI and the offline
            # Kaggle run are unchanged.
            cells.append(md(renumber("## 2 · " + source.get("title", "The model backend"),
                                     counter)))
            cells.append(code(MODEL_RUNTIME))
            cells.append(md(renumber(LIVE_MD, counter)))
            cells.append(code(live_cell(source["task"], source["replay"],
                                        source.get("system"), source["check"])))
        elif kind in ("md", "html"):
            # An HTML/SVG diagram is markdown too — it just renders as a picture
            # instead of asking the reader to parse a print statement.
            cells.append(md(renumber(source, counter)))
        else:
            cells.append(code(source))

    # ---- close ------------------------------------------------------------
    expect = ex.get("expect") or lab.get("expect", "")
    if expect:
        # A1.1 runs no code at all — it is a drawing lesson — so "proved" would
        # be a lie there.
        # "Proved" is only honest when something ran. A lesson that carries
        # no code cell states what the procedure gives you instead, and one
        # whose `expect` describes an execution it no longer performs is a
        # lesson lying about itself — so the section is dropped entirely there.
        ran = any(k in RUNS for k, _ in steps)
        if ran:
            cells.append(md(f"## What you just proved\n\n{expect}"))
    if challenge := ex.get("challenge"):
        cells.append(md(f"## Your turn\n\n{challenge}"))

    # ---- the knowledge gap, on the last lesson of a chapter ---------------
    if bridge := BRIDGES.get(entry["track_id"]) if entry["last_in_track"] else None:
        cells.append(md(
            f"## Where this leaves you\n\n"
            f"**What you can do now.** {bridge['gained']}\n\n"
            f"**What you still cannot do.** {bridge['gap']}\n\n"
            f"**{bridge['next']}**"))

    foot = ""
    if nxt:
        foot = (f"**Next → [{nxt['s']['id']} · {nxt['s']['title']}]"
                f"({SITE}/lessons/{nxt['s']['id']}.html)**\n\n")
    cells.append(md(
        f"---\n\n{foot}"
        f"[All lessons]({SITE}/lessons/) · "
        f"[This lesson's page]({SITE}/lessons/{sid}.html) · "
        f"[Source]({REPO}/blob/{BRANCH}/labs/notebooks/{sid}.ipynb)\n\n"
        f"*Cyber Commons — a free, open commons for Cyber AI.*"))

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
            "kaggle": {"accelerator": "none", "dataSources": [],
                       "isInternetEnabled": False, "language": "python",
                       "sourceType": "notebook"},
            "cybercommons": {"session": sid, "track": entry["track_id"],
                             "title": s["title"]},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if any notebook is stale")
    a = ap.parse_args()

    seq = flatten()
    missing = [e["s"]["id"] for e in seq if e["s"]["id"] not in EXERCISES]
    if missing:
        print(f"::error::{len(missing)} sessions have no exercise: {missing}", file=sys.stderr)
        return 1

    # A notebook that imports anything outside the standard library cannot run
    # on an offline Kaggle kernel. Catch it here rather than in a reader's browser.
    banned = ("import cybercommons", "from cybercommons", "git clone", "pip install")

    OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for i, e in enumerate(seq):
        sid = e["s"]["id"]
        nb = notebook(e, seq[i - 1] if i else None,
                      seq[i + 1] if i + 1 < len(seq) else None)
        body = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
        for bad in banned:
            if bad in body:
                print(f"::error::{sid} is not self-contained: found {bad!r}", file=sys.stderr)
                return 1
        text = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
        f = OUT / f"{sid}.ipynb"
        if not f.exists() or f.read_text() != text:
            stale.append(sid)
            if not a.check:
                f.write_text(text)

    keep = {f"{e['s']['id']}.ipynb" for e in seq}
    for f in OUT.glob("*.ipynb"):
        if f.name not in keep:
            stale.append(f"{f.name} (removed)")
            if not a.check:
                f.unlink()

    if a.check:
        if stale:
            print(f"::error::labs/notebooks is out of date ({len(stale)}): {stale[:5]}"
                  f"\nRun: python3 scripts/build_notebooks.py", file=sys.stderr)
            return 1
        print(f"ok: {len(seq)} notebooks up to date")
        return 0

    print(f"wrote {len(seq)} self-contained notebooks to labs/notebooks "
          f"({len(stale)} changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
