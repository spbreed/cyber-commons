#!/usr/bin/env python3
"""Function A as a hands-on lab: site/lab/index.html, where every step runs in
the reader's browser.

    python3 scripts/build_lab.py           # write the page and the Python bundle
    python3 scripts/build_lab.py --check   # fail if either is stale, or if any
                                           # step's output drifts from its lesson

Students said Function A was a lot of reading before anything ran. The lab is
the other way in. It follows the shape of a protocol explorer: lessons down the
left, the parties in a lesson as lanes, each step an arrow between two of them,
and a play bar — reset, back, play, step, speed — that runs the steps in order.
Every step is real Python against the real CyberTravels code, run by Pyodide in
the browser, and the code a reader sees is editable.

**What makes it honest.** Each lesson runs against the tree *as it stood at the
end of that lesson* (`checkpoint.py --at`), shipped as a bundle of source files
this script writes. Nothing is a recording: if Python cannot start, the page
says so and shows no output. No step asks a model anything — where a lesson is
about what a model proposes, the reader types the proposal — because a canned
model answer is the substitution this repository refuses everywhere else.

**What the gate does.** `--check` runs every step again with CPython, isolated,
in a fresh checkpoint of its lesson, and compares the output with the `expect`
in `scripts/exercises/lab_a.py`. Writing that file found a real defect: A1.7's
lesson page told readers to call `Budget.exhausted()`, which does not exist
until Function B. Nothing had ever run the snippet at its own checkpoint.

**Without JavaScript** the page is a long, readable list of every lesson's
steps with their code and commands. The script only adds the player.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from exercises import labs as LABS                    # noqa: E402
from exercises import lessonskills as LS              # noqa: E402
from exercises import repo as R                       # noqa: E402

OUT = ROOT / "site" / "lab"
PAGE = OUT / "index.html"
BUNDLE = OUT / "cybertravels.json"
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf8"))
# The functions taught as labs, in curriculum order, and every lab in them.
FNS = [f for f in CUR["functions"] if f["id"] in LABS.MODULES]
LAB = LABS.load()
# Pinned: a version months old, so a CDN change cannot move the page under us.
PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/"
# `ssl` and `sqlite3` are standard library that Pyodide ships separately:
# PyJWT imports `ssl` for its key-set client, and without it `import jwt` fails,
# identity.py falls back to "PyJWT is not installed", and every identity step
# refuses for a reason that is not true.
# PyJWT by exact wheel, not by name: installing by name asks PyPI's index which
# version is newest, so the same page could run different code next month.
PYJWT = ("https://files.pythonhosted.org/packages/79/84/0fdf9b18ba31d69877bd39"
         "c9cd6052b47f3761e9910c15de788e519f079f/PyJWT-2.9.0-py3-none-any.whl")
E = html.escape


def lessons() -> list[tuple[dict, dict]]:
    return [(t, s) for f in FNS for t in f["tracks"] for s in t["sessions"]]


# --------------------------------------------------------------------------- #
# The Python each lesson runs against
# --------------------------------------------------------------------------- #
def checkpoint(sid: str, dest: Path) -> Path:
    """The CyberTravels package as it stood at the end of `sid`, under dest."""
    pkg = dest / "cybertravels"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "checkpoint.py"),
                        "--at", sid, "--out", str(pkg)],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"checkpoint {sid} failed:\n{r.stdout}{r.stderr}")
    return dest


def bundle() -> dict:
    """Every lesson's tree, with identical files stored once.

    Sixteen lessons resolve to seven distinct trees and most files repeat
    across them, so files are keyed by content hash and a tree is a map from
    path to hash. Only `.py` files ship: the browser runs code, and the data
    directory is created fresh by the code itself.
    """
    files: dict[str, str] = {}
    trees: dict[str, dict[str, str]] = {}
    by_lesson: dict[str, str] = {}
    with tempfile.TemporaryDirectory() as tmp:
        for _t, s in lessons():
            root = checkpoint(s["id"], Path(tmp) / s["id"])
            tree = {}
            for f in sorted((root / "cybertravels").rglob("*.py")):
                src = f.read_text(encoding="utf8")
                h = hashlib.sha256(src.encode()).hexdigest()[:16]
                files[h] = src
                tree[f.relative_to(root).as_posix()] = h
            tid = hashlib.sha256(json.dumps(tree, sort_keys=True).encode()).hexdigest()[:10]
            trees[tid] = tree
            by_lesson[s["id"]] = tid
    return {"_note": "Generated by scripts/build_lab.py from checkpoint.py. "
                     "Do not edit.",
            "lessons": by_lesson, "trees": trees, "files": files}


# --------------------------------------------------------------------------- #
# Consistency, and running every step for real
# --------------------------------------------------------------------------- #
def shape_problems() -> list[str]:
    want = [s["id"] for _t, s in lessons()]
    bad = []
    if sorted(LAB) != sorted(want):
        bad.append(f"lab lessons {sorted(set(LAB) ^ set(want))} do not match the "
                   f"functions in exercises/labs.py")
    for sid, lab in LAB.items():
        actors = lab["actors"]
        if not 2 <= len(actors) <= 4:
            bad.append(f"{sid}: {len(actors)} lanes; the diagram holds two to four")
        for i, st in enumerate(lab["steps"], 1):
            if ("code" in st) == ("cmd" in st):
                bad.append(f"{sid} step {i}: needs exactly one of code or cmd")
            a, b, _ = st["arrow"]
            for x in (a, b):
                if x not in actors:
                    bad.append(f"{sid} step {i}: arrow names {x!r}, not a lane")
            if "code" in st and "expect" not in st:
                bad.append(f"{sid} step {i}: code with no recorded expect")
            for path in re.findall(r"\b((?:scripts|skills)/[\w./-]+\.py)\b",
                                   st.get("cmd", "")):
                if not (ROOT / path).exists():
                    bad.append(f"{sid} step {i}: {path} does not exist")
    return bad


RUNNER = r"""
import contextlib, io, json, sys, traceback
LAB = __import__("exercises." + sys.argv[2], fromlist=["LAB"]).LAB
ns, out = {"__name__": "__lab__"}, []
for st in LAB[sys.argv[1]]["steps"]:
    if "code" not in st:
        continue
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(st["code"], "<step>", "exec"), ns)
    except BaseException:
        buf.write(traceback.format_exc(limit=-1))
    out.append(buf.getvalue())
print(json.dumps(out))
"""


def run_problems() -> list[str]:
    """Run every step with CPython in its lesson's own checkpoint.

    Isolated (-I) and from inside the checkpoint, so `import cybertravels`
    can only mean that tree: run from the repository root it silently imported
    the finished application instead, and A1.0's list of parts came back with
    six packages that do not exist until Function C.
    """
    try:
        import jwt  # noqa: F401
    except BaseException:  # noqa: BLE001 — a broken wheel raises PanicException
        return ["PyJWT is not importable, so the identity steps cannot run. "
                "pip install PyJWT (CI does, before this gate)"]
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        lab_dir = Path(tmp) / "exercises"
        lab_dir.mkdir()
        (lab_dir / "__init__.py").write_text("")
        for name in LABS.MODULES.values():
            (lab_dir / f"{name}.py").write_text(
                (ROOT / "scripts" / "exercises" / f"{name}.py").read_text(encoding="utf8"))
        for sid, lab in LAB.items():
            root = checkpoint(sid, Path(tmp) / "cp" / sid)
            env = {k: v for k, v in os.environ.items()
                   if not k.startswith(("CT_", "OPENAI", "ANTHROPIC"))}
            env["PYTHONPATH"] = f"{root}{os.pathsep}{tmp}"
            r = subprocess.run([sys.executable, "-c",
                                "import sys; sys.path[:0] = __import__('os')"
                                ".environ['PYTHONPATH'].split(__import__('os').pathsep);"
                                + RUNNER, sid, LABS.module_of(sid)],
                               cwd=root, env=env, capture_output=True, text=True)
            if r.returncode:
                bad.append(f"{sid}: runner failed\n{r.stderr[-600:]}")
                continue
            got = json.loads(r.stdout.strip().splitlines()[-1])
            steps = [st for st in lab["steps"] if "code" in st]
            for i, (st, out) in enumerate(zip(steps, got), 1):
                if out != st["expect"]:
                    bad.append(f"{sid} step {i} ({st['title']}): printed\n"
                               f"    {out!r}\n  expected\n    {st['expect']!r}")
    return bad


# --------------------------------------------------------------------------- #
# The page
# --------------------------------------------------------------------------- #
CSS = r"""
body{background:#fbfcfd}
.lab-shell{display:grid;grid-template-columns:270px minmax(0,1fr);min-height:calc(100vh - 64px)}
.lab-side{border-right:1px solid var(--line-soft);background:#f6f8fa;padding:18px 14px 28px;
  position:sticky;top:64px;height:calc(100vh - 64px);overflow:auto}
.lab-side .fn a{font-size:inherit;color:inherit;display:inline;padding:0;background:none}
.lab-side .fn{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--text-faint);margin:2px 8px 10px}
.lab-side .fnh{margin:18px 8px 2px;padding-top:12px;border-top:1px solid var(--line-soft);
  font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--defend)}
.lab-side .fnh:first-child{border-top:0;padding-top:0;margin-top:4px}
.lab-fn{font-size:24px;margin:34px 0 0}
.lab-side .ch{margin:14px 0 4px;padding:0 8px;font-weight:700;font-size:15px;color:var(--text)}
.lab-side .ch small{display:block;font-weight:500;color:var(--text-faint);font-size:12.5px;line-height:1.35}
.lab-side a{display:flex;gap:10px;align-items:baseline;padding:6px 10px;border-radius:8px;
  color:var(--text-dim);text-decoration:none;font-size:15px;line-height:1.3}
.lab-side a b{font-family:"IBM Plex Mono",monospace;font-size:11.5px;font-weight:500;color:var(--text-faint);min-width:34px}
.lab-side a:hover{background:#eef3f7;color:var(--text)}
.lab-side a[aria-current=page]{background:#fff;color:var(--text);box-shadow:0 1px 2px rgba(13,27,38,.08),0 0 0 1px var(--line-soft)}
.lab-side a[aria-current=page] b{color:var(--defend)}
.lab-side .foot{margin-top:22px;padding:12px 10px 0;border-top:1px solid var(--line-soft);font-size:13.5px;line-height:1.5;color:var(--text-faint)}
.lab-main{padding:22px 28px 60px;min-width:0}
.lab-intro{max-width:880px;margin:0 0 18px}
.lab-intro h1{font-size:30px;margin:6px 0 6px}
.lab-intro p{margin:0;color:var(--text-dim);font-size:16.5px}
.lab-intro.slim{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:14px}
.lab-intro.slim .py{margin-top:0}
.lab-pn{display:flex;justify-content:space-between;gap:12px;margin-left:auto;font-size:15px}
.lab-main>.lab-pn{margin:0 0 10px;max-width:none}
.lab-pn a{text-decoration:none;font-weight:600}
.lab-go{display:inline-block;background:var(--defend);color:#fff !important;text-decoration:none;font-weight:600;
  padding:8px 18px;border-radius:9px}
.lab-ch{display:flex;gap:10px;align-items:center;font-size:21px;margin:26px 0 10px}
.lab-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.lab-card{display:block;border:1px solid var(--line);border-radius:12px;background:#fff;padding:14px 16px;
  text-decoration:none;color:var(--text);transition:box-shadow .15s,border-color .15s}
.lab-card:hover{border-color:var(--defend);box-shadow:0 4px 14px rgba(13,27,38,.08)}
.lab-card b{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--defend)}
.lab-card h3{font-size:18px;margin:2px 0 4px}
.lab-card p{margin:0 0 8px;font-size:15px;color:var(--text-dim);line-height:1.45}
.lab-card span{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--text-faint)}
.lab-intro .py{display:inline-flex;gap:8px;align-items:center;margin-top:10px;font-family:"IBM Plex Mono",monospace;
  font-size:12px;color:var(--text-faint)}
.lab-intro .py i{width:8px;height:8px;border-radius:50%;background:#c3ced8;display:inline-block}
.lab-intro .py[data-state=ready] i{background:#059669}
.lab-intro .py[data-state=loading] i{background:#0891b2;animation:pulse 1s infinite}
.lab-intro .py[data-state=failed] i{background:#b91c1c}
@keyframes pulse{50%{opacity:.35}}
section.lab{border:1px solid var(--line);border-radius:14px;background:#fff;margin:0 0 26px;overflow:hidden}
.lab-head{padding:18px 22px 14px;border-bottom:1px solid var(--line-soft)}
.lab-head .tags{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tag{font-family:"IBM Plex Mono",monospace;font-size:11px;font-weight:600;letter-spacing:.06em;
  padding:3px 8px;border-radius:6px;background:var(--defend-soft);color:#0b5566}
.tag.dim{background:#eef2f5;color:var(--text-dim);font-weight:500}
.lab-head h2{font-size:24px;margin:8px 0 4px}
.lab-head p{margin:0;color:var(--text-dim);font-size:16px;max-width:820px}
.lab-head .links{margin-top:8px;font-size:14px;display:flex;gap:16px;flex-wrap:wrap}
.lab-head .links a{text-decoration:none}
.modes{display:inline-flex;border:1px solid var(--line);border-radius:9px;padding:2px;background:#f6f8fa;margin-left:auto}
.modes button{font:inherit;font-size:13.5px;border:0;background:transparent;padding:4px 12px;border-radius:7px;color:var(--text-faint);cursor:pointer}
.modes button[aria-pressed=true]{background:#fff;color:var(--text);box-shadow:0 1px 2px rgba(13,27,38,.1)}
/* the sequence: lanes and numbered arrows */
.seq{padding:16px 22px 6px;border-bottom:1px solid var(--line-soft);background:#fcfdfe}
.lanes,.srow{display:grid;grid-template-columns:30px repeat(var(--n),minmax(0,1fr))}
.lanes div{text-align:center;font-weight:700;font-size:14.5px;color:var(--text);padding:0 4px 8px;
  border-bottom:2px solid var(--line)}
.lanes div.adv{color:#a16207;border-color:#f3ddb6}
.srow{position:relative;width:100%;border:0;background:transparent;padding:0;font:inherit;cursor:pointer;
  min-height:40px;text-align:left;color:inherit}
.srow .n{grid-column:1;align-self:center;font-family:"IBM Plex Mono",monospace;font-size:11.5px;
  width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:#eef2f5;color:var(--text-faint)}
.srow .lane{grid-row:1;border-left:1px dashed #d6e1ea;margin-left:50%}
.srow .ar{position:absolute;top:50%;height:2px;background:#9fb3c3;transform:translateY(-1px)}
.srow .ar::after{content:"";position:absolute;top:-4px;border:5px solid transparent}
.srow .ar.r::after{right:-2px;border-left-color:#9fb3c3}
.srow .ar.l::after{left:-2px;border-right-color:#9fb3c3}
.srow .ar.self{height:16px;background:transparent;border:2px solid #9fb3c3;border-left:0;border-radius:0 9px 9px 0;transform:translateY(-8px)}
.srow .ar.self::after{display:none}
.srow .lb{position:absolute;top:50%;transform:translateY(-118%);font-family:"IBM Plex Mono",monospace;
  font-size:11.5px;color:var(--text-faint);white-space:nowrap;padding:0 4px;background:#fcfdfe}
.srow:hover .n{background:#dfe8ef}
.srow.done .n{background:#d7efe6;color:#047857}
.srow.done .ar{background:#6fb59a}.srow.done .ar.r::after{border-left-color:#6fb59a}.srow.done .ar.l::after{border-right-color:#6fb59a}
.srow.done .ar.self{background:transparent;border-color:#6fb59a}
.srow.cur .n{background:var(--defend);color:#fff}
.srow.cur .ar{background:var(--defend)}.srow.cur .ar.r::after{border-left-color:var(--defend)}.srow.cur .ar.l::after{border-right-color:var(--defend)}
.srow.cur .ar.self{background:transparent;border-color:var(--defend)}
.srow.cur .lb{color:var(--defend);font-weight:600}
.srow.fail .n{background:#b91c1c;color:#fff}
/* the play bar */
.bar{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:10px 18px;border-bottom:1px solid var(--line-soft);background:#fff}
.bar button{font:inherit;font-size:14px;border:1px solid transparent;background:transparent;color:var(--text-dim);
  border-radius:8px;padding:5px 10px;cursor:pointer;line-height:1.2}
.bar button:hover{background:#eef3f7}
.bar button:disabled{opacity:.4;cursor:default;background:transparent}
.bar .play{background:var(--defend);color:#fff;font-weight:600;padding:6px 16px}
.bar .play:hover{background:#0b5f74}
.bar .sp{display:flex;gap:2px;align-items:center;margin-left:8px;font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--text-faint)}
.bar .sp button{font-family:"IBM Plex Mono",monospace;font-size:12px;padding:3px 7px}
.bar .sp button[aria-pressed=true]{background:#eef2f5;color:var(--text)}
.bar .count{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:var(--text-faint)}
/* a step */
ol.steps{list-style:none;margin:0;padding:0}
.step{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);border-bottom:1px solid var(--line-soft)}
.step:last-child{border-bottom:0}
.step .say{padding:18px 22px}
.step .say .k{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--text-faint);letter-spacing:.05em}
.step .say h3{font-size:19px;margin:4px 0 8px}
.step .say ul{margin:0;padding-left:18px;color:var(--text-dim);font-size:16px}
.step .say li{margin:3px 0}
.step .cell{padding:16px 18px;background:#f7f9fb;border-left:1px solid var(--line-soft);min-width:0}
.cell .lbl{display:flex;align-items:center;gap:8px;font-family:"IBM Plex Mono",monospace;font-size:11px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--text-faint);margin-bottom:6px}
.cell .lbl .sp{flex:1}
.cell pre,.cell textarea{display:block;width:100%;margin:0;font-family:"IBM Plex Mono",monospace;font-size:13px;line-height:1.55;
  background:#0d1b26;color:#e6f0f6;border:0;border-radius:9px;padding:12px 14px;overflow:auto;white-space:pre;tab-size:4}
.cell textarea{resize:vertical;min-height:4em;outline:none}
.cell textarea:focus{box-shadow:0 0 0 2px var(--defend-lt)}
.cell .cmd pre{background:#122433}
.cell .acts{display:flex;gap:8px;align-items:center;margin:8px 0 0;flex-wrap:wrap}
.cell .acts button{font:inherit;font-size:13.5px;border:1px solid var(--line);background:#fff;color:var(--text-dim);
  border-radius:8px;padding:4px 12px;cursor:pointer}
.cell .acts button.run{background:var(--defend);border-color:var(--defend);color:#fff;font-weight:600}
.cell .acts button.run:hover{background:#0b5f74}
.cell .acts .note{font-size:13px;color:var(--text-faint)}
.cell .out{white-space:pre-wrap;word-break:break-word;margin-top:10px;background:#fff;color:var(--text);border:1px solid var(--line);min-height:2.6em}
.cell .out.err{border-color:#f0c4c4;background:#fff7f7;color:#7f1d1d}
.cell .out:empty::before{content:"Output appears here when you press Run.";color:var(--text-faint);font-style:italic}
.cell .mine{font-size:13.5px;color:var(--text-faint);margin:8px 2px 0}
.lab-hud{font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:#047857;background:#f1fbf7;
  border:1px solid #bfe6d6;border-radius:999px;padding:2px 10px}
.lab-hud:empty{display:none}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#0d1b26;color:#fff;
  padding:9px 18px;border-radius:999px;font-weight:600;z-index:90;box-shadow:0 10px 30px rgba(0,0,0,.25)}
/* the lesson, folded */
.lesson{padding:18px 22px 22px;border-top:1px solid var(--line-soft);background:#fcfdfe}
.lesson h3{font-size:18px;margin:0 0 2px}
.lesson>p{margin:0 0 10px;font-size:14.5px;color:var(--text-faint)}
.lfold{border:1px solid var(--line-soft);border-radius:10px;background:#fff;margin:6px 0}
.lfold summary{cursor:pointer;padding:9px 14px;font-weight:600;font-size:16px;color:var(--text)}
.lfold[open] summary{border-bottom:1px solid var(--line-soft)}
.lbody{padding:6px 16px 12px;font-size:15.5px;color:var(--text-dim);max-width:900px}
.lbody pre{overflow:auto}
.lbody table{border-collapse:collapse;width:100%;font-size:14.5px;margin:8px 0}
.lbody th,.lbody td{border:1px solid var(--line-soft);padding:5px 8px;text-align:left;vertical-align:top}
.lbody h2,.lbody h3{font-size:17px;margin:14px 0 6px}
/* the IDE route */
.ide{padding:18px 22px 22px}
.ide h3{font-size:18px;margin:16px 0 6px}
.ide h3:first-child{margin-top:0}
.ide p{margin:0 0 8px;color:var(--text-dim);font-size:15.5px;max-width:820px}
.ide pre{font-family:"IBM Plex Mono",monospace;font-size:13px;line-height:1.55;background:#0d1b26;color:#e6f0f6;
  border-radius:9px;padding:12px 14px;overflow:auto;margin:0}
.ide details{margin-top:8px;border:1px solid var(--line-soft);border-radius:9px;background:#fbfcfd}
.ide summary{cursor:pointer;padding:8px 12px;font-weight:600;color:var(--text-dim)}
.ide details pre{border-radius:0 0 9px 9px;max-height:420px}
.blk{position:relative}
.blk .copy{position:absolute;top:8px;right:8px;font-family:"IBM Plex Mono",monospace;font-size:11.5px;
  border:1px solid rgba(255,255,255,.25);background:rgba(13,27,38,.6);color:#e6f0f6;border-radius:6px;padding:3px 8px;cursor:pointer}
.blk .copy:hover{background:rgba(13,27,38,.9)}
.blk pre{padding-right:76px}
/* with JavaScript: one lesson, one step, one mode at a time */
html.js section.lab:not(.on){display:none}
html.js .step:not(.on){display:none}
html.js section.lab[data-mode=run] .ide,html.js section.lab[data-mode=ide] .run-pane{display:none}
html:not(.js) .bar,html:not(.js) .modes,html:not(.js) .acts .run{display:none}
@media (max-width:900px){
  .lab-shell{grid-template-columns:1fr}
  .lab-side{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line-soft);padding:12px}
  .lab-side nav{display:flex;flex-wrap:wrap;gap:4px}
  .lab-side .ch{width:100%;margin:8px 0 2px}
  .lab-side .ch small,.lab-side .foot{display:none}
  .lab-side a{padding:4px 8px;font-size:14px}
  .lab-side a span{display:none}
  .lab-main{padding:16px 12px 40px}
  .step{grid-template-columns:1fr}
  .step .cell{border-left:0;border-top:1px solid var(--line-soft)}
  .seq{padding:12px 10px 4px}
  .lanes div{font-size:12.5px}
  .srow .lb{font-size:10.5px}
  .bar .sp{margin-left:0}
}
"""

JS = r"""
(function(){
var PY = %(pyodide)s, BUNDLE = "cybertravels.json";
var pyodide = null, booting = null, data = null, nsFor = {}, mounted = {};
var status = document.querySelector(".lab-intro .py");
function say(state, text){ if(!status) return; status.dataset.state = state; status.querySelector("span").textContent = text; }

function boot(){
  if (booting) return booting;
  say("loading", "Starting Python in your browser (about 12 MB, only the first time)...");
  booting = new Promise(function(res, rej){
    var s = document.createElement("script"); s.src = PY + "pyodide.js";
    s.onload = res; s.onerror = function(){ rej(new Error("could not load Pyodide from " + PY)); };
    document.head.appendChild(s);
  }).then(function(){ return loadPyodide({indexURL: PY}); })
    .then(function(p){ pyodide = p; return p.loadPackage(["sqlite3", "ssl", "micropip"]); })
    .then(function(){ return pyodide.runPythonAsync("import micropip\nawait micropip.install(" + JSON.stringify(%(pyjwt)s) + ")"); })
    .then(function(){ return fetch(BUNDLE).then(function(r){ if(!r.ok) throw new Error("bundle " + r.status); return r.json(); }); })
    .then(function(b){
      data = b;
      pyodide.runPython([
        "import contextlib, io, sys, traceback",
        "def _lab_run(src, ns):",
        "    buf = io.StringIO()",
        "    try:",
        "        with contextlib.redirect_stdout(buf):",
        "            exec(compile(src, '<step>', 'exec'), ns)",
        "        return [buf.getvalue(), '']",
        "    except BaseException:",
        "        return [buf.getvalue(), traceback.format_exc(limit=-2)]",
        "def _lab_use(root):",
        "    for m in [m for m in sys.modules if m == 'cybertravels' or m.startswith('cybertravels.')]:",
        "        del sys.modules[m]",
        "    sys.path[:] = [p for p in sys.path if not p.startswith('/lab/')]",
        "    sys.path.insert(0, root)"
      ].join("\n"));
      say("ready", "Python is running in your browser. Nothing is installed on your computer.");
    })
    .catch(function(e){ var m = String(e.message || e).trim().split("\n").pop();
      say("failed", "Python could not start in this browser (" + m + "). Nothing ran. Use In your IDE to run it on your computer.");
      booting = null; throw new Error(m); });
  return booting;
}

function mount(tid){
  var root = "/lab/" + tid;
  if (!mounted[tid]) {
    var tree = data.trees[tid];
    Object.keys(tree).forEach(function(path){
      var full = root + "/" + path, dir = full.slice(0, full.lastIndexOf("/"));
      pyodide.FS.mkdirTree(dir);
      pyodide.FS.writeFile(full, data.files[tree[path]]);
    });
    mounted[tid] = true;
  }
  return root;
}

function fresh(sec){
  // A clean namespace and a clean database: the same state a reader gets by
  // starting Python again in a fresh checkpoint.
  var root = mount(sec.dataset.tree);
  pyodide.globals.get("_lab_use")(root);
  try { pyodide.FS.rmdir; pyodide.runPython("import shutil, os\nshutil.rmtree('" + root + "/cybertravels/data', ignore_errors=True)"); } catch(e) {}
  var ns = pyodide.globals.get("dict")();
  ns.set("__name__", "__lab__");
  nsFor[sec.id] = ns;
  return ns;
}

function runStep(sec, li){
  var out = li.querySelector(".out"), ta = li.querySelector("textarea");
  if (!ta) return Promise.resolve(true);
  out.classList.remove("err"); out.textContent = "Running...";
  return boot().then(function(){
    if (sec.dataset.active !== "1") { fresh(sec); sec.dataset.active = "1";
      document.querySelectorAll("section.lab").forEach(function(o){ if(o!==sec) o.dataset.active = ""; }); }
    var ns = nsFor[sec.id] || fresh(sec);
    var t0 = performance.now();
    var r = pyodide.globals.get("_lab_run")(ta.value, ns).toJs();
    var ms = Math.round(performance.now() - t0);
    out.textContent = (r[0] || "") + (r[1] || "");
    if (!r[0] && !r[1]) out.textContent = "(ran, printed nothing)";
    out.classList.toggle("err", !!r[1]);
    li.querySelector(".note").textContent = r[1] ? "it raised an error" : "ran in " + ms + " ms, in your browser";
    return !r[1];
  }).catch(function(e){ out.classList.add("err"); out.textContent = "Python is not running, so nothing ran. " + e.message; return false; });
}

function setup(sec){
  var steps = [].slice.call(sec.querySelectorAll(".step")), rows = [].slice.call(sec.querySelectorAll(".srow"));
  var cur = 0, playing = false, speed = 1, timer = null;
  var count = sec.querySelector(".count"), play = sec.querySelector(".play");
  function show(i){
    cur = Math.max(0, Math.min(steps.length - 1, i));
    steps.forEach(function(s, k){ s.classList.toggle("on", k === cur); });
    rows.forEach(function(r, k){ r.classList.toggle("cur", k === cur); r.setAttribute("aria-current", k === cur); });
    count.textContent = "Step " + (cur + 1) + " / " + steps.length;
    sec.querySelector(".prev").disabled = cur === 0;
    sec.querySelector(".next").disabled = cur === steps.length - 1;
  }
  function mark(i, ok){ rows[i].classList.toggle("done", ok); rows[i].classList.toggle("fail", !ok);
    if (ok) progress(sec.id, i, steps.length); }
  // Steps share one Python session, so step 3 may use a name step 1 made.
  // Running step 3 first raised NameError, which read as broken code; any
  // earlier step not yet run in this session is run first, in order.
  function exec(i){
    var chain = Promise.resolve(true);
    for (var k = 0; k < i; k++) (function(k){
      chain = chain.then(function(ok){ if (!ok || rows[k].classList.contains("done")) return ok;
        return runStep(sec, steps[k]).then(function(r){ mark(k, r); return r; }); });
    })(k);
    return chain.then(function(ok){ if (!ok) return false;
      return runStep(sec, steps[i]).then(function(r){ mark(i, r); return r; }); });
  }
  function stop(){ playing = false; clearTimeout(timer); play.textContent = "▶ Play"; }
  function loop(){
    if (!playing) return;
    exec(cur).then(function(ok){
      if (!playing) return;
      if (!ok || cur === steps.length - 1) { stop(); return; }
      timer = setTimeout(function(){ show(cur + 1); loop(); }, 1600 / speed);
    });
  }
  play.onclick = function(){ if (playing) { stop(); return; } playing = true; play.textContent = "❚❚ Pause";
    if (rows[cur].classList.contains("done") && cur < steps.length - 1) show(cur + 1); loop(); };
  sec.querySelector(".next").onclick = function(){ stop(); show(cur + 1); exec(cur); };
  sec.querySelector(".prev").onclick = function(){ stop(); show(cur - 1); };
  sec.querySelector(".reset").onclick = function(){ stop(); sec.dataset.active = ""; delete nsFor[sec.id];
    rows.forEach(function(r){ r.classList.remove("done", "fail"); });
    sec.querySelectorAll("textarea").forEach(function(t){ t.value = t.defaultValue; });
    sec.querySelectorAll(".out").forEach(function(o){ o.textContent = ""; o.classList.remove("err"); });
    sec.querySelectorAll(".note").forEach(function(o){ o.textContent = ""; });
    show(0); };
  sec.querySelectorAll(".sp button").forEach(function(b){ b.onclick = function(){ speed = +b.dataset.s;
    sec.querySelectorAll(".sp button").forEach(function(o){ o.setAttribute("aria-pressed", o === b); }); }; });
  rows.forEach(function(r, k){ r.onclick = function(){ stop(); show(k); }; });
  steps.forEach(function(li, k){ var b = li.querySelector(".acts .run");
    if (b) b.onclick = function(){ stop(); show(k); exec(k); };
    var ta = li.querySelector("textarea");
    if (ta) ta.addEventListener("keydown", function(e){ if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); exec(k); } }); });
  sec.querySelectorAll(".modes button").forEach(function(b){ b.onclick = function(){ sec.dataset.mode = b.dataset.m;
    sec.querySelectorAll(".modes button").forEach(function(o){ o.setAttribute("aria-pressed", o === b); }); }; });
  show(0);
}

// Progress, for the home page's quest. Kept in this browser only; every
// access is guarded because storage can be blocked, and then nothing here
// changes how the lab itself works.
var KEY = "cc.v1", CHAPTERS = %(chapters)s;
function load(){ try { return Object.assign({xp:0, steps:{}, done:[], badges:[], quiz:{}},
  JSON.parse(localStorage.getItem(KEY) || "{}")); } catch(e) { return null; } }
function store(st){ try { localStorage.setItem(KEY, JSON.stringify(st)); } catch(e) {} }
function toast(t){ var d = document.createElement("div"); d.className = "toast"; d.textContent = t;
  document.body.appendChild(d); setTimeout(function(){ d.remove(); }, 1600); }
function badge(st, b, name){ if (st.badges.indexOf(b) < 0) { st.badges.push(b); toast("Badge: " + name); } }
function progress(sid, i, n){
  var st = load(); if (!st) return;
  var got = st.steps[sid] = st.steps[sid] || [];
  if (got.indexOf(i) >= 0) return;
  got.push(i); st.xp += 10; toast("+10 XP");
  badge(st, "first", "First run");
  if (got.length === n && st.done.indexOf(sid) < 0) { st.done.push(sid); st.xp += 20; toast("Lab " + sid + " complete · +20 XP"); }
  Object.keys(CHAPTERS).forEach(function(c){
    if (CHAPTERS[c].every(function(x){ return st.done.indexOf(x) >= 0; })) badge(st, c, "Chapter " + c + " cleared"); });
  store(st); hud();
}
function hud(){ var st = load(), el = document.querySelector(".lab-hud"); if (!st || !el) return;
  el.textContent = st.xp + " XP · " + st.done.length + " of " + %(total)d + " labs"; }
document.addEventListener("click", function(e){
  if (e.target.closest && e.target.closest(".ide .copy")) { var st = load(); if (st) { badge(st, "local", "Took it local"); store(st); } } });

function copyable(){
  document.querySelectorAll(".blk").forEach(function(b){
    var btn = document.createElement("button"); btn.className = "copy"; btn.type = "button"; btn.textContent = "Copy";
    btn.onclick = function(){ var t = b.querySelector("pre,textarea"); var v = t.value !== undefined ? t.value : t.textContent;
      (navigator.clipboard ? navigator.clipboard.writeText(v) : Promise.reject()).then(function(){ btn.textContent = "Copied"; },
        function(){ btn.textContent = "Select and copy"; }); setTimeout(function(){ btn.textContent = "Copy"; }, 1600); };
    // In a code cell the button sits beside Run: over the editor it covered
    // the end of the first line, which is the line a reader edits first.
    var acts = b.parentNode.querySelector(".acts");
    if (b.querySelector("textarea") && acts) { btn.className = "copy-code"; acts.insertBefore(btn, acts.querySelector(".note")); }
    else b.appendChild(btn);
  });
}

function route(){
  document.querySelectorAll("section.lab").forEach(function(x){ x.classList.add("on"); });
  // With 55 lessons the sidebar is longer than the screen; a B3 lesson opened
  // with its own entry scrolled out of sight. Scroll the sidebar, not the page.
  var cur = document.querySelector('.lab-side a[aria-current="page"]'), side = document.querySelector(".lab-side");
  if (cur && side && side.scrollHeight > side.clientHeight) side.scrollTop = cur.offsetTop - side.clientHeight / 3;
}

document.querySelectorAll("section.lab").forEach(setup);
copyable();
route();
hud();
})();
"""


def ext_link(sid: str) -> str:
    return f"../lessons/{sid}.html"


def arrow_row(i: int, st: dict, actors: list[str]) -> str:
    a, b, label = st["arrow"]
    ia, ib, n = actors.index(a), actors.index(b), len(actors)
    centre = lambda k: (k + 0.5) / n * 100  # noqa: E731
    # The number column is 30px, so lanes are laid out over the remaining width.
    pos = lambda pct: f"calc(30px + (100% - 30px) * {pct / 100:.4f})"  # noqa: E731
    lanes = "".join(f'<span class="lane" style="grid-column:{k + 2}"></span>' for k in range(n))
    if ia == ib:
        ar = (f'<span class="ar self" style="left:{pos(centre(ia))};width:22px"></span>'
              f'<span class="lb" style="left:{pos(centre(ia))}">{E(label)}</span>')
    else:
        lo, hi = sorted((centre(ia), centre(ib)))
        d = "r" if ib > ia else "l"
        ar = (f'<span class="ar {d}" style="left:{pos(lo)};width:calc((100% - 30px) * {(hi - lo) / 100:.4f})"></span>'
              f'<span class="lb" style="left:{pos(lo)}">{E(label)}</span>')
    return (f'<button type="button" class="srow" data-i="{i}" '
            f'aria-label="Step {i + 1}: {E(st["title"])}">'
            f'<span class="n">{i + 1}</span>{lanes}{ar}</button>')


def blk(text: str, cls: str = "") -> str:
    return f'<div class="blk {cls}"><pre>{E(text)}</pre></div>'


def step_html(sid: str, i: int, st: dict, n: int) -> str:
    say = "".join(f"<li>{E(x)}</li>" for x in st["say"])
    if "code" in st:
        rows = st["code"].count("\n") + 1
        cell = (f'<div class="lbl">Python <span class="sp"></span>edit it, then run</div>'
                f'<div class="blk"><textarea spellcheck="false" rows="{rows}" '
                f'aria-label="Python for step {i + 1}">{E(st["code"])}</textarea></div>'
                f'<div class="acts"><button type="button" class="run">▶ Run</button>'
                f'<span class="note"></span></div>'
                f'<pre class="out" aria-live="polite"></pre>')
    else:
        cell = (f'<div class="lbl">On your computer</div>{blk(st["cmd"], "cmd")}'
                f'<p class="mine">A browser cannot do this step. Copy it into a '
                f'terminal in the folder you cloned.</p>')
    return (f'<li class="step" data-i="{i}"><div class="say">'
            f'<div class="k">STEP {i + 1} OF {n}</div><h3>{E(st["title"])}</h3>'
            f'<ul>{say}</ul></div><div class="cell">{cell}</div></li>')


def ide_html(sid: str, title: str, lab: dict) -> str:
    name = LS.skill_name(sid, title)
    skill_md = (ROOT / "lesson-skills" / name / "SKILL.md").read_text(encoding="utf8")
    audits = LS.audits_of(sid)
    code = "".join(f"# step {i}: {st['title']}\n{st['code']}\n"
                   for i, st in enumerate(lab["steps"], 1) if "code" in st)
    parts = [
        "<h3>1 · Link this lesson's skill into your AI tool</h3>",
        "<p>Claude Code, Codex, Cursor, Gemini, Copilot and others. It links the "
        "skill; it does not copy it, so a fix reaches you on your next pull.</p>",
        blk(f"python3 scripts/install_skills.py --all --lessons {sid}\n"),
        "<h3>2 · Ask your agent to do the lesson</h3>",
        f"<p>Type <code>/{E(name)}</code>, or just ask it to “do {sid}”. It gets the "
        f"code as it stood at the end of {sid}, runs it, and tells you what happened.</p>",
        "<h3>3 · No agent? Run the same thing from a terminal</h3>",
        blk(f"python3 scripts/lesson.py {sid}\n"),
    ]
    if code:
        parts += [
            "<h3>4 · Run this page's steps on your computer</h3>",
            f"<p>The same Python as the steps above. Get the code as it stood at "
            f"the end of {sid}, save the steps as <code>lab.py</code> in that "
            f"folder, and run it.</p>",
            blk(f"python3 scripts/checkpoint.py --at {sid} --out work/{sid}/cybertravels\n"
                f"cd work/{sid}\npython3 lab.py\n"),
            f'<details><summary>lab.py, every step of {sid}</summary>{blk(code)}</details>',
        ]
    parts += [
        f"<h3>{5 if code else 4} · Copy the skill itself</h3>",
        f"<p>The lesson skill is a folder with one <code>SKILL.md</code>. Paste it "
        f"into your tool's skills folder as <code>{E(name)}/SKILL.md</code> if you "
        f"would rather not link it.</p>",
        f'<details><summary>lesson-skills/{E(name)}/SKILL.md</summary>{blk(skill_md)}</details>',
    ]
    if audits:
        links = ", ".join(f'<a href="{E(R.tree("skills/" + a))}">{E(a)}</a>'
                          for a, _s in audits)
        parts.append(f"<p>It calls the audit skill {links}, which needs a model. "
                     f"Your agent is one.</p>")
    return '<div class="ide">' + "".join(parts) + "</div>"


def section(track: dict, s: dict, tid: str) -> str:
    sid, lab = s["id"], LAB[s["id"]]
    actors = lab["actors"]
    adv = {"Attacker"}
    lanes = "".join(f'<div class="{"adv" if a in adv else ""}">{E(a)}</div>'
                    for a in actors)
    n = len(lab["steps"])
    rows = "".join(arrow_row(i, st, actors) for i, st in enumerate(lab["steps"]))
    steps = "".join(step_html(sid, i, st, n) for i, st in enumerate(lab["steps"]))
    head = (f'<div class="lab-head"><div class="tags"><span class="tag">{sid}</span>'
            f'<span class="tag dim">{E(track["id"])} · {E(track["title"].split(" — ")[0])}</span>'
            f'<span class="modes" role="group" aria-label="Where to run it">'
            f'<button type="button" data-m="run" aria-pressed="true">In your browser</button>'
            f'<button type="button" data-m="ide" aria-pressed="false">In your IDE</button></span></div>'
            f'<h2>{E(s["title"])}</h2><p>{E(lab["goal"])}</p>'
            f'<div class="links"><a href="#lesson">For detailed learning ↓</a>'
            '</div></div>')
    bar = ('<div class="bar"><button type="button" class="reset" title="Start this lesson again">↺ Reset</button>'
           '<button type="button" class="prev" aria-label="Previous step">‹</button>'
           '<button type="button" class="play">▶ Play</button>'
           '<button type="button" class="next" aria-label="Next step">›</button>'
           '<span class="sp">speed' + "".join(
               f'<button type="button" data-s="{x}" aria-pressed="{str(x == 1).lower()}">{x:g}×</button>'
               for x in (0.5, 1, 2, 3)) +
           '</span><span class="count"></span></div>')
    run = (f'<div class="run-pane"><div class="seq" style="--n:{len(actors)}">'
           f'<div class="lanes" style="--n:{len(actors)}"><span></span>{lanes}</div>'
           f'{rows}</div>{bar}<ol class="steps">{steps}</ol></div>')
    return (f'<section class="lab" id="{sid}" data-tree="{tid}" data-mode="run" '
            f'aria-label="{sid} {E(s["title"])}">{head}{run}'
            f'{ide_html(sid, s["title"], lab)}{lesson_html(sid)}</section>')


def lesson_html(sid: str) -> str:
    """The lesson itself, folded under the lab.

    Function A's lesson pages are gone; their content lives here, each part
    closed until a reader opens it, so the page stays about the lab. Only what
    the lab does not already show comes across — `build_site.lab_sections`
    decides that, next to the lesson renderer it borrows from.
    """
    import build_site as BS
    entry = next(e for e in BS.flatten() if e["s"]["id"] == sid)
    folds = "".join(f'<details class="lfold"><summary>{E(h)}</summary>'
                    f'<div class="lbody">{body}</div></details>'
                    for h, body in BS.lab_sections(entry))
    return (f'<div class="lesson" id="lesson"><h3>For detailed learning</h3>'
            f'<p>The ideas behind the steps above. Open any part to read it.</p>{folds}</div>')


def side(current: str | None) -> str:
    out = ['<aside class="lab-side"><div class="fn"><a href="index.html" '
           'style="padding:0;display:inline">Hands-on labs</a></div><nav>']
    for t in (t for f in FNS for t in f["tracks"]):
        if t is next(f for f in FNS if t in f["tracks"])["tracks"][0]:
            fn = next(f for f in FNS if t in f["tracks"])
            out.append(f'<div class="fnh">Function {E(fn["id"])} · '
                       f'{E(fn["title"].split(" — ")[0])}</div>')
        out.append(f'<div class="ch">{E(t["id"])} <small>{E(t["title"].split(" — ")[0])}</small></div>')
        for s in t["sessions"]:
            short = s["title"].split(" — ")[0]
            cur = ' aria-current="page"' if s["id"] == current else ""
            out.append(f'<a href="{s["id"]}.html"{cur}><b>{s["id"]}</b>'
                       f'<span>{E(short)}</span></a>')
    out.append('</nav><div class="foot">Every step runs real Python in your '
               'browser, against CyberTravels as it stood at the end of that '
               'lesson. Nothing is installed on your computer.<br><br>'
               '<a href="../lessons/index.html" style="padding:0">All lessons</a></div></aside>')
    return "".join(out)


STATUS = ('<div class="py" data-state="idle"><i></i><span>Python starts the '
          'first time you press Run or Play.</span></div>')


def shell(title: str, desc: str, current: str | None, main: str, script: str) -> str:
    import build_site as BS
    head = BS.HEAD.format(title=E(title), desc=E(desc))
    return (head.replace("</head>", f"<style>{CSS}</style>"
                         "<script>document.documentElement.classList.add('js')</script></head>")
            + "<!-- Generated by scripts/build_lab.py from scripts/exercises/lab_*.py. Do not edit. -->"
            + BS.NAV.replace('href="index.html">All lessons', 'href="../lessons/index.html">All lessons')
            + f'<div class="lab-shell">{side(current)}<main class="lab-main">{main}</main></div>'
            + (f"<script>{script}</script>" if script else "") + "</body></html>\n")


def index_page() -> str:
    """The way in: what the lab is, and every lesson as a card.

    One page per lesson, because sixteen lessons in one file was 250 KB to
    show one of them. Old links pointed at `index.html#A1.4`; the one line of
    script below sends those to the lesson's own page.
    """
    n_code = sum(1 for l in LAB.values() for st in l["steps"] if "code" in st)
    cards = []
    for fn in FNS:
        cards.append(f'<h2 class="lab-fn">Function {E(fn["id"])} · {E(fn["title"])}</h2>')
        for t in fn["tracks"]:
            cards.append(_chapter_cards(t))
    main = _intro(n_code) + "".join(cards)
    redirect = ('function go(){var h=decodeURIComponent(location.hash.slice(1));'
                'if(/^[A-F]\\d\\.\\d+$/.test(h))location.replace(h+".html");}'
                'go();window.addEventListener("hashchange",go);')
    return shell("Hands-on labs — Cyber Commons",
                 "Every lab step runs real Python in your browser.",
                 None, main, redirect)


def _chapter_cards(t: dict) -> str:
    cards = [f'<h2 class="lab-ch"><span class="tag">{E(t["id"])}</span> '
             f'{E(t["title"].split(" — ")[0])}</h2><div class="lab-cards">']
    for s in t["sessions"]:
        lab = LAB[s["id"]]
        runs = sum(1 for st in lab["steps"] if "code" in st)
        cards.append(f'<a class="lab-card" href="{s["id"]}.html"><b>{s["id"]}</b>'
                     f'<h3>{E(s["title"])}</h3><p>{E(lab["goal"])}</p>'
                     f'<span>{len(lab["steps"])} steps · {runs} run in your browser</span></a>')
    return "".join(cards) + "</div>"


def _intro(n_code: str) -> str:
    return (f'<div class="lab-intro"><span class="tag">HANDS-ON LABS</span>'
            f'<h1>Learn by running it, in your browser</h1>'
            f'<p>Pick a lesson. Press <b>Play</b> to run its steps in order, or '
            f'<b>Run</b> one step at a time. Every one of the {n_code} Python '
            f'steps is real code from CyberTravels, and you can change it. '
            f'To do the same on your computer, open <b>In your IDE</b> on any lesson.</p>'
            f'<p style="margin-top:12px"><a class="lab-go" href="A0.0.html">Start at A0.0 →</a></p>'
            f'</div>')


def lesson_page(b: dict, i: int) -> str:
    seq = lessons()
    t, s = seq[i]
    prev = seq[i - 1][1] if i else None
    nxt = seq[i + 1][1] if i + 1 < len(seq) else None
    nav = '<div class="lab-pn">' + (
        f'<a href="{prev["id"]}.html">← {prev["id"]}</a>' if prev else '<span></span>') + (
        f'<a href="{nxt["id"]}.html">{nxt["id"]} →</a>' if nxt else '<span></span>') + '</div>'
    main = (f'<div class="lab-intro slim">{STATUS}<span class="lab-hud" aria-live="polite"></span>{nav}</div>'
            f'{section(t, s, b["lessons"][s["id"]])}{nav}')
    js = JS % {"pyodide": json.dumps(PYODIDE), "pyjwt": json.dumps(PYJWT),
               "chapters": json.dumps({tr["id"]: [x["id"] for x in tr["sessions"]]
                                       for f in FNS for tr in f["tracks"]}),
               "total": len(seq)}
    return shell(f"{s['id']} hands-on — {s['title']} | Cyber Commons",
                 f"{s['id']}, hands on: {LAB[s['id']]['goal']}", s["id"], main, js)


def render() -> dict[Path, str]:
    b = bundle()
    out = {BUNDLE: json.dumps(b, indent=0, sort_keys=True, ensure_ascii=False) + "\n",
           PAGE: index_page()}
    for i, (_t, s) in enumerate(lessons()):
        out[OUT / f"{s['id']}.html"] = lesson_page(b, i)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="fail if the page or bundle is stale, or any step's output drifts")
    args = ap.parse_args()
    bad = shape_problems()
    if bad:
        print("lab_a.py does not hold together:\n  " + "\n  ".join(bad))
        return 1
    out = render()
    if args.check:
        stale = [p.relative_to(ROOT).as_posix() for p, t in out.items()
                 if not p.exists() or p.read_text(encoding="utf8") != t]
        stale += [f"{p.relative_to(ROOT).as_posix()} (no lesson owns it)"
                  for p in OUT.glob("*.html") if p not in out]
        drift = run_problems()
        for p in stale:
            print(f"stale: {p} — run python3 scripts/build_lab.py")
        for d in drift:
            print(f"drift: {d}")
        n = sum(1 for l in LAB.values() for st in l["steps"] if "code" in st)
        if stale or drift:
            return 1
        print(f"ok: the lab is current, and all {n} Python steps in "
              f"{len(LAB)} lessons print what they say, each at its own checkpoint")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("*.html"):
        if p not in out:
            p.unlink()          # a page for a lesson that is gone would still load
    for p, t in out.items():
        p.write_text(t, encoding="utf8")
    print(f"wrote {len(out) - 1} pages under {OUT.relative_to(ROOT)} and {BUNDLE.relative_to(ROOT)} "
          f"({len(json.loads(out[BUNDLE])['trees'])} distinct trees for {len(LAB)} lessons)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
