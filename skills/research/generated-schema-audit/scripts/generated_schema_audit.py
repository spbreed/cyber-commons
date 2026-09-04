#!/usr/bin/env python3
"""Audit a generated database scaffold for tables that hold secrets and carry no policy, using the catalogue rather than the application.

This is the executable half of the `generated-schema-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SCAFFOLD = [
 "create table profiles (id uuid primary key, email text, api_key text);",
 "create table posts    (id uuid primary key, author uuid, body text);",
 "alter table posts enable row level security;",
 "create policy p_read on posts for select using (true);",
]

def audit(statements):
    """The check a generator does not run, expressed as three questions."""
    tables = [s.split()[2] for s in statements if s.startswith("create table")]
    rls_on = {s.split()[2] for s in statements if "enable row level security" in s}
    permissive = [s.split()[2] for s in statements
                  if s.startswith("create policy") and "using (true)" in s]
    findings = []
    for tbl in tables:
        if tbl not in rls_on:
            findings.append((tbl, "critical", "RLS disabled - open via the public API"))
    for s in statements:
        if s.startswith("create policy") and "using (true)" in s:
            findings.append((s.split()[4], "high", "policy matches every row"))
    return tables, findings

tables, findings = audit(SCAFFOLD)
print(f"tables created : {', '.join(tables)}")
print(f"findings       : {len(findings)}\n")
print(f"{'table':12s}{'severity':11s}why")
for tbl, sev, why in findings:
    print(f"{tbl:12s}{sev:11s}{why}")

print()
print("The application works. Every feature passes. `profiles` holds an api_key")
print("column and has no policy at all, and nothing in the test suite is shaped")
print("like the question that would find it.")
assert any(f[1] == "critical" for f in findings)
assert "profiles" in [f[0] for f in findings]

# One query answers the critical half, across every table at once.
CATALOG = [                       # what pg_class would return
 {"relname": "profiles", "relrowsecurity": False},
 {"relname": "posts",    "relrowsecurity": True},
 {"relname": "sessions", "relrowsecurity": False},
 {"relname": "audit",    "relrowsecurity": True},
]
SENSITIVE = {"profiles", "sessions", "audit"}

open_tables = sorted(r["relname"] for r in CATALOG if not r["relrowsecurity"])
print("select relname from pg_class where relrowsecurity = false;")
for name in open_tables:
    mark = "  <- holds credentials or session state" if name in SENSITIVE else ""
    print(f"   {name}{mark}")

print(f"\ntables open via the public API : {len(open_tables)} of {len(CATALOG)}")
exposed_sensitive = [t for t in open_tables if t in SENSITIVE]
print(f"of those, sensitive             : {len(exposed_sensitive)} "
      f"({', '.join(exposed_sensitive)})")
print()
print("This is a one-line query and it is the highest-value one in the whole")
print("pattern. It is also not something an application test can express, which")
print("is why it belongs in CI against the schema rather than in the test suite.")
assert exposed_sensitive == ["profiles", "sessions"]
