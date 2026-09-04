---
name: how-a-lesson-runs
description: >-
  Load an agent skill and execute it the way every lesson in this commons does —
  read the SKILL.md, split its frontmatter from its procedure, check its output
  contract, and run its script — using one shared runtime rather than a copy per
  notebook. Use to learn the mechanism, or to wire the same runtime into your own
  notebooks.
allowed-tools: Read, Grep, Glob
---

# How a lesson runs

Every lesson here does the same three things, in the same order, and this skill
is that procedure applied to itself. Reading it is the fastest way to understand
what the other 116 lessons are doing, and to do it in a notebook of your own.

## When to use this

First — before any other lesson, if you want to know what you are looking at.
Again later, when you want to run these skills somewhere that is not this
repository.

## Procedure

**1 — Put the SKILL.md first.** The procedure is the thing being taught, so it
is the first cell. A notebook that opens on sixty lines of parser has put the
machinery above the point, and a reader who scrolls past machinery to reach the
content learns to scroll past it everywhere.

**2 — Load the shared runtime rather than carrying it.** The parser, the
contract checker and the model adapter are the same in every lesson. Carried
per notebook they were 9,730 lines of identical code that could only be fixed by
rebuilding everything. Loaded, they are one file with one place to fix.

On Kaggle the runtime is attached to the kernel as a **source** — a script
kernel, listed in `kernelDataSources`. Two things about that are worth knowing
before you rely on it, because neither is in the documentation and both cost an
afternoon:

- the attached script does **not** land on `sys.path`, and it is **not** named
  after the kernel — it is mounted as `__script__.py`, so it is loaded by path;
- the mount has two layouts, `/kaggle/input/<slug>/` and
  `/kaggle/input/notebooks/<user>/<slug>/`, and both occur. Match either.

**3 — Split the frontmatter from the body.** The frontmatter is what an agent
*routes* on — the description decides whether this skill fires at all — and the
body is what it follows once it does. They are different audiences for different
purposes, and a skill that blurs them fires at the wrong time.

**4 — Read the output contract, and check something against it.** The contract
is the JSON block under `## Output contract`. It is what makes a skill checkable
instead of aspirational — and it has a ceiling worth stating out loud: **an
empty result conforms perfectly.** Conformance is a statement about the
serialiser. Accuracy costs more.

**5 — Run the skill's own script.** Not a paraphrase of it: the file in
`skills/<area>/<name>/scripts/`. A lesson that reimplements what a skill does
teaches the reimplementation, and the two drift the first time either changes.

## Output contract

```json
{
  "skill": {"name": "str", "description_words": 0, "allowed_tools": ["str"], "procedure_lines": 0},
  "runtime": {"loaded_from": "kaggle|repository", "path": "str", "shared": true},
  "contract": {"keys": ["str"], "conforms": true, "conformance_proves_accuracy": false},
  "script": {"path": "str", "ran": true}
}
```

## Failure modes

- **Copying the runtime into each notebook.** It works, and then a fix means
  rebuilding all of them and hoping.
- **Reading conformance as correctness.** The empty result passes.
- **Importing the attached kernel by name.** It is not on the path and it is not
  called what you think; load it by path.
