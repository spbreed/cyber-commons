#!/usr/bin/env python3
"""Query an exposed data API as an anonymous caller with row-level security off and on, and count what a leaked key returns.

This is the executable half of the `row-level-policy-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

AGENTS = [
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
print(f"\nsigned in as dana@example, RLS enabled: {len(owner_rows)} row")
print()
print("Same key, same endpoint, same table. The only difference is whether a")
print("policy exists for the API to consult.")
assert len(data_api(AGENTS, anon, False)) == 3
assert len(data_api(AGENTS, anon, True)) == 0 and len(owner_rows) == 1

REPORTED_SCALE = {"Treblle": 770_000, "Wiz-sourced reporting": 1_500_000}
PROVIDERS = ["OpenAI", "Anthropic", "AWS", "GitHub", "Google Cloud"]

for source, n in sorted(REPORTED_SCALE.items()):
    print(f"{source:26s}{n:>10,} agents exposed")
low, high = min(REPORTED_SCALE.values()), max(REPORTED_SCALE.values())
print(f"\nreported range            {low:>10,} - {high:,}")
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
print(f"\nthe platform can revoke {len(platform_can_fix)} of {len(REVOCABLE_BY)}.")
print("The third is a key in somebody else's provider account, and the only")
print("person who can turn it off may not know it was ever exposed. That is the")
print("difference between a platform breach and a supply-chain one.")
assert len(platform_can_fix) == 2
