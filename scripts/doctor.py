#!/usr/bin/env python3
"""Check this machine can do the lessons, and say what to fix if it cannot.

Students testing Function A asked for one thing more than any other: "check
their actual computer, and explain how to fix setup errors". A0.0 told a reader
to type `git --version` and `python3 --version` and compare the output against a
sentence, which works until the answer is something the sentence did not
anticipate — and on Windows `python3` is not the command, so the very first
check misfired for a third of readers.

This asks the machine instead. Every check prints one line and, when it fails,
the command that fixes it for the platform it is actually running on.

    python3 scripts/doctor.py

Exit codes: 0 everything needed is present, 1 something required is missing.
Optional things that are absent are reported and do not fail the run — a reader
with no model configured can still do the third way of every lesson, and saying
"broken" to them would be a lie.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WINDOWS = platform.system() == "Windows"
# Spelled out here rather than inline, because an f-string cannot carry the
# backslashes a Windows venv path needs.
VENV_PIP = ".venv\\Scripts\\pip" if WINDOWS else ".venv/bin/pip"

# The results, so the summary counts rather than re-deriving.
FAILED: list[str] = []
MISSING_OPTIONAL: list[str] = []


def say(ok: bool | None, what: str, detail: str = "", fix: str = "") -> None:
    """One line per check. `ok=None` means optional and absent."""
    mark = {True: "  ok  ", False: " FAIL ", None: " --   "}[ok]
    print(f"{mark}{what:<34}{detail}")
    if fix and ok is not True:
        for line in fix.splitlines():
            print(f"        {line}")
    if ok is False:
        FAILED.append(what)
    elif ok is None:
        MISSING_OPTIONAL.append(what)


def version_of(*cmd: str) -> str | None:
    """First line of `cmd --version`, or None if it will not run."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                           encoding="utf8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    out = (r.stdout + r.stderr).strip().splitlines()
    return out[0] if out else None


def check_python() -> None:
    v = sys.version_info
    want = (3, 10)
    detail = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= want:
        say(True, "python", detail)
    else:
        say(False, "python", f"{detail}, need 3.10 or newer",
            "Install from https://www.python.org/downloads/ and open a new "
            "terminal.")

    # The Windows tell. `python3` on Windows is usually a Store stub that prints
    # nothing useful or opens the Microsoft Store, so A0.0 telling everyone to
    # type `python3 --version` sent Windows readers to a dead end on line one.
    if WINDOWS:
        say(True, "the command to type", "python  (not python3, on Windows)",
            "If `python` opens the Microsoft Store, install Python from\n"
            "python.org and tick \"Add python.exe to PATH\", or use `py -3`.")


def check_git() -> None:
    v = version_of("git", "--version")
    if v:
        say(True, "git", v.replace("git version ", ""))
    else:
        say(False, "git", "not found",
            "https://git-scm.com/downloads, then open a NEW terminal — a "
            "terminal only\nnotices a new program when it starts.")


def check_repo() -> None:
    """Are we actually inside the commons, and is it complete?"""
    needed = [("skills", "the 140 skills"), ("scripts", "the harness"),
              ("cybertravels", "the application the lessons build"),
              ("site/data/curriculum.json", "the lesson list")]
    missing = [name for name, _ in needed if not (ROOT / name).exists()]
    if missing:
        say(False, "the repository", f"missing {', '.join(missing)}",
            "Run this from inside the folder you cloned:\n"
            "  git clone --branch master "
            "https://github.com/spbreed/cyber-commons.git\n"
            "  cd cyber-commons")
        return
    n = len(list((ROOT / "skills").glob("*/*/SKILL.md")))
    say(True, "the repository", f"{ROOT}, {n} skills")


def check_model() -> None:
    """Optional, and the reason it is optional matters.

    Way 3 of every lesson needs no model. Reporting "no model" as a failure
    would tell a reader with no account that the repository is broken, which is
    the error A0.0 spends a section avoiding.
    """
    claude = shutil.which("claude")
    base = os.environ.get("OPENAI_BASE_URL")
    key = os.environ.get("OPENAI_API_KEY")
    if claude:
        say(True, "a model", f"claude CLI at {claude} (no API key needed)")
    elif base and key:
        say(True, "a model", f"OPENAI_BASE_URL={base}, "
                             f"MODEL={os.environ.get('MODEL', '(unset!)')}")
    elif base or key:
        say(False, "a model", "half-configured",
            "Set all three: OPENAI_BASE_URL, OPENAI_API_KEY and MODEL.\n"
            "With only some of them set, a skill cannot tell what to call.")
    else:
        say(None, "a model", "none configured — ways 1 and 2 will exit 2",
            "Optional. Way 3 of every lesson (read the code and the diff) needs\n"
            "no model at all. A0.0 step 4 sets one up when you want one.")


def check_pyjwt() -> None:
    """Optional: only the smoke tests need it, and they skip cleanly."""
    # BaseException, not Exception, and that is not defensive padding: a broken
    # `cryptography` wheel makes `import jwt` raise pyo3's PanicException, which
    # does not inherit from Exception. This very machine does it. A doctor that
    # dies with a traceback while diagnosing a traceback is worse than no doctor,
    # so the one place that imports somebody else's compiled extension catches
    # everything and reports it as a finding.
    try:
        import jwt
        say(True, "PyJWT", f"{jwt.__version__} — the smoke tests can run")
    except BaseException as e:                               # noqa: BLE001
        kind = type(e).__name__
        if isinstance(e, ImportError):
            say(None, "PyJWT", "absent — smoke tests will report as skipped",
                "Optional, and a skip is not a failure. To run them:\n"
                f"  {'python' if WINDOWS else 'python3'} -m pip install PyJWT")
        else:
            say(None, "PyJWT", f"installed but will not import ({kind})",
                "Usually a broken `cryptography` build, not a broken PyJWT.\n"
                "The smoke tests will skip; everything else works. To fix it:\n"
                f"  {'python' if WINDOWS else 'python3'} -m pip install "
                f"--force-reinstall cryptography PyJWT\n"
                "or use a virtual environment, which is cleaner:\n"
                f"  {'python' if WINDOWS else 'python3'} -m venv .venv && "
                f"{VENV_PIP} install PyJWT")


def check_writable() -> None:
    probe = ROOT / "work"
    try:
        probe.mkdir(exist_ok=True)
        (probe / ".doctor").write_text("ok")
        (probe / ".doctor").unlink()
        say(True, "somewhere to write", f"{probe}")
    except OSError as e:
        say(False, "somewhere to write", str(e),
            "The lessons write the application into work/. Check the folder's\n"
            "permissions, or pass --out somewhere else.")


def check_install_targets() -> None:
    """What `install_skills.py` would change, named before it changes it.

    Students asked to be told what installed tools can change and how to remove
    them. A link into a home directory is a small thing and it is still a thing
    somebody should be told about before it happens.
    """
    homes = {"claude": Path.home() / ".claude" / "skills",
             "codex": Path.home() / ".codex" / "skills",
             "gemini": Path.home() / ".gemini" / "skills"}
    live = [f"{t} ({p})" for t, p in homes.items() if p.exists()]
    detail = "; ".join(live) if live else "none yet"
    say(True, "skill links", detail,
        "install_skills.py creates symlinks in those folders and writes\n"
        "nothing else anywhere. To remove every one of them:\n"
        f"  {'python' if WINDOWS else 'python3'} scripts/install_skills.py "
        f"--all --uninstall")


def main() -> int:
    print(f"cyber commons · doctor        {platform.system()} "
          f"{platform.release()}\n")
    check_python()
    check_git()
    check_repo()
    check_writable()
    check_model()
    check_pyjwt()
    check_install_targets()

    print()
    if FAILED:
        print(f"{len(FAILED)} thing(s) to fix: {', '.join(FAILED)}")
        print("Each one above has the command under it.")
        return 1
    if MISSING_OPTIONAL:
        print(f"Ready. {len(MISSING_OPTIONAL)} optional thing(s) absent: "
              f"{', '.join(MISSING_OPTIONAL)}.")
        print("You can start A1.0 now — way 3 of every lesson works without "
              "them.")
        return 0
    print("Ready for every lesson, every way.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
