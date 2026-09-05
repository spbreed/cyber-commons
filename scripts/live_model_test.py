#!/usr/bin/env python3
"""Run the model-facing lessons against a real backend and report what happened.

Every lesson in the commons runs offline against a deterministic replay. Some of
them also carry a live section that calls a real model through the same code
path. This runs those for real, so "the labs work against a real model" is an
evidenced statement rather than a design intention.

    # an open-weight model from Kaggle, served OpenAI-compatibly
    export OPENAI_BASE_URL=http://127.0.0.1:11434/v1 OPENAI_API_KEY=local
    python3 scripts/live_model_test.py --model qwen2.5-7b-instruct --save

There is one backend on purpose. The frontier path was removed: the commons is
free to run, and every model result in this repository was established against
open weights served locally. MODELS.md has the Kaggle download.

**Credentials never enter this repository.** A local server usually needs no
key at all; anything set is read from the environment, never printed, never
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
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = ROOT / "labs" / "notebooks"

# The lessons carrying a live model section, derived rather than listed. A
# hardcoded list goes stale the first time a chapter is renumbered, and it goes
# stale silently — the script keeps passing while testing fewer lessons than it
# claims to.
sys.path.insert(0, str(ROOT / "scripts"))
from exercises import EXERCISES  # noqa: E402

def _calls_a_model(ex: dict) -> bool:
    """A lesson is model-facing if the skill script it runs calls a model.

    Lessons no longer emit an adapter of their own — the round trip lives in
    the skill's script, so the question is about the file in `skills/` rather
    than about the lesson's steps. Deriving it this way also means a skill that
    gains or loses a model call is picked up without editing this script.
    """
    for kind, source in ex["steps"]:
        if kind != "skill_script" or not isinstance(source, str):
            continue
        path = ROOT / "skills" / source
        try:
            src = path.read_text()
            # Scripts import `ask` from the shared runtime now; they used to
            # carry their own `def ask(`. Accept both, or this returns zero
            # model-facing lessons and silently tests nothing.
            if "def ask(" in src or ("cyber_commons_skill_runtime import" in src
                                     and "ask" in src.split("import", 1)[1][:200]):
                return True
        except OSError:
            continue
    return False


LESSONS = sorted(
    (sid for sid, ex in EXERCISES.items() if _calls_a_model(ex)),
    key=lambda s: (s[0], int(s[1]), [int(p) for p in s[2:].split(".") if p]))

def live_cells(sid: str) -> str:
    """The adapter plus the live round-trip — not the whole notebook.

    Running only these cells keeps the cost to the calls the lesson's own live
    section makes and keeps the rest of the lesson (which needs no model) out of
    the bill.

    Two shapes exist, and both are real. Most lessons carry one round trip: a
    task, a replay to fall back to, and one acceptance property. B2.0 carries an
    agentic **loop** — plan, act, verify, repeat — which is several calls and is
    the only lesson whose subject is the harness itself. Testing only the first
    shape would leave the loop lesson, the one most sensitive to model size,
    unexercised.
    """
    nb = json.loads((NB / f"{sid}.ipynb").read_text())
    src = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    # Search every code cell, not the first two: a lesson may introduce its
    # model section part-way through, and a positional assumption here fails
    # the moment one does.
    adapter = next((s for s in src if "model backend" in s), None)
    if adapter is None:
        raise SystemExit(f"{sid}: no model adapter cell")
    live = next((s for s in src if "answer, used, model" in s), None)
    if live is not None:
        return f"{adapter}\n\n{live}"
    loop_cells = [s for s in src if "def plan(" in s or "loop(TASK" in s]
    if not loop_cells:
        raise SystemExit(f"{sid}: expected a live cell or a harness loop")
    return "\n\n".join([adapter, *loop_cells])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="override the served model's name")
    ap.add_argument("--session", help="run one lesson only")
    ap.add_argument("--save", action="store_true", help="write the evidence file")
    a = ap.parse_args()

    env = dict(os.environ)
    if not env.get("OPENAI_BASE_URL"):
        print("No endpoint. Serve an open-weight model from Kaggle and set "
              "OPENAI_BASE_URL to it — MODELS.md has the download and the "
              "llama.cpp command.", file=sys.stderr)
        return 2
    if a.model:
        env["MODEL"] = a.model

    todo = [a.session] if a.session else LESSONS
    rows, failed = [], []
    print(f"backend: open-weight   lessons: {len(todo)}\n")

    for sid in todo:
        src = live_cells(sid)
        buf, t0 = io.StringIO(), time.time()
        ok, err = True, None
        real_env, os.environ = os.environ, env
        try:
            with contextlib.redirect_stdout(buf):
                # "__main__", not a private name: @dataclass resolves
                # sys.modules[cls.__module__] at class creation, and a module
                # name nothing registered makes that None. A notebook and a
                # Kaggle kernel are both __main__, so this also runs the cells
                # in the module context they were built for.
                exec(compile(src, sid, "exec"), {"__name__": "__main__"})
        except Exception as e:                       # noqa: BLE001 - reported, not raised
            # With the location. A bare "AttributeError: 'NoneType' object has
            # no attribute '__dict__'" costs whoever hits it an hour; the frame
            # says which lesson's cell and which line.
            frame = traceback.extract_tb(e.__traceback__)[-1]
            ok, err = False, (f"{type(e).__name__}: {e}  "
                              f"[{frame.filename}:{frame.lineno} {frame.line}]")
        finally:
            os.environ = real_env
        out = buf.getvalue()
        took = time.time() - t0

        def line(prefix: str, default: str = "?") -> str:
            return next((ln.split(":", 1)[1].strip() for ln in out.splitlines()
                         if ln.startswith(prefix)), default)

        used = line("backend used")
        model = line("model        :")
        held = line("held on")
        prop = line("property checked")
        answer = out.split("answer:\n", 1)[-1].split("\n\nproperty", 1)[0].strip()

        # The loop lesson prints a different shape, because it is a different
        # thing: several calls, and a verdict from a verifier rather than from a
        # one-shot property. Read it on its own terms rather than making the
        # lesson print a shape it does not have.
        if used == "?" and line("backend  ") != "?":
            used = line("backend  ")
            model = os.environ.get("MODEL", env.get("MODEL", "?"))
            prop = ("the verified loop returns a parameterised query, and the "
                    "unverified one does not have to")
            verified = [ln for ln in out.splitlines() if ln.startswith("verified :")]
            # The second `verified` line is the one that ran with a verifier;
            # the first deliberately has none, and reporting that one would
            # score the lesson on the run it is teaching you not to trust.
            held = str(len(verified) > 1 and "True" in verified[-1])
            answer = line("accepted ", "")

        # A lesson that fell back to the replay has not been tested live. Carry
        # the adapter's own reason into the report: "fell back to replay" on
        # its own sends whoever reads it looking for a bug in the harness, when
        # the cause is usually one line further up and is about the account.
        why = next((ln.split("failed:", 1)[1].strip()
                    for ln in out.splitlines() if "failed:" in ln), "")
        if ok and used != "open-weight":
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

    # Two different questions, and conflating them is how this script would
    # report "8/8" while two lessons' acceptance properties did not hold.
    # Reaching the backend is plumbing; the property holding is the claim.
    held = [r for r in rows if r["property_held"] == "True"]
    broke = [r["session"] for r in rows if r["property_held"] != "True"]
    print(f"\n{len(rows) - len(failed)}/{len(rows)} lessons reached a real "
          f"open-weight model")
    print(f"{len(held)}/{len(rows)} lessons had their acceptance property hold "
          f"on {rows[0]['model'] if rows else '?'}")
    if broke:
        print(f"property did NOT hold: {', '.join(broke)} — the lesson ran, the "
              f"model's answer did not satisfy it")
    if failed:
        print(f"never reached the backend: {failed}", file=sys.stderr)

    if a.save:
        out = NB / "_live_model.json"
        prev = {}
        if out.is_file():
            prev = json.loads(out.read_text()).get("runs", {})
        # Keyed by backend AND model, because comparing two models is the whole
        # reason to run this twice. Keying on the backend alone means the second
        # run silently deletes the first, and the interesting result — which
        # lessons a smaller model cannot satisfy — is exactly what gets lost.
        key = f"open-weight:{rows[0]['model']}" if rows else "open-weight"
        prev[key] = {
            "model": rows[0]["model"] if rows else None,
            "checked": len(rows),
            "reached_backend": len(rows) - len(failed),
            "property_held": sum(1 for r in rows if r["property_held"] == "True"),
            "property_failed": [r["session"] for r in rows
                                if r["property_held"] != "True"],
            "note": ("Each row is one real API call through the same adapter the "
                     "notebook uses. The offline path is unchanged and remains "
                     "the default; no credential appears in this file."),
            "results": rows,
        }
        out.write_text(json.dumps(
            {"generated_by": "scripts/live_model_test.py",
             "note": ("Each row is one real API call through the same adapter the "
                      "notebook uses. `reached_backend` is plumbing; "
                      "`property_held` is the claim. No credential appears here."),
             "runs": prev}, indent=1) + "\n")
        print(f"wrote {out.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
