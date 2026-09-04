#!/usr/bin/env python3
"""Execute every skill in `skills/` and report what actually ran.

`check_skills.py` answers whether a skill can be *loaded*: does the frontmatter
parse, does the contract parse, does routing resolve. This answers the other
half — does the skill **run**, and does its script still work.

A skill is tested three ways, and all three are reported separately because
they fail for different reasons:

  parses      the frontmatter and body split, name matches the directory
  contract    the output contract is valid JSON
  script      the skill's own script executes to completion, standard library
              only, and prints something

The script check runs each file in a subprocess with a stripped environment, so
a skill that quietly depends on a model key, a network path or something a
notebook happened to define is caught here rather than on somebody else's
machine.

    python3 scripts/test_skills.py           # report
    python3 scripts/test_skills.py --check   # CI: non-zero on any failure
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from exercises.skills import SKILL_RUNTIME  # noqa: E402

_ns: dict = {}
exec(SKILL_RUNTIME, _ns)
parse_skill, contract_of = _ns["parse_skill"], _ns["contract_of"]

# Anything that could let a script reach a model, a network or a credential is
# removed. A skill script must be deterministic and offline; if one of these
# variables changes its behaviour, that is the finding.
STRIP = ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL", "ANTHROPIC_API_KEY",
         "ANTHROPIC_WORKSPACE_ID", "ANTHROPIC_BASE_URL",
         "KAGGLE_USERNAME", "KAGGLE_KEY", "KAGGLE_CONFIG_DIR")


def clean_env() -> dict:
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env["PYTHONHASHSEED"] = "0"
    return env


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="non-zero exit on any failure")
    ap.add_argument("--skill", help="test one skill, e.g. threats/tool-scope-abuse-probe")
    a = ap.parse_args()

    paths = sorted((ROOT / "skills").glob("*/*/SKILL.md"))
    if a.skill:
        paths = [p for p in paths if f"{p.parent.parent.name}/{p.parent.name}" == a.skill]
        if not paths:
            sys.exit(f"no such skill: {a.skill}")

    rows, problems = [], []
    for p in paths:
        ref = f"{p.parent.parent.name}/{p.parent.name}"
        row = {"skill": ref, "parses": False, "contract": False,
               "script": None, "lines": 0, "seconds": 0.0}

        try:
            meta, body = parse_skill(p.read_text())
            row["parses"] = meta["name"] == p.parent.name
            if not row["parses"]:
                problems.append(f"{ref}: name {meta['name']!r} != directory")
        except Exception as e:                                  # noqa: BLE001
            problems.append(f"{ref}: will not parse — {e}")
            rows.append(row)
            continue

        try:
            contract_of(body)
            row["contract"] = True
        except Exception as e:                                  # noqa: BLE001
            problems.append(f"{ref}: contract — {e}")

        # The script is optional: a skill whose output is a diagram or a
        # judgement has nothing deterministic to run, and saying so is better
        # than shipping a script that prints a paragraph.
        scripts = sorted((p.parent / "scripts").glob("*.py"))
        if scripts:
            for s in scripts:
                t0 = time.time()
                r = subprocess.run([sys.executable, str(s)], capture_output=True,
                                   text=True, env=clean_env(), cwd=str(ROOT),
                                   timeout=120)
                row["seconds"] = round(time.time() - t0, 2)
                out = r.stdout.strip()
                row["lines"] = len(out.splitlines())
                if r.returncode != 0:
                    row["script"] = False
                    tail = (r.stderr.strip().splitlines() or ["(no stderr)"])[-1]
                    problems.append(f"{ref}: {s.name} exited {r.returncode} — {tail}")
                elif not out:
                    # A script that runs and prints nothing has not been shown
                    # to do anything, which is the failure this catches.
                    row["script"] = False
                    problems.append(f"{ref}: {s.name} ran and printed nothing")
                else:
                    row["script"] = True

        mark = {True: "ok  ", False: "FAIL", None: "  - "}[row["script"]]
        print(f"  {mark} {ref:52s} contract={'y' if row['contract'] else 'N'} "
              f"{row['lines']:4d} lines {row['seconds']:5.2f}s")
        rows.append(row)

    ran = [r for r in rows if r["script"] is True]
    noscript = [r for r in rows if r["script"] is None]
    print(f"\n{len(rows)} skill(s): {len(ran)} executed a script, "
          f"{len(noscript)} carry none, {len(problems)} problem(s)")
    for pr in problems:
        print(f"::error::{pr}", file=sys.stderr)

    (ROOT / "labs" / "notebooks" / "_skill_tests.json").write_text(json.dumps({
        "generated_by": "scripts/test_skills.py",
        "note": ("Each row is one skill: whether its frontmatter and output "
                 "contract parse, and whether its own script runs to completion "
                 "in a stripped environment and prints something. A script that "
                 "runs and prints nothing counts as a failure."),
        "skills": len(rows), "executed": len(ran), "without_script": len(noscript),
        "problems": problems, "results": rows,
    }, indent=1) + "\n")
    return 1 if (problems and a.check) else 0


if __name__ == "__main__":
    sys.exit(main())
