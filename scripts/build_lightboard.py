#!/usr/bin/env python3
"""Generate LIGHTBOARD.md — a speaking script for every lesson, to record from.

This is written to be **read aloud**, not read. Different job from the page:
the page can be re-read, a recording cannot, so every line has to land the
first time and sound like a person who has done the work rather than someone
narrating a slide.

The shape per lesson is always the same five beats, because a recurring shape
is what lets somebody record 134 of these without each one becoming a fresh
writing problem:

    COLD OPEN    the scene, no preamble. Never "in this lesson we will".
    THE STAKES   why it costs something. Day 0, said out loud.
    WHAT WE DO   the thing on the board. Day 1.
    THE NUMBER   what comes out, and what it means. Day 2.
    THE TURN     hand it to them, and point at what is next.

The content is pulled from the same sources the lesson is built from — the
hook, the CyberTravels grounding, Day 0/1/2, what the run proves, the challenge
— so a script cannot describe a lesson that no longer exists, and re-running
this after an edit brings the script back in step. The connective phrasing is
written here; the substance is the lesson's own.

    python3 scripts/build_lightboard.py            # write LIGHTBOARD.md
    python3 scripts/build_lightboard.py --check    # CI: fail if it is stale
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
OUT = ROOT / "LIGHTBOARD.md"

from exercises import EXERCISES                      # noqa: E402
from exercises.cybertravels import GROUNDING         # noqa: E402
from exercises.days import DAYS, FUNCTION_DAYS       # noqa: E402

SITE = "https://cybercommons.ai"


def plain(text: str) -> str:
    """Markdown stripped back to something you can say.

    A script full of asterisks and backticks is a script somebody stumbles
    over on the third take.
    """
    t = text.strip()
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)     # links -> their text
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", t)
    t = re.sub(r"^#+\s*", "", t, flags=re.M)
    t = re.sub(r"\s*\n\s*", " ", t)
    return re.sub(r"\s{2,}", " ", t).strip()


def first_sentences(text: str, n: int = 2) -> str:
    parts = re.split(r"(?<=[.!?])\s+", plain(text))
    return " ".join(parts[:n]).strip()


def sessions():
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            for i, s in enumerate(tr["sessions"]):
                yield fn, tr, s, i == len(tr["sessions"]) - 1


def board(sid: str, ex: dict) -> str:
    """What to draw while talking. The diagram is already the lesson's spine."""
    dia = (ex.get("diagram") or "").strip("\n")
    head = [ln for ln in dia.splitlines() if ln.strip()][:1]
    return head[0].strip() if head else "the component map"


def script(fn, tr, s, last) -> str:
    sid = s["id"]
    ex = EXERCISES.get(sid, {})
    d0, d1, d2 = DAYS.get(sid, ("", "", ""))
    runs = any(k in ("py", "skill_script", "model")
               for k, _ in ex.get("steps", []))

    out = [f"### {sid} · {s['title']}", ""]
    out.append(f"`{fn['id']}` · {tr['title']}  ·  "
               f"[page]({SITE}/lessons/{sid}.html)"
               + ("  ·  runs a skill" if runs else "  ·  reading lesson"))
    out.append("")
    out.append(f"**On the board:** {board(sid, ex)}")
    out.append("")

    out.append("**COLD OPEN**")
    out.append("")
    out.append("> " + plain(ex.get("hook", s.get("risk", ""))))
    out.append("")

    out.append("**THE STAKES** — why anyone should care")
    out.append("")
    out.append("> " + plain(d0 or s.get("risk", "")))
    if g := GROUNDING.get(sid):
        out.append(">")
        out.append("> And this is not hypothetical — it is CyberTravels, the same "
                   "company we have been following. " + plain(g))
    out.append("")

    out.append("**WHAT WE DO** — the thing on the board")
    out.append("")
    out.append("> " + plain(d1 or s.get("control", "")))
    out.append("")

    out.append("**THE NUMBER** — what comes out, and what it means")
    out.append("")
    if runs:
        out.append("> Then we run it. Not a screenshot — the real thing, and you can "
                   "run it yourself in your own Kaggle account in about a minute.")
        out.append(">")
    out.append("> " + plain(d2 or "What you count instead, and why that is the honest answer."))
    if expect := ex.get("expect"):
        out.append(">")
        out.append("> Watch for this: " + first_sentences(expect, 2))
    out.append("")

    out.append("**THE TURN** — hand it over")
    out.append("")
    if challenge := ex.get("challenge"):
        out.append("> " + first_sentences(challenge, 2))
    else:
        out.append("> Go and try this against a system you actually run. That is "
                   "where it stops being a lesson.")
    if last:
        out.append(">")
        out.append("> That closes this chapter. The next one picks up the thing "
                   "this one could not do.")
    out.append("")
    out.append("---")
    out.append("")
    return "\n".join(out)


def build() -> str:
    doc = ["""# LIGHTBOARD.md — what to say, lesson by lesson

A recording script for all 134 lessons. Written to be **read aloud**, which is
a different job from the page: a reader can go back, a viewer cannot, so every
line has to land the first time.

## How to use this

Each lesson is five beats. Say them in order and you have a recording.

| beat | what it is | roughly |
|---|---|---|
| **Cold open** | the scene. No preamble, no "in this lesson we will" | 15–20s |
| **The stakes** | why it costs something if you do nothing | 20–30s |
| **What we do** | the thing you draw on the board | 30–45s |
| **The number** | what comes out, and what it means | 20–30s |
| **The turn** | hand it to them, point at what is next | 10–15s |

Two to three minutes a lesson. Long enough to be worth watching, short enough
that you will actually record 134 of them.

## Reading it well

- **Do not read the quote blocks word for word.** They are the beat, in your
  words on the day. The one exception is a number — say those exactly.
- **Start cold.** No "hello and welcome". The cold open is the hook because
  somebody landed here from a search result and gives you eight seconds.
- **Name CyberTravels every time.** It is the spine. Every lesson is the same
  company failing in a new way, and saying so is what makes lesson forty feel
  like it belongs to lesson two.
- **Never oversell the number.** Where a lesson has a real measurement, say it
  flatly and let it do the work. Where it does not, say that too — "this one
  produces no number, and here is what you count instead" buys more credibility
  than a number you invented.
- **On the board:** the line given per lesson is the diagram's own first line.
  Draw it as you talk; do not draw it first and then explain it.

## Keeping it true

Generated by `scripts/build_lightboard.py` from the same sources the lessons
are built from — the hook, the CyberTravels grounding, Day 0/1/2, what the run
proves, the challenge. Edit a lesson and re-run it; do not hand-edit this file,
it is overwritten. The connective phrasing is in the generator; the substance
is each lesson's own.

---
"""]
    current_fn = None
    for fn, tr, s, last in sessions():
        if fn["id"] != current_fn:
            current_fn = fn["id"]
            fd = FUNCTION_DAYS.get(fn["id"], {})
            doc.append(f"\n## Function {fn['id']} — {fn['title']}\n")
            if who := fd.get("who"):
                doc.append(f"**Who you are talking to.** {plain(who)}\n")
            if d0 := fd.get("day0"):
                doc.append(f"**The pitch for this whole function, in one breath.** "
                           f"{first_sentences(d0, 2)}\n")
            doc.append("---\n")
        doc.append(script(fn, tr, s, last))
    return "\n".join(doc).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if LIGHTBOARD.md is stale")
    a = ap.parse_args()

    text = build()
    n = text.count("\n### ")
    if a.check:
        if not OUT.is_file() or OUT.read_text() != text:
            print("::error::LIGHTBOARD.md is stale — run "
                  "python3 scripts/build_lightboard.py", file=sys.stderr)
            return 1
        print(f"ok: LIGHTBOARD.md is up to date ({n} lesson scripts)")
        return 0

    OUT.write_text(text)
    print(f"wrote {OUT.name} — {n} lesson scripts, "
          f"{len(text.split())} words, about {n * 2.5:.0f} minutes of recording")
    return 0


if __name__ == "__main__":
    sys.exit(main())
