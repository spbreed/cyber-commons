#!/usr/bin/env python3
"""Generate LIGHTBOARD.md — a speaking script for every lesson, to record from.

This is written to be **read aloud**, not read. Different job from the page:
the page can be re-read, a recording cannot, so every line has to land the
first time and sound like a person who has done the work rather than someone
narrating a slide.

**Every lesson is a story with a position in a longer one.** That is the thing
an earlier version of this file got wrong, and it got it wrong in a way that
was worst exactly where it mattered most — the first recording somebody
watches. Three bugs, all of them the same bug:

  - the grounding line said "CyberTravels, the same company we have been
    following" on lesson one, where nobody has followed anything yet;
  - "then we run it" sat directly above "nothing is computed here", because
    the run was filed under the number rather than under the work;
  - "that closes this chapter" was said on a chapter *opener*, because a
    one-lesson chapter is both first and last.

So position is computed rather than assumed. Every beat knows whether it is
opening the curriculum, opening a function, mid-chapter, or closing one, and
says the thing that is true there.

The shape per lesson is a fixed sequence, because a recurring shape is what
lets somebody record 134 of these without each one becoming a fresh writing
problem:

    WHERE WE ARE   one line of continuity. What the last one left you with.
    ORIENT         only on the entry points — the ground rules for a newcomer.
    1 OPEN         the scene, no preamble.
    2 WHY IT COSTS Day 0, said out loud, then the same thing in CyberTravels.
    3 WHAT WE BUILD Day 1 — the thing on the board, and the run.
    4 THE NUMBER   Day 2 — what comes out, and what it means.
    5 HAND OVER    the challenge, and the name of the next lesson.

The content is pulled from the same sources the lesson is built from — the
hook, the CyberTravels grounding, Day 0/1/2, what the run proves, the challenge,
the chapter bridge — so a script cannot describe a lesson that no longer exists,
and re-running this after an edit brings the script back in step. The connective
phrasing is written here; the substance is the lesson's own.

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

from exercises import EXERCISES                              # noqa: E402
from exercises.cybertravels import GROUNDING                 # noqa: E402
from exercises.days import DAYS, FUNCTION_DAYS, FUNCTION_INTRO  # noqa: E402
from exercises.framing import BRIDGES                        # noqa: E402

SITE = "https://cybercommons.ai"

# --- the entry points, and what a newcomer needs before the cold open --------
#
# This is the only substantive prose in this generator, and it is here rather
# than in the lesson sources on purpose: it is direction for the person
# recording, not content of the lesson. It exists because "start cold" is
# excellent advice for lesson ninety and terrible advice for lesson one — a
# viewer who has never shipped an agent does not need a scene, they need to
# know what an agent is, and thirty seconds spent there is what makes every
# later cold open land.
#
# Keyed by lesson id. A0.1 is the front door of the whole commons; the other
# five are the function intros from FUNCTION_INTRO, which are where somebody
# arriving from a search result actually lands.
ORIENT = {
 "A0.1": (
  "**Thirty seconds on what an agent is, before anything else.** Assume half "
  "your viewers have never shipped one. A model that only answers questions is "
  "a chatbot. Give it tools — let it call an API, read a file, move money — and "
  "a loop that picks which tool to call next, and it is an agent. That is the "
  "entire difference, and it is the entire problem: a chatbot that is wrong "
  "says something wrong, an agent that is wrong *does* something wrong. "
  "Everything in this commons follows from that one sentence.",
  "**Then say what this is, plainly.** A hundred and thirty-four lessons, free, "
  "no vendor and no paid account, and every one of them runs — you press a "
  "button and the thing executes in your own account. Say that you are going to "
  "use one made-up company for all of it, and that you will introduce it in the "
  "next video.",
 ),
 "A1.0": (
  "**Introduce CyberTravels properly — this is the one that has to land.** It is "
  "a corporate travel company that does not exist: four agents, one of which can "
  "issue refunds. It is invented on purpose, and say why out loud. Every lesson "
  "in all five functions is grounded in the same company, so the refund limit an "
  "attacker walks past in one lesson is the same limit a detection watches in "
  "another and a report counts in a third. By the fourth function you are not "
  "learning a fourth example — you are watching a system you already understand "
  "fail in a new way.",
 ),
 "B2.0": (
  "**If your viewer has done application security, tell them what is different, "
  "or they will assume they can skip this.** The pipeline is not new. What is "
  "new is that code now arrives faster than any human review can keep up with, "
  "and some of it was written by an agent that cannot tell you why. Everything "
  "in this chapter is that one pressure.",
 ),
 "C1.0": (
  "**Say the distinction first, because most people hear “red team” and think "
  "jailbreaks.** Getting a model to say something it should not is a prompt "
  "result. Getting an *agent* to do something it should not — spend money, "
  "touch a file, message another agent — is an incident. This chapter is the "
  "second one, and it is the one nobody has a playbook for.",
 ),
 "D1.0": (
  "**Open by granting that their SOC already works.** They have sensors, a lake, "
  "rules, an on-call rota. None of that is wrong and none of it is being "
  "replaced. The question this whole chapter asks is narrower and more "
  "uncomfortable: when an agent is the thing that went wrong, would any of it "
  "have fired?",
 ),
 "E1.0": (
  "**Governance has a reputation, so beat the audience to it.** Say out loud "
  "that most people hear this word and picture a spreadsheet nobody reads. Then "
  "say what you actually mean: being able to show, later and to somebody "
  "hostile, that a decision was made on purpose and by a named person. That is "
  "an engineering problem, and it is the one that decides whether the thing you "
  "built is allowed to stay switched on.",
 ),
}


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


def first_sentences(text: str, n: int = 2, cap: int = 320) -> str:
    """The opening of a block, cut at a sentence end rather than mid-clause.

    `expect` in particular is written for somebody reading terminal output and
    runs to a thousand characters on the longest lessons. Read aloud in full it
    is unspeakable — exit codes and tracebacks — so it is cut here and labelled
    as what is on screen rather than as words to say.
    """
    parts = re.split(r"(?<=[.!?])\s+", plain(text))
    out = ""
    for p in parts[:n]:
        if out and len(out) + len(p) + 1 > cap:
            break
        out = f"{out} {p}".strip()
    return out


def lessons() -> list[dict]:
    """Every lesson, flat, each knowing where it sits.

    The neighbours are computed once here because three separate beats need
    them — continuity at the top, the chapter close at the bottom, and whether
    this is the first thing anybody watches.
    """
    flat = []
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            for i, s in enumerate(tr["sessions"]):
                flat.append({"fn": fn, "tr": tr, "s": s,
                             "i": i, "n": len(tr["sessions"])})
    for k, item in enumerate(flat):
        item["prev"] = flat[k - 1] if k else None
        item["next"] = flat[k + 1] if k + 1 < len(flat) else None
        item["first_of_chapter"] = item["i"] == 0
        item["last_of_chapter"] = item["i"] == item["n"] - 1
        # A one-lesson chapter is both. It is never a close: there is nothing
        # behind it to close, and saying so on the front door of the whole
        # commons reads as an ending on the first video somebody watches.
        item["closes_chapter"] = item["last_of_chapter"] and item["n"] > 1
    return flat


def board(ex: dict) -> str:
    """What to draw while talking. The diagram is already the lesson's spine."""
    dia = (ex.get("diagram") or "").strip("\n")
    head = [ln for ln in dia.splitlines() if ln.strip()][:1]
    return head[0].strip() if head else "the component map"


def minutes(runs: bool, oriented: bool) -> str:
    """Honest length. An orientation beat and a live run both cost time."""
    return "3–4 min" if oriented else ("2–3 min" if runs else "2 min")


def grounding_line(sid: str, item: dict) -> str:
    """The CyberTravels line, phrased for where the viewer actually is.

    The lead-in used to be the same everywhere — "the same company we have been
    following" — which is a lie on lesson one and the reason the opening of the
    curriculum read as though the viewer had missed something.
    """
    g = GROUNDING.get(sid)
    if not g:
        return ""
    if sid == "A0.1":
        note = "you have not introduced it yet, so you are only planting the name"
    elif sid == FUNCTION_INTRO.get(item["fn"]["id"]):
        note = "name the company again — a lot of people start watching here"
    else:
        note = "same company, same four agents, new way of failing"
    return f"**In CyberTravels** *({note})*\n\n{plain(g)}"


def continuity(item: dict) -> str:
    """One line saying what the viewer is walking in from.

    A recording has no sidebar and no breadcrumb. Without this, lesson forty is
    a stranger; with it, the series is one argument.
    """
    sid = item["s"]["id"]
    if item["prev"] is None:
        return ("**Where we are.** The very beginning — this is the first thing "
                "anybody watches. Nothing to refer back to, so do not refer back.")
    p = item["prev"]
    if item["first_of_chapter"]:
        b = BRIDGES.get(p["tr"]["id"], {})
        gap = plain(b.get("gap", "")) if b else ""
        # A new function is a bigger step than a new chapter and the viewer has
        # to be told which one they just took — the whole question being asked
        # of CyberTravels changes here, not just the subject matter.
        if p["fn"]["id"] != item["fn"]["id"]:
            opener = (f"**Where we are.** New function, not just a new chapter — "
                      f"say so. Function {p['fn']['id']} asked one question of "
                      f"CyberTravels and finished; Function {item['fn']['id']}, "
                      f"{plain(item['fn']['title'])}, asks a different one of the "
                      f"same company. Chapter {p['tr']['id']} left off here")
        else:
            opener = (f"**Where we are.** New chapter. Chapter {p['tr']['id']} ended "
                      f"on what it could not do")
        return (f"{opener}: “{first_sentences(gap, 1)}” That is what this "
                f"one picks up." if gap else f"{opener}. This chapter picks it up.")
    return (f"**Where we are.** Straight on from {p['s']['id']}, "
            f"{plain(p['s']['title'])}. One sentence on that, then move — do not "
            f"recap, the viewer either saw it or did not.")


def handover(item: dict, ex: dict) -> list[str]:
    """The last beat: their turn, then where they are going.

    Always names the next lesson by id and title. A script that ends on "go and
    try this" and nothing else is a script that ends the series every time.
    """
    out = []
    if challenge := ex.get("challenge"):
        out.append(first_sentences(challenge, 2))
    else:
        out.append("Go and try this against a system you actually run. That is "
                   "where it stops being a lesson.")

    final = item["next"] is None
    if item["closes_chapter"]:
        b = BRIDGES.get(item["tr"]["id"], {})
        if gained := b.get("gained"):
            out.append(f"**That closes Chapter {item['tr']['id']}.** "
                       f"{first_sentences(gained, 2)}")
        if gap := b.get("gap"):
            # On the very last lesson there is no next chapter to sell, so the
            # gap is the honest ending rather than a hook. Saying "the reason
            # anybody clicks the next chapter" there points at nothing.
            why = ("Say this part slowly — it is the honest ending, and it is "
                   "better than pretending the subject is finished."
                   if final else
                   "Say this part slowly — it is the reason anybody clicks the "
                   "next chapter.")
            out.append(f"**And here is what it still cannot do.** "
                       f"{first_sentences(gap, 2)} {why}")
        if (nxt := b.get("next")) and not final:
            # The bridge already ends with its own "Next → A2.1, agent identity"
            # pointer. Left in, it prints twice in one line. Strip that tail and
            # re-add the pointer below from the curriculum, so the id and the
            # title are the real ones rather than a second copy that can drift.
            body = re.sub(r"\s*Next\s*→.*$", "", plain(nxt)).strip()
            out.append(f"**Then the next chapter.** {first_sentences(body, 2)}")

    if n := item["next"]:
        out.append(f"**Next →** {n['s']['id']} · {plain(n['s']['title'])}.")
    else:
        if last_word := BRIDGES.get(item["tr"]["id"], {}).get("next"):
            out.append(f"**Leave them with this.** "
                       f"{first_sentences(last_word, 2)}")
        out.append("**That is the last lesson in the commons.** Say so, thank them, "
                   # Not "on Monday morning". A weekday standing in for "soon"
                   # is the house rule check_clarity.py enforces on every
                   # rendered page, and it does not stop applying because this
                   # file is read aloud instead of read.
                   "and point at the one thing you would go and do first thing "
                   "tomorrow — name a real thing, not “keep learning”.")
    return out


def script(item: dict) -> str:
    fn, tr, s = item["fn"], item["tr"], item["s"]
    sid = s["id"]
    ex = EXERCISES.get(sid, {})
    d0, d1, d2 = DAYS.get(sid, ("", "", ""))
    runs = any(k in ("py", "skill_script", "model")
               for k, _ in ex.get("steps", []))
    orient = ORIENT.get(sid)

    out = [f"### {sid} · {s['title']}", ""]
    out.append(f"Chapter {tr['id']} · lesson {item['i'] + 1} of {item['n']} · "
               f"{'runs a skill' if runs else 'reading lesson'} · "
               f"{minutes(runs, bool(orient))} · "
               f"[page]({SITE}/lessons/{sid}.html)")
    out.append("")
    out.append(continuity(item))
    out.append("")
    out.append(f"**On the board.** {board(ex)}")
    out.append("")

    if orient:
        out.append("#### ⓪ First, the ground rules *(30–45s — only on this lesson)*")
        out.append("")
        for para in orient:
            out.append(para)
            out.append("")

    out.append("#### ① Open — the scene *(15–20s)*")
    out.append("")
    out.append(plain(ex.get("hook", s.get("risk", ""))))
    out.append("")

    out.append("#### ② Why it costs something — Day 0 *(20–30s)*")
    out.append("")
    out.append(plain(d0 or s.get("risk", "")))
    if g := grounding_line(sid, item):
        out.append("")
        out.append(g)
    out.append("")

    out.append("#### ③ What we build — Day 1 *(30–45s)*")
    out.append("")
    out.append(plain(d1 or s.get("control", "")))
    # The run belongs here, with the work. It used to sit under the number,
    # which is how "then we run it" ended up printed directly above "nothing is
    # computed in this lesson" on the lessons that produce no measurement.
    if runs:
        out.append("")
        out.append("**Then run it on camera.** Not a screenshot — the real thing, "
                   "and say that they can run the identical cell in their own "
                   "Kaggle account in about a minute.")
    out.append("")

    out.append("#### ④ The number — Day 2 *(20–30s)*")
    out.append("")
    out.append(plain(d2 or "This one produces no number. Say that, and say what "
                           "you count instead — it buys more than a figure you "
                           "invented."))
    if expect := ex.get("expect"):
        out.append("")
        out.append(f"*On screen (do not read this out, point at it):* "
                   f"{first_sentences(expect, 2)}")
    out.append("")

    out.append("#### ⑤ Hand it over *(10–15s)*")
    out.append("")
    for para in handover(item, ex):
        out.append(para)
        out.append("")

    out.append("---")
    out.append("")
    return "\n".join(out)


HEADER = """# LIGHTBOARD.md — what to say, lesson by lesson

A recording script for all 134 lessons. Written to be **read aloud**, which is
a different job from the page: a reader can go back, a viewer cannot, so every
line has to land the first time.

## Record these six first

Do not start at lesson one and grind forwards. Record the **entry points**
first, in this order, because they are where people actually arrive and they
are the only ones that carry an orientation beat for somebody who has never
shipped an agent:

| order | lesson | opens |
|---|---|---|
| 1 | **A0.1** | the whole commons — what an agent is, and what this is |
| 2 | **A1.0** | Function A, and CyberTravels itself. The one that has to land |
| 3 | **B2.0** | Function B — the AI SDLC |
| 4 | **C1.0** | Function C — red teaming agents, not models |
| 5 | **D1.0** | Function D — the SOC |
| 6 | **E1.0** | Function E — governance |

Those six are three to four minutes each. Everything after them is two to
three, because the ground rules are already laid and you never have to lay
them again.

Then take a whole chapter at a time rather than jumping around. The chapter
close is written as a close — it names what you gained, what it still cannot
do, and the next chapter — and that only works if you recorded the chapter.

## The shape of one lesson

Each lesson is one continuity line and five beats. Say them in order and you
have a recording.

| beat | what it is | roughly |
|---|---|---|
| **Where we are** | one line. What the last lesson left them holding | 5–10s |
| **① Open** | the scene. No preamble, no "in this lesson we will" | 15–20s |
| **② Why it costs** | Day 0 — what goes wrong if you do nothing — then the same thing inside CyberTravels | 20–30s |
| **③ What we build** | Day 1 — the thing you draw, and the run on camera | 30–45s |
| **④ The number** | Day 2 — what comes out, and what it means | 20–30s |
| **⑤ Hand it over** | their turn, then the name of the next lesson | 10–15s |

The six entry-point lessons add a **⓪ ground rules** beat before the open.
Nothing else does — say it once and never again.

## Reading it well

- **Do not read this word for word.** It is the beat, in your words on the day.
  The one exception is a number: say those exactly.
- **Start cold — after the first six.** No "hello and welcome". Somebody landed
  here from a search result and gives you eight seconds. But on an entry point,
  the ⓪ beat comes first: a viewer who does not know what an agent is cannot be
  hooked by a scene about one.
- **Always say where you are.** The continuity line is not optional padding. A
  recording has no sidebar and no breadcrumb, so without it lesson forty is a
  stranger and with it the series is one argument.
- **Name CyberTravels every time** — but check how. On the first lesson you are
  planting the name, on a function opener you are re-introducing it, and
  everywhere else it is the same company failing in a new way. Each lesson below
  tells you which.
- **Never oversell the number.** Where a lesson has a real measurement, say it
  flatly and let it do the work. Where it does not, say that too — "this one
  produces no number, and here is what you count instead" buys more credibility
  than a number you invented.
- **What is on screen is not what you say.** Where a lesson prints output, the
  script marks it *on screen* — point at it, do not narrate exit codes.
- **On the board:** the line given per lesson is the diagram's own first line.
  Draw it as you talk; do not draw it first and then explain it.

## Keeping it true

Generated by `scripts/build_lightboard.py` from the same sources the lessons
are built from — the hook, the CyberTravels grounding, Day 0/1/2, what the run
proves, the challenge, and the chapter bridges. Edit a lesson and re-run it; do
not hand-edit this file, it is overwritten. The connective phrasing and the six
orientation beats are in the generator; everything else is each lesson's own.

---
"""


def build() -> str:
    doc = [HEADER]
    current_fn = None
    for item in lessons():
        fn = item["fn"]
        if fn["id"] != current_fn:
            current_fn = fn["id"]
            fd = FUNCTION_DAYS.get(fn["id"], {})
            doc.append(f"\n## Function {fn['id']} — {fn['title']}\n")
            if who := fd.get("who"):
                doc.append(f"**Who you are talking to.** {plain(who)}\n")
            if d0 := fd.get("day0"):
                doc.append(f"**The pitch for this whole function, in one breath.** "
                           f"{first_sentences(d0, 2)}\n")
            if intro := FUNCTION_INTRO.get(fn["id"]):
                doc.append(f"**Record {intro} first.** It carries the ground-rules "
                           f"beat for this function; every lesson after it assumes "
                           f"you said it.\n")
            doc.append("---\n")
        doc.append(script(item))
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
    print(f"wrote {OUT.name} — {n} lesson scripts, {len(ORIENT)} with an "
          f"orientation beat, {len(text.split())} words, "
          f"about {n * 2.5 + len(ORIENT):.0f} minutes of recording")
    return 0


if __name__ == "__main__":
    sys.exit(main())
