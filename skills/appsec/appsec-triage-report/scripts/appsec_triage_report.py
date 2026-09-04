#!/usr/bin/env python3
"""Calibrate severity from reachability and impact, and write the report a maintainer can act on.

This is the executable half of the `appsec-triage-report` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# The skill runtime comes from the shared library, not from a copy in this file.
# In a lesson notebook the cell above has already loaded it; standalone, find it
# the same way that cell does.
import glob as _glob, importlib.util as _ilu, os as _os, sys as _sys

if "cyber_commons_skill_runtime" not in _sys.modules:
    _where = (sorted(_glob.glob("/kaggle/input/**/cyber-commons-skill-runtime/__script__.py",
                                recursive=True))
              + [_os.path.join(p, "skills/_runtime/cyber_commons_skill_runtime.py")
                 for p in (".", "..", "../..",
                           _os.path.join(_os.path.dirname(__file__), "../../../_runtime"))])
    _found = next((p for p in _where if _os.path.isfile(p)), None)
    if _found is None:
        raise SystemExit("shared skill runtime not found; looked at " + repr(_where))
    _spec = _ilu.spec_from_file_location("cyber_commons_skill_runtime", _found)
    _mod = _ilu.module_from_spec(_spec)
    _sys.modules["cyber_commons_skill_runtime"] = _mod
    _spec.loader.exec_module(_mod)

from cyber_commons_skill_runtime import check, contract_of, parse_skill


def _skill_md():
    """The SKILL.md next to this script, or the one the notebook already parsed."""
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


import pathlib as _pathlib

SKILL_MD = _skill_md()
meta, body = parse_skill(SKILL_MD)

from dataclasses import dataclass

@dataclass
class Finding:
    fid: str; cwe: str; rule_severity: str
    confirmed: bool; reachable: str        # reachable | unknown | unreachable
    chains_into: str                       # "" if none
    historical_risk: float

RULE_SEV = {"low":1,"medium":2,"high":3,"critical":4}
INV = {v:k for k,v in RULE_SEV.items()}
CHAIN_SEV = {"": 0, "data_exposure": 3, "account_takeover": 4, "admin_actions": 4}

FINDINGS = [
 Finding("F-01","CWE-89","high",  True,  "reachable",   "account_takeover", 0.82),
 Finding("F-02","CWE-89","high",  False, "unreachable", "", 0.10),
 Finding("F-03","CWE-22","medium",True,  "reachable",   "data_exposure", 0.91),
 Finding("F-04","CWE-798","high", False, "unknown",     "", 0.05),
 Finding("F-05","CWE-352","medium",True, "reachable",   "account_takeover", 0.30),
 Finding("F-06","CWE-89","high",  False, "unknown",     "", 0.40),
]

def calibrate(f):
    base = RULE_SEV[f.rule_severity]
    score = base
    why = [f"rule severity {f.rule_severity} ({base})"]
    if f.confirmed:            score += 2; why.append("confirmed by execution (+2)")
    else:                      score -= 1; why.append("not confirmed (-1)")
    if f.reachable == "reachable":     score += 1; why.append("reachable from an entry point (+1)")
    elif f.reachable == "unreachable": score -= 2; why.append("unreachable (-2)")
    else:                              why.append("reachability unknown (0)")
    if f.chains_into:
        score = max(score, CHAIN_SEV[f.chains_into] + 2)
        why.append(f"chains into {f.chains_into} (floor raised)")
    if f.historical_risk > 0.6: score += 1; why.append("in a historical risk zone (+1)")
    band = ("critical" if score >= 6 else "high" if score >= 4
            else "medium" if score >= 2 else "low")
    return {"fid": f.fid, "rule": f.rule_severity, "calibrated": band,
            "score": score, "why": why}

rows = [calibrate(f) for f in FINDINGS]
print(f"{'id':7s}{'rule sev':10s}{'calibrated':12s}{'score':>6}")
print("-" * 40)
for r in rows:
    moved = "" if r["rule"] == r["calibrated"] else "   ← moved"
    print(f"{r['fid']:7s}{r['rule']:10s}{r['calibrated']:12s}{r['score']:>6}{moved}")

by_rule = sorted(FINDINGS, key=lambda f: -RULE_SEV[f.rule_severity])
by_cal  = sorted(rows, key=lambda r: -r["score"])

print(f"{'rank':6s}{'by rule severity':22s}{'by calibrated severity':24s}")
print("-" * 56)
for i, (a, b) in enumerate(zip(by_rule, by_cal), 1):
    print(f"{i:<6}{a.fid + ' (' + a.rule_severity + ')':22s}"
          f"{b['fid'] + ' (' + b['calibrated'] + ')':24s}")

top_rule = {f.fid for f in by_rule[:3]}
top_cal  = {r["fid"] for r in by_cal[:3]}
print(f"\ntop-3 by rule       : {sorted(top_rule)}")
print(f"top-3 by calibration: {sorted(top_cal)}")
print(f"disagreement        : {sorted(top_rule ^ top_cal)}")
for r in rows:
    f = next(x for x in FINDINGS if x.fid == r["fid"])
    if r["fid"] in top_rule - top_cal:
        print(f"\n{r['fid']} is high by rule and {r['calibrated']} calibrated because:")
        for w in r["why"]: print(f"   · {w}")
assert top_rule != top_cal

from dataclasses import dataclass as dc

@dc
class Stage:
    name: str; found: int; escaped: int; false_positives: int; minutes: float

PIPELINE_STAGES = [
 Stage("design",   2,  9,  1,  40),
 Stage("code",    14,  6,  9,  70),
 Stage("review",   9,  4, 22, 110),
 Stage("test",     4,  2,  3,  50),
 Stage("deploy",   1,  1,  1,  20),
 Stage("runtime",  1,  0,  0, 180),
]
ESCAPE_MULTIPLIER = 6.0

print(f"{'stage':9s}{'found':>6}{'escaped':>9}{'FP':>5}{'precision':>11}{'min/find':>10}")
print("-" * 51)
for s in PIPELINE_STAGES:
    total = s.found + s.false_positives
    prec = s.found/total if total else 0
    per = s.minutes/s.found if s.found else 0
    print(f"{s.name:9s}{s.found:>6}{s.escaped:>9}{s.false_positives:>5}{prec:>11.2f}{per:>10.1f}")

def escape_cost(stages, m=ESCAPE_MULTIPLIER):
    n = len(stages)
    return {s.name: round(s.escaped * (m ** (n-i-1)) / 1000, 2)
            for i, s in enumerate(stages)}

costs = escape_cost(PIPELINE_STAGES)
print(f"\n{'stage':9s}{'escaped':>9}{'relative escape cost':>22}")
print("-" * 42)
for s in PIPELINE_STAGES:
    bar = "█" * min(int(costs[s.name] * 2), 34)
    print(f"{s.name:9s}{s.escaped:>9}{costs[s.name]:>14}  {bar}")

# The one-page report the pipeline actually emits.
def report(findings, calibrated, stages, costs):
    crit = [r for r in calibrated if r["calibrated"] == "critical"]
    confirmed = [f for f in findings if f.confirmed]
    unvalidated = [f for f in findings if not f.confirmed and f.reachable == "unknown"]
    worst_stage = max(costs, key=costs.get)
    return f"""APPSEC PIPELINE REPORT

  findings emitted            {len(findings)}
  confirmed by execution      {len(confirmed)}   (stage 12)
  unvalidated + unknown reach {len(unvalidated)}   ← a gap in probe generation, not a pass
  calibrated critical         {len(crit)}   {[r['fid'] for r in crit]}

  severity is calibrated from: confirmation, reachability, chaining and
  historical risk — not from the rule that fired.

  highest escape cost at stage: {worst_stage} ({costs[worst_stage]})
  → that is where the next analyser should be pointed, not where the
    most findings currently are."""

print(report(FINDINGS, rows, PIPELINE_STAGES, costs))
assert max(costs, key=costs.get) == "design"

contract = contract_of(body)
RANK = ["informational", "low", "medium", "high", "critical"]

def calibrated(f):
    """Severity from evidence, capped when nothing was reproduced."""
    base = f.rule_severity
    if not f.confirmed and RANK.index(base) > RANK.index("medium"):
        return "medium", f"capped from {base}: not reproduced"
    return base, "as assessed"

demonstrated, asserted = [], []
for f in FINDINGS:
    sev, why = calibrated(f)
    if f.confirmed:
        demonstrated.append({
          "finding_id": f.fid, "severity": sev,
          "severity_inputs": {"reproduced": f.confirmed,
                              "auth": "user", "sink": f.cwe},
          "title": f"{f.cwe} in {f.fid}", "impact": f.chains_into or "no demonstrated impact",
          "observable": f"{f.reachable} path exercised in the sandbox",
          "fix": f"remove the {f.cwe} class at the query layer",
          "fix_cost": "low"})
    else:
        asserted.append({"finding_id": f.fid, "severity": sev,
                         "why_not_demonstrated": f"{f.reachable}; {why}"})

summary = {k: 0 for k in RANK}
for d in demonstrated: summary[d["severity"]] += 1
for a_ in asserted:    summary[a_["severity"]] += 1

rep = {"report": {
  "summary": summary,
  "demonstrated": demonstrated,
  "asserted": asserted,
  "scope": {"analysed": [f.fid for f in FINDINGS],
            "deferred": ["dependencies not in scope"],
            "blind_spots": ["dynamic dispatch not resolved statically"]},
  "quality": {"validated": len(demonstrated),
              "failed_to_reproduce": len(asserted),
              "false_positive_rate": round(len(asserted) / len(FINDINGS), 2)},
}}
problems = check(rep, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\ndemonstrated {len(demonstrated)} · asserted {len(asserted)}")
for a_ in asserted:
    print(f"   {a_['finding_id']}  {a_['severity']:8s} {a_['why_not_demonstrated']}")
print(f"\nmeasured false-positive rate: {rep['report']['quality']['false_positive_rate']:.0%}")

raw_summary = {k: 0 for k in RANK}
for f in FINDINGS: raw_summary[f.rule_severity] += 1

print(f"{'severity':14s}{'uncalibrated':>14s}{'calibrated':>12s}")
for k in reversed(RANK):
    print(f"{k:14s}{raw_summary[k]:>14d}{summary[k]:>12d}")

inflated = [f.fid for f in FINDINGS
            if not f.confirmed and RANK.index(f.rule_severity) > RANK.index("medium")]
print(f"\nfindings reported above Medium on no evidence: {inflated}")
print()
print("Both versions are schema-valid; only one of them is defensible. The")
print("uncalibrated table leads with Highs that were never reproduced, and the")
print("reader cannot tell which. The first time one of them turns out to be a")
print("false positive, every other number in the report is discounted too.")
assert inflated, "the demo needs at least one finding the cap catches"
assert summary["high"] < raw_summary["high"]
