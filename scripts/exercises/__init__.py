"""Per-session notebook exercises, one entry per curriculum session id.

Schema
------
    "B2.5": {
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
from .track_a import EXERCISES as _a        # Function A — build it first
from .track_a0 import EXERCISES as _a0      # how to run the commons at all
from .track_b1 import EXERCISES as _b1
from .track_b2 import EXERCISES as _b2
from .track_b3 import EXERCISES as _b3
from .track_c2a import EXERCISES as _c2a      # the SDLC pipeline, part 1
from .track_c2b import EXERCISES as _c2b      # the SDLC pipeline, part 2
from .track_c2c import EXERCISES as _c2c      # agentic pentest, C2.10-C2.14
from .track_d1 import EXERCISES as _d1
from .track_d2 import EXERCISES as _d2
from .track_e1 import EXERCISES as _e1
from .track_e2 import EXERCISES as _e2
from .track_f1 import EXERCISES as _f1
from .track_f2 import EXERCISES as _f2
from .track_f3 import EXERCISES as _f3
from .track_new import EXERCISES as _new   # the five-phase E lessons, F1.13

EXERCISES: dict[str, dict] = {
    **_intro,
    **_incident,
    **_cases,
    **_register,
    **_a,
    **_a0, **_b1, **_b2, **_b3, **_c2a, **_c2b, **_c2c,
    **_d1, **_d2, **_e1, **_e2, **_f1, **_f2, **_f3, **_new,
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
