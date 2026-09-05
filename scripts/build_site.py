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

DIRECTION = {"defend": ("d", "AI for Security"), "secure": ("s", "Security of AI"),
             "both": ("b", "Both directions")}


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


def notebook_block(sid: str) -> str:
    """Render the lesson's notebook inline — the same cells, in order.

    The page shows the notebook rather than a separate prose copy of it, so the
    thing you read and the thing you run cannot drift apart.
    """
    f = NB_DIR / f"{sid}.ipynb"
    if not f.is_file():
        return ""
    nb = json.loads(f.read_text())
    parts = ['<div class="nb">']
    for cell in nb.get("cells", []):
        src = "".join(cell.get("source", []))
        if not src.strip():
            continue
        if cell["cell_type"] == "markdown":
            parts.append(f'<div class="nbmd">{md_to_html(src)}</div>')
        else:
            # A lesson page shows what the skill **printed**, not the eight
            # lines that located the file and ran it. The code lives in the
            # repository and is linked from the cell; putting it on the page
            # again made the page look like source and buried the result.
            parts.append(output_block(sid))
    parts.append("</div>")
    return "".join(parts)


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
        '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700'
        '&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600'
        '&display=swap" rel="stylesheet">'
        '<link rel="stylesheet" href="../assets/lesson.css"></head><body>')

FOOT = ('<footer><div class="fin"><span>Cyber Commons · Navigating Cyber Singularity</span>'
        f'<span><a href="../index.html">Home</a> · <a href="index.html">All lessons</a> · '
        f'<a href="{REPO}">Source</a></span></div></footer></body></html>')


def lesson_page(entry, prev, nxt) -> str:
    s, sid = entry["s"], entry["s"]["id"]
    lab = LABS.get(sid, {})
    dcls, dlabel = DIRECTION.get(s.get("track", "both"), DIRECTION["both"])
    ex_url, ex_label = exercise_link(sid)
    title = f"{sid} — {s['title']} | Cyber Commons"

    parts = [HEAD.format(title=html.escape(title),
                         desc=html.escape((s.get("control") or s.get("risk") or "")[:180])), NAV]
    parts.append('<div class="wrap"><div class="lhead">')
    parts.append(f'<div class="crumb"><a href="index.html">All lessons</a> › '
                 f'{html.escape(entry["fn"])} › {html.escape(entry["track"])}</div>')
    parts.append(f'<div class="sid">{html.escape(sid)}</div>')
    parts.append(f'<h1>{html.escape(s["title"])}</h1>')
    badges = [f'<span class="badge {dcls}">{dlabel}</span>']
    if s.get("featured"):
        badges.append('<span class="badge s">Flagship lab</span>')
    badges.append(f'<span class="badge t">{html.escape(entry["track_id"])}</span>')
    parts.append('<div class="badges">' + "".join(badges) + '</div></div>')

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

    nb = notebook_block(sid)
    if nb:
        parts.append('<h3 class="nbh">The notebook</h3>')
        parts.append(nb)
    elif lab.get("run"):                       # fallback if a notebook is missing
        parts.append(f'<pre><code>{html.escape(chr(10).join(lab["run"]))}</code></pre>')

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


def curriculum_block() -> str:
    """The chapter grid: one row per track, linking to that track's first lesson."""
    out = ['<div class="chapters rv">']
    for fn in CUR["functions"]:
        out.append(f'<div class="fnrow"><span class="fk">Function {html.escape(fn["id"])}</span>'
                   f'<span class="fn">{html.escape(fn["title"])}</span></div>')
        for tr in fn["tracks"]:
            first = tr["sessions"][0]["id"]
            n = len(tr["sessions"])
            out.append(f'<a class="chrow" href="lessons/{first}.html">'
                       f'<span class="cid">{html.escape(tr["id"])}</span>'
                       f'<span class="ct">{html.escape(tr["title"])}</span>'
                       f'<span class="cn">{n} lesson{"s" if n != 1 else ""}</span></a>')
    out.append("</div>")
    return "\n".join(out)


def homepage(src: str) -> str:
    n = home_numbers()
    if CUR_BEGIN not in src or CUR_END not in src:
        raise SystemExit("site/index.html has lost its CURRICULUM markers")
    head, rest = src.split(CUR_BEGIN, 1)
    _, tail = rest.split(CUR_END, 1)
    src = f"{head}{CUR_BEGIN}\n{curriculum_block()}\n{CUR_END}{tail}"

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
