#!/usr/bin/env python3
"""Do one lesson end to end, and say what happened.

    python3 scripts/lesson.py A0.0                      # the whole lesson
    python3 scripts/lesson.py A1.1 --answer ans.json    # finish an audit you answered yourself
    python3 scripts/lesson.py A1.1 --use-runtime        # let the runtime call a model instead

This is the harness behind a lesson skill (`lesson-skills/`). A learner picks
the skill in their agent; the agent runs this and reads back the result. It is
also what to run when there is no agent, so the two routes do the same thing.

It does five things, in order, and reports each honestly:

  1. gets the CyberTravels code as it stood at the end of the lesson,
  2. shows what that lesson added,
  3. runs the tests that exist at that point,
  4. runs the lesson's audit,
  5. prints a READBACK: What I did / What changed / The number / Read this next.

**Nothing here is substituted for a result.** A step that cannot run says why
and is reported as skipped or refused, never as passed. The audit is the only
step that needs a model; with none configured it exits 2 and says so.

**Who answers the audit.** There are three kinds, told apart by
`exercises.lessonskills.audit_kind`:

  * a **model** audit is answered by the agent that called this, because it is
    already a model and needs no key or endpoint: the harness prints the
    audit's task, the agent answers it, and `--answer` checks that answer
    against the audit skill's own output contract. `--use-runtime` calls a
    model through the runtime instead (a signed-in `claude` CLI, or
    `OPENAI_BASE_URL`), which is what CI and anyone with no agent uses;
  * a **demo** audit is a deterministic worked example with no model and no
    contract, so the harness just runs it and its output is the result;
  * the lessons that test the runtime itself (A0.0, A0.1) try the runtime first
    and fall back to the agent, so a learner whose only model is their
    assistant is not stopped by a check about a route they are not using.

A lesson that runs several audits takes `--audit 2`, `--audit 3`.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "_runtime"))

import checkpoint                                             # noqa: E402
from exercises import EXERCISES                               # noqa: E402
from exercises.lessonskills import (RUNTIME_LESSONS,  # noqa: E402
                                    audit_kind, audits_of)

MARKER = ".lesson"           # what wrote this folder, and what it held when it did


# ---------------------------------------------------------------- 1 · the code
def manifest(d: Path) -> str:
    """A fingerprint of every file in a checkpoint folder, marker excluded.

    `checkpoint.write()` deletes its target folder before writing. That is right
    for a snapshot and wrong for a learner who has edited the copy, so the
    harness records what it wrote and refuses to replace a folder that no longer
    matches. Without it, moving from one lesson to the next would silently throw
    away the learner's changes.
    """
    h = hashlib.sha256()
    for p in sorted(x for x in d.rglob("*") if x.is_file()
                    and x.name != MARKER and "__pycache__" not in x.parts):
        h.update(p.relative_to(d).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def get_code(sid: str, out: Path, force: bool) -> dict:
    """Write the checkpoint. Returns {ok, files, note}."""
    order = checkpoint.lesson_order()
    if sid not in order:
        return {"ok": False, "files": 0, "note": f"{sid} is not a lesson"}
    if out.name != "cybertravels":
        # The smoke test imports the tree as `cybertravels`, so any other folder
        # name would make step 3 fail for a reason unrelated to the lesson.
        return {"ok": False, "files": 0,
                "note": "the output folder must be named cybertravels"}
    replaced = False
    if out.exists() and any(out.iterdir()):
        mark = out / MARKER
        if not force:
            if not mark.is_file():
                return {"ok": False, "files": 0,
                        "note": f"{out} already exists and this harness did not "
                                f"write it. Use --out for another folder, or "
                                f"--force to replace it."}
            written = mark.read_text().split()[-1]
            if manifest(out) != written:
                return {"ok": False, "files": 0,
                        "note": f"you have changed files in {out}. Use --out "
                                f"for another folder, or --force to discard "
                                f"your changes."}
        replaced = True
    tree = checkpoint.build(sid, order)
    n = checkpoint.write(tree, out)
    (out / MARKER).write_text(f"{sid} {manifest(out)}\n")
    return {"ok": True, "files": n,
            "note": "Replaced the earlier copy." if replaced else ""}


# ------------------------------------------------------------ 2 · what changed
def what_changed(sid: str) -> dict:
    """Files and lines this one lesson added or changed in CyberTravels."""
    order = checkpoint.lesson_order()
    i = order.index(sid)
    before = checkpoint.build(order[i - 1], order) if i else {}
    after = checkpoint.build(sid, order)
    added = sorted(set(after) - set(before))
    changed = sorted(r for r in set(after) & set(before)
                     if after[r] != before[r])
    lines = 0
    for rel in added:
        lines += len((after[rel] or "").splitlines())
    for rel in changed:
        b, c = (before[rel] or "").splitlines(), (after[rel] or "").splitlines()
        lines += abs(len(c) - len(b))
    return {"added": added, "changed": changed, "lines": lines,
            "previous": order[i - 1] if i else None}


# ----------------------------------------------------------------- 3 · testing
def smoke(out: Path) -> dict:
    """Run the checkpoint's own smoke test, if it has one and PyJWT is there."""
    if not (out / "tests" / "smoke_test.py").is_file():
        return {"status": "none",
                "note": "no smoke test exists at this lesson yet; the first "
                        "one arrives with a later lesson"}
    try:
        subprocess.run([sys.executable, "-c", "import jwt"], check=True,
                       capture_output=True)
    except (subprocess.CalledProcessError, OSError):
        return {"status": "skipped",
                "note": "PyJWT is not installed, so the test could not run. "
                        "That is not evidence the code is broken: "
                        "pip install PyJWT"}
    r = subprocess.run([sys.executable, "-m", "cybertravels.tests.smoke_test"],
                       cwd=out.parent, capture_output=True, text=True,
                       encoding="utf8", errors="replace", timeout=180)
    lines = (r.stdout + r.stderr).strip().splitlines()
    ok = sum(1 for x in lines if x.strip().startswith("ok "))
    bad = sum(1 for x in lines if x.strip().startswith("FAIL"))
    return {"status": "passed" if r.returncode == 0 else "failed",
            "ok": ok, "fail": bad, "tail": lines[-6:]}


# ------------------------------------------------------------------- 4 · audit
def audit_at(sid: str, n: int) -> tuple[str, Path, str, int] | None:
    """(skill ref, script path, kind, how many audits the lesson has) or None."""
    found = audits_of(sid)
    if not found or not 1 <= n <= len(found):
        return None
    ref, script = found[n - 1]
    path = ROOT / "skills" / script
    return ref, path, audit_kind(path), len(found)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("lesson_audit", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def audit_via_runtime(sid: str, script: Path) -> dict:
    """Run the audit script, which calls a model through the runtime."""
    # UTF-8 both ways: the audit prints dashes, and a Windows console decodes a
    # child's output as cp1252 unless told otherwise, which turns each one into
    # three characters of noise.
    r = subprocess.run([sys.executable, str(script)], capture_output=True,
                       text=True, encoding="utf8", errors="replace",
                       timeout=600, cwd=ROOT,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    out = r.stdout
    if r.returncode == 2:
        return {"status": "refused", "how": "runtime",
                "note": "no model is configured for the runtime",
                "output": out.strip()}
    if r.returncode not in (0, 1):
        return {"status": "error", "how": "runtime",
                "note": f"the audit script exited {r.returncode}",
                "output": (out + r.stderr).strip()}
    def grab(key):
        m = re.search(rf"^{key}\s*:\s*(.*)$", out, re.M)
        return m.group(1).strip() if m else None

    v = grab("violations")
    if v is None and r.returncode == 0:
        # A demonstration: no model was asked and there is no contract, so there
        # is no violation count and the output is the whole result.
        return {"status": "ran", "how": "demo", "output": out.strip()}
    return {"status": "held" if r.returncode == 0 else "broken", "how": "runtime",
            "violations": int(v) if v and v.isdigit() else None,
            "backend": grab("model backend"), "model": grab("model"),
            "output": out.strip()}


def audit_task(sid: str, script: Path) -> dict:
    """Print the audit's task for the calling agent to answer."""
    import cyber_commons_skill_runtime as rt
    mod = load_module(script)
    skill_md = mod.SKILL.read_text(encoding="utf8")
    _, prompt = rt.build_prompt(skill_md, mod.task())
    return {"status": "waiting", "how": "agent", "prompt": prompt}


def audit_validate(sid: str, script: Path, answer: Path) -> dict:
    """Hold the agent's own answer to the audit skill's output contract."""
    import cyber_commons_skill_runtime as rt
    mod = load_module(script)
    skill_md = mod.SKILL.read_text(encoding="utf8")
    try:
        instance, problems = rt.validate_answer(
            skill_md, answer.read_text(encoding="utf8"))
    except (ValueError, OSError) as e:
        return {"status": "broken", "how": "agent", "violations": None,
                "note": str(e).splitlines()[0]}
    return {"status": "held" if not problems else "broken", "how": "agent",
            "violations": len(problems), "problems": problems,
            "answer": instance}


# ---------------------------------------------------------------- the readback
def shown(p: Path) -> str:
    """A path as the learner would type it: relative to the repository if inside."""
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def readback(sid: str, title: str, code: dict, diff: dict | None, test: dict | None,
             audit: dict | None, has_audit: bool, out: Path,
             which: int = 1, total: int = 0) -> tuple[str, int]:
    """The four headings, every line derived from something that ran."""
    did, changed, number, nxt = [], [], [], []
    rc = 0

    if code["ok"]:
        did.append(f"Wrote the CyberTravels code as it stood at the end of "
                   f"{sid} ({code['files']} files) to {shown(out)}."
                   + (f" {code['note']}" if code["note"] else ""))
    else:
        did.append(f"Could not get the code: {code['note']}")
        rc = 1

    if test:
        if test["status"] == "passed":
            did.append(f"Ran its tests: {test['ok']} checks passed.")
        elif test["status"] == "failed":
            did.append(f"Ran its tests: {test['fail']} failed, {test['ok']} passed.")
            rc = 1
        else:
            did.append(f"Tests not run — {test['note']}.")

    if audit is None:
        did.append("No audit to run: this is a reading lesson." if not has_audit
                   else "The audit was not run.")
    elif audit["status"] == "refused":
        did.append("Tried to run the audit and stopped: no model is "
                   "configured. That is expected on a fresh machine.")
        rc = 2
    elif audit["status"] == "waiting":
        did.append("Printed the audit's task for the agent to answer."
                   + (" The runtime has no model, so the agent answers; that is "
                      "all a lesson needs." if audit.get("fallback") else ""))
    elif audit["status"] == "ran":
        did.append("Ran the audit. It is a worked example with no model in it, "
                   "so its output above is the result.")
    elif audit["status"] in ("held", "broken"):
        who = (f"{audit.get('model')} ({audit.get('backend')})"
               if audit.get("model") else "the agent")
        did.append(f"Ran the audit, answered by {who}."
                   + ("" if audit["status"] == "held" else
                      " The answer did not fit the audit's output contract."))
        if audit["status"] == "broken":
            rc = 1
    else:
        did.append(f"The audit did not complete: {audit.get('note', '')}")
        rc = 1

    if diff:
        n, c = len(diff["added"]), len(diff["changed"])
        if n == 0 and c == 0:
            changed.append("This lesson adds nothing to the code. It is about "
                           "the system as it stands.")
        elif diff["previous"] is None:
            changed.append(f"This is the first lesson, so all {n} files are new: "
                           f"the whole starting application.")
        else:
            changed.append(f"Added {n} file(s) and changed {c} that already "
                           f"existed, about {diff['lines']} lines, since "
                           f"{diff['previous']}.")
        first = (diff["added"] + diff["changed"])[:6]
        if first:
            changed.append("Including: " + ", ".join(first)
                           + (" …" if n + c > 6 else ""))
    else:
        changed.append("Nothing to compare: the code was not written.")

    if test and test["status"] == "passed":
        number.append(f"Checks passed in this lesson's own test: {test['ok']}.")
    if audit and audit.get("violations") is not None:
        number.append(f"Ways the audit's answer broke its contract, counted by "
                      f"the harness rather than by the model: "
                      f"{audit['violations']}.")
        if audit["status"] == "broken":
            for p in audit.get("problems", [])[:5]:
                number.append(f"    {p}")
    if audit and audit["status"] == "held":
        number.append("Conformance only: the shape is right. That does not "
                      "make the answer correct.")
    if audit and audit["status"] == "ran":
        number.append("The audit prints its own figures above; this harness "
                      "adds none. There is no contract to break, so no "
                      "violation count exists for it.")
    if not number:
        number.append("No number was produced. What to count instead: whether "
                      "each step above ran, was skipped, or was refused.")

    order = checkpoint.lesson_order()
    i = order.index(sid) if sid in order else -1
    if audit and audit["status"] == "refused":
        nxt.append("Set up a model (Route A, B or C on the lesson page), then run "
                   f"this lesson again: python3 scripts/lesson.py {sid}")
    if audit and audit["status"] == "waiting":
        nxt.append("Answer the task above with one JSON object in "
                   f"work/answer.json, then run: python3 scripts/lesson.py {sid} "
                   f"--answer work/answer.json")
    if total > 1 and which < total:
        nxt.append(f"This lesson runs {total} audits and this was number {which}. "
                   f"Run the next: python3 scripts/lesson.py {sid} "
                   f"--audit {which + 1}")
    if 0 <= i < len(order) - 1:
        n = order[i + 1]
        how = "pick its skill in your agent"
        nxt.append(f"Next lesson: {n} — {how}.")

    def block(head, items):
        return [head] + [f"  {x}" if not x.startswith("    ") else x for x in items] + [""]

    lines = ["", "=" * 68, f"READBACK — {sid} · {title}", "=" * 68, ""]
    lines += block("What I did", did)
    lines += block("What changed", changed)
    lines += block("The number", number)
    lines += block("Read this next", nxt or ["This is the last lesson."])
    return "\n".join(lines), rc


# ------------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lesson", help="lesson id, for example A0.0")
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "cybertravels",
                    help="where to write the code (default work/cybertravels)")
    ap.add_argument("--force", action="store_true",
                    help="replace the output folder even if you changed it")
    ap.add_argument("--answer", type=Path,
                    help="your answer to the audit, as JSON, to be checked")
    ap.add_argument("--use-runtime", action="store_true",
                    help="run the audit through the runtime's model instead")
    ap.add_argument("--audit", type=int, default=1, metavar="N",
                    help="which audit, for a lesson that runs several (default 1)")
    ap.add_argument("--no-audit", action="store_true", help="skip the audit")
    a = ap.parse_args()

    # A Windows console that is not UTF-8 raises on the first dash it meets.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    sid = a.lesson.upper()
    cur = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf8"))
    titles = {s["id"]: s["title"] for f in cur["functions"]
              for t in f["tracks"] for s in t["sessions"]}
    if sid not in titles:
        print(f"{sid} is not a lesson. `python3 scripts/checkpoint.py --list` "
              f"shows the ids.", file=sys.stderr)
        return 1
    title = titles[sid]
    print(f"{sid} — {title}\n")

    out = a.out.resolve()
    print("1 · getting the code …")
    code = get_code(sid, out, a.force)
    print(f"    {'ok' if code['ok'] else 'FAILED'}: "
          + (f"{code['files']} files" if code["ok"] else code["note"]))

    diff = test = audit = None
    if code["ok"]:
        print("2 · working out what this lesson added …")
        diff = what_changed(sid)
        print("3 · running the tests that exist at this point …")
        test = smoke(out)
        print(f"    {test['status']}")

    found = audit_at(sid, a.audit)
    which, total = a.audit, len(audits_of(sid))
    if code["ok"] and found and not a.no_audit:
        ref, script, kind, total = found
        print(f"4 · the audit, skills/{ref}"
              + (f" ({which} of {total})" if total > 1 else "") + " …")
        if kind == "demo":
            audit = audit_via_runtime(sid, script)
        elif a.answer:
            audit = audit_validate(sid, script, a.answer)
        elif a.use_runtime or sid in RUNTIME_LESSONS:
            audit = audit_via_runtime(sid, script)
            if audit["status"] == "refused" and not a.use_runtime:
                # The runtime has no model. The agent that called this is one,
                # so hand it the task rather than stopping at a route the
                # learner is not using.
                audit = {**audit_task(sid, script), "fallback": True}
        else:
            audit = audit_task(sid, script)
        if audit["status"] == "waiting":
            print("\n" + "-" * 68)
            print("THE AUDIT — answer this yourself, following the skill above.")
            print("Reply with one JSON object and nothing invented, then run:")
            print(f"  python3 scripts/lesson.py {sid} --audit {which} "
                  f"--answer work/answer.json")
            print("-" * 68)
            print(audit["prompt"])
            print("-" * 68)
        elif audit.get("output"):
            print(audit["output"])
    elif not found:
        print("4 · no audit for this lesson." if not audits_of(sid)
              else f"4 · this lesson has {total} audit(s); --audit {a.audit} "
                   f"is out of range.")

    text, rc = readback(sid, title, code, diff, test, audit, bool(audits_of(sid)),
                        out, which, total)
    print(text)
    return rc


if __name__ == "__main__":
    sys.exit(main())
