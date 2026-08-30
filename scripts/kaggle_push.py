#!/usr/bin/env python3
"""Push Cyber Commons lab notebooks to Kaggle and run them there.

Credentials are read in this order, and **never** from the repository:

  1. $KAGGLE_USERNAME + $KAGGLE_KEY
  2. $KAGGLE_CONFIG_DIR/kaggle.json
  3. ~/.kaggle/kaggle.json

Auth note: `KGAT_`-prefixed Kaggle tokens are **Bearer** tokens. The older
username+key Basic scheme returns 401 for them, which reads like a bad
credential rather than a wrong scheme — hence the explicit handling here.

If a credential file is found inside this repository the script refuses to run.
`scripts/check_secrets.py` enforces the same rule at commit time.

Usage
-----
  python3 scripts/kaggle_push.py --check                 # auth + reachability only
  python3 scripts/kaggle_push.py --session A2.5          # push one notebook
  python3 scripts/kaggle_push.py --all                   # push all of them
  python3 scripts/kaggle_push.py --all --wait            # push, then poll status
  python3 scripts/kaggle_push.py --all --public          # needs a verified phone

Kernels are created **private** by default. Kaggle rejects a public push with
HTTP 403 unless the owning account has a verified phone number.

Each notebook becomes a Kaggle kernel named `cyber-commons-<id>`; Kaggle runs it
on push, so "did it execute remotely" is answered by `--wait`, which polls the
kernel status endpoint and reports `complete` / `error` per session.

Network note: Kaggle's API hosts must be reachable. In restricted egress
environments (`kaggle.com` blocked at the proxy) `--check` fails fast and says
so rather than pretending the push happened.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "labs" / "notebooks"
API = "https://www.kaggle.com/api/v1"


# --------------------------------------------------------------- credentials
def credentials() -> tuple[str, str]:
    """(username, key) from the environment or a config file outside the repo."""
    user, key = os.environ.get("KAGGLE_USERNAME"), os.environ.get("KAGGLE_KEY")
    if user and key:
        return user, key

    candidates = []
    if cfg := os.environ.get("KAGGLE_CONFIG_DIR"):
        candidates.append(Path(cfg) / "kaggle.json")
    candidates.append(Path.home() / ".kaggle" / "kaggle.json")

    for path in candidates:
        if not path.is_file():
            continue
        # a credential file inside the repo is a mistake we refuse to normalise
        try:
            path.resolve().relative_to(ROOT)
        except ValueError:
            pass                                  # outside the repo — good
        else:
            sys.exit(f"refusing to read credentials from inside the repo: {path}\n"
                     "Move kaggle.json to ~/.kaggle/kaggle.json.")
        data = json.loads(path.read_text())
        return data["username"], data["key"]

    sys.exit("no Kaggle credentials found.\n"
             "Set KAGGLE_USERNAME + KAGGLE_KEY, or place kaggle.json at "
             "~/.kaggle/kaggle.json (chmod 600). Never commit it.")


def call(path: str, payload: dict | None = None, timeout: int = 120) -> dict:
    """POST (or GET) the Kaggle API.

    Two Kaggle-specific traps are handled here:

      * `KGAT_` tokens authenticate as **Bearer**, not Basic.
      * `/kernels/push` answers **HTTP 200 with `hasError: true`** when it
        rejects a push. Checking only the status code reports every failed
        push as a success, so the body is inspected and raised.
    """
    _, key = credentials()
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{API}{path}", data=body,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json",
                 "User-Agent": "cyber-commons-lab-push"},
        method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read().decode())
    if isinstance(out, dict) and out.get("hasError"):
        raise RuntimeError(out.get("error") or "kaggle rejected the request")
    return out


# ------------------------------------------------------------------- pushing
def push(session: str, username: str, private: bool = True) -> dict:
    """Create/update the kernel for one session. Kaggle runs it on push."""
    nb = NB_DIR / f"{session}.ipynb"
    if not nb.is_file():
        raise FileNotFoundError(f"no notebook for {session}: {nb}")
    slug = f"cyber-commons-{session.lower().replace('.', '-')}"
    return call("/kernels/push", {
        # `id` is an integer field; the string form of a kernel is `slug`,
        # qualified with the owning account.
        "slug": f"{username}/{slug}",
        "newTitle": f"Cyber Commons {session}",
        "text": nb.read_text(),
        "language": "python",
        "kernelType": "notebook",
        # Private by default: Kaggle refuses a public push with HTTP 403
        # "Phone verification is required to make a notebook public" unless the
        # owning account has verified a phone number. That is an account
        # setting, not something this script can or should work around — pass
        # --public once the account is verified.
        "isPrivate": private,
        # the labs are stdlib-only by design, so they pass with the internet off
        "enableInternet": False,
        "enableGpu": False,
        "datasetDataSources": [],
        "competitionDataSources": [],
        "kernelDataSources": [],
        "categoryIds": ["cybersecurity"],
    })


def status(session: str, username: str) -> dict:
    slug = f"cyber-commons-{session.lower().replace('.', '-')}"
    return call(f"/kernels/status?userName={username}&kernelSlug={slug}")


def sessions(arg_session: str | None, want_all: bool) -> list[str]:
    if arg_session:
        return [arg_session]
    if want_all:
        return sorted(p.stem for p in NB_DIR.glob("*.ipynb"))
    sys.exit("pass --session <ID> or --all")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="one session id, e.g. A2.5")
    ap.add_argument("--all", action="store_true", help="every notebook in labs/notebooks")
    ap.add_argument("--check", action="store_true", help="verify auth + reachability, push nothing")
    ap.add_argument("--wait", action="store_true", help="poll until each kernel finishes")
    ap.add_argument("--public", action="store_true",
                    help="publish the kernels publicly (requires a phone-verified "
                         "Kaggle account; a 403 here means it is not verified)")
    ap.add_argument("--timeout", type=int, default=900,
                    help="seconds to wait for each batch to finish")
    ap.add_argument("--concurrency", type=int, default=4,
                    help="kernels in flight at once (Kaggle's ceiling is 5)")
    a = ap.parse_args()

    user, _ = credentials()
    print(f"authenticating to Kaggle as {user}")

    if a.check:
        try:
            me = call("/kernels/list?pageSize=1")
        except urllib.error.HTTPError as e:
            print(f"auth reached Kaggle but was rejected: HTTP {e.code} {e.reason}\n"
                  "A 401 here usually means the token is being sent as Basic; "
                  "KGAT_ tokens are Bearer.", file=sys.stderr)
            return 1
        except urllib.error.URLError as e:
            print(f"cannot reach {API}: {e.reason}\n"
                  "If this is a proxy denial, Kaggle is blocked by egress policy — "
                  "run this script from a machine with Kaggle access.", file=sys.stderr)
            return 1
        print(f"ok: credentials valid as '{user}', API reachable "
              f"({len(me)} kernel(s) visible)")
        return 0

    todo = sessions(a.session, a.all)
    print(f"pushing {len(todo)} notebook(s) in batches of {a.concurrency} "
          f"(Kaggle allows 5 concurrent batch CPU sessions)")
    # Start from whatever is already on record. A single-session push must
    # amend the ledger, not replace it: overwriting it with one row silently
    # discards the evidence that the other 107 kernels ran.
    results: dict[str, str] = {}
    try:
        results = json.loads((NB_DIR / "_kaggle_push.json").read_text())["results"]
    except (OSError, KeyError, json.JSONDecodeError):
        pass

    # ...but a lesson that has been renumbered or merged away is no longer
    # evidence of anything. Left in, its row sends the verifier looking for a
    # notebook that does not exist.
    live = {p.stem for p in NB_DIR.glob("*.ipynb")}
    if stale := sorted(set(results) - live):
        print(f"dropping {len(stale)} ledger row(s) for sessions that no longer "
              f"exist: {', '.join(stale)}")
        results = {s: v for s, v in results.items() if s in live}

    def push_one(sid: str) -> str:
        """Push with backoff. Returns a URL, or a string starting with ERROR."""
        for attempt in range(6):
            try:
                return push(sid, user, private=not a.public).get("url", "pushed")
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="replace")
                if e.code == 403 and "Phone verification" in body:
                    return ("ERROR HTTP 403 — the Kaggle account needs a verified "
                            "phone number before notebooks can be public; "
                            "drop --public or verify it")
                if e.code == 429:                       # rate limited
                    time.sleep(min(2 ** attempt * 5, 60)); continue
                return f"ERROR HTTP {e.code} {body[:80]}"
            except RuntimeError as e:                   # hasError in the body
                if "Maximum batch" in str(e):           # concurrency ceiling
                    time.sleep(20); continue
                return f"ERROR {e}"
            except Exception as e:                      # noqa: BLE001
                return f"ERROR {e}"
        return "ERROR retries exhausted (rate limit or concurrency ceiling)"

    def wait_for(batch: list[str], deadline: float) -> None:
        """Poll until every kernel in the batch reaches a terminal state."""
        pending = list(batch)
        while pending and time.time() < deadline:
            time.sleep(15)
            for sid in list(pending):
                try:
                    st = status(sid, user).get("status", "")
                except Exception:                       # noqa: BLE001 — transient
                    continue
                if st in ("complete", "error", "cancelAcknowledged"):
                    print(f"      {sid:8s} {st}")
                    results[sid] = st
                    pending.remove(sid)
        for sid in pending:
            results[sid] = "timeout"
            print(f"      {sid:8s} timeout")

    batches = [todo[i:i + a.concurrency] for i in range(0, len(todo), a.concurrency)]
    for n, batch in enumerate(batches, 1):
        print(f"\n[batch {n}/{len(batches)}] {batch}")
        launched = []
        for sid in batch:
            results[sid] = push_one(sid)
            ok = not results[sid].startswith("ERROR")
            print(f"   {sid:8s} {'→ ' + results[sid] if ok else results[sid][:88]}")
            if ok:
                launched.append(sid)
        # Kaggle runs a kernel on push, so the batch must finish before the next
        # one starts or every subsequent push hits the concurrency ceiling.
        if launched and a.wait:
            wait_for(launched, time.time() + a.timeout)

    out = NB_DIR / "_kaggle_push.json"
    out.write_text(json.dumps({"user": user, "results": results}, indent=1) + "\n")
    print(f"\nwrote {out.relative_to(ROOT)}")
    failed = [s for s, v in results.items() if v.startswith("ERROR") or v in ("error", "timeout")]
    if failed:
        print(f"{len(failed)} failed: {failed}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
