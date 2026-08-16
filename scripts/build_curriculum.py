#!/usr/bin/env python3
"""Generate curriculum/*.md (one file per track + Module 0) from the single
source of truth: site/data/curriculum.json + curriculum/labs.json.

The website renders from the same JSON, so the docs and the site can never
drift. Run after editing either JSON:

    python3 scripts/build_curriculum.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
LABS = json.loads((ROOT / "curriculum" / "labs.json").read_text())["labs"]
OUT = ROOT / "curriculum"

DIRECTION = {"defend": "AI for Security", "secure": "Security of AI", "both": "both directions"}


def lab_block(sid: str) -> str:
    lab = LABS.get(sid)
    if not lab:
        return ""
    lines = [f"\n**Run it** — {lab['goal']}\n", "```bash"]
    lines += lab["run"]
    lines += ["```", f"\n*Expect:* {lab['expect']}\n"]
    return "\n".join(lines)


def session_md(s: dict) -> str:
    out = [f"### {s['id']} — {s['title']}", ""]
    out.append(f"`{DIRECTION.get(s.get('track','both'))}`" + ("  ·  **flagship lab**" if s.get("featured") else ""))
    out.append("")
    if s.get("risk"):
        out.append(f"- **Risk** — {s['risk']}")
    if s.get("control"):
        out.append(f"- **Control** — {s['control']}")
    if s.get("lab"):
        out.append(f"- **Lab** — {s['lab']}")
    tools = ", ".join(f"`{t}`" for t in s.get("tools", []))
    models = ", ".join(f"`{m}`" for m in s.get("models", []))
    if tools:
        out.append(f"- **Tools** — {tools}")
    if models:
        out.append(f"- **Models** — {models}")
    out.append(lab_block(s["id"]))
    if s.get("repo"):
        out.append(f"> Lab source: [`{s['repo']}`](../{s['repo']})\n")
    return "\n".join(out)



def write_tracks():
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
                  "> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.", "",
                  "---", ""]
            for s in tr["sessions"]:
                md.append(session_md(s))
                md.append("---\n")
            adj = CUR.get("adjacency", {}).get(tr["id"])
            if adj:
                md.append(f"**Adjacency requirement:** also complete {adj} — the failures happen in the seams.\n")
            (OUT / f"track-{tr['id'].lower()}.md").write_text("\n".join(md))
            n += 1
    index += ["", "## Seniority overlay", "",
              "Every track runs at three depths. The topics don't change; the accountability does.", "",
              "| Depth | Typical grade | What you do | Assessment |", "|---|---|---|---|"]
    for r in CUR["seniority"]:
        index.append(f"| **{r['depth']}** | {r['grade']} | {r['does']} | {r['assessed']} |")
    (OUT / "README.md").write_text("\n".join(index) + "\n")
    return n


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    b = write_tracks()
    total = sum(len(t["sessions"]) for f in CUR["functions"] for t in f["tracks"])
    with_labs = sum(1 for f in CUR["functions"] for t in f["tracks"] for s in t["sessions"] if s["id"] in LABS)
    print(f"wrote {b} track files ({total} sessions, {with_labs} with runnable command blocks)")
