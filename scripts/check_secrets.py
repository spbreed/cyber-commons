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
    # `sk-` keys are not one shape. The classic OpenAI key is `sk-` plus 48
    # alphanumerics, but an Anthropic key is `sk-ant-api03-...` and a modern
    # OpenAI project key is `sk-proj-...`, both of which carry hyphens and
    # underscores in the body. A rule anchored on alphanumerics alone matches
    # the classic form and silently misses the two that are actually issued
    # today — verified against real keys, which is the only way this gets
    # found.
    ("API key, sk- prefixed", re.compile(r"\bsk-(?:[a-z]{2,10}-)*[A-Za-z0-9_-]{24,}")),
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
    # The fake key in the Semgrep lab's target file. It is there because the
    # finding of that lab is that `p/secrets` does NOT flag it, so it has to
    # stay in the tree and be readable as a key.
    "sk-live-4f9a2b1c8e7d6a5b3c2d1e0f9a8b7c6d",
}


# Shapes the rules above MUST catch, and shapes they must not. These are the
# real formats issued today, with the secret bodies replaced by filler of the
# same length and character class — the originals were checked against this
# list once and are not in this repository. Run as `--self-test`; CI runs it.
MUST_DETECT = [
    "sk-ant-api03-" + "Aa0_" * 22 + "-og15NgAA",          # Anthropic
    "sk-proj-" + "Aa0_" * 20 + "T3BlbkFJ" + "Aa0" * 8,    # OpenAI project
    "sk-" + "A" * 48,                                      # OpenAI classic
    "KGAT_" + "0" * 32,                                    # Kaggle
    "ghp_" + "A" * 36,                                     # GitHub
    "-----BEGIN RSA PRIVATE KEY-----",
]
MUST_IGNORE = [
    "we pinned sk-learn and it was fine",
    "sk-abc",
    "the sk- prefix is common to several providers",
]


def self_test() -> int:
    """Check the rules against the shapes they exist for.

    This is here because the alphanumeric-only `sk-` rule matched the classic
    OpenAI key and silently missed both an Anthropic key and a modern OpenAI
    project key — both of which carry hyphens in the body. A scanner that is
    never tested against a real shape is a scanner nobody has checked.
    """
    bad = 0
    for s in MUST_DETECT:
        if not any(p.search(s) for _, p in RULES):
            print(f"  MISS  a credential shape is not detected: {s[:24]}...")
            bad += 1
    for s in MUST_IGNORE:
        hit = next((n for n, p in RULES if p.search(s)), None)
        if hit:
            print(f"  NOISE {hit!r} fires on ordinary text: {s!r}")
            bad += 1
    print(f"self-test: {len(MUST_DETECT)} shapes must match, "
          f"{len(MUST_IGNORE)} must not - {bad} problem(s)")
    return 1 if bad else 0


def tracked_files() -> list[str]:
    """Files git knows about, plus anything staged for this commit."""
    def git(*args: str) -> list[str]:
        p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
        return [ln for ln in p.stdout.splitlines() if ln.strip()]

    return sorted(set(git("ls-files")) | set(git("diff", "--cached", "--name-only")))


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
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
    return self_test()


if __name__ == "__main__":
    sys.exit(main())
