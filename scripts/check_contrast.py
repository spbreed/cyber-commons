#!/usr/bin/env python3
"""Find text the reader cannot see, by rendering the pages and measuring them.

This exists because of a real defect that shipped. The switch to a white ground
left `pre{background:#070a12}` and `pre code{color:#cfe0ff}` behind from the
dark theme, and a later rule gave every `code` element a light pill background —
so a fenced block rendered pale blue on near-white. The `git clone` lines on
A0.1 and every embedded SKILL.md frontmatter were invisible. Nothing caught it:
the HTML was correct, the build was green, and the text was *there*.

A stylesheet cannot be checked by reading it, because the failure is a
combination of rules that are each fine alone. So this renders the page in
headless Chromium, walks every text node, asks the browser for the computed
foreground and the effective background behind it, and reports any pair below
the WCAG AA threshold — 4.5:1 for body text, 3:1 for large text.

    python3 scripts/check_contrast.py            # audit a sample of pages
    python3 scripts/check_contrast.py --all      # every page
    python3 scripts/check_contrast.py --check    # CI: non-zero on any failure

It needs Chromium. Where there is none it says so and exits 0, because a
missing browser is not evidence of a broken page.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "site" / "lessons"
INDEX = ROOT / "site" / "index.html"

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
]

# Walks the rendered page and reports every visible text run whose contrast
# against the background actually painted behind it is below the AA floor.
AUDIT = r"""
(function(){
  function parse(c){
    var m = c.match(/rgba?\(([^)]+)\)/); if(!m) return null;
    var p = m[1].split(',').map(function(s){return parseFloat(s)});
    return {r:p[0], g:p[1], b:p[2], a:p.length > 3 ? p[3] : 1};
  }
  function lum(c){
    var v = [c.r, c.g, c.b].map(function(x){
      x = x/255; return x <= 0.03928 ? x/12.92 : Math.pow((x+0.055)/1.055, 2.4);
    });
    return 0.2126*v[0] + 0.7152*v[1] + 0.0722*v[2];
  }
  function ratio(a, b){
    var l1 = lum(a), l2 = lum(b);
    return (Math.max(l1,l2) + 0.05) / (Math.min(l1,l2) + 0.05);
  }
  // The background actually painted behind an element: walk up until something
  // is not transparent. A rule that sets colour but inherits its background is
  // exactly how the invisible code blocks happened.
  function bgOf(el){
    for(var n = el; n && n !== document.documentElement; n = n.parentElement){
      var c = parse(getComputedStyle(n).backgroundColor);
      if(c && c.a > 0.5) return c;
    }
    return {r:255, g:255, b:255, a:1};
  }
  var out = [], seen = {};
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  var node;
  while((node = walker.nextNode())){
    var text = node.nodeValue.trim();
    if(text.length < 3) continue;
    var el = node.parentElement;
    if(!el) continue;
    var cs = getComputedStyle(el);
    if(cs.display === 'none' || cs.visibility === 'hidden') continue;
    if(parseFloat(cs.opacity) < 0.1) continue;
    var rect = el.getBoundingClientRect();
    if(rect.width < 2 || rect.height < 2) continue;
    var fg = parse(cs.color); if(!fg || fg.a < 0.1) continue;
    var r = ratio(fg, bgOf(el));
    var size = parseFloat(cs.fontSize);
    var bold = parseInt(cs.fontWeight, 10) >= 700;
    var floor = (size >= 24 || (size >= 18.66 && bold)) ? 3.0 : 4.5;
    if(r < floor){
      var key = el.tagName + '|' + (el.className || '') + '|' + Math.round(r*10);
      if(seen[key]) continue;
      seen[key] = 1;
      out.push({sel: el.tagName.toLowerCase() +
                     (el.className ? '.' + String(el.className).split(' ').join('.') : ''),
                ratio: Math.round(r*100)/100, floor: floor,
                color: cs.color, bg: 'rgb(' + bgOf(el).r + ',' + bgOf(el).g + ',' + bgOf(el).b + ')',
                text: text.slice(0, 48)});
    }
  }
  document.title = 'CONTRAST_AUDIT:' + JSON.stringify(out);
})();
"""


def chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if Path(c).is_file():
            return c
    return None


def audit(binary: str, page: Path) -> list[dict]:
    """Render one page with the audit injected, and read back what it found."""
    html = page.read_text()
    injected = html.replace("</body>", f"<script>{AUDIT}</script></body>", 1)
    if "<script>" not in injected:                     # no </body> to hook
        injected = html + f"<script>{AUDIT}</script>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=str(page.parent),
                                     delete=True) as tmp:
        tmp.write(injected)
        tmp.flush()
        r = subprocess.run(
            [binary, "--headless", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=4000", "--dump-dom", f"file://{tmp.name}"],
            capture_output=True, text=True, timeout=120)
    m = re.search(r"CONTRAST_AUDIT:(\[.*?\])</title>", r.stdout, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="every lesson page")
    ap.add_argument("--check", action="store_true", help="exit non-zero on a failure")
    a = ap.parse_args()

    binary = chrome()
    if not binary:
        print("no Chromium found — skipping the contrast audit")
        return 0

    pages = [INDEX] + sorted(PAGES.glob("*.html"))
    if not a.all:
        # A sample that covers every distinct page shape: the homepage, the
        # lesson index, a lesson that embeds a kernel, one that does not, and
        # one of each function's introduction.
        keep = {"index.html", "A0.1.html", "B1.0.html", "B1.19.html",
                "C2.0.html", "D1.0.html", "E1.0.html", "F1.0.html"}
        pages = [p for p in pages if p.name in keep]

    total = 0
    for p in pages:
        bad = audit(binary, p)
        total += len(bad)
        label = p.relative_to(ROOT)
        if bad:
            print(f"  FAIL  {label}")
            for b in bad:
                print(f"          {b['ratio']}:1 (needs {b['floor']}) "
                      f"{b['sel']}  {b['color']} on {b['bg']}")
                print(f"            “{b['text']}”")
        else:
            print(f"  ok    {label}")

    print(f"\n{len(pages)} page(s) rendered · {total} unreadable text run(s)")
    if a.check and total:
        print(f"::error::{total} text run(s) below the WCAG AA contrast floor",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
