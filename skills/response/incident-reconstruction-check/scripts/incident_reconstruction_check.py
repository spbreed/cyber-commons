#!/usr/bin/env python3
"""Reconstruct an incident from logs that attribute every action to a human, and refuse to report a narrative the evidence does not carry.

This is the executable half of the `incident-reconstruction-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
from dataclasses import dataclass, field

@dataclass
class LogLine:
    ts: float
    logged_actor: str     # what the audit log records
    real_actor: str       # what actually happened (held out from the responder)
    action: str
    target: str = ""

def render(lines, truth=False):
    base = min(l.ts for l in lines)
    rows = [f"{'t+s':>6}  {'actor':16s}{'action':16s}target"]
    for l in sorted(lines, key=lambda x: x.ts):
        who = l.real_actor if truth else l.logged_actor
        rows.append(f"{l.ts-base:>6.0f}  {who:16s}{l.action:16s}{l.target}")
    return "\n".join(rows)

t0 = time.time()
INCIDENT = [
 LogLine(t0,      "dana@corp", "dana@corp",   "login",       "sso"),
 LogLine(t0+22,   "dana@corp", "dana@corp",   "open_ticket", "SEC-4471"),
 LogLine(t0+40,   "dana@corp", "patch-agent", "read_file",   "/work/repo/billing.py"),
 LogLine(t0+41,   "dana@corp", "patch-agent", "read_file",   "/home/app/.aws/credentials"),
 LogLine(t0+43,   "dana@corp", "patch-agent", "http_post",   "collect.example.com"),
 LogLine(t0+180,  "dana@corp", "dana@corp",   "logout",      "sso"),
]
print("WHAT THE RESPONDER SEES")
print(render(INCIDENT))

NARRATIVE = """
At 14:02 dana@corp authenticated via SSO and opened ticket SEC-4471. Eighteen
seconds later the same account read billing.py, then read the application's AWS
credentials, and posted to an external host. The account then remained active
for a further two minutes before logging out.

Assessment: credential theft by an authenticated insider. Recommend immediate
suspension of dana@corp pending investigation.
"""
print("A MODEL'S RECONSTRUCTION (fluent, supported by every log line):")
print(NARRATIVE)

print("WHAT ACTUALLY HAPPENED")
print(render(INCIDENT, truth=True))

def reconstruct(lines):
    logged = {l.logged_actor for l in lines}
    real   = {l.real_actor for l in lines}
    wrong  = [l for l in lines if l.logged_actor != l.real_actor]
    return {"actors_in_logs": sorted(logged),
            "actors_in_reality": sorted(real),
            "misattributed_lines": len(wrong),
            "hidden_actors": sorted(real - logged),
            "attribution": "sound" if not wrong else "BROKEN",
            "consequence": ("none" if not wrong else
                            f"containment aimed at {sorted(logged)} leaves "
                            f"{sorted(real - logged)} running")}

r = reconstruct(INCIDENT)
for k, v in r.items(): print(f"{k:22s}{v}")
print("\nEvery sentence in that narrative is supported by the logs.")
print("The conclusion is wrong, and the recommended action does nothing.")

def evidence_check(lines, has_acting_identity_field, has_act_chain):
    limits = []
    if not has_acting_identity_field:
        limits.append("no acting-identity field: every line attributes to the "
                      "principal, so agent actions are indistinguishable from human ones")
    if not has_act_chain:
        limits.append("no delegation chain: cannot establish who caused the task")
    rates = {}
    for l in lines:
        rates.setdefault(l.logged_actor, []).append(l.ts)
    for actor, ts in rates.items():
        if len(ts) > 2:
            span = max(ts) - min(ts)
            per_min = len(ts) / max(span/60, 1e-9)
            if per_min > 30:
                limits.append(f"{actor} shows {per_min:.0f} actions/min — "
                              f"not human-paced; an agent is likely present")
    return limits

limits = evidence_check(INCIDENT, has_acting_identity_field=False, has_act_chain=False)
print("EVIDENTIARY LIMITS (must appear before any conclusion):")
for l in limits: print(f"   ⚠ {l}")

SAFE = f"""
Timeline: dana@corp authenticated, opened SEC-4471; the account then read
billing.py, read AWS credentials, and posted externally.

LIMITS OF THIS RECONSTRUCTION
{chr(10).join('  - ' + l for l in limits)}

Assessment: an actor holding dana@corp's credential performed the reads and the
POST. The logs CANNOT establish whether that actor was the human or an agent
operating with her token. Containment must therefore address both.
"""
print(SAFE)
assert limits
