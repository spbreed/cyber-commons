#!/usr/bin/env python3
"""Make every `run` block in curriculum/labs.json start with something that exists.

The problem this fixes: most `run` blocks began `cd labs/<name>` for directories
that were never created (21 of the 24 paths referenced). Those commands were
real in the sense that they name the right tool and the right invocation, but a
reader following them hit a missing directory — and the site's exercise links,
derived from the same lines, 404'd.

The fix keeps both halves honest:

  * the **notebook** goes first, because it runs today, anywhere, with nothing
    installed — and it is what the lesson page renders and what Kaggle opens;
  * the **original tooling commands** are kept underneath, relabelled as the
    full-infrastructure variant, because they are the real thing you would run
    with a container registry and are the target the notebook models.

Idempotent: running it twice changes nothing.

    python3 scripts/relink_labs.py [--check]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABS_PATH = ROOT / "curriculum" / "labs.json"
NB_DIR = ROOT / "labs" / "notebooks"

NB_MARKER = "# --- the notebook: runs anywhere, stdlib only, no install ---"
INFRA_MARKER = ("# --- the full variant, against the real tooling "
                "(needs a container registry) ---")


def notebook_lines(sid: str) -> list[str]:
    return [
        NB_MARKER,
        f"jupyter notebook labs/notebooks/{sid}.ipynb    # or open it on the lesson page",
        f"python3 scripts/run_notebooks.py --session {sid}   # run it headless and check it",
    ]


def rewrite(entry: dict, sid: str) -> dict:
    run = list(entry.get("run", []))
    if run and run[0] == NB_MARKER:              # already converted
        return entry
    existing = [ln for ln in run if ln.strip()]
    new = notebook_lines(sid)
    if existing:
        new += ["", INFRA_MARKER, *existing]
    entry["run"] = new
    return entry


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if any block is unconverted")
    a = ap.parse_args()

    doc = json.loads(LABS_PATH.read_text())
    labs = doc["labs"]

    missing_nb = [sid for sid in labs if not (NB_DIR / f"{sid}.ipynb").is_file()]
    if missing_nb:
        print(f"::error::no notebook for {len(missing_nb)} session(s): {missing_nb[:8]}",
              file=sys.stderr)
        return 1

    stale = [sid for sid, e in labs.items()
             if not (e.get("run") and e["run"][0] == NB_MARKER)]
    if a.check:
        if stale:
            print(f"::error::{len(stale)} lab block(s) still point at a path that may "
                  f"not exist: {stale[:8]}\nRun: python3 scripts/relink_labs.py",
                  file=sys.stderr)
            return 1
        print(f"ok: all {len(labs)} lab blocks lead with a runnable notebook")
        return 0

    for sid, entry in labs.items():
        rewrite(entry, sid)
    doc["_conventions"] = doc.get("_conventions", "")
    LABS_PATH.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(f"rewrote {len(stale)} of {len(labs)} lab blocks to lead with the notebook")
    return 0


if __name__ == "__main__":
    sys.exit(main())
