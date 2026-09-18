#!/usr/bin/env python3
"""Check every counted claim in the documentation against the tree it describes.

    python3 scripts/check_claims.py            # report
    python3 scripts/check_claims.py --check    # CI: non-zero on any drift

A repository that counts itself in prose goes wrong the same way every time:
somebody adds a skill and eleven sentences elsewhere quietly become false. This
session alone, "115 skills", "118 lessons", "the other 117 notebooks", "seven
skills call a model", "eleven plausible tasks" and A0.1's "13 skills import the
runtime" all drifted, and A0.4's drift failed Kaggle verification twice before
the cause was fixed rather than the instance.

None of those were caught by a test, because each one is *prose*. This is the
test. Each entry pairs a sentence with the thing it claims, so the number is
compared against the tree rather than against the last time somebody looked.

**The right fix is usually to delete the number, not to update it.** A count in
a sentence has to be maintained; a count printed by a script that inventories
the tree maintains itself. Prefer the second, and use this for the claims that
genuinely belong in prose — the ones on the front page, where a reader needs a
figure to decide whether to keep reading.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from exercises import EXERCISES  # noqa: E402


def facts() -> dict[str, int]:
    """What is actually true, measured from the tree."""
    cur = json.loads((ROOT / "site/data/curriculum.json").read_text())
    routing = (ROOT / "scripts/check_skills.py").read_text()
    cases = routing.split("ROUTING_CASES = [", 1)[1].split("\n]", 1)[0]
    listed = subprocess.run([sys.executable, str(ROOT / "scripts/live_model_test.py"),
                             "--list"], capture_output=True, text=True)
    return {
        "skills": len(list((ROOT / "skills").rglob("SKILL.md"))),
        # Measured from the lesson sources, not from "does the notebook have a
        # code cell". Every notebook is code-only now, including the reading
        # lessons whose single cell is a comment — counting cells would report
        # all 134 as running a skill, which is the claim this exists to check.
        # Restricted to ids the curriculum actually carries: EXERCISES still
        # holds three orphans from the Function C trim, and they are not lessons.
        "run_a_skill": sum(
            1 for sid, ex in EXERCISES.items()
            if sid in {s["id"] for f in cur["functions"] for t in f["tracks"]
                       for s in t["sessions"]}
            and any(k in ("py", "skill_script", "model")
                    for k, _ in ex.get("steps", []))),
        "sessions": sum(len(t["sessions"]) for f in cur["functions"]
                        for t in f["tracks"]),
        "chapters": sum(len(f["tracks"]) for f in cur["functions"]),
        "functions": len(cur["functions"]),
        "diagrams": len(glob.glob(str(ROOT / "site/assets/diagrams/*.svg"))),
        "model_facing": len(listed.stdout.strip().splitlines()),
        "routing_cases": len(re.findall(r'^\s*"', cases, re.M)),
        "skills_with_script": sum(
            1 for d in (ROOT / "skills").rglob("SKILL.md")
            if list(d.parent.glob("scripts/*.py"))),
        # How many check scripts CI actually invokes. The README counts them,
        # and CLAUDE.md's gate table groups a couple of them onto one row, so
        # the two numbers are allowed to differ — check_claude_md.py is what
        # holds the table itself to the workflow.
        "ci_scripts": len(set(re.findall(
            r"python3 scripts/([a-z_0-9]+\.py)",
            (ROOT / ".github/workflows/pages.yml").read_text()))),
    }


# (file, regex with ONE numeric group, fact key, what the sentence claims)
# Keep this list short. A claim that needs an entry here is usually a claim
# that should have been a printed count instead.
# MODELS.md used to carry "The N model-facing lessons were run against two
# sizes". It was removed rather than updated: the sentence describes one past
# measurement, so a count that tracked the tree would have claimed every lesson
# added afterwards was in a run it was not. That is the case this file's own
# docstring calls for — delete the number, do not maintain it.
CLAIMS = [
    ("README.md", r"\*\*(\d+) lessons across \d+ chapters\.\*\*", "sessions",
     "the headline lesson count"),
    ("README.md", r"\*\*\d+ lessons across (\d+) chapters\.\*\*", "chapters",
     "the headline chapter count"),
    ("README.md", r"skill\*\*\. (\d+) of the \d+ do", "run_a_skill",
     "how many lessons execute something"),
    ("README.md", r"It runs (\d+) scripts, each of which", "ci_scripts",
     "how many check scripts CI runs"),
    ("README.md", r"skills/\s+(\d+) agent skills", "skills",
     "the layout listing"),
    ("README.md", r"source of truth: (\d+) sessions", "sessions",
     "the layout listing"),
    ("README.md", r"every one of the (\d+) carries a script the lesson runs", "skills",
     "the script-per-skill claim"),
    # A0.1's "Expect" line describes what the preflight actually prints. It
    # said "120 skills, 119 with a script" while the notebook printed 139/139 —
    # a number a reader checks their own run against, which is the worst kind
    # to have wrong. It also carried "at the time of writing, and the count
    # moves as the commons grows", which is how a number gets permission to be
    # wrong; the hedge is gone and the count is checked instead.
    ("curriculum/labs.json", r"14 areas, (\d+) skills", "skills",
     "A0.1's expected skill count"),
    ("curriculum/labs.json", r"14 areas, \d+ skills, (\d+) with a script",
     "skills_with_script", "A0.1's expected script count"),
    ("LESSON_DESIGN.md", r"Every one of the (\d+) lessons has the same shape",
     "sessions", "the authoring contract's opening"),
    ("skills/README.md", r"^(\d+) skills the curriculum teaches", "skills",
     "the skills index"),
    ("skills/README.md", r"that (\d+) plausible tasks", "routing_cases",
     "the routing check's size"),
]

WORDS = {"six": 6, "seven": 7, "eight": 8}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit non-zero on drift")
    a = ap.parse_args()

    f = facts()
    print("measured from the tree")
    for k, v in sorted(f.items()):
        print(f"   {k:<20}{v}")
    print()

    problems, checked = [], 0
    for path, pattern, key, what in CLAIMS:
        text = (ROOT / path).read_text()
        m = re.search(pattern, text, re.M)
        if not m:
            problems.append(f"{path}: the sentence carrying {what} is gone or "
                            f"reworded — this check no longer protects anything "
                            f"(pattern: {pattern})")
            continue
        checked += 1
        claimed = WORDS.get(m.group(1), None)
        if claimed is None:
            claimed = int(m.group(1))
        if claimed != f[key]:
            problems.append(f"{path}: {what} says {claimed}, tree has "
                            f"{f[key]} — {m.group(0)[:60]!r}")

    for p in problems:
        print(f"  FAIL  {p}")
    print(f"{checked}/{len(CLAIMS)} counted claims checked · "
          f"{len(problems)} problem(s)")
    if problems and a.check:
        print(f"::error::{len(problems)} documentation claim(s) no longer match "
              f"the tree", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
