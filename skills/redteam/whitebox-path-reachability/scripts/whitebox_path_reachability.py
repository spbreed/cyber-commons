#!/usr/bin/env python3
"""Separate reachable sinks from present ones, and name the authorisation predicate on each path.

This is the executable half of the `whitebox-path-reachability` skill: the check
the SKILL.md next to it describes, run against the CyberTravels estate so two
runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle kernel with the
internet switched off.
"""

# What a white-box engagement is actually handed. Naming the source per fact is
# the difference between a finding and an assertion — a reader can go and check
# any row of this.
DATA_SOURCES = [
    ("repository at a pinned commit", "entry points, call graph, sinks"),
    ("dependency lock file",          "the versions really resolved"),
    ("IaC plan",                      "what is exposed, and to whom"),
    ("tool / MCP manifests",          "what each agent may call"),
    ("IAM policy + role bindings",    "the authority behind each caller"),
    ("API schema (OpenAPI)",          "the objects and verbs that exist"),
    ("prior findings",                "what has already been refuted"),
]

# entry point -> ordered hops -> sink. `guard` is the authorisation predicate
# actually present on that hop, or None where there is none.
PATHS = [
    ("POST /bookings",            [("handler", "session"), ("svc.book", "owner==caller")], "db.bookings.write",   True),
    ("POST /refunds",             [("handler", "session"), ("svc.refund", None)],          "payments.refund",     True),
    ("GET  /bookings/{id}",       [("handler", "session"), ("svc.get", None)],             "db.bookings.read",    True),
    ("MCP  vendor.itinerary",     [("tool_router", None), ("svc.book", "owner==caller")],  "db.bookings.write",   True),
    ("cron nightly_reconcile",    [("job", "service_account")],                            "payments.refund",     True),
    ("(none)",                    [],                                                      "admin.reset_all",     False),
    ("(none)",                    [],                                                      "db.audit.purge",      False),
]


def main() -> int:
    print("what this engagement was handed, and what each source establishes\n")
    for src, gives in DATA_SOURCES:
        print(f"  {src:<32} {gives}")

    # The distinction the whole lesson turns on. "session" proves the caller is
    # somebody. It does not prove they are entitled to THIS object, and a path
    # carrying only authentication is the shape every BOLA finding has.
    AUTHN = {"session", "service_account"}

    print("\npaths from a real entry point to a sink\n")
    reachable, unreachable, authz_missing = [], [], []
    for entry, hops, sink, ok in PATHS:
        if not ok:
            unreachable.append(sink)
            continue
        reachable.append(sink)
        guards = [g for _, g in hops if g]
        authz = [g for g in guards if g not in AUTHN]
        trail = " -> ".join(h for h, _ in hops)
        mark = "AUTHZ OK " if authz else "AUTHN ONLY"
        if not authz:
            authz_missing.append((entry, sink, guards))
        print(f"  {mark} {entry:<26} {trail} -> {sink}")
        print(f"            authn: {', '.join(g for g in guards if g in AUTHN) or 'none'}"
              f"   authz: {', '.join(authz) or 'NONE ON ANY HOP'}")

    print(f"\nsinks present in the tree      {len(PATHS)}")
    print(f"sinks reachable from an entry  {len(reachable)}")
    print(f"  of those, authenticated only {len(authz_missing)}")
    print(f"sinks present but unreachable  {len(unreachable)}  "
          f"({', '.join(unreachable)})")

    print("\nthe unreachable ones are REPORTED, not dropped:")
    print("  they are one route away from being findings, and the next feature")
    print("  that adds a route will not re-run this analysis on its own.")

    print("\nfindings worth a tester's time — reachable, and nothing on the path")
    print("checks that this caller is entitled to this object:")
    for entry, sink, guards in authz_missing:
        print(f"  - {sink:<22} from {entry:<24} "
              f"(has {', '.join(guards) or 'nothing'}, which is not authorisation)")
    print("\nthat is the shape of every BOLA finding, and it is the shape of the")
    print("CyberTravels refund incident: the caller was authenticated throughout.")

    assert authz_missing, "an estate where every reachable sink checks entitlement needs no lesson"
    assert unreachable, "reporting only reachable sinks hides the near misses"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
