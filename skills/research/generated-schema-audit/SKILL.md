---
name: generated-schema-audit
description: >-
  Audit a generated database scaffold for tables that hold secrets and carry no
  access policy, working from the catalogue rather than from the application's
  own queries. Use after any scaffold, migration or agent-authored schema
  change.
allowed-tools: Read, Grep, Glob
---

# Everything works, and two tables are open

A generated scaffold produces a schema that runs. Whether it is safe is a
different question and the application cannot answer it, because the application
only touches the tables it uses. The catalogue knows about all of them, and the
gap between those two sets is where this finding lives.

## When to use this

After a scaffold generator, an agent-authored migration, or any schema change
nobody reviewed statement by statement.

## Procedure

**1 — Read the statements as written.** Table by table, column by column. Flag
every column that holds a credential, a token, a session or personal data — an
`api_key` column in a profiles table is the shape to look for.

**2 — Check policy per table, not per application feature.** For each table:
does an access policy exist at all, and does it name a subject. "No policy" and
"a policy that permits everyone" are different findings.

**3 — Enumerate from the catalogue.** Query the system catalogue for every table
in the schema. Compare against the tables the application references. The
difference is the set nobody has looked at.

**4 — Classify by sensitivity and policy together.** Sensitive with no policy is
critical. Non-sensitive with no policy is a finding with a lower number and the
same cause.

**5 — Report per table with the statement that created it.** A finding that
points at a line in a migration gets fixed; one that says "enable RLS" gets
discussed.

## Output contract

```json
{
  "statements": [{"table": "str", "columns": ["str"], "sensitive_columns": ["str"]}],
  "policies": [{"table": "str", "policy": "none|open|scoped", "subject": "str|null"}],
  "catalogue": {"tables": ["str"], "referenced_by_app": ["str"], "unreviewed": ["str"]},
  "findings": [{"table": "str", "severity": "critical|high|medium", "created_by": "str"}]
}
```

## Failure modes

- **Auditing the application's queries.** They cover the tables it uses.
- **Treating "no policy" as "open policy".** They are different fixes.
- **Reporting the table without the statement.** Nobody knows where to change
  it.
