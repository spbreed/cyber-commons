"""Per-session notebook exercises, one entry per curriculum session id.

Schema
------
    "A2.5": {
        "concept":   str,   REQUIRED markdown — introduce the idea BEFORE any risk
        "steps":     [("md" | "py", source), ...],
        "expect":    str,   what a correct run prints
        "challenge": str,   the "Your turn" prompt
    }

Two rules the build enforces:

  * **Concept first.** `concept` is required. A lesson that opens with a risk
    teaches people to fear a mechanism they cannot describe.
  * **Self-contained.** Code steps may import only the standard library. No
    shared package, no clone, no pip — so every notebook runs on a Kaggle
    kernel with the internet switched off.
"""
from __future__ import annotations

from .track_a1 import EXERCISES as _a1
from .track_a2 import EXERCISES as _a2
from .track_a3 import EXERCISES as _a3
from .track_b1 import EXERCISES as _b1
from .track_b1b import EXERCISES as _b1b
from .track_b2 import EXERCISES as _b2
from .track_c1 import EXERCISES as _c1
from .track_c2 import EXERCISES as _c2
from .track_d1 import EXERCISES as _d1
from .track_d2 import EXERCISES as _d2
from .track_e1 import EXERCISES as _e1
from .track_e2 import EXERCISES as _e2
from .track_e3 import EXERCISES as _e3

EXERCISES: dict[str, dict] = {
    **_a1, **_a2, **_a3, **_b1, **_b1b, **_b2,
    **_c1, **_c2, **_d1, **_d2, **_e1, **_e2, **_e3,
}

__all__ = ["EXERCISES"]
