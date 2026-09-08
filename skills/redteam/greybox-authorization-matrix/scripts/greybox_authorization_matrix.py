#!/usr/bin/env python3
"""Fill a roles-by-objects-by-verbs matrix from real credentials, and rank the cells nobody tested.

This is the executable half of the `greybox-authorization-matrix` skill: the
check the SKILL.md next to it describes, run against the CyberTravels estate so
two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle kernel with the
internet switched off.
"""

# Grey box is defined by what you are given, and this is the list. One
# credential per role is the entire reason the mode can find BOLA at all.
DATA_SOURCES = [
    ("one credential per role",   "traveller, agent-svc, finance — the minimum"),
    ("API schema (OpenAPI)",      "every object and verb that exists"),
    ("object id samples per role", "two ids you own, two you must not"),
    ("the role matrix as designed", "what the team BELIEVES is enforced"),
    ("rate limits and scope",     "so the run does not become an incident"),
]

ROLES = ["traveller", "agent-svc", "finance"]
OBJECTS = ["booking(own)", "booking(other)", "refund", "profile(other)", "audit_log"]
VERBS = ["read", "write"]

# (role, object, verb) -> "allow" | "deny"  : what the design says.
DESIGN = {
    ("traveller", "booking(own)", "read"): "allow",
    ("traveller", "booking(own)", "write"): "allow",
    ("traveller", "booking(other)", "read"): "deny",
    ("traveller", "booking(other)", "write"): "deny",
    ("traveller", "refund", "read"): "allow",
    ("traveller", "refund", "write"): "deny",
    ("traveller", "profile(other)", "read"): "deny",
    ("traveller", "profile(other)", "write"): "deny",
    ("traveller", "audit_log", "read"): "deny",
    ("traveller", "audit_log", "write"): "deny",
    ("agent-svc", "booking(own)", "read"): "allow",
    ("agent-svc", "booking(own)", "write"): "allow",
    ("agent-svc", "booking(other)", "read"): "deny",
    ("agent-svc", "booking(other)", "write"): "deny",
    ("agent-svc", "refund", "read"): "allow",
    ("agent-svc", "refund", "write"): "allow",
    ("agent-svc", "profile(other)", "read"): "deny",
    ("agent-svc", "profile(other)", "write"): "deny",
    ("agent-svc", "audit_log", "read"): "deny",
    ("agent-svc", "audit_log", "write"): "deny",
    ("finance", "booking(own)", "read"): "allow",
    ("finance", "booking(own)", "write"): "deny",
    ("finance", "booking(other)", "read"): "allow",
    ("finance", "booking(other)", "write"): "deny",
    ("finance", "refund", "read"): "allow",
    ("finance", "refund", "write"): "allow",
    ("finance", "profile(other)", "read"): "deny",
    ("finance", "profile(other)", "write"): "deny",
    ("finance", "audit_log", "read"): "allow",
    ("finance", "audit_log", "write"): "deny",
}

# What the engagement actually exercised, and what came back. Everything absent
# from this dict is an UNTESTED cell — which is the output of the skill.
TESTED = {
    ("traveller", "booking(own)", "read"): "allow",
    ("traveller", "booking(own)", "write"): "allow",
    ("traveller", "booking(other)", "read"): "allow",     # <- mismatch
    ("traveller", "refund", "read"): "allow",
    ("traveller", "refund", "write"): "deny",
    ("traveller", "audit_log", "read"): "deny",
    ("agent-svc", "booking(own)", "read"): "allow",
    ("agent-svc", "booking(other)", "write"): "allow",    # <- mismatch
    ("agent-svc", "refund", "write"): "allow",
    ("finance", "booking(other)", "read"): "allow",
    ("finance", "refund", "write"): "allow",
    ("finance", "audit_log", "read"): "allow",
}

# How much a wrong answer in this cell costs, so the untested list is ranked by
# something other than the order the endpoints appear in the schema.
BLAST = {"booking(other)": 3, "refund": 4, "profile(other)": 4, "audit_log": 5,
         "booking(own)": 1}


def main() -> int:
    print("what a grey-box engagement is handed\n")
    for src, gives in DATA_SOURCES:
        print(f"  {src:<30} {gives}")

    cells = [(r, o, v) for r in ROLES for o in OBJECTS for v in VERBS]
    print(f"\nthe matrix: {len(ROLES)} roles x {len(OBJECTS)} objects x "
          f"{len(VERBS)} verbs = {len(cells)} cells\n")
    print(f"  {'role':<10} {'object':<16} {'verb':<6} {'design':<7} "
          f"{'observed':<9} verdict")

    findings, untested = [], []
    for r, o, v in cells:
        want = DESIGN[(r, o, v)]
        got = TESTED.get((r, o, v))
        if got is None:
            untested.append((r, o, v, want))
            verdict = "UNTESTED"
        elif got != want:
            findings.append((r, o, v, want, got))
            verdict = "*** MISMATCH ***"
        else:
            verdict = "ok"
        print(f"  {r:<10} {o:<16} {v:<6} {want:<7} {got or '-':<9} {verdict}")

    print(f"\ntested {len(cells) - len(untested)} of {len(cells)} cells "
          f"({1 - len(untested) / len(cells):.0%})")

    print(f"\n{len(findings)} mismatch(es) — the design says one thing and the "
          f"estate does another:")
    for r, o, v, want, got in findings:
        print(f"  ! {r} can {v} {o}: designed {want}, observed {got}")

    print(f"\n{len(untested)} untested cells, ranked by what a wrong answer costs:")
    ranked = sorted(untested, key=lambda c: -BLAST[c[1]])
    for r, o, v, want in ranked[:6]:
        print(f"  {BLAST[o]}  {r:<10} {v:<6} {o:<16} designed {want}, never exercised")

    print("\nan endpoint-coverage report would call this engagement complete:")
    print("every endpoint in the schema was touched at least once. authorisation")
    print("does not live in endpoints, it lives in cells, and the two highest-cost")
    print("cells here were never sent a single request.")

    assert findings, "a matrix with no mismatch has not been run against a real estate"
    assert untested, "full coverage of every cell is not what an engagement produces"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
