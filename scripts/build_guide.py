#!/usr/bin/env python3
"""Render the Function A course guide to site/guide/function-a.html.

    python3 scripts/build_guide.py            # write the page
    python3 scripts/build_guide.py --check    # fail if it has drifted

**Two readers.** Somebody working through Function A alone, and somebody
running it for a room. It was built as a trainer guide and is now both, which
was a content change rather than a retitle: every lab's notes are split into
what both readers need and a room-only half rendered in its own block, so a
solo reader can skip the instructions to project things and a trainer can
still find them.

**Why this is generated.** A guide repeats facts that live in the lesson
sources — how many lessons there are, what each lab prints, which ceiling
fires at what number — and a hand-written draft of this one reached review
with three of them already wrong: fifteen lessons when there were sixteen,
"seven to nine components" after A1.0 had settled on nine, and A2.4's output
accuracy at 0.600 after the scorer was corrected to 0.400. This page is read
standing in front of a class, or alone with nobody to catch the error, so a
stale number here is worse than a stale number in a design document.

So the narrative lives in `scripts/exercises/guide_a.py` and **every number is
measured here**: lesson titles, Risk and Control and the lab line come from
`curriculum.json`; the component count from the architecture-map skill's own
fixture; the tool table from `cybertravels/config.TOOL_POLICY`; the span kinds
by reading the calls in `cybertravels/`; the ceilings from `config` and
`a2a/protocol`; A2.4's six numbers by calling the skill's own scoring
functions; the reading volume by counting the lesson prose.
`{placeholders}` in an expected output are filled from that measurement, and
**an unknown placeholder is an error** rather than a silent gap — which is the
mechanism that stops a number here going stale again.

The page is written to `site/guide/` rather than `site/lessons/`, because
`build_site.py` prunes any `*.html` in `site/lessons/` that is not a current
lesson page. A guide put there would be deleted by the next build. A generated
one-line redirect stays at the page's former `site/teach/` address, because a
link that has been handed to somebody should not start 404ing.
"""
from __future__ import annotations

import argparse
import ast
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_site import COPY_JS, md_to_html                      # noqa: E402
from exercises.repo import BRANCH, REPO                         # noqa: E402
from exercises import guide_a as T                              # noqa: E402
from exercises import EXERCISES                                 # noqa: E402

CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
OUT = ROOT / "site" / "guide" / "function-a.html"
# Where this page used to live. A generated stub redirects from it.
MOVED = ROOT / "site" / "teach" / "function-a.html"


# ------------------------------------------------------------------ the tree

def sessions() -> dict[str, dict]:
    return {s["id"]: s for f in CUR["functions"] for t in f["tracks"]
            for s in t["sessions"]}


def load(rel: str):
    """Import a module by path, for the skill scripts and the application.

    These are not importable packages — the skills live under `skills/<area>/`
    with no `__init__.py` anywhere — so a path import is the only route. None
    of them does work at import time; `announce_backend()` is inside `main()`.
    """
    spec = importlib.util.spec_from_file_location(Path(rel).stem, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def int_const(rel: str, name: str) -> int:
    """Read a module-level integer constant without importing the module.

    `cybertravels/a2a/protocol.py` opens with `from .. import config`, which a
    path import cannot satisfy — there is no parent package when the file is
    loaded by location. The ceiling is a literal, so parsing is both enough
    and stricter: a `MAX_HOPS` that stopped being a literal would fail here
    rather than quietly report whatever the expression evaluated to.
    """
    tree = ast.parse((ROOT / rel).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
                return node.value.value
            raise SystemExit(f"build_guide.py: {rel}:{name} is no "
                             f"longer an integer literal")
    raise SystemExit(f"build_guide.py: {rel} has no {name}")


def span_kinds() -> list[str]:
    """Every span kind the application can emit, read from the call sites.

    Counted from the calls rather than from a list in `observability.py`,
    because there is no such list: `span()` takes the kind as a string and the
    helpers below it each pass their own. A hand-maintained count would drift
    the first time a lesson added a stage, which is how "eleven span kinds"
    got written down while the tree had twelve.
    """
    seen = []
    for py in sorted((ROOT / "cybertravels").rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        for m in re.finditer(r"\.span\(\s*[\"']([a-z_]+)[\"']", py.read_text()):
            if m.group(1) not in seen:
                seen.append(m.group(1))
    return seen


READING_WPM = 180      # the rate the page states beside the figure it derives


def reading_volume() -> tuple[int, int]:
    """(words, minutes) of Function A prose, counted from the lesson sources.

    A self-study reader needs a figure the taught duration does not give them:
    "about four hours" is a facilitated session, and somebody working alone
    wants to know how much of it is reading. Commands and table rows are
    stripped, because typing a command is not reading a sentence, and the rate
    is printed next to the number so it is a derivation rather than a claim.
    """
    ids = [s for s in sessions() if s.startswith("A")]
    total = 0
    for sid in ids:
        ex = EXERCISES.get(sid) or {}
        for key in ("hook", "concept", "steps", "challenge"):
            v = ex.get(key)
            items = [v] if isinstance(v, str) else (v or [])
            for item in items:
                for part in (item if isinstance(item, (list, tuple)) else [item]):
                    if not isinstance(part, str):
                        continue
                    t = re.sub(r"```.*?```", " ", part, flags=re.S)
                    t = re.sub(r"^\s*\|.*$", " ", t, flags=re.M)
                    total += len(t.split())
    return total, round(total / READING_WPM)


def measure() -> dict[str, object]:
    """Every number the guide quotes, taken from the thing that produces it."""
    arch = load("skills/architecture/agentic-architecture-map/scripts/"
                "agentic_architecture_map.py")
    blast = load("skills/architecture/blast-radius-review/scripts/"
                 "blast_radius_review.py")
    audit = load("skills/threats/audit-answerability-check/scripts/"
                 "audit_answerability_check.py")
    score = load("skills/research/agent-eval-scoring/scripts/"
                 "agent_eval_scoring.py")
    cfg = load("cybertravels/config.py")

    comp = arch.COMPONENTS
    pol = cfg.TOOL_POLICY
    irrev = [k for k, v in blast.ACTIONS.items() if not v["reversible"]]
    extern = [k for k in irrev if blast.ACTIONS[k]["external"]]
    tca, oa = score.tool_call_accuracy(), score.output_accuracy()
    spans = span_kinds()
    words, minutes = reading_volume()

    def names(xs):
        xs = [f"`{x}`" for x in xs]
        return ", ".join(xs[:-1]) + " and " + xs[-1] if len(xs) > 1 else xs[0]

    return {
        "components": len(comp),
        "present": sum(1 for v in comp.values() if v[2]),
        "absent": names([k for k, v in comp.items() if not v[2]]),
        "tools": len(pol),
        "internal": sum(1 for v in pol.values()
                        if v["audience"] == cfg.AUD_INTERNAL_MCP),
        "vendor": sum(1 for v in pol.values()
                      if v["audience"] == cfg.AUD_VENDOR_MCP),
        "high_risk": sum(1 for v in pol.values() if v["high_risk"]),
        "high_risk_names": names([k for k, v in pol.items() if v["high_risk"]]),
        "words": f"{words:,}", "reading_minutes": minutes,
        "reading_wpm": READING_WPM,
        "max_steps": cfg.MAX_STEPS,
        "max_calls": cfg.MAX_TOOL_CALLS,
        "max_per_target": cfg.MAX_CALLS_PER_TARGET,
        "max_hops": int_const("cybertravels/a2a/protocol.py", "MAX_HOPS"),
        "a20_questions": len(audit.QUESTIONS),
        "spans": len(spans),
        "span_list": ", ".join(f"`{s}`" for s in spans),
        # Three decimal places, because that is how the skill prints them
        # (`f"{...:.3f}"`). A guide saying 0.4 beside a run saying 0.400 reads
        # as two different numbers to somebody comparing them under pressure.
        "exact": f"{tca['exact']:.3f}", "name_only": f"{tca['name_only']:.3f}",
        "order_ignored": f"{tca['order_ignored']:.3f}", "n": tca["n"],
        "accuracy": f"{oa['accuracy']:.3f}", "correct": oa["correct"],
        "incorrect": oa["incorrect"], "unscoreable": oa["unscoreable"],
        "irreversible": len(irrev), "irreversible_names": names(irrev),
        "external": len(extern), "external_names": names(extern),
        "cast": {k: v for k, v in getattr(cfg, "USERS", {}).items()},
    }


def fill(text: str, facts: dict) -> str:
    """Substitute {placeholders} from the measurements, loudly.

    `str.format` would raise KeyError with no context. A course guide that
    half-renders is worse than one that refuses to build, so the unknown name
    and the sentence it is in both go into the message.
    """
    def one(m):
        key = m.group(1)
        if key not in facts:
            raise SystemExit(
                f"build_guide.py: no measurement named {{{key}}}, in:\n"
                f"  {text[:160]}\n"
                f"  known: {', '.join(sorted(k for k in facts if k != 'cast'))}")
        return str(facts[key])
    return re.sub(r"\{([a-z_0-9]+)\}", one, text)


# ------------------------------------------------------------------- the page

HEAD = ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        '<title>{title}</title><meta name="description" content="{desc}">'
        '<link rel="icon" href="../assets/favicon.ico" sizes="16x16 32x32 48x48">'
        '<link rel="icon" type="image/png" href="../assets/favicon.png" sizes="256x256">'
        '<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700'
        '&family=IBM+Plex+Mono:wght@400;500;600'
        '&display=swap" rel="stylesheet">'
        '<link rel="stylesheet" href="../assets/lesson.css"></head><body>')

NAV = ('<header class="nav"><div class="nav-in">'
       '<a class="brand" href="../index.html"><img src="../assets/logo-mark.png" alt="Cyber Commons">'
       '<span>Cyber <b>Commons</b><small>Navigating Cyber Singularity</small></span></a>'
       '<nav class="nav-links"><a href="../lessons/index.html">All lessons</a>'
       '<a href="../index.html#curriculum">Curriculum</a>'
       f'<a href="{REPO}">GitHub</a></nav></div></header>')

FOOT = ('<footer><div class="fin"><span>Cyber Commons · Navigating Cyber Singularity</span>'
        '<span><a href="../index.html">Home</a> · '
        '<a href="../lessons/index.html">All lessons</a> · '
        f'<a href="{REPO}">Source</a></span></div></footer>'
        + COPY_JS + '</body></html>')

# Same vocabulary as a lesson page, so a trainer who has read the lessons knows
# what a colour means before reading the heading. Amber is the adversary or
# urgency and nothing else, which is why the failure table gets it and the
# glossary does not.
HUES = {
    "glance": "cyan", "outcomes": "blue", "prework": "violet",
    "framing": "violet",
    "schedule": "cyan", "labs": "green", "capstone": "blue",
    "check": "pink", "handover": "slate", "pitfalls": "amber",
    "failures": "amber", "prompts": "green", "glossary": "slate",
}


def sec(key: str, title: str, icon: str, body: str, sub: str = "") -> str:
    hue = HUES[key]
    subhtml = f'<p class="sub">{sub}</p>' if sub else ""
    return (f'<section class="ls ls-{hue}" id="{key}">'
            f'<h2 class="lsh"><span class="lsi">{icon}</span>{html.escape(title)}</h2>'
            f'<div class="lsb">{subhtml}{body}</div></section>')


def lesson_link(sid: str, ses: dict, short: bool = False) -> str:
    """A link to a lesson page. `short` gives the id alone.

    The titles here run to fourteen words, so the schedule's lesson column —
    five of them in one cell — rendered as a paragraph rather than a list. The
    title moves to the link's tooltip, and the lab block below carries it in
    full, so nothing is lost and the table is scannable.
    """
    s = ses.get(sid)
    if short:
        t = f' title="{html.escape(s["title"])}"' if s else ""
        return f'<a href="../lessons/{sid}.html"{t}>{html.escape(sid)}</a>'
    label = f"{sid} — {s['title']}" if s else sid
    return f'<a href="../lessons/{sid}.html">{html.escape(label)}</a>'


def table(headers: list[str], rows: list[list[str]]) -> str:
    """A table in the markup the mobile stacking rules are written against.

    `data-h` on every cell is required, not decorative: under 760px the CSS
    hides `thead` and stacks each row, labelling each cell from that attribute.
    A table emitted without it stacks into unlabelled values — nine cells in a
    column with nothing saying which is the risk and which the control.
    """
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for r in rows:
        tds = "".join(
            f'<td data-h="{html.escape(headers[n] if n < len(headers) else "")}">'
            f'{c}</td>' for n, c in enumerate(r))
        body.append(f"<tr>{tds}</tr>")
    return (f'<div class="tw"><table class="md"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def md(text: str) -> str:
    return md_to_html(text)


def inline(text: str) -> str:
    """Inline markdown only — for a table cell, where <p> would break the row."""
    out = md_to_html(text)
    return re.sub(r"</?p>", "", out).strip()


def glance(ses: dict, facts: dict) -> str:
    """Course at a glance: what either reader checks before committing to it."""
    ids = [sid for m in T.MODULES for sid in m[2]]
    rows = [
        ["Function", "A — Getting Started: Building Agentic AI"],
        ["Lessons", f'{len(ids)} — {lesson_link(ids[0], ses)} '
                    f'through {lesson_link(ids[-1], ses)}'],
        # The taught figure alone misleads somebody working alone, who has no
        # facilitator setting the pace. The reading half is counted from the
        # lesson prose and the rate is stated, so it is a derivation rather
        # than an estimate somebody typed.
        ["Duration", f'{html.escape(T.COURSE["duration"])} — of which about '
                     f'{facts["reading_minutes"]} minutes is reading '
                     f'({facts["words"]} words of lesson prose at '
                     f'{facts["reading_wpm"]} words a minute). On your own, '
                     f'expect longer: the labs are where the time goes'],
        ["Audience", inline(T.COURSE["audience"])],
        ["Prerequisites", inline(T.COURSE["prereq"])],
        ["On your own", inline(T.COURSE["solo"])],
        ["With a room", inline(T.COURSE["room"])],
        ["What you build",
         'The CyberTravels agentic platform — '
         f'{facts["present"]} of the {facts["components"]} agent components, '
         f'{facts["tools"]} tools behind two MCP servers, and the controls '
         'between a model\'s suggestion and a real action'],
        ["The one sentence to hold",
         f'<b>{html.escape(T.COURSE["board"])}</b>'],
    ]
    mod = table(
        ["Time", "Module", "Lessons", "You leave with"],
        [[m[0], f"<b>{html.escape(m[1])}</b>",
          " · ".join(lesson_link(x, ses, short=True) for x in m[2]) or "—",
          inline(m[3]) or "—"] for m in T.MODULES])
    short = (md("**Half the time?** " + T.COURSE["short"])
             + room("", [T.COURSE["short_room"]]))
    ways = table(
        ["Way", "What it does", "Needs a model?", "Use it for"],
        [[inline(f"**{w[0]}**"), inline(w[1]), inline(w[2]), inline(w[3])]
         for w in T.WAYS])
    return (rows_table(rows) + '<h3>The four hours</h3>' + mod + short
            + '<h3>Three ways to do any lesson</h3>'
            + '<p>Every lesson can be done three ways. Way 1 is the '
              'default; the other two matter because a machine with no model '
              'configured can still do every lesson, and because "what '
              'actually changed?" is the question that comes up most.</p>'
            + ways)


def rows_table(rows: list[list[str]]) -> str:
    """A two-column key/value table — no thead, so each row labels itself."""
    body = "".join(f'<tr><th>{html.escape(k)}</th><td>{v}</td></tr>'
                   for k, v in rows)
    return f'<div class="tw"><table class="md kv"><tbody>{body}</tbody></table></div>'


def outcomes(ses: dict) -> str:
    return table(["By the end, you can…", "Proved in", "Evidence"],
                 [[inline(o[0]),
                   " · ".join(lesson_link(x, ses, short=True) for x in o[1]),
                   inline(o[2])] for o in T.OUTCOMES])


def room(title: str, items: list[str]) -> str:
    """A block only somebody running this for other people needs.

    Rendered separately rather than mixed into the prose, because "project the
    component table" is noise to a solo reader and the page is now written for
    both. An empty list renders nothing at all.
    """
    items = [i for i in items if i]
    if not items:
        return ""
    body = ("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"
            if len(items) > 1 else md(items[0]))
    # The label is "For a room" alone unless the title adds something a
    # reader cannot see from where the block sits. A lab block's title is its
    # lesson id, which is in the heading six lines above it.
    suffix = f' · {html.escape(title)}' if title else ""
    return (f'<div class="room"><div class="rl">For a room{suffix}</div>'
            f'{body}</div>')


def prework() -> str:
    out = [md("Whoever you are, this is the part that blocks everything else: "
              "a machine that cannot run a lesson is the one failure that "
              "stops a reader entirely."),
           "<ul>"
           + "".join(f"<li>{inline(i)}</li>" for i in T.PREWORK_SOLO)
           + "</ul>"]
    for when, items in T.PREWORK_ROOM.items():
        out.append(room(when, items))
    return "".join(out)


def cast(facts: dict) -> str:
    """The three people every example uses, from config plus the teaching note."""
    rows = []
    for who, note in T.CAST_NOTE.items():
        u = facts["cast"].get(who) or {}
        role = u.get("role", "")
        rows.append([f"<b>{html.escape(who.title())}</b>",
                     f"<code>{html.escape(role)}</code>" if role else "—",
                     inline(note)])
    return table(["Who", "Role", "And so"], rows)


def labs(ses: dict, facts: dict) -> str:
    """One block per lesson: key idea, the prompt, expected output, debrief."""
    out = []
    for mod in T.MODULES:
        window, name, ids, _ = mod
        if not ids:
            continue      # Framing has its own section; a break has no lab
        out.append(f'<h3 id="m-{slug(name)}">{html.escape(window)} · '
                   f'{html.escape(name)}</h3>')
        if name in T.MODULE_INTRO:
            out.append(md(T.MODULE_INTRO[name]))
        if name == "Setup and the nine words":
            out.append(md("Paste this once at the start, so Claude knows how "
                          "to behave for the whole course:"))
            out.append(f'<pre><code class="language-text">'
                       f'{html.escape(T.OPENER_PROMPT)}</code></pre>')
        if name == "Build the agent core":
            out.append(cast(facts))
        for sid in ids:
            out.append(lab_block(sid, ses, facts))
    return "".join(out)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def lab_block(sid: str, ses: dict, facts: dict) -> str:
    lab = T.LABS[sid]
    s = ses[sid]
    # `tlab`, not `lab`: `.rc .lab` and `.video .cap .lab` are already the
    # small uppercase label in the stylesheet, and reusing the name here would
    # shrink every lab block's contents to 10px uppercase.
    p = [f'<div class="tlab" id="{sid}">',
         f'<div class="tlabh"><span class="tlabid">{html.escape(sid)}</span>',
         f'<a href="../lessons/{sid}.html">{html.escape(s["title"])}</a>',
         f'<span class="tlabmin">{lab["minutes"]} min</span></div>']

    if s.get("risk") or s.get("control"):
        p.append('<div class="rc">')
        if s.get("risk"):
            p.append('<div class="risk"><div class="lab">Risk</div>'
                     f'<p>{html.escape(s["risk"])}</p></div>')
        if s.get("control"):
            p.append('<div class="ctrl"><div class="lab">Control</div>'
                     f'<p>{html.escape(s["control"])}</p></div>')
        p.append('</div>')

    p.append('<h4>Key idea</h4>' + md(fill(lab["idea"], facts)))
    p.append('<h4>Prompt to Claude</h4>'
             f'<pre><code class="language-text">'
             f'{html.escape(fill(lab["prompt"], facts))}</code></pre>')
    p.append('<h4>Expected output</h4>'
             '<div class="expected">' + md(fill(lab["expect"], facts)) + '</div>')
    for note in lab["notes"]:
        p.append(md(fill(note, facts)))
    p.append(room("", [fill(n, facts) for n in lab["teach"]]))
    q, a = lab["debrief"]
    # "Debrief" is a trainer's word. Alone, the same question is the thing you
    # answer before moving on, which is why it is labelled for both and the
    # no-single-answer line no longer says "the discussion".
    p.append('<div class="debrief"><div class="dl">Answer this before moving '
             'on</div>'
             + md(fill(q, facts))
             + (md("**Answer.** " + fill(a, facts)) if a else
                md("*No single right answer — having one of your own is the "
                   "point.*"))
             + '</div>')
    if s.get("lab"):
        p.append(md(f"**Lab.** {s['lab']}"))
    p.append('</div>')
    return "".join(p)


def capstone(facts: dict) -> str:
    out = ["<ol>"]
    for item in T.CAPSTONE:
        out.append(f"<li>{inline(fill(item, facts))}</li>")
    out.append("</ol>")
    out.append(room("", T.CAPSTONE_ROOM))
    out.append("<h3>What a good answer to each contains</h3>")
    out.append(md("Check your own three answers against this, or mark "
                  "somebody else's. An answer that misses a name but gets the "
                  "*order* right is the better answer."))
    out.append(table(["The question", "What a good answer contains"],
                     [[f"<b>{html.escape(q)}</b>", inline(a)]
                      for q, a in T.CAPSTONE_GUIDE]))
    return "".join(out)


def quick_check() -> str:
    rows = [[f"{i}. {inline(q)}", inline(a)]
            for i, (q, a) in enumerate(T.QUICK_CHECK, 1)]
    return table(["Question", "Answer"], rows)


def handover(ses: dict) -> str:
    return table(["What you built", "Attacked in", "By"],
                 [[inline(w), lesson_link(sid, ses), inline(how)]
                  for w, sid, how in T.HANDOVER])


def roles(ses: dict) -> str:
    return ('<p>Function A is the shared floor. After it, a reader goes '
            'wherever their job is:</p><ul>'
            + "".join(f"<li>For {html.escape(who)} — {lesson_link(sid, ses)}</li>"
                      for who, sid in T.ROLE_STARTS)
            + "</ul>")


def failures() -> str:
    return table(["What you see", "Why", "Fix"],
                 [[inline(a), inline(b), inline(c)] for a, b, c in T.FAILURES])


def pitfalls() -> str:
    """Each pitfall, what to do about it, and the room-only addition if any.

    The third column is empty on half the rows and that is correct — three of
    these are the same mistake whether you are alone or facilitating, and
    inventing a trainer action for them would be padding.
    """
    return table(["Pitfall", "What to do", "If you are running it for a room"],
                 [[f"<b>{inline(a)}</b>", inline(b), inline(c) if c else "—"]
                  for a, b, c in T.PITFALLS])


def framing() -> str:
    """Module 0, which has no lesson of its own.

    A taught session gets this in the first fifteen minutes from the person at
    the front. A solo reader got nothing — the schedule listed a module with
    no lessons and no content, which reads as a gap rather than as the idea
    the other fifteen lessons hang off.
    """
    return "".join(md(x) for x in T.FRAMING)


def prompts() -> str:
    return table(["When", "Prompt"],
                 [[inline(a), f"<code>{html.escape(b)}</code>"]
                  for a, b in T.PROMPT_BANK])


def glossary() -> str:
    return table(["Term", "In one line"],
                 [[f"<b>{inline(a)}</b>", inline(b)] for a, b in T.GLOSSARY])


INDEX = [
    ("glance", "Course at a glance"),
    ("outcomes", "What you can do by the end"),
    ("prework", "Before you start"),
    ("framing", "The idea the whole course hangs off"),
    ("labs", "The four hours, lab by lab"),
    ("capstone", "Capstone, and what a good answer contains"),
    ("check", "Quick check"),
    ("handover", "What Function B does to all of this"),
    ("pitfalls", "Pitfalls, and what to do"),
    ("failures", "Setup failures, in the order they happen"),
    ("prompts", "Prompt bank"),
    ("glossary", "Glossary"),
]


def page() -> str:
    ses = sessions()
    facts = measure()
    ids = [sid for m in T.MODULES for sid in m[2]]

    toc = ('<nav class="toc" aria-label="On this page">'
           '<div class="tocl">On this page</div><ol>'
           + "".join(f'<li><a href="#{k}">{html.escape(t)}</a></li>'
                     for k, t in INDEX)
           + "</ol></nav>")

    parts = [
        HEAD.format(title="Function A Course Guide — Building Agentic AI | "
                          "Cyber Commons",
                    desc=html.escape(
                        f"Work through Function A alone or run it for a room: "
                        f"{len(ids)} lessons, the prompt and expected output "
                        f"for every lab, and what to do when a machine fails.")),
        NAV,
        '<div class="wrap"><div class="lhead">',
        '<div class="crumb"><a href="../lessons/index.html">All lessons</a> › '
        'Course guide</div>',
        '<div class="sid">COURSE GUIDE</div>',
        '<h1>Function A — Building Agentic AI with Claude</h1>',
        '<div class="badges">'
        f'<span class="badge d">{len(ids)} lessons</span>'
        f'<span class="badge t">{html.escape(T.COURSE["duration"])}</span>'
        '<span class="badge b">Self-study or taught</span></div>',
        md("**Use this on your own, or to run Function A for other people.** "
           "Everything here serves both; the shaded blocks marked *For a room* "
           "are the only parts a solo reader can skip."),
        md("Every number on this page is generated from the lesson sources and "
           "the application, so an expected output here is what the command "
           "actually prints. If a run disagrees with this page, **trust the "
           "run** and correct `scripts/exercises/guide_a.py`."),
        '</div>',
        toc,
        sec("glance", "Course at a glance", "◉", glance(ses, facts)),
        sec("outcomes", "What you can do by the end", "✓",
            outcomes(ses)),
        sec("prework", "Before you start", "◴", prework()),
        sec("framing", "The idea the whole course hangs off", "▦", framing(),
            "Fifteen minutes before the first lesson. A taught session opens "
            "with this; alone, read it and move on."),
        sec("labs", "The four hours, lab by lab", "▶", labs(ses, facts),
            "Key idea, the prompt to paste, what it prints, and the question "
            "to answer before moving on."),
        sec("capstone", "Capstone, and what a good answer contains", "✓",
            capstone(facts)),
        sec("check", "Quick check", "✎", quick_check(),
            "Eight questions. Cover the answer column, or use any three with "
            "a room."),
        sec("handover", "What Function B does to all of this", "→",
            handover(ses) + roles(ses)),
        sec("pitfalls", "Pitfalls, and what to do", "◉", pitfalls()),
        sec("failures", "Setup failures, in the order they happen", "◉",
            failures()),
        sec("prompts", "Prompt bank", "▶", prompts()),
        sec("glossary", "Glossary", "▦", glossary()),
        '<div class="pager">'
        '<a href="../lessons/A0.0.html"><div class="k">Start here</div>'
        '<div class="t">A0.0 — set up your computer</div></a>'
        '<a class="next" href="../lessons/index.html">'
        '<div class="k">All 149 lessons</div>'
        '<div class="t">The full curriculum</div></a></div>',
        '</div>',
        FOOT,
    ]
    return "".join(parts)


# ------------------------------------------------------------------ the gate

def consistency(ses: dict) -> list[str]:
    """Checks that a lesson cannot be dropped from, or lost by, this guide."""
    bad = []
    fn_a = sorted(sid for sid in ses if sid.startswith("A"))
    scheduled = [sid for m in T.MODULES for sid in m[2]]

    for sid in scheduled:
        if sid not in ses:
            bad.append(f"MODULES schedules {sid}, which the curriculum does "
                       f"not carry")
    dupes = [x for x in set(scheduled) if scheduled.count(x) > 1]
    for sid in sorted(dupes):
        bad.append(f"MODULES schedules {sid} more than once")
    for sid in fn_a:
        if sid not in scheduled:
            bad.append(f"{sid} is a Function A lesson and no module teaches it")
        if sid not in T.LABS:
            bad.append(f"{sid} has no LABS entry — no prompt, no expected output")
    for sid in T.LABS:
        if sid not in ses:
            bad.append(f"LABS has {sid}, which the curriculum does not carry")

    # Every lesson id this guide links to must exist, wherever it is named.
    # A trainer following a dead link mid-session has no way to recover.
    cited = [sid for o in T.OUTCOMES for sid in o[1]]
    cited += [sid for _, sid, _ in T.HANDOVER]
    cited += [sid for _, sid in T.ROLE_STARTS]
    for sid in cited:
        if sid not in ses:
            bad.append(f"a cited lesson id does not exist: {sid}")
    return bad


def redirect_stub() -> str:
    """The page's former address, as a generated redirect rather than a 404.

    It is generated rather than hand-written so `--check` covers it: a
    hand-written file in a directory nothing regenerates is the category of
    artefact this repository distrusts. It carries a visible link as well as
    the meta refresh, because a refresh a browser blocks must still leave
    something clickable.
    """
    url = "../guide/function-a.html"
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            f'<meta http-equiv="refresh" content="0; url={url}">'
            f'<link rel="canonical" href="{url}">'
            '<title>Moved — Function A Course Guide | Cyber Commons</title>'
            '<meta name="robots" content="noindex">'
            '<link rel="stylesheet" href="../assets/lesson.css"></head><body>'
            '<div class="wrap"><div class="lhead">'
            '<h1>This page has moved</h1>'
            '<p>The Function A trainer guide is now the '
            f'<a href="{url}">Function A course guide</a> \u2014 it serves '
            'self-study as well as taught sessions.</p>'
            '</div></div></body></html>')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="non-zero exit if a committed page has drifted")
    a = ap.parse_args()

    problems = consistency(sessions())
    for p in problems:
        print(f"::error::course guide: {p}", file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} problem(s) in scripts/exercises/guide_a.py")
        return 1

    want = {OUT: page(), MOVED: redirect_stub()}
    stale = [f for f, text in want.items()
             if (f.read_text() if f.is_file() else "") != text]

    if a.check:
        if stale:
            for f in stale:
                print(f"::error::{f.relative_to(ROOT)} is stale — run "
                      f"python3 scripts/build_guide.py", file=sys.stderr)
            return 1
        print(f"site/guide/function-a.html is current "
              f"({len(T.LABS)} labs, {len(want[OUT]):,} bytes), and so is the "
              f"redirect at its old address")
        return 0

    for f, text in want.items():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    print(f"wrote site/guide/function-a.html — {len(T.LABS)} labs, "
          f"{len(want[OUT]):,} bytes"
          + ("" if stale else " (unchanged)")
          + "\nwrote site/teach/function-a.html — redirect to its new address")
    return 0


if __name__ == "__main__":
    sys.exit(main())
