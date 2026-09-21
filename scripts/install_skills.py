#!/usr/bin/env python3
"""Link this repository's skills into whichever agent CLIs you use.

One central store, many tools. `skills/<area>/<name>/` is the only copy that
exists; every coding agent gets a **symlink** to it, so editing a `SKILL.md`
here is immediately live in Claude Code, Codex, Gemini CLI and the rest. No
sync step, nothing to remember, and no chance of two tools running different
versions of the same procedure.

    ~/.claude/skills/appsec-vuln-audit  ->  <repo>/skills/appsec/appsec-vuln-audit
    ~/.codex/skills/appsec-vuln-audit   ->  the same directory
    ~/.gemini/skills/appsec-vuln-audit  ->  the same directory

**Why symlinks and not copies.** A copy is a fork with a friendly name. The
first time you fix a skill you fix it in one place and three tools keep the
bug, and nothing tells you — the other copies still load, still validate, and
still answer. The link cannot drift because there is nothing to drift from.

**Why the layout changes.** The commons files skills by area
(`skills/appsec/…`) because 141 skills in one directory is unreadable. Agents
expect a flat `skills/<name>/`, with the directory name matching the `name` in
the frontmatter — that is the agentskills.io rule. So each link is made
individually, flattened. There are no name collisions across areas; this
script checks before it writes.

    python3 scripts/install_skills.py --list          # what is installed where
    python3 scripts/install_skills.py --tool claude   # link into one tool
    python3 scripts/install_skills.py --all           # every tool it can find
    python3 scripts/install_skills.py --all --dry-run
    python3 scripts/install_skills.py --tool claude --uninstall

**Two stores.** `skills/<area>/<name>/` holds the audit skills, the procedures.
`lesson-skills/<name>/` holds one skill per lesson, named `a1-1-the-loop`, which
is what a learner picks in their agent to do a lesson. Both are linked, never
copied. Without `--lessons` this links the audits, as it always has; with it,
only the lesson skills unless `--audits` is added:

    python3 scripts/install_skills.py --all --lessons A     # every A lesson
    python3 scripts/install_skills.py --all --lessons A0.0  # one lesson
    python3 scripts/install_skills.py --tool copilot --lessons A

**Windows.** A symlink needs Developer Mode or an elevated shell, but a
directory *junction* does not, and for a directory it is the same thing to
everything that reads it: one folder, no copy, edits visible at once. So a
failed symlink falls back to a junction, and only if that fails too does this
say so and suggest `--copy`, which is honest about being a snapshot.

**GitHub Copilot** reads project skills from `.github/skills/` inside the
repository, so `--tool copilot` links there rather than into your home
directory. **Codex** reads `.agents/skills/` (Cursor and Copilot read it too),
which is `--tool agents`. Those links are machine-specific, so both folders are
gitignored.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from exercises.lessonskills import matches  # noqa: E402

STORE = ROOT / "skills"
LESSONS = ROOT / "lesson-skills"
STORES = (STORE, LESSONS)

# Where each agent looks for skills. All of them follow the same convention —
# a directory per skill, named for the skill — because they implement the same
# open format. Adding a tool is one row.
TOOLS = {
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "gemini": Path.home() / ".gemini" / "skills",
    "cursor": Path.home() / ".cursor" / "skills",
    "opencode": Path.home() / ".opencode" / "skills",
    "goose": Path.home() / ".config" / "goose" / "skills",
    # Copilot loads project skills from the repository itself, not from $HOME.
    "copilot": ROOT / ".github" / "skills",
    # The shared project location: Codex reads `.agents/skills` (its docs list
    # no `~/.codex/skills`, which is what the `codex` row above still points
    # at), and Cursor and Copilot read it as well.
    "agents": ROOT / ".agents" / "skills",
}


def skills() -> list[Path]:
    """Every audit skill directory in the store. `_runtime` is a library, not a skill."""
    return sorted(p.parent for p in STORE.glob("*/*/SKILL.md")
                  if not p.parent.parent.name.startswith("_"))


def lesson_skills(selector: str | None = None) -> list[Path]:
    """The per-lesson skills, optionally only those a selector names.

    The lesson id is read from each skill's own `commons-lesson:` line rather
    than from its directory name, so the selection cannot disagree with the
    skill about which lesson it is.
    """
    out = []
    for p in sorted(LESSONS.glob("*/SKILL.md")):
        m = re.search(r"commons-lesson:\s*(\S+)", p.read_text(encoding="utf8"))
        if selector is None or (m and matches(m.group(1), selector)):
            out.append(p.parent)
    return out


def collisions() -> dict[str, list[str]]:
    """Skill names claimed by more than one place.

    Flattening is only safe while these are empty. Checked rather than assumed,
    because the day somebody adds `detection/triage-report` next to
    `appsec/triage-report` the install would silently link one and drop the
    other. The lesson skills are in the same flat namespace as the audits, so
    they are checked against them too.
    """
    seen: dict[str, list[str]] = {}
    for d in skills():
        seen.setdefault(d.name, []).append(f"{d.parent.name}/{d.name}")
    for d in lesson_skills():
        seen.setdefault(d.name, []).append(f"lesson-skills/{d.name}")
    return {k: v for k, v in seen.items() if len(v) > 1}


def is_link(p: Path) -> bool:
    """A symlink, or on Windows a directory junction.

    `Path.is_symlink()` is False for a junction, so a junction this script made
    on an earlier run would look like somebody's own directory and be skipped
    rather than recognised. Junctions and symlinks are both reparse points.
    """
    if p.is_symlink():
        return True
    if os.name == "nt":
        try:
            return bool(os.lstat(p).st_file_attributes
                        & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except (OSError, AttributeError):
            return False
    return False


def points_into_stores(p: Path) -> bool:
    try:
        target = p.resolve()
    except OSError:
        return False
    return any(s in target.parents for s in STORES)


def unlink_link(p: Path) -> None:
    """Remove a link without touching what it points at.

    `unlink()` on a junction raises; `rmdir()` removes the junction itself and
    leaves the target alone, which is what is wanted.
    """
    if p.is_symlink():
        p.unlink()
    else:
        os.rmdir(p)


def make_junction(src: Path, dst: Path) -> None:
    try:
        import _winapi
        _winapi.CreateJunction(str(src), str(dst))
    except (ImportError, AttributeError, OSError):
        r = subprocess.run(["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise OSError(r.stdout.strip() or r.stderr.strip() or "mklink failed")


def link_one(src: Path, dst: Path, *, copy: bool, dry: bool) -> str:
    """Return what happened: linked, relinked, copied, kept, or an error."""
    if is_link(dst):
        if dst.resolve() == src.resolve():
            return "already linked"
        if dry:
            return "would relink (points somewhere else)"
        unlink_link(dst)
    elif dst.exists():
        # A real directory here is somebody's own skill, or an older copy.
        # Never delete it silently — say so and let them decide.
        return "SKIPPED — a real directory is already there, not a link"

    if dry:
        return "would link"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if copy:
        shutil.copytree(src, dst)
        return "copied (a snapshot — it will not track edits)"
    try:
        dst.symlink_to(src, target_is_directory=True)
        return "linked"
    except OSError as e:
        if os.name == "nt":
            try:
                make_junction(src, dst)
                return "linked (junction — needs no Developer Mode)"
            except OSError as e2:
                return (f"FAILED — no symlink ({e}) and no junction ({e2}). "
                        f"Enable Developer Mode, or use --copy.")
        return f"FAILED — {e}. Use --copy for a snapshot."


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tool", action="append", choices=sorted(TOOLS),
                    help="install for this tool; repeatable")
    ap.add_argument("--all", action="store_true",
                    help="every tool whose directory already exists")
    ap.add_argument("--lessons", metavar="SEL",
                    help="link the per-lesson skills for SEL: a function (A), a "
                         "chapter (A1), a lesson (A1.1) or all. Audits are not "
                         "linked unless --audits is also given")
    ap.add_argument("--audits", action="store_true",
                    help="with --lessons: also link the audit skills")
    ap.add_argument("--list", action="store_true", help="show what is installed")
    ap.add_argument("--uninstall", action="store_true",
                    help="remove links this script made; never touches a real directory")
    ap.add_argument("--copy", action="store_true",
                    help="copy instead of linking. A snapshot; it will not track edits")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    all_skills = skills()
    if dup := collisions():
        print("REFUSING: these skill names appear in more than one place, so a "
              "flat install would drop one of each:", file=sys.stderr)
        for name, where in sorted(dup.items()):
            print(f"   {name}: {', '.join(where)}", file=sys.stderr)
        return 1

    if a.list:
        every_lesson = lesson_skills()
        print(f"{len(all_skills)} audit skill(s) in {STORE.relative_to(ROOT)}, "
              f"{len(every_lesson)} lesson skill(s) in "
              f"{LESSONS.relative_to(ROOT)}\n")
        for tool, path in sorted(TOOLS.items()):
            if not path.exists():
                print(f"  {tool:<10} {path}  (not present)")
                continue
            entries = [d for d in path.iterdir() if d.is_dir()]
            mine = [d for d in entries if is_link(d) and points_into_stores(d)]
            audits = sum(1 for d in mine if STORE in d.resolve().parents)
            lessons = sorted(d.name for d in mine if LESSONS in d.resolve().parents)
            other = len(entries) - len(mine)
            print(f"  {tool:<10} {path}  —  {audits} audit(s) and "
                  f"{len(lessons)} of {len(every_lesson)} lesson skill(s) "
                  f"linked, {other} of its own")
            for name in lessons:
                print(f"               {name}")
        return 0

    targets = list(a.tool or [])
    if a.all:
        # Only tools that are actually installed. Creating ~/.gemini for
        # somebody who does not use Gemini is litter, not helpfulness.
        targets = [t for t, p in TOOLS.items() if p.parent.exists()]
        if not targets:
            print("No agent CLI directories found. Name one with --tool, and it "
                  "will be created.", file=sys.stderr)
            return 1
    if not targets:
        ap.error("choose --tool, --all, or --list")

    # What to link. Bare, this is the audits, as before. With --lessons it is
    # the lesson skills a learner picks, and only those: linking 139 audits
    # next to them would bury the lesson names in a list nobody asked for.
    chosen: list[Path] = []
    if a.lessons:
        chosen += lesson_skills(a.lessons)
        if not chosen:
            print(f"No lesson skill matches {a.lessons!r}. Lessons are converted "
                  f"a few at a time; `--list` shows which exist.", file=sys.stderr)
            return 1
        if a.audits:
            chosen += all_skills
    else:
        chosen = all_skills

    rc = 0
    for tool in targets:
        dest = TOOLS[tool]
        print(f"\n{tool} — {dest}")
        counts: dict[str, int] = {}
        for src in chosen:
            if a.uninstall:
                dst = dest / src.name
                if is_link(dst) and dst.resolve() == src.resolve():
                    what = "would unlink" if a.dry_run else "unlinked"
                    if not a.dry_run:
                        unlink_link(dst)
                elif dst.exists():
                    what = "left alone — not a link to this store"
                else:
                    continue
            else:
                what = link_one(src, dest / src.name, copy=a.copy, dry=a.dry_run)
            counts[what] = counts.get(what, 0) + 1
            if what.startswith(("SKIPPED", "FAILED")):
                print(f"   {src.name}: {what}")
                rc = 1
        for what, n in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"   {n:4d}  {what}")

    if not a.uninstall and not a.dry_run and rc == 0:
        print("\nEdit a SKILL.md in this repository and every linked tool sees "
              "the change immediately. There is no sync step.")
        if a.lessons:
            print("Restart your agent (or reload its skills), open it in this "
                  "folder, and pick a lesson skill by name.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
