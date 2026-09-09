#!/usr/bin/env python3
"""Review every lesson's prose with a model, and report what a first-time reader would trip over.

The gates in this repository check *structure* — that a lesson has a hook, that
its diagram precedes its code, that its counts match the tree. None of them can
read. So the failure they cannot see is the one readers actually report: a
sentence that assumes context the reader does not have, an idiom that does not
travel, a term used before it is defined.

This is the reading pass, run by a model over the rendered prose of each lesson.
It is a **review tool, not a gate**: it costs money, it needs the network, and
its output is a judgement rather than a fact. Nothing in CI depends on it.

    export ANTHROPIC_API_KEY=...
    python3 scripts/judge_content.py                 # every lesson
    python3 scripts/judge_content.py --session D1.1  # one
    python3 scripts/judge_content.py --limit 20      # a sample
    python3 scripts/judge_content.py --out findings.json

What it looks for, and nothing else — a judge asked for "feedback" returns
opinions about tone, which are not actionable and drown the real findings:

  * **undefined term** — a term used before this lesson or an earlier one
    defines it, including acronyms on first use.
  * **unexplained idiom** — figurative or culture-specific phrasing a competent
    non-native reader would not resolve. This is what put "on a Tuesday" into
    six lessons before anyone noticed.
  * **ambiguous referent** — "it", "this", "that" where more than one antecedent
    is available.
  * **unsupported claim** — a number or assertion the lesson states without
    saying where it came from.
  * **missing step** — reasoning that jumps, where a reader has to infer a link
    the text does not make.

Findings carry a severity so the list can be triaged rather than read whole:
`blocker` (the reader is stopped), `friction` (they continue, slower), `nit`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = ROOT / "labs" / "notebooks"
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())

# Either backend, whichever key is present. The judge is a reading pass, not a
# benchmark — the point is that some competent model reads every lesson, not
# which one.
ANTHROPIC = "https://api.anthropic.com/v1/messages"
OPENAI = "https://api.openai.com/v1/chat/completions"

SYSTEM = """You review technical security curriculum prose for first-time readers.

The audience is a working security practitioner — an architect, an engineer, a
SOC analyst, a GRC lead — who is competent in security but new to agentic AI,
and who may not be a native English speaker. They are reading alone, with
nobody to explain it to them.

Report ONLY these five categories:
  undefined_term      a term or acronym used before anything defines it
  unexplained_idiom   figurative or culture-specific phrasing that will not travel
  ambiguous_referent  "it"/"this"/"that" with more than one possible antecedent
  unsupported_claim   a number or assertion with no stated source or derivation
  missing_step        reasoning that jumps; the reader must infer an unstated link

Do NOT comment on tone, style, voice, formatting, length, or word choice you
merely dislike. Do NOT suggest rewrites of things that are already clear. A
lesson with nothing wrong should return an empty list, and most well-written
lessons will.

Severity:
  blocker   a reader is stopped or misled
  friction  a reader continues but has to re-read or guess
  nit       correct but could be plainer

Return ONLY a JSON object, no prose around it:
{"findings":[{"category":"...","severity":"...","quote":"the exact phrase from
the text","why":"one sentence on what the reader cannot resolve","fix":"a
concrete suggested replacement"}]}"""


def lesson_prose(sid: str) -> str:
    """The markdown a reader actually sees, minus code cells."""
    nb = json.loads((NB / f"{sid}.ipynb").read_text())
    return "\n\n".join("".join(c["source"]) for c in nb["cells"]
                       if c["cell_type"] == "markdown")


def backend() -> tuple[str, str, str]:
    """(name, key, model) for whichever provider has a key set."""
    if k := os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", k, os.environ.get("JUDGE_MODEL",
                                              "claude-sonnet-4-5-20250929")
    if k := os.environ.get("OPENAI_API_KEY"):
        return "openai", k, os.environ.get("JUDGE_MODEL", "gpt-4o-mini")
    return "", "", ""


def ask(who: str, key: str, model: str, sid: str, text: str,
        timeout: int) -> list[dict]:
    prompt = f"Lesson {sid}\n\n{text[:60000]}"
    if who == "anthropic":
        url, headers = ANTHROPIC, {"content-type": "application/json",
                                   "x-api-key": key,
                                   "anthropic-version": "2023-06-01"}
        body = {"model": model, "max_tokens": 2000, "system": SYSTEM,
                "messages": [{"role": "user", "content": prompt}]}
    else:
        url, headers = OPENAI, {"content-type": "application/json",
                                "authorization": f"Bearer {key}"}
        body = {"model": model, "max_tokens": 2000,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": prompt}]}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        payload = json.loads(r.read())
    if who == "anthropic":
        out = "".join(b.get("text", "") for b in payload.get("content", []))
    else:
        out = payload["choices"][0]["message"]["content"]
    out = out.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    try:
        return json.loads(out).get("findings", [])
    except json.JSONDecodeError:
        print(f"  {sid}: judge did not return JSON, skipped", file=sys.stderr)
        return []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--out", default="judge-findings.json")
    a = ap.parse_args()

    who, key, model = backend()
    if not key:
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY. This tool is a local\n"
              "review pass — the key belongs in your shell, never in the repo.",
              file=sys.stderr)
        return 2
    print(f"judging with {who}/{model}\n")

    ids = [s["id"] for f in CUR["functions"] for t in f["tracks"]
           for s in t["sessions"]]
    if a.session:
        ids = [i for i in ids if i == a.session] or sys.exit(f"no lesson {a.session}")
    if a.limit:
        ids = ids[:a.limit]

    all_findings, counts = {}, {"blocker": 0, "friction": 0, "nit": 0}
    for n, sid in enumerate(ids, 1):
        try:
            found = ask(who, key, model, sid, lesson_prose(sid), a.timeout)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"  {sid}: unreachable ({type(e).__name__}), skipped",
                  file=sys.stderr)
            continue
        if found:
            all_findings[sid] = found
            for f in found:
                counts[f.get("severity", "nit")] = \
                    counts.get(f.get("severity", "nit"), 0) + 1
        mark = f"{len(found)} finding(s)" if found else "clean"
        print(f"  [{n:>3}/{len(ids)}] {sid:<7} {mark}")

    Path(a.out).write_text(json.dumps(all_findings, indent=2) + "\n")
    total = sum(len(v) for v in all_findings.values())
    print(f"\n{len(ids)} lesson(s) reviewed · {len(all_findings)} with findings · "
          f"{total} finding(s)")
    print("  " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"written to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
