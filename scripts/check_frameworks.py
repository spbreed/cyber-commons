#!/usr/bin/env python3
"""Check that every lesson resolves to framework labels, and that every label is real.

Two ways a mapping file rots. It goes stale — a track is added and nothing
notices that its lessons carry no labels at all. Or it drifts into invention —
a NIST function that is not one of the four, an EU AI Act article nobody
checked, an ATLAS tactic that does not exist. Both are worse than no mapping,
because a reader in a regulated industry may quote it.

So: every lesson must resolve to a row, every code must be in the vocabulary
below, and a track with no labels must say so on purpose via `why_empty`.

Run:
  python3 scripts/check_frameworks.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
FW = json.loads((ROOT / "curriculum" / "frameworks.json").read_text())

# The four NIST AI RMF 1.0 core functions. There are no others.
NIST = {"GOVERN", "MAP", "MEASURE", "MANAGE"}

# MITRE ATLAS tactics. Tactic names are used rather than technique ids because
# a wrong technique id looks authoritative and is hard to spot; the one
# exception is spelled out explicitly.
ATLAS_TACTICS = {
    "Reconnaissance", "Resource Development", "Initial Access", "ML Model Access",
    "Execution", "Persistence", "Privilege Escalation", "Defense Evasion",
    "Credential Access", "Discovery", "Collection", "ML Attack Staging",
    "Exfiltration", "Impact",
}
ATLAS_TECHNIQUES = {"AML.T0051"}          # LLM Prompt Injection

OWASP_RE = re.compile(r"^(LLM(0[1-9]|10)|T([1-9]|1[0-5]))$")
EUAI_RE = re.compile(r"^Art\. \d{1,3}$")


def main() -> int:
    problems: list[str] = []
    titles = FW["euai_titles"]

    # 1 — the vocabulary. Nothing outside it, anywhere in the file.
    rows = {f"track {k}": v for k, v in FW["tracks"].items()}
    rows.update({f"lesson {k}": v for k, v in FW["lessons"].items()})
    for where, row in rows.items():
        for code in row.get("owasp", []):
            if not OWASP_RE.match(code):
                problems.append(f"{where}: {code!r} is not an OWASP LLM01-LLM10 or T1-T15 id")
        for code in row.get("atlas", []):
            if code not in ATLAS_TACTICS and code not in ATLAS_TECHNIQUES:
                problems.append(f"{where}: {code!r} is not a MITRE ATLAS tactic, and "
                                f"not one of the vetted technique ids {sorted(ATLAS_TECHNIQUES)}")
        for code in row.get("nist", []):
            if code not in NIST:
                problems.append(f"{where}: {code!r} is not a NIST AI RMF function {sorted(NIST)}")
        for code in row.get("euai", []):
            if not EUAI_RE.match(code):
                problems.append(f"{where}: {code!r} is not an EU AI Act article reference")
            elif code not in titles:
                problems.append(f"{where}: {code} has no title in euai_titles — add it, so a "
                                f"reader can see what the article is before trusting the label")

    # 2 — coverage. Every lesson resolves, and an empty row is deliberate.
    lessons = FW["lessons"]
    covered = 0
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            tid = tr["id"]
            if tid not in FW["tracks"]:
                problems.append(f"track {tid} has no row in frameworks.json")
                continue
            track_row = FW["tracks"][tid]
            track_empty = not any(track_row.get(k) for k in ("owasp", "atlas", "nist", "euai"))
            if track_empty and not track_row.get("why_empty"):
                problems.append(f"track {tid} maps to nothing and does not say why "
                                f"(add \"why_empty\")")
            for s in tr["sessions"]:
                row = lessons.get(s["id"], track_row)
                if any(row.get(k) for k in ("owasp", "atlas", "nist", "euai")):
                    covered += 1

    # 3 — overrides must name a lesson that exists.
    ids = {s["id"] for fn in CUR["functions"] for t in fn["tracks"] for s in t["sessions"]}
    for sid in lessons:
        if sid not in ids:
            problems.append(f"lesson override {sid!r} is not a lesson in curriculum.json")

    total = len(ids)
    for p in problems:
        print(f"::error::{p}", file=sys.stderr)
    print(f"{total} lessons · {covered} carry framework labels · "
          f"{total - covered} deliberately unmapped · {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
