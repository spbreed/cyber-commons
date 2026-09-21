"""Which lessons are taught by picking a skill in your own agent, and what it is called.

A lesson has two artefacts (CLAUDE.md §2): the page and the audit skill under
`skills/`. A third, `lesson-skills/<name>/`, is what a learner actually picks in
Claude Code, Codex, Cursor or Copilot: one per lesson, named for the lesson, so
typing `a1` lists A1.x in order. It is generated from the lesson's own sources
by `scripts/build_lesson_skills.py`, and it calls the audit skill rather than
copying it.

It is a separate layer and not a rename of the audit skills because they are
shared. Eighteen audits are used by two or three lessons each — the A1 and A2
audits are all reused later by B, C, D or E, and `run-replayability-audit`
serves A2.1, D1.10 and E5.1 — so an audit cannot be named for one lesson
without being wrong for the others.

Everything that has to agree on which lessons are converted reads it from here:
the generator, the page builder, the harness, and the gates that check them.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# Functions converted so far, by letter. A function is added here in the same
# commit as its regenerated skills and pages, and never before: a page that
# tells a learner to pick a skill that is not in `lesson-skills/` is a broken
# first step, which is worse than the old run block. Lessons inside a converted
# function need no entry of their own — a new lesson takes the skill treatment
# from the moment it is in the curriculum, and `build_lesson_skills.py --check`
# fails until its skill is generated.
FUNCTIONS: frozenset[str] = frozenset({"A"})


def _lesson_ids() -> list[str]:
    cur = json.loads((ROOT / "site" / "data" / "curriculum.json")
                     .read_text(encoding="utf8"))
    return [s["id"] for f in cur["functions"] for t in f["tracks"]
            for s in t["sessions"]]


ROLLED_OUT: frozenset[str] = frozenset(
    sid for sid in _lesson_ids() if sid[0] in FUNCTIONS)

# Lessons whose audit *is* a test of the runtime reaching a model. The harness
# tries the runtime first for these, because showing whether this machine's
# runtime can call a model is what the lesson is for. If it cannot, the agent
# answers the audit itself, like every other lesson, so a learner whose only
# model is their assistant is not stopped by a check that concerns a route they
# are not using.
RUNTIME_LESSONS: frozenset[str] = frozenset({"A0.0", "A0.1"})


def slug(title: str) -> str:
    """The lesson's short name: its title before the first dash.

    Titles are "Name — what it covers", and the part after the dash is a
    sentence, not a name. A few have a comma instead ("The audit trail, and the
    four questions it has to answer"), which cuts the same way.
    """
    head = re.split(r"\s+[—–-]\s+|,\s+", title, maxsplit=1)[0]
    s = re.sub(r"[^a-z0-9]+", "-", head.lower()).strip("-")
    return s[:40].rstrip("-") or "lesson"


def skill_name(sid: str, title: str) -> str:
    """`A1.1` + "The loop — …" -> `a1-1-the-loop`.

    Lowercase and hyphenated because the agentskills.io format requires the
    directory name to match the frontmatter name, and every agent loads it
    from there. The id leads so the names sort in lesson order.
    """
    return f"{sid.lower().replace('.', '-')}-{slug(title)}"


def matches(sid: str, selector: str) -> bool:
    """Does a lesson id fall under `A`, `A1`, `A1.1` or `all`?

    A chapter is `A1` and its lessons are `A1.0`, `A1.1` … so the chapter
    test needs the dot, or `A1` would also claim `A10.0` if that ever existed.
    """
    sel = selector.strip()
    if sel.lower() == "all":
        return True
    if re.fullmatch(r"[A-Za-z]", sel):
        return sid[0].upper() == sel.upper()
    if re.fullmatch(r"[A-Za-z]\d+", sel):
        return sid.upper().startswith(sel.upper() + ".")
    return sid.upper() == sel.upper()


def audits_of(sid: str) -> list[tuple[str, str]]:
    """[(`area/name`, script path under skills/)] in the order the lesson runs them.

    Read from the lesson's own steps — the same place `check_claims.py` and the
    page builder read it — so there is one answer to "which skills does this
    lesson run". Ten lessons run two or three.
    """
    from . import EXERCISES
    refs, scripts = [], []
    for kind, value in EXERCISES.get(sid, {}).get("steps", []):
        if kind == "skill":
            refs.append(value)
        elif kind == "skill_script":
            scripts.append(value)
    return list(zip(refs, scripts))


def audit_kind(script: str | Path) -> str:
    """`model` if an agent can answer this audit, `demo` if it only runs.

    A model audit has the shape every generated skill script has: a module
    level `SKILL` and a `task()` that returns the input, which is what lets an
    agent be handed the prompt and its answer be checked against the contract.
    Nine audits are deterministic demonstrations with neither — they print a
    worked example and call no model, so there is nothing to answer.

    Read from the syntax tree, never by importing: a demo does its work at
    import, so importing one to ask what it is would run it.
    """
    p = script if isinstance(script, Path) else ROOT / "skills" / script
    tree = ast.parse(p.read_text(encoding="utf8"))
    has_task = any(isinstance(n, ast.FunctionDef) and n.name == "task"
                   for n in tree.body)
    has_skill = any(isinstance(n, ast.Assign)
                    and any(getattr(t, "id", None) == "SKILL" for t in n.targets)
                    for n in tree.body)
    return "model" if has_task and has_skill else "demo"
