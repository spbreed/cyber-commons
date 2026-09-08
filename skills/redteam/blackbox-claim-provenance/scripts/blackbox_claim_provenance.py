#!/usr/bin/env python3
"""Split an external probe's claims into what was observed and what was inferred, and refuse a severity on the second kind.

This is the executable half of the `blackbox-claim-provenance` skill: the check
the SKILL.md next to it describes, run against the CyberTravels estate so two
runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle kernel with the
internet switched off.
"""

# Everything a black-box engagement is allowed to look at. The list is short on
# purpose: that is the whole constraint of the mode.
DATA_SOURCES = [
    ("DNS and certificate transparency", "names that exist"),
    ("TLS handshake",                    "the terminator, and its config"),
    ("HTTP status, headers, body",       "what the app chose to return"),
    ("error strings",                    "occasionally a stack, usually a template"),
    ("response timing",                  "a signal, and a noisy one"),
    ("public artefacts (JS, sitemaps)",  "routes the front end knows about"),
    ("the scope document",               "what you are permitted to touch"),
]

# claim, the evidence behind it, and whether the evidence ENTAILS it.
CLAIMS = [
    ("host api.cybertravels.example resolves and serves TLS 1.3",
     "handshake completed, cert chain read", True),
    ("/bookings/{id} exists",
     "200 on a known id, 404 on a random one", True),
    ("/bookings/{id} returns another tenant's booking",
     "404 on a random id", False),
    ("the app runs on Django",
     "X-Frame-Options and a csrftoken cookie name", False),
    ("an admin surface exists at /admin",
     "302 to a login form, distinct from the 404 template", True),
    ("the database is PostgreSQL",
     "an error string containing 'duplicate key value'", False),
    ("rate limiting is applied per IP",
     "429 after 61 requests in 60s from one address", True),
    ("rate limiting is NOT applied per account",
     "not tested; no second address available", False),
    ("refunds are processed synchronously",
     "response time 1.9s vs 120ms on reads", False),
    ("the refund endpoint accepts a booking id it does not own",
     "not tested; would require a second account", False),
    ("a vendor MCP server is in the request path",
     "a Server header naming a proxy", False),
    ("passport numbers are returned by /profile",
     "observed in a response to our own account", True),
]


def main() -> int:
    print("what a black-box engagement may look at\n")
    for src, gives in DATA_SOURCES:
        print(f"  {src:<36} {gives}")

    observed = [c for c in CLAIMS if c[2]]
    inferred = [c for c in CLAIMS if not c[2]]

    print(f"\nOBSERVED — the evidence entails the claim  ({len(observed)})\n")
    for claim, ev, _ in observed:
        print(f"  + {claim}")
        print(f"      because: {ev}")

    print(f"\nINFERRED — the evidence is consistent with the claim, and with "
          f"others  ({len(inferred)})\n")
    for claim, ev, _ in inferred:
        print(f"  ? {claim}")
        print(f"      from:    {ev}")

    print("\nwhy each inference fails, in one line:")
    print("  another tenant's booking  — a 404 on a random id is what CORRECT")
    print("                              authorisation also looks like")
    print("  Django / PostgreSQL       — headers and error strings are copied,")
    print("                              proxied and templated by other stacks")
    print("  no per-account rate limit — untested is not disproved")
    print("  synchronous refunds       — latency has a dozen other causes")
    print("  vendor MCP in the path    — a Server header names a hop, not a role")
    print("  refund accepts foreign id — the finding that MATTERS, and this mode")
    print("                              cannot reach it with one account")

    print(f"\nreport: {len(observed)} findings, {len(inferred)} open questions")
    print("no severity is attached to anything in the second list. an inference")
    print("with a CVSS score beside it reads as a finding to everyone downstream,")
    print("and the person who has to retract it is not the person who wrote it.")
    print("\nthe last open question is the one to escalate: it needs a second")
    print("credential, which makes it a grey-box test, not a better black-box one.")

    assert inferred, "a black-box run that inferred nothing did not look hard enough"
    assert len(observed) < len(CLAIMS), "everything observed means the split was not applied"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
