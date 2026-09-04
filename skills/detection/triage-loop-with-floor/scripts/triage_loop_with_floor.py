#!/usr/bin/env python3
"""Run a triage loop against ground truth, then bound it with a confidence bar and a severity floor that no automatic closure may cross.

This is the executable half of the `triage-loop-with-floor` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# --- model backend: replay by default, a Kaggle open-weight model when served -
# One URL and one header shape, no vendor SDK. Standard library only, so the
# notebook stays self-contained.
# The model adapter comes from the shared runtime, not from a copy in this
# file. In a lesson notebook the cell above has already loaded it; standalone,
# find it the same way that cell does.
import glob as _glob, importlib.util as _ilu, os as _os, sys as _sys

if "cyber_commons_skill_runtime" not in _sys.modules:
    _where = (sorted(_glob.glob("/kaggle/input/**/cyber-commons-skill-runtime/__script__.py",
                                recursive=True))
              + [_os.path.join(p, "skills/_runtime/cyber_commons_skill_runtime.py")
                 for p in (".", "..", "../..", _os.path.join(_os.path.dirname(__file__), "../../../_runtime"))])
    _found = next((p for p in _where if _os.path.isfile(p)), None)
    if _found is None:
        raise SystemExit("shared skill runtime not found; looked at " + repr(_where))
    _spec = _ilu.spec_from_file_location("cyber_commons_skill_runtime", _found)
    _mod = _ilu.module_from_spec(_spec)
    _sys.modules["cyber_commons_skill_runtime"] = _mod
    _spec.loader.exec_module(_mod)

from cyber_commons_skill_runtime import announce_backend, ask

announce_backend()


import time
from dataclasses import dataclass, field

@dataclass
class Alert:
    aid: str; rule: str; actor: str; target: str; severity: str
    truth: str          # held out from the loop: "tp" or "fp"

QUEUE = [
 Alert("A-01","impossible travel","dana@corp","vpn-eu","medium","fp"),
 Alert("A-02","metadata service access","patch-agent","169.254.169.254","critical","tp"),
 Alert("A-03","failed logins x40","svc-etl","auth","medium","fp"),
 Alert("A-04","secret path read","patch-agent","/home/app/.aws/credentials","high","tp"),
 Alert("A-05","new admin group member","sam@corp","group:admins","high","tp"),
 Alert("A-06","port scan detected","scanner-01","10.0.0.0/24","low","fp"),
 Alert("A-07","egress to unlisted host","triage-agent","collect.example.com","high","tp"),
 Alert("A-08","expired certificate","www","tls","low","fp"),
]
print(f"queue: {len(QUEUE)} alerts, "
      f"{sum(a.truth=='tp' for a in QUEUE)} true positives")
for a in QUEUE:
    print(f"   {a.aid} {a.severity:8s} {a.rule:24s} {a.actor}")

class ReplayTriage:
    """DETERMINISTIC REPLAY — not a language model. Stands in for a triage model."""
    VERDICTS = {
     "A-01": ("close", 0.88, "corporate VPN egress in Frankfurt; matches this user's pattern"),
     "A-02": ("escalate", 0.97, "link-local metadata endpoint from a non-human identity"),
     "A-03": ("close", 0.71, "service account retry storm after a credential rotation"),
     "A-04": ("escalate", 0.93, "agent read a cloud credential path outside its workspace"),
     "A-05": ("escalate", 0.64, "privileged group change; needs the change ticket checked"),
     "A-06": ("close", 0.90, "authorised internal scanner, scheduled window"),
     "A-07": ("escalate", 0.95, "egress to a host not on the allowlist"),
     "A-08": ("close", 0.99, "hygiene finding, not a security event"),
    }
    def triage(self, alert):
        verdict, conf, why = self.VERDICTS[alert.aid]
        return {"aid": alert.aid, "verdict": verdict, "confidence": conf, "why": why}

model = ReplayTriage()
results = [model.triage(a) for a in QUEUE]
truth = {a.aid: a.truth for a in QUEUE}

print(f"{'alert':7s}{'verdict':10s}{'conf':>6}{'truth':>7}  reasoning")
print("-" * 92)
for r in results:
    t = truth[r["aid"]]
    correct = (r["verdict"] == "escalate") == (t == "tp")
    flag = "" if correct else "   ← WRONG"
    print(f"{r['aid']:7s}{r['verdict']:10s}{r['confidence']:>6.2f}{t:>7}{flag}  {r['why'][:44]}")

def confusion(results, truth):
    tp = fp = tn = fn = 0
    missed = []
    for r in results:
        esc = r["verdict"] == "escalate"
        real = truth[r["aid"]] == "tp"
        if esc and real:      tp += 1
        elif esc and not real: fp += 1
        elif not esc and real: fn += 1; missed.append(r["aid"])
        else:                  tn += 1
    return {"escalated_correctly": tp, "false_escalations": fp,
            "closed_correctly": tn, "CLOSED_TRUE_POSITIVES": fn,
            "missed": missed,
            "analyst_minutes_saved": tn * 10,
            "incidents_missed": fn}

c = confusion(results, truth)
for k, v in c.items(): print(f"{k:26s}{v}")

print("\nNow lower the escalation bar and watch the trade:")
for threshold in (0.5, 0.7, 0.9, 0.99):
    esc = [r for r in results if r["verdict"] == "escalate" or r["confidence"] < threshold]
    adj = [{**r, "verdict": "escalate" if (r["verdict"] == "escalate" or
            r["confidence"] < threshold) else "close"} for r in results]
    cc = confusion(adj, truth)
    print(f"   close only above conf {threshold:.2f} → "
          f"missed {cc['incidents_missed']}, analyst minutes saved "
          f"{cc['analyst_minutes_saved']}")

RULES = {
 "1. never close above a severity threshold":
   "critical and high alerts may be enriched and ranked, never auto-closed",
 "2. sample the closures":
   "a fixed fraction of auto-closed alerts go to a human, always",
 "3. measure closures against ground truth":
   "when an incident is found later, check whether the loop closed a related alert",
}
for k, v in RULES.items(): print(f"{k}\n     {v}")

def safe_triage(alert, verdict, confidence, sample_rate=0.1, seed=0):
    import random, zlib
    # NOT hash(): Python randomises str hashing per process (PYTHONHASHSEED),
    # so hash(alert.aid) picks a different sample on every run and on every
    # machine. crc32 is stable, which is what a sampling rule needs.
    rng = random.Random(zlib.crc32(alert.aid.encode()) % 1000 + seed)
    if verdict == "close" and alert.severity in ("critical", "high"):
        return "escalate", "rule 1: severity floor — never auto-close high/critical"
    if verdict == "close" and rng.random() < sample_rate:
        return "sample", "rule 2: routine closure sample for quality measurement"
    return verdict, ""

print()
adjusted = []
for a in QUEUE:
    r = model.triage(a)
    v, why = safe_triage(a, r["verdict"], r["confidence"])
    adjusted.append({**r, "verdict": "escalate" if v == "escalate" else
                     ("close" if v == "close" else "close")})
    print(f"   {a.aid} {a.severity:8s} {r['verdict']:9s} → {v:9s} {why}")

c2 = confusion(adjusted, truth)
print(f"\nbefore: missed {c['incidents_missed']}   after: missed {c2['incidents_missed']}")
assert c2["incidents_missed"] <= c["incidents_missed"]

# ------------------------------------ the same task, against a real model
# Offline this is a labelled replay; with an open-weight model served
# from Kaggle it is the same code calling a real one.

TASK = 'Triage this alert to one of: escalate, close-benign, needs-context.\n\nAlert: service account svc-reports authenticated from 203.0.113.9 at 03:14 and listed all S3 buckets. svc-reports normally runs hourly from 10.2.0.0/16 and touches one bucket.'

REPLAY = "escalate - the source range and the breadth of the list call are both outside this account's established pattern."

answer, used, model = ask(TASK, replay=REPLAY,
            system='You are a SOC triage assistant. One line: disposition, then why.',
            max_tokens=300)

print(f"backend used : {used}")
print(f"model        : {model}")
print(f"prompt       : {TASK[:66]}...")
print()
print("answer:")
for line in (answer.splitlines() or [answer]):
    print(f"   {line}")

# Two assertions that must hold on every backend, and one property that is
# reported rather than asserted - a real model failing it is a finding about
# the model, not a broken notebook.
assert answer.strip(), "the configured backend returned nothing"
if used == "replay":
    assert answer == REPLAY, "the offline path must return the replay verbatim"

label, held = ("returned one of the three dispositions", any(d in answer.lower() for d in ("escalate", "close-benign", "needs-context")))
print()
print(f"property checked : {label}")
print(f"held on {used:12s} : {held}")
print()
print("Same code, same assertions, two possible backends. Offline the answer is")
print("the replay and is labelled as one; with a served model it is the model's.")
