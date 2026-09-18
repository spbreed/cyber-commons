#!/usr/bin/env python3
"""Prove the skill harness prints the same thing on every machine.

**What this can and cannot cover.** Every skill in this commons is executed by
a model, and a model is not deterministic — so this does not, and must not,
claim that a lesson's findings reproduce byte for byte. Saying otherwise would
be the most misleading thing in the repository.

What it checks is the half that *is* ours: the harness. With no model
available every skill refuses, legibly and in a fixed form, and that refusal
has to be identical across runs. A refusal that varies means something
unordered reached the message — a set iterated into a sort, a dict printed
directly, an address in a repr — and the same defect would make every real
result undiffable too.

Each script is run under several `PYTHONHASHSEED` values, which is what
surfaces it: Python randomises string hashing per process, so a set or a dict
built from strings iterates differently on every run unless something orders
it.

    python3 scripts/check_determinism.py             # every skill, 3 seeds
    python3 scripts/check_determinism.py --seeds 4
    python3 scripts/check_determinism.py --skill grc/control-evidence
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / "skills" / "_runtime"


def scripts() -> list[Path]:
    return sorted(ROOT.glob("skills/*/*/scripts/*.py"))


def ref(p: Path) -> str:
    return f"{p.parents[2].name}/{p.parents[1].name}"


def outputs(path: Path, seeds: list[str], timeout: int) -> list[str]:
    """stdout once per hash seed, in seed order."""
    out = []
    for seed in seeds:
        prev = os.environ.get("PYTHONPATH", "")
        # CLAUDE_CLI=0 and no endpoint: this gate is about the refusal, which
        # is deterministic. With a model reachable every run would differ and
        # the check would be measuring the model instead of the harness.
        env = dict(os.environ, PYTHONHASHSEED=seed, CLAUDE_CLI="0",
                   PYTHONPATH=f"{RUNTIME}{os.pathsep}{prev}" if prev else str(RUNTIME))
        for k in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL"):
            env.pop(k, None)
        p = subprocess.run([sys.executable, str(path)], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=timeout)
        # Exit 2 with the refusal is the expected outcome here, not a failure.
        if p.returncode not in (0, 2):
            raise RuntimeError(f"exited {p.returncode} under PYTHONHASHSEED="
                               f"{seed}: {p.stderr.strip()[-400:]}")
        out.append(p.stdout)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--skill", help="one skill, e.g. grc/control-evidence")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    paths = scripts()
    if a.skill:
        paths = [p for p in paths if ref(p) == a.skill]
        if not paths:
            sys.exit(f"no such skill: {a.skill}")

    seeds = [str(s) for s in range(a.seeds)]
    if not a.quiet:
        print(f"checking {len(paths)} skill(s) under {len(seeds)} hash seeds "
              f"— the no-model refusal, which is the deterministic half\n")

    varied, broken = [], []
    for p in paths:
        try:
            outs = outputs(p, seeds, a.timeout)
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            broken.append(ref(p))
            print(f"  FAIL {ref(p):48s} {str(e)[:90]}")
            continue
        if len(set(outs)) == 1:
            if not a.quiet:
                print(f"  ok   {ref(p):48s} identical across {len(seeds)} seeds")
        else:
            varied.append(ref(p))
            first = next((i for i, (x, y) in
                          enumerate(zip(outs[0].splitlines(), outs[1].splitlines()))
                          if x != y), 0)
            print(f"  VARY {ref(p):48s} first differs at line {first + 1}")

    ok = len(paths) - len(varied) - len(broken)
    print(f"\n{ok}/{len(paths)} skills are deterministic across "
          f"{len(seeds)} hash seeds")
    if varied:
        print(f"::error::output varies between runs: {varied}", file=sys.stderr)
    if broken:
        print(f"::error::failed to run: {broken}", file=sys.stderr)
    return 1 if (varied or broken) else 0


if __name__ == "__main__":
    sys.exit(main())
