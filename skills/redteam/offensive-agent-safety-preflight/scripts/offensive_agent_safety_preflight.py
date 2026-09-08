#!/usr/bin/env python3
"""Refuse to start an offensive-agent engagement until every safety control is present, and tell the SOC what to expect.

This is the executable half of the `offensive-agent-safety-preflight` skill: the
check the SKILL.md next to it describes, run against two CyberTravels engagement
configurations so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle kernel with the
internet switched off.
"""

# Seven controls. BLOCKING means the engagement does not start without it — not
# because the control is more important, but because its absence cannot be
# noticed later. A missing egress allowlist is invisible until data has left.
CONTROLS = [
    ("zero_data_retention", True,
     "provider retains no prompts or completions",
     "target data enters a third party's training set or breach"),
    ("sandbox", True,
     "the agent runs in an isolated, disposable workspace",
     "a payload that escapes lands on a corporate host"),
    ("egress_allowlist", True,
     "outbound restricted to the engagement scope",
     "the agent tests something you were not authorised to touch"),
    ("secret_management", True,
     "credentials injected at call time, never in prompt or repo",
     "the tester's own credentials end up in a trace or a report"),
    ("human_in_the_loop", True,
     "a named person approves every destructive action",
     "an exploit runs against production because it looked in scope"),
    ("deterministic_guardrails", True,
     "scope and rate enforced outside the model, not asked of it",
     "the model is argued out of the scope it was told to respect"),
    ("soc_notified", False,
     "the SOC has the window, source addresses and expected signatures",
     "your own detection team runs a real incident against you"),
]

ENGAGEMENTS = {
 "cybertravels-q3-external": {
    "zero_data_retention": True,  "sandbox": True,   "egress_allowlist": True,
    "secret_management": True,    "human_in_the_loop": True,
    "deterministic_guardrails": True, "soc_notified": True,
 },
 "quick-look-before-the-board": {
    "zero_data_retention": False, "sandbox": True,   "egress_allowlist": False,
    "secret_management": True,    "human_in_the_loop": False,
    "deterministic_guardrails": False, "soc_notified": False,
 },
}


def preflight(name, cfg):
    print(f"\n=== {name}")
    blocking, advisory = [], []
    for key, is_blocking, what, cost in CONTROLS:
        ok = cfg.get(key, False)
        mark = "PASS" if ok else ("BLOCK" if is_blocking else "WARN ")
        print(f"  [{mark}] {key:<26} {what}")
        if not ok:
            print(f"          if absent: {cost}")
            (blocking if is_blocking else advisory).append(key)
    if blocking:
        print(f"\n  ENGAGEMENT REFUSED — {len(blocking)} blocking control(s) "
              f"missing: {', '.join(blocking)}")
    else:
        print("\n  ENGAGEMENT MAY START")
        if advisory:
            print(f"  advisory: {', '.join(advisory)}")
    return not blocking, blocking, advisory


def main() -> int:
    print("the seven controls an offensive agent runs inside")
    print("(six blocking; SOC notification is advisory because its absence is")
    print(" recoverable — you can always pick up the phone mid-engagement)")

    results = {n: preflight(n, c) for n, c in ENGAGEMENTS.items()}

    print("\n" + "=" * 66)
    print("what the SOC is told, for the engagement that may start\n")
    ok_name = next(n for n, (ok, *_) in results.items() if ok)
    print(f"  engagement   {ok_name}")
    print("  window       2026-09-14 09:00 to 2026-09-18 18:00 UTC")
    print("  sources      198.51.100.0/29 only")
    print("  expect       credential stuffing signatures, BOLA probes on")
    print("               /bookings and /refunds, and a burst of 4xx")
    print("  do NOT       suppress the rules. record what fired and what did not")
    print("               — that measurement is the point of telling them.")

    print("\nthe last line is the one people skip. an engagement the SOC muted")
    print("produces a clean report and no information about whether anything")
    print("would have been detected, which was half the reason to run it.")

    refused = [n for n, (ok, *_) in results.items() if not ok]
    assert refused, "a preflight that passes every configuration is decoration"
    assert any(ok for ok, *_ in results.values()), "and one that passes none is broken"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
