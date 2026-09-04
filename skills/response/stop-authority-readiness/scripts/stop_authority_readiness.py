#!/usr/bin/env python3
"""Turn stop authority from a vague answer into a named mechanism with a measured time-to-stop and a known cost.

This is the executable half of the `stop-authority-readiness` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

VAGUE = {
 "who":       "the security team",
 "mechanism": "we can turn off the agents",
 "time":      "quickly",
 "breaks":    "not much",
 "restart":   "when it's safe",
}
CONCRETE = {
 "who":       "on-call SRE, no approval required for non-human identities",
 "mechanism": "revoke the SPIFFE identity at the gateway (survives restart)",
 "time":      "measured 12s decision→first failed call, game day 2026-07-04",
 "breaks":    "auto-remediation pauses; ticket queue grows ~40/hour; "
              "agreed with the service owner 2026-05-11",
 "restart":   "security lead, after the C1.2 containment suite passes on the new build",
}
for k in VAGUE:
    print(f"{k:11s} VAGUE    {VAGUE[k]}")
    print(f"{'':11s} CONCRETE {CONCRETE[k]}\n")

from dataclasses import dataclass

@dataclass
class Agent:
    name: str; running: bool = True; identity_valid: bool = True
    def can_act(self): return self.running and self.identity_valid

MECHANISMS = {
 "kill the process":      (2,   lambda a: setattr(a, "running", False)),
 "network quarantine":    (5,   lambda a: None),
 "revoke the identity":   (12,  lambda a: setattr(a, "identity_valid", False)),
 "rotate the credential": (420, lambda a: setattr(a, "identity_valid", False)),
}
print(f"{'mechanism':24s}{'secs':>6}{'stops it':>10}{'survives restart':>19}")
print("-" * 60)
for name, (secs, apply) in MECHANISMS.items():
    a = Agent("patch-agent")
    apply(a)
    stopped = not a.can_act()
    a.running = True                      # a supervisor restarts the process
    survives = not a.can_act()
    print(f"{name:24s}{secs:>6}{str(stopped):>10}{str(survives):>19}")
print("\nThe fastest mechanism is the one that does not survive a restart.")
print("Speed without persistence is a pause, not a stop.")

GAME_DAY = [
 ("decision made",                    0),
 ("on-call authenticates to the IdP", 4),
 ("identity revoked",                 9),
 ("gateway cache expires",            12),
 ("agent's next call fails",          12),
 ("confirmed in telemetry",           38),
]
print(f"{'step':38s}{'t+s':>6}")
print("-" * 46)
for step, t in GAME_DAY: print(f"{step:38s}{t:>6}")
mttstop = GAME_DAY[4][1]
print(f"\nmeasured time-to-stop: {mttstop}s")
print(f"time-to-confirm:       {GAME_DAY[-1][1]}s")

def cost_of_stop(rate_per_min, seconds):
    return round(rate_per_min * seconds / 60)
for rate in (60, 300, 1200):
    print(f"   at {rate:>5}/min a {mttstop}s stop still permits "
          f"{cost_of_stop(rate, mttstop):>4} further actions")

def stop_authority_ready(answers, measured_seconds, tested_days_ago):
    problems = []
    if any(len(v.split()) < 4 for v in answers.values()):
        problems.append("at least one answer is not specific")
    if measured_seconds is None:
        problems.append("time-to-stop has never been measured")
    if tested_days_ago is None or tested_days_ago > 180:
        problems.append("not tested in the last 180 days")
    return (not problems), problems

for label, ans, secs, days in (("as usually documented", VAGUE, None, None),
                               ("after a game day", CONCRETE, 12, 41)):
    ok, problems = stop_authority_ready(ans, secs, days)
    print(f"\n{label}: ready={ok}")
    for p in problems: print(f"   ⚠ {p}")
assert stop_authority_ready(CONCRETE, 12, 41)[0]
