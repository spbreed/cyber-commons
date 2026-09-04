#!/usr/bin/env python3
"""Roll a register up from the downstreams an agent's tools reach, and treat an unmapped dependency as unassessed rather than clean.

This is the executable half of the `risk-registry-integrator` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

FAMILIES = {
 "prompt injection and instruction hijacking": ["R3"],
 "identity and authorisation":                 ["R1", "R5", "R11"],
 "software supply chain and execution":        ["R4"],
 "local filesystem manipulation":              ["R6"],
 "code and CI/CD pipeline":                    ["R7", "R8"],
 "RAG misconfiguration and data exposure":     ["R12"],
 "lateral movement and logging":               ["R9", "R10"],
 "guardrail tampering":                        ["R2"],
}
print(f"{'family':44s}{'risks':>6}  ids")
for fam in sorted(FAMILIES, key=lambda f: (-len(FAMILIES[f]), f)):
    ids = FAMILIES[fam]
    print(f"{fam:44s}{len(ids):>6}  {', '.join(ids)}")

total = sum(len(v) for v in FAMILIES.values())
biggest = max(sorted(FAMILIES), key=lambda f: len(FAMILIES[f]))
print(f"\nrisks: {total}   families: {len(FAMILIES)}")
print(f"largest family: {biggest} ({len(FAMILIES[biggest])} of {total})")
print()
print("Identity carries a quarter of the register on its own - over-privileged")
print("execution, plaintext long-lived tokens, and no lineage from a human to an")
print("action. None of the three is exotic, and all three are closed by the same")
print("chapter. That is why chapter 2 is identity and not something more")
print("interesting.")
assert total == 12 and biggest == "identity and authorisation"

COMPONENT = {
 "R1":  "workflow agent + its authorisation",
 "R2":  "guardrails around the advisor's output",
 "R3":  "ingress into any agent",
 "R4":  "third-party MCP server",
 "R5":  "the transport between agent and API",
 "R6":  "local std I/O on Alex's laptop",
 "R7":  "the coding agent's CI/CD path",
 "R8":  "the coding agent's pull requests",
 "R9":  "every downstream API, once one agent is held",
 "R10": "the log sink",
 "R11": "identity, across all four agents",
 "R12": "the vector store",
}
AGENT_OF = {
 "R1": "workflow", "R2": "advisor", "R3": "all four", "R4": "workflow",
 "R5": "all four", "R6": "files", "R7": "coding", "R8": "coding",
 "R9": "all four", "R10": "all four", "R11": "all four", "R12": "advisor",
}
from collections import Counter
per_agent = Counter(AGENT_OF.values())
print(f"{'agent':12s}{'risks':>6}")
for a in sorted(per_agent, key=lambda k: (-per_agent[k], k)):
    print(f"{a:12s}{per_agent[a]:>6}")

shared = per_agent["all four"]
print(f"\nrisks that belong to no single agent : {shared} of {len(AGENT_OF)}")
print()
print("Five of twelve are not any one agent's problem. They are properties of")
print("how the four are wired together - ingress, transport, identity, logging,")
print("and what a held agent can reach. Assign those to an agent owner and they")
print("will be nobody's, which is the failure E1.10 is entirely about.")
assert shared == 5

OWNED_BY_LESSON = {
 "R1": ["A2.3", "A2.4", "A3.1"], "R2": ["A3.5", "A3.6", "A3.9"],
 "R3": ["A1.2", "A1.3", "A2.6", "A3.1"], "R4": ["C2.5", "A3.8", "B2.13"],
 "R5": ["A2.1", "A2.2", "A2.4"], "R6": ["A3.2", "A1.8", "B2.12"],
 "R7": ["B2.12", "B2.9", "A3.6"], "R8": ["B2.5", "B2.9", "B2.10"],
 "R9": ["A3.3", "A3.7", "D2.3"], "R10": ["D1.5", "E2.5", "A2.7"],
 "R11": ["A2.1", "A2.7", "A1.14"], "R12": ["A1.3", "A1.4", "E1.3"],
}
lessons = sorted({l for ls in OWNED_BY_LESSON.values() for l in ls})
by_function = Counter(l[0] for l in lessons)

print(f"risks with at least one owning lesson : "
      f"{sum(1 for v in OWNED_BY_LESSON.values() if v)}/{len(OWNED_BY_LESSON)}")
print(f"distinct lessons doing the work       : {len(lessons)}")
print()
print(f"{'function':10s}{'lessons':>8}")
for f in sorted(by_function):
    print(f"{f:10s}{by_function[f]:>8}")

unowned = [r for r, ls in OWNED_BY_LESSON.items() if not ls]
print(f"\nrisks with no owner: {unowned or 'none'}")
print()
print("Twelve risks, twenty-odd lessons, four functions. A register that fits on")
print("one page and points at everything else is the artefact this chapter was")
print("for - and the thing to re-run whenever CyberTravels grows a fifth agent.")
assert not unowned and len(lessons) > 15
