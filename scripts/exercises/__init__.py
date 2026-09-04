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

from .framing import DIAGRAMS, HOOKS
from .casestudies import EXERCISES as _cases
from .register import EXERCISES as _register
from .incident import EXERCISES as _incident
from .intros import EXERCISES as _intro
from .track_a1 import EXERCISES as _a1
from .track_a2 import EXERCISES as _a2
from .track_a3 import EXERCISES as _a3
from .track_b2a import EXERCISES as _b2a      # the SDLC pipeline, part 1
from .track_b2b import EXERCISES as _b2b      # the SDLC pipeline, part 2
from .track_c1 import EXERCISES as _c1
from .track_c2 import EXERCISES as _c2
from .track_d1 import EXERCISES as _d1
from .track_d2 import EXERCISES as _d2
from .track_e1 import EXERCISES as _e1
from .track_e2 import EXERCISES as _e2
from .track_e3 import EXERCISES as _e3

EXERCISES: dict[str, dict] = {
    **_intro,
    **_incident,
    **_cases,
    **_register,
    **_a1, **_a2, **_a3, **_b2a, **_b2b,
    **_c1, **_c2, **_d1, **_d2, **_e1, **_e2, **_e3,
}

# The hook and the diagram live in framing.py rather than beside the lesson
# body, because they are about how a lesson opens rather than what it teaches —
# and keeping all 121 of each in one file is the only way to see whether they
# are consistent. The build fails on any lesson missing either.
for _sid, _ex in EXERCISES.items():
    if _sid in HOOKS:
        _ex["hook"] = HOOKS[_sid]
    if _sid in DIAGRAMS:
        _ex["diagram"] = DIAGRAMS[_sid]

__all__ = ["EXERCISES"]
