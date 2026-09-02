#!/usr/bin/env python3
"""Run the model-facing lessons against a real backend and report what happened.

Every lesson in the commons runs offline against a deterministic replay. Some of
them also carry a live section that calls a real model through the same code
path. This runs those for real, so "the labs work with a frontier model" is an
evidenced statement rather than a design intention.

    # frontier — cheapest current Claude model
    export ANTHROPIC_API_KEY=...          # or put it in ~/.anthropic/key
    python3 scripts/live_model_test.py --backend frontier

    # open weight — anything OpenAI-compatible
    export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama
    python3 scripts/live_model_test.py --backend open-weight --model glm-4.6

**Credentials never enter this repository.** The key is read from the
environment or from a file outside the working tree, it is never printed, never
written to the evidence file, and `scripts/check_secrets.py` blocks anything
credential-shaped from being committed. This script is not run in CI — CI runs
the offline path, which is the one that has to be deterministic.

The evidence it writes (`labs/notebooks/_live_model.json`) records the model id,
the per-lesson verdict and the answers, so a reader can see what a real model
said rather than taking the claim on trust.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import contextlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = ROOT / "labs" / "notebooks"

# The lessons carrying a live model section, derived rather than listed. A
# hardcoded list goes stale the first time a chapter is renumbered, and it goes
# stale silently — the script keeps passing while testing fewer lessons than it
# claims to.
sys.path.insert(0, str(ROOT / "scripts"))
from exercises import EXERCISES  # noqa: E402

LESSONS = sorted(
    (sid for sid, ex in EXERCISES.items()
     if any(kind == "model" for kind, _ in ex["steps"])),
    key=lambda s: (s[0], int(s[1]), [int(p) for p in s[2:].split(".") if p]))

KEY_FILES = [Path.home() / ".anthropic" / "key", Path.home() / ".anthropic_key"]


def load_key() -> str | None:
    """Environment first, then a file outside the repository. Never the repo."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    for f in KEY_FILES:
        try:
            if f.is_file():
                key = f.read_text().strip()
                if key:
                    return key
        except OSError:
            pass
    return None


def live_cells(sid: str) -> str:
    """The adapter plus the live round-trip — not the whole notebook.

    Running only these two cells keeps the cost to one API call per lesson and
    keeps the rest of the lesson (which needs no model) out of the bill.
    """
    nb = json.loads((NB / f"{sid}.ipynb").read_text())
    src = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    # Search every code cell, not the first two: a lesson may introduce its
    # model section part-way through, and a positional assumption here fails
    # the moment one does.
    adapter = next((s for s in src if "model backend" in s), None)
    live = next((s for s in src if "answer, used, model" in s), None)
    if adapter is None or live is None:
        raise SystemExit(f"{sid}: expected an adapter cell and a live cell")
    return f"{adapter}\n\n{live}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", choices=["frontier", "open-weight"], default="frontier")
    ap.add_argument("--model", help="override the backend's default model")
    ap.add_argument("--session", help="run one lesson only")
    ap.add_argument("--save", action="store_true", help="write the evidence file")
    a = ap.parse_args()

    env = dict(os.environ)
    if a.backend == "frontier":
        key = load_key()
        if not key:
            print("No key. Set ANTHROPIC_API_KEY, or write it to ~/.anthropic/key "
                  "(outside this repository).", file=sys.stderr)
            return 2
        env["ANTHROPIC_API_KEY"] = key
        env.pop("OPENAI_BASE_URL", None)
    else:
        if not env.get("OPENAI_BASE_URL"):
            print("No endpoint. Set OPENAI_BASE_URL to any OpenAI-compatible API.",
                  file=sys.stderr)
            return 2
        env.pop("ANTHROPIC_API_KEY", None)
    if a.model:
        env["MODEL"] = a.model

    todo = [a.session] if a.session else LESSONS
    rows, failed = [], []
    print(f"backend: {a.backend}   lessons: {len(todo)}\n")

    for sid in todo:
        src = live_cells(sid)
        buf, t0 = io.StringIO(), time.time()
        ok, err = True, None
        real_env, os.environ = os.environ, env
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(src, sid, "exec"), {"__name__": "__live__"})
        except Exception as e:                       # noqa: BLE001 - reported, not raised
            ok, err = False, f"{type(e).__name__}: {e}"
        finally:
            os.environ = real_env
        out = buf.getvalue()
        took = time.time() - t0

        used = next((ln.split(":", 1)[1].strip() for ln in out.splitlines()
                     if ln.startswith("backend used")), "?")
        model = next((ln.split(":", 1)[1].strip() for ln in out.splitlines()
                      if ln.startswith("model        :")), "?")
        held = next((ln.split(":", 1)[1].strip() for ln in out.splitlines()
                     if ln.startswith("held on")), "?")
        prop = next((ln.split(":", 1)[1].strip() for ln in out.splitlines()
                     if ln.startswith("property checked")), "?")
        answer = out.split("answer:\n", 1)[-1].split("\n\nproperty", 1)[0].strip()

        # A lesson that fell back to the replay has not been tested live. Carry
        # the adapter's own reason into the report: "fell back to replay" on
        # its own sends whoever reads it looking for a bug in the harness, when
        # the cause is usually one line further up and is about the account.
        why = next((ln.split("failed:", 1)[1].strip()
                    for ln in out.splitlines() if "failed:" in ln), "")
        if ok and used != a.backend:
            ok = False
            err = (f"fell back to {used!r} instead of calling the backend"
                   + (f" — {why}" if why else ""))
        if not ok:
            failed.append(sid)

        print(f"  {'ok  ' if ok else 'FAIL'} {sid:7s}{took:5.1f}s  "
              f"backend={used:12s}property held={held}")
        if err:
            print(f"       {err}")
        rows.append({"session": sid, "ok": ok, "backend": used, "model": model,
                     "property": prop, "property_held": held,
                     "seconds": round(took, 2), "error": err,
                     "answer": answer})

    print(f"\n{len(rows) - len(failed)}/{len(rows)} lessons ran against a real "
          f"{a.backend} model")
    if failed:
        print(f"failed: {failed}", file=sys.stderr)

    if a.save:
        out = NB / "_live_model.json"
        prev = {}
        if out.is_file():
            prev = json.loads(out.read_text()).get("runs", {})
        prev[a.backend] = {
            "model": rows[0]["model"] if rows else None,
            "checked": len(rows), "passed": len(rows) - len(failed),
            "note": ("Each row is one real API call through the same adapter the "
                     "notebook uses. The offline path is unchanged and remains "
                     "the default; no credential appears in this file."),
            "results": rows,
        }
        out.write_text(json.dumps({"generated_by": "scripts/live_model_test.py",
                                   "runs": prev}, indent=1) + "\n")
        print(f"wrote {out.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
