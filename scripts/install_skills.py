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

Windows: symlinks need Developer Mode or an elevated shell. Where they are
unavailable this says so and suggests `--copy`, which is honest about being a
snapshot rather than pretending it is a link.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "skills"

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
}


def skills() -> list[Path]:
    """Every skill directory in the store. `_runtime` is a library, not a skill."""
    return sorted(p.parent for p in STORE.glob("*/*/SKILL.md")
                  if not p.parent.parent.name.startswith("_"))


def collisions() -> dict[str, list[str]]:
    """Skill names claimed by more than one area.

    Flattening is only safe while these are empty. Checked rather than assumed,
    because the day somebody adds `detection/triage-report` next to
    `appsec/triage-report` the install would silently link one and drop the
    other.
    """
    seen: dict[str, list[str]] = {}
    for d in skills():
        seen.setdefault(d.name, []).append(f"{d.parent.name}/{d.name}")
    return {k: v for k, v in seen.items() if len(v) > 1}


def link_one(src: Path, dst: Path, *, copy: bool, dry: bool) -> str:
    """Return what happened: linked, relinked, copied, kept, or an error."""
    if dst.is_symlink():
        if dst.resolve() == src.resolve():
            return "already linked"
        if dry:
            return f"would relink (points at {os.readlink(dst)})"
        dst.unlink()
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
        return (f"FAILED — {e}. On Windows, enable Developer Mode or use "
                f"--copy.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tool", action="append", choices=sorted(TOOLS),
                    help="install for this tool; repeatable")
    ap.add_argument("--all", action="store_true",
                    help="every tool whose directory already exists")
    ap.add_argument("--list", action="store_true", help="show what is installed")
    ap.add_argument("--uninstall", action="store_true",
                    help="remove links this script made; never touches a real directory")
    ap.add_argument("--copy", action="store_true",
                    help="copy instead of linking. A snapshot; it will not track edits")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    all_skills = skills()
    if dup := collisions():
        print("REFUSING: these skill names appear in more than one area, so a "
              "flat install would drop one of each:", file=sys.stderr)
        for name, where in sorted(dup.items()):
            print(f"   {name}: {', '.join(where)}", file=sys.stderr)
        return 1

    if a.list:
        print(f"{len(all_skills)} skill(s) in {STORE.relative_to(ROOT)}\n")
        for tool, path in sorted(TOOLS.items()):
            if not path.exists():
                print(f"  {tool:<10} {path}  (not present)")
                continue
            linked = sum(1 for d in path.iterdir()
                         if d.is_symlink() and STORE in d.resolve().parents)
            other = sum(1 for d in path.iterdir() if d.is_dir() and not d.is_symlink())
            print(f"  {tool:<10} {path}  —  {linked} linked here, {other} of its own")
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

    rc = 0
    for tool in targets:
        dest = TOOLS[tool]
        print(f"\n{tool} — {dest}")
        counts: dict[str, int] = {}
        for src in all_skills:
            if a.uninstall:
                dst = dest / src.name
                if dst.is_symlink() and dst.resolve() == src.resolve():
                    what = "would unlink" if a.dry_run else "unlinked"
                    if not a.dry_run:
                        dst.unlink()
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

    if not a.uninstall and not a.dry_run:
        print("\nEdit a SKILL.md in this repository and every linked tool sees "
              "the change immediately. There is no sync step.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
