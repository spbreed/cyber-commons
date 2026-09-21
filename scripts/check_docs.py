#!/usr/bin/env python3
"""Check every Markdown file in the repository against the tree it describes.

`check_claims.py` covers the counted claims in a handful of documents and
`check_claude_md.py` covers CLAUDE.md's structure. Nothing covered the other
fifty-odd Markdown files, and they had rotted in exactly the ways you would
expect — each one found by hand, which is the argument for this file existing:

- **`lessons/README.md`** pointed every example at `spbreed.github.io`, which is
  not where the site lives, and used `M0.2` from an id scheme retired long ago.
- **`labs/incident-register/README.md`** linked three times to
  `../notebooks/C2.8.ipynb`, a lesson removed in the Function D trim.
- **`labs/b2.10-eval-harness/README.md`** linked to `../../docs/…` from inside
  the lab, which resolves to a `docs/` at the repository root that has never
  existed, and to `curriculum/track-c2.md` for a chapter that is now D1.
- **`MODELS.md`** ended on `[Open an issue](../../issues)` — a GitHub-relative
  path that only works in the web UI and resolves nowhere in a clone.

Four rules, all objective:

1. **Every relative link resolves.** A link to a file that is not there is the
   cheapest kind of wrong to detect and the most annoying to hit.
2. **No link points at a retired lesson.** Lesson ids are renumbered; a doc
   still naming the old one reads as authoritative and is not.
3. **Every `scripts/*.py` a doc names exists.**
4. **The site is cited at its own domain.** `spbreed.github.io/cyber-commons`
   still resolves, so nothing breaks loudly — the links simply stop being the
   canonical ones, and a reader who copies them spreads the wrong host.

    python3 scripts/check_docs.py            # report
    python3 scripts/check_docs.py --check    # CI: non-zero on any problem
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
LESSON_IDS = {s["id"] for f in CUR["functions"] for t in f["tracks"]
              for s in t["sessions"]}

# Vendored third-party trees. Their docs describe their own projects and are not
# ours to correct; scanning them produces noise that gets the gate switched off.
SKIP_PREFIXES = ("labs/tools/",)

SITE = "cybercommons.ai"
STALE_HOSTS = ("spbreed.github.io",)

LINK = re.compile(r"\]\(([^)]+)\)")
NOTEBOOK = re.compile(r"notebooks/([A-E]\d+\.\d+)\.ipynb")
# Only *our* scripts/ directory. Without the lookbehind this also matches
# "cybergym/scripts/verify_agent_result.py", which belongs to a third-party
# repository the reader clones — a real script, just not one of ours, and
# flagging it teaches people to ignore the gate.
SCRIPT = re.compile(r"(?<![\w/])scripts/([a-z_0-9]+\.py)")


def tracked_python() -> set[str]:
    """Basenames of every Python file git knows about.

    Computed once. An `rglob` per script name per document walks the vendored
    virtualenvs under `labs/tools/` thousands of times over and takes this gate
    from under a second to over two minutes, which is how a gate gets removed.
    """
    out = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return {Path(p).name for p in out}


PY_FILES = tracked_python()


def markdown_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return [p for p in out if not p.startswith(SKIP_PREFIXES)]


def check(rel: str) -> list[str]:
    text = (ROOT / rel).read_text(errors="ignore")
    here = (ROOT / rel).parent
    problems = []

    # Links are found in prose only. `AGENTS[intent](message, session)` is
    # Python inside backticks, and reading it as a link failed a generated
    # lesson reference over code that is correct.
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    prose = re.sub(r"`[^`\n]*`", "", prose)

    for m in LINK.finditer(prose):
        target = m.group(1).strip()
        # A bare fragment, an absolute URL, or an HTML-ish target is not ours.
        if target.startswith(("http", "mailto", "#", "<", "data:")):
            continue
        path = target.split("#")[0]
        if not path:
            continue
        if not (here / path).exists():
            problems.append(f"links to {target}, which does not exist")

    for sid in sorted(set(NOTEBOOK.findall(text))):
        if sid not in LESSON_IDS:
            problems.append(f"links to notebook {sid}, which is not a lesson "
                            f"any more")

    for s in sorted(set(SCRIPT.findall(text))):
        if not (ROOT / "scripts" / s).is_file() and s not in PY_FILES:
            problems.append(f"names scripts/{s}, which does not exist")

    for host in STALE_HOSTS:
        if host in text:
            problems.append(f"cites {host} rather than {SITE}")

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit non-zero on drift")
    a = ap.parse_args()

    files = markdown_files()
    total = 0
    for rel in files:
        for p in check(rel):
            print(f"  FAIL  {rel}: {p}")
            total += 1

    print(f"\n{len(files)} markdown file(s) checked · {len(LESSON_IDS)} lesson "
          f"id(s) known · {total} problem(s)")
    if a.check and total:
        print(f"::error::{total} problem(s) in the repository's markdown",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
