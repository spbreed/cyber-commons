#!/usr/bin/env python3
"""Upload a lightboard recording to YouTube and register it against a session.

Used by .github/workflows/publish-video.yml, and runnable locally.

Auth uses an OAuth **refresh token** (no browser in CI). Create one once:
  1. Google Cloud console → enable "YouTube Data API v3"
  2. Create an OAuth client (type: Desktop) → note client id + secret
  3. Run:  python3 scripts/youtube_upload.py --auth-setup
     and follow the printed URL to mint a refresh token.
  4. Store as repo secrets: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

Then:
    python3 scripts/youtube_upload.py --session A2.5 --file recordings/a2.5.mp4 \
        --privacy unlisted

    python3 scripts/youtube_upload.py --session A2.5 --file x.mp4 --dry-run
        # prints the exact metadata and does not call YouTube

Title/description/tags are generated from curriculum.json so every video is
labelled consistently and links back to the chapter.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text())
SITE_URL = os.environ.get("SITE_URL", "https://spbreed.github.io/cyber-commons/")

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


def find_session(sid: str):
    for s in CUR["module0"]["sessions"]:
        if s["id"] == sid:
            return s, CUR["module0"]["title"], "Module 0"
    for fn in CUR["functions"]:
        for tr in fn["tracks"]:
            for s in tr["sessions"]:
                if s["id"] == sid:
                    return s, tr["title"], f"Function {fn['id']} — {fn['title']}"
    return None, None, None


def build_metadata(sid: str, privacy: str, playlist_note: str = "") -> dict:
    s, track_title, fn_title = find_session(sid)
    if not s:
        raise SystemExit(f"error: '{sid}' is not a session id in curriculum.json")
    title = f"{sid} — {s['title']} | Cyber Commons"
    desc = [
        f"{fn_title} · {track_title}", "",
        f"RISK — {s.get('risk','')}", "",
        f"CONTROL — {s.get('control','')}", "",
        f"LAB — {s.get('lab','')}", "",
    ]
    if s.get("tools"):
        desc.append("Tools: " + ", ".join(s["tools"]))
    if s.get("models"):
        desc.append("Open-weight models: " + ", ".join(s["models"]))
    desc += ["",
             "Cyber Commons is a free, open commons for Cyber AI — every lab runs on",
             "open-source tooling and open-weight models. No frontier-lab account needed.",
             ""]
    if SITE_URL:
        desc.append(f"Chapter + runnable lab: {SITE_URL}#curriculum")
    if playlist_note:
        desc.append(playlist_note)
    tags = ["cyber commons", "AI security", "agentic security", sid,
            track_title, "open source security", "lightboard"]
    return {
        "snippet": {"title": title[:100], "description": "\n".join(desc)[:4900],
                    "tags": [t[:30] for t in tags][:15], "categoryId": "28"},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }


def access_token() -> str:
    import urllib.parse, urllib.request
    cid = os.environ.get("YT_CLIENT_ID")
    csec = os.environ.get("YT_CLIENT_SECRET")
    rtok = os.environ.get("YT_REFRESH_TOKEN")
    if not all([cid, csec, rtok]):
        raise SystemExit("error: set YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN "
                         "(see --auth-setup)")
    body = urllib.parse.urlencode({
        "client_id": cid, "client_secret": csec,
        "refresh_token": rtok, "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=body), timeout=60) as r:
        return json.loads(r.read())["access_token"]


def upload(path: Path, meta: dict) -> str:
    """Resumable upload; returns the YouTube video id."""
    import urllib.request
    tok = access_token()
    size = path.stat().st_size
    init = urllib.request.Request(
        f"{UPLOAD_URL}?uploadType=resumable&part=snippet,status",
        data=json.dumps(meta).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                 "X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/*"})
    with urllib.request.urlopen(init, timeout=120) as r:
        session_url = r.headers["Location"]
    put = urllib.request.Request(session_url, data=path.read_bytes(), method="PUT",
                                 headers={"Authorization": f"Bearer {tok}",
                                          "Content-Length": str(size)})
    with urllib.request.urlopen(put, timeout=3600) as r:
        return json.loads(r.read())["id"]


def auth_setup():
    print(__doc__.split("Then:")[0])
    print("\nOnce you have client id/secret, mint a refresh token with:\n")
    print("  pip install google-auth-oauthlib")
    print("  python3 - <<'EOF'\n"
          "from google_auth_oauthlib.flow import InstalledAppFlow\n"
          "f = InstalledAppFlow.from_client_config(\n"
          "  {'installed':{'client_id':'<ID>','client_secret':'<SECRET>',\n"
          "   'auth_uri':'https://accounts.google.com/o/oauth2/auth',\n"
          "   'token_uri':'https://oauth2.googleapis.com/token'}},\n"
          "  ['https://www.googleapis.com/auth/youtube.upload'])\n"
          "c = f.run_local_server(port=0)\n"
          "print('YT_REFRESH_TOKEN=', c.refresh_token)\nEOF")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session")
    ap.add_argument("--file")
    ap.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"])
    ap.add_argument("--dry-run", action="store_true", help="print metadata, upload nothing")
    ap.add_argument("--auth-setup", action="store_true")
    a = ap.parse_args()

    if a.auth_setup:
        auth_setup()
        return 0
    if not a.session:
        print("error: --session is required", file=sys.stderr)
        return 2

    meta = build_metadata(a.session, a.privacy)
    if a.dry_run:
        print(json.dumps(meta, indent=1))
        print("\n[dry-run] nothing uploaded.")
        return 0

    path = Path(a.file or "")
    if not path.is_file():
        print(f"error: recording not found: {path}", file=sys.stderr)
        return 2
    vid = upload(path, meta)
    print(f"uploaded: https://www.youtube.com/watch?v={vid}")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "link_video.py"),
                    "--session", a.session, "--youtube-id", vid,
                    "--title", meta["snippet"]["title"]], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
