#!/usr/bin/env python3
"""Record which Kaggle kernels are publicly reachable, so the site can embed them.

A lesson page embeds its Kaggle kernel in an iframe. Kaggle's embedded viewer
only renders a kernel the visitor can see, and a private kernel renders as an
**empty frame with no error** — the worst possible failure, because the build is
green, the page looks finished, and the reader gets a blank rectangle.

So the embed is conditional, and this is what it is conditional on. Each kernel's
public URL is probed once; 200 means a visitor can see it, 404 means it is still
private. `build_site.py` embeds only the kernels listed here and falls back to
the recorded output for the rest, which is why a half-finished
`kaggle_push.py --all --public` degrades into the previous rendering rather than
into blank frames.

Re-run it after any public push:

    python3 scripts/kaggle_push.py --all --public
    python3 scripts/check_kaggle_public.py
    python3 scripts/build_site.py

    python3 scripts/check_kaggle_public.py --check   # CI: report, never fail

It never fails the build. Kaggle being unreachable from a CI runner is not a
reason to refuse a deploy, and the fallback is the safe direction.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
NB = ROOT / "labs" / "notebooks"
OUT = NB / "_kaggle_public.json"
OWNER = "cybercommons"


def slug(sid: str) -> str:
    """The kernel slug scripts/kaggle_push.py creates. Kept identical on purpose."""
    return f"cyber-commons-{sid.lower().replace('.', '-')}"


def sessions() -> list[str]:
    return [s["id"] for f in CUR["functions"] for t in f["tracks"]
            for s in t["sessions"]]


def runs_code(sid: str) -> bool:
    """Only a lesson with a code cell has anything to embed."""
    f = NB / f"{sid}.ipynb"
    if not f.is_file():
        return False
    return any(c["cell_type"] == "code"
               for c in json.loads(f.read_text()).get("cells", []))


def probe(sid: str) -> tuple[str, bool]:
    url = f"https://www.kaggle.com/code/{OWNER}/{slug(sid)}"
    # GET, not HEAD: Kaggle answers HEAD with 404 even for a public kernel, so
    # a HEAD probe reports every kernel private and silently disables every
    # embed. Found exactly that way.
    req = urllib.request.Request(url,
                                 headers={"User-Agent": "cyber-commons-site-build"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return sid, r.status == 200
    except urllib.error.HTTPError as e:
        return sid, e.code == 200
    except Exception:
        # Unreachable is not the same as private, but the safe answer is the
        # same: do not embed something we could not confirm.
        return sid, False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report only; this gate never fails a build")
    a = ap.parse_args()

    ids = [s for s in sessions() if runs_code(s)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(pool.map(probe, ids))

    public = sorted(k for k, v in results.items() if v)
    private = sorted(k for k, v in results.items() if not v)

    OUT.write_text(json.dumps({
        "_readme": "Kernels a visitor can see, so site/lessons embeds them. "
                   "Written by scripts/check_kaggle_public.py; a lesson not "
                   "listed renders its recorded output instead of an iframe.",
        "owner": OWNER,
        "public": public,
    }, indent=2) + "\n")

    print(f"{len(ids)} lesson(s) run a kernel · {len(public)} public · "
          f"{len(private)} not embeddable yet")
    if private:
        head = ", ".join(private[:12])
        print(f"  still private: {head}"
              f"{f' … and {len(private) - 12} more' if len(private) > 12 else ''}")
        print("  run: python3 scripts/kaggle_push.py --all --public")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
