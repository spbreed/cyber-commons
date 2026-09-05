#!/usr/bin/env python3
"""Validate every agent skill in `skills/`.

A skill is only useful if an agent can load it, decide when to fire it, and be
held to what it promised. This checks all three, and it uses the same runtime
the lessons use — so if a skill would fail here it would fail in a notebook.

    python3 scripts/check_skills.py          # report
    python3 scripts/check_skills.py --check  # CI: non-zero on any problem

What it enforces, and why each one is a real failure mode:

  * **frontmatter parses**, with `name` and `description` — an agent cannot
    load a skill whose header it cannot read.
  * **the directory name matches `name`** — they are two places to say the same
    thing, and they drift.
  * **`allowed-tools` is declared** — a skill with no stated bound has whatever
    the caller has.
  * **the output contract parses as JSON** — a contract that cannot be parsed
    cannot be checked, which makes it decoration.
  * **descriptions do not collide** — routing is by description alone, so two
    skills that score identically on a plausible task means the wrong one runs
    and the tiebreak is alphabetical.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from exercises.skills import SKILL_RUNTIME  # noqa: E402

_ns: dict = {}
exec(SKILL_RUNTIME, _ns)
parse_skill, route, contract_of = _ns["parse_skill"], _ns["route"], _ns["contract_of"]

# Tasks a reader might plausibly bring. Each must route somewhere with a margin:
# a tie means two descriptions overlap and the winner is decided by sort order.
ROUTING_CASES = [
    "map the attack surface of this repository before we review it",
    "what could go wrong with this architecture",
    "review this code for SQL injection",
    "write a proof of concept for this finding",
    "write up the findings and assign severity",
    "audit the coding agent's configuration and MCP servers",
    "who is this agent calling as, and is the delegation auditable",
    "how bad would it be if this agent were compromised",
    "work the alert queue and decide what to auto-close",
    "scope what this agent touched during the incident",
    "prepare audit evidence that this control works",
    # Added as the catalogue grew past a hundred skills. Each of these is a
    # sentence somebody would actually type, and each was a tie at some point
    # while the descriptions were being written.
    "which regulations apply to this agent and what is the shortest clock",
    "tier this use case by how much authority it has",
    "can this run unattended, and at what autonomy level",
    "our canaries and honeypots need designing for an agent environment",
    "the model provider changed the model, what does that invalidate",
    "how long would it actually take us to stop a running agent",
    "find the personal data in this agent trace and try to erase it",
    "measure whether this jailbreak technique reproduces",
]


# The loading model an agent uses, as budgets. Metadata is loaded for every
# skill at startup; the body only on activation; scripts/ and references/ only
# when something actually needs them.
DESCRIPTION_BUDGET = 110      # ~100 tokens, with room for one long sentence
BODY_BUDGET = 5000

REQUIRED_SECTIONS = [
    (("When to use this", "Safety preconditions"),
     "an agent needs the activation condition, not just the procedure"),
    (("Procedure", "Step-by-step"),
     "numbered steps, each an instruction rather than a description"),
    (("Example", "Inputs"),
     "a real input and the real output, so the shape is not left to guesswork"),
    (("Failure modes", "Common edge cases"),
     "the ways it goes wrong, including the ones that fail silently"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="non-zero exit on any problem")
    a = ap.parse_args()

    paths = sorted((ROOT / "skills").glob("*/*/SKILL.md"))
    if not paths:
        print("::error::no skills found under skills/", file=sys.stderr)
        return 1

    problems, skills = [], {}
    for p in paths:
        ref = f"{p.parent.parent.name}/{p.parent.name}"
        try:
            meta, body = parse_skill(p.read_text())
        except Exception as e:                                  # noqa: BLE001
            problems.append(f"{ref}: will not parse — {e}")
            continue
        if meta["name"] != p.parent.name:
            problems.append(f"{ref}: frontmatter name {meta['name']!r} != "
                            f"directory {p.parent.name!r}")
        if not meta.get("allowed-tools"):
            problems.append(f"{ref}: declares no allowed-tools")

        # The progressive-disclosure budgets. An agent loads every skill's
        # metadata at startup and pays for it whether the skill fires or not,
        # so the description is the expensive field; the body is only paid for
        # on activation, and the resources only when they run. See
        # skills/README.md — these are the numbers that contract is written to.
        d_tokens = len(meta["description"].split()) * 4 // 3
        b_tokens = len(body.split()) * 4 // 3
        if d_tokens > DESCRIPTION_BUDGET:
            problems.append(f"{ref}: description is ~{d_tokens} tokens, over "
                            f"the {DESCRIPTION_BUDGET} startup budget — every "
                            f"agent pays for it on every task")
        if b_tokens > BODY_BUDGET:
            problems.append(f"{ref}: body is ~{b_tokens} tokens, over the "
                            f"{BODY_BUDGET} activation budget — move detail "
                            f"into scripts/ or references/")

        # The sections a skill needs to be usable by an agent that has just
        # activated it: when to reach for it, the steps, a worked example, and
        # the ways it fails.
        for names, why in REQUIRED_SECTIONS:
            if not any(f"## {n}" in body for n in names):
                problems.append(f"{ref}: no '## {names[0]}' section — {why}")
        try:
            contract_of(body)
            has_contract = True
        except Exception as e:                                  # noqa: BLE001
            problems.append(f"{ref}: output contract — {e}")
            has_contract = False
        skills[meta["name"]] = meta
        print(f"  ok  {meta['name']:26s} {len(meta['description'].split()):3d}w  "
              f"tools={len(meta.get('allowed-tools', [])):d}  "
              f"contract={'yes' if has_contract else 'NO'}")

    print(f"\nrouting {len(ROUTING_CASES)} plausible tasks across {len(skills)} skills")
    for task in ROUTING_CASES:
        pick, scores, margin = route(task, skills)
        if margin > 0:
            print(f"  ok  {task[:52]:54s} -> {pick} (margin {margin})")
        else:
            tied = sorted(n for n, s in scores.items() if s == scores[pick])
            problems.append(f"routing tie on {task!r}: {tied} all score "
                            f"{scores[pick]} — the descriptions overlap, so the "
                            f"winner is whichever sorted first")
            print(f"  TIE {task[:52]:54s} -> {tied}")

    print(f"\n{len(paths)} skill(s), {len(problems)} problem(s)")
    for pr in problems:
        print(f"::error::{pr}", file=sys.stderr)
    return 1 if (problems and a.check) else 0


if __name__ == "__main__":
    sys.exit(main())
