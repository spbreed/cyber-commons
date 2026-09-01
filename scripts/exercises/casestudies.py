"""Two more real case studies: Moltbook, and the pattern underneath it.

C2.8 works the Hugging Face / OpenAI agent-swarm incident, which is where the
control register comes from. These two follow it, and they are deliberately a
pair: **the instance, then the class.**

Sources are named in each lesson and the figures are theirs, not ours. Where
public reporting disagrees on a number — and on Moltbook's scale it does — both
figures are carried rather than one being picked.
"""

from . import diagrams as D

SOURCES_MOLTBOOK = """
> **Sources.** Public reporting on the Moltbook disclosure, late January 2026:
> [Treblle's breakdown](https://treblle.com/blog/moltbook-breach-breakdown),
> [PointGuard AI](https://www.pointguardai.com/ai-security-incidents/moltbook-ai-agent-network-platform-vulnerability),
> [Vectra AI](https://www.vectra.ai/blog/moltbook-and-the-illusion-of-harmless-ai-agent-communities)
> and [Kiteworks](https://www.kiteworks.com/cybersecurity-risk-management/moltbook-ai-agent-security-threat-enterprise-data-protection/).
> Figures below are theirs. Reporting disagrees on the scale — 770,000 agents
> in one account, 1.5 million in another — and both are carried here rather
> than one being chosen.
"""

SOURCES_SUPABASE = """
> **Sources.** Public write-ups of the Supabase misconfiguration patterns and
> CVE-2025-48757: [VibeAppScanner](https://vibeappscanner.com/issues/supabase),
> [GuardLayer](https://www.guardlayer.io/blog/supabase-security-breaches).
> Supabase itself has not been breached; the pattern is in applications built
> on it, which is what makes it a lesson about defaults rather than about a
> vendor.
"""

EXERCISES: dict[str, dict] = {

"C2.9": {
 "concept": """
Moltbook launched in late January 2026 as a social network with an unusual
membership rule: the accounts were autonomous AI agents, posting, commenting and
forming communities, with humans watching. Within days a security researcher,
Jameson O'Reilly, found that the whole thing was readable by anyone.

The mechanism is almost disappointingly small. Moltbook ran on **Supabase**, and
the site shipped its Supabase URL and publishable ("anon") key in the client —
which is normal and by design. What was not normal is that **Row-Level Security
was disabled on the tables behind it**. In Supabase, RLS is what turns "this key
identifies the application" into "this key may read this row". Without it, the
anon key is a read-everything key.

So a single query returned every agent's record. Those records held, in
plaintext, in a client-readable table:

- each agent's **secret API key** — spanning OpenAI, Anthropic, AWS, GitHub and
  Google Cloud accounts belonging to the humans who created them,
- claim tokens and verification codes,
- the owner relationships linking every agent back to its creator.

Anyone holding those keys could impersonate any agent on the platform, post as
it, and drive it — without ever failing an authentication check, because they
were authenticating correctly, as the agent.

Two things make this a Function C case study rather than a footnote.

**The blast radius is not the platform.** A social network for agents losing its
own data is a bad day. A social network for agents losing the *provider
credentials of everyone who registered one* is an incident in every one of those
providers' accounts, and the platform cannot revoke them for you.

**The second surface was never touched.** Moltbook's architecture — agents
ingesting and acting on content other agents post — is an indirect prompt
injection surface by construction (A1.3). The breach did not use it. It did not
need to.

The fix was two SQL statements.
""",
 "steps": [
  ("md", SOURCES_MOLTBOOK),

  ("md", "## 2 · What the client was holding, and what that key could reach"),
  ("html", D.svg(D.DEFS
    + D.box(6, 16, 190, 62, "browser", sub="anyone, unauthenticated")
    + D.label(101, 96, "ships the Supabase URL", anchor="middle")
    + D.label(101, 110, "+ the anon key (by design)", anchor="middle")
    + D.box(268, 16, 170, 62, "Supabase Data API", colour=D.SECURE)
    + D.box(510, 6, 184, 40, "row-level security", colour=D.BAD, dashed=True)
    + D.label(602, 60, "DISABLED", anchor="middle", colour=D.BAD, weight="600")
    + D.box(510, 78, 184, 52, "agents table", sub="every row, every column")
    + D.arrow(197, 47, 265) + D.arrow(439, 47, 506, 100)
    + D.label(350, 150, "the anon key was never the problem. the absent policy was.",
              anchor="middle", size=11.5),
    height=168,
    caption="RLS is what turns 'this key identifies the application' into 'this "
            "key may read this row'. Without it the anon key reads everything.")),

  ("md", "## 3 · The query, and the two statements that close it\\n\\n"
         "This is worth running rather than drawing, because the interesting part "
         "is what comes back — and how little has to change for it to stop."),
  ("py", '''AGENTS = [
 {"id": "a-0001", "owner": "dana@example",  "handle": "@researchbot",
  "provider_key": "sk-REDACTED-openai",     "claim_token": "clm_8fA2"},
 {"id": "a-0002", "owner": "sam@example",   "handle": "@newsdigest",
  "provider_key": "sk-ant-REDACTED",        "claim_token": "clm_2bQ7"},
 {"id": "a-0003", "owner": "kim@example",   "handle": "@dealfinder",
  "provider_key": "AKIA-REDACTED-aws",      "claim_token": "clm_9zR1"},
]

def data_api(table, caller, rls_enabled):
    """Supabase's PostgREST surface, in miniature.

    `caller` is whoever the anon key resolves to - which is nobody in
    particular. With RLS off there is no policy to consult, so every row is
    returned; with RLS on, the policy decides.
    """
    if not rls_enabled:
        return list(table)                       # no policy exists to consult
    return [r for r in table if r["owner"] == caller]

anon = None                                      # the anon key is not a person
for label, rls in (("RLS disabled (as shipped)", False), ("RLS enabled", True)):
    rows = data_api(AGENTS, caller=anon, rls_enabled=rls)
    print(f"{label:28s}rows returned: {len(rows)}")
    for r in rows:
        print(f"      {r['handle']:14s}{r['owner']:16s}{r['provider_key']}")

owner_rows = data_api(AGENTS, caller="dana@example", rls_enabled=True)
print(f"\\nsigned in as dana@example, RLS enabled: {len(owner_rows)} row")
print()
print("Same key, same endpoint, same table. The only difference is whether a")
print("policy exists for the API to consult.")
assert len(data_api(AGENTS, anon, False)) == 3
assert len(data_api(AGENTS, anon, True)) == 0 and len(owner_rows) == 1
'''),

  ("md", "## 4 · The fix, in full"),
  ("html", D.table(
    ["", "SQL"],
    [["1", "<code>alter table agents enable row level security;</code>"],
     ["2", "<code>create policy owner_reads on agents for select "
           "using (auth.uid() = owner_id);</code>"]],
    caption="Reported as roughly two statements. The gap between an incident and "
            "no incident was a policy nobody wrote, not a control nobody could "
            "afford.")),

  ("md", "## 5 · Why the blast radius is not the platform's\\n\\n"
         "Moltbook losing its own data would be a bad day for Moltbook. What was "
         "in the table belonged to everyone who had registered an agent, and "
         "Moltbook could not revoke any of it."),
  ("py", '''REPORTED_SCALE = {"Treblle": 770_000, "Wiz-sourced reporting": 1_500_000}
PROVIDERS = ["OpenAI", "Anthropic", "AWS", "GitHub", "Google Cloud"]

for source, n in sorted(REPORTED_SCALE.items()):
    print(f"{source:26s}{n:>10,} agents exposed")
low, high = min(REPORTED_SCALE.values()), max(REPORTED_SCALE.values())
print(f"\\nreported range            {low:>10,} - {high:,}")
print(f"provider accounts implicated: {', '.join(PROVIDERS)}")

# Who can actually revoke each thing that leaked.
REVOCABLE_BY = {
 "the Moltbook session token": "Moltbook",
 "the claim token":            "Moltbook",
 "the agent's provider key":   "the individual who created the agent",
}
print()
print(f"{'what leaked':30s}who can revoke it")
for what in sorted(REVOCABLE_BY):
    print(f"{what:30s}{REVOCABLE_BY[what]}")

platform_can_fix = [w for w in REVOCABLE_BY if REVOCABLE_BY[w] == "Moltbook"]
print(f"\\nthe platform can revoke {len(platform_can_fix)} of {len(REVOCABLE_BY)}.")
print("The third is a key in somebody else's provider account, and the only")
print("person who can turn it off may not know it was ever exposed. That is the")
print("difference between a platform breach and a supply-chain one.")
assert len(platform_can_fix) == 2
'''),

  ("md", "## 6 · The surface the attack did not need\\n\\n"
         "Worth saying plainly, because it is the part that generalises: the "
         "interesting architectural risk in Moltbook was never exercised."),
  ("html", D.table(
    ["surface", "status in this incident", "where it is taught"],
    [["credential store readable by anyone",
      "<b>used — this was the breach</b>", "A3.8, and the Supabase pattern in C2.10"],
     ["agents ingest and act on other agents' posts",
      "present, untouched", "A1.3 indirect prompt injection, A1.9 comms poisoning"],
     ["agents coordinating at population scale",
      "present, untouched", "A1.10, D1.10 fleet correlation"]],
    caption="An architecture can hold two novel risks and still be undone by a "
            "missing row policy. Novelty is not the same as likelihood.")),
 ],
 "expect": "With RLS disabled the anon key returns all three agent rows, secret "
           "provider keys included; with RLS enabled and no signed-in user it "
           "returns none, and one row for the owner. Reported scale spans "
           "770,000 to 1.5 million agents across five providers, and of the "
           "three things that leaked the platform can revoke two — the third is "
           "a key in somebody else's account.",
 "challenge": "Run `select relname from pg_class where relrowsecurity = false` "
              "against your own project, or the equivalent for whatever backend "
              "you use. Then find the table holding anything credential-shaped "
              "and check whether it is reachable from the client at all — the "
              "answer to the second question is the one that decides the size of "
              "your bad day.",
},

"C2.10": {
 "concept": """
Moltbook is the instance. This is the class, and the class is bigger than any
one platform.

Supabase has not been breached. What has happened repeatedly is that
*applications built on it* expose their data, and the write-ups converge on a
small number of patterns — two of them critical:

**Tables without Row-Level Security.** RLS was historically opt-in. A table
created without it is, in the write-ups' own words, "completely open via the
public API": anyone with the anon key — which ships to every browser — can read
it, and depending on policy, write it.

**The `service_role` key in client code.** That key exists to bypass RLS for
trusted server-side work. In a frontend bundle it is a complete RLS bypass and
full administrative database access, regardless of how good the policies are.

Three more sit just below: overly permissive policies, RPC functions with no
authorisation check of their own, and unsecured storage buckets.

What makes this a lesson rather than a checklist is **why it recurs now**.
Code generators scaffold a project, create tables and write the frontend — and
happily emit `create table` with no policy attached, because nothing in the
prompt asked for one and the code works without it. The failure is invisible in
testing: the app functions perfectly. One write-up puts it at **73% of
"vibe-coded" applications carrying at least one security issue**, with secrets
the most common category.

The structural fix is the one worth taking away. From 2026, new Supabase
projects **no longer expose public-schema tables through the Data API by
default** — closing the gap at the level of the default rather than at the level
of everyone remembering. That is the same argument as default-deny on the tool
call (A3.1), arriving at a database.
""",
 "steps": [
  ("md", SOURCES_SUPABASE),

  ("md", "## 2 · The two critical patterns, and what each defeats"),
  ("html", D.table(
    ["pattern", "what an attacker holds", "what it defeats", "severity"],
    [["table with RLS disabled", "the anon key, from any browser",
      "all row-level access control on that table", "<b>critical</b>"],
     ["<code>service_role</code> key in the frontend", "an admin key",
      "every policy, on every table", "<b>critical</b>"],
     ["overly permissive policy", "the anon key",
      "the intent of the policy, not its existence", "high"],
     ["RPC function with no auth check", "the anon key",
      "the policies the function bypasses", "high"],
     ["unsecured storage bucket", "the bucket URL", "object-level access", "high"]],
    emphasise=3,
    caption="The first two are not degrees of the same problem. One removes the "
            "policy; the other removes the policy engine.")),

  ("md", "## 3 · Why generated code lands here by default\\n\\n"
         "This is the part worth running: the vulnerable version and the safe "
         "version are indistinguishable from the application's behaviour, which "
         "is exactly why testing does not catch it."),
  ("py", '''SCAFFOLD = [
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
print(f"findings       : {len(findings)}\\n")
print(f"{'table':12s}{'severity':11s}why")
for tbl, sev, why in findings:
    print(f"{tbl:12s}{sev:11s}{why}")

print()
print("The application works. Every feature passes. `profiles` holds an api_key")
print("column and has no policy at all, and nothing in the test suite is shaped")
print("like the question that would find it.")
assert any(f[1] == "critical" for f in findings)
assert "profiles" in [f[0] for f in findings]
'''),

  ("md", "## 4 · The detection that actually scales"),
  ("py", '''# One query answers the critical half, across every table at once.
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

print(f"\\ntables open via the public API : {len(open_tables)} of {len(CATALOG)}")
exposed_sensitive = [t for t in open_tables if t in SENSITIVE]
print(f"of those, sensitive             : {len(exposed_sensitive)} "
      f"({', '.join(exposed_sensitive)})")
print()
print("This is a one-line query and it is the highest-value one in the whole")
print("pattern. It is also not something an application test can express, which")
print("is why it belongs in CI against the schema rather than in the test suite.")
assert exposed_sensitive == ["profiles", "sessions"]
'''),

  ("md", "## 5 · The fix that does not rely on anyone remembering\\n\\n"
         "Two ways to close this. Only one of them survives the next engineer, "
         "the next generated scaffold, and the next deadline."),
  ("html", D.svg(D.DEFS
    + D.box(6, 14, 320, 96, "fix each table", colour=D.SECURE)
    + D.label(166, 58, "alter table … enable row level security", anchor="middle")
    + D.label(166, 76, "create policy … using (auth.uid() = owner)", anchor="middle")
    + D.label(166, 96, "correct, and true only until the next table", anchor="middle")
    + D.box(374, 14, 320, 96, "fix the default", colour=D.GOOD)
    + D.label(534, 58, "tables are not exposed through the Data API", anchor="middle")
    + D.label(534, 76, "unless something opts them in", anchor="middle")
    + D.label(534, 96, "the Supabase default since 2026", anchor="middle")
    + D.label(350, 138, "the same argument as default-deny on the tool call (A3.1), "
                        "arriving at a database", anchor="middle", size=11.5),
    height=152,
    caption="A control that depends on everyone remembering is a control with a "
            "half-life.")),

  ("md", "## 6 · What this hands to the rest of the commons"),
  ("html", D.table(
    ["finding here", "the control, and where it lives"],
    [["credential-shaped data in a client-readable table",
      "A3.8 — shared infrastructure between agent runs"],
     ["an admin key reachable from the client",
      "A3.8 — admin plane off the workload path"],
     ["a default that is open until closed",
      "A3.1 — default-deny, applied to data rather than tools"],
     ["a schema check no application test expresses",
      "D1.9 — detections whose subject is the platform"],
     ["73% of generated apps carrying at least one issue",
      "B1.15 — securing the developers' coding agents"]],
    caption="Every row is a control that already exists in this curriculum. The "
            "case study's job was to show you why it is there.")),
 ],
 "expect": "An audit of a four-statement scaffold finds a critical issue: the "
           "`profiles` table holds an api_key column and has no RLS at all, "
           "while every feature of the application works. The catalogue query "
           "then finds two of four tables open via the public API, both of them "
           "holding credentials or session state — a one-line check that no "
           "application test expresses.",
 "challenge": "Take the last thing a code generator scaffolded for you and run "
              "the two questions from this lesson against it: which tables have "
              "no row policy, and is any admin-scoped key reachable from the "
              "client bundle? Neither question is about the framework — both are "
              "about what the default was when nobody said otherwise.",
},

}
