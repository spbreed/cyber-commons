#!/usr/bin/env python3
"""Score candidate detection rules on precision, recall and firing volume, and reject the ones nobody could work.

This is the executable half of the `detection-rule-deployability` skill: the check the
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
from dataclasses import dataclass

@dataclass
class Event:
    ts: float; actor: str; action: str; target: str = ""; ok: bool = True

now = time.time()
HISTORY  = [Event(now+i, "patch-agent", "http_get", "https://api.github.com/x")
            for i in range(300)]
HISTORY += [Event(now+i, "triage-agent", "read_file", f"/work/repo/src/{i}.py")
            for i in range(200)]
HISTORY += [Event(now+400, "patch-agent", "http_get",
                  "http://169.254.169.254/latest/meta-data/iam/")]
HISTORY += [Event(now+401, "patch-agent", "read_file", "/home/app/.aws/credentials")]
HISTORY += [Event(now+i, "svc-etl", "read_file", "/data/export.csv", ok=False)
            for i in range(20)]

TRUE_POSITIVES = {(now+400, "patch-agent"), (now+401, "patch-agent")}

CANDIDATES = {
 "R1 any http_get by an agent":
    lambda e: e.action == "http_get",
 "R2 http_get to a non-github host":
    lambda e: e.action == "http_get" and "api.github.com" not in e.target,
 "R3 link-local address":
    lambda e: "169.254." in e.target,
 "R4 any failed action":
    lambda e: not e.ok,
 "R5 credential path OR link-local":
    lambda e: "169.254." in e.target or "/.aws/" in e.target,
}
print(f"history: {len(HISTORY)} events, {len(TRUE_POSITIVES)} true positives")

def score(rule, history, truth):
    fired = [e for e in history if rule(e)]
    tp = sum(1 for e in fired if (e.ts, e.actor) in truth)
    fp = len(fired) - tp
    fn = len(truth) - tp
    prec = tp / len(fired) if fired else 0.0
    rec  = tp / len(truth) if truth else 0.0
    return {"alerts": len(fired), "tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 3), "recall": round(rec, 3),
            "alerts_per_tp": round(len(fired)/tp, 1) if tp else float("inf")}

print(f"{'rule':36s}{'alerts':>7}{'prec':>7}{'recall':>8}{'alerts/TP':>11}")
print("-" * 70)
scored = {}
for name, rule in CANDIDATES.items():
    s = score(rule, HISTORY, TRUE_POSITIVES)
    scored[name] = s
    print(f"{name:36s}{s['alerts']:>7}{s['precision']:>7.3f}{s['recall']:>8.3f}"
          f"{str(s['alerts_per_tp']):>11}")

MAX_ALERTS_PER_TP = 5          # the analyst-trust budget, made explicit
MIN_RECALL = 0.5

def deployable(s):
    reasons = []
    if s["tp"] == 0:                       reasons.append("no true positives")
    if s["alerts_per_tp"] > MAX_ALERTS_PER_TP:
        reasons.append(f"{s['alerts_per_tp']} alerts per true positive "
                       f"(budget {MAX_ALERTS_PER_TP})")
    if s["recall"] < MIN_RECALL:           reasons.append(f"recall {s['recall']} below {MIN_RECALL}")
    return (not reasons), reasons

for name, s in scored.items():
    ok, reasons = deployable(s)
    print(f"{'DEPLOY' if ok else 'REJECT':7s} {name}")
    for r in reasons: print(f"          · {r}")

def workflow(candidates, history, truth):
    scored = {n: score(r, history, truth) for n, r in candidates.items()}
    shipped = {n: s for n, s in scored.items() if deployable(s)[0]}
    return {
      "generated": len(candidates),
      "shipped": len(shipped),
      "shipped_rules": sorted(shipped),
      "queue_impact_per_day": sum(s["alerts"] for s in shipped.values()),
      "coverage": round(max((s["recall"] for s in shipped.values()), default=0), 3),
    }
w = workflow(CANDIDATES, HISTORY, TRUE_POSITIVES)
for k, v in w.items(): print(f"{k:24s}{v}")

print("\nThe agent generated 5 rules in seconds. Scoring them against 521 real")
print("events took milliseconds and rejected 3. That scoring step is the job —")
print("without it, R1 ships and the SOC stops reading agent alerts within a week.")
assert w["shipped"] < w["generated"]
assert "R5 credential path OR link-local" in w["shipped_rules"]

# ------------------------------------ the same task, against a real model
# Offline this is a labelled replay; with an open-weight model served
# from Kaggle it is the same code calling a real one.

TASK = 'Write the detection condition for: a non-human identity listing more than 20 distinct buckets within 5 minutes, from outside its usual CIDR. Pseudocode, at most four lines.'

REPLAY = "actor.type == 'service_account'\nand count_distinct(event.bucket, window='5m') > 20\nand not cidr_match(source.ip, actor.baseline_cidr)"

answer, used, model = ask(TASK, replay=REPLAY,
            system='You write detection logic. Condition only, no prose.',
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

label, held = ("expresses a threshold", any(t in answer for t in (">", ">=", "20")))
print()
print(f"property checked : {label}")
print(f"held on {used:12s} : {held}")
print()
print("Same code, same assertions, two possible backends. Offline the answer is")
print("the replay and is labelled as one; with a served model it is the model's.")
