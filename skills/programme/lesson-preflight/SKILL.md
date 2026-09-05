---
name: lesson-preflight
description: >-
  Verify that a notebook host can fetch and execute a procedure that lives in a
  repository rather than in the notebook, and prove it by running one. Use
  before depending on a hosted notebook's output, when a lesson or shared
  notebook prints nothing, or when "it works on my machine" is the only
  evidence a procedure runs.
allowed-tools: Read, Glob, Bash
---

# Can this host actually run the procedure, and did it?

A notebook that carries its own code is easy to trust and impossible to
maintain: a fix means rebuilding every copy. A notebook that **fetches** its
code is the opposite — one fix, everywhere — and it buys that with a
dependency the reader cannot see. Two things have to be true before its output
means anything, and neither is visible in the output itself:

1. the procedure was **fetched**, and
2. the interpreter could **import what the procedure imports**.

When either is false the notebook does not print a wrong answer. It prints
nothing, or it prints a traceback, and a reader who scrolled past it will
report that the lesson is broken. This procedure makes both conditions
explicit, then demonstrates each failure before showing the success, so the
two error messages are recognised rather than debugged.

## When to use this

Before running anything out of a repository on a host you do not control —
Kaggle, Colab, a CI runner, a colleague's kernel. Also the first thing to run
when a notebook that used to work stops printing: it separates "the fetch
failed" from "the procedure failed", which are fixed in completely different
places.

## Procedure

**1 — Locate the tree, from the running file rather than the shell.** A
notebook's working directory is set by the host, not by you: it is the
repository root in a checkout and `/kaggle/working` on Kaggle. Resolve the
tree relative to the script's own path and the answer is the same in both.
A `cwd`-relative path here is the single most common reason a procedure runs
locally and not on the host.

**2 — Inventory what was fetched, not what should have been.** Count the
skills that carry both a `SKILL.md` and a script. A partial fetch — a sparse
checkout with the wrong path, a dataset attached at the wrong mount point — is
indistinguishable from a complete one until something is counted.

**3 — Reproduce failure (a): the tree was never fetched.** Run the procedure
against a root where it does not exist. The interpreter reports `[Errno 2]`
and exits before a single line of the procedure runs. This is what a host with
no network does, and it is a fetch problem, not a code problem.

**4 — Reproduce failure (b): the shared library is not on the path.** Run the
procedure with its runtime removed from `PYTHONPATH`. It gets further — the
file exists, the interpreter starts — and dies on `ModuleNotFoundError`. The
fetch was fine; the environment was not.

**5 — Run it correctly, and checksum the output.** Both conditions true, the
procedure runs. Record the line count and a CRC of the bytes. Two runs of the
same procedure that print different bytes are a defect in the procedure, and
without a checksum nobody notices until the diff is large.

## Example

**Input** — the fixture committed at the top of [`scripts/lesson_preflight.py`](scripts/lesson_preflight.py). Edit it and re-run: the buckets, counts and verdicts below are derived from it, not hard-coded.

**Output** — the opening lines of a real run:

```
the tree this host fetched
  areas            : 14
  skills           : 120
  with a script    : 119
  shared runtime   : present
  resolved from    : the running file, not the working directory

(a) the tree was never fetched  --  a host with no network
```

The run continues past this. The script is the example: `test_skills.py` executes it on every build, so this block cannot drift from what the skill actually prints.

## Output contract

```json
{
  "tree": {"areas": 0, "skills": 0, "with_script": 0, "runtime_present": true},
  "failures": [{"condition": "not-fetched|no-runtime-on-path", "exit_code": 1, "error": "str"}],
  "run": {"script": "str", "lines": 0, "crc32": "str", "exit_code": 0},
  "ready": true
}
```

`ready` is true only when both failures were reproduced **and** the correct run
exited zero. A preflight that reports readiness without having seen the
failures has tested one path out of three.

## Failure modes

- **Checking the working directory instead of the script's own location.**
  Passes on a checkout, fails on every host that sets `cwd` elsewhere — which
  is all of them.
- **Treating a silent run as a pass.** A procedure that exits zero and prints
  nothing has not run; it has been imported. Assert on the output, not the
  return code.
- **Reporting the count you expected.** Inventory the tree that is on disk. A
  hard-coded total turns a partial fetch into a clean report.
- **Checksumming a path.** Any absolute path in the output makes the CRC
  host-specific, and the check that was meant to prove reproducibility becomes
  the thing that breaks it.
