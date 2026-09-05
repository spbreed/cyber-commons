#!/usr/bin/env python3
"""Check every counted claim in the documentation against the tree it describes.

    python3 scripts/check_claims.py            # report
    python3 scripts/check_claims.py --check    # CI: non-zero on any drift

A repository that counts itself in prose goes wrong the same way every time:
somebody adds a skill and eleven sentences elsewhere quietly become false. This
session alone, "115 skills", "118 lessons", "the other 117 notebooks", "seven
skills call a model", "eleven plausible tasks" and A0.1's "13 skills import the
runtime" all drifted, and A0.1's drift failed Kaggle verification twice before
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


def facts() -> dict[str, int]:
    """What is actually true, measured from the tree."""
    nb = sorted(glob.glob(str(ROOT / "labs/notebooks/*.ipynb")))
    cells = [json.loads(Path(f).read_text())["cells"] for f in nb]
    cur = json.loads((ROOT / "site/data/curriculum.json").read_text())
    routing = (ROOT / "scripts/check_skills.py").read_text()
    cases = routing.split("ROUTING_CASES = [", 1)[1].split("\n]", 1)[0]
    listed = subprocess.run([sys.executable, str(ROOT / "scripts/live_model_test.py"),
                             "--list"], capture_output=True, text=True)
    return {
        "skills": len(list((ROOT / "skills").rglob("SKILL.md"))),
        "notebooks": len(nb),
        "run_a_skill": sum(1 for c in cells
                           if any(x["cell_type"] == "code" for x in c)),
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
    }


# (file, regex with ONE numeric group, fact key, what the sentence claims)
# Keep this list short. A claim that needs an entry here is usually a claim
# that should have been a printed count instead.
CLAIMS = [
    ("README.md", r"\*\*(\d+) lessons across \d+ chapters\.\*\*", "sessions",
     "the headline lesson count"),
    ("README.md", r"\*\*\d+ lessons across (\d+) chapters\.\*\*", "chapters",
     "the headline chapter count"),
    ("README.md", r"they \*\*run a skill\*\*\. (\d+) of the \d+ do", "run_a_skill",
     "how many lessons execute something"),
    ("README.md", r"Every one of the (\d+) is executed in CI", "notebooks",
     "the CI coverage claim"),
    ("README.md", r"skills/\s+(\d+) agent skills", "skills",
     "the layout listing"),
    ("README.md", r"labs/notebooks/\s+(\d+) generated notebooks", "notebooks",
     "the layout listing"),
    ("README.md", r"source of truth: (\d+) sessions", "sessions",
     "the layout listing"),
    ("README.md", r"\*\*Every one of the (\d+) notebooks has been run twice",
     "notebooks", "the Kaggle verification claim"),
    ("README.md", r"and every one of the (\d+) carries\s*\n\s*a script", "skills",
     "the script-per-skill claim"),
    ("LESSON_DESIGN.md", r"Every one of the (\d+) lessons has the same shape",
     "sessions", "the authoring contract's opening"),
    ("skills/README.md", r"^(\d+) skills the curriculum teaches", "skills",
     "the skills index"),
    ("skills/README.md", r"that (\d+) plausible tasks", "routing_cases",
     "the routing check's size"),
    ("MODELS.md", r"The (six|seven|eight) model-facing lessons were run",
     "model_facing", "how many lessons call a model"),
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
