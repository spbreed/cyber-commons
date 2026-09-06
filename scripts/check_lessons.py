#!/usr/bin/env python3
"""Check every lesson against the authoring contract in LESSON_DESIGN.md.

Seven rules, and each one exists because breaking it made a lesson worse:

1. **One concept, three parts.** Every lesson carries a `hook`, a `diagram` and
   a `concept`. The hook is brief — a paragraph, not an essay — because a hook
   that has to be read twice is a summary.

2. **The picture before the terminal.** The framework cell is rendered before
   the first code cell in every built notebook. Teaching the "how" before the
   "why" is the most common way a good lesson lands badly.

3. **Grounded in CyberTravels.** Every lesson says what its idea looks like in
   CyberTravels — the one system the whole commons is taught on — so a reader is
   never asked to hold a fresh example per lesson.

4. **A bridge out of every chapter.** The last lesson of each chapter names the
   skill just acquired, the flaw it still has, and the next chapter as the
   answer. A chapter that ends without that reads as though the subject is
   closed.

5. **An anchor on every Function D and Function E lesson.** Both are long
   arguments told in one unit — an interval between an agent acting and the
   control being back at target (D1.0), and a key control indicator computed
   from the estate (E1.1). Every other lesson in those functions says in a line
   which part of that unit it moves. Without the rule a lesson can be internally
   coherent, read fine on its own page, and belong to no argument at all.

6. **Chapters cited by id, not by number.** The chapter number is an ordinal in
   `curriculum.json` and is rendered nowhere, so "Chapter 11" in prose is
   unresolvable by a reader and goes stale the moment a chapter is inserted.
   Prose says "Chapter D3". The numbers themselves are checked for being
   contiguous, and a bridge whose track no longer exists is a failure.

7. **Realistic demos.** A lesson whose code only ever shows the happy path has
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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
NB = ROOT / "labs" / "notebooks"

from exercises import EXERCISES  # noqa: E402
from exercises.anchors import ANCHORS  # noqa: E402
from exercises.cybertravels import GROUNDING  # noqa: E402
from exercises.framing import BRIDGES  # noqa: E402

# Functions D and E are long arguments rather than collections, and each is told
# in one unit: an interval between an agent acting and the control being back at
# target (D1.0), and a key control indicator computed from the estate (E1.1).
# Every other lesson in those two functions says in a line under its concept
# which part of that unit it moves. Enforced rather than reported because the
# failure it prevents is silent — a lesson that belongs to no argument still
# reads fine on its own page.
ANCHOR_ORIGIN = {"D": "D1.0", "E": "E1.1"}
# The origins themselves, plus E1.0: it introduces the function that E1.1's unit
# is told in, so an anchor there would restate the concept directly above it.
ANCHOR_EXEMPT = {"D1.0", "E1.0", "E1.1"}

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
                yield s, fn["id"], tr["id"], i == len(tr["sessions"]) - 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit non-zero on failure")
    a = ap.parse_args()

    problems, happy_path_only, total = [], [], 0

    seen_anchors = set()
    for s, fn, track, last in sessions():
        sid = s["id"]
        total += 1
        ex = EXERCISES.get(sid)
        if ex is None:
            problems.append(f"{sid}: no exercise")
            continue

        # 1 — one concept, three parts, grounded in the running system
        if not GROUNDING.get(sid, "").strip():
            problems.append(f"{sid}: no CyberTravels grounding")
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

        # 4 — every lesson in D and E says where it sits on its function's spine
        if fn in ANCHOR_ORIGIN and sid not in ANCHOR_EXEMPT:
            anchor = (ANCHORS.get(sid) or "").strip()
            if not anchor:
                problems.append(f"{sid}: no anchor to {ANCHOR_ORIGIN[fn]} — "
                                f"every Function {fn} lesson states which part "
                                f"of that spine it moves; add one to "
                                f"scripts/exercises/anchors.py")
            else:
                seen_anchors.add(sid)
                if "\n> " + anchor.splitlines()[0] not in "\n".join(
                        "".join(c["source"]) for c in cells):
                    problems.append(f"{sid}: anchor defined but not rendered — "
                                    f"rebuild the notebooks")

        # 7 — realistic demos (reported, not enforced)
        body = "\n".join("".join(c["source"]) for c in cells).lower()
        if (kinds.count("code") and s.get("kind") not in EXEMPT_KINDS
                and not any(w in body for w in FAILURE_WORDS)):
            happy_path_only.append(sid)

    # An anchor naming a lesson that does not exist is a rename nobody finished.
    for orphan in sorted(set(ANCHORS) - seen_anchors):
        problems.append(f"{orphan}: anchor defined for a lesson that is not in "
                        f"an anchored function ({', '.join(sorted(ANCHOR_ORIGIN))})")

    # 6a — chapters are contiguous, and a bridge belongs to a real track.
    # Both of these had drifted: Function D grew from two chapters to five and
    # nothing renumbered, and the bridges for B1 and for the two-track D outlived
    # their tracks — dead text that still described the curriculum's shape.
    chapters = [(tr["id"], tr.get("chapter"))
                for fn in CUR["functions"] for tr in fn["tracks"]]
    for tid, ch in chapters:
        if ch is None:
            problems.append(f"track {tid}: no chapter number")
    got = sorted(c for _, c in chapters if c is not None)
    if got != list(range(len(chapters))):
        problems.append(f"chapters are not 0..{len(chapters) - 1}: {got}")
    for tid in sorted(set(BRIDGES) - {t for t, _ in chapters}):
        problems.append(f"bridge {tid}: no such track — delete it rather than "
                        f"leaving it to describe a curriculum that changed")

    # 6b — chapters are cited by track id, never by number. The number is an
    # ordinal in curriculum.json and is rendered nowhere, so "Chapter 11" in
    # prose is unresolvable by a reader and silently stale for an author.
    numbered = re.compile(r"Chapters?\s+\d")
    for f in sorted((ROOT / "scripts" / "exercises").glob("*.py")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if numbered.search(line):
                problems.append(f"{f.name}:{i}: chapter cited by number — use "
                                f"the track id, e.g. 'Chapter D3'")

    for p in problems:
        print(f"  FAIL  {p}")
    print(f"\n{total} lessons · {len(problems)} problem(s) · "
          f"{len(BRIDGES)} chapter bridges · {len(seen_anchors)} anchored "
          f"({', '.join(f'{f}→{o}' for f, o in sorted(ANCHOR_ORIGIN.items()))})")
    print(f"{len(happy_path_only)} lesson(s) show only a happy path: "
          f"{', '.join(happy_path_only) or 'none'}")

    if a.check and problems:
        print(f"::error::{len(problems)} lesson(s) break the authoring contract "
              f"— see LESSON_DESIGN.md", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
