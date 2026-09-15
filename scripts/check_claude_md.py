#!/usr/bin/env python3
"""Keep CLAUDE.md true, by checking it against the repository it describes.

A context file that has drifted is worse than none: it is read with the same
confidence as a correct one, and it is believed. The counts in it are already
covered by `check_claims.py`; this checks the structural claims, which are the
ones that rot silently when a script is renamed or a gate is removed.

Three rules:

1. **Every script CLAUDE.md names exists.** A doc that sends an agent to
   `scripts/check_foo.py` when there is no such file costs a confused session.

2. **Every gate CLAUDE.md lists in its pre-deployment table is actually in the
   workflow**, and every gate in the workflow is listed. This is the one that
   matters: a gate deleted from CI but still described here reads as protection
   that is not there, and a gate added without a row here is one nobody knows
   the reason for — which is how gates get deleted.

3. **Every repo-relative path it links to exists.**

    python3 scripts/check_claude_md.py            # report
    python3 scripts/check_claude_md.py --check    # CI: non-zero on drift
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "CLAUDE.md"
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"



def scripts_named(text: str) -> set[str]:
    """Script names, however the prose refers to them.

    Paths appear as `scripts/check_foo.py` in the build order and as a bare
    `check_foo.py` in the gate table, where the column is already narrow. Both
    are the same claim, so both count.
    """
    return (set(re.findall(r"scripts/([a-z_0-9]+\.py)", text))
            | set(re.findall(r"`([a-z_0-9]+\.py)[^`]*`", text)))


def gate_scripts_in_workflow() -> set[str]:
    wf = WORKFLOW.read_text()
    return {m for m in re.findall(r"python3 scripts/([a-z_0-9]+\.py)", wf)}


def linked_paths(text: str) -> set[str]:
    out = set()
    for m in re.finditer(r"\]\(([^)#:]+)\)", text):
        p = m.group(1).strip()
        if p.startswith(("http", "mailto", "#")):
            continue
        out.add(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit non-zero on drift")
    a = ap.parse_args()

    if not DOC.is_file():
        print("no CLAUDE.md")
        return 0
    text = DOC.read_text()
    problems = []

    # 1 — every script it names is a file
    named = scripts_named(text)
    for s in sorted(named):
        if not (ROOT / "scripts" / s).is_file():
            problems.append(f"names scripts/{s}, which does not exist")

    # 2 — the doc and the workflow agree, in both directions.
    #
    # An earlier version compared only the gate table against a hand-kept list
    # of "not really gates", which is a second thing to keep in sync and was
    # wrong within an hour: build_notebooks.py and relink_labs.py are build
    # steps when run bare and gates when run with --check. So the invariant is
    # stated without a special case. Every script CI runs is described
    # somewhere in CLAUDE.md, and nothing the gate table promises is absent
    # from CI.
    table = text.split("## 5 · Pre-deployment testing", 1)[-1]
    table = table.split("## 6 ·", 1)[0]
    listed = scripts_named(table)
    running = gate_scripts_in_workflow()
    for s in sorted(running - named):
        problems.append(f"the workflow runs scripts/{s} and CLAUDE.md never "
                        f"mentions it — an agent reading this file would not "
                        f"know it has to pass")
    for s in sorted(listed - running):
        problems.append(f"the gate table lists {s} but the workflow does not "
                        f"run it — this reads as protection that is not there")

    # 3 — every repo-relative link resolves
    for p in sorted(linked_paths(text)):
        if not (ROOT / p).exists():
            problems.append(f"links to {p}, which does not exist")

    for p in problems:
        print(f"  FAIL  {p}")
    print(f"\nCLAUDE.md · {len(named)} script(s) named · {len(listed)} gate(s) "
          f"documented · {len(running)} gate(s) in CI · {len(problems)} problem(s)")

    if a.check and problems:
        print(f"::error::CLAUDE.md has drifted from the repository in "
              f"{len(problems)} place(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
