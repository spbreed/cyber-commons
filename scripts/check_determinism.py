#!/usr/bin/env python3
"""Prove every notebook prints the same thing on every machine.

A lesson is only evidence if the reader's run matches the one on the page. Two
notebooks shipped that did not, and neither failed locally, because a single
local pass runs every notebook under one interpreter with one hash seed:

  * B1.2 iterated a set difference into a stable sort. With tied scores the
    sort preserved set-iteration order, which PYTHONHASHSEED randomises.
  * D1.1 seeded a sampling RNG from hash(str), which PYTHONHASHSEED also
    randomises.

Both surfaced only when Kaggle ran them on a different machine. This script
makes that a local, cheap check instead: run each notebook under several
deliberately different hash seeds and require byte-identical stdout.

    python3 scripts/check_determinism.py            # all notebooks
    python3 scripts/check_determinism.py --session B1.2 --seeds 8

Exit status is non-zero if any notebook varies, so CI can gate on it.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "labs" / "notebooks"

# 0 disables randomisation entirely; the rest are arbitrary distinct seeds. A
# seed of 0 alone would hide exactly the bugs this script exists to catch.
SEEDS = ["0", "1", "12345", "99991", "524287", "7", "31337", "8191"]


def code_of(path: Path) -> str:
    nb = json.loads(path.read_text())
    return "\n\n".join("".join(c["source"]) for c in nb["cells"]
                       if c["cell_type"] == "code")


def outputs(path: Path, seeds: list[str], timeout: int) -> list[str]:
    """stdout of the notebook once per hash seed, in seed order."""
    src = code_of(path)
    out = []
    for seed in seeds:
        env = dict(os.environ, PYTHONHASHSEED=seed)
        p = subprocess.run([sys.executable, "-c", src], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=timeout)
        if p.returncode != 0:
            raise RuntimeError(f"exited {p.returncode} under PYTHONHASHSEED={seed}: "
                               f"{p.stderr.strip()[-400:]}")
        out.append(p.stdout)
    return out


def first_difference(a: str, b: str) -> str:
    """The first line where two runs disagree, quoted for a bug report."""
    al, bl = a.split("\n"), b.split("\n")
    for i, (x, y) in enumerate(zip(al, bl), 1):
        if x != y:
            return f"line {i}:\n    seed A: {x!r}\n    seed B: {y!r}"
    return f"one run has {len(al)} lines, the other {len(bl)}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="check a single session id, e.g. B1.2")
    ap.add_argument("--seeds", type=int, default=4,
                    help=f"how many hash seeds to try (max {len(SEEDS)}, default 4)")
    ap.add_argument("--timeout", type=int, default=120, help="seconds per run")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--quiet", action="store_true", help="report failures only")
    a = ap.parse_args()

    seeds = SEEDS[:max(2, min(a.seeds, len(SEEDS)))]
    paths = ([NB_DIR / f"{a.session}.ipynb"] if a.session
             else sorted(NB_DIR.glob("*.ipynb")))
    if missing := [p for p in paths if not p.is_file()]:
        sys.exit(f"no such notebook: {missing[0]}")

    print(f"checking {len(paths)} notebook(s) under {len(seeds)} hash seeds "
          f"({', '.join(seeds)})\n")

    varying, broken = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        futures = {pool.submit(outputs, p, seeds, a.timeout): p for p in paths}
        for fut in concurrent.futures.as_completed(futures):
            sid = futures[fut].stem
            try:
                runs = fut.result()
            except Exception as e:                              # noqa: BLE001
                broken.append(sid)
                print(f"  ERR  {sid:8s} {e}", file=sys.stderr)
                continue
            if len(set(runs)) == 1:
                if not a.quiet:
                    print(f"  ok   {sid:8s} identical across {len(seeds)} seeds")
                continue
            varying.append(sid)
            distinct = sorted(set(runs), key=runs.index)
            print(f"  VARY {sid:8s} {len(distinct)} distinct outputs — "
                  f"{first_difference(distinct[0], distinct[1])}", file=sys.stderr)

    print(f"\n{len(paths) - len(varying) - len(broken)}/{len(paths)} notebooks are "
          f"deterministic across {len(seeds)} hash seeds")
    if varying:
        print(f"::error::output depends on PYTHONHASHSEED: {varying}. Seed sampling "
              f"from zlib.crc32 rather than hash(), and give every sort a full "
              f"tiebreak so equal keys cannot reorder.", file=sys.stderr)
    if broken:
        print(f"::error::failed to run: {broken}", file=sys.stderr)
    return 1 if varying or broken else 0


if __name__ == "__main__":
    sys.exit(main())
