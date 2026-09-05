# Agent skills

121 skills the curriculum teaches you to write, and then uses. Each one is a
real `SKILL.md` — markdown with YAML frontmatter, the format a coding agent
actually loads — not an illustration of one. 121 of them carry a script
the lesson executes, and `test_skills.py` runs every one of those on every
build.

| area | skills |
|---|---|
| [`appsec/`](appsec) | 20 |
| [`architecture/`](architecture) | 2 |
| [`attestation/`](attestation) | 11 |
| [`detection/`](detection) | 11 |
| [`grc/`](grc) | 7 |
| [`identity/`](identity) | 5 |
| [`programme/`](programme) | 11 |
| [`redteam/`](redteam) | 4 |
| [`regulatory/`](regulatory) | 9 |
| [`research/`](research) | 10 |
| [`response/`](response) | 8 |
| [`runtime/`](runtime) | 6 |
| [`secops/`](secops) | 2 |
| [`threats/`](threats) | 16 |
| | **121** |

## How an agent loads these, and why the shape matters

An agent does not read a skill the way you are reading this page. It pulls in
detail progressively, only as the task calls for it, and a skill is worth
structuring around that:

| stage | what is loaded | when | budget |
|---|---|---|---|
| **metadata** | `name` and `description` | at startup, for **every** skill | ~100 tokens |
| **instructions** | the whole `SKILL.md` body | when the skill is activated | < 5,000 tokens |
| **resources** | `scripts/`, `references/`, `assets/` | only when actually needed | unbounded |

Three consequences, and each one is a rule in this repository:

**The description is the routing key, not a summary.** It is the only thing an
agent sees for a skill it has not activated, and it is paid for on every task
whether the skill fires or not. So it says *what the skill does* and *when to
reach for it*, in about a hundred tokens.
[`check_skills.py`](../scripts/check_skills.py) routes a sample of real tasks
across every description and fails on a tie, because two descriptions that
score the same mean the winner is whichever sorted first.

**The body stays small enough to be worth activating.** Every body here is
under 1,300 tokens against a 5,000 budget, and the gate is enforced. Anything
longer belongs in a resource.

**The bulk lives in `scripts/`, which is loaded only when it runs.** That is
why the procedure is prose and the fixture is a file: the agent reads the
procedure to decide *what* to do and opens the script only when it is going to
execute it.

## What every skill carries

- **`## When to use this`** — the activation conditions, in prose.
- **`## Procedure`** or **`## Step-by-step`** — numbered steps, each one an
  instruction rather than a description.
- **`## Example`** — a real input and the real opening lines of a real run.
  Not written by hand: taken from the script's own output and re-checked on
  every build, so it cannot drift from what the skill actually prints.
- **`## Output contract`** — the JSON shape the skill promises, which is what
  makes it checkable rather than aspirational.
- **`## Failure modes`** or **`## Common edge cases`** — the ways this
  procedure goes wrong in practice, including the ones that fail silently.

## The three parts, and what each is for

```yaml
---
name: appsec-vuln-audit
description: >-
  Audit code for vulnerabilities against a threat model, then deduplicate,
  verify in context, and filter to what is actually reachable. Use when asked
  to review code for security bugs ...
allowed-tools: Read, Grep, Glob, Bash
---
```

- **`name`** identifies it, and must match the directory.
- **`description`** is the **routing key**, not documentation. An agent decides
  whether to load a skill by reading this sentence and nothing else. A vague
  description never fires; two overlapping descriptions fire the wrong one.
- **`allowed-tools`** bounds it.

## The output contract

Every skill declares one, as a JSON block under `## Output contract`. It is
what makes a skill checkable instead of aspirational — the next stage joins
against those keys, and the lessons validate real output against them.

**A contract cannot tell you the answer is right.** Conformance is a statement
about the serialiser: it is close to free by construction, and an empty result
scores perfectly. Several lessons make exactly this point by passing the check
with a hollow result. Accuracy is the expensive part, and it lives outside the
schema.

## Using them

Copy a skill into your agent's skills directory:

```bash
cp -r skills/appsec/appsec-vuln-audit ~/.claude/skills/
```

Nothing in them is specific to this repository, and none of them require a
particular model or vendor.

## Checking them

```bash
python3 scripts/check_skills.py --check
```

Validates that every skill parses, names itself consistently, declares its
tools, carries a parseable contract, sits inside its loading budgets, and
carries the sections an activated agent needs — and that 19 plausible tasks
each route to exactly one skill with a non-zero margin. A tie is a real defect: the
winner would be decided by alphabetical order rather than by meaning. CI runs
this on every push.

## Editing them

The files here are the single source of truth. `build_notebooks.py` embeds them
verbatim into the lessons that use them, so a skill and the lesson teaching it
cannot drift — change a skill and the notebook is stale until rebuilt, which CI
fails on.

```bash
python3 scripts/build_notebooks.py   # re-embed
python3 scripts/run_notebooks.py     # prove the lessons still run
```

The sixty-line runtime the lessons use to parse, route and check skills lives in
[`scripts/exercises/skills.py`](../scripts/exercises/skills.py) and is emitted
into the notebooks as literal source, because a notebook carries every line it
runs.
