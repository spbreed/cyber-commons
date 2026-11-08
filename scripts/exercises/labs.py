"""Which functions are taught as hands-on labs, and where their steps live.

A function listed here has no lesson pages: each lesson is its lab page,
`site/lab/<id>.html`, and `site/lessons/<id>.html` is a redirect to it. The
page builder, the lab builder, the guide builder and the gates that read a
lesson's page all ask this module, so a function moves to the lab model in one
place rather than in six `startswith("A")` checks that drift apart.
"""
from __future__ import annotations

import importlib

# function id -> the module under scripts/exercises/ holding its steps
MODULES = {"A": "lab_a", "B": "lab_b", "C": "lab_c", "D": "lab_d", "E": "lab_e", "F": "lab_f"}


def has_lab(sid: str) -> bool:
    return sid[:1] in MODULES


def module_of(sid: str) -> str:
    return MODULES[sid[:1]]


def load() -> dict:
    """Every lab, keyed by lesson id, across the functions listed above."""
    out = {}
    for name in MODULES.values():
        out.update(importlib.import_module(f"exercises.{name}").LAB)
    return out
