#!/usr/bin/env python3
"""Check every lesson against the authoring contract in LESSON_DESIGN.md.

Four rules, and each one exists because breaking it made a lesson worse:

1. **One concept, three parts.** Every lesson carries a `hook`, a `diagram` and
   a `concept`. The hook is brief — a paragraph, not an essay — because a hook
   that has to be read twice is a summary.

2. **The picture before the terminal.** The framework cell is rendered before
   the first code cell in every built notebook. Teaching the "how" before the
   "why" is the most common way a good lesson lands badly.

3. **A bridge out of every chapter.** The last lesson of each chapter names the
   skill just acquired, the flaw it still has, and the next chapter as the
   answer. A chapter that ends without that reads as though the subject is
   closed.

4. **Realistic demos.** A lesson whose code only ever shows the happy path has
   not shown the reader anything they could not have assumed. This one is
   reported rather than enforced — a handful of lessons are legitimately
   demonstrations rather than experiments — but the count is printed so it
   cannot drift quietly.

    python3 scripts/check_lessons.py            # report
    python3 scripts/check_lessons.py --check    # CI: non-zero on any failure
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
NB = ROOT / "labs" / "notebooks"

from exercises import EXERCISES  # noqa: E402
from exercises.framing import BRIDGES  # noqa: E402

HOOK_MIN_WORDS, HOOK_MAX_WORDS = 20, 90

# Something in the lesson that is not the happy path: a refusal, a failure, a
# number that is worse than the one before it. Risk lessons and introductions
# are exempt — for a risk lesson the failure *is* the demonstration, and an
# introduction demonstrates nothing at all.
FAILURE_WORDS = ("deny", "refus", "block", "fail", "breaks", "cannot",
                 "got through", "unanswerable", "leak", "escape", "diluted",
                 "stale", "costs more", "not deployable", "no defence",
                 "wrong", "worse", "never saw", "no record", "0.00",
                 "refut", "unverifiable", "false")
EXEMPT_KINDS = {"risk", "introduction", "architecture"}


def sessions():
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            for i, s in enumerate(tr["sessions"]):
                yield s, tr["id"], i == len(tr["sessions"]) - 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit non-zero on failure")
    a = ap.parse_args()

    problems, happy_path_only, total = [], [], 0

    for s, track, last in sessions():
        sid = s["id"]
        total += 1
        ex = EXERCISES.get(sid)
        if ex is None:
            problems.append(f"{sid}: no exercise")
            continue

        # 1 — one concept, three parts
        for field in ("hook", "diagram", "concept"):
            if not (ex.get(field) or "").strip():
                problems.append(f"{sid}: no {field}")
        words = len((ex.get("hook") or "").split())
        if words and not HOOK_MIN_WORDS <= words <= HOOK_MAX_WORDS:
            problems.append(f"{sid}: hook is {words} words, wanted "
                            f"{HOOK_MIN_WORDS}-{HOOK_MAX_WORDS}")

        # 2 — the picture before the terminal
        path = NB / f"{sid}.ipynb"
        if not path.is_file():
            problems.append(f"{sid}: notebook not built")
            continue
        cells = json.loads(path.read_text())["cells"]
        kinds = [c["cell_type"] for c in cells]
        heads = ["".join(c["source"])[:40] for c in cells]
        framework = next((i for i, h in enumerate(heads)
                          if h.startswith("## 2 · The framework")), None)
        first_code = kinds.index("code") if "code" in kinds else None
        if framework is None:
            problems.append(f"{sid}: no framework section")
        elif first_code is not None and first_code < framework:
            problems.append(f"{sid}: a code cell precedes the framework")

        # 3 — a bridge out of every chapter
        if last and track not in BRIDGES:
            problems.append(f"{sid}: last lesson of {track} with no chapter bridge")

        # 4 — realistic demos (reported, not enforced)
        body = "\n".join("".join(c["source"]) for c in cells).lower()
        if (kinds.count("code") and s.get("kind") not in EXEMPT_KINDS
                and not any(w in body for w in FAILURE_WORDS)):
            happy_path_only.append(sid)

    for p in problems:
        print(f"  FAIL  {p}")
    print(f"\n{total} lessons · {len(problems)} problem(s) · "
          f"{len(BRIDGES)} chapter bridges")
    print(f"{len(happy_path_only)} lesson(s) show only a happy path: "
          f"{', '.join(happy_path_only) or 'none'}")

    if a.check and problems:
        print(f"::error::{len(problems)} lesson(s) break the authoring contract "
              f"— see LESSON_DESIGN.md", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
