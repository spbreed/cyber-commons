#!/usr/bin/env python3
"""Generate one HTML page per lesson from the single source of truth.

Inputs (edit these — never edit the generated HTML):
  site/data/curriculum.json   structure: functions -> tracks -> sessions
  curriculum/labs.json        the runnable command block per session
  site/data/videos.json       published recordings (written by link_video.py)
  lessons/<ID>.md             OPTIONAL long-form notes for a lesson (markdown)

Output:
  site/lessons/<ID>.html      one page per session
  site/lessons/index.html     all lessons, grouped

Run:
  python3 scripts/build_site.py          # rebuild every lesson page
  python3 scripts/build_site.py --check  # verify pages are up to date (CI)

Markdown for lesson notes uses python-markdown when installed; without it a
small built-in renderer covers headings, lists, code, links, bold/italic and
blockquotes, so the build never hard-fails on a missing dependency.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
LABS = json.loads((ROOT / "curriculum" / "labs.json").read_text())["labs"]
VIDEOS = json.loads((ROOT / "site" / "data" / "videos.json").read_text()).get("videos", {})
NOTES_DIR = ROOT / "lessons"
OUT = ROOT / "site" / "lessons"
# Owner, repository, branch and the URLs built from them all live in one
# module. Links built against a branch that has no such path are the bug that
# constant exists to prevent, and scripts/check_repo_links.py enforces it.
from exercises.repo import BRANCH, RAW, REPO  # noqa: E402

# Execution evidence still gates CI — scripts/test_skills.py and
# scripts/check_determinism.py must both pass — but it is no longer printed on
# the page. A badge on every lesson saying the skill ran is a claim the reader
# cannot check and stops reading after the third time.

# Framework labels, resolved per lesson: a lesson takes its track's row from
# curriculum/frameworks.json unless it names itself in `lessons`, which
# replaces the row outright. The per-lesson direction badge that used to sit
# here went with the two-direction framing it belonged to.
FRAMEWORKS = json.loads((ROOT / "curriculum" / "frameworks.json").read_text())


def frameworks_for(sid: str, track_id: str) -> dict:
    row = FRAMEWORKS["lessons"].get(sid) or FRAMEWORKS["tracks"].get(track_id, {})
    return {k: row.get(k, []) for k in ("owasp", "atlas", "nist", "euai")}


def framework_url(kind: str, code: str) -> str:
    """Where a label points. Verified by scripts/check_framework_links.py."""
    u = FRAMEWORKS["urls"]
    if kind == "owasp":
        return (u["owasp_llm"].get(code, "") if code.startswith("LLM")
                else u["owasp_agentic"])
    if kind == "atlas":
        return u["atlas"]
    if kind == "nist":
        return u["nist"]
    if kind == "euai":
        return u["euai"].replace("{n}", code.replace("Art.", "").strip())
    return ""


def framework_chips(sid: str, track_id: str) -> str:
    """A row of labels under the lesson title, each linking to its source."""
    f = frameworks_for(sid, track_id)
    titles = FRAMEWORKS["euai_titles"]
    out = []

    def chip(kind, label, code, tip=""):
        url = framework_url(kind, code)
        t = f' title="{html.escape(tip)}"' if tip else ""
        return (f'<a class="fw" href="{html.escape(url)}"{t} '
                f'target="_blank" rel="noopener">'
                f'<i>{label}</i>{html.escape(code)}</a>')

    for code in f["owasp"]:
        out.append(chip("owasp",
                        "OWASP LLM" if code.startswith("LLM") else "OWASP Agentic",
                        code))
    for code in f["atlas"]:
        out.append(chip("atlas", "MITRE ATLAS", code))
    for code in f["nist"]:
        out.append(chip("nist", "NIST AI RMF", code))
    for code in f["euai"]:
        out.append(chip("euai", "EU AI Act", code, titles.get(code, "")))
    if not out:
        return ""
    return ('<div class="fws"><span class="fwl">Maps to</span>'
            + "".join(out) + "</div>")


# ----------------------------------------------------------------- markdown
def md_to_html(text: str) -> str:
    try:
        import markdown  # type: ignore
        return markdown.markdown(text, extensions=["fenced_code", "tables"])
    except ImportError:
        pass
    out, lines, i = [], text.splitlines(), 0
    def inline(s):
        s = html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        return s
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].startswith("```"):
                buf.append(lines[j]); j += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            i = j + 1; continue
        if m := re.match(r"^(#{1,4})\s+(.*)", ln):
            lvl = len(m.group(1)); out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        if re.match(r"^\s*\d+\.\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ol>" + "".join(items) + "</ol>"); continue
        if ln.startswith(">"):
            out.append("<blockquote>" + inline(ln.lstrip("> ")) + "</blockquote>"); i += 1; continue
        if ln.strip():
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "```", ">")) \
                    and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                para.append(lines[i]); i += 1
            out.append("<p>" + inline(" ".join(para)) + "</p>"); continue
        i += 1
    return "\n".join(out)


# ------------------------------------------------------------------ helpers
def flatten():
    """Every session in course order, with its track/function context."""
    seq = []
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            for i, s in enumerate(tr["sessions"]):
                seq.append({"s": s, "track_id": tr["id"], "track": tr["title"],
                            "fn": f"Function {fn['id']} — {fn['title']}",
                            "fn_id": fn["id"],
                            # Nothing set this, so `entry.get("last_in_track")`
                            # was None on all 148 pages and the chapter bridge
                            # has never rendered on any of them. Sixteen
                            # bridges were written, checked for existing, and
                            # shown to nobody; the gate only ever asked whether
                            # BRIDGES had a key for the track.
                            "last_in_track": i == len(tr["sessions"]) - 1})
    return seq


def exercise_link(sid: str) -> tuple[str, str]:
    """(url, label) for the skill behind a lesson.

    Resolved from the lesson's own steps, so it always points at a directory
    that exists. An earlier version guessed a lab directory out of the command
    block and pointed at `main`, which produced 404s on two counts: most of
    those directories were never created, and the content lives on a branch.
    """
    rel = "skills/" + (script_of(sid) or "").rsplit("/scripts/", 1)[0]
    return f"{REPO}/tree/{BRANCH}/{rel}", rel


# The lesson body is rendered from `scripts/exercises/` — the same sources the
# skills and the recording scripts are built from. There is one copy of the
# prose and one copy of the procedure, and neither lives on this page.
sys.path.insert(0, str(ROOT / "scripts"))
from exercises import EXERCISES                       # noqa: E402
from exercises.about import ABOUT                     # noqa: E402
from exercises.anchors import ANCHORS                 # noqa: E402
from exercises.cybertravels import GROUNDING          # noqa: E402
from exercises.days import DAYS, FUNCTION_DAYS, FUNCTION_INTRO  # noqa: E402
from exercises.framing import BRIDGES                 # noqa: E402
from exercises.layout import parts_for, runs_something  # noqa: E402
SKILLS_DIR = ROOT / "skills"

# Every section gets one colour and one icon, and they are fixed across all 134
# lessons so the shape of a page is learnable: a reader who has read two knows
# where the framework is on the third without reading a heading.
SECTIONS = {
 "relevance": ("amber",  "\u25c9", "Use case relevance"),
 "days":      ("violet", "\u25f4", "What this lesson is \u2014 Day 0, Day 1, Day 2"),
 "framework": ("cyan",   "\u25a6", "The framework, and how it works"),
 "about":     ("violet", "\u25f4", "What this lesson is"),
 "skill":     ("green",  "\u25b6", "Real time execution as skill"),
 "proved":    ("blue",   "\u2713", "What you just proved"),
 "turn":      ("pink",   "\u270e", "Your turn"),
 "bridge":    ("slate",  "\u2192", "Where this leaves you"),
}


def sec_open(key: str, extra: str = "") -> str:
    hue, icon, title = SECTIONS[key]
    return (f'<section class="ls ls-{hue}">'
            f'<h2 class="lsh"><span class="lsi">{icon}</span>'
            f'{html.escape(title)}{extra}</h2>'
            f'<div class="lsb">')


def skill_html(ref: str) -> str:
    """The SKILL.md as prose, with its frontmatter kept as the block an agent parses."""
    path = SKILLS_DIR / ref / "SKILL.md"
    if not path.is_file():
        raise SystemExit(f"build_site.py: no such skill: skills/{ref}/SKILL.md")
    _, front, body = path.read_text().split("---", 2)
    link = f"{REPO}/blob/{BRANCH}/skills/{ref}/SKILL.md"
    return (f'<p class="skillref">The skill — '
            f'<a href="{link}" target="_blank" rel="noopener">'
            f'<code>skills/{html.escape(ref)}/SKILL.md</code></a></p>'
            f'<pre class="front"><code>{html.escape(front.strip())}</code></pre>'
            + md_to_html(body.strip()))


def steps_html(sid: str, ex: dict) -> tuple[str, str]:
    """(the prose steps, the skill procedure) — the code steps are not rendered.

    A lesson's steps interleave explanation with the thing that runs. On the
    page the explanation belongs under the framework and the procedure under
    execution, so they are split here rather than replayed in source order.
    """
    prose, skill = [], []
    for kind, source in ex.get("steps", []):
        if kind == "skill":
            skill.append(skill_html(source))
        elif kind == "md" and isinstance(source, str):
            prose.append(md_to_html(source.replace("\\n", "\n")))
        elif kind == "html":
            prose.append(source)
    return "".join(prose), "".join(skill)


def lesson_body(entry: dict) -> str:
    """The whole lesson, from source, in whichever sections it has earned.

    Which sections those are is declared in scripts/exercises/layout.py rather
    than assumed here; see that module for why a page carrying a Risk panel
    about the reader leaving is worse than a page carrying no Risk panel.
    """
    sid = entry["s"]["id"]
    ex = EXERCISES.get(sid)
    if ex is None:
        raise SystemExit(f"build_site.py: no exercise for {sid}")
    parts = page_parts(entry)
    out = []

    # 1 — why this matters, as a scene in the running system
    if "relevance" in parts:
        out.append(sec_open("relevance"))
        out.append(f"<p class=\"lead\">{html.escape(ex['hook'].strip())}</p>")
        if ground := GROUNDING.get(sid):
            out.append(f'<div class="ct"><b>At CyberTravels.</b> '
                       f'{html.escape(ground.strip())}</div>')
        out.append("</div></section>")
    else:
        # The hook is still the best paragraph on the page. It is just not a
        # use case, and a setup lesson has no CyberTravels scene to tie it to,
        # so it leads without a heading promising something it is not.
        out.append(f'<p class="lead solo">{html.escape(ex["hook"].strip())}</p>')

    # 2 — what it is and what it is worth, in one block rather than two
    # Without the Day table the description still answers the question a
    # reader arrived with, so it keeps a section, under a heading that
    # promises only what is underneath it rather than three days that were
    # never there.
    about = (ABOUT.get(sid) or "").strip()
    if not ("days" in parts or about):
        day = None
    else:
        out.append(sec_open("days" if "days" in parts else "about"))
        if about:
            out.append(md_to_html(about))
        day = DAYS.get(sid) if "days" in parts else None
    if day:
        d0, d1, d2 = day
        out.append('<div class="days">')
        for cls, lab, txt in (("d0", "Day 0 \u2014 why", d0),
                              ("d1", "Day 1 \u2014 how", d1),
                              ("d2", "Day 2 \u2014 measure", d2)):
            out.append(f'<div class="{cls}"><span>{lab}</span>'
                       f'<p>{html.escape(txt.strip())}</p></div>')
        out.append("</div>")
    if "days" in parts or about:
        fn_id = entry["fn"].split()[1] if entry["fn"].startswith("Function ") else ""
        if FUNCTION_INTRO.get(fn_id) == sid and (fd := FUNCTION_DAYS.get(fn_id)):
            out.append(f'<div class="fnday"><b>Who this function is for.</b> '
                       f'{html.escape(fd["who"].strip())}</div>')
        out.append("</div></section>")

    # 3 — the picture, the idea it names, and how the thing actually works
    prose, skill = steps_html(sid, ex)
    out.append(sec_open("framework"))
    out.append(f'<pre class="dia">{html.escape(ex["diagram"].strip(chr(10)))}</pre>')
    out.append(md_to_html(ex["concept"].strip()))
    if anchor := ANCHORS.get(sid):
        out.append(f'<blockquote class="anchor">{html.escape(anchor.strip())}'
                   f'</blockquote>')
    if prose:
        out.append(f'<div class="how">{prose}</div>')
    out.append("</div></section>")

    # 4 — the procedure, and how to run it on your own machine
    #
    # The run block now appears on EVERY lesson, including the three that run
    # no skill, because it also carries the checkpoint — and a reader landing
    # on a reading lesson needs the tree as it stood there just as much. It
    # used to be gated on has_code(), which meant the introductions to three
    # functions offered no way to get the system those functions are about.
    out.append(sec_open("skill"))
    if skill:
        out.append(f'<div class="skillmd">{skill}</div>')
    out.append(run_block(sid))
    out.append("</div></section>")

    # 5, 6, 7 — the result, the exercise, and the gap into the next chapter
    if "proved" in parts and (expect := ex.get("expect")):
        out.append(sec_open("proved") + md_to_html(expect.strip()) + "</div></section>")
    if "turn" in parts and (challenge := ex.get("challenge")):
        out.append(sec_open("turn") + md_to_html(challenge.strip()) + "</div></section>")
    if "bridge" in parts and (b := BRIDGES.get(entry["track_id"])):
        out.append(sec_open("bridge")
                   + f"<p><b>What you can do now.</b> {html.escape(b['gained'])}</p>"
                   + f"<p><b>What you still cannot do.</b> {html.escape(b['gap'])}</p>"
                   + f"<p class=\"nextch\">{html.escape(b['next'])}</p>"
                   + "</div></section>")
    return "".join(out)


DIAGRAM_MARK = re.compile(r"^\[diagram:(dot|puml):([a-z0-9-]+)\]$", re.M)
DIAGRAMS_DIR = ROOT / "site" / "assets" / "diagrams"


FALLBACK_SCRIPT = "the skill\u2019s script"


def script_of(sid: str) -> str | None:
    """The skill script this lesson runs, as `<area>/<name>/scripts/<file>.py`.

    Read from the lesson's own steps. It used to be parsed back out of the
    built notebook, which meant the page could only name a script after a
    build had produced one; the sources are the answer and always were.
    """
    for kind, value in EXERCISES.get(sid, {}).get("steps", []):
        if kind == "skill_script" and isinstance(value, str):
            return value
    return None



def has_code(sid: str) -> bool:
    """Does this lesson actually have something to run?

    Several lessons — the function introductions, the architecture map — are
    diagrams and prose end to end. Offering a run command on those sends the
    reader to something with nothing in it to execute, which teaches them the
    instruction is decorative everywhere else too.

    Defined in exercises/layout.py, because the same answer also decides
    whether the page carries a "What you just proved" section, and the gate
    that checks that has to read it from the same place.
    """
    return runs_something(sid)


def page_parts(entry: dict) -> frozenset[str]:
    """Which parts of the template this lesson renders.

    One call site for the whole build, and check_lessons.py calls the same
    function on the same inputs, so the gate and the page cannot disagree
    about what a lesson is supposed to carry.
    """
    s = entry["s"]
    return parts_for(s["id"], s.get("kind"), entry["track_id"],
                     runs=has_code(s["id"]),
                     last_in_track=bool(entry.get("last_in_track")))


def run_block(sid: str) -> str:
    """How to run this lesson's skill, on the reader's own machine.

    Two routes, because they are genuinely different things. Installing the
    skill into an agent is what the agentskills.io format is *for* — the agent
    reads the SKILL.md and carries out the procedure itself. Running the script
    is for when you want the same committed fixture every time, so two runs are
    comparable. Both appear, in that order, because the first is the one a
    reader will actually use and the second is the one a reviewer needs.
    """
    script = script_of(sid)
    # The checkpoint comes first and is offered on every lesson, including the
    # three that run no skill. A reader who lands here needs CyberTravels as it
    # stood at this lesson before anything else makes sense — the finished tree
    # contains every control the lessons after this one exist to build, and
    # handing it over spoils all of them.
    checkpoint = (
        '<p><b>Get your copy of CyberTravels as it stood here.</b> Everything '
        'taught up to this lesson, and nothing taught after it — so the '
        'exercises ahead of you still work.</p>'
        f'<pre><code>python3 scripts/checkpoint.py --at {html.escape(sid)} '
        f'--out work/cybertravels\n'
        f'python3 scripts/checkpoint.py --at {html.escape(sid)} --diff'
        f'   # what this lesson changed</code></pre>')
    if not script:
        return ('<div class="runbox">' + checkpoint +
                '<p class="runnote">This is a reading lesson — there is no '
                'skill to run. The checkpoint is still worth taking, because '
                'the next lesson that does run one starts from it.</p></div>')
    name = script.split("/")[1]
    return (
        '<div class="runbox">' + checkpoint +
        '<p><b>Run it in your agent.</b> Link the skills store into whichever '
        'CLI you use — Claude Code, Codex, Gemini and the rest read the same '
        'format — then ask for the task in your own words.</p>'
        '<pre><code>python3 scripts/install_skills.py --all\n'
        f'# then, in your agent: ask for "{html.escape(name.replace("-", " "))}"'
        '</code></pre>'
        '<p><b>Or run the harness directly</b>, against the fixture committed '
        'with the skill, so two runs are comparable:</p>'
        f'<pre><code>python3 skills/{html.escape(script)}</code></pre>'
        '<p class="runnote">Both need a model. A signed-in Claude Code CLI '
        'needs no API key; any OpenAI-compatible endpoint works too. With '
        'neither, the skill exits 2 and says so rather than inventing an '
        'answer. <a href="A0.0.html">A0.0</a> sets this up.</p>'
        '</div>')


def video_block(sid: str, title: str) -> str:
    v = VIDEOS.get(sid)
    if v and (v.get("youtube_id") or v.get("url")):
        yid = v.get("youtube_id")
        inner = (f'<iframe src="https://www.youtube-nocookie.com/embed/{html.escape(yid)}" '
                 f'title="{html.escape(title)}" loading="lazy" allowfullscreen '
                 f'allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture"></iframe>'
                 ) if yid else (
                 f'<div class="ph"><div class="icon">▶</div>'
                 f'<p><a href="{html.escape(v["url"])}">Watch the recording</a></p></div>')
        link = v.get("url") or f"https://www.youtube.com/watch?v={yid}"
        cap = (f'<span>Lightboard recording{" · " + html.escape(v["duration"]) if v.get("duration") else ""}</span>'
               f'<a href="{html.escape(link)}" target="_blank" rel="noopener">Open on YouTube ↗</a>')
        return f'<div class="video"><div class="frame">{inner}</div><div class="cap">{cap}</div></div>'
    # placeholder — the lesson is written, the recording is not made yet
    return ('<div class="video empty"><div class="frame"><div class="ph">'
            '<div class="icon">▶</div>'
            '<div class="lab">Lightboard recording</div>'
            '<p>Not recorded yet. The lesson below is complete and runnable today — '
            'the video is added later without touching this page.</p>'
            '</div></div><div class="cap"><span>Video placeholder</span>'
            f'<span>publishes automatically from <code>recordings/{html.escape(sid)}.mp4</code></span>'
            '</div></div>')


NAV = ('<header class="nav"><div class="nav-in">'
       '<a class="brand" href="../index.html"><img src="../assets/logo-mark.png" alt="Cyber Commons">'
       '<span>Cyber <b>Commons</b><small>Navigating Cyber Singularity</small></span></a>'
       '<nav class="nav-links"><a href="index.html">All lessons</a>'
       '<a href="../index.html#curriculum">Curriculum</a>'
       f'<a href="{REPO}">GitHub</a></nav></div></header>')

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

FOOT = ('<footer><div class="fin"><span>Cyber Commons · Navigating Cyber Singularity</span>'
        f'<span><a href="../index.html">Home</a> · <a href="index.html">All lessons</a> · '
        f'<a href="{REPO}">Source</a></span></div></footer></body></html>')


def lesson_page(entry, prev, nxt) -> str:
    s, sid = entry["s"], entry["s"]["id"]
    lab = LABS.get(sid, {})
    ex_url, ex_label = exercise_link(sid)
    title = f"{sid} — {s['title']} | Cyber Commons"

    parts = [HEAD.format(title=html.escape(title),
                         desc=html.escape((s.get("control") or s.get("risk") or "")[:180])), NAV]
    parts.append('<div class="wrap"><div class="lhead">')
    parts.append(f'<div class="crumb"><a href="index.html">All lessons</a> › '
                 f'{html.escape(entry["fn"])} › {html.escape(entry["track"])}</div>')
    parts.append(f'<div class="sid">{html.escape(sid)}</div>')
    parts.append(f'<h1>{html.escape(s["title"])}</h1>')
    badges = []
    if s.get("featured"):
        badges.append('<span class="badge s">Flagship lab</span>')
    badges.append(f'<span class="badge t">{html.escape(entry["track_id"])}</span>')
    parts.append('<div class="badges">' + "".join(badges) + '</div>')
    parts.append(framework_chips(sid, entry["track_id"]) + '</div>')

    parts.append(video_block(sid, f"{sid} — {s['title']}"))

    # The Risk and Control panel, only where the lesson has a risk to a system
    # and a control that closes it. A setup lesson does not: its "risk" was
    # that a reader might leave, which is a risk to the commons rather than to
    # anything anybody secures. scripts/exercises/layout.py holds the decision.
    if "riskcontrol" in page_parts(entry) and (s.get("risk") or s.get("control")):
        parts.append('<div class="rc">')
        if s.get("risk"):
            parts.append(f'<div class="risk"><div class="lab">Risk</div><p>{html.escape(s["risk"])}</p></div>')
        if s.get("control"):
            parts.append(f'<div class="ctrl"><div class="lab">Control</div><p>{html.escape(s["control"])}</p></div>')
        parts.append('</div>')

    parts.append('<div class="sec"><h2>The lab</h2>')
    # From the session, never from labs.json: the two used to hold separate
    # copies of the same sentence and six of them had drifted onto other
    # lessons entirely.
    if s.get("lab"):
        parts.append(f'<p class="sub">{html.escape(s["lab"])}</p>')

    # One button, and only on a lesson that has something to run — a reading
    # lesson gets none, because there is nothing on the other end of it.
    if has_code(sid):
        skill_dir = (script_of(sid) or "").rsplit("/scripts/", 1)[0]
        parts.append('<div class="cta-row">'
                     f'<a class="btn k" href="{REPO}/tree/{BRANCH}/skills/'
                     f'{html.escape(skill_dir)}" target="_blank" rel="noopener">'
                     f'↗ Open this skill in the repository</a>'
                     '</div>')
        # Collapsed by default. It is prerequisite detail — the same few
        # sentences on every page — and a reader who has run one lesson never
        # needs it again, so it should not sit above the lesson every time.
        # <details> needs no JavaScript and stays keyboard-accessible.
        parts.append('<details class="runnote"><summary>What running a lesson '
                     'needs</summary>'
                     '<div class="runbody"><p>Every skill here is carried out by '
                     'a <b>model</b>; the script is the harness. Link the skills '
                     'store into your agent with '
                     '<code>python3 scripts/install_skills.py --all</code> and ask '
                     'for the task in your own words, or run '
                     f'<code>python3 skills/{html.escape(script_of(sid) or FALLBACK_SCRIPT)}</code> '
                     'against the fixture committed with the skill.</p>'
                     '<p>A signed-in Claude Code CLI needs <b>no API key</b>; any '
                     'OpenAI-compatible endpoint works too. With neither, the '
                     'skill exits 2 and says so rather than inventing an answer. '
                     '<a href="A0.0.html">A0.0</a> sets it up, and '
                     '<a href="A0.1.html">A0.1</a> explains how a lesson is '
                     'built.</p></div></details>')
    else:
        parts.append('<p class="sub runnote">This lesson is a reading lesson — '
                     'diagrams and prose, no code to run.</p>')

    parts.append(lesson_body(entry))

    if lab.get("expect"):
        parts.append(f'<div class="expect"><b>Expect</b>{html.escape(lab["expect"])}</div>')

    # One list — packages and models together, in the order they appear in the
    # lesson. The reader wants to know what is in front of them, not which
    # procurement category each item belongs to.
    used = list(dict.fromkeys([*s.get("tools", []), *s.get("open_weight", []),
                               *s.get("frontier", [])]))
    if used:
        chips = "".join(f'<span>{html.escape(t)}</span>' for t in used)
        parts.append(f'<p class="sub toolslab">Tools used</p>'
                     f'<div class="chips">{chips}</div>')

    parts.append(f'<p class="sub" style="margin-top:10px">Skill source: '
                 f'<code>{html.escape(ex_label)}</code></p>'
                 '</div>')

    note = NOTES_DIR / f"{sid}.md"
    if note.exists():
        body = note.read_text()
        body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.DOTALL)  # strip front-matter
        parts.append(f'<div class="notes">{md_to_html(body)}</div>')

    parts.append('<div class="pager">')
    if prev:
        parts.append(f'<a href="{prev["s"]["id"]}.html"><span class="k">← Previous</span>'
                     f'<span class="t">{html.escape(prev["s"]["id"])} · {html.escape(prev["s"]["title"])}</span></a>')
    else:
        parts.append('<span></span>')
    if nxt:
        parts.append(f'<a class="next" href="{nxt["s"]["id"]}.html"><span class="k">Next →</span>'
                     f'<span class="t">{html.escape(nxt["s"]["id"])} · {html.escape(nxt["s"]["title"])}</span></a>')
    parts.append('</div></div>')
    parts.append(FOOT)
    return "".join(parts)


def index_page(seq) -> str:
    done = sum(1 for e in seq if e["s"]["id"] in VIDEOS)
    parts = [HEAD.format(title="All lessons | Cyber Commons",
                         desc="Every Cyber Commons lesson: risk, control, runnable lab and recording."), NAV]
    parts.append('<div class="wrap"><div class="lhead">'
                 '<div class="sid">Curriculum</div><h1>All lessons</h1>'
                 f'<div class="badges"><span class="badge b">{len(seq)} lessons</span>'
                 f'<span class="badge d">{done} recorded</span></div></div>')
    cur_fn = None
    for e in seq:
        if e["fn"] != cur_fn:
            cur_fn = e["fn"]
            parts.append(f'<div class="sec"><h2>{html.escape(cur_fn)}</h2>')
        sid = e["s"]["id"]
        mark = "▶" if sid in VIDEOS else "·"
        parts.append(f'<p style="margin:6px 0"><a href="{sid}.html" style="text-decoration:none">'
                     f'<span class="sid">{mark} {html.escape(sid)}</span> '
                     f'<span style="color:var(--text)">{html.escape(e["s"]["title"])}</span></a> '
                     f'<span style="color:var(--text-faint);font-size:13px">— {html.escape(e["track"])}</span></p>')
    parts.append('</div></div>')
    parts.append(FOOT)
    return "".join(parts)


# ----------------------------------------------------------------- homepage
# site/index.html is hand-written prose, and two things in it are not prose:
# the chapter grid and every count in the copy. Both were typed by hand and
# both had drifted — the page advertised 118 lessons for two chapters longer
# than that was true. So the numbers come from the same source of truth the
# lesson pages do, and `--check` fails when the committed page disagrees.
HOME = ROOT / "site" / "index.html"
CUR_BEGIN = "<!-- CURRICULUM:BEGIN — generated by scripts/build_site.py, do not hand-edit -->"
CUR_END = "<!-- CURRICULUM:END -->"
DAY_BEGIN = "<!-- DAYS:BEGIN — generated by scripts/build_site.py, do not hand-edit -->"
DAY_END = "<!-- DAYS:END -->"


def home_numbers() -> dict[str, int]:
    """Every count the homepage is allowed to state, measured not typed."""
    return {
        "sessions": sum(len(t["sessions"]) for f in CUR["functions"] for t in f["tracks"]),
        "chapters": sum(len(f["tracks"]) for f in CUR["functions"]),
        "functions": len(CUR["functions"]),
        "skills": len(list((ROOT / "skills").rglob("SKILL.md"))),
        # Measured from the lesson sources — the steps that actually execute —
        # which is where the answer lives now that there are no notebooks.
        "run_a_skill": sum(1 for f in CUR["functions"] for t in f["tracks"]
                           for s in t["sessions"] if has_code(s["id"])),
    }


# The homepage names the six functions in the language a reader arrives with,
# which is not the language the curriculum stores. curriculum.json's titles are
# the id every lesson page's breadcrumb and every cross-reference is built
# from, so renaming them there for a copy change would ripple through the whole
# tree. The mapping lives here instead, and a function missing from it fails
# the build rather than quietly falling back to the stored title.
TRACKS = {
    "A": ("Build an agentic system",
          "Set your machine up, then build CyberTravels end to end — the loop, "
          "MCP tools, identity and delegation, memory, agent-to-agent, spans "
          "and an audit trail — before any of it is called a risk."),
    "B": ("Agent architecture &amp; risks",
          "One reference architecture for agentic systems, and every risk that "
          "attaches to a component of it."),
    "C": ("AI SDLC &amp; harness",
          "An AppSec pipeline that runs before and after deploy, and the harness "
          "that measures whether it works."),
    "D": ("AI red teaming",
          "One authorised, scoped offensive lifecycle against your own estate — "
          "from ingestion and elicitation to containment, forensics and "
          "governance."),
    "E": ("Agentic SOC",
          "Detection and response when the analyst is directing agents rather "
          "than reading alerts one at a time."),
    "F": ("AI GRC",
          "Risk, control, regulatory mapping and the CISO office, for systems "
          "that take actions on their own."),
}


def days_block() -> str:
    """The Day 0/1/2 legend, once — not repeated per track.

    An earlier version printed all three days for all six functions on the
    homepage, which was the same 1,500 words the function introductions already
    carry. The homepage's job is to say what the three words mean; the detail
    belongs on the page that uses it.
    """
    legend = [
        ("d0", "Day 0 · why",
         "What goes wrong if you do nothing, and why this is worth an "
         "afternoon."),
        ("d1", "Day 1 · how",
         "The concrete thing you stand up — a control, a pipeline stage, a "
         "detection."),
        ("d2", "Day 2 · measure",
         "The number that says it worked, and keeps saying so afterwards."),
    ]
    out = ['<div class="daylegend rv">']
    for cls, tag, text in legend:
        out.append(f'<div><span class="dtag {cls}">{tag}</span>'
                   f'<p>{html.escape(text)}</p></div>')
    out.append("</div>")
    return "\n".join(out)


# The introduction chapter is not part of any function's argument — it is about
# the commons itself — so the homepage's track cards exclude it from their links
# and their counts. Naming the track here rather than inferring it means a
# renumber that moves the introduction fails the build loudly.
INTRO_TRACK = "A0"


def curriculum_block() -> str:
    """Five track cards, one per function, linking to that track's first lesson."""
    from exercises.days import FUNCTION_DAYS
    missing = [f["id"] for f in CUR["functions"] if f["id"] not in TRACKS]
    if missing:
        raise SystemExit(f"scripts/build_site.py: no homepage name for function(s) "
                         f"{missing} — add them to TRACKS")
    out = ['<div class="tracks rv">']
    for i, fn in enumerate(CUR["functions"], 1):
        name, blurb = TRACKS[fn["id"]]
        body = [t for t in fn["tracks"] if t["id"] != INTRO_TRACK]
        if not body:
            raise SystemExit(f"scripts/build_site.py: function {fn['id']} is only "
                             f"the introduction chapter")
        first = body[0]["sessions"][0]["id"]
        n = sum(len(t["sessions"]) for t in body)
        who = FUNCTION_DAYS[fn["id"]]["who_short"]
        out.append(f'<a class="trk" href="lessons/{first}.html">'
                   f'<div class="k">{i:02d}</div>'
                   f'<h3>{name}</h3><p>{blurb}</p>'
                   f'<p class="for">{html.escape(who)}</p>'
                   f'<div class="n">{n} lessons</div></a>')
    out.append("</div>")
    return "\n".join(out)


def homepage(src: str) -> str:
    n = home_numbers()
    if CUR_BEGIN not in src or CUR_END not in src:
        raise SystemExit("site/index.html has lost its CURRICULUM markers")
    head, rest = src.split(CUR_BEGIN, 1)
    _, tail = rest.split(CUR_END, 1)
    src = f"{head}{CUR_BEGIN}\n{curriculum_block()}\n{CUR_END}{tail}"

    if DAY_BEGIN not in src or DAY_END not in src:
        raise SystemExit("site/index.html has lost its DAYS markers")
    head, rest = src.split(DAY_BEGIN, 1)
    _, tail = rest.split(DAY_END, 1)
    src = f"{head}{DAY_BEGIN}\n{days_block()}\n{DAY_END}{tail}"

    def fill(m):
        key = m.group(2)
        if key not in n:
            raise SystemExit(f'site/index.html has data-n="{key}", which is not a '
                             f'measured fact ({", ".join(sorted(n))})')
        return f"{m.group(1)}{n[key]}{m.group(3)}"

    return re.sub(r'(<span data-n="(\w+)">)[^<]*(</span>)', fill, src)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if generated pages differ (CI)")
    a = ap.parse_args()

    seq = flatten()

    # Link integrity. Every "Open this skill" button points at a directory
    # inside this repository, so a 404 is detectable here rather than by a
    # reader. This is the check that was missing when those links shipped
    # broken.
    broken = [e["s"]["id"] for e in seq
              if has_code(e["s"]["id"])
              and not (ROOT / "skills" /
                       (script_of(e["s"]["id"]) or "x").rsplit("/scripts/", 1)[0]
                       ).is_dir()]
    if broken:
        print(f"::error::{len(broken)} lesson(s) link to a skill directory that "
              f"does not exist: {broken[:8]}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    pages = {f"{e['s']['id']}.html": lesson_page(e, seq[i - 1] if i else None,
                                                 seq[i + 1] if i + 1 < len(seq) else None)
             for i, e in enumerate(seq)}
    pages["index.html"] = index_page(seq)

    stale = []
    for name, content in pages.items():
        f = OUT / name
        if not f.exists() or f.read_text() != content:
            stale.append(name)
            if not a.check:
                f.write_text(content)
    for f in OUT.glob("*.html"):            # drop pages for removed sessions
        if f.name not in pages:
            stale.append(f"{f.name} (removed)")
            if not a.check:
                f.unlink()

    home_src = HOME.read_text()
    home_new = homepage(home_src)
    if home_new != home_src:
        stale.append("../index.html")
        if not a.check:
            HOME.write_text(home_new)

    if a.check:
        if stale:
            print(f"::error::site is out of date ({len(stale)}): {stale[:5]}"
                  f"{'…' if len(stale) > 5 else ''}\nRun: python3 scripts/build_site.py")
            return 1
        print(f"ok: {len(pages)} lesson pages and the homepage are up to date")
        return 0

    notes = len([f for f in NOTES_DIR.glob("*.md") if f.stem != "README"]) if NOTES_DIR.exists() else 0
    print(f"wrote {len(pages)} pages to site/lessons "
          f"({len(seq)} lessons · {len(VIDEOS)} with video · {notes} with authored notes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
