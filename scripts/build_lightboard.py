#!/usr/bin/env python3
"""Generate LIGHTBOARD.md — a word-for-word speaking script for every lesson.

This is written to be **read aloud verbatim**. That is a stronger promise than
the earlier version made, and it changes what the generator has to emit: not
beats to paraphrase, but finished sentences. Somebody recording 134 videos
should be able to look at the page and talk, without translating notes into
speech on camera.

Two rules follow from that, and they are the whole design:

1. **Everything is a complete, speakable sentence.** The lesson sources are not
   uniformly sentence-shaped — Day 1 is usually an imperative ("Run it in an
   isolate…") and Day 2 is usually a bare noun phrase ("Share of tool calls
   whose selecting text came from a trusted origin"). Neither can be joined to
   a lead-in with a colon without producing something nobody can say. So every
   frame here ends its own sentence first, and the fragment follows as its own
   utterance, which is exactly how people talk.

2. **What you say and what you do are never mixed.** Spoken words are plain
   paragraphs. Stage directions — draw this, run the skill, point at the output
   — are in square brackets and italics, and the header says once that those
   are the only things not read aloud.

**Every lesson is a story with a position in a longer one.** Position is
computed rather than assumed, because assuming it produced three bugs that were
worst exactly where they mattered most — the first recording somebody watches:
the CyberTravels line said "the same company we have been following" on lesson
one; "then we run it" printed above "nothing is computed here"; and "that
closes this chapter" was said on a chapter *opener*, since a one-lesson chapter
is both first and last.

The shape per lesson:

    ⓪ GROUND RULES  only on the six entry points — spoken, for a newcomer.
    ① OPEN          the scene, no preamble.
    ② WHY IT COSTS  Day 0, then the same thing inside CyberTravels.
    ③ WHAT WE DO    Day 1 — the thing on the board, and the run.
    ④ THE NUMBER    Day 2 — what comes out, and what it means.
    ⑤ HAND OVER     the challenge, and the name of the next lesson.

The substance is pulled from the same sources the lesson is built from — hook,
grounding, Day 0/1/2, expected output, challenge, chapter bridge — so a script
cannot describe a lesson that no longer exists. The connective sentences and
the six orientation beats are written here.

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
WPM = 140          # unhurried delivery to camera, measured against a read-through

# --- the six entry points ----------------------------------------------------
#
# The only substantive prose in this generator, and it is here rather than in
# the lesson sources on purpose: it is what the presenter says, not what the
# page says. It exists because "start cold" is excellent advice for lesson
# ninety and useless for lesson one — a viewer who has never shipped an agent
# cannot be hooked by a scene about one, and thirty seconds spent on the
# definition is what makes every later cold open land.
#
# Keyed by lesson id: A0.1 is the front door of the whole commons, and the
# other five are FUNCTION_INTRO — where somebody arriving from a search result
# actually lands. Written as words to say, in the first person, out loud.
ORIENT = {
 "A0.1": [
  "Before anything else, thirty seconds on what an agent actually is, because "
  "if you have never shipped one, none of the rest of this will land properly.",
  "A model that only answers questions is a chatbot. Give it tools — let it "
  "call an API, read a file, move money — and give it a loop that decides "
  "which tool to call next, and now it is an agent. That is the entire "
  "difference. And it is also the entire problem. A chatbot that is wrong says "
  "something wrong. An agent that is wrong does something wrong. Everything "
  "here follows from that one sentence.",
  "So, what this is. A hundred and thirty-five lessons. It is free, there is no "
  "vendor, there is no paid account, and every single one of them runs — one "
  "command on your own machine, in whichever coding assistant you already use. "
  "I am going to use one made-up company for all of it, and I will introduce "
  "you to them in the next video.",
 ],
 "A1.0": [
  "Let me introduce you to CyberTravels, because you are going to be seeing a "
  "lot of them.",
  "CyberTravels is a corporate travel company that does not exist. I made them "
  "up. They run four agents, and one of those agents can issue refunds. I "
  "invented them deliberately, and here is why.",
  "Every lesson, in all five functions, is grounded in this same company. So "
  "the refund limit an attacker walks straight past in one lesson is the same "
  "limit a detection is watching in another, and the same limit a compliance "
  "report is counting in a third. By the fourth function you are not learning a "
  "fourth example. You are watching a system you already understand fail in a "
  "new way.",
 ],
 "B2.0": [
  "If you have done application security before, let me tell you what is "
  "different here, because otherwise you will assume you can skip this chapter.",
  "The pipeline is not new. What is new is that code now arrives faster than "
  "any human review can keep up with, and some of it was written by an agent "
  "that cannot tell you why it wrote it. Everything in this chapter comes out "
  "of that one pressure.",
 ],
 "C1.0": [
  "One distinction before we start, because most people hear red team and think "
  "jailbreaks.",
  "Getting a model to say something it should not say is a prompt result. "
  "Getting an agent to do something it should not do — spend money, touch a "
  "file, message another agent — is an incident. This chapter is about the "
  "second one, and it is the one almost nobody has a playbook for.",
 ],
 "D1.0": [
  "Let me say this up front: your SOC already works. You have sensors, you have "
  "a lake, you have rules, you have an on-call rota. None of that is wrong, and "
  "none of it is getting replaced here.",
  "The question this whole chapter asks is narrower than that, and a bit more "
  "uncomfortable. When an agent is the thing that went wrong — would any of it "
  "have fired?",
 ],
 "E1.0": [
  "Governance has a reputation, so let me get ahead of it. Most people hear "
  "that word and picture a spreadsheet nobody reads.",
  "Here is what I actually mean by it: being able to show, later, and to "
  "somebody who is not on your side, that a decision was made on purpose and by "
  "a named person. That is an engineering problem. And it is the one that "
  "decides whether the thing you built is allowed to stay switched on.",
 ],
}

# Substitutions applied to every spoken line. Each is here because the source
# is written to be read on a page and this file is read into a microphone.
SAY_SUBS = [
    (re.compile(r"(\d)\s*%"), r"\1 percent"),          # "29%" -> "29 percent"
    (re.compile(r"\s*→\s*"), ", then "),           # ingress -> agent_runtime
    (re.compile(r"\s*->\s*"), ", then "),
    (re.compile(r"\s*&\s*"), " and "),
    (re.compile(r"~(\d)"), r"about \1"),
    # Tool names are written as identifiers and said as words. issue_refund is
    # "issue refund" out loud; nobody says the underscore.
    (re.compile(r"\b([a-z]+)_([a-z_]+)\b"),
     lambda m: m.group(0).replace("_", " ")),
]


def say(text: str) -> str:
    """One spoken line: markdown stripped, and said the way a person says it.

    A script full of asterisks, backticks and snake_case is a script somebody
    stumbles over on the third take.
    """
    t = text.strip()
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)     # links -> their text
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", t)
    t = re.sub(r"^#+\s*", "", t, flags=re.M)
    t = re.sub(r"\s*\n\s*", " ", t)
    for pat, rep in SAY_SUBS:
        t = pat.sub(rep, t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    # Every spoken line ends as a sentence. Several sources are fragments with
    # no terminal stop, and a script that runs two of them together is a script
    # that gets read as one breathless clause.
    return t if not t or t[-1] in ".!?:—" else t + "."


def drop_pointer(text: str) -> str:
    """Strip a chapter bridge's own trailing "Next → A2.1, agent identity".

    Left in, it prints twice in one closing beat. It has to be removed from the
    RAW text, before say(): the arrow substitution turns it into ", then A2.1"
    first, and then there is no pointer left to match. The pointer is re-added
    afterwards from the curriculum, where the id and the title cannot drift.
    """
    return re.sub(r"\s*Next\s*(→|->).*$", "", text).strip()


def sentences(text: str, n: int = 2, cap: int = 320) -> str:
    """The opening of a block, cut at a sentence end rather than mid-clause."""
    parts = re.split(r"(?<=[.!?])\s+", say(text))
    out = ""
    for p in parts[:n]:
        if out and len(out) + len(p) + 1 > cap:
            break
        out = f"{out} {p}".strip()
    return out


def lessons() -> list[dict]:
    """Every lesson, flat, each knowing where it sits.

    The neighbours are computed once because three beats need them: continuity
    at the top, the chapter close at the bottom, and whether this is the first
    thing anybody watches.
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
        # behind it to close, and saying so on the front door of the commons
        # reads as an ending on the first video somebody watches.
        item["closes_chapter"] = item["last_of_chapter"] and item["n"] > 1
    return flat


def board(ex: dict) -> str:
    """What to draw while talking. The diagram is already the lesson's spine."""
    dia = (ex.get("diagram") or "").strip("\n")
    head = [ln for ln in dia.splitlines() if ln.strip()][:1]
    return head[0].strip() if head else "the component map"


def opening(item: dict) -> list[tuple[str, str]]:
    """The spoken bridge in from whatever the viewer just watched.

    A recording has no sidebar and no breadcrumb. Without this, lesson forty is
    a stranger; with it, the series is one argument. It is deliberately short
    mid-chapter — a bridge, not a recap — and does the real work at the
    boundaries, where a viewer has just changed subject or changed function.
    """
    if item["prev"] is None:
        return []
    p = item["prev"]
    if not item["first_of_chapter"]:
        return [("say", f"Still inside chapter {item['tr']['id']}. Last one was "
                        f"{say(p['s']['title'])}")]

    gap = sentences(BRIDGES.get(p["tr"]["id"], {}).get("gap", ""), 1)
    out = []
    if p["fn"]["id"] != item["fn"]["id"]:
        out.append(("say",
                    f"That is Function {p['fn']['id']} done. Function "
                    f"{item['fn']['id']} asks a different question of the same "
                    f"company: {say(item['fn']['title'])}"))
    if gap:
        out.append(("say", f"Chapter {p['tr']['id']} left us here. {gap} "
                           f"That is what this chapter picks up."))
    elif not out:
        out.append(("say", f"New chapter. Chapter {p['tr']['id']} is done, and "
                           f"this one picks up where it stopped."))
    return out


def grounding_line(sid: str, item: dict) -> list[tuple[str, str]]:
    """The CyberTravels line, said the way it is true where the viewer is.

    The lead-in used to be identical everywhere — "the same company we have
    been following" — which is a lie on lesson one and the reason the opening
    of the curriculum read as though the viewer had missed something.
    """
    g = GROUNDING.get(sid)
    if not g:
        return []
    if sid == "A0.1":
        lead = ("You have not met CyberTravels yet — that is the next video — "
                "but here is where they come in.")
    elif sid == FUNCTION_INTRO.get(item["fn"]["id"]):
        lead = ("And this is CyberTravels again — the same company, because a lot "
                "of people start watching here.")
    else:
        lead = "Same company, same four agents, new way of failing."
    return [("say", f"{lead} {say(g)}")]


def closing(item: dict, ex: dict) -> list[tuple[str, str]]:
    """Their turn, then where they are going next.

    Always names the next lesson. A script that ends on "go and try this" and
    nothing else ends the series every time.
    """
    out = [("say", sentences(ex.get("challenge") or
                             "Go and try this against a system you actually run. "
                             "That is where it stops being a lesson.", 2))]
    final = item["next"] is None

    if item["closes_chapter"]:
        b = BRIDGES.get(item["tr"]["id"], {})
        if gained := b.get("gained"):
            out.append(("say", f"That closes chapter {item['tr']['id']}. "
                               f"{sentences(gained, 2)}"))
        if gap := b.get("gap"):
            out.append(("do", "Slow down here. This is the reason anybody clicks "
                              "the next chapter." if not final else
                              "Slow down here. This is the ending — do not "
                              "rush it, and do not pretend the subject is "
                              "finished."))
            out.append(("say", f"And here is what it still cannot do. "
                               f"{sentences(gap, 2)}"))
        if (nxt := b.get("next")) and not final:
            out.append(("say", sentences(drop_pointer(nxt), 2)))

    if n := item["next"]:
        out.append(("say", f"Next up: {n['s']['id']}, {say(n['s']['title'])}"))
    else:
        if last := BRIDGES.get(item["tr"]["id"], {}).get("next"):
            out.append(("say", sentences(drop_pointer(last), 2)))
        out.append(("do", "That is the last lesson in the commons. Thank them, "
                          "and name one real thing you would go and do first "
                          "thing tomorrow — a real thing, not “keep learning”."))
    return out


def beats(item: dict) -> list[tuple[str, str, str]]:
    """The whole lesson as (heading, kind, text), kind being say or do."""
    s = item["s"]
    sid = s["id"]
    ex = EXERCISES.get(sid, {})
    d0, d1, d2 = DAYS.get(sid, ("", "", ""))
    runs = any(k in ("py", "skill_script", "model")
               for k, _ in ex.get("steps", []))

    rows: list[tuple[str, str, str]] = []

    def add(head, kind, text):
        rows.append((head, kind, text))

    if orient := ORIENT.get(sid):
        h = "⓪ Ground rules — only on this lesson"
        add(h, "do", f"Draw nothing yet. Talk to camera.")
        for para in orient:
            add(h, "say", say(para))

    h = "① Open"
    for kind, text in opening(item):
        add(h, kind, text)
    # The board line and the expected output are shown, not folded into the
    # bracketed direction: both routinely contain square brackets themselves
    # ("[ user ] --- ... ---> ingress", "[Errno 2]"), and a direction that
    # nests brackets breaks the one rule this file has.
    add(h, "do", "Draw this as you talk. Do not draw it first and then explain it.")
    add(h, "draw", board(ex))
    add(h, "say", say(ex.get("hook", s.get("risk", ""))))

    h = "② Why it costs something"
    add(h, "say", "Here is what that costs you.")
    add(h, "say", say(d0 or s.get("risk", "")))
    for kind, text in grounding_line(sid, item):
        add(h, kind, text)

    h = "③ What we do about it"
    add(h, "say", "So here is what we do in this lesson.")
    add(h, "say", say(d1 or s.get("control", "")))
    # The run belongs here, with the work. It used to sit under the number,
    # which is how "then we run it" ended up printed directly above "nothing is
    # computed in this lesson" on every lesson that produces no measurement.
    if runs:
        add(h, "do", "Run the skill on camera now. Let it finish on screen.")
        add(h, "say", "That is not a screenshot. It just ran, and you can run "
                      "the identical command on your own machine in about a "
                      "minute.")

    h = "④ The number"
    # Not every lesson produces one, and roughly a dozen say so in Day 2 itself
    # — "Nothing is computed here", "No number yet". Announcing "here is the
    # number" directly above that is the same contradiction that used to put
    # "then we run it" above "nothing is computed", so the frame is chosen from
    # what Day 2 actually says rather than assumed.
    numberless = re.match(r"\s*(nothing|none|no\b|not yet)", (d2 or "").lower())
    if d2 and not numberless:
        add(h, "say", "And here is the number that tells you it worked.")
    else:
        add(h, "say", "Now, this one does not hand you a number, and I would "
                      "rather say that out loud than invent one.")
    add(h, "say", say(d2 or "So here is what you count instead: whether you can "
                            "do the thing this lesson described, on a system you "
                            "actually run."))
    if expect := ex.get("expect"):
        add(h, "do", "Point at the output on screen. Do not read it out.")
        add(h, "show", sentences(expect, 2))

    h = "⑤ Hand it over"
    for kind, text in closing(item, ex):
        add(h, kind, text)
    return rows


def script(item: dict) -> str:
    s = item["s"]
    sid = s["id"]
    ex = EXERCISES.get(sid, {})
    runs = any(k in ("py", "skill_script", "model")
               for k, _ in ex.get("steps", []))
    rows = beats(item)
    words = sum(len(t.split()) for _, kind, t in rows if kind == "say")

    out = [f"### {sid} · {s['title']}", ""]
    out.append(f"Chapter {item['tr']['id']} · lesson {item['i'] + 1} of "
               f"{item['n']} · {'runs a skill' if runs else 'reading lesson'} "
               f"· {words} words, about {words / WPM:.1f} min spoken · "
               f"[page]({SITE}/lessons/{sid}.html)")
    out.append("")

    head = None
    for h, kind, text in rows:
        if h != head:
            head, _ = h, out.append(f"**{h}**")
            out.append("")
        if kind == "do":
            out.append(f"*[{text}]*")
        elif kind == "draw":
            out.append("```")
            out.append(text)
            out.append("```")
        elif kind == "show":
            out.append(f"> {text}")
        else:
            out.append(text)
        out.append("")

    out.append("---")
    out.append("")
    return "\n".join(out)


HEADER = """# LIGHTBOARD.md — the word-for-word script, lesson by lesson

A recording script for all 134 lessons, written to be **read aloud exactly as
written**. Open the lesson, talk. No translating notes into sentences while the
camera is running.

## The one rule

**Read every plain line word for word. Never read a line in square brackets.**

Square-bracketed italics are stage directions — draw this, run the skill, point
at the output, slow down. Everything else is speech, already in sentences,
already said the way a person says it: no asterisks, no backticks, "29 percent"
rather than "29%", "issue refund" rather than `issue_refund`.

## Record these six first

Do not start at lesson one and grind forwards. Record the **entry points**
first, in this order, because they are where people actually arrive and they
are the only ones carrying a ground-rules beat for somebody who has never
shipped an agent:

| order | lesson | opens |
|---|---|---|
| 1 | **A0.1** | the whole commons — what an agent is, and what this is |
| 2 | **A1.0** | Function A, and CyberTravels itself. The one that has to land |
| 3 | **B2.0** | Function B — the AI SDLC |
| 4 | **C1.0** | Function C — red teaming agents, not models |
| 5 | **D1.0** | Function D — the SOC |
| 6 | **E1.0** | Function E — governance |

Say the ground rules once, in those six, and never again. Every lesson after
them assumes you said it.

Then take a whole chapter at a time rather than jumping around. The chapter
close is written as a close — what you gained, what it still cannot do, and the
next chapter — and that only works if you recorded the chapter.

## The shape of one lesson

| beat | what happens | roughly |
|---|---|---|
| **① Open** | one bridge line from the last lesson, then the scene | 20–30s |
| **② Why it costs something** | Day 0 — what goes wrong if you do nothing — then CyberTravels | 20–30s |
| **③ What we do about it** | Day 1, and the run on camera | 30–45s |
| **④ The number** | Day 2 — what comes out, and what it means | 20–30s |
| **⑤ Hand it over** | their turn, then the name of the next lesson | 10–15s |

The six entry points add a **⓪ ground rules** beat before the open. Nothing
else does.

Each lesson's heading gives its spoken word count and the time that comes to at
an unhurried 140 words a minute. That is words only — it does not count the
pause while the skill runs, so budget a little more on the lessons that execute
something. A model takes longer than a local computation did.

## Reading it well

- **The script is the floor, not the ceiling.** It is written to work read
  straight. If a better sentence arrives on the day, take it — but the numbers
  are exact, so say those as written.
- **Start cold, after the first six.** No "hello and welcome". Somebody landed
  here from a search result and gives you eight seconds. On an entry point the
  ⓪ beat comes first: a viewer who does not know what an agent is cannot be
  hooked by a scene about one.
- **The bridge line is not padding.** A recording has no sidebar. Without it
  lesson forty is a stranger; with it the series is one argument.
- **Never oversell the number.** Where a lesson has a real measurement the
  script says it flatly — let it do the work. Where there is none, the script
  says so out loud, which buys more than a figure you invented.
- **Draw while you talk**, not before. The board line is the lesson diagram's
  own first line.

## Keeping it true

Generated by `scripts/build_lightboard.py` from the same sources the lessons
are built from — the hook, the CyberTravels grounding, Day 0/1/2, the expected
output, the challenge, and the chapter bridges. Edit a lesson and re-run it; do
not hand-edit this file, it is overwritten. The connective sentences and the six
ground-rules beats live in the generator; everything else is each lesson's own.

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
                doc.append(f"*[Who is watching: {say(who)}]*\n")
            if d0 := fd.get("day0"):
                doc.append(f"*[The pitch for the whole function, if you need it "
                           f"in one breath: {sentences(d0, 2)}]*\n")
            if intro := FUNCTION_INTRO.get(fn["id"]):
                doc.append(f"*[Record {intro} first. It carries the ground-rules "
                           f"beat for this function, and every lesson after it "
                           f"assumes you said it.]*\n")
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

    spoken = sum(len(t.split()) for item in lessons()
                 for _, kind, t in beats(item) if kind == "say")
    OUT.write_text(text)
    print(f"wrote {OUT.name} — {n} word-for-word scripts, {len(ORIENT)} with a "
          f"ground-rules beat, {spoken} spoken words, "
          f"about {spoken / WPM / 60:.1f} hours of recording")
    return 0


if __name__ == "__main__":
    sys.exit(main())
