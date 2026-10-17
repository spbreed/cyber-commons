#!/usr/bin/env python3
"""Fail when markdown source reaches the reader as literal text.

    python3 scripts/check_rendered_markdown.py            # report
    python3 scripts/check_rendered_markdown.py --check     # non-zero on a hit

**Why this exists.** 78 of the 149 lesson pages were serving raw markdown in
visible prose — `**Anchor -> E1.0.**` on fifty Function E and F pages, a
grounding line reading ``You add `bind_call()` and a `cnf` claim`` with its
backticks on 39, and a list item wrapped over two source lines emitting as a
`<li>` plus a stray `<p>` with the sentence cut in half. Every page built
green, every other gate passed, and nothing read the rendered text.

Five causes, all now fixed in `build_site.py`: three emitters that escaped
markdown instead of rendering it (the anchor blockquote, the CyberTravels
grounding line, the lab line from `curriculum.json`), a bold rule whose
`[^*]+` could not span a nested `*emphasis*`, and list and blockquote loops
that consumed one source line per block.

This is the gate that would have caught all five, and it is deliberately dumb:
it strips tags and code blocks and looks at what is left. A gate that read the
source rather than the page is the vacuous kind this repository has been bitten
by before.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# `pre` and `code` are exempt: a backtick inside a shell comment or an HCL
# block is content, not a rendering failure. B3.2's `# No `egress` block`
# comment is the case that made this explicit.
STRIP = re.compile(r"<script.*?</script>|<style.*?</style>|<pre.*?</pre>"
                   r"|<code.*?</code>", re.S)

PATTERNS = [
    (r"\*\*[^*\n]{0,80}", "bold markers, unrendered"),
    (r"(?<![\w`])`[^`\n]{1,60}`(?![\w`])", "a code span, unrendered"),
    (r"^[ \t]*[-*][ \t]+\S", "a list bullet, unrendered"),
    (r"^[ \t]*#{1,4}[ \t]+\S", "a heading marker, unrendered"),
    (r"\[[^\]\n]{1,60}\]\([^)\n]{1,120}\)", "a link, unrendered"),
]


def visible(page: Path) -> str:
    t = STRIP.sub(" ", page.read_text())
    return html.unescape(re.sub(r"<[^>]+>", "\n", t))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="non-zero exit on any hit")
    a = ap.parse_args()

    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        print("no rendered pages — run python3 scripts/build_site.py first")
        return 1

    bad = 0
    for page in pages:
        text = visible(page)
        for pattern, why in PATTERNS:
            for m in re.finditer(pattern, text, re.M):
                bad += 1
                snippet = re.sub(r"\s+", " ", m.group(0))[:70]
                print(f"::error::{page.relative_to(ROOT)}: {why} — {snippet!r}",
                      file=sys.stderr)

    if bad:
        print(f"\n{bad} fragment(s) of markdown reaching the reader across "
              f"{len(pages)} page(s)")
        return 1 if a.check else 0
    print(f"{len(pages)} page(s) rendered · no markdown source in visible text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
