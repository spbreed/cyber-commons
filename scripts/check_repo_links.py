#!/usr/bin/env python3
"""Every branch-pinned link to this repository points at the published branch.

A lesson page links into the repository constantly — the skills tree, a
`SKILL.md`, the CyberTravels sample, the raw notebook Kaggle fetches. Each of
those URLs carries a branch name, and the name was written out longhand in nine
files. One of them had drifted to a branch that does not exist on the remote at
all: `track_b2.py` linked to `.../tree/main/labs/tools/keycloak-obo`, and there
has never been a `main`. It rendered as an ordinary link and returned 404.

Nothing caught it, because it falls between two gates. `check_docs.py` checks
relative links in Markdown; `check_claude_md.py` checks one file. An absolute
GitHub URL inside a `.py` lesson source is outside both.

So the branch lives in `scripts/exercises/repo.py` and this checks that every
`github.com/<owner>/<repo>/{tree,blob}/…` and `raw.githubusercontent.com/…` in
the tree agrees with it.

    python3 scripts/check_repo_links.py            # report
    python3 scripts/check_repo_links.py --check    # CI: non-zero on drift
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from exercises.repo import BRANCH, NAME, OWNER  # noqa: E402

# Vendored third-party trees, and this file, which spells out a wrong branch on
# purpose to say what went wrong.
SKIP = ("labs/tools/", "scripts/check_repo_links.py", "scripts/exercises/repo.py")

# The branch segment is captured up to the next slash, which is *not* the whole
# branch when it contains one — `claude/vulnbench-…` reports as `claude`. That
# is fine for deciding pass or fail, since anything but an exact match on the
# published branch is a mismatch either way, but the message has to say so
# rather than name a branch nobody wrote.
GITHUB = re.compile(rf"github\.com/{OWNER}/{NAME}/(?:tree|blob)/([^/\s)\"']+)")
RAW = re.compile(rf"raw\.githubusercontent\.com/{OWNER}/{NAME}/([^/\s)\"']+)")


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    keep = (".py", ".md", ".json", ".yml", ".yaml", ".sh", ".ipynb", ".html")
    return [p for p in out
            if p.endswith(keep) and not p.startswith(SKIP) and p not in SKIP]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit non-zero on drift")
    a = ap.parse_args()

    problems, checked = [], 0
    for rel in tracked():
        try:
            text = (ROOT / rel).read_text(errors="ignore")
        except OSError:
            continue
        for pat in (GITHUB, RAW):
            for m in pat.finditer(text):
                checked += 1
                found = m.group(1)
                if found != BRANCH:
                    line = text.count("\n", 0, m.start()) + 1
                    problems.append(f"{rel}:{line} does not pin {BRANCH!r} "
                                    f"(starts {found!r})")

    for p in problems:
        print(f"  FAIL  {p}")
    print(f"\n{checked} branch-pinned link(s) checked against "
          f"exercises/repo.py (branch {BRANCH!r}) · {len(problems)} problem(s)")

    if a.check and problems:
        print(f"::error::{len(problems)} link(s) pin a branch that is not "
              f"{BRANCH}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
