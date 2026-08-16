# Agent skills

Eleven skills the curriculum teaches you to write, and then uses. Each one is a
real `SKILL.md` — markdown with YAML frontmatter, the format a coding agent
actually loads — not an illustration of one.

```
skills/appsec/appsec-repo-recon/SKILL.md        phase 1 · stages 1-4
skills/appsec/appsec-threat-model/SKILL.md      phase 2 · stages 5-6
skills/appsec/appsec-vuln-audit/SKILL.md        phase 3 · stages 7-10
skills/appsec/appsec-exploit-validate/SKILL.md  phase 4 · stages 11-14
skills/appsec/appsec-triage-report/SKILL.md     phase 5 · stage 15
skills/appsec/coding-agent-hardening/SKILL.md   securing the agents themselves
skills/architecture/blast-radius-review/SKILL.md
skills/identity/agent-identity-review/SKILL.md
skills/secops/detection-triage/SKILL.md
skills/secops/incident-scoping/SKILL.md
skills/grc/control-evidence/SKILL.md
```

The first five compose into the fifteen-stage AppSec pipeline that the
[B1 track](../curriculum/) builds one stage at a time.

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
tools, carries a parseable contract — and that eleven plausible tasks each
route to exactly one skill with a non-zero margin. A tie is a real defect: the
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
