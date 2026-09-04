#!/usr/bin/env python3
"""Test a fleet kill switch for what it leaves valid — tokens, evidence, and the runs you needed to keep.

This is the executable half of the `fleet-kill-switch-test` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

FLEET = [
 {"id": f"agent-{i:03d}",
  "experiment": "exploitgym",
  "token": f"tok-{i:03d}",
  "token_ttl_hours": 72}
 for i in range(8)
]
ISSUED = {a["token"] for a in FLEET}

def terminate_only(fleet):
    return {"terminated": len(fleet), "tokens_still_valid": len(ISSUED)}

def terminate_and_revoke(fleet, revoked):
    revoked |= {a["token"] for a in fleet}
    return {"terminated": len(fleet), "tokens_still_valid": len(ISSUED - revoked)}

r1 = terminate_only(FLEET)
print(f"terminate only        : {r1['terminated']} agents stopped, "
      f"{r1['tokens_still_valid']} tokens still valid for up to 72h")

revoked = set()
r2 = terminate_and_revoke(FLEET, revoked)
print(f"terminate and revoke  : {r2['terminated']} agents stopped, "
      f"{r2['tokens_still_valid']} tokens still valid")
print()
print("In the source incident, third-party access ended when the third party")
print("revoked its keys - not when the agents stopped. Stopping the process is")
print("the visible half of containment and the smaller one.")
assert r1["tokens_still_valid"] == 8 and r2["tokens_still_valid"] == 0

def kill(fleet, preserve=True, revoke=True):
    steps, evidence = [], 0
    if preserve:
        steps.append("snapshot state and transcripts")
        evidence = len(fleet)
    steps.append("terminate")
    if revoke:
        steps.append("revoke credentials")
    return {"steps": steps, "evidence_preserved": evidence,
            "reconstructable": evidence == len(fleet)}

for label, preserve in (("terminate first", False), ("preserve first", True)):
    r = kill(FLEET, preserve=preserve)
    print(f"{label:18s}{' -> '.join(r['steps']):58s}"
          f"reconstructable={r['reconstructable']}")
print()
print("The ordering is the whole design. Terminating first is faster by seconds")
print("and costs the investigation everything, which is the trade nobody makes")
print("deliberately at three in the morning.")
assert kill(FLEET, preserve=True)["reconstructable"]
assert not kill(FLEET, preserve=False)["reconstructable"]

TESTS = [
 ("Q1", True,  4.2, "full fleet, clean conditions"),
 ("Q2", True,  4.9, "full fleet, one region degraded"),
 ("Q3", False, None, "not run - no window agreed"),
 ("Q4", True,  6.8, "partial failure: revocation API throttled"),
]
TARGET_MIN = 5.0
print(f"{'quarter':9s}{'ran':5s}{'minutes':>9}  condition")
for q, ran, mins, cond in TESTS:
    shown = f"{mins:.1f}" if mins else "-"
    print(f"{q:9s}{('yes' if ran else 'no'):5s}{shown:>9}  {cond}")

timed = [m for _, ran, m, _ in TESTS if ran and m]
over = [m for m in timed if m > TARGET_MIN]
print(f"\ntests run: {len(timed)} of {len(TESTS)}   target: under {TARGET_MIN:.0f} min")
print(f"over target: {len(over)}  ({', '.join(f'{m:.1f}' for m in over) or 'none'})")
print()
print("The quarter that was not run is the finding, and the quarter that ran")
print("long is the second one: under partial failure the revocation half is")
print("what slows down, which is the half that matters.")
assert len(timed) == 3 and over == [6.8]
