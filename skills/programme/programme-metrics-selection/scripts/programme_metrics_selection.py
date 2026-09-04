#!/usr/bin/env python3
"""Compute the metrics that degrade under neglect and separate them from the comfortable ones that do not.

This is the executable half of the `programme-metrics-selection` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}
now = time.time(); DAY = 86400

FLEET = {"pr-remediation": [("read_file","self",True),("write_file","project",True),
                            ("deploy","org",False)],
         "claims-triage":  [("read_file","self",True),("issue_refund","tenant",False)],
         "doc-summariser": [("read_file","self",True)]}
GATED = {"pr-remediation": set(), "claims-triage": {"issue_refund"},
         "doc-summariser": set()}
def blast(t, g): return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n,s,rev in t if n not in g)
exposure = sum(blast(t, GATED[a]) for a, t in FLEET.items())

ATTACKS = [("metadata",False),("traversal",False),("unlisted egress",True),("denied tool",False)]
asr = sum(1 for _, t in ATTACKS if t)/len(ATTACKS)

CONTROL_TESTS = {"AC-1": now-3*DAY, "AC-2": now-9*DAY, "SB-1": now-45*DAY,
                 "EV-1": now-5*DAY, "EV-2": now-12*DAY}
WINDOW = {"AC-1":30,"AC-2":30,"SB-1":30,"EV-1":60,"EV-2":30}
REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]
evidenced = sum(1 for c in REQUIRED
                if c in CONTROL_TESTS and (now-CONTROL_TESTS[c])/DAY <= WINDOW[c])
assurance = evidenced/len(REQUIRED)

REGISTERED, ESTIMATED = 41, 120
coverage = REGISTERED/ESTIMATED
TIME_TO_STOP = 12

METRICS = {
 "exposure   fleet blast radius":        (exposure, "units of unreviewed action"),
 "likelihood red-team ASR":              (f"{asr:.0%}", "measured, containment surface"),
 "assurance  controls evidenced":        (f"{assurance:.0%}", f"{evidenced}/{len(REQUIRED)}"),
 "coverage   agents in inventory":       (f"{coverage:.0%}", f"{REGISTERED} of ~{ESTIMATED} est."),
 "speed      measured time-to-stop":     (f"{TIME_TO_STOP}s", "game day 41 days ago"),
}
for k, (v, note) in METRICS.items():
    print(f"{k:36s}{str(v):>8}   {note}")

COMFORTABLE = {
 "findings closed this quarter": "goes up with activity; says nothing about posture",
 "training completion %":        "reaches 98% and stays there forever",
 "number of AI policies":        "monotonically increasing by construction",
 "tools evaluated":              "measures procurement, not risk",
}
print("metrics that look like governance and are not:")
for m, why in COMFORTABLE.items():
    print(f"   {m:34s}{why}")

def degrades_under_neglect(metric):
    DEGRADES = {"exposure": True, "likelihood": True, "assurance": True,
                "coverage": True, "speed": True,
                "findings closed": False, "training completion": False,
                "number of policies": False, "tools evaluated": False}
    return DEGRADES.get(metric, False)

print(f"\n{'metric':28s}{'degrades if ignored?':>22}")
print("-" * 52)
for m in ("exposure","likelihood","assurance","coverage","speed",
          "findings closed","training completion","number of policies"):
    print(f"{m:28s}{str(degrades_under_neglect(m)):>22}")
print("\nThe first five fall on their own. That is what makes them worth")
print("reporting monthly — the report itself creates the pressure.")

def project(months, exposure, asr, assurance, coverage, ttl_days=41):
    """What happens to each metric if nobody does anything for N months."""
    new_agents_per_month = 3
    exposure_growth = 8            # blast units per new agent, ungoverned
    controls_going_stale = 0.12    # fraction of evidence expiring per month
    return {
      "exposure":  exposure + months * new_agents_per_month * exposure_growth,
      "likelihood": min(asr + months * 0.03, 1.0),
      "assurance": max(assurance - months * controls_going_stale, 0.0),
      "coverage":  max(coverage - months * 0.04, 0.0),
      "days_since_stop_test": ttl_days + months * 30,
    }

print(f"{'month':>6}{'exposure':>10}{'ASR':>7}{'assurance':>11}{'coverage':>10}"
      f"{'stop test age':>15}")
print("-" * 60)
for m in (0, 3, 6, 12):
    p = project(m, exposure, asr, assurance, coverage)
    print(f"{m:>6}{p['exposure']:>10}{p['likelihood']:>7.0%}{p['assurance']:>11.0%}"
          f"{p['coverage']:>10.0%}{p['days_since_stop_test']:>15}")

p12 = project(12, exposure, asr, assurance, coverage)
print(f"\nAfter a year of no investment: exposure {exposure}→{p12['exposure']}, "
      f"assurance {assurance:.0%}→{p12['assurance']:.0%}.")
print("Nobody made a bad decision. This is the default trajectory, and the")
print("monthly report is what makes it visible before it is a board topic.")
assert p12["assurance"] < assurance and p12["exposure"] > exposure
