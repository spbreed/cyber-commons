#!/usr/bin/env python3
"""Register a lightboard recording against a curriculum session.

Writes site/data/videos.json, which the website reads to show a ▶ Watch link on
the right chapter. Used both by hand and by the publish-video workflow after a
successful YouTube upload.

    python3 scripts/link_video.py --session A2.5 --youtube-id dQw4w9WgXcQ \
        --title "A2.5 — Delegation that survives audit"

    python3 scripts/link_video.py --list          # what's published, what's missing
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = ROOT / "site" / "data" / "curriculum.json"
VID = ROOT / "site" / "data" / "videos.json"


def all_sessions() -> dict[str, str]:
    c = json.loads(CUR.read_text())
    out = {s["id"]: s["title"] for s in c["module0"]["sessions"]}
    for fn in c["functions"]:
        for tr in fn["tracks"]:
            for s in tr["sessions"]:
                out[s["id"]] = s["title"]
    return out


def load() -> dict:
    if VID.exists():
        return json.loads(VID.read_text())
    return {"playlist": "", "videos": {}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="curriculum session id, e.g. A2.5 or M0.1")
    ap.add_argument("--youtube-id")
    ap.add_argument("--url", help="full URL instead of a YouTube id")
    ap.add_argument("--title")
    ap.add_argument("--duration", help="e.g. 24:10")
    ap.add_argument("--playlist", help="set the course playlist URL")
    ap.add_argument("--list", action="store_true", help="show coverage and exit")
    ap.add_argument("--remove", action="store_true", help="unregister the session")
    a = ap.parse_args()

    sessions = all_sessions()
    data = load()

    if a.list:
        pub = data.get("videos", {})
        try:
            print(f"published: {len(pub)}/{len(sessions)} sessions\n")
            for sid, title in sessions.items():
                mark = "▶" if sid in pub else "·"
                print(f"  {mark} {sid:6s} {title}")
        except BrokenPipeError:
            pass  # piped into head/less
        return 0

    if a.playlist:
        data["playlist"] = a.playlist

    if a.session:
        if a.session not in sessions:
            print(f"error: '{a.session}' is not a session id in curriculum.json.\n"
                  f"       run --list to see valid ids.", file=sys.stderr)
            return 2
        if a.remove:
            data.get("videos", {}).pop(a.session, None)
        else:
            if not (a.youtube_id or a.url):
                print("error: need --youtube-id or --url", file=sys.stderr)
                return 2
            entry = {"title": a.title or sessions[a.session], "published": date.today().isoformat()}
            if a.youtube_id:
                entry["youtube_id"] = a.youtube_id
            if a.url:
                entry["url"] = a.url
            if a.duration:
                entry["duration"] = a.duration
            data.setdefault("videos", {})[a.session] = entry

    data.setdefault("_note", "Registry of published lightboard recordings; keys are curriculum.json session ids.")
    VID.write_text(json.dumps(data, indent=1) + "\n")
    n = len(data.get("videos", {}))
    print(f"videos.json updated — {n}/{len(sessions)} sessions have a recording")
    return 0


if __name__ == "__main__":
    sys.exit(main())
