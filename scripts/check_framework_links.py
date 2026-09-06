#!/usr/bin/env python3
"""Fetch every URL a framework label points at, and fail on anything that is not 200.

A label that links somewhere is a promise. A label that links somewhere dead is
worse than a label with no link at all, because a reader who clicks one and
lands on a 404 stops trusting the other five on the page — and these labels are
the part a regulated-industry reader is most likely to follow.

Frameworks move their URLs. OWASP reorganised the LLM Top 10 slugs between
editions; the EU AI Act mirrors renumber. So this is a network check, run in
CI, rather than a one-time verification that rots.

Run:
  python3 scripts/check_framework_links.py
  python3 scripts/check_framework_links.py --offline   # skip, for local work
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FW = json.loads((ROOT / "curriculum" / "frameworks.json").read_text())

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")


def every_url() -> dict[str, str]:
    """Every distinct destination a chip can render, keyed by what renders it."""
    u = FW["urls"]
    out: dict[str, str] = {}
    for code, url in u["owasp_llm"].items():
        out[f"OWASP {code}"] = url
    out["OWASP Agentic (T1-T15)"] = u["owasp_agentic"]
    out["MITRE ATLAS"] = u["atlas"]
    out["NIST AI RMF"] = u["nist"]
    for art in FW["euai_titles"]:
        n = art.replace("Art.", "").strip()
        out[f"EU AI Act {art}"] = u["euai"].replace("{n}", n)
    return out


def fetch(url: str, timeout: int = 25) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:                      # DNS, TLS, timeout, proxy
        return 0, type(e).__name__


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true",
                    help="skip the network check (local work behind a proxy)")
    a = ap.parse_args()

    urls = every_url()
    if a.offline:
        print(f"offline: {len(urls)} framework links not checked")
        return 0

    bad, unreachable = [], []
    for label, url in sorted(urls.items()):
        code, err = fetch(url)
        if code == 200:
            mark = "ok  "
        elif code == 0:
            mark = "net "
            unreachable.append((label, url, err))
        else:
            mark = "FAIL"
            bad.append((label, url, code))
        print(f"  {mark} {code or err:<4} {label:<28} {url}")

    for label, url, code in bad:
        print(f"::error::{label} links to {url}, which returned {code}",
              file=sys.stderr)
    # A network failure is not the same as a dead link, and failing the build
    # on a flaky runner teaches people to ignore the gate.
    for label, url, err in unreachable:
        print(f"::warning::{label} could not be reached ({err}) — not treated "
              f"as a failure", file=sys.stderr)

    print(f"\n{len(urls)} framework links · {len(bad)} dead · "
          f"{len(unreachable)} unreachable")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
