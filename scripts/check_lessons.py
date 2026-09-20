#!/usr/bin/env python3
"""Check every lesson against the authoring contract in LESSON_DESIGN.md.

Rules, each one here because breaking it made a lesson worse:

0. **Day 0, Day 1, Day 2, on every lesson that has three days.** A lesson says
   why it is worth doing, how it is done, and what number tells you it worked.
   Readers reported that they could not tell what the commons was for until
   somebody explained it; this is that explanation. It is required of every
   lesson whose layout declares a `days` section — which is every lesson about
   the system, and not the two setup pages, where the honest Day 2 was
   "Nothing is computed here."

0a. **A section renders if and only if there is something behind it.** Which
   parts of the template a lesson carries is declared in
   `scripts/exercises/layout.py`, and checked here from both sides. Rendering
   a section with nothing in it teaches a reader the headings are decoration;
   leaving the source for a section that no longer renders is worse, because
   the prose is invisible on the page and nobody can find it to correct.
   B1.0 carried a "What you just proved" paragraph for a lesson that runs
   nothing, and had done for months.

1. **One concept, three parts.** Every lesson carries a `hook`, a `diagram` and
   a `concept`. The hook is brief — a paragraph, not an essay — because a hook
   that has to be read twice is a summary.

2. **The picture before the terminal.** The framework cell is rendered before
   the run block on every built page. Teaching the "how" before the
   "why" is the most common way a good lesson lands badly.

3. **Grounded in CyberTravels.** Every lesson about the system says what its
   idea looks like in CyberTravels — the one system the whole commons is taught
   on — so a reader is never asked to hold a fresh example per lesson. The two
   setup pages are about the reader's own machine and carry no grounding;
   A0.0's used to read "Nothing in CyberTravels yet", under a heading
   promising the idea in the running system.

4. **A bridge out of every chapter, pointing at the chapter that follows.**
   The last lesson of each chapter names the skill just acquired, the flaw it
   still has, and the next chapter as the answer. A chapter that ends without
   that reads as though the subject is closed. The lesson it names is checked
   against the curriculum's own order: A0's bridge went on saying "Next →
   B1.0" after the renumber put two chapters in between, sending readers past
   the chapters that build the system the rest of the commons is taught on.

5. **An anchor on every Function D and Function E lesson.** Both are long
   arguments told in one unit — an interval between an agent acting and the
   control being back at target (E1.0), and a key control indicator computed
   from the estate (F1.1). Every other lesson in those functions says in a line
   which part of that unit it moves. Without the rule a lesson can be internally
   coherent, read fine on its own page, and belong to no argument at all.

6. **Chapters cited by id, not by number.** The chapter number is an ordinal in
   `curriculum.json` and is rendered nowhere, so "Chapter 11" in prose is
   unresolvable by a reader and goes stale the moment a chapter is inserted.
   Prose says "Chapter E3". The numbers themselves are checked for being
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
PAGES = ROOT / "site" / "lessons"

from exercises import EXERCISES  # noqa: E402
from exercises.anchors import ANCHORS  # noqa: E402
from exercises.cybertravels import GROUNDING  # noqa: E402
from exercises.days import DAYS, FUNCTION_DAYS  # noqa: E402
from exercises.framing import BRIDGES  # noqa: E402
from exercises.layout import PARTS, parts_for, runs_something, why_dropped  # noqa: E402

# Functions D and E are long arguments rather than collections, and each is told
# in one unit: an interval between an agent acting and the control being back at
# target (E1.0), and a key control indicator computed from the estate (F1.1).
# Every other lesson in those two functions says in a line under its concept
# which part of that unit it moves. Enforced rather than reported because the
# failure it prevents is silent — a lesson that belongs to no argument still
# reads fine on its own page.
ANCHOR_ORIGIN = {"E": "E1.0", "F": "F1.1"}
# The origins themselves, plus F1.0: it introduces the function that F1.1's unit
# is told in, so an anchor there would restate the concept directly above it.
ANCHOR_EXEMPT = {"E1.0", "F1.0", "F1.1"}

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
EXEMPT_KINDS = {"risk", "introduction", "architecture", "setup"}

# What has to exist in the sources for a part of the template to have anything
# to render, and where an author goes to add or delete it. `bridge` is absent
# on purpose: a bridge belongs to a chapter rather than a lesson, so it is
# legitimately defined while rendering on one page only.
PART_SOURCE = {
    "riskcontrol": ("risk / control", "site/data/curriculum.json"),
    "relevance":   ("CyberTravels grounding", "scripts/exercises/cybertravels.py"),
    "days":        ("Day 0/1/2", "scripts/exercises/days.py"),
    "proved":      ("expect", "the lesson's track_*.py"),
    "turn":        ("challenge", "the lesson's track_*.py"),
}


# What each part looks like on the built page. Exact strings, and the Day
# heading is matched in full because "What this lesson is" is a prefix of it
# and is also the heading the days-less pages carry.
PAGE_MARK = {
    "riskcontrol": '<div class="rc">',
    "relevance":   ">Use case relevance<",
    "days":        "What this lesson is — Day 0, Day 1, Day 2<",
    "proved":      ">What you just proved<",
    "turn":        ">Your turn<",
    "bridge":      ">Where this leaves you<",
}


def part_content(part: str, s: dict, ex: dict) -> str:
    """The source text behind one part, or "" when there is none."""
    sid = s["id"]
    if part == "riskcontrol":
        return ((s.get("risk") or "") + (s.get("control") or "")).strip()
    if part == "relevance":
        return (GROUNDING.get(sid) or "").strip()
    if part == "days":
        d = DAYS.get(sid) or ()
        return "".join(x or "" for x in d).strip()
    return (ex.get({"proved": "expect", "turn": "challenge"}[part]) or "").strip()


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
    # Which lessons are off the full template, and which sections they drop.
    # Printed rather than enforced: the point is that every deviation is
    # visible in one place, so a section quietly disappearing from a hundred
    # pages cannot pass as curation.
    curated: dict[str, list[str]] = {}

    seen_anchors = set()
    for s, fn, track, last in sessions():
        sid = s["id"]
        total += 1
        ex = EXERCISES.get(sid)
        if ex is None:
            problems.append(f"{sid}: no exercise")
            continue

        # 0a — the template, applied where it applies and nowhere else. Both
        # directions: a heading with nothing under it, and prose under no
        # heading at all.
        parts = parts_for(sid, s.get("kind"), track,
                          runs=runs_something(sid),
                          last_in_track=last)
        if dropped := sorted(set(PARTS) - parts - {"bridge"}):
            curated[sid] = dropped
        for part, (what, where) in PART_SOURCE.items():
            has = bool(part_content(part, s, ex))
            if part in parts and not has:
                problems.append(f"{sid}: renders the {part} section with no "
                                f"{what} behind it — write one in {where}, or "
                                f"drop the section in exercises/layout.py")
            elif part not in parts and has:
                problems.append(
                    f"{sid}: carries {what} in {where} for a {part} section "
                    f"the page does not render — delete it, or put {part} "
                    f"back in exercises/layout.py. It does not render because: "
                    f"{why_dropped(sid, s.get('kind'), track) or 'the lesson runs nothing'}")

        # 0b — Day 0/1/2 is three days or it is nothing
        if "days" in parts:
            day = DAYS.get(sid)
            if not day or len(day) != 3 or not all(x and x.strip() for x in day):
                problems.append(f"{sid}: Day 0/1/2 is incomplete — say why this "
                                f"is worth doing, how it is done, and what "
                                f"number tells you it worked, in "
                                f"scripts/exercises/days.py")

        # 1 — one concept, three parts
        for field in ("hook", "diagram", "concept"):
            if not (ex.get(field) or "").strip():
                problems.append(f"{sid}: no {field}")
        words = len((ex.get("hook") or "").split())
        if words and not HOOK_MIN_WORDS <= words <= HOOK_MAX_WORDS:
            problems.append(f"{sid}: hook is {words} words, wanted "
                            f"{HOOK_MIN_WORDS}-{HOOK_MAX_WORDS}")

        # 2 — the picture before the terminal.
        # Checked on the built page, not the notebook: the notebook now carries
        # code and nothing else, and the lesson is rendered from source by
        # build_site.py. The rule is unchanged — the framework has to come
        # before anything that runs — only where it is enforced moved.
        page_f = PAGES / f"{sid}.html"
        if not page_f.is_file():
            problems.append(f"{sid}: lesson page not built — run build_site.py")
            continue
        page = page_f.read_text()
        framework = page.find("The framework, and how it works")
        execution = page.find("Real time execution as skill")
        if framework < 0:
            problems.append(f"{sid}: no framework section on the page")
        elif 0 <= execution < framework:
            problems.append(f"{sid}: the execution section precedes the framework")

        # 0c — and the page agrees with the declaration. Checked against what
        # the reader sees rather than against the same dict build_site.py read,
        # because a gate that asserts a function equals itself protects nothing.
        for part, mark in PAGE_MARK.items():
            on_page = mark in page
            if (part in parts) != on_page:
                problems.append(
                    f"{sid}: layout.py says {part} "
                    f"{'renders' if part in parts else 'does not render'} and "
                    f"the built page says the opposite — rebuild the site")

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
                import html as _h
                if _h.escape(anchor.splitlines()[0]) not in page:
                    problems.append(f"{sid}: anchor defined but not rendered — "
                                    f"rebuild the site")

        # 7 — realistic demos (reported, not enforced)
        body = page.lower()
        # "Does this lesson run something" is read from the page's own run
        # block now, not from a notebook's code cells.
        if ("runbox" in page and s.get("kind") not in EXEMPT_KINDS
                and not any(w in body for w in FAILURE_WORDS)):
            happy_path_only.append(sid)

    # Every function says who it is for and what its three days are, because
    # the homepage and each function introduction render from this.
    for fn in sorted({f["id"] for f in CUR["functions"]}):
        entry = FUNCTION_DAYS.get(fn)
        if not entry or not all(entry.get(k, "").strip()
                                for k in ("who", "day0", "day1", "day2")):
            problems.append(f"function {fn}: needs who / day0 / day1 / day2 in "
                            f"scripts/exercises/days.py")

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

    # 6c — and a bridge names the chapter that actually comes next. A bridge
    # whose track still exists can still send a reader to the wrong place:
    # A0's went on saying "Next → B1.0" after the renumber put A1 and A2 in
    # between, which skipped the two chapters that build the system.
    order = [(tid, ses[0]["id"]) for fn in CUR["functions"] for tr in fn["tracks"]
             for tid, ses in [(tr["id"], tr["sessions"])] if ses]
    for i, (tid, _) in enumerate(order[:-1]):
        b = BRIDGES.get(tid)
        if not b:
            continue
        nxt_track, nxt_lesson = order[i + 1]
        if nxt_track not in b["next"] and nxt_lesson not in b["next"]:
            problems.append(f"bridge {tid}: names neither {nxt_track} nor "
                            f"{nxt_lesson}, which is what actually follows it "
                            f"— fix BRIDGES in scripts/exercises/framing.py")

    # 6b — chapters are cited by track id, never by number. The number is an
    # ordinal in curriculum.json and is rendered nowhere, so "Chapter 11" in
    # prose is unresolvable by a reader and silently stale for an author.
    numbered = re.compile(r"Chapters?\s+\d")
    for f in sorted((ROOT / "scripts" / "exercises").glob("*.py")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if numbered.search(line):
                problems.append(f"{f.name}:{i}: chapter cited by number — use "
                                f"the track id, e.g. 'Chapter E3'")

    for p in problems:
        print(f"  FAIL  {p}")
    print(f"\n{total} lessons · {len(problems)} problem(s) · "
          f"{len(BRIDGES)} bridges · {len(DAYS)} with Day 0/1/2 · "
          f"{len(seen_anchors)} anchored "
          f"({', '.join(f'{f}→{o}' for f, o in sorted(ANCHOR_ORIGIN.items()))})")
    print(f"{len(happy_path_only)} lesson(s) show only a happy path: "
          f"{', '.join(happy_path_only) or 'none'}")
    print(f"{len(curated)} lesson(s) off the full template:")
    for sid, dropped in sorted(curated.items()):
        print(f"   {sid:<8}no {', '.join(dropped)}")

    if a.check and problems:
        print(f"::error::{len(problems)} lesson(s) break the authoring contract "
              f"— see LESSON_DESIGN.md", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
