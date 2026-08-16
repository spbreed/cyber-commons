#!/usr/bin/env python3
"""Generate one runnable Jupyter notebook per lesson.

    labs/notebooks/<ID>.ipynb      one per session, 104 of them

Inputs (the same single source of truth the site builds from):
    site/data/curriculum.json     structure, risk, control, tools, models
    curriculum/labs.json          the goal and expected-output line
    scripts/exercises/            the per-session exercise body (code + prose)

Every notebook is self-contained and runs top to bottom with **no network and no
pip install** — standard library plus `labs/cybercommons`, which the bootstrap
cell locates whether the notebook is opened from a clone, from the repository
root, or from a Kaggle kernel (where the bootstrap clones the repo if the kernel
has internet enabled, and otherwise falls back to the vendored copy).

    python3 scripts/build_notebooks.py           # write them all
    python3 scripts/build_notebooks.py --check   # CI: fail if any is stale
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
LABS = json.loads((ROOT / "curriculum" / "labs.json").read_text())["labs"]
OUT = ROOT / "labs" / "notebooks"
REPO = "https://github.com/spbreed/cyber-commons"
BRANCH = "claude/vulnbench-setup-scheduling-81aqov"

from exercises import EXERCISES  # noqa: E402

DIRECTION = {"defend": "AI for Security", "secure": "Security of AI",
             "both": "Both directions"}


# ------------------------------------------------------------------ ipynb bits
def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(source)}


def code(source: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _lines(source)}


def _lines(text: str) -> list[str]:
    """nbformat stores source as a list of lines, each keeping its newline."""
    text = text.strip("\n")
    return [ln + "\n" for ln in text.split("\n")[:-1]] + [text.split("\n")[-1]]


BOOTSTRAP = '''\
# --- Cyber Commons bootstrap -------------------------------------------------
# Puts the lab library on the path. Works from a clone, from the repo root, and
# on Kaggle. Standard library only — nothing to install, no network required.
import sys, os, subprocess
from pathlib import Path

def _find_labs():
    for base in [Path.cwd(), *Path.cwd().parents]:
        if (base / "labs" / "cybercommons" / "__init__.py").is_file():
            return base / "labs"
    # Kaggle kernels start in /kaggle/working with the repo absent. If the
    # kernel has internet enabled we clone it; if not, this raises and the
    # message tells you to attach the repo as a dataset instead.
    dest = Path("/kaggle/working/cyber-commons")
    if not dest.exists():
        subprocess.run(["git", "clone", "--depth", "1", "--branch", "%(branch)s",
                        "%(repo)s", str(dest)], check=True)
    return dest / "labs"

sys.path.insert(0, str(_find_labs()))
import cybercommons
print(cybercommons.banner("%(sid)s"))
'''


def bootstrap_cell(sid: str) -> dict:
    return code(BOOTSTRAP % {"sid": sid, "repo": REPO, "branch": BRANCH})


# ------------------------------------------------------------------ assembly
def flatten() -> list[dict]:
    seq = []
    m0 = CUR["module0"]
    for s in m0["sessions"]:
        seq.append({"s": s, "track_id": "M0", "track": m0["title"],
                    "fn": "Module 0 — the shared core"})
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            for s in tr["sessions"]:
                seq.append({"s": s, "track_id": tr["id"], "track": tr["title"],
                            "fn": f"Function {fn['id']} — {fn['title']}"})
    return seq


def notebook(entry: dict) -> dict:
    s = entry["s"]
    sid = s["id"]
    lab = LABS.get(sid, {})
    ex = EXERCISES.get(sid)
    if ex is None:
        raise KeyError(f"no exercise defined for {sid} — add it to scripts/exercises/")

    goal = ex.get("goal") or lab.get("goal") or s.get("lab", "")
    expect = ex.get("expect") or lab.get("expect", "")
    tools = ", ".join(s.get("tools", [])) or "—"
    models = ", ".join(s.get("models", [])) or "—"

    cells = [md(
        f"# {sid} · {s['title']}\n\n"
        f"**{entry['fn']} → {entry['track']}**  ·  "
        f"*{DIRECTION.get(s.get('track', 'both'), 'Both directions')}*\n\n"
        f"---\n\n"
        f"**Risk.** {s.get('risk', '')}\n\n"
        f"**Control.** {s.get('control', '')}\n\n"
        f"**This lab.** {goal}\n\n"
        f"| | |\n|---|---|\n"
        f"| Open-source tooling | {tools} |\n"
        f"| Open-weight models | {models} |\n\n"
        f"> Runs anywhere: standard library only, no network, no API key. "
        f"Where a lesson names a real tool you would deploy (Falco, OPA, SPIRE, "
        f"Keycloak), the notebook models the *decision* that tool makes, so the "
        f"lesson still lands on a machine that cannot pull containers."
    ), bootstrap_cell(sid)]

    if intro := ex.get("intro"):
        cells.append(md(intro))

    for kind, source in ex["steps"]:
        cells.append(md(source) if kind == "md" else code(source))

    if expect:
        cells.append(md(f"### Expect\n\n{expect}"))
    if challenge := ex.get("challenge"):
        cells.append(md(f"### Your turn\n\n{challenge}"))

    cells.append(md(
        f"---\n\n"
        f"[All lessons]({REPO}/tree/{BRANCH}/labs/notebooks) · "
        f"[Lesson page](https://spbreed.github.io/cyber-commons/lessons/{sid}.html) · "
        f"[Lab library]({REPO}/tree/{BRANCH}/labs/cybercommons)\n\n"
        f"*Cyber Commons — a free, open commons for Cyber AI.*"))

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
            # Kaggle reads these when the notebook is pushed as a kernel
            "kaggle": {"accelerator": "none", "dataSources": [],
                       "isInternetEnabled": False, "language": "python",
                       "sourceType": "notebook"},
            "cybercommons": {"session": sid, "track": entry["track_id"],
                             "title": s["title"]},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if any notebook is stale")
    a = ap.parse_args()

    seq = flatten()
    missing = [e["s"]["id"] for e in seq if e["s"]["id"] not in EXERCISES]
    if missing:
        print(f"::error::{len(missing)} sessions have no exercise: {missing}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for e in seq:
        sid = e["s"]["id"]
        text = json.dumps(notebook(e), indent=1, ensure_ascii=False) + "\n"
        f = OUT / f"{sid}.ipynb"
        if not f.exists() or f.read_text() != text:
            stale.append(sid)
            if not a.check:
                f.write_text(text)

    keep = {f"{e['s']['id']}.ipynb" for e in seq}
    for f in OUT.glob("*.ipynb"):
        if f.name not in keep:
            stale.append(f"{f.name} (removed)")
            if not a.check:
                f.unlink()

    if a.check:
        if stale:
            print(f"::error::labs/notebooks is out of date ({len(stale)}): {stale[:5]}"
                  f"\nRun: python3 scripts/build_notebooks.py", file=sys.stderr)
            return 1
        print(f"ok: {len(seq)} notebooks up to date")
        return 0

    print(f"wrote {len(seq)} notebooks to labs/notebooks"
          f" ({len(stale)} changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
