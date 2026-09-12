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
NB_DIR = ROOT / "labs" / "notebooks"
OUT = ROOT / "site" / "lessons"
REPO = "https://github.com/spbreed/cyber-commons"
# The branch the content actually lives on. Links built against a branch that
# has no such path are the bug this constant exists to prevent — CI checks it.
BRANCH = "claude/vulnbench-setup-scheduling-81aqov"
RAW = f"https://raw.githubusercontent.com/spbreed/cyber-commons/{BRANCH}"

# Execution evidence still gates CI — scripts/run_notebooks.py and
# scripts/kaggle_verify.py must both pass — but it is no longer printed on the
# page. A badge on every lesson saying the notebook ran is a claim the reader
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
            for s in tr["sessions"]:
                seq.append({"s": s, "track_id": tr["id"], "track": tr["title"],
                            "fn": f"Function {fn['id']} — {fn['title']}", "fn_id": fn["id"]})
    return seq


def exercise_link(sid: str) -> tuple[str, str]:
    """(url, label) for the exercise behind a lesson.

    Every session has a notebook — `build_notebooks.py` fails the build if one
    is missing — so this always resolves to a path that exists. The previous
    version guessed a lab directory out of the command block and pointed at
    `main`, which produced 404s on two counts: most of those directories were
    never created, and the content lives on a branch.
    """
    rel = f"labs/notebooks/{sid}.ipynb"
    return f"{REPO}/blob/{BRANCH}/{rel}", rel


def kaggle_url(sid: str) -> str:
    """Kaggle's import-from-URL entry point.

    Opening this signs the reader into their own Kaggle account and creates a
    new kernel in it from the raw notebook — so the exercise lands in *their*
    workspace, not ours. The notebook's own bootstrap cell then clones the
    repository for the lab library.
    """
    return f"https://www.kaggle.com/kernels/welcome?src={RAW}/labs/notebooks/{sid}.ipynb"


# The lesson body is rendered from the same sources the notebook is built from,
# never from the notebook itself. The notebook now carries code and nothing
# else — the prose lived in both places and the copy inside the notebook was
# the one nobody could correct.
sys.path.insert(0, str(ROOT / "scripts"))
from exercises import EXERCISES                       # noqa: E402
from exercises.about import ABOUT                     # noqa: E402
from exercises.anchors import ANCHORS                 # noqa: E402
from exercises.cybertravels import GROUNDING          # noqa: E402
from exercises.days import DAYS, FUNCTION_DAYS, FUNCTION_INTRO  # noqa: E402
from exercises.framing import BRIDGES                 # noqa: E402
SKILLS_DIR = ROOT / "skills"

# Every section gets one colour and one icon, and they are fixed across all 134
# lessons so the shape of a page is learnable: a reader who has read two knows
# where the framework is on the third without reading a heading.
SECTIONS = {
 "relevance": ("amber",  "\u25c9", "Use case relevance"),
 "days":      ("violet", "\u25f4", "What this lesson is \u2014 Day 0, Day 1, Day 2"),
 "framework": ("cyan",   "\u25a6", "The framework, and how it works"),
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


KAGGLE_OWNER = "cybercommons"

# Which kernels a visitor can actually see. Written by
# scripts/check_kaggle_public.py; missing or empty means embed nothing, which
# is the safe direction — a private kernel renders as a blank frame, not an
# error, so an unconditional embed fails silently on every page.
_KP = NB_DIR / "_kaggle_public.json"
KAGGLE_PUBLIC = set(
    json.loads(_KP.read_text()).get("public", []) if _KP.is_file() else [])


def kaggle_slug(sid: str) -> str:
    """The kernel slug scripts/kaggle_push.py creates for a session."""
    return f"cyber-commons-{sid.lower().replace('.', '-')}"


def kaggle_embed(sid: str) -> str:
    """The live Kaggle kernel for a lesson, as Kaggle's own embedded viewer."""
    slug = kaggle_slug(sid)
    return (
        f'<div class="kembed">'
        f'<div class="kbar"><span class="kdot"></span>'
        f'<span>Live Kaggle notebook — {html.escape(sid)}</span>'
        f'<a href="https://www.kaggle.com/code/{KAGGLE_OWNER}/{slug}" '
        f'target="_blank" rel="noopener">open on Kaggle ↗</a></div>'
        f'<iframe src="https://www.kaggle.com/embed/{KAGGLE_OWNER}/{slug}" '
        f'title="Kaggle notebook {html.escape(sid)}" loading="lazy" '
        f'frameborder="0" scrolling="auto"></iframe></div>')


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
    execution, so they are split here rather than replayed in notebook order.
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
    """The whole lesson, in its seven fixed sections, from source."""
    sid = entry["s"]["id"]
    ex = EXERCISES.get(sid)
    if ex is None:
        raise SystemExit(f"build_site.py: no exercise for {sid}")
    out = []

    # 1 — why this matters, as a scene in the running system
    out.append(sec_open("relevance"))
    out.append(f"<p class=\"lead\">{html.escape(ex['hook'].strip())}</p>")
    if ground := GROUNDING.get(sid):
        out.append(f'<div class="ct"><b>At CyberTravels.</b> '
                   f'{html.escape(ground.strip())}</div>')
    out.append("</div></section>")

    # 2 — what it is and what it is worth, in one block rather than two
    day = DAYS.get(sid)
    out.append(sec_open("days"))
    if about := ABOUT.get(sid):
        out.append(md_to_html(about.strip()))
    if day:
        d0, d1, d2 = day
        out.append('<div class="days">')
        for cls, lab, txt in (("d0", "Day 0 \u2014 why", d0),
                              ("d1", "Day 1 \u2014 how", d1),
                              ("d2", "Day 2 \u2014 measure", d2)):
            out.append(f'<div class="{cls}"><span>{lab}</span>'
                       f'<p>{html.escape(txt.strip())}</p></div>')
        out.append("</div>")
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

    # 4 — the procedure, and the kernel that runs it
    has_code = bool(NB_DIR.joinpath(f"{sid}.ipynb").is_file() and any(
        c["cell_type"] == "code"
        for c in json.loads((NB_DIR / f"{sid}.ipynb").read_text())["cells"]))
    if skill or has_code:
        out.append(sec_open("skill"))
        if skill:
            out.append(f'<div class="skillmd">{skill}</div>')
        if has_code:
            if sid in KAGGLE_PUBLIC:
                out.append(kaggle_embed(sid))
                out.append('<details class="recorded"><summary>The recorded run, '
                           'checked byte for byte against the Kaggle kernel above'
                           '</summary>' + output_block(sid) + "</details>")
            else:
                out.append(output_block(sid))
        out.append("</div></section>")

    # 5, 6, 7 — the result, the exercise, and the gap into the next chapter
    if has_code and (expect := ex.get("expect")):
        out.append(sec_open("proved") + md_to_html(expect.strip()) + "</div></section>")
    if challenge := ex.get("challenge"):
        out.append(sec_open("turn") + md_to_html(challenge.strip()) + "</div></section>")
    if entry.get("last_in_track") and (b := BRIDGES.get(entry["track_id"])):
        out.append(sec_open("bridge")
                   + f"<p><b>What you can do now.</b> {html.escape(b['gained'])}</p>"
                   + f"<p><b>What you still cannot do.</b> {html.escape(b['gap'])}</p>"
                   + f"<p class=\"nextch\">{html.escape(b['next'])}</p>"
                   + "</div></section>")
    return "".join(out)


DIAGRAM_MARK = re.compile(r"^\[diagram:(dot|puml):([a-z0-9-]+)\]$", re.M)
DIAGRAMS_DIR = ROOT / "site" / "assets" / "diagrams"


def output_block(sid: str) -> str:
    """The recorded stdout, with any emitted diagram source shown as the picture.

    A skill that emits a graph prints DOT or PlantUML, because source is text
    and the notebook has to stay standard-library-only. On the page that source
    is forty lines of coordinates nobody reads, and the rendered SVG — produced
    from exactly those bytes by `scripts/render_diagrams.py` with the real
    binaries — is the thing worth looking at. So the source is replaced by its
    render, and the rest of the output is untouched.
    """
    out = recorded_output(sid)
    marks = list(DIAGRAM_MARK.finditer(out))
    if not marks:
        return (f'<div class="nbcode"><span class="nbtag">Out</span>'
                f'<pre><code>{html.escape(out)}</code></pre></div>')

    parts, cursor = [], 0
    for i, m in enumerate(marks):
        head = out[cursor:m.start()].rstrip()
        if head.strip():
            parts.append(f'<div class="nbcode"><span class="nbtag">Out</span>'
                         f'<pre><code>{html.escape(head)}</code></pre></div>')
        stem = m.group(2)
        body_end = marks[i + 1].start() if i + 1 < len(marks) else len(out)
        body = out[m.end():body_end]
        terminator = "}" if m.group(1) == "dot" else "@enduml"
        cut = body.rindex(terminator) + len(terminator) if terminator in body else 0
        cursor = m.end() + cut
        if (DIAGRAMS_DIR / f"{stem}.svg").is_file():
            parts.append(
                f'<figure class="nbdiag"><img src="../assets/diagrams/{stem}.svg" '
                f'alt="{html.escape(stem.replace("-", " "))}" loading="lazy">'
                f'<figcaption>Rendered from the skill\u2019s own '
                f'{"Graphviz DOT" if m.group(1) == "dot" else "PlantUML"} output '
                f'by <code>scripts/render_diagrams.py</code>. '
                f'<a href="../assets/diagrams/{stem}.svg" target="_blank" '
                f'rel="noopener">open full size</a></figcaption></figure>')
        else:
            parts.append(f'<div class="nbcode"><span class="nbtag">Out</span>'
                         f'<pre><code>{html.escape(body[:cut])}</code></pre></div>')
    tail = out[cursor:].strip()
    if tail:
        parts.append(f'<div class="nbcode"><span class="nbtag">Out</span>'
                     f'<pre><code>{html.escape(tail)}</code></pre></div>')
    return "".join(parts)


FALLBACK_SCRIPT = "the skill\u2019s script"


def script_of(sid: str) -> str | None:
    """The skill script this lesson runs, read out of the built notebook.

    Naming it on the page is the point of the change: the reader can open that
    file in the repository and see the whole procedure, rather than scrolling a
    notebook that used to inline it.
    """
    f = NB_DIR / f"{sid}.ipynb"
    if not f.is_file():
        return None
    for cell in json.loads(f.read_text()).get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for line in cell.get("source", []):
            if line.startswith("SCRIPT = "):
                return line.split("=", 1)[1].strip().strip('"')
    return None


def recorded_output(sid: str) -> str:
    """What this lesson printed when it ran — on Kaggle, verified against local.

    `labs/notebooks/_output/<id>.txt` is written by `run_notebooks.py` on every
    run, so it cannot show output from a lesson that has since changed —
    which the previous source, refreshed only when kaggle_verify was passed
    --save, silently did. `kaggle_verify.py` separately proves this same text
    is what a Kaggle kernel printed.
    """
    f = ROOT / "labs" / "notebooks" / "_output" / f"{sid}.txt"
    if f.is_file() and f.read_text().strip():
        return f.read_text().rstrip()
    return "(no output — this is a reading lesson)"


def has_code(sid: str) -> bool:
    """Does this lesson actually have something to run?

    Several lessons — the function introductions, the architecture map — are
    diagrams and prose end to end. Offering "Run on Kaggle" on those sends the
    reader to a kernel with nothing in it to execute, which teaches them the
    button is decorative everywhere else too.
    """
    path = NB_DIR / f"{sid}.ipynb"
    if not path.is_file():
        return False
    return any(c.get("cell_type") == "code" and "".join(c.get("source", [])).strip()
               for c in json.loads(path.read_text()).get("cells", []))


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
        '<link rel="icon" type="image/png" href="../assets/favicon.png">'
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

    if s.get("risk") or s.get("control"):
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

    # The buttons come first: the point of the page is that you can run it.
    # Two buttons, and only on a lesson that has code — a reading lesson gets
    # neither, because there is nothing on the other end of them.
    if has_code(sid):
        parts.append('<div class="cta-row">'
                     f'<a class="btn k" href="{kaggle_url(sid)}" target="_blank" rel="noopener">'
                     f'▶ Run on Kaggle</a>'
                     f'<a class="btn p" href="{ex_url}" target="_blank" rel="noopener">'
                     f'↗ Open the notebook on GitHub</a>'
                     '</div>')
        # Collapsed by default. It is prerequisite detail — the same four
        # sentences on all 120 pages — and a reader who has run one lesson
        # never needs it again, so it should not sit above the lesson every
        # time. <details> needs no JavaScript and stays keyboard-accessible.
        parts.append('<details class="kagnote"><summary>What “Run on Kaggle” '
                     'does, and what it needs</summary>'
                     '<div class="kagbody"><p>“Run on Kaggle” opens the notebook in '
                     '<b>your own</b> Kaggle account as a new kernel. The notebook '
                     'carries no procedure: it clones this repository — shallow '
                     'and sparse, the skills directory only, about three seconds '
                     '— and runs '
                     f'<code>{html.escape(script_of(sid) or FALLBACK_SCRIPT)}</code> '
                     'out of it. Switch <b>Internet</b> on in the notebook '
                     'settings first; Kaggle gates that on a verified phone '
                     'number, and without one you can attach the dataset '
                     '<code>cybercommons/cyber-commons-skills</code> instead. '
                     'The copy is yours to edit and re-run, and nothing is '
                     'written back here.</p>'
                     '<p>New here? <a href="A0.1.html">A0.1</a> walks the whole '
                     'mechanism and runs it on itself.</p></div></details>')
    else:
        parts.append('<p class="sub kagnote">This lesson is a reading lesson — '
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

    parts.append(f'<p class="sub" style="margin-top:10px">Notebook source: '
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
    nb = list(NB_DIR.glob("*.ipynb"))
    return {
        "sessions": sum(len(t["sessions"]) for f in CUR["functions"] for t in f["tracks"]),
        "chapters": sum(len(f["tracks"]) for f in CUR["functions"]),
        "functions": len(CUR["functions"]),
        "skills": len(list((ROOT / "skills").rglob("SKILL.md"))),
        "run_a_skill": sum(1 for f in nb
                           if any(c["cell_type"] == "code"
                                  for c in json.loads(f.read_text())["cells"])),
    }


# The homepage names the five functions in the language a reader arrives with,
# which is not the language the curriculum stores. curriculum.json's titles are
# embedded in 39 notebooks and in every lesson page's breadcrumb, so renaming
# them there would mean rebuilding and re-verifying all 120 notebooks for a
# copy change. The mapping lives here instead, and a function missing from it
# fails the build rather than quietly falling back to the stored title.
TRACKS = {
    "A": ("Agent architecture &amp; risks",
          "One reference architecture for agentic systems, and every risk that "
          "attaches to a component of it."),
    "B": ("AI SDLC &amp; harness",
          "An AppSec pipeline that runs before and after deploy, and the harness "
          "that measures whether it works."),
    "C": ("AI red teaming",
          "One authorised, scoped offensive lifecycle against your own estate — "
          "from ingestion and elicitation to containment, forensics and "
          "governance."),
    "D": ("Agentic SOC",
          "Detection and response when the analyst is directing agents rather "
          "than reading alerts one at a time."),
    "E": ("AI GRC",
          "Risk, control, regulatory mapping and the CISO office, for systems "
          "that take actions on their own."),
}


def days_block() -> str:
    """The Day 0/1/2 legend, once — not repeated per track.

    An earlier version printed all three days for all five functions on the
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

    # Link integrity. Every "Open the exercise" button points at a path inside
    # this repository, so a 404 is detectable here rather than by a reader.
    # This is the check that was missing when those links shipped broken.
    broken = [e["s"]["id"] for e in seq
              if not (NB_DIR / f"{e['s']['id']}.ipynb").is_file()]
    if broken:
        print(f"::error::{len(broken)} lesson(s) link to a notebook that does not "
              f"exist: {broken[:8]}\nRun: python3 scripts/build_notebooks.py",
              file=sys.stderr)
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
