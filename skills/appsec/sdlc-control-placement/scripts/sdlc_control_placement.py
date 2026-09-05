#!/usr/bin/env python3
"""Place CyberTravels' security techniques on the pre/post-deploy line and count the risks covered only on the side that cannot act.

This is the executable half of the `sdlc-control-placement` skill: the coverage
review the SKILL.md next to it describes, run against CyberTravels' actual
tooling inventory so the gaps it finds are the ones the rest of this chapter
goes on to close.

Standard library only, and deterministic.
"""

# (technique, side, what the OTHER side sees that this cannot, can it block a merge)
TECHNIQUES = [
    ("SAST / code analysis",        "pre",  "whether the vulnerable path is reached with real traffic", True),
    ("SCA and SBOM scanning",       "pre",  "what actually loaded, versus what the manifest pinned", True),
    ("IaC and policy-as-code",      "pre",  "the identity and network the workload really got", True),
    ("threat modelling",            "pre",  "entry points added by a config change, not a commit", False),
    ("tool-schema / MCP review",    "both", "a description edited by the server after review", True),
    ("DAST / attack simulation",    "post", "the commit that introduced it", False),
    ("egress enforcement",          "post", "the config change that widened the allowlist", False),
    ("runtime posture and drift",   "post", "the plan the drift departed from", False),
    ("detection and canaries",      "post", "anything at all before it happens", False),
    ("attestation",                 "both", "nothing - it signs on the left and re-checks on the right", False),
]

# CyberTravels' risk classes, and which side each technique above actually
# covers them from. Sides, not tool names: two products on the same side of the
# line do not add coverage, they add invoices.
RISKS = [
    ("injection in application code",            ["pre", "post"]),
    ("vulnerable declared dependency",           ["pre"]),
    ("undeclared vendored binary",               []),
    ("over-broad IAM role at runtime",           ["post"]),
    ("prompt injection through retrieved text",  ["post"]),
    ("tool schema edited after review",          ["pre", "post"]),
    ("guardrail switched off after the demo",    ["post"]),
    ("secret committed to the repository",       ["pre"]),
]

print("techniques, placed")
print(f"   {'technique':<30}{'side':<7}{'gate':<6}blind to")
report = {"techniques": [], "risks": []}
for name, side, blind, gate in TECHNIQUES:
    print(f"   {name:<30}{side:<7}{'yes' if gate else '-':<6}{blind}")
    report["techniques"].append({"name": name, "side": side, "blind_to": blind})

gate_capable = sum(1 for *_, g in TECHNIQUES if g)
report["gate_capable"] = gate_capable
print()
print(f"{gate_capable} of {len(TECHNIQUES)} can block a merge. Everything else is")
print("advisory - it produces a ticket, and a ticket is a request, not a control.")
print()

# Steps 4 and 5 — the two shapes that both read as "covered" on an inventory.
print("risks, by which side covers them")
counts = {"pre_only": 0, "post_only": 0, "uncovered": 0}
for risk, sides in RISKS:
    if not sides:
        shape = "uncovered"
    elif sides == ["pre"]:
        shape = "pre-only"
    elif sides == ["post"]:
        shape = "post-only"
    else:
        shape = "covered"
    counts[shape.replace("-", "_")] = counts.get(shape.replace("-", "_"), 0) + 1
    mark = {"covered": "  ", "pre-only": "->", "post-only": "->", "uncovered": "!!"}[shape]
    print(f"   {mark} {risk:<42}{shape}")
    report["risks"].append({"risk": risk, "sides": sides, "shape": shape})
report["counts"] = counts
print()

print(f"pre-only  {counts['pre_only']}   preventable, and invisible once it ships:")
print("           nothing on the right would tell you it happened.")
print(f"post-only {counts['post_only']}   visible, and unpreventable: detection is the whole")
print("           of the control, and the merge that caused it went through.")
print(f"uncovered {counts['uncovered']}   nothing on either side. B2.7 is this row - an")
print("           artefact with no manifest entry has no identifier, so the")
print("           SCA pass on the left never had anything to look up.")
print()
print("All three of those render as one word on a tooling inventory. The middle")
print("row is the one that gets signed off, because a control exists, it runs,")
print("and it reports - and it reports afterwards.")

assert counts["post_only"], "no post-only risks - the placement is probably all 'both'"
assert counts["uncovered"], "an inventory with no gaps has not been read carefully"
assert gate_capable < len(TECHNIQUES) / 2, "most techniques cannot gate; check the placement"
