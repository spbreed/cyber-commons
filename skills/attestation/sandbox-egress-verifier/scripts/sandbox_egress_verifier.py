#!/usr/bin/env python3
"""Evaluate the same destinations under a deny-list and under an exact allow-list.

This is the executable half of the `sandbox-egress-verifier` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

ALLOW = {"api.corp.example", "reports-db.corp.example"}
DENY_SUFFIXES = {".evil.example"}          # the deny-list, for comparison

def by_denylist(host):
    return not any(host.endswith(s) for s in DENY_SUFFIXES)

def by_allowlist(host):
    return host in ALLOW                    # exact, not suffix

DESTINATIONS = [
 ("api.corp.example",              "the one it actually needs"),
 ("archive.evil.example",          "A1.3's exfiltration target"),
 ("attacker-bucket.s3.amazonaws.com", "a bucket anyone can create"),
 ("169.254.169.254",               "cloud metadata - every credential"),
 ("pastebin.example",              "not on anyone's deny-list"),
]

print(f"{'destination':38s}{'deny-list':12s}{'allow-list':12s}note")
for host, note in DESTINATIONS:
    d, a = by_denylist(host), by_allowlist(host)
    print(f"{host:38s}{'allow' if d else 'block':12s}{'allow' if a else 'block':12s}{note}")

leaked = [h for h, _ in DESTINATIONS if by_denylist(h) and h not in ALLOW]
print(f"\ndeny-list lets through : {len(leaked)}  {leaked}")
print(f"allow-list lets through : {sorted(h for h, _ in DESTINATIONS if by_allowlist(h))}")
print()
print("The deny-list blocked exactly the destination somebody had already")
print("thought of. It cannot be completed, because the internet cannot be")
print("enumerated.")
print()
print("Placement matters as much: this check belongs in the network path, not")
print("in the agent. A check inside the process being attacked is advice.")
assert len(leaked) == 3 and len([h for h, _ in DESTINATIONS if by_allowlist(h)]) == 1
