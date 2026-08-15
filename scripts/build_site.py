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
REPO = "https://github.com/spbreed/cyber-commons"

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
    m0 = CUR["module0"]
    for s in m0["sessions"]:
        seq.append({"s": s, "track_id": "M0", "track": m0["title"],
                    "fn": "Module 0 — the shared core", "fn_id": "M0"})
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            for s in tr["sessions"]:
                seq.append({"s": s, "track_id": tr["id"], "track": tr["title"],
                            "fn": f"Function {fn['id']} — {fn['title']}", "fn_id": fn["id"]})
    return seq


def exercise_link(sid: str, sess: dict) -> tuple[str, str]:
    """(url, label) for the GitHub exercise behind a lesson."""
    if sess.get("repo"):
        return f"{REPO}/tree/main/{sess['repo']}", sess["repo"]
    lab = LABS.get(sid, {})
    for line in lab.get("run", []):
        if m := re.search(r"cd\s+(labs/[\w.\-/]+)", line):
            return f"{REPO}/tree/main/{m.group(1)}", m.group(1)
    track = sid.split(".")[0].lower()
    if track.startswith("m0"):
        return f"{REPO}/blob/main/curriculum/module-0.md", "curriculum/module-0.md"
    return f"{REPO}/blob/main/curriculum/track-{track}.md", f"curriculum/track-{track}.md"


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
    ex_url, ex_label = exercise_link(sid, s)
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
    if lab.get("goal"):
        parts.append(f'<p class="sub">{html.escape(lab["goal"])}</p>')
    elif s.get("lab"):
        parts.append(f'<p class="sub">{html.escape(s["lab"])}</p>')
    if lab.get("run"):
        cmds = "\n".join(lab["run"])
        parts.append(f'<pre><code>{html.escape(cmds)}</code></pre>')
    if lab.get("expect"):
        parts.append(f'<div class="expect"><b>Expect</b>{html.escape(lab["expect"])}</div>')

    chips = "".join(f'<span>{html.escape(t)}</span>' for t in s.get("tools", []))
    chips += "".join(f'<span class="m">{html.escape(m)}</span>' for m in s.get("models", []))
    if chips:
        parts.append(f'<div class="chips">{chips}</div>')

    parts.append('<div class="cta-row">'
                 f'<a class="btn p" href="{ex_url}" target="_blank" rel="noopener">↗ Open the exercise on GitHub</a>'
                 f'<a class="btn" href="{REPO}/blob/main/MODELS.md" target="_blank" rel="noopener">Get a model free</a>'
                 '</div>'
                 f'<p class="sub" style="margin-top:10px">Exercise source: <code>{html.escape(ex_label)}</code></p>'
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if generated pages differ (CI)")
    a = ap.parse_args()

    seq = flatten()
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

    if a.check:
        if stale:
            print(f"::error::site/lessons is out of date ({len(stale)}): {stale[:5]}"
                  f"{'…' if len(stale) > 5 else ''}\nRun: python3 scripts/build_site.py")
            return 1
        print(f"ok: {len(pages)} lesson pages up to date")
        return 0

    notes = len([f for f in NOTES_DIR.glob("*.md") if f.stem != "README"]) if NOTES_DIR.exists() else 0
    print(f"wrote {len(pages)} pages to site/lessons "
          f"({len(seq)} lessons · {len(VIDEOS)} with video · {notes} with authored notes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
