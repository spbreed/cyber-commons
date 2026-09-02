#!/usr/bin/env python3
"""Fetch what each Kaggle kernel actually printed, and check it against the local run.

`kaggle_push.py --wait` reports a kernel status of `complete`. That means Kaggle
finished executing it — it does **not** mean the notebook produced the right
output. A kernel that prints nothing at all also completes.

This script closes that gap: it pulls the remote stdout for every pushed kernel
and compares it line-for-line against a fresh local run of the same notebook.
Byte-identical output on two independent machines is the actual evidence that a
lesson runs — and, because the notebooks are deterministic by design, anything
less is a finding.

    python3 scripts/kaggle_verify.py              # verify every pushed kernel
    python3 scripts/kaggle_verify.py --session A1.1
    python3 scripts/kaggle_verify.py --save       # keep the remote stdout

Writes `labs/notebooks/_kaggle_verified.json`. Credentials are read the same way
as `kaggle_push.py` — environment or `~/.kaggle/kaggle.json`, never the repo.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
NB_DIR = ROOT / "labs" / "notebooks"
API = "https://www.kaggle.com/api/v1"

from kaggle_push import credentials, status  # noqa: E402  — same credential rules


def fetch_output(user: str, session: str, timeout: int = 90, attempts: int = 5) -> str:
    """The kernel's stdout, joined. Empty string if Kaggle returned none.

    Kaggle rate-limits a fast sweep of 108 kernels with HTTP 429. That is a
    "come back later", not a verification failure, so back off and retry rather
    than recording the session as unverified.
    """
    slug = f"cyber-commons-{session.lower().replace('.', '-')}"
    _, key = credentials()
    req = urllib.request.Request(
        f"{API}/kernels/output?userName={user}&kernelSlug={slug}",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "cyber-commons-verify"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503) or attempt == attempts - 1:
                raise
            # Respect Retry-After when Kaggle sends one; otherwise 4s, 8s, 16s…
            wait = int(e.headers.get("Retry-After") or 0) or 4 * 2 ** attempt
            print(f"  .... {session:8s} HTTP {e.code}, retrying in {wait}s")
            time.sleep(wait)

    log = body.get("log") or ""
    if not log:
        return ""
    try:
        entries = json.loads(log)
    except (json.JSONDecodeError, TypeError):
        return log if isinstance(log, str) else ""
    return "".join(e.get("data", "") for e in entries
                   if isinstance(e, dict) and e.get("stream_name") == "stdout")


# Anything that would move a lesson off its offline path. Kaggle has none of
# these, so neither may the local comparison run.
MODEL_ENV = {"ANTHROPIC_API_KEY", "ANTHROPIC_WORKSPACE_ID", "ANTHROPIC_BASE_URL",
             "OPENAI_API_KEY", "OPENAI_BASE_URL", "MODEL"}


def kernel_status(session: str, user: str, tries: int = 5) -> str:
    """Kaggle's status for one kernel, retrying through rate limits.

    `/kernels/status` returns HTTP 429 "TooManyRequests" well before 121
    sequential calls are done. Treating a 429 as "not complete" turns a
    transient throttle into a permanent skip, and the run then reports a
    smaller denominator as though that were the real one.
    """
    delay = 2.0
    for attempt in range(tries):
        try:
            return status(session, user).get("status", "unknown")
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                return "unknown"
            time.sleep(delay)
            delay *= 2
        except Exception:                         # noqa: BLE001 — reported by caller
            return "unknown"
    return "unknown"


def local_output(session: str) -> str:
    """Re-run the notebook locally, now, so both sides are compared identically.

    Comparing against the stored line count in _results.json is subtly wrong:
    that count includes blank lines, while Kaggle's log stream is normalised
    below. Re-running costs a tenth of a second and removes the discrepancy.
    """
    import os
    import subprocess
    nb = json.loads((NB_DIR / f"{session}.ipynb").read_text())
    src = "\n\n".join("".join(c["source"]) for c in nb["cells"]
                       if c["cell_type"] == "code")
    # Hermetic, deliberately. A Kaggle kernel has no model credentials, so the
    # lesson takes the replay path there. If the operator happens to have
    # ANTHROPIC_API_KEY exported, the local side takes the frontier path
    # instead and every model lesson "mismatches" — which is a fact about the
    # shell, not about the notebook, and it makes the whole claim of this
    # script ("the same thing on two machines") depend on who ran it.
    env = {k: v for k, v in os.environ.items()
           if k not in MODEL_ENV and not k.startswith("KAGGLE_")}
    p = subprocess.run([sys.executable, "-c", src], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=180)
    return p.stdout


def has_code(session: str) -> bool:
    """Does this lesson run anything at all?

    A1.1 is a drawing lesson with no code cells, so an empty remote log is the
    correct result for it rather than the failure it would be anywhere else.
    """
    nb = json.loads((NB_DIR / f"{session}.ipynb").read_text())
    return any(c["cell_type"] == "code" and "".join(c["source"]).strip()
               for c in nb["cells"])


def normalise(text: str) -> list[str]:
    """Kaggle's log stream splits on newlines differently; compare content."""
    return [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n") if ln.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="verify a single session id")
    ap.add_argument("--save", action="store_true", help="keep the remote stdout on disk")
    a = ap.parse_args()

    user, _ = credentials()

    try:
        pushed = json.loads((NB_DIR / "_kaggle_push.json").read_text())["results"]
    except OSError:
        sys.exit("no labs/notebooks/_kaggle_push.json — run scripts/kaggle_push.py first")

    # Everything the push ledger did not record as an error. The ledger's value
    # is the kernel URL after a plain `--all` push and the string "complete"
    # only after `--all --wait`, so filtering on "complete" silently verified
    # nothing whenever the push had not waited — and reported that as "no
    # kernels to verify" rather than as the bug it was.
    todo = ([a.session] if a.session
            else sorted(s for s, v in pushed.items()
                        if not str(v).startswith("ERROR")))
    if not todo:
        sys.exit("no successfully pushed kernels in the ledger — "
                 "run scripts/kaggle_push.py first")

    # Kaggle is the authority on whether a kernel finished, not the ledger.
    if not a.session:
        pending, unknown = [], []
        for sid in list(todo):
            st = kernel_status(sid, user)
            if st == "complete":
                continue
            (unknown if st == "unknown" else pending).append((sid, st))
            todo.remove(sid)
        if pending:
            print(f"{len(pending)} kernel(s) still running, skipped: "
                  f"{', '.join(f'{s} ({k})' for s, k in pending[:8])}"
                  f"{' …' if len(pending) > 8 else ''}\n")
        if unknown:
            # Never silently. A status this script could not read is a gap in
            # the evidence, not a kernel that failed and not one that passed.
            print(f"{len(unknown)} kernel(s) whose status could not be read "
                  f"even after retries — NOT verified, and not counted as "
                  f"either pass or fail: {', '.join(s for s, _ in unknown)}\n",
                  file=sys.stderr)
    if not todo:
        sys.exit("no kernels have finished running yet — try again in a minute")

    print(f"verifying {len(todo)} kernel(s) against the local run\n")
    rows, mismatched, empty = [], [], []
    for sid in todo:
        try:
            remote = fetch_output(user, sid)
        except urllib.error.HTTPError as e:
            rows.append({"session": sid, "ok": False, "why": f"HTTP {e.code}"})
            print(f"  {sid:8s} ERROR HTTP {e.code}")
            continue

        r_lines = normalise(remote)
        l_lines = normalise(local_output(sid))
        # Identical content, compared after the same normalisation. This is the
        # strong form: the two machines printed the same thing, not merely a
        # similar amount of it.
        identical = r_lines == l_lines
        runs_code = has_code(sid)
        # Empty remote output is a failure for a lesson that runs code — a
        # notebook printing nothing also reports 'complete'. For a lesson with
        # no code cells it is the only correct answer.
        ok = identical and (bool(r_lines) or not runs_code)
        if not r_lines and runs_code:
            empty.append(sid)
        elif not ok:
            mismatched.append(sid)
        first_diff = next((i for i, (x, y) in enumerate(zip(r_lines, l_lines))
                           if x != y), None)
        rows.append({"session": sid, "ok": ok, "identical": identical,
                     "runs_code": runs_code,
                     "remote_lines": len(r_lines), "local_lines": len(l_lines),
                     "first_differing_line": first_diff})
        mark = "ok  " if ok else "DIFF"
        detail = ((f"{len(r_lines):>4} lines, identical to the local run"
                   if r_lines else "   0 lines, and the lesson runs no code")
                  if ok
                  else f"remote {len(r_lines)} vs local {len(l_lines)}"
                       + (f", first diff at line {first_diff}" if first_diff is not None else ""))
        print(f"  {mark} {sid:8s} {detail}")

        if a.save:
            (NB_DIR / "_kaggle_output").mkdir(exist_ok=True)
            (NB_DIR / "_kaggle_output" / f"{sid}.txt").write_text(remote)

    passed = sum(r["ok"] for r in rows)
    summary = {
        "generated_by": "scripts/kaggle_verify.py",
        "account": user,
        "verified": passed,
        "checked": len(rows),
        "empty_output": empty,
        "line_count_mismatch": mismatched,
        "note": ("A kernel status of 'complete' only means Kaggle finished running "
                 "it — a notebook printing nothing also completes. Each row here "
                 "compares the kernel's remote stdout against a fresh local run of "
                 "the same notebook, after identical normalisation. 'identical: "
                 "true' means both machines printed exactly the same thing."),
        "results": rows,
    }
    if not a.session:
        (NB_DIR / "_kaggle_verified.json").write_text(json.dumps(summary, indent=1) + "\n")

    print(f"\n{passed}/{len(rows)} kernels printed exactly what the local run printed")
    if empty:
        print(f"empty remote output: {empty}", file=sys.stderr)
    if mismatched:
        print(f"line-count mismatch: {mismatched}", file=sys.stderr)
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
