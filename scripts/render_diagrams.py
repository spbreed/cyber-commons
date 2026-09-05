#!/usr/bin/env python3
"""Render every diagram a skill emits with the real Graphviz and PlantUML, and check the result is worth looking at.

A skill emits diagram **source** — DOT or PlantUML — because source is text, so
the skill stays standard library only and runs on a Kaggle kernel with nothing
installed. This turns that source into SVG using the actual binaries, which is
the half that needs a machine with tools on it.

    python3 scripts/render_diagrams.py            # render and validate
    python3 scripts/render_diagrams.py --check    # CI: fail if any is stale

Output goes to `site/assets/diagrams/<stem>.svg`, which the lesson pages embed,
alongside `<stem>.dot` or `<stem>.puml` — the emitted source, committed so that
`--check` can tell whether a skill's diagram changed. Staleness is measured on
that source and never on the SVG: the source is deterministic and the render is
not, because a different Graphviz or PlantUML lays the same graph out
differently. Comparing rendered bytes failed CI on a diagram that was correct on
both machines.

**Validation is the point, not the rendering.** `dot` exits 0 on a graph that
renders as a single unreadable smear, and PlantUML writes a PNG containing the
words "syntax error" and exits 0 while doing it. So every render is checked
against properties a broken one fails:

  * the renderer exited 0 and wrote a file;
  * the SVG contains at least as many `<text>` elements as the source has
    labels — a node that rendered without its label is the commonest silent
    failure;
  * PlantUML output does not contain the string "syntax error", which is how
    that tool reports a problem;
  * the canvas is neither degenerate nor enormous: between 120 and 4000 px on
    each side, so a diagram that collapsed to nothing or sprawled off the page
    is caught;
  * no label is clipped by its own node box, checked by comparing the text
    length against the box width Graphviz allotted it.

A diagram that fails any of those is reported with the reason, and `--check`
fails CI on it.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OUT = ROOT / "site" / "assets" / "diagrams"
RUNTIME = SKILLS / "_runtime"

SVG_NS = "{http://www.w3.org/2000/svg}"
MIN_PX, MAX_PX = 120, 4000

# A skill announces a diagram by printing this marker, then the source.
MARKER = re.compile(r"^\[diagram:(dot|puml):([a-z0-9-]+)\]$", re.M)


def emitted() -> list[tuple[str, str, str, str]]:
    """(skill_ref, kind, stem, source) for every diagram every skill prints."""
    found = []
    for script in sorted(SKILLS.rglob("scripts/*.py")):
        ref = str(script.relative_to(SKILLS).parent.parent)
        p = subprocess.run([sys.executable, str(script)], capture_output=True,
                           text=True, env={"PATH": "/usr/bin:/bin",
                                           "PYTHONPATH": str(RUNTIME),
                                           "PYTHONHASHSEED": "0"})
        out = p.stdout
        marks = list(MARKER.finditer(out))
        for i, m in enumerate(marks):
            start = m.end() + 1
            end = marks[i + 1].start() if i + 1 < len(marks) else len(out)
            body = out[start:end]
            # The source ends at the renderer's own terminator; anything the
            # skill printed after it is prose, not diagram.
            if m.group(1) == "dot":
                body = body[:body.rindex("}") + 1] if "}" in body else body
            else:
                body = body[:body.rindex("@enduml") + 7] if "@enduml" in body else body
            found.append((ref, m.group(1), m.group(2), body))
    return found


def render(kind: str, stem: str, source: str) -> tuple[Path | None, str]:
    """Render with the real binary. Returns (path, error)."""
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{stem}.svg"
    if kind == "dot":
        p = subprocess.run(["dot", "-Tsvg", "-o", str(dst)], input=source,
                           capture_output=True, text=True)
    else:
        # A temp name, not "<stem>.puml": that path is the committed source
        # and plantuml's input file is deleted after the run, which quietly
        # removed the very file --check compares against.
        src = OUT / f".{stem}.render.puml"
        src.write_text(source)
        p = subprocess.run(["plantuml", "-tsvg", "-o", str(OUT), str(src)],
                           capture_output=True, text=True)
        rendered = OUT / f".{stem}.render.svg"
        if rendered.is_file():
            rendered.replace(dst)
        src.unlink(missing_ok=True)
    if p.returncode:
        return None, f"{kind} exited {p.returncode}: {p.stderr.strip()[:160]}"
    if not dst.is_file() or dst.stat().st_size == 0:
        return None, f"{kind} exited 0 and wrote nothing"
    return dst, ""


def validate(path: Path, kind: str, source: str) -> list[str]:
    """Properties a diagram that is not worth looking at will fail."""
    problems = []
    svg = path.read_text()

    # PlantUML reports a problem by drawing it and exiting 0.
    if "syntax error" in svg.lower() or "cannot find" in svg.lower():
        problems.append("the renderer drew an error message instead of a diagram")

    if kind == "puml":
        # A line starting with an apostrophe is PlantUML's comment syntax. A
        # note that opens on a quoted phrase is silently deleted from the
        # diagram — valid SVG, exit 0, sentence gone. Caught here because no
        # amount of looking at the render tells you a line is missing unless
        # you already knew it should be there.
        for i, ln in enumerate(source.splitlines(), 1):
            if ln.lstrip().startswith("'"):
                problems.append(f"line {i} starts with an apostrophe, which "
                                f"PlantUML treats as a comment and drops: "
                                f"{ln.strip()[:60]}")

    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        return problems + [f"the SVG does not parse: {e}"]

    def px(v):
        return float(re.sub(r"[^0-9.]", "", v or "0") or 0)

    w, h = px(root.get("width")), px(root.get("height"))
    if not (MIN_PX <= w <= MAX_PX and MIN_PX <= h <= MAX_PX):
        problems.append(f"canvas is {w:.0f}x{h:.0f}px, outside "
                        f"{MIN_PX}-{MAX_PX} — collapsed or sprawling")

    texts = [t for t in root.iter(f"{SVG_NS}text") if (t.text or "").strip()]
    if kind == "dot":
        # Every node and edge label in the source should have arrived. A node
        # rendered without its text is the commonest silent failure and the
        # SVG is perfectly valid without it.
        wanted = len(re.findall(r'label="([^"]+)"', source))
        if len(texts) < wanted:
            problems.append(f"{wanted} labels in the source, {len(texts)} "
                            f"<text> elements in the SVG — some did not render")
    elif len(texts) < 2:
        problems.append(f"only {len(texts)} text elements — the diagram is empty")

    # Clipping: Graphviz sizes a box to its label, so a node box narrower than
    # its own text means the label was not measured and will overflow. Only
    # node groups — an edge's arrowhead is a legitimately tiny polygon, and
    # scanning every polygon flags all of them.
    for g in root.iter(f"{SVG_NS}g"):
        if g.get("class") != "node":
            continue
        label = next((t.text or "" for t in g.iter(f"{SVG_NS}text")), "")
        for shape in list(g.iter(f"{SVG_NS}polygon")) + list(g.iter(f"{SVG_NS}path")):
            pts = shape.get("points") or shape.get("d", "")
            xs = [float(n) for n in re.findall(r"-?\d+\.?\d*", pts)][::2]
            if len(xs) < 3:
                continue
            box = max(xs) - min(xs)
            # ~6px per character at 11pt Helvetica, and Graphviz pads by ~8px.
            if label and box < len(label) * 5:
                problems.append(f"node {label!r} is {box:.0f}px wide for "
                                f"{len(label)} characters — the label is clipped")
            break
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="CI: fail on a stale or invalid diagram")
    a = ap.parse_args()

    for binary in ("dot", "plantuml"):
        if subprocess.run(["which", binary], capture_output=True).returncode:
            print(f"::error::{binary} is not installed. "
                  f"apt-get install graphviz plantuml", file=sys.stderr)
            return 1

    items = emitted()
    if not items:
        print("no skill emitted a diagram", file=sys.stderr)
        return 1

    bad, stale = [], []
    print(f"{len(items)} diagram(s) emitted by skills\n")
    for ref, kind, stem, source in items:
        # Staleness is measured on the SOURCE, not the render. The source is
        # what the skill emits and it is deterministic; the SVG is not, because
        # a different Graphviz or PlantUML lays the same graph out differently.
        # Comparing rendered bytes failed CI on a diagram that was correct on
        # both machines and merely 10 bytes apart.
        src_path = OUT / f"{stem}.{kind}"
        if not src_path.is_file() or src_path.read_text() != source:
            stale.append(stem)
            if not a.check:
                src_path.write_text(source)
        path, err = render(kind, stem, source)
        if err:
            print(f"  FAIL {stem:<34}{kind:<6}{err}")
            bad.append(stem)
            continue
        problems = validate(path, kind, source)
        size = path.stat().st_size
        if problems:
            print(f"  FAIL {stem:<34}{kind:<6}{size:>6}B  {ref}")
            for p in problems:
                print(f"       {p}")
            bad.append(stem)
        else:
            print(f"  ok   {stem:<34}{kind:<6}{size:>6}B  {ref}")

    print(f"\n{len(items) - len(bad)}/{len(items)} rendered and validated")
    if bad:
        print(f"::error::{len(bad)} diagram(s) did not render usefully: {bad}",
              file=sys.stderr)
        return 1
    if a.check and stale:
        print(f"::error::{len(stale)} diagram(s) whose committed source no "
              f"longer matches what the skill emits: {stale}\n"
              f"Run: python3 scripts/render_diagrams.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
