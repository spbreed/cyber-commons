#!/usr/bin/env python3
"""Calibrate severity from reachability and impact, and write the report a maintainer can act on.

This is the executable half of the `appsec-triage-report` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# --- the skill's own contract, available both ways -------------------------
# This script is run two ways and both have to work: standalone from a
# terminal, and embedded in the lesson notebook underneath the cell that
# already parsed the SKILL.md. So take what is already defined and read the
# file only when it is not.
import pathlib as _pathlib


def _skill_md():
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


if "contract_of" not in globals():
    import json, re

    def parse_skill(md):
        """Split a SKILL.md into (frontmatter dict, body).

        Frontmatter is a small, fixed subset of YAML: `key: value`, plus folded
        scalars (`description: >-`) whose continuation lines are indented. That is
        all a skill needs, and parsing it directly means no dependency.
        """
        if not md.startswith("---"):
            raise ValueError("a SKILL.md must open with a frontmatter block")
        _, front, body = md.split("---", 2)
        meta, key = {}, None
        for line in front.strip().splitlines():
            if not line.strip():
                continue
            if not line[0].isspace() and ":" in line:
                key, val = line.split(":", 1)
                key, val = key.strip(), val.strip()
                # `>-` and `|` open a folded block; the value is on the next lines
                meta[key] = "" if val in (">-", ">", "|", "|-") else val
            elif key is not None:
                meta[key] = (meta[key] + " " + line.strip()).strip()
        if "allowed-tools" in meta:
            meta["allowed-tools"] = [t.strip() for t in meta["allowed-tools"].split(",")
                                     if t.strip()]
        for required in ("name", "description"):
            if not meta.get(required):
                raise ValueError(f"skill is missing a {required!r}")
        return meta, body.strip()

    _WORD = re.compile(r"[a-z][a-z-]{3,}")

    def route(task, skills):
        """Pick the skill whose description best matches a task. Deterministic.

        The description is not documentation — it is the routing key. An agent
        decides whether to load a skill by reading it, so a vague description means
        the skill never fires when it should, and two overlapping descriptions mean
        the wrong one fires.

        Returns (pick, scores, margin). A margin of 0 means the top two scored the
        same and the "winner" is just whichever sorted first — an arbitrary answer
        wearing a confident face. Callers should refuse to auto-route on margin 0
        rather than pretend the tiebreak meant something.
        """
        want = set(_WORD.findall(task.lower()))
        def score(meta):
            return len(want & set(_WORD.findall(meta["description"].lower())))
        scores = {n: score(skills[n]) for n in sorted(skills)}
        # sort names first, then by score: ties must break identically on every
        # machine or the same task routes differently on two runs
        ranked = sorted(sorted(skills), key=lambda n: -scores[n])
        top = scores[ranked[0]]
        margin = top - (scores[ranked[1]] if len(ranked) > 1 else 0)
        return ranked[0], scores, margin

    def contract_of(body):
        """The JSON block under '## Output contract' — the skill's machine promise."""
        # non-greedy across any prose between the heading and the fence
        m = re.search(r"## Output contract\b.*?```json\n(.*?)```", body, re.S)
        if not m:
            raise ValueError("skill declares no output contract")
        return json.loads(m.group(1))

    def check(instance, contract, path="$"):
        """Structural conformance of an instance against a contract template.

        Returns the list of problems. An empty list means the shape is right — and
        that is *all* it means. Conformance is not accuracy: an empty findings list
        conforms perfectly and tells you nothing.
        """
        problems = []
        if isinstance(contract, dict):
            if not isinstance(instance, dict):
                return [f"{path}: expected an object, got {type(instance).__name__}"]
            for k, v in sorted(contract.items()):
                if k not in instance:
                    problems.append(f"{path}.{k}: missing")
                else:
                    problems += check(instance[k], v, f"{path}.{k}")
        elif isinstance(contract, list):
            if not isinstance(instance, list):
                return [f"{path}: expected a list, got {type(instance).__name__}"]
            for i, item in enumerate(instance):          # every element, same template
                problems += check(item, contract[0], f"{path}[{i}]")
        elif isinstance(contract, str) and "|" in contract:
            if instance not in contract.split("|"):
                problems.append(f"{path}: {instance!r} is not one of {contract}")
        elif isinstance(contract, bool):                  # before the numeric case:
            if not isinstance(instance, bool):            # bool is a subclass of int
                problems.append(f"{path}: expected bool, got {type(instance).__name__}")
        elif isinstance(contract, (int, float)):
            # JSON has one number type. A contract written `0` must accept 0.4, or
            # every cost and rate in the pipeline has to be rounded to satisfy a
            # checker rather than to be correct.
            if isinstance(instance, bool) or not isinstance(instance, (int, float)):
                problems.append(f"{path}: expected a number, got {type(instance).__name__}")
        elif not isinstance(instance, type(contract)):
            problems.append(f"{path}: expected {type(contract).__name__}, "
                            f"got {type(instance).__name__}")
        return problems

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
