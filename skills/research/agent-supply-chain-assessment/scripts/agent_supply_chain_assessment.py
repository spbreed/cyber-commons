#!/usr/bin/env python3
"""Score new packages and MCP connectors for typosquatting and then re-score them weighted by the authority the agent runs with.

This is the executable half of the `agent-supply-chain-assessment` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Package:
    name: str; version: str; signed: bool = False
    downloads: int = 0; age_days: int = 999

KNOWN_GOOD = {"requests", "urllib3", "numpy", "pandas", "cryptography",
              "pytest", "flask", "colorama", "langchain"}

def levenshtein(a, b):
    if len(a) < len(b): a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + (ca != cb)))
        prev = cur
    return prev[-1]

def typosquat(pkg, known=KNOWN_GOOD):
    if pkg.name in known:
        return None
    near = sorted((levenshtein(pkg.name, k), k) for k in known)[:1]
    if near and near[0][0] <= 2:
        return f"distance {near[0][0]} from popular package {near[0][1]!r}"
    return None

def assess(pkg):
    flags = []
    if not pkg.signed:        flags.append("unsigned — no attestation to source")
    if pkg.age_days < 30:     flags.append(f"published {pkg.age_days}d ago — no soak time")
    if pkg.downloads < 1000:  flags.append(f"only {pkg.downloads} downloads")
    if (t := typosquat(pkg)): flags.append(t)
    verdict = "block" if len(flags) >= 3 else "review" if flags else "allow"
    return verdict, flags

for p in [Package("requests", "2.31.0", True, 900_000, 400),
          Package("requsts", "2.31.0", False, 12, 3),
          Package("colourama", "0.4.6", False, 40, 9),
          Package("langchain", "0.2.1", False, 400_000, 200)]:
    v, flags = assess(p)
    print(f"{p.name+'=='+p.version:24s}{v}")
    for f in flags: print(f"      · {f}")

NEW_ARTEFACTS = {
 "model weights": {
   "signing": "Sigstore/in-toto possible, rarely used",
   "popularity signal": "NONE — 'popular checkpoint' is not provenance",
   "lineage": "a fine-tune of a fine-tune; base model often unrecorded",
   "runs with": "no authority of its own — but shapes every decision",
   "honest verdict": "assess the PUBLISHER, because you cannot assess the artefact"},
 "prompt / tool packages (MCP, skills)": {
   "signing": "NO convention exists",
   "popularity signal": "star counts, which are trivially gamed",
   "lineage": "none recorded",
   "runs with": "YOUR AGENT'S AUTHORITY — this is the dangerous one",
   "honest verdict": "treat as executable code, because it is"},
}
for artefact, props in NEW_ARTEFACTS.items():
    print(f"=== {artefact} ===")
    for k, v in props.items():
        print(f"   {k:20s} {v}")
    print()

# An MCP tool package assessed with the ordinary signals — they still fire.
mcp_pkg = Package("mcp-jira-connector", "0.0.3", signed=False,
                  downloads=180, age_days=6)
v, flags = assess(mcp_pkg)
print(f"{mcp_pkg.name}: {v}")
for f in flags: print(f"   · {f}")
print("\nGood news: the existing process EXTENDS to it rather than needing")
print("invention. Bad news: nothing in that process accounts for the fact that")
print("this package will run with your agent's tools.")

def authority_weighted(pkg, runs_with_agent_authority, agent_blast):
    v, flags = assess(pkg)
    if runs_with_agent_authority and v != "allow":
        return "block", flags + [f"runs with agent authority (blast {agent_blast})"]
    return v, flags

v2, flags2 = authority_weighted(mcp_pkg, True, agent_blast=43)
print(f"\nauthority-weighted verdict: {v2}")
for f in flags2: print(f"   · {f}")
assert v2 == "block"

def risk_assessment(artefact, signals_available):
    known = [s for s, ok in signals_available.items() if ok]
    unknown = [s for s, ok in signals_available.items() if not ok]
    return {
      "artefact": artefact,
      "assessed_on": known,
      "cannot_assess": unknown,
      "statement": (f"assessed on {len(known)}/{len(signals_available)} signals; "
                    f"{', '.join(unknown)} not available for this artefact class"),
    }

for artefact, sig in (
  ("python package", {"signature": True, "downloads": True, "age": True, "lineage": True}),
  ("model weights",  {"signature": False, "downloads": False, "age": True, "lineage": False}),
  ("MCP tool pack",  {"signature": False, "downloads": False, "age": True, "lineage": False}),
):
    r = risk_assessment(artefact, sig)
    print(f"{r['artefact']:18s}{r['statement']}")
print("\nThat last sentence is the deliverable. A risk rating that hides which")
print("signals were unavailable is a number someone will later rely on.")
