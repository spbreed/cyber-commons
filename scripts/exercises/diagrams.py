"""HTML and SVG diagrams for the parts of a lesson that explain rather than run.

A code cell that builds a dictionary of definitions and prints it as a table is
not a demonstration — it is a diagram wearing a `print` statement, and it costs
the reader a mental parse for nothing. Those become real diagrams; code stays
where something is actually computed, reproduced or asserted.

Two shapes cover almost all of it:

``table``  a definition or comparison laid out as a table. Renders everywhere,
           including GitHub's notebook viewer, because it is plain HTML with no
           dependence on styles surviving sanitisation.
``svg``    a structural picture — boxes, arrows, boundaries. Renders in Jupyter,
           on Kaggle and on the lesson pages.

Both are emitted into a markdown cell, so they cost the notebook nothing at run
time and nothing in dependencies.
"""
from __future__ import annotations

import html as _html

# One palette for every diagram. These render on a white Jupyter/Kaggle
# notebook AND on the site's dark lesson pages, which is why the default is
# `currentColor` — it inherits whatever the surrounding page is using — and why
# the accents are mid-tones rather than the near-black that reads well on only
# one of the two.
INK = "currentColor"
DIM = "#8A93A6"
LINE = "#8A93A6"
DEFEND = "#4D9BFF"      # AI for security
SECURE = "#E0912F"      # security of AI
BAD = "#E05C4B"
GOOD = "#3FA06B"


def table(headers: list[str], rows: list[list[str]], *, caption: str = "",
          emphasise: int | None = None) -> str:
    """A definition or comparison table.

    `emphasise` marks one column as the one the reader should come away with.
    """
    def cell(text: str, tag: str = "td", strong: bool = False) -> str:
        # currentColor at low opacity for rules, so the table reads on a light
        # notebook and on a dark lesson page without two stylesheets.
        style = ("padding:6px 11px;border-bottom:1px solid rgba(138,147,166,.35);"
                 "text-align:left;vertical-align:top;font-size:13px")
        if tag == "th":
            style += ";font-weight:600;border-bottom:2px solid rgba(138,147,166,.7)"
        if strong:
            style += ";font-weight:600"
        return f'<{tag} style="{style}">{text}</{tag}>'

    head = "".join(cell(_html.escape(h), "th") for h in headers)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(
            cell(c if c.startswith("<") else _html.escape(c),
                 strong=(emphasise is not None and i == emphasise))
            for i, c in enumerate(r)) + "</tr>"
    cap = (f'<div style="font-size:12px;color:{DIM};margin-top:6px">{caption}</div>'
           if caption else "")
    return (f'<table style="border-collapse:collapse;margin:4px 0 2px;width:100%">'
            f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>{cap}")


def svg(body: str, *, width: int = 700, height: int = 260,
        caption: str = "") -> str:
    """Wrap hand-written SVG with the shared type and caption treatment."""
    cap = (f'<div style="font-size:12px;color:{DIM};margin-top:2px">{caption}</div>'
           if caption else "")
    return (f'<svg viewBox="0 0 {width} {height}" width="100%" '
            f'style="max-width:{width}px;height:auto;font-family:ui-monospace,'
            f'SFMono-Regular,Menlo,monospace;font-size:12px">{body}</svg>{cap}')


# ----------------------------------------------------------------- SVG parts
def box(x: int, y: int, w: int, h: int, label: str, *, sub: str = "",
        colour: str = INK, fill: str = "none", dashed: bool = False) -> str:
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" '
           f'fill="{fill}" stroke="{colour}" stroke-width="1.4"{dash}/>')
    ty = y + (h / 2 + 4 if not sub else h / 2 - 3)
    out += (f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" '
            f'fill="{colour}">{_html.escape(label)}</text>')
    if sub:
        out += (f'<text x="{x + w / 2}" y="{y + h / 2 + 13}" text-anchor="middle" '
                f'fill="{DIM}" font-size="10.5">{_html.escape(sub)}</text>')
    return out


def arrow(x1: int, y1: int, x2: int, y2: int | None = None, *, label: str = "",
          colour: str = LINE, dashed: bool = False) -> str:
    """`y2` defaults to `y1`, because most arrows in these diagrams are level."""
    if y2 is None:
        y2 = y1
    dash = ' stroke-dasharray="4 4"' if dashed else ""
    out = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" '
           f'stroke-width="1.4" marker-end="url(#a)"{dash}/>')
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 6
        out += (f'<text x="{mx}" y="{my}" text-anchor="middle" fill="{DIM}" '
                f'font-size="10.5">{_html.escape(label)}</text>')
    return out


def label(x: int, y: int, text: str, *, colour: str = DIM, size: float = 11,
          anchor: str = "start", weight: str = "normal") -> str:
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{colour}" '
            f'font-size="{size}" font-weight="{weight}">{_html.escape(text)}</text>')


DEFS = ('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{LINE}"/></marker></defs>')
