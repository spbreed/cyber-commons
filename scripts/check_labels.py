#!/usr/bin/env python3
"""Check the ground truth in cybertravels/LABELS.md still describes the tree.

    python3 scripts/check_labels.py            # report
    python3 scripts/check_labels.py --check    # CI: non-zero on drift

`LABELS.md` is the hand-written key four AppSec skills score their recall and
precision against. Every row names a file and a unit. Nothing compared those
names to the tree, and the skills do not derive them either — the unit names
are hard-coded in each skill's fixture, because the key has to be written by
reading the code rather than by running a scanner over it.

That leaves one silent failure, and it is the worst kind: rename or delete a
function in `cybertravels/` and the key keeps claiming a defect that is not
there. Recall is then measured against units that do not exist, every number
downstream is wrong, and nothing fails. This gate closes it.

Three rules:

1. **Every unit the key names exists**, in the file the key names it in.
2. **Every unit each skill's fixture names exists**, so a skill and the key
   cannot drift apart from each other either.
3. **The labelled non-defects are still there** — a corpus where everything is
   broken cannot measure precision, and losing a safe twin is as damaging as
   losing a defect.

It deliberately does **not** check that the defect is still *defective*. That
is a judgement about code, not a fact about names, and a gate that claimed to
make it would be the kind of vacuous check this repository keeps deleting.
What it guarantees is narrower and worth having: the key is talking about
functions that exist.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / "cybertravels"
LABELS = TREE / "LABELS.md"

# Where each skill keeps the unit names it scores against. Kept here rather
# than parsed out of the scripts, because a regex over source that silently
# matched nothing would reintroduce exactly the vacuous pass this gate exists
# to prevent.
SKILL_FIXTURES = {
    "appsec/idor-detection-recall": ("IDOR", "AUTHORISED"),
    "appsec/dead-code-ast-reachability": (),
    "appsec/sast-semgrep-deterministic": (),
}


def units_in(path: Path) -> set[str]:
    """Every function and method name defined in a file."""
    try:
        tree = ast.parse(path.read_text())
    except (OSError, SyntaxError) as e:
        raise RuntimeError(f"{path}: {e}")
    return {n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def rows_from_labels() -> list[tuple[str, str, str]]:
    """(file, unit, section) for every row in both tables of the key."""
    text = LABELS.read_text()
    out = []
    section = "defect"
    for line in text.splitlines():
        if line.startswith("## Not defects"):
            section = "not-a-defect"
        elif line.startswith("## ") and "Not defects" not in line:
            if section == "not-a-defect":
                section = "other"
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # Both tables carry `file` then `unit` as backticked cells, though the
        # defect table is numbered and the non-defect table is not.
        got = [re.fullmatch(r"`([^`]+)`", c) for c in cells]
        pair = [m.group(1) for m in got if m]
        if len(pair) >= 2 and pair[0].endswith(".py"):
            out.append((pair[0], pair[1], section))
    return out


def fixture_names(skill: str, names: tuple[str, ...]) -> set[str]:
    """The unit names a skill's fixture declares, read from its source."""
    script = next((ROOT / "skills" / skill / "scripts").glob("*.py"))
    tree = ast.parse(script.read_text())
    found: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name) or target.id not in names:
                continue
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                continue
            found |= {str(v) for v in value}
    return found


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit non-zero on drift")
    a = ap.parse_args()

    problems: list[str] = []
    rows = rows_from_labels()
    if not rows:
        print("::error::no rows parsed out of LABELS.md — this gate would pass "
              "vacuously", file=sys.stderr)
        return 1

    defects = [r for r in rows if r[2] == "defect"]
    safe = [r for r in rows if r[2] == "not-a-defect"]
    print(f"cybertravels/LABELS.md — {len(defects)} defect row(s), "
          f"{len(safe)} labelled non-defect(s)\n")

    by_file: dict[str, set[str]] = {}
    for rel, unit, section in rows:
        path = TREE / rel
        if not path.is_file():
            problems.append(f"LABELS.md names {rel}, which is not in the tree")
            continue
        if rel not in by_file:
            by_file[rel] = units_in(path)
        mark = "ok  " if unit in by_file[rel] else "GONE"
        if unit not in by_file[rel]:
            problems.append(
                f"LABELS.md ({section}) names {rel}::{unit}, which no longer "
                f"exists — the key is scoring against a unit that is not there")
        print(f"  {mark}  {rel}::{unit}  ({section})")

    print()
    for skill, names in SKILL_FIXTURES.items():
        if not names:
            continue
        declared = fixture_names(skill, names)
        everywhere = set().union(*by_file.values()) if by_file else set()
        missing = sorted(declared - everywhere)
        print(f"  {'ok  ' if not missing else 'DRIFT'}  {skill}: "
              f"{len(declared)} unit(s) in its fixture")
        for unit in missing:
            problems.append(
                f"{skill} scores against '{unit}', which is not in any file "
                f"LABELS.md names")

    for p in problems:
        print(f"\n  FAIL  {p}")
    print(f"\n{len(rows)} labelled unit(s) checked · {len(problems)} problem(s)")
    if problems and a.check:
        print(f"::error::{len(problems)} label(s) no longer describe the tree",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
