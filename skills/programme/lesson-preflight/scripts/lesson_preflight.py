#!/usr/bin/env python3
"""Prove that this host can fetch and execute a procedure that lives in the repository, by failing twice on purpose and then succeeding.

This is the executable half of the `lesson-preflight` skill: the check the
SKILL.md next to it describes, run against this repository's own skills tree —
which is the estate the check is about, so the numbers it prints are real
rather than synthetic.

Standard library only, and deterministic: it prints no path, no version and no
timestamp, so the bytes a Kaggle kernel produces are the bytes produced here
and `kaggle_verify.py` can compare the two.
"""

import os
import re
import subprocess
import sys
import zlib
from pathlib import Path

# Step 1 — locate the tree from the running file, never from the working
# directory. This file is at skills/programme/lesson-preflight/scripts/, so the
# repository root is four levels up. On Kaggle `cwd` is /kaggle/working and the
# clone is beside it; in a checkout `cwd` is wherever the reader happened to be.
# Neither matters here, which is the entire point.
ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / "skills"
RUNTIME = SKILLS / "_runtime"

# The procedure this preflight runs to prove the chain: A1.2's, the first
# executable lesson after this one.
DEMO = "skills/threats/instruction-channel-check/scripts/instruction_channel_check.py"
# Only the skills that import the shared runtime can demonstrate failure (b).
# This is one of them; A1.2's is self-contained and would succeed with no
# PYTHONPATH at all, which would teach the wrong lesson.
IMPORTER = "skills/grc/control-evidence/scripts/control_evidence.py"


def run(script, *, root, runtime):
    """Run a procedure the way a lesson cell does, with the two conditions as knobs."""
    env = dict(os.environ, PYTHONHASHSEED="0")
    env["PYTHONPATH"] = str(RUNTIME) if runtime else ""
    p = subprocess.run([sys.executable, os.path.join(root, script)],
                       capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr


def why(stderr):
    """The one line of a traceback worth printing, with every path removed.

    A preflight whose own output contains an absolute path cannot be compared
    between two hosts, which is the failure mode this skill warns about.
    """
    if "No such file or directory" in stderr:
        return "[Errno 2] No such file or directory"
    for line in reversed(stderr.strip().splitlines()):
        if line.startswith("ModuleNotFoundError"):
            return line.strip()
    return re.sub(r"[/\\][^\s'\"]+", "<path>", stderr.strip().splitlines()[-1])[:120]


# --------------------------------------------------------------- 2 · inventory
areas, skills, with_script = set(), 0, 0
for md in sorted(SKILLS.rglob("SKILL.md")):
    skills += 1
    areas.add(md.parent.parent.name)
    if list(md.parent.glob("scripts/*.py")):
        with_script += 1

# These counts are a function of the tree, not constants: adding a skill — or
# making one import the shared runtime — changes them, and a Kaggle kernel run
# before that change prints the older number until it is re-run. That is the
# check doing its job; it inventories what was actually fetched. The operational
# consequence is that A0.1 must be the LAST notebook pushed in any cycle, or it
# verifies against a tree that changed after its kernel ran. Both times this
# lesson has failed kaggle_verify, that was why.
print("the tree this host fetched")
print(f"  areas            : {len(areas)}")
print(f"  skills           : {skills}")
print(f"  with a script    : {with_script}")
print(f"  shared runtime   : {'present' if (RUNTIME / 'cyber_commons_skill_runtime.py').is_file() else 'MISSING'}")
print("  resolved from    : the running file, not the working directory")
print()

report = {"tree": {"areas": len(areas), "skills": skills,
                   "with_script": with_script,
                   "runtime_present": (RUNTIME / "cyber_commons_skill_runtime.py").is_file()},
          "failures": []}

# ------------------------------------------------- 3 · failure (a), not fetched
print("(a) the tree was never fetched  --  a host with no network")
rc, _, err = run(DEMO, root=str(ROOT / "no-such-clone"), runtime=True)
print(f"    exit {rc}: {why(err)}")
print("    Nothing ran. This is a fetch problem: on Kaggle, Internet is off in")
print("    the notebook settings, or the account is not phone-verified.")
report["failures"].append({"condition": "not-fetched", "exit_code": rc, "error": why(err)})
assert rc != 0, "a missing procedure must not exit zero"
print()

# ------------------------------------------- 4 · failure (b), library not found
print("(b) fetched, but the shared runtime is not on PYTHONPATH")
rc, _, err = run(IMPORTER, root=str(ROOT), runtime=False)
print(f"    exit {rc}: {why(err)}")
# Match an actual import statement, not the substring: this file mentions the
# module name in the line below, and a naive `in` check counted the counter.
importers = sum(
    1 for s in sorted(SKILLS.rglob("scripts/*.py"))
    if any(ln.startswith("from cyber_commons_skill" + "_runtime import")
           for ln in s.read_text().splitlines()))
print("    The file was there and the interpreter started. "
      f"{importers} of the skills")
print("    import the shared runtime rather than carrying a copy of it, and")
print("    the lesson cell is what puts it on the path.")
report["failures"].append({"condition": "no-runtime-on-path", "exit_code": rc, "error": why(err)})
assert rc != 0, "a missing import must not exit zero"
print()

# ------------------------------------------------ 5 · both true, and checksummed
print("(c) fetched, runtime on the path  --  the procedure runs")
rc, out, err = run(DEMO, root=str(ROOT), runtime=True)
body = out.strip().splitlines()
for line in body[:6]:
    print(f"    | {line}")
print(f"    | ... {max(0, len(body) - 6)} more lines")
print(f"    exit {rc} · {len(body)} lines · crc32 {zlib.crc32(out.encode()) & 0xFFFFFFFF:08x}")
report["run"] = {"script": DEMO, "lines": len(body),
                 "crc32": f"{zlib.crc32(out.encode()) & 0xFFFFFFFF:08x}",
                 "exit_code": rc}
assert rc == 0 and body, "a procedure that prints nothing has not run"
print()

report["ready"] = len(report["failures"]) == 2 and rc == 0
print(f"ready: {report['ready']}")
print()
print("Two of the three paths above are failures, and they are the two you will")
print("actually meet. A preflight that only shows (c) has tested one path in")
print("three and calls the host ready on the strength of it.")
