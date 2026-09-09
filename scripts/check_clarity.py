#!/usr/bin/env python3
"""Catch the phrasing a reader outside your head cannot resolve.

`judge_content.py` is the reading pass, and it needs a model, a key and the
network. This is the part of the same job that can be decided by a rule, so it
runs in CI on every commit and costs nothing.

It exists because of one real defect. Six lessons said a vendor could change a
model "on a Tuesday" — an idiom meaning "without warning, on an ordinary day".
A reader reported it as a mention of Tuesday out of nowhere, which is exactly
right: the day carries no meaning, and nothing in the text says so.

Two rules, both deliberately narrow. A clarity checker that fires on style
becomes a checker people silence:

1. **No weekday as a stand-in for "at any time".** If a weekday appears, it must
   be a real day in a real timeline — an incident at 03:00 on the Monday is
   fine, "the vendor can change it on a Tuesday" is not. The rule is simply that
   weekday names are not used at all in lesson prose, because every legitimate
   use so far has been expressible without one.

2. **No culture-specific idiom.** Figurative phrasing that a competent reader
   who learned English elsewhere has to look up. The list is curated rather than
   clever: each entry is a phrase that has appeared in security writing and
   means nothing literal.

    python3 scripts/check_clarity.py            # report
    python3 scripts/check_clarity.py --check    # CI: non-zero on any hit
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
NB = ROOT / "labs" / "notebooks"

WEEKDAYS = re.compile(
    r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b")

# Each of these means something only if you already know the metaphor.
IDIOMS = [
    "low-hanging fruit", "silver bullet", "moving the needle", "move the needle",
    "rabbit hole", "elephant in the room", "boils down to", "boil down to",
    "at the end of the day", "touch base", "circle back", "in the weeds",
    "bread and butter", "ballpark", "out of the gate", "home run",
    "slam dunk", "no-brainer", "drink from the firehose", "belt and braces",
    "kick the tyres", "kick the tires", "run it up the flagpole",
    "boiling the ocean", "boil the ocean", "apples to oranges",
    "the whole nine yards", "back of the envelope", "ducks in a row",
]
IDIOM_RE = re.compile("|".join(re.escape(i) for i in IDIOMS), re.I)

# Prose only. A weekday inside a code cell is usually a date in test data, and
# a lesson that teaches cron legitimately prints day names.
def prose(sid: str) -> str:
    nb = json.loads((NB / f"{sid}.ipynb").read_text())
    return "\n".join("".join(c["source"]) for c in nb["cells"]
                     if c["cell_type"] == "markdown")


def context(text: str, at: int, width: int = 68) -> str:
    start = max(0, at - width // 2)
    return " ".join(text[start:start + width].split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    ids = [s["id"] for f in CUR["functions"] for t in f["tracks"]
           for s in t["sessions"]]
    problems = []
    for sid in ids:
        text = prose(sid)
        for m in WEEKDAYS.finditer(text):
            problems.append(f"{sid}: weekday '{m.group(0)}' — say what you mean "
                            f"('at any time', 'without notice'): "
                            f"…{context(text, m.start())}…")
        for m in IDIOM_RE.finditer(text):
            problems.append(f"{sid}: idiom '{m.group(0)}' — "
                            f"…{context(text, m.start())}…")

    for p in problems:
        print(f"  FAIL  {p}")
    print(f"\n{len(ids)} lesson(s) read · {len(problems)} phrase(s) a reader "
          f"would have to decode")

    if a.check and problems:
        print(f"::error::{len(problems)} unclear phrase(s) — see the lines above",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
