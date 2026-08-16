"""Per-session notebook exercises, one entry per curriculum session id.

Schema
------
    "A2.5": {
        "goal":      str,   optional — overrides curriculum/labs.json
        "intro":     str,   optional markdown shown before the first step
        "steps":     [("md" | "py", source), ...],
        "expect":    str,   optional — overrides labs.json
        "challenge": str,   optional "Your turn" prompt
    }

Code steps run against `labs/cybercommons`, standard library only, so every
notebook executes on a Kaggle kernel with the internet switched off.
"""
from __future__ import annotations

from .module0 import EXERCISES as _m0
from .track_a import EXERCISES as _a
from .track_b import EXERCISES as _b
from .track_c import EXERCISES as _c
from .track_d import EXERCISES as _d
from .track_e import EXERCISES as _e

EXERCISES: dict[str, dict] = {**_m0, **_a, **_b, **_c, **_d, **_e}

__all__ = ["EXERCISES"]
