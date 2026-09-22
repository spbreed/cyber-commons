#!/usr/bin/env python3
"""Generate the skill a learner picks to do a lesson, from the lesson's own sources.

    python3 scripts/build_lesson_skills.py            # write lesson-skills/
    python3 scripts/build_lesson_skills.py --check    # CI: nothing stale, nothing loose

A learner should not have to open a terminal to learn a lesson. They pick one
skill in their own agent — `/a1-1-the-loop` in Claude Code, the same name in
Codex, Cursor or Copilot — and the agent teaches the idea, gets the code that
lesson adds, runs it, and says what happened. This writes that skill.

**Generated, never hand-edited.** The name, the teaching text and the audit it
calls all come from `site/data/curriculum.json` and `scripts/exercises/`, the
same sources the page renders from, so the page and the skill cannot describe
two different lessons. Which lessons exist as skills yet is
`exercises/lessonskills.py`.

**It calls the audit skill; it does not copy it.** The procedure for the audit
stays in `skills/<area>/<name>/SKILL.md`, the one place it is written down. The
lesson skill is the driver: teach, get the code, run, read back.

What `--check` refuses, and why each is a real failure:

  * a lesson skill that is stale against its sources — somebody changed a
    lesson and the skill still teaches the old one;
  * a directory in `lesson-skills/` that no lesson owns — a skill
    for a lesson that was renamed or removed still loads and still answers;
  * a skill whose name does not match its directory, or whose description does
    not open with its lesson id — the id is how a learner finds it;
  * an audit the skill names that is not in `skills/` — the lesson would tell a
    learner to run something that is not there.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from exercises import EXERCISES                                # noqa: E402
from exercises.lessonskills import (LESSON_IDS, RUNTIME_LESSONS,  # noqa: E402
                                    audit_kind, audits_of, skill_name)

OUT = ROOT / "lesson-skills"
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf8"))


def sessions() -> dict[str, dict]:
    return {s["id"]: s for f in CUR["functions"] for t in f["tracks"]
            for s in t["sessions"]}


def prose_of(sid: str) -> str:
    """The lesson's teaching text, as markdown: the concept, then the steps.

    HTML steps (tables, diagrams) are left out because an agent reads
    markdown, and the page still carries them. The audit's own SKILL.md is not
    repeated here either; the lesson skill points at it.
    """
    ex = EXERCISES[sid]
    parts = [ex["concept"].strip()]
    for kind, source in ex.get("steps", []):
        if kind == "md" and isinstance(source, str):
            parts.append(source.replace("\\n", "\n").strip())
        elif kind == "fold":
            # Folded on the page, not hidden from the agent: it still has to
            # be able to help a learner who opens it.
            for k, s in source[1]:
                if k == "md" and isinstance(s, str):
                    parts.append(s.replace("\\n", "\n").strip())
    return "\n\n".join(parts)


def _one_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def audit_instructions(sid: str, audits: list[tuple[str, str]]) -> str:
    """Step 3 of the procedure: what the agent does about the lesson's audit(s).

    Written per audit *kind*, because the three are different jobs and telling
    an agent to answer a worked example, or to skip a question it was meant to
    answer, is how a lesson quietly stops teaching what it says it does.
    """
    if not audits:
        return ("3. This lesson has no audit to run; the harness says so in its "
                "readback. Read the concept together instead.")
    blocks = []
    for n, (ref, script) in enumerate(audits, 1):
        kind = audit_kind(script)
        flag = f" --audit {n}" if len(audits) > 1 else ""
        head = f"audit {n} of {len(audits)}, `skills/{ref}`" if len(audits) > 1 \
            else f"the audit, `skills/{ref}`"
        if kind == "demo":
            blocks.append(
                f"   - {head[0].upper() + head[1:]}, is a **worked example with no "
                f"model in it**. The harness runs it itself and its output is the "
                f"result. Do not answer anything for it.")
        elif sid in RUNTIME_LESSONS:
            blocks.append(
                f"   - {head[0].upper() + head[1:]}, shows whether *this computer's "
                f"runtime* can reach a model, so the harness tries the runtime "
                f"first. If it prints the audit's task instead, the runtime has "
                f"no model and you answer it, as below. That is fine: a "
                f"learner using an assistant does not need the runtime.")
        else:
            blocks.append(
                f"   - {head[0].upper() + head[1:]}, **asks you a question**. You are "
                f"the model. The harness prints the audit's task; answer it "
                f"yourself, following the audit skill's procedure, with one JSON "
                f"object written to `work/answer.json`, then run "
                f"`PY scripts/lesson.py {sid}{flag} --answer work/answer.json`.")
    tail = ("   The readback printed *before* you answer is provisional; the "
            "one after `--answer` is the one to read to the learner. The harness "
            "checks your answer against the audit's own output contract and says "
            "how many places it broke it. Never fill in a number you did not "
            "derive from the task. If you cannot answer, say so; a made-up answer "
            "has the right shape and passes the check.")
    if not any(audit_kind(s) == "model" for _, s in audits):
        tail = ""
    order = ("   This lesson runs several audits: do them in order, one "
             "readback each.\n" if len(audits) > 1 else "")
    return ("3. **The audit.**\n" + "\n".join(blocks) + ("\n" + order if order
            else "\n") + (tail if tail else "")).rstrip("\n")


def render_skill(sid: str, s: dict) -> str:
    name = skill_name(sid, s["title"])
    ex = EXERCISES[sid]
    title = s["title"]
    desc = (f"{sid} — {title.split(' — ')[0]}. Do this lesson: explains the idea "
            f"in plain words, gets the CyberTravels code as it stood at the end "
            f"of {sid}, runs it, and reports what happened. Use when working "
            f"through lesson {sid} or when asked to do {sid}.")
    if len(desc) > 400:
        raise SystemExit(f"{sid}: description is {len(desc)} characters; an "
                         f"agent loads it for every skill at startup")

    audits = audits_of(sid)
    audit_step = audit_instructions(sid, audits)

    challenge = (ex.get("challenge") or "").strip()
    hook = _one_line(ex.get("hook") or "")
    audit_line = (", ".join(f"`skills/{r}`" for r, _ in audits) if audits
                  else "none — this is a reading lesson")

    return f"""---
name: {name}
description: >-
  {desc}
license: Apache-2.0
allowed-tools: Read, Glob, Bash
metadata:
  commons-lesson: {sid}
  commons-audit: {", ".join(r for r, _ in audits) if audits else "none"}
  commons-generated: scripts/build_lesson_skills.py
---

<!-- Generated by scripts/build_lesson_skills.py from the lesson's sources.
     Edit scripts/exercises/ or site/data/curriculum.json, not this file. -->

# {sid} — {title}

{hook}

## When to use this

The learner wants to do lesson **{sid}**: they typed `/{name}`, picked it from
their agent's skill list, or asked to "do {sid}". One skill is one lesson, and
the learner never has to type a command themselves: you run them.

## Before you start

1. **Be in the repository.** `scripts/lesson.py` must exist in the current
   folder. If it does not, ask the learner to open the `cyber-commons` folder
   they cloned in their agent and start again.
2. **Find the Python command.** Try `python3 --version`. On Windows that name is
   often a Microsoft Store shortcut that prints "Python was not found" or exits
   with 49; if so use `python`, then `py -3`. Call the one that works `PY`
   below, and use it for every command.

## Procedure

1. **Teach it first.** Read `references/lesson.md`, next to this file, and
   explain the idea to the learner in plain words *before* running anything.
   The idea comes before the code. Assume they have never written code unless
   they have told you otherwise; define a term the first time you use it.
2. **Run the lesson.** From the repository root:
   `PY scripts/lesson.py {sid}`. It gets the CyberTravels code as it stood at
   the end of {sid} into `work/cybertravels`, shows what this lesson added,
   runs the tests that exist at this point, and runs the audit
   ({audit_line}). It ends with a READBACK.
{audit_step}
4. **Say what happened.** Read the READBACK to the learner in your own words,
   under its four headings: **What I did**, **What changed**, **The number**,
   **Read this next**. Use only what it printed. If it says a step was skipped
   or refused, say that plainly and pass on the fix it gave; a skipped step is
   not a pass.
5. **Give them the exercise.**{" " + challenge if challenge else " This lesson has none."}
6. **Point at the next lesson**, from the readback's last heading.

## The readback

`scripts/lesson.py` always ends with the same four headings, so a learner
learns where to look. Every line is derived from something the harness ran; it
never prints a number it did not measure. Where a lesson has no number, it says
what to count instead.

## Failure modes

- **`python3` prints "Python was not found".** The Windows Store shortcut. Use
  `python` or `py -3`.
- **Exit 2, "no model configured".** Expected on a fresh machine. It is not a
  broken repository; the readback names the fix.
- **A refusal in about two seconds.** A quota or rate-limit rejection, not a
  failure of the lesson. Stop; do not record a result from it.
- **"you have changed files in work/cybertravels".** The harness replaces that
  folder for each lesson and will not overwrite edits. Use `--out` for another
  folder, or `--force` if the learner agrees to lose them.
- **A test is reported skipped.** Say so. `PyJWT` missing is the usual reason,
  and `pip install PyJWT` fixes it.
"""


def render_reference(sid: str, s: dict) -> str:
    ex = EXERCISES[sid]
    challenge = (ex.get("challenge") or "").strip()
    out = [f"# {sid} — {s['title']}", "",
           "<!-- Generated by scripts/build_lesson_skills.py. -->", "",
           prose_of(sid)]
    if challenge:
        out += ["", "## Your turn", "", challenge]
    return "\n".join(out) + "\n"


def _orphan_dirs(files: dict) -> set:
    """Directories under lesson-skills/ that no expected file lives in.

    Deepest first when removed, so `<skill>/references/` goes before
    `<skill>/`. Returns only the topmost orphan for reporting, because naming
    both a skill folder and its `references/` child is one fact twice.
    """
    if not OUT.is_dir():
        return set()
    keep = {q for p in files for q in p.parents}
    return {d for d in OUT.iterdir()
            if d.is_dir() and d not in keep}


def expected() -> dict[Path, str]:
    """Every generated file, as {path: text}, written by nobody."""
    have = sessions()
    files: dict[Path, str] = {}
    for sid in sorted(LESSON_IDS):
        if sid not in have:
            raise SystemExit(f"lessonskills.LESSON_IDS names {sid}, which the "
                             f"curriculum does not carry")
        s = have[sid]
        d = OUT / skill_name(sid, s["title"])
        files[d / "SKILL.md"] = render_skill(sid, s)
        files[d / "references" / "lesson.md"] = render_reference(sid, s)
    return files


def problems_with(files: dict[Path, str]) -> list[str]:
    problems: list[str] = []
    for p, text in files.items():
        if p.name != "SKILL.md":
            continue
        d = p.parent.name
        m = re.search(r"^name: (\S+)$", text, re.M)
        if not m or m.group(1) != d:
            problems.append(f"{d}: frontmatter name does not match the directory")
        sid = re.search(r"commons-lesson: (\S+)", text).group(1)
        if not re.search(rf"^  {re.escape(sid)} — ", text, re.M):
            problems.append(f"{d}: description does not open with {sid}")
        a = re.search(r"commons-audit: (.+)", text).group(1).strip()
        for ref in ([] if a == "none" else [x.strip() for x in a.split(",")]):
            if not (ROOT / "skills" / ref / "SKILL.md").is_file():
                problems.append(f"{d}: names the audit skills/{ref}, which is "
                                f"not there")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if anything is stale or loose")
    a = ap.parse_args()

    files = expected()
    problems = problems_with(files)

    on_disk = {p for p in OUT.rglob("*") if p.is_file()} if OUT.is_dir() else set()

    if a.check:
        for p, text in files.items():
            # Compared as bytes' worth of text with newlines normalised: a
            # Windows checkout may have turned LF into CRLF and that is not
            # drift in what the skill says.
            if not p.is_file() or p.read_text(encoding="utf8").replace(
                    "\r\n", "\n") != text:
                problems.append(f"{p.relative_to(ROOT)}: stale — run "
                                f"python3 scripts/build_lesson_skills.py")
        for p in sorted(on_disk - set(files)):
            problems.append(f"{p.relative_to(ROOT)}: not owned by any "
                            f"lesson — a skill for a lesson that "
                            f"was removed still loads and still answers")
        # Directories too, not only files. The build unlinks an orphaned
        # skill's files and left the directory standing, so `--check` — which
        # walked files — reported clean while `lesson-skills/` still carried a
        # folder named for a lesson that had been renumbered away. An empty
        # skill directory does not answer anything, but it is what a reader
        # sees when they list the store, and this gate's whole promise is that
        # nothing in there is unowned.
        for d in sorted(_orphan_dirs(files)):
            problems.append(f"{d.relative_to(ROOT)}/: a directory no lesson "
                            f"owns — its files are gone and the folder is not")
        for p in problems:
            print(f"  FAIL  {p}")
        if problems:
            print(f"::error::{len(problems)} lesson-skill problem(s)",
                  file=sys.stderr)
            return 1
        print(f"ok: {len(LESSON_IDS)} lesson skill(s) up to date "
              f"({', '.join(sorted(LESSON_IDS))})")
        return 0

    if problems:
        for p in problems:
            print(f"  FAIL  {p}")
        return 1
    for p in sorted(on_disk - set(files)):
        p.unlink()
    # Then the directories the unlinking emptied, deepest first.
    for d in sorted(_orphan_dirs(files), key=lambda x: -len(x.parts)):
        for sub in sorted(d.rglob("*"), key=lambda x: -len(x.parts)):
            sub.rmdir() if sub.is_dir() else sub.unlink()
        d.rmdir()
    for p, text in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n": the generated files are compared byte for byte, so a
        # Windows machine must not write CRLF into them.
        with open(p, "w", encoding="utf8", newline="\n") as fh:
            fh.write(text)
    print(f"wrote {len(files)} file(s) for {len(LESSON_IDS)} lesson skill(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
