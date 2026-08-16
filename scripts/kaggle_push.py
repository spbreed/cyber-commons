#!/usr/bin/env python3
"""Push Cyber Commons lab notebooks to Kaggle and run them there.

Credentials are read in this order, and **never** from the repository:

  1. $KAGGLE_USERNAME + $KAGGLE_KEY
  2. $KAGGLE_CONFIG_DIR/kaggle.json
  3. ~/.kaggle/kaggle.json

If a credential file is found inside this repository the script refuses to run.
`scripts/check_secrets.py` enforces the same rule at commit time.

Usage
-----
  python3 scripts/kaggle_push.py --check                 # auth + reachability only
  python3 scripts/kaggle_push.py --session A2.5          # push one notebook
  python3 scripts/kaggle_push.py --all                   # push all 104
  python3 scripts/kaggle_push.py --all --wait            # push, then poll status

Each notebook becomes a Kaggle kernel named `cyber-commons-<id>`; Kaggle runs it
on push, so "did it execute remotely" is answered by `--wait`, which polls the
kernel status endpoint and reports `complete` / `error` per session.

Network note: Kaggle's API hosts must be reachable. In restricted egress
environments (`kaggle.com` blocked at the proxy) `--check` fails fast and says
so rather than pretending the push happened.
"""
from __future__ import annotations

import argparse
import base64
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


def call(path: str, payload: dict | None = None, timeout: int = 60) -> dict:
    """POST (or GET) the Kaggle API with HTTP basic auth."""
    user, key = credentials()
    token = base64.b64encode(f"{user}:{key}".encode()).decode()
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{API}{path}", data=body,
        headers={"Authorization": f"Basic {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "cyber-commons-lab-push"},
        method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


# ------------------------------------------------------------------- pushing
def push(session: str, username: str, private: bool = False) -> dict:
    """Create/update the kernel for one session. Kaggle runs it on push."""
    nb = NB_DIR / f"{session}.ipynb"
    if not nb.is_file():
        raise FileNotFoundError(f"no notebook for {session}: {nb}")
    slug = f"cyber-commons-{session.lower().replace('.', '-')}"
    return call("/kernels/push", {
        "id": f"{username}/{slug}",
        "title": f"Cyber Commons {session}",
        "newTitle": f"Cyber Commons {session}",
        "text": nb.read_text(),
        "language": "python",
        "kernelType": "notebook",
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
    ap.add_argument("--private", action="store_true", help="create kernels private")
    ap.add_argument("--timeout", type=int, default=900, help="seconds to wait per kernel")
    a = ap.parse_args()

    user, _ = credentials()
    print(f"authenticating to Kaggle as {user}")

    if a.check:
        try:
            me = call("/kernels/list?mine=true&pageSize=1")
        except urllib.error.HTTPError as e:
            print(f"auth reached Kaggle but was rejected: HTTP {e.code} {e.reason}", file=sys.stderr)
            return 1
        except urllib.error.URLError as e:
            print(f"cannot reach {API}: {e.reason}\n"
                  "If this is a proxy denial, Kaggle is blocked by egress policy — "
                  "run this script from a machine with Kaggle access.", file=sys.stderr)
            return 1
        print(f"ok: credentials valid, API reachable ({len(me)} kernels visible)")
        return 0

    todo = sessions(a.session, a.all)
    print(f"pushing {len(todo)} notebook(s)")
    results: dict[str, str] = {}
    for sid in todo:
        try:
            r = push(sid, user, private=a.private)
            results[sid] = r.get("url", "pushed")
            print(f"  {sid:8s} → {results[sid]}")
        except Exception as e:                      # noqa: BLE001 — report, keep going
            results[sid] = f"ERROR {e}"
            print(f"  {sid:8s} ! {e}", file=sys.stderr)

    if a.wait:
        print("\npolling kernel status")
        pending = [s for s in todo if not results[s].startswith("ERROR")]
        deadline = time.time() + a.timeout
        while pending and time.time() < deadline:
            time.sleep(15)
            for sid in list(pending):
                try:
                    st = status(sid, user).get("status", "")
                except Exception:                   # noqa: BLE001 — transient, retry
                    continue
                if st in ("complete", "error", "cancelAcknowledged"):
                    print(f"  {sid:8s} {st}")
                    results[sid] = st
                    pending.remove(sid)
        for sid in pending:
            results[sid] = "timeout"
            print(f"  {sid:8s} timeout")

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
