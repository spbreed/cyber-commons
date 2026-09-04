#!/usr/bin/env python3
"""Execute every lesson notebook and record what actually happened.

This is the evidence step. A notebook that has never been run is a claim, and
this repository does not ship claims — `labs/notebooks/_results.json` is written
from real execution and committed alongside the notebooks.

    python3 scripts/run_notebooks.py                # run all 104
    python3 scripts/run_notebooks.py --session A2.5 # run one
    python3 scripts/run_notebooks.py --quiet        # summary only

Execution model: each notebook's code cells are concatenated in order and run in
a fresh subprocess with a clean namespace, which is what a Jupyter kernel does
for a top-to-bottom "Run All" — the only mode these notebooks claim to support.
Using a subprocess rather than jupyter/nbclient keeps this dependency-free, so
the evidence step itself needs no packages the labs don't.

Exit status is non-zero if any notebook fails, so CI can gate on it.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "labs" / "notebooks"
RESULTS = NB_DIR / "_results.json"


def code_of(nb: dict) -> str:
    """The notebook's code cells, concatenated in order."""
    out = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        out.append("".join(cell["source"]))
    return "\n\n".join(out)


# The shared skill runtime, the way Kaggle provides it. On Kaggle it is an
# attached utility script already on the path; locally it is a file in the
# repository, so put it there before the notebook imports it.
RUNTIME_DIR = ROOT / "skills" / "_runtime"


def _env() -> dict:
    import os
    path = os.environ.get("PYTHONPATH", "")
    return dict(os.environ,
                PYTHONPATH=f"{RUNTIME_DIR}{os.pathsep}{path}" if path else str(RUNTIME_DIR))


def run_one(path: Path, timeout: int = 120) -> dict:
    nb = json.loads(path.read_text())
    src = code_of(nb)
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-c", src], cwd=ROOT, env=_env(),
                       capture_output=True, text=True, timeout=timeout)
    elapsed = time.monotonic() - t0
    return {
        "session": path.stem,
        "ok": p.returncode == 0,
        "returncode": p.returncode,
        "seconds": round(elapsed, 2),
        "stdout_lines": len(p.stdout.splitlines()),
        "stdout_chars": len(p.stdout),
        # keep the tail of stderr only on failure — enough to diagnose, not a dump
        "error": "" if p.returncode == 0 else p.stderr.strip()[-1200:],
        "code_cells": sum(1 for c in nb["cells"] if c["cell_type"] == "code"),
        "markdown_cells": sum(1 for c in nb["cells"] if c["cell_type"] == "markdown"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="run a single session id, e.g. A2.5")
    ap.add_argument("--quiet", action="store_true", help="summary only")
    ap.add_argument("--timeout", type=int, default=120, help="seconds per notebook")
    a = ap.parse_args()

    paths = ([NB_DIR / f"{a.session}.ipynb"] if a.session
             else sorted(NB_DIR.glob("*.ipynb")))
    missing = [p for p in paths if not p.is_file()]
    if missing:
        print(f"no such notebook: {missing[0]}", file=sys.stderr)
        return 1

    results, failed = [], []
    for p in paths:
        try:
            r = run_one(p, a.timeout)
        except subprocess.TimeoutExpired:
            r = {"session": p.stem, "ok": False, "returncode": -1,
                 "seconds": a.timeout, "stdout_lines": 0, "stdout_chars": 0,
                 "error": f"timed out after {a.timeout}s",
                 "code_cells": 0, "markdown_cells": 0}
        results.append(r)
        if not r["ok"]:
            failed.append(r)
        if not a.quiet:
            mark = "ok  " if r["ok"] else "FAIL"
            print(f"{mark} {r['session']:8s} {r['seconds']:>6.2f}s  "
                  f"{r['stdout_lines']:>4d} lines out")
            if not r["ok"]:
                print("     " + r["error"].replace("\n", "\n     ")[:900])

    total = len(results)
    passed = total - len(failed)
    summary = {
        "generated_by": "scripts/run_notebooks.py",
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "notebooks": total,
        "passed": passed,
        "failed": len(failed),
        "total_seconds": round(sum(r["seconds"] for r in results), 2),
        "total_output_lines": sum(r["stdout_lines"] for r in results),
        "results": results,
    }
    # only rewrite the committed evidence on a full run
    if not a.session:
        RESULTS.write_text(json.dumps(summary, indent=1) + "\n")

    print(f"\n{passed}/{total} notebooks executed cleanly in "
          f"{summary['total_seconds']}s, producing "
          f"{summary['total_output_lines']} lines of real output")
    if failed:
        print(f"{len(failed)} FAILED: {[r['session'] for r in failed]}", file=sys.stderr)
        return 1
    if not a.session:
        print(f"evidence written to {RESULTS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
