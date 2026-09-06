#!/usr/bin/env python3
"""Check every lesson against the authoring contract in LESSON_DESIGN.md.

Six rules, and each one exists because breaking it made a lesson worse:

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

5. **An anchor on every Function E lesson.** Function E is one argument told in
   one unit — the key control indicator defined in E1.1 — and every other lesson
   in E says in a line what it contributes to that indicator or takes from it.
   Without the rule a governance lesson can be internally coherent, read fine on
   its own page, and belong to no argument at all.

6. **Realistic demos.** A lesson whose code only ever shows the happy path has
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
from exercises.anchors import ANCHORS  # noqa: E402
from exercises.cybertravels import GROUNDING  # noqa: E402
from exercises.framing import BRIDGES  # noqa: E402

# Function E is one argument — a control framework, a regulatory map and a
# programme — and its unit is the key control indicator defined in E1.1. Each
# other lesson in E states, in a line under its concept, what it contributes to
# that indicator or takes from it. The rule is enforced rather than reported
# because the failure it prevents is silent: a lesson that is internally
# coherent and belongs to no argument reads fine on its own page.
# E1.1 defines the unit and E1.0 introduces the function that is told in it, so
# neither points at anything — an anchor on either is a paragraph repeating the
# concept directly above it.
ANCHORED_FN, ANCHOR_ORIGIN = "E", "E1.1"
ANCHOR_EXEMPT = {"E1.0", ANCHOR_ORIGIN}

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

        # 4 — every Function E lesson says where it sits against E1.1
        if fn == ANCHORED_FN and sid not in ANCHOR_EXEMPT:
            anchor = (ANCHORS.get(sid) or "").strip()
            if not anchor:
                problems.append(f"{sid}: no anchor to {ANCHOR_ORIGIN} — every "
                                f"Function {ANCHORED_FN} lesson states what it "
                                f"contributes to the indicator, or takes from "
                                f"it; add one to scripts/exercises/anchors.py")
            else:
                seen_anchors.add(sid)
                if "\n> " + anchor.splitlines()[0] not in "\n".join(
                        "".join(c["source"]) for c in cells):
                    problems.append(f"{sid}: anchor defined but not rendered — "
                                    f"rebuild the notebooks")

        # 5 — realistic demos (reported, not enforced)
        body = "\n".join("".join(c["source"]) for c in cells).lower()
        if (kinds.count("code") and s.get("kind") not in EXEMPT_KINDS
                and not any(w in body for w in FAILURE_WORDS)):
            happy_path_only.append(sid)

    # An anchor naming a lesson that does not exist is a rename nobody finished.
    for orphan in sorted(set(ANCHORS) - seen_anchors):
        problems.append(f"{orphan}: anchor defined for a lesson that is not in "
                        f"Function {ANCHORED_FN}")

    for p in problems:
        print(f"  FAIL  {p}")
    print(f"\n{total} lessons · {len(problems)} problem(s) · "
          f"{len(BRIDGES)} chapter bridges · {len(seen_anchors)} anchored to "
          f"{ANCHOR_ORIGIN}")
    print(f"{len(happy_path_only)} lesson(s) show only a happy path: "
          f"{', '.join(happy_path_only) or 'none'}")

    if a.check and problems:
        print(f"::error::{len(problems)} lesson(s) break the authoring contract "
              f"— see LESSON_DESIGN.md", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
