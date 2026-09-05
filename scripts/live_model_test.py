#!/usr/bin/env python3
"""Run the model-facing skills against a real backend and report what happened.

Every lesson in the commons runs offline against a deterministic replay. Six of
them execute a skill whose script calls a real model through the shared adapter.
This runs those scripts for real, so "the labs work against a real model" is an
evidenced statement rather than a design intention.

    # an open-weight model from Kaggle, served OpenAI-compatibly
    export OPENAI_BASE_URL=http://127.0.0.1:11434/v1 OPENAI_API_KEY=local
    python3 scripts/live_model_test.py --model qwen2.5-7b-instruct --save

There is one backend on purpose. The frontier path was removed: the commons is
free to run, and every model result in this repository was established against
open weights served locally. MODELS.md has the Kaggle download.

**It runs the skill's own script, in a subprocess.** It used to extract the
adapter and live cells out of the built notebook and `exec` them. That stopped
working when the code moved into `skills/` — a notebook now carries one cell
that runs a file, so there is no adapter cell to find, and this reported
`no model adapter cell` for every lesson. Running the file is also exactly what
the lesson does, which is the property that makes this evidence rather than a
parallel implementation.

**The acceptance property is the one the script prints, not its exit code.**
Each model-facing skill reports `property checked` and `held on <backend>`, and
reports it deliberately rather than asserting it: a real model failing a content
property is a finding about the model, not a broken notebook. Most of these
scripts assert only that the backend returned a non-empty string. Scoring them
on the exit code therefore measures plumbing and prints it as accuracy — it
scored every lesson as held at 1.5B, including the two that do not hold there.
The exit code is still recorded, as `script_exit_ok`; it is a different claim.

**Credentials never enter this repository.** A local server usually needs no key
at all; anything set is read from the environment, never printed, never written
to the evidence file, and `scripts/check_secrets.py` blocks anything
credential-shaped from being committed. This script is not run in CI — CI runs
the offline path, which is the one that has to be deterministic.

The evidence it writes (`labs/notebooks/_live_model.json`) records the model id,
the per-lesson verdict and what came back, so a reader can see what a real model
said rather than taking the claim on trust.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = ROOT / "labs" / "notebooks"
RUNTIME = ROOT / "skills" / "_runtime"

sys.path.insert(0, str(ROOT / "scripts"))
from exercises import EXERCISES  # noqa: E402


def _script_of(ex: dict) -> str | None:
    """The skill script a lesson runs, if that script calls a model.

    Derived rather than listed. A hardcoded list goes stale the first time a
    chapter is renumbered, and it goes stale silently — the script keeps
    passing while testing fewer lessons than it claims to.
    """
    for kind, source in ex.get("steps", []):
        if kind != "skill_script" or not isinstance(source, str):
            continue
        path = ROOT / "skills" / source
        try:
            src = path.read_text()
        except OSError:
            continue
        # Scripts import `ask` from the shared runtime; they used to define
        # their own `def ask(`. Accept both, or this finds nothing at all.
        head = src.split("import", 1)[1][:200] if "import" in src else ""
        if "def ask(" in src or ("cyber_commons_skill_runtime import" in src
                                 and "ask" in head):
            return source
    return None


MODEL_LESSONS = {sid: s for sid, ex in EXERCISES.items() if (s := _script_of(ex))}
LESSONS = sorted(
    MODEL_LESSONS,
    key=lambda s: (s[0], int(s[1]), [int(p) for p in s[2:].split(".") if p]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="override the served model's name")
    ap.add_argument("--session", help="run one lesson only")
    ap.add_argument("--save", action="store_true", help="write the evidence file")
    ap.add_argument("--list", action="store_true", help="print the lessons and exit")
    a = ap.parse_args()

    if a.list:
        for sid in LESSONS:
            print(f"{sid:8s}{MODEL_LESSONS[sid]}")
        return 0

    if not os.environ.get("OPENAI_BASE_URL"):
        print("No endpoint. Serve an open-weight model from Kaggle and set "
              "OPENAI_BASE_URL to it — MODELS.md has the download and the "
              "llama.cpp command.", file=sys.stderr)
        return 2

    env = dict(os.environ, PYTHONPATH=str(RUNTIME), PYTHONHASHSEED="0")
    if a.model:
        env["MODEL"] = a.model

    todo = [a.session] if a.session else LESSONS
    rows, unreached, broke = [], [], []
    print(f"backend: open-weight   lessons: {len(todo)}\n")

    for sid in todo:
        script = MODEL_LESSONS.get(sid)
        if script is None:
            print(f"  SKIP {sid}: runs no model-facing skill")
            continue
        t0 = time.time()
        p = subprocess.run([sys.executable, str(ROOT / "skills" / script)],
                           capture_output=True, text=True, env=env, timeout=900)
        took = time.time() - t0
        out = p.stdout

        def line(prefix: str, default: str = "?") -> str:
            return next((ln.split(":", 1)[1].strip() for ln in out.splitlines()
                         if ln.startswith(prefix)), default)

        backend = line("model backend")
        model = line("model         ")

        # A lesson that fell back to the replay has not been tested live. Carry
        # the adapter's own reason: "fell back to replay" on its own sends
        # whoever reads it looking for a bug in the harness, when the cause is
        # usually one line further up and is about the endpoint.
        why = next((ln.split("failed:", 1)[1].strip()
                    for ln in out.splitlines() if "failed:" in ln), "")
        reached = backend == "open-weight"

        # The acceptance property is the one the script PRINTS, not its exit
        # code. Four of these skills assert only that the backend returned a
        # non-empty string and then report the content property separately, on
        # purpose — "a real model failing it is a finding about the model, not
        # a broken notebook". Reading the exit code instead scored all six as
        # held at 1.5B, which is a plumbing result wearing an accuracy label.
        prop = next((ln.split(":", 1)[1].strip() for ln in out.splitlines()
                     if ln.startswith("property checked")), None)
        verdict = next((ln.split(":", 1)[1].strip() for ln in out.splitlines()
                        if ln.startswith("held on")), None)
        if verdict is not None:
            held, source = verdict == "True", "reported property"
        else:
            held, source = p.returncode == 0, "assertions"
        ran = p.returncode == 0
        err = None
        if not ran:
            err = "script exited non-zero: " + p.stderr.strip()[-300:]
        if not reached:
            unreached.append(sid)
            err = (f"fell back to {backend!r} instead of calling the backend"
                   + (f" — {why}" if why else ""))
        if not held:
            broke.append(sid)

        print(f"  {'ok  ' if reached and held and ran else 'FAIL'} {sid:7s}"
              f"{took:6.1f}s  backend={backend:12s}held={str(held):5s} ({source})")
        if prop:
            print(f"       property: {prop}")
        if err:
            print(f"       {err}")
        rows.append({"session": sid, "script": script, "reached_backend": reached,
                     "backend": backend, "model": model, "property": prop,
                     "property_held": held, "property_source": source,
                     "script_exit_ok": ran, "seconds": round(took, 2),
                     "error": err, "output": out.strip()[-4000:]})

    if not rows:
        print("nothing ran", file=sys.stderr)
        return 1

    # Two different questions, and conflating them is how this would report
    # "6/6" while two lessons' acceptance properties did not hold. Reaching the
    # backend is plumbing; the property holding is the claim.
    print(f"\n{len(rows) - len(unreached)}/{len(rows)} lessons reached a real "
          f"open-weight model")
    print(f"{len(rows) - len(broke)}/{len(rows)} lessons had their acceptance "
          f"property hold on {rows[0]['model']}")
    if broke:
        print(f"property did NOT hold: {', '.join(broke)} — the lesson ran, the "
              f"model's answer did not satisfy it")
    if unreached:
        print(f"never reached the backend: {unreached}", file=sys.stderr)

    if a.save:
        out_path = NB / "_live_model.json"
        prev = {}
        if out_path.is_file():
            prev = json.loads(out_path.read_text()).get("runs", {})
        # Keyed by backend AND model, because comparing two models is the whole
        # reason to run this twice. Keying on the backend alone means the second
        # run silently deletes the first, and the interesting result — which
        # lessons a smaller model cannot satisfy — is exactly what gets lost.
        prev[f"open-weight:{rows[0]['model']}"] = {
            "model": rows[0]["model"],
            "checked": len(rows),
            "reached_backend": len(rows) - len(unreached),
            "property_held": len(rows) - len(broke),
            "property_failed": broke,
            "results": rows,
        }
        out_path.write_text(json.dumps(
            {"generated_by": "scripts/live_model_test.py",
             "note": ("Each row is one real run of a skill's own script through "
                      "the shared adapter — the same file the lesson executes. "
                      "`reached_backend` is plumbing; `property_held` is the "
                      "script's own assertions. No credential appears here."),
             "runs": prev}, indent=1) + "\n")
        print(f"wrote {out_path.relative_to(ROOT)}")
    return 1 if (unreached or broke) else 0


if __name__ == "__main__":
    sys.exit(main())
