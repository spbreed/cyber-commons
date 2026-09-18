#!/usr/bin/env python3
"""Materialise `cybertravels/` as it stood at the end of any lesson.

    python3 scripts/checkpoint.py --at G1.4 --out ./my-cybertravels
    python3 scripts/checkpoint.py --list            # every checkpoint, in order
    python3 scripts/checkpoint.py --at G1.4 --diff  # what that one lesson added
    python3 scripts/checkpoint.py --check           # CI: the four gates below

A reader who opens the commons at D2.3 needs the system as it stood after
D2.2 — everything taught so far, nothing taught later. Handing them the
finished tree spoils every exercise between here and the end; handing them a
bare repository makes the lesson unrunnable.

**The finished tree is the source of truth, and checkpoints are derived from
it.** That is forced rather than chosen: ten skills scan `cybertravels/` and
`check_labels.py` holds the ground-truth key to it, so the complete tree has to
exist on master. Per-lesson patch files would invert that and rot the first
time an early lesson changed.

## How a file says when it appeared

One magic comment near the top:

    # step:file G1.4

The file does not exist in any checkpoint before that lesson.

## How a block says when it appeared

Four markers. `add` introduces something; `was`/`now` replaces one thing with
another; `end` closes either.

    # step:G1.4 was
    #~ token = DEV_TOKEN          # one long-lived token, every scope
    # step:G1.4 now
    ex = identity.token_exchange(user, agent, audience, scope)
    token = ex["access_token"]
    # step:G1.4 end

**Every line of a `was` region is commented out with `#~`,** and the
materialiser strips that prefix when it emits one. This is not cosmetic and it
is the thing the design got wrong first: the committed tree has to be the tree
that runs and the tree the scanners read, so both branches cannot be live code
in it. Leave them live and the naive assignment executes immediately before the
real one, referencing names that do not exist yet — the application breaks, and
it breaks in the file the whole commons is about.

**`was` is not scaffolding.** The naive branch is what Function A attacks: a
reader at A1.2 gets the ingress with no provenance, so the injection actually
works, and A2.6 flips the region so it stops working. The vulnerability is real
at that checkpoint rather than described, which is the whole reason for
building this instead of shipping one finished tree.

## The four gates `--check` runs

1. **The last checkpoint is byte-identical to the committed tree.** The
   load-bearing one. Without it the markers drift out of step with the code and
   nothing says so — every other gate would still pass while the checkpoints
   quietly described a system that no longer exists.
2. **Every checkpoint parses.** A checkpoint that does not is a lesson whose
   increment was not a clean one.
3. **Every id in a marker is a real lesson id**, and markers are balanced.
4. **A `was` region is never empty, and every line in one is `#~`-commented.**
   Empty means "this did not exist before", which is what `add` says. An
   uncommented line means the committed tree is running code it should not be.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / "cybertravels"

sys.path.insert(0, str(ROOT / "scripts"))

# `# step:file G1.4` — anywhere in the first 40 lines. The HTML form is
# accepted too: the operator console is a file that appears at a lesson like
# any other, and a marker syntax that only worked in Python would have silently
# left it present from the first checkpoint.
FILE_RE = re.compile(
    r"^\s*(?:#|<!--)\s*step:file\s+([A-Z]\d+\.\d+)\s*(?:-->)?\s*$", re.M)
# `# step:G1.4 was|now|add|end`, on its own line, any indentation.
BLOCK_RE = re.compile(r"^[ \t]*#\s*step:([A-Z]\d+\.\d+)\s+(was|now|add|end)\s*$")

# `#~ ` prefixes every line of a `was` region so the committed tree never runs
# it. The materialiser takes the prefix off when it emits the naive branch.
WAS_LINE = re.compile(r"^([ \t]*)#~ ?")
UNCOMMENT = re.compile(r"^([ \t]*)#~ ?")

# Files with no marker are present from the first checkpoint. That is the right
# default: data fixtures, .gitignore and requirements.txt are not taught, they
# are just there.
ALWAYS = "—"


def lesson_order() -> list[str]:
    """Every lesson id, in curriculum order. The spine of everything here."""
    cur = json.loads((ROOT / "site/data/curriculum.json").read_text())
    return [s["id"] for f in cur["functions"] for t in f["tracks"]
            for s in t["sessions"]]


def sources() -> list[Path]:
    return sorted(p for p in TREE.rglob("*")
                  if p.is_file()
                  and "__pycache__" not in p.parts
                  and p.suffix not in (".db", ".pyc"))


def introduced_in(path: Path) -> str:
    """The lesson that creates this file, or ALWAYS."""
    try:
        head = "\n".join(path.read_text().splitlines()[:40])
    except UnicodeDecodeError:
        return ALWAYS
    m = FILE_RE.search(head)
    return m.group(1) if m else ALWAYS


def materialise(text: str, have: set[str]) -> str:
    """Strip every region belonging to a lesson not in `have`."""
    out, mode = [], None
    for line in text.splitlines(keepends=True):
        m = BLOCK_RE.match(line.rstrip("\n"))
        if m:
            sid, kind = m.groups()
            mode = None if kind == "end" else (sid, kind)
            continue
        if mode is None:
            out.append(line)
            continue
        sid, kind = mode
        done = sid in have
        if kind in ("now", "add") and done:
            out.append(line)
        elif kind == "was" and not done:
            out.append(UNCOMMENT.sub(r"\1", line, count=1))
    return "".join(out)


def strip_file_marker(text: str) -> str:
    """Remove the marker line entirely, newline included."""
    return re.sub(r"^\s*(?:#|<!--)\s*step:file\s+[A-Z]\d+\.\d+\s*(?:-->)?\s*\n",
                  "", text, count=1, flags=re.M)


def build(at: str, order: list[str]) -> dict[str, str]:
    """{relative path: contents} for the tree as it stood at the end of `at`."""
    if at not in order:
        raise SystemExit(f"no such lesson: {at}")
    have = set(order[:order.index(at) + 1])
    tree: dict[str, str] = {}
    for p in sources():
        rel = str(p.relative_to(TREE))
        born = introduced_in(p)
        if born != ALWAYS and born not in have:
            continue
        try:
            text = p.read_text()
        except UnicodeDecodeError:
            tree[rel] = None          # binary: copied verbatim
            continue
        tree[rel] = strip_file_marker(materialise(text, have))
    return tree


def write(tree: dict[str, str], out: Path) -> int:
    if out.exists():
        shutil.rmtree(out)
    n = 0
    for rel, text in sorted(tree.items()):
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            shutil.copyfile(TREE / rel, dst)
        else:
            dst.write_text(text)
        n += 1
    return n


# --------------------------------------------------------------------------- #
# the gates
# --------------------------------------------------------------------------- #
def check(order: list[str]) -> list[str]:
    problems: list[str] = []
    known = set(order)

    # 3 — ids are real, markers balance, and a `was` is never empty
    for p in sources():
        try:
            lines = p.read_text().splitlines()
        except UnicodeDecodeError:
            continue
        rel = p.relative_to(TREE)
        born = introduced_in(p)
        if born != ALWAYS and born not in known:
            problems.append(f"{rel}: step:file names {born}, which is not a lesson")
        open_at, body = None, 0
        for i, line in enumerate(lines, 1):
            m = BLOCK_RE.match(line)
            if not m:
                if open_at:
                    body += 1
                    if open_at[1] == "was" and line.strip() and \
                            not WAS_LINE.match(line):
                        problems.append(
                            f"{rel}:{i}: a `was` line is not commented with "
                            f"`#~` — the committed tree would run the naive "
                            f"branch as well as the real one")
                continue
            sid, kind = m.groups()
            if sid not in known:
                problems.append(f"{rel}:{i}: step:{sid} is not a lesson id")
            if kind == "end":
                if open_at is None:
                    problems.append(f"{rel}:{i}: `end` with nothing open")
                open_at = None
            else:
                if open_at and open_at[1] == "was" and body == 0:
                    problems.append(
                        f"{rel}:{open_at[0]}: empty `was` region — use `add`, "
                        f"which is what \"it did not exist before\" means")
                if open_at and kind == "add":
                    problems.append(f"{rel}:{i}: `add` inside an open region")
                open_at, body = (i, kind), 0
        if open_at:
            problems.append(f"{rel}:{open_at[0]}: region never closed")

    # 1 — the last checkpoint IS the committed tree, minus the markers
    #
    # `expected` is computed by a deliberately dumb second pass rather than by
    # calling materialise(), so this compares two implementations of the same
    # rule instead of comparing materialise() with itself. A gate that asserts
    # a function equals itself passes forever and protects nothing.
    def expected(text: str) -> str:
        keep, drop = [], False
        for line in text.splitlines(keepends=True):
            m = BLOCK_RE.match(line.rstrip("\n"))
            if m:
                drop = m.group(2) == "was"
                continue
            if FILE_RE.match(line.rstrip("\n")):
                continue
            if not drop:
                keep.append(line)
        return "".join(keep)

    final = build(order[-1], order)
    for p in sources():
        rel = str(p.relative_to(TREE))
        if rel not in final:
            problems.append(f"{rel}: absent from the final checkpoint — its "
                            f"step:file names a lesson that never runs")
            continue
        if final[rel] is None:
            continue
        want = expected(p.read_text())
        if final[rel] != want:
            d = list(difflib.unified_diff(
                want.splitlines(), final[rel].splitlines(),
                "committed", "materialised", lineterm="", n=1))[:8]
            problems.append(f"{rel}: the final checkpoint is not the committed "
                            f"tree:\n      " + "\n      ".join(d))

    # 2 — every checkpoint parses
    for sid in order:
        tree = build(sid, order)
        for rel, text in tree.items():
            if text is None or not rel.endswith(".py"):
                continue
            try:
                ast.parse(text)
            except SyntaxError as e:
                problems.append(f"checkpoint {sid}: {rel} does not parse "
                                f"(line {e.lineno}: {e.msg}) — the increment "
                                f"for this lesson is not a clean one")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--at", help="lesson id, e.g. G1.4")
    ap.add_argument("--out", type=Path, help="where to write the checkpoint")
    ap.add_argument("--list", action="store_true",
                    help="every checkpoint and what it adds")
    ap.add_argument("--diff", action="store_true",
                    help="with --at: what that one lesson changed")
    ap.add_argument("--check", action="store_true", help="CI: run the gates")
    a = ap.parse_args()

    order = lesson_order()

    if a.check:
        problems = check(order)
        for p in problems:
            print(f"  FAIL  {p}")
        touched = {sid for p in sources() if p.suffix == ".py"
                   for sid, _ in BLOCK_RE.findall("") or []}
        marked = sum(1 for p in sources() if introduced_in(p) != ALWAYS)
        print(f"\n{len(order)} checkpoint(s) · {len(sources())} file(s) · "
              f"{marked} with a step:file marker · {len(problems)} problem(s)")
        if problems:
            print(f"::error::{len(problems)} checkpoint problem(s)",
                  file=sys.stderr)
            return 1
        return 0

    if a.list:
        prev: dict[str, str] = {}
        for sid in order:
            tree = build(sid, order)
            added = sorted(set(tree) - set(prev))
            changed = sorted(r for r in set(tree) & set(prev)
                             if tree[r] != prev[r])
            if added or changed:
                bits = []
                if added:
                    bits.append("+ " + ", ".join(added))
                if changed:
                    bits.append("~ " + ", ".join(changed))
                print(f"  {sid:<7} {' · '.join(bits)}")
            prev = tree
        return 0

    if not a.at:
        ap.error("choose --at, --list or --check")

    if a.diff:
        i = order.index(a.at)
        before = build(order[i - 1], order) if i else {}
        after = build(a.at, order)
        for rel in sorted(set(before) | set(after)):
            b, c = before.get(rel), after.get(rel)
            if b == c:
                continue
            for line in difflib.unified_diff(
                    (b or "").splitlines(), (c or "").splitlines(),
                    f"a/{rel}", f"b/{rel}", lineterm=""):
                print(line)
        return 0

    if not a.out:
        ap.error("--at needs --out (or --diff)")
    tree = build(a.at, order)
    n = write(tree, a.out)
    print(f"{n} file(s) written to {a.out} — cybertravels as it stood at the "
          f"end of {a.at}.\nEverything taught up to here, and nothing taught "
          f"after it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
