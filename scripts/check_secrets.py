#!/usr/bin/env python3
"""Refuse to let a credential reach git history.

Run standalone (`python3 scripts/check_secrets.py`) or as a pre-commit hook
(`scripts/install-hooks.sh`). It scans tracked and staged files for the token
shapes this project actually handles — Kaggle API tokens above all, since the
Kaggle workflow in `scripts/kaggle_push.py` takes a live key.

The rule for this repo is absolute: **credentials live in ~/.kaggle/kaggle.json
or the environment, never in the tree.** This script is the enforcement.

Exit status: 0 clean, 1 something credential-shaped was found.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Each rule is (name, compiled pattern). Patterns are deliberately narrow: a
# scanner that cries wolf gets disabled, and a disabled scanner catches nothing.
RULES = [
    ("Kaggle API token", re.compile(r"KGAT_[A-Za-z0-9]{16,}")),
    ("Kaggle legacy key in JSON", re.compile(r'"key"\s*:\s*"[0-9a-f]{32}"')),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9]{32,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

# This file states the token shapes it hunts for, so it would flag itself.
SELF = {"scripts/check_secrets.py"}

# Values that are credential-shaped but publicly documented as non-credentials.
# The blind IaC corpus is deliberately-vulnerable Terraform — hardcoded keys are
# the finding the benchmark is testing for, so they have to stay in the tree.
# Allowlisting the literal values keeps the rule tight: a *real* AKIA in the
# same file still trips the scanner.
FIXTURES = {
    "AKIAIOSFODNN7EXAMPLE",     # AWS's own documented example access key id
    "AKIAIOSFODNN7EXAMAAA",     # variant used in the blind corpus
}


def tracked_files() -> list[str]:
    """Files git knows about, plus anything staged for this commit."""
    def git(*args: str) -> list[str]:
        p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
        return [ln for ln in p.stdout.splitlines() if ln.strip()]

    return sorted(set(git("ls-files")) | set(git("diff", "--cached", "--name-only")))


def main() -> int:
    hits: list[tuple[str, str, int, str]] = []
    for rel in tracked_files():
        if rel in SELF:
            continue
        f = ROOT / rel
        if not f.is_file():
            continue                      # deleted in this commit
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        for name, pat in RULES:
            for m in pat.finditer(text):
                if m.group(0) in FIXTURES:
                    continue
                line = text.count("\n", 0, m.start()) + 1
                # never echo the secret itself into logs or CI output
                hits.append((rel, name, line, m.group(0)[:6] + "…"))

    if hits:
        print("BLOCKED — credential-shaped content in tracked files:\n", file=sys.stderr)
        for rel, name, line, redacted in hits:
            print(f"  {rel}:{line}  {name}  ({redacted})", file=sys.stderr)
        print("\nMove it to ~/.kaggle/kaggle.json or an environment variable and "
              "remove it from the tree.", file=sys.stderr)
        return 1

    print(f"ok: no credentials in {len(tracked_files())} tracked files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
