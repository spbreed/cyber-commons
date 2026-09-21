#!/usr/bin/env python3
"""Generate curriculum/*.md (one file per track + Module 0) from the single
source of truth: site/data/curriculum.json + curriculum/labs.json.

The website renders from the same JSON, so a page and its chapter doc always
say the same thing *once this has been run*. It had not been, and that is why
`--check` exists: these fifteen files are committed, and nothing compared them
against their source. A fix to "a system that changed on Tuesday" landed in
curriculum.json and in the rendered page, and sat uncorrected in
`curriculum/track-f1.md` — where `check_clarity.py` could not see it, because
that gate reads the site.

    python3 scripts/build_curriculum.py            # write curriculum/*.md
    python3 scripts/build_curriculum.py --check    # CI: fail if they are stale
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from exercises.lessonskills import ROLLED_OUT, skill_name  # noqa: E402

CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf8"))
LABS = json.loads((ROOT / "curriculum" / "labs.json").read_text(encoding="utf8"))["labs"]
OUT = ROOT / "curriculum"
TITLES = {s["id"]: s["title"] for f in CUR["functions"] for t in f["tracks"]
          for s in t["sessions"]}


def lesson_run(sid: str) -> list[str]:
    """The run block of a converted lesson, derived rather than typed.

    A converted lesson is done by picking its skill in an agent, and the page
    prints the same thing (`build_site.lesson_skill_block`). Typing it into
    labs.json as well would be a second copy to drift, so labs.json carries no
    entry for a converted lesson and this is what the chapter doc shows.
    """
    name = skill_name(sid, TITLES[sid])
    return [
        "# --- 1 · the repository. master is the trunk. ---",
        "git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons",
        "",
        "# --- 2 · link this lesson's skill into your agent, once. On Windows,",
        "#         use `python` where this says `python3`. ---",
        f"python3 scripts/install_skills.py --all --lessons {sid}",
        "",
        "# --- 3 · in your agent, open this folder and pick the skill:",
        f"#         {name}",
        f"#         (Claude Code and Copilot: /{name} · Cursor: type / and",
        f"#         search · Codex: ${name}). It ends with a readback. ---",
        "",
        "# --- or, with no agent, run the same lesson yourself ---",
        f"python3 scripts/lesson.py {sid}",
    ]



def lab_block(sid: str, goal: str = "") -> str:
    lab = {"run": lesson_run(sid)} if sid in ROLLED_OUT else LABS.get(sid)
    if not lab:
        return ""
    # The goal comes from the session, which is the only copy of it now.
    lines = [f"\n**Run it** — {goal}\n", "```bash"]
    lines += lab["run"]
    # No "*Expect:*" line: labs.json no longer carries one. It rendered a
    # second conclusion beside the lesson's own "What you just proved" — the
    # same paragraph on 59 pages, another lesson's on four — and the chapter
    # doc inherited it from the same field. See scripts/exercises/layout.py.
    lines += ["```", ""]
    return "\n".join(lines)


def session_md(s: dict) -> str:
    out = [f"### {s['id']} — {s['title']}", ""]
    if s.get("featured"):
        out.append("**flagship lab**")
        out.append("")
    if s.get("risk"):
        out.append(f"- **Risk** — {s['risk']}")
    if s.get("control"):
        out.append(f"- **Control** — {s['control']}")
    if s.get("lab"):
        out.append(f"- **Lab** — {s['lab']}")
    tools = ", ".join(f"`{t}`" for t in s.get("tools", []))
    open_weight = ", ".join(f"`{m}`" for m in s.get("open_weight", []))
    frontier = ", ".join(f"`{m}`" for m in s.get("frontier", []))
    if tools:
        out.append(f"- **Tools** — {tools}")
    if open_weight:
        out.append(f"- **Open-weight models** — {open_weight}")
    if frontier:
        out.append(f"- **Frontier models** — {frontier}"
                   "  ·  *every lab runs on either, and offline on neither*")
    out.append(lab_block(s["id"], s.get("lab", "")))
    if s.get("repo"):
        out.append(f"> Lab source: [`{s['repo']}`](../{s['repo']})\n")
    return "\n".join(out)



def render() -> dict[Path, str]:
    """Every generated file as {path: text}, written by nobody.

    Separated from writing so --check can compare without touching the tree.
    """
    out: dict[Path, str] = {}
    n = 0
    index = ["# Curriculum", "",
             "Generated from [`site/data/curriculum.json`](../site/data/curriculum.json) — the same source the website renders. Edit the JSON (and [`labs.json`](labs.json)), then run `python3 scripts/build_curriculum.py`.", "",
             "You take the track for the chair you sit in, plus two sessions from a neighbouring track.", "",
             "| Track | Role | Sessions | Function |", "|---|---|---|---|"]
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            index.append(f"| [{tr['id']}](track-{tr['id'].lower()}.md) | {tr['title']} | {len(tr['sessions'])} | {fn['id']} — {fn['title']} |")

            md = [f"# Track {tr['id']} — {tr['title']}", "",
                  f"**Function {fn['id']} · {fn['title']}**  ", f"*{fn['blurb']}*", "",
                  f"**Job titles:** {tr.get('titles','')}", "",
                  f"**What changes:** {tr.get('changes','')}", "",
                  f"**Autonomy focus:** {tr.get('autonomy','')}", "",
                  f"**Deliverable:** {tr.get('deliverable','')}", "",
                  "> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.", "",
                  "---", ""]
            for s in tr["sessions"]:
                md.append(session_md(s))
                md.append("---\n")
            adj = CUR.get("adjacency", {}).get(tr["id"])
            if adj:
                md.append(f"**Adjacency requirement:** also complete {adj} — the failures happen in the seams.\n")
            out[OUT / f"track-{tr['id'].lower()}.md"] = "\n".join(md)
            n += 1
    index += ["", "## Seniority overlay", "",
              "Every track runs at three depths. The topics don't change; the accountability does.", "",
              "| Depth | Typical grade | What you do | Assessment |", "|---|---|---|---|"]
    for r in CUR["seniority"]:
        index.append(f"| **{r['depth']}** | {r['grade']} | {r['does']} | {r['assessed']} |")
    out[OUT / "README.md"] = "\n".join(index) + "\n"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if any generated file is stale")
    a = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    files = render()
    total = sum(len(t["sessions"]) for f in CUR["functions"] for t in f["tracks"])
    with_labs = sum(1 for f in CUR["functions"] for t in f["tracks"]
                    for s in t["sessions"]
                    if s["id"] in LABS or s["id"] in ROLLED_OUT)

    if a.check:
        stale = [p.name for p, text in files.items()
                 if not p.is_file() or p.read_text() != text]
        if stale:
            print("::error::stale against site/data/curriculum.json — run "
                  "python3 scripts/build_curriculum.py: " + ", ".join(sorted(stale)),
                  file=sys.stderr)
            return 1
        print(f"ok: {len(files)} curriculum file(s) up to date "
              f"({total} sessions, {with_labs} with runnable command blocks)")
        return 0

    for p, text in files.items():
        p.write_text(text)
    print(f"wrote {len(files)} curriculum file(s) ({total} sessions, "
          f"{with_labs} with runnable command blocks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
