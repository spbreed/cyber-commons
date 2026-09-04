#!/usr/bin/env python3
"""Publish `skills/` to Kaggle as a dataset, so a kernel can run the real files.

A Kaggle kernel on this account **cannot clone the repository**: DNS does not
resolve inside the kernel even with internet enabled, because that requires a
phone-verified account. Probed rather than assumed —

    fatal: unable to access 'https://github.com/spbreed/cyber-commons/':
    Could not resolve host: github.com

So the repository reaches Kaggle the way Kaggle intends: as a **dataset**
attached to each notebook, mounted read-only at
`/kaggle/input/cyber-commons-skills/`. Same effect as a shallow clone of
`skills/`, no network, and it works on a free account.

    python3 scripts/kaggle_dataset.py --check    # is it published, and how old
    python3 scripts/kaggle_dataset.py            # create or update it

The dataset holds one zip of the skills tree; Kaggle expands it on ingest, so a
notebook sees `skills/<area>/<name>/SKILL.md` and `.../scripts/<name>.py` at
the paths they have in the repository.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from kaggle_push import API, call, credentials  # noqa: E402

SLUG = "cyber-commons-skills"
TITLE = "Cyber Commons skills"


def bundle() -> bytes:
    """The skills tree as a zip, deterministically ordered.

    Fixed timestamps and sorted names, so republishing an unchanged tree
    produces an identical archive. Kaggle keeps a version per upload; a
    non-deterministic bundle would mint one on every run.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT / "skills").rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts:
                continue
            info = zipfile.ZipInfo(str(p.relative_to(ROOT)), date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    return buf.getvalue()


def _request(path: str, payload: dict | None, key: str, method: str = "POST") -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"authorization": f"Bearer {key}",
                                          "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode() or "{}")


def upload(blob: bytes, name: str, key: str) -> str:
    """Kaggle's two-step upload: ask for a signed URL, then PUT the bytes.

    The registration must be **form-encoded**. Sent as JSON the endpoint
    returns 200 and a usable token, and silently drops the file name — the
    failure surfaces much later, at create time, as "Path must be non-null",
    which says nothing about where the name went.
    """
    req = urllib.request.Request(
        f"{API}/datasets/upload/file/{len(blob)}/{int(time.time())}",
        data=urllib.parse.urlencode({"fileName": name}).encode(),
        headers={"authorization": f"Bearer {key}",
                 "content-type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=120) as r:
        started = json.loads(r.read().decode())
    url = started.get("createUrl")
    if not url:
        raise SystemExit(f"no upload URL in the response: {started}")
    put = urllib.request.Request(url, data=blob, method="PUT",
                                 headers={"content-length": str(len(blob))})
    with urllib.request.urlopen(put, timeout=300):
        pass
    return started["token"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report whether the dataset exists, and stop")
    a = ap.parse_args()

    user, key = credentials()
    ref = f"{user}/{SLUG}"

    existing = call(f"/datasets/list?user={user}&search={SLUG}")
    published = any(d.get("ref") == ref for d in existing)
    print(f"dataset {ref}: {'published' if published else 'not published yet'}")
    if a.check:
        return 0

    blob = bundle()
    print(f"bundling skills/ -> {len(blob):,} bytes")
    token = upload(blob, "skills.zip", key)

    if published:
        out = _request(f"/datasets/create/version/{user}/{SLUG}",
                       {"versionNotes": "skills tree from the repository",
                        "files": [{"token": token}], "isPrivate": False,
                        "deleteOldVersions": False}, key)
    else:
        out = _request("/datasets/create/new",
                       {"title": TITLE, "slug": SLUG, "ownerSlug": user,
                        "licenseName": "CC0-1.0", "isPrivate": False,
                        "files": [{"token": token}],
                        "subtitleText": "Every agent skill in the Cyber Commons, "
                                        "with the script each one runs",
                        "descriptionText": "The skills tree from the repository, "
                                           "so a Kaggle kernel runs the real files.",
                        "categoryIds": []}, key)
    if out.get("error"):
        raise SystemExit(f"Kaggle refused it: {out['error']}")
    print(f"  -> {out.get('url', ref)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
