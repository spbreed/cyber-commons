#!/usr/bin/env python3
"""Check the incident control register against the curriculum it was split into.

`labs/incident-register/register.json` assigns each of the source report's forty
controls to a lesson. Three ways that can rot, and this catches all three:

1. **A control with no owner.** The whole point of the register is that every
   control is taught, tested and evidenced somewhere. An unassigned row is a
   sentence in a document.
2. **An owner that does not exist.** Lessons get renumbered; a register that
   still points at the old id is worse than no register.
3. **The register and the lesson disagreeing.** C2.8 embeds its own copy so the
   notebook stays self-contained, and a copy is a thing that drifts.

    python3 scripts/check_register.py            # report
    python3 scripts/check_register.py --check    # CI: non-zero on any problem
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

REG = json.loads((ROOT / "labs" / "incident-register" / "register.json").read_text())
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())

from exercises.incident import REGISTER as EMBEDDED  # noqa: E402

ROW = re.compile(r'\("(C\d+\.\d+)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    lessons = {s["id"] for f in CUR["functions"] for t in f["tracks"]
               for s in t["sessions"]}
    problems = []

    controls = REG["controls"]
    for c in controls:
        if not c.get("lesson"):
            problems.append(f"{c['id']}: no owning lesson")
        elif c["lesson"] not in lessons:
            problems.append(f"{c['id']}: owner {c['lesson']} is not a session id")

    # the copy embedded in C2.8, which is what a reader actually runs
    embedded = {m.group(1): (m.group(3), m.group(4), m.group(5))
                for m in ROW.finditer(EMBEDDED)}
    if set(embedded) != {c["id"] for c in controls}:
        only_file = sorted({c["id"] for c in controls} - set(embedded))
        only_nb = sorted(set(embedded) - {c["id"] for c in controls})
        problems.append(f"register.json and the C2.8 copy differ: "
                        f"only in the file {only_file}, only in the notebook {only_nb}")
    for c in controls:
        got = embedded.get(c["id"])
        want = (c["type"], c["nist"], c["lesson"])
        if got and got != want:
            problems.append(f"{c['id']}: notebook has {got}, register.json has {want}")

    for p in problems:
        print(f"  FAIL  {p}")

    by_fn = Counter(c["lesson"][0] for c in controls if c.get("lesson"))
    by_type = Counter(c["type"] for c in controls)
    print(f"\n{len(REG['rows'])} rows · {len(controls)} controls · "
          f"{len(problems)} problem(s)")
    print("  by function: " + "  ".join(f"{k}={v}" for k, v in sorted(by_fn.items())))
    print("  by type:     " + "  ".join(f"{k}={v}" for k, v in sorted(by_type.items())))

    if a.check and problems:
        print(f"::error::{len(problems)} problem(s) in the incident register",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
