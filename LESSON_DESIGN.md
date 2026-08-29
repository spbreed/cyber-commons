# How a Cyber Commons lesson is built

Every one of the 121 lessons has the same shape. Not for tidiness — each rule
below is here because breaking it made a lesson worse in a specific,
reproducible way.

`scripts/check_lessons.py` enforces what can be enforced and reports the rest.
It runs in CI.

---

## 1 · One concept, in three parts

A lesson teaches **one** thing. If you cannot say what it is in a sentence, it
is two lessons.

| Part | Field | What it is |
|---|---|---|
| **Hook** | `hook` | 20–90 words. Why this matters, as a consequence. |
| **Framework** | `diagram` + `concept` | The picture, then the idea it names. |
| **Practical application** | `steps` | The idea working, where it breaks, the control. |

**The hook is a consequence, not a definition.** "An agent has three
identities" is a definition. "Four agents share one service account, and the
audit log answers *what happened* perfectly and cannot answer *which one* at
all" is a hook. It is concrete, it is specific, and the reader wants the next
paragraph.

Never open with "in this lesson we will". The reader can see the title.

## 2 · The picture before the terminal

The `diagram` is rendered **before the first code cell**, always. The build
refuses a lesson without one and `check_lessons.py` fails if a code cell ever
precedes the framework.

The "why" and the "what" belong to a diagram. Only the "how" belongs to a
terminal. Leading with the terminal produces a reader who can reproduce your
keystrokes and cannot say what they were for.

Diagrams are **plain ASCII**, monospace, roughly 60 columns. Box-drawing
characters and colour do not survive every renderer; `+--+` does. A good
diagram fits on a screen and has at most one idea in it — if it needs a legend,
it is two diagrams.

Hooks, diagrams and chapter bridges all live in
[`scripts/exercises/framing.py`](scripts/exercises/framing.py), apart from the
lesson bodies, because keeping all 121 of each in one file is the only way to
see whether they are consistent with one another.

## 3 · Sections are renumbered by the build

Write `## 2 · …`, `## 3 · …` in your steps and stop thinking about it. The
build renumbers every `## N ·` heading sequentially after the framework, so
adding a section to the template never means editing 121 exercise files.

Markdown steps must use **real newlines**. A `"\n"` inside a normal Python
string is two characters and used to render as literal `\n` on the lesson page;
the build now normalises it, but write it correctly.

## 4 · Realistic demos — show the failure

A demo that only ever works has told the reader nothing they could not have
assumed. Where it is relevant — and it usually is — the lesson should:

- **narrate the actual steps**, including the ones that did not work;
- **show the error**, not a description of the error;
- **show the control failing first**, then holding, so the reader can see what
  the control is for;
- **print the number that is worse**, not only the one that improved.

Risk lessons are exempt in the obvious sense: for them the failure *is* the
demonstration. `check_lessons.py` reports every non-risk lesson whose output
contains no failure signal at all, so the count cannot drift quietly.

The same rule governs a recording. If a command fails on camera, keep it and
say why it failed. A flawless take teaches people that their own first attempt
going wrong means they are doing it wrong.

## 5 · Every chapter ends on the gap

The last lesson of each chapter carries a bridge, in `BRIDGES`, with three
moves and only three:

1. **What you can do now.** The skill, stated as a capability.
2. **What you still cannot do.** The flaw that skill still has — named plainly,
   not hedged.
3. **The next chapter as the answer**, with the specific lesson to open.

A chapter that ends without this reads as though the subject is closed. Almost
none of them are.

---

## Writing a new lesson

```python
# scripts/exercises/track_<id>.py
"B2.13": {
 "concept": """...the idea, in prose...""",
 "steps": [
   ("md", "## 2 · Demo — the idea working"),
   ("py", '''...'''),
   ("md", "## 3 · Where it breaks"),
   ("py", '''...'''),
   ("md", "## 4 · The control, and a check that it holds"),
   ("py", '''...'''),
 ],
 "expect": "what a correct run prints",
 "challenge": "the same thing, against a system you own",
},
```

```python
# scripts/exercises/framing.py
HOOKS["B2.13"] = "..."       # 20-90 words, a consequence
DIAGRAMS["B2.13"] = """..."""  # ASCII, ~60 columns
```

Then:

```bash
python3 scripts/build_notebooks.py
python3 scripts/run_notebooks.py --session B2.13
python3 scripts/check_lessons.py
python3 scripts/check_determinism.py --session B2.13
python3 scripts/build_curriculum.py && python3 scripts/build_site.py
```

Code cells use the **standard library only** — no imports outside it, nothing
to clone, no `pip install` — and must be **deterministic**: seed from
`zlib.crc32` rather than `hash()`, sort before iterating a set, and give every
sort a full tiebreak. Both are gates in CI.
