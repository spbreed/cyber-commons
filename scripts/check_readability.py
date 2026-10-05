#!/usr/bin/env python3
"""Keep the do-this-now instructions followable by somebody new.

Students reviewing Function A asked for "shorter explanations" and "clear steps
they can follow on their own", and the setup lesson is aimed at readers in about
year 9. Prose drifts back towards the author's own register unless something
measures it, so this is the thing that measures it.

**It reads the step instructions only.** The concept sections of this curriculum
are deliberately long-sentenced and argumentative, and that is the house voice —
a gate that flattened them would be deleted within a month and would deserve to
be. What a reader has to *follow with their hands* is a different job, and that
is the `steps` of each lesson in `scripts/exercises/`.

Two numbers, both chosen from what the tree already measures rather than from a
readability formula:

* **No single instruction over SENTENCE_CEILING words.** A 50-word instruction
  is not a style preference, it is a sentence somebody has to re-read twice
  before they can type anything.
* **A lesson's average instruction under AVERAGE_CEILING words.** Function A
  measured 16.0 at the time this was written and the whole curriculum 19.8, so
  the bar is set where it catches drift rather than where it fails the present.

    python3 scripts/check_readability.py            # report every lesson
    python3 scripts/check_readability.py --check    # non-zero exit on a failure
    python3 scripts/check_readability.py --function A

Exit 1 on a failure, and the failure names the lesson and prints the sentence,
because "A2.4 is unreadable" is not actionable and the sentence is.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from exercises import EXERCISES                               # noqa: E402

SENTENCE_CEILING = 45
AVERAGE_CEILING = 25

# Which functions the ceilings are *enforced* on, as opposed to reported.
#
# Function A is where a reader with no background starts, it is the part the
# student review actually tested, and it meets both ceilings as of this commit.
# The other five functions do not: 39 lessons carry a single step instruction
# that packs a whole skill's method into one sentence, averaging 25 to 33 words.
#
# Enforcing everywhere today would turn CI red on 39 lessons nobody has rewritten
# yet, and a gate that is red on arrival gets switched off rather than fixed. So
# the rest are printed as a backlog on every run, with the count, which keeps them
# visible instead of discovered again in six months. Widen this set as each
# function is rewritten — that is the whole point of it being a set.
ENFORCED = ("A",)

# A sentence that is mostly a path, a command or a contract key is not prose and
# counting its words says nothing about whether a reader can follow it.
CODEISH = re.compile(r"^[\s`'\"/.\w:-]*$")


def step_prose(sid: str) -> str:
    """The markdown a reader follows, with everything that is not prose removed.

    Code blocks are replaced by a full stop rather than deleted. Deleting them
    joins the sentence before to the sentence after, and the splitter then
    reports one 49-word sentence that does not exist — which is exactly the
    false positive this comment exists to stop somebody re-introducing.
    """
    out = []
    for step in (EXERCISES.get(sid) or {}).get("steps", []):
        if step[0] != "md":
            continue
        s = step[1]
        s = re.sub(r"```.*?```", " . ", s, flags=re.S)   # code -> boundary
        s = re.sub(r"^\s*\|.*$", " ", s, flags=re.M)     # table rows
        s = re.sub(r"^#+ .*$", " . ", s, flags=re.M)     # headings
        out.append(s)
    return " ".join(out)


def sentences(text: str) -> list[str]:
    text = re.sub(r"[`*_\[\]()]", "", text)
    text = re.sub(r"\s+", " ", text)
    out = []
    for s in re.split(r"(?<=[.!?:])\s+", text):
        s = s.strip()
        if len(s.split()) > 3 and not CODEISH.match(s):
            out.append(s)
    return out


def lesson_ids() -> list[str]:
    cur = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
    return [s["id"] for f in cur["functions"] for t in f["tracks"]
            for s in t["sessions"]]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="non-zero exit on any failure")
    ap.add_argument("--function", metavar="X",
                    help="only lessons in this function, for example A")
    a = ap.parse_args()

    problems, backlog, rows = [], [], []
    for sid in lesson_ids():
        if a.function and not sid.startswith(a.function):
            continue
        ss = sentences(step_prose(sid))
        if not ss:
            continue
        lens = [len(s.split()) for s in ss]
        avg = statistics.mean(lens)
        rows.append((sid, avg, max(lens), len(ss)))
        where = problems if sid[0] in ENFORCED else backlog

        for s in ss:
            n = len(s.split())
            if n > SENTENCE_CEILING:
                where.append(f"{sid}: a {n}-word instruction, over the "
                             f"{SENTENCE_CEILING}-word ceiling — split it:\n"
                             f"       {s[:150]}…")
        if avg > AVERAGE_CEILING:
            where.append(f"{sid}: instructions average {avg:.1f} words, over "
                         f"the {AVERAGE_CEILING}-word ceiling")

    rows.sort(key=lambda r: -r[1])
    for sid, avg, mx, n in rows:
        flag = "  <-- " if avg > AVERAGE_CEILING or mx > SENTENCE_CEILING else ""
        print(f"  {sid:7s} avg {avg:5.1f}  longest {mx:3d}  "
              f"{n:3d} instruction(s){flag}")

    if rows:
        print(f"\n{len(rows)} lesson(s) with step instructions · "
              f"mean {statistics.mean(r[1] for r in rows):.1f} words · "
              f"longest single instruction {max(r[2] for r in rows)}")

    if backlog:
        print(f"\nbacklog — {len(backlog)} instruction(s) outside "
              f"{'/'.join(ENFORCED)} over a ceiling, reported not enforced:")
        for b in backlog:
            print(f"   {b.splitlines()[0]}")
        print("   Each is one sentence introducing a skill. Rewriting a "
              "function moves it into ENFORCED.")

    for p in problems:
        print(f"::error::{p}", file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} readability problem(s) in "
              f"{'/'.join(ENFORCED)}")
        return 1 if a.check else 0
    print(f"\nevery instruction in {'/'.join(ENFORCED)} is inside both ceilings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
