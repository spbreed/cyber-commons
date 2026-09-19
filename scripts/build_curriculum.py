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
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
LABS = json.loads((ROOT / "curriculum" / "labs.json").read_text())["labs"]
OUT = ROOT / "curriculum"



def lab_block(sid: str, goal: str = "") -> str:
    lab = LABS.get(sid)
    if not lab:
        return ""
    # The goal comes from the session, which is the only copy of it now.
    lines = [f"\n**Run it** — {goal}\n", "```bash"]
    lines += lab["run"]
    lines += ["```", f"\n*Expect:* {lab['expect']}\n"]
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
                    for s in t["sessions"] if s["id"] in LABS)

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
