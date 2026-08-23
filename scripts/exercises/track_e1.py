"""E1 — The GRC Practitioner (Risk & Control). Nine sessions.

The governing insight for the whole E function: **point-in-time control testing
fails for AI**, because the thing you tested is not the thing running next week
and none of the changes that break it are code changes.

    E1.1  why point-in-time testing fails
    E1.2  the inventory — you cannot govern what you cannot list
    E1.3  risk tiering by authority and data, not by model
    E1.4  control mapping (control → framework, never the reverse)
    E1.5  evaluation output as audit evidence
    E1.6  operating vs outcome guardrails
    E1.7  continuous control verification
    E1.8  third-party and model supply chain
    E1.9  model and agent lifecycle governance
"""

from .skills import SKILL_RUNTIME

EXERCISES: dict[str, dict] = {

"E1.1": {
 "concept": """
Classical control testing has a simple shape: a control is designed, an auditor
tests it once or twice a year, and a passing test is recorded for the period.

That works when the thing being tested changes only through a process that
generates evidence. For an agent, the four things that change its behaviour are:

- the **model version** — changed by your provider, possibly without notice,
- the **prompt** — edited in a console,
- the **tool manifest** — a config change,
- the **approval settings** — a toggle in an admin UI.

None of them is a code change. None generates a change record. All of them
invalidate the conditions the control was tested under.

The honest consequence is that a control tested six months ago is not passing —
it is **unevidenced**, which is a third state most GRC tooling cannot represent.
Introducing that third state is the whole of this lesson.
""",
 "steps": [
  ("md", "## 2 · Demo — the same evidence, two ways of reading it"),
  ("py", '''import time
from dataclasses import dataclass, field

now = time.time(); DAY = 86400

@dataclass
class ControlTest:
    cid: str
    passed: bool
    evidence: str
    tested_at: float
    valid_for_days: float = 30

    def age_days(self, at): return (at - self.tested_at) / DAY
    def point_in_time(self, at): return "PASS" if self.passed else "FAIL"
    def continuous(self, at):
        if self.age_days(at) > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

TESTS = [
 ControlTest("AC-1", True,  "act chain sampled from gateway logs", now -   3*DAY),
 ControlTest("AC-2", True,  "delegation refusal regression suite", now -   9*DAY),
 ControlTest("SB-1", True,  "egress denial evidence",              now -  45*DAY),
 ControlTest("SB-2", True,  "approval gate screenshot",            now - 210*DAY),
 ControlTest("EV-1", True,  "audit sample of 50 agent actions",    now -   5*DAY),
 ControlTest("DR-1", False, "drift alerting not deployed",         now),
]
REQUIRED = ["AC-1", "AC-2", "SB-1", "SB-2", "EV-1", "DR-1", "EV-2", "ST-1"]

print(f"{'control':9s}{'age (days)':>12}{'point-in-time':>16}{'continuous':>13}")
print("-" * 52)
by_id = {t.cid: t for t in TESTS}
for cid in REQUIRED:
    t = by_id.get(cid)
    if t is None:
        print(f"{cid:9s}{'—':>12}{'(not tested)':>16}{'NO EVIDENCE':>13}")
        continue
    print(f"{cid:9s}{t.age_days(now):>12.0f}{t.point_in_time(now):>16}{t.continuous(now):>13}")
'''),
  ("md", "## 3 · Where it breaks — the two numbers those readings produce"),
  ("py", '''def posture(tests, required, at, mode):
    by_id = {t.cid: t for t in tests}
    passing = 0
    for cid in required:
        t = by_id.get(cid)
        if t is None: continue
        state = t.point_in_time(at) if mode == "point-in-time" else t.continuous(at)
        passing += state == "PASS"
    return passing, round(passing/len(required), 3)

for mode in ("point-in-time", "continuous"):
    n, pct = posture(TESTS, REQUIRED, now, mode)
    print(f"{mode:16s} {n}/{len(REQUIRED)} controls passing = {pct:.0%}")

print("\\nThe difference is entirely SB-1 and SB-2, which nobody did anything")
print("wrong to. Time simply passed, and the agent they were tested against")
print("has had two model upgrades since.")
'''),
  ("md", "## 4 · The control — a freshness window per control, derived from drift\n\n"
         "The window is not an audit-calendar choice. It comes from **how fast "
         "the thing the control tests actually changes.**"),
  ("py", '''DRIFT_RATE = {          # observed TVD/day for what each control depends on
 "AC-1": 0.0005,        # identity model changes slowly
 "AC-2": 0.0005,
 "SB-1": 0.0020,        # egress needs change with new integrations
 "SB-2": 0.0090,        # tool manifests change weekly
 "EV-1": 0.0010,
 "DR-1": 0.0090,
}
TOLERANCE = 0.25

def window(cid):
    r = DRIFT_RATE.get(cid)
    return int(TOLERANCE / r) if r else 90

print(f"{'control':9s}{'drift/day':>12}{'window (days)':>15}{'current age':>13}{'state':>9}")
print("-" * 60)
for cid in REQUIRED:
    t = by_id.get(cid)
    w = window(cid)
    if t is None:
        print(f"{cid:9s}{'—':>12}{w:>15}{'—':>13}{'NO EVIDENCE':>9}")
        continue
    t.valid_for_days = w
    print(f"{cid:9s}{DRIFT_RATE.get(cid, 0):>12.4f}{w:>15}{t.age_days(now):>13.0f}"
          f"{t.continuous(now):>9}")

n, pct = posture(TESTS, REQUIRED, now, "continuous")
print(f"\\nwith drift-derived windows: {n}/{len(REQUIRED)} = {pct:.0%} currently evidenced")
assert pct < 0.6
print("\\nSB-2 tests a tool manifest that changes weekly; a 210-day-old screenshot")
print("cannot evidence it. Saying so is the control, not a criticism of anyone.")
'''),
 ],
 "expect": "Point-in-time reading reports 5 of 8 controls passing (63%); the "
           "continuous reading reports 3 of 8 (38%), with SB-1 and SB-2 STALE and "
           "EV-2 and ST-1 having no evidence at all. Drift-derived windows tighten "
           "SB-2 to roughly 27 days, confirming a 210-day-old screenshot cannot "
           "evidence a weekly-changing manifest.",
 "challenge": "Pick your three most important AI controls and set a freshness "
              "window for each from the observed change rate of what it tests. "
              "Then recompute your posture. The number will drop, and it will be "
              "the first honest one you have had.",
},

"E1.2": {
 "concept": """
You cannot govern, tier, test or revoke what you cannot list. The AI inventory is
therefore the first control, not a documentation exercise.

The honest finding of every first inventory is the same: **most of it was already
in production.** Not because anyone was reckless, but because AI features arrive
inside products you already bought, and agents get created programmatically by
other agents.

Three sources, and the third finds what the first two miss:

1. the **model registry** — what your ML team registered,
2. **procurement and expense** — what someone bought,
3. **egress logs to model-provider domains** — what is actually being used.

Source 3 is the one that discovers the department using a frontier API on a
personal card, and the SaaS product that quietly added an AI feature.
""",
 "steps": [
  ("md", "## 2 · Demo — build the inventory from three sources"),
  ("py", '''from dataclasses import dataclass, field

@dataclass
class AIAsset:
    name: str
    kind: str              # model | agent | copilot | embedded-feature
    owner: str = ""
    autonomy: str = "L1"
    data: tuple = ()
    external: bool = False
    discovered_via: str = "registry"

    def gaps(self):
        g = []
        if not self.owner:
            g.append("no named owner — nobody can accept the risk or recertify it")
        if self.discovered_via != "registry":
            g.append(f"not registered — found via {self.discovered_via}")
        if self.autonomy in ("L2.5", "L3") and not self.owner:
            g.append("acts semi-autonomously with nobody accountable")
        return g

REGISTRY = [
 AIAsset("fraud-scoring-model", "model", "risk-eng", "L1", ("customer",)),
 AIAsset("support-summariser", "copilot", "support-eng", "L1", ("customer",)),
]
PROCUREMENT = [
 AIAsset("vendor-contract-analyser", "embedded-feature", "", "L1", ("regulated",),
         discovered_via="expense report"),
]
EGRESS = [
 AIAsset("unknown-openai-usage-marketing", "copilot", "", "L1", ("public",),
         discovered_via="egress logs"),
 AIAsset("pr-remediation-agent", "agent", "", "L2.5", ("customer",), True,
         discovered_via="egress logs"),
 AIAsset("agent-worker-7f3c", "agent", "", "L2.5", ("customer",),
         discovered_via="egress logs"),
]
ALL = REGISTRY + PROCUREMENT + EGRESS
print(f"{'asset':34s}{'kind':18s}{'autonomy':10s}{'owner':14s}found via")
print("-" * 92)
for a in ALL:
    print(f"{a.name:34s}{a.kind:18s}{a.autonomy:10s}{a.owner or '—':14s}{a.discovered_via}")
print(f"\\nregistry found {len(REGISTRY)}; the other two sources found "
      f"{len(ALL)-len(REGISTRY)} more.")
'''),
  ("md", "## 3 · Where it breaks — the gap distribution is always like this"),
  ("py", '''unowned = [a for a in ALL if not a.owner]
unregistered = [a for a in ALL if a.discovered_via != "registry"]
high_autonomy_unowned = [a for a in ALL if a.autonomy in ("L2.5","L3") and not a.owner]

print(f"assets                    {len(ALL)}")
print(f"no named owner            {len(unowned)}  {[a.name for a in unowned]}")
print(f"never registered          {len(unregistered)}")
print(f"L2.5+ with no owner       {len(high_autonomy_unowned)}  "
      f"{[a.name for a in high_autonomy_unowned]}")

print("\\ngaps in detail:")
for a in ALL:
    for g in a.gaps():
        print(f"   {a.name:34s}{g}")
assert high_autonomy_unowned
'''),
  ("md", "## 4 · The control — a discovery query you can re-run"),
  ("py", '''MODEL_PROVIDER_DOMAINS = {"api.openai.com", "api.anthropic.com",
                          "generativelanguage.googleapis.com",
                          "api.mistral.ai", "api.together.xyz"}

EGRESS_LOG = [
 {"src": "marketing-workstation-14", "host": "api.openai.com", "bytes": 240_000},
 {"src": "svc-pr-remediation",       "host": "api.anthropic.com", "bytes": 8_400_000},
 {"src": "build-runner-3",           "host": "registry.npmjs.org", "bytes": 90_000},
 {"src": "agent-worker-7f3c",        "host": "api.together.xyz", "bytes": 1_200_000},
]
def discover(log, known_names):
    found = []
    for row in log:
        if row["host"] not in MODEL_PROVIDER_DOMAINS: continue
        if row["src"] in known_names: continue
        found.append({"source": row["src"], "provider": row["host"],
                      "volume": row["bytes"],
                      "finding": "AI usage not present in the inventory"})
    return found

known = {a.name for a in REGISTRY + PROCUREMENT}
for f in discover(EGRESS_LOG, known):
    print(f"{f['source']:30s}{f['provider']:34s}{f['volume']:>10,} bytes")
    print(f"{'':30s}{f['finding']}")

def inventory_health(assets):
    return {"total": len(assets),
            "owned": sum(1 for a in assets if a.owner),
            "registered": sum(1 for a in assets if a.discovered_via == "registry"),
            "coverage": round(sum(1 for a in assets if a.owner)/len(assets), 2)}
print(f"\\n{inventory_health(ALL)}")
'''),
 ],
 "expect": "The registry lists 2 assets; procurement and egress logs find 4 more. "
           "Four assets have no owner, four were never registered, and two "
           "L2.5-autonomy agents have nobody accountable. The egress query "
           "identifies three sources talking to model providers that are absent "
           "from the inventory, giving an ownership coverage of 0.33.",
 "challenge": "Run the egress query for real: one week of traffic to model-"
              "provider domains, joined against your inventory. It takes an hour "
              "and it always finds something.",
},

"E1.3": {
 "concept": """
Risk-tier by what the system **can do**, not by which model it uses.

Tiering on model capability is the common mistake and it tracks vendor marketing
rather than exposure: every GPT-class deployment becomes "high" and every small
model "low". That gets the answer exactly backwards for the case that matters —
a small local model with production deploy rights and regulated data.

Three inputs determine consequence, and none of them is the model:

- **Autonomy** — what its output can trigger without a human.
- **Data** — what it can read, especially regulated or customer data.
- **Reach** — whether it can act externally.

The model matters for *likelihood* of a bad output, which is a different and
smaller term than consequence.
""",
 "steps": [
  ("md", "## 2 · Demo — tier by authority and data"),
  ("py", '''from dataclasses import dataclass

@dataclass
class AIAsset:
    name: str; kind: str; owner: str = ""; autonomy: str = "L1"
    data: tuple = (); external: bool = False; registered: bool = True

TIER_THRESHOLDS = [(9, "critical"), (6, "high"), (3, "medium"), (0, "low")]

def risk_tier(a):
    score, why = 0, []
    pts = {"L1": 0, "L2": 1, "L2.5": 3, "L3": 5}[a.autonomy]
    if pts: score += pts; why.append(f"autonomy {a.autonomy} (+{pts})")
    if "regulated" in a.data: score += 3; why.append("regulated data (+3)")
    if "customer" in a.data:  score += 2; why.append("customer data (+2)")
    if a.external:            score += 2; why.append("can act externally (+2)")
    if not a.registered:      score += 1; why.append("unregistered (+1)")
    tier = next(t for th, t in TIER_THRESHOLDS if score >= th)
    return {"tier": tier, "score": score, "because": why}

ASSETS = [
 AIAsset("frontier chatbot, public docs, read-only", "copilot", "x", "L1", ("public",)),
 AIAsset("small local model with prod deploy rights", "agent", "x", "L3",
         ("customer", "regulated"), True),
 AIAsset("mid model, gated writes, internal only", "agent", "x", "L2", ("employee",)),
 AIAsset("frontier model summarising customer tickets", "copilot", "x", "L1",
         ("customer",)),
 AIAsset("unregistered remediation agent", "agent", "", "L2.5", ("customer",),
         True, registered=False),
]
print(f"{'asset':46s}{'tier':10s}{'score':>6}")
print("-" * 66)
for a in ASSETS:
    t = risk_tier(a)
    print(f"{a.name:46s}{t['tier']:10s}{t['score']:>6}")
    for w in t["because"]:
        print(f"{'':46s}{w}")
'''),
  ("md", "## 3 · Where it breaks — tier by model instead, and compare"),
  ("py", '''MODEL_TIER = {   # the questionnaire that asks 'which model?' first
 "frontier chatbot, public docs, read-only": "high",
 "small local model with prod deploy rights": "low",
 "mid model, gated writes, internal only": "medium",
 "frontier model summarising customer tickets": "high",
 "unregistered remediation agent": "medium",
}
print(f"{'asset':46s}{'by model':10s}{'by authority':14s}agreement")
print("-" * 84)
disagreements = 0
for a in ASSETS:
    by_auth = risk_tier(a)["tier"]
    by_model = MODEL_TIER[a.name]
    agree = by_auth == by_model
    disagreements += not agree
    print(f"{a.name:46s}{by_model:10s}{by_auth:14s}{'' if agree else '← DISAGREE'}")
print(f"\\n{disagreements}/{len(ASSETS)} disagree.")
print("The worst inversion: the small local model with deploy rights tiers LOW")
print("on model capability and CRITICAL on what it can actually do.")
assert risk_tier(ASSETS[1])["tier"] == "critical"
assert MODEL_TIER[ASSETS[1].name] == "low"
'''),
  ("md", "## 4 · The control — the four questions the questionnaire should ask"),
  ("py", '''QUESTIONS = [
 ("What can it change without a human approving that specific action?",
  "autonomy — the largest term"),
 ("What data can it read, and is any of it regulated or customer data?",
  "consequence of a leak"),
 ("Can it act outside our boundary?",
  "reach"),
 ("Is it registered, with a named owner?",
  "governability — an unowned asset cannot be remediated"),
]
NOT_ASKED = [
 "Which model does it use?",
 "How many parameters?",
 "Is the vendor SOC 2 certified?",
]
print("ASK:")
for q, why in QUESTIONS: print(f"   {q}\\n      → {why}")
print("\\nDO NOT tier on:")
for q in NOT_ASKED: print(f"   {q}")
print("   (these matter for LIKELIHOOD and vendor risk — a separate, smaller term)")

def tier_from_answers(can_change, reads_regulated, reads_customer, external, registered):
    a = AIAsset("x", "agent", "o" if registered else "", can_change,
                tuple(filter(None, ("regulated" if reads_regulated else "",
                                    "customer" if reads_customer else ""))),
                external, registered)
    return risk_tier(a)["tier"]

print("\\nworked example — a new request:")
print("   'an agent that can issue refunds up to £500, reads customer orders,'")
print("   'runs internally, owned by payments-eng'")
print("   tier:", tier_from_answers("L2.5", False, True, False, True))
'''),
 ],
 "expect": "The public read-only chatbot tiers low; the small local model with "
           "deploy rights and regulated data tiers critical at score 12. Tiering "
           "by model disagrees on 4 of 5 assets, most sharply inverting the small "
           "local model from low to critical. The worked example tiers the refund "
           "agent as high.",
 "challenge": "Re-tier your top ten AI use cases using only the four questions. "
              "Note which ones move, and be ready to explain the movement to "
              "whoever wrote the original questionnaire — the model question is "
              "usually question one.",
},

"E1.4": {
 "concept": """
Control mapping runs one way: **control → framework.**

Starting from the framework produces a checklist that is complete, satisfies an
assessor, and defends nothing — because it enumerates clauses rather than
capabilities, and a clause with no operating control behind it evidences nothing.

Starting from controls produces the opposite: a smaller list of things you
actually do, each of which happens to satisfy several framework clauses. The
framework coverage is an **output**, and that is the only mapping that survives a
supervisor asking "show me".
""",
 "steps": [
  ("md", "## 2 · Demo — the control catalogue, and what it satisfies"),
  ("py", '''from dataclasses import dataclass

@dataclass(frozen=True)
class Control:
    cid: str; text: str; kind: str; frameworks: tuple

CATALOGUE = [
 Control("AC-1", "agent identities are distinct from human and separately revocable",
         "preventive", ("NIST AI RMF: GOVERN-1.2", "ISO 42001: 6.1", "EU AI Act: Art.14")),
 Control("AC-2", "delegated authority narrows at every hop and is recorded in an act chain",
         "preventive", ("NIST AI RMF: MANAGE-2.2", "ISO 42001: 8.1")),
 Control("SB-1", "agent egress is deny-by-default with an allowlist",
         "preventive", ("NIST AI RMF: MANAGE-2.1", "ISO 27001: A.8.20")),
 Control("SB-2", "privileged tools require approval below autonomy L3",
         "preventive", ("EU AI Act: Art.14 human oversight",)),
 Control("EV-1", "every agent action is logged with the acting identity",
         "detective", ("ISO 42001: 9.1", "EU AI Act: Art.12 record-keeping")),
 Control("EV-2", "harness accuracy evaluated against a held-out key each release",
         "detective", ("NIST AI RMF: MEASURE-2.3",)),
 Control("DR-1", "behavioural drift from the signed-off baseline raises an alert",
         "detective", ("NIST AI RMF: MEASURE-2.4", "ISO 42001: 9.1")),
 Control("ST-1", "a tested stop mechanism halts an agent fleet without vendor help",
         "corrective", ("EU AI Act: Art.14", "DORA: Art.11")),
]
print(f"{'control':8s}{'kind':12s}satisfies")
print("-" * 84)
for c in CATALOGUE:
    print(f"{c.cid:8s}{c.kind:12s}{len(c.frameworks)} clause(s): {c.frameworks[0]}")
    for f in c.frameworks[1:]:
        print(f"{'':20s}{f}")
'''),
  ("py", '''def map_controls(tier, catalogue=CATALOGUE):
    if tier in ("critical", "high"):
        required = list(catalogue)
    else:
        required = [c for c in catalogue if c.kind == "preventive" or c.cid == "EV-1"]
    frameworks = sorted({f for c in required for f in c.frameworks})
    return {"tier": tier, "controls": [c.cid for c in required],
            "frameworks_satisfied": frameworks}

for tier in ("critical", "medium"):
    m = map_controls(tier)
    print(f"\\ntier {tier}: {len(m['controls'])} controls → "
          f"{len(m['frameworks_satisfied'])} framework clauses")
    print(f"   controls   {m['controls']}")
    for f in m["frameworks_satisfied"]:
        print(f"   satisfies  {f}")
'''),
  ("md", "## 3 · Where it breaks — start from the framework instead"),
  ("py", '''FRAMEWORK_CLAUSES = [
 "NIST AI RMF: GOVERN-1.1 policies are documented",
 "NIST AI RMF: GOVERN-1.2 roles and responsibilities are defined",
 "NIST AI RMF: MAP-1.1 context is established",
 "NIST AI RMF: MEASURE-2.3 performance is evaluated",
 "ISO 42001: 6.1 actions to address risks",
 "ISO 42001: 7.2 competence",
 "ISO 42001: 9.1 monitoring and measurement",
]
have = {f for c in CATALOGUE for f in c.frameworks}
print(f"{'clause':52s}{'operating control?':>20}")
print("-" * 74)
orphans = []
for clause in FRAMEWORK_CLAUSES:
    covered = clause in have
    if not covered: orphans.append(clause)
    print(f"{clause:52s}{('yes' if covered else 'NO — checklist only'):>20}")
print(f"\\n{len(orphans)}/{len(FRAMEWORK_CLAUSES)} clauses have no operating control behind them.")
print("Working framework-first, those get a policy document and a tick. Working")
print("control-first, they are visibly uncovered — which is the useful state.")
assert orphans
'''),
  ("md", "## 4 · The control — evidence flows from the control, not the clause"),
  ("py", '''EVIDENCE = {
 "AC-1": "gateway logs containing an act chain for every action; monthly sample",
 "AC-2": "regression suite cases IDN-01/IDN-04, run on every release",
 "SB-1": "90-day egress denial log",
 "SB-2": "tool policy in git + denial log",
 "EV-1": "audit sample of 50 actions with acting identity present",
 "EV-2": "expert accuracy against a held-out key, per release",
 "DR-1": "drift alerts and their dispositions",
 "ST-1": "game-day record with measured time-to-stop",
}
def evidence_pack(tier):
    m = map_controls(tier)
    return [{"control": cid, "evidence": EVIDENCE[cid],
             "satisfies": [f for c in CATALOGUE if c.cid == cid for f in c.frameworks]}
            for cid in m["controls"]]

pack = evidence_pack("critical")
for row in pack[:4]:
    print(f"{row['control']}  {row['evidence']}")
    for f in row["satisfies"]:
        print(f"      → {f}")
print(f"\\n{len(pack)} controls produce evidence for "
      f"{len({f for r in pack for f in r['satisfies']})} framework clauses.")
print("One artefact, many clauses. That ratio is why control-first is cheaper.")
'''),
 ],
 "expect": "The catalogue's 8 controls map to framework clauses across NIST AI "
           "RMF, ISO 42001, ISO 27001, the EU AI Act and DORA. Critical tier "
           "requires all 8 and satisfies 12 clauses; medium requires 5. Working "
           "framework-first leaves 3 of 7 clauses with no operating control. The "
           "evidence pack shows one artefact satisfying several clauses.",
 "challenge": "Take one framework clause your programme claims to satisfy and ask "
              "which operating control produces its evidence. If the answer is a "
              "policy document, the clause is ticked and undefended.",
},

"E1.5": {
 "concept": """
Evaluation output is the strongest audit evidence an AI programme can produce,
and it only works if you present the right number.

B2.10 established the distinction; this lesson turns it into evidence:

- **Conformance** — schema validity. ~100% by construction. A build-health
  signal, not a quality claim.
- **Expert accuracy** — correctness against a held-out key. The number that
  evidences anything.

Four properties make an eval result auditable:

1. the key was **held out** — the harness never saw it,
2. the number reported is **accuracy**, not conformance,
3. the **sample size** is stated,
4. it **expires**, so it cannot silently age into a claim.

Miss the fourth and you have produced a number that will be quoted three years
from now about a system that has since had six model upgrades.
""",
 "steps": [
  ("md", "## 2 · Demo — produce the evidence"),
  ("py", '''import json, time
from dataclasses import dataclass, field

@dataclass
class Truth:
    qid: str; cwe: str; file: str

def path_key(p):
    parts = [x for x in p.replace("\\\\", "/").split("/") if x not in ("", ".")]
    return "/".join(parts[-2:]) if len(parts) > 1 else (parts[-1] if parts else "")

TRUTHS = {f"q{i}": Truth(f"q{i}", ["CWE-89","CWE-78","CWE-22","CWE-798"][i % 4],
                         f"{['CWE-89','CWE-78','CWE-22','CWE-798'][i % 4]}/{i}.py")
          for i in range(1, 25)}

def harness_answers(truths, skill=0.75, seed=5):
    import random
    rng = random.Random(seed)
    out = {}
    for q, t in truths.items():
        right = rng.random() < skill
        out[q] = json.dumps({"qid": q, "cwe": t.cwe if right else "CWE-89",
                             "file": t.file, "line": 1,
                             "rationale": "untrusted input reaches the sink"})
    return out

def evaluate(answers, truths):
    conforming = expert = 0
    for q, t in truths.items():
        try: d = json.loads(answers[q])
        except (json.JSONDecodeError, KeyError): continue
        conforming += 1
        if path_key(d["file"]) != path_key(t.file): continue
        expert += 1.0 if d["cwe"].upper() == t.cwe else 0.5
    return {"n": len(truths),
            "conformance": round(conforming/len(truths), 4),
            "expert_accuracy": round(expert/len(truths), 4)}

r = evaluate(harness_answers(TRUTHS), TRUTHS)
print(f"n                {r['n']}")
print(f"conformance      {r['conformance']:.4f}   ← structural. NOT a quality claim.")
print(f"expert accuracy  {r['expert_accuracy']:.4f}   ← the number that evidences EV-2")
'''),
  ("md", "## 3 · Where it breaks — the number that gets quoted"),
  ("py", '''CLAIMS = [
 ("Our AI security harness scores 100%.", "conformance", False),
 ("Our harness achieves 100% schema conformance.", "conformance", True),
 ("Our harness scores 0.81 expert accuracy on a 24-question held-out set.",
  "accuracy", True),
 ("Our harness passes all automated checks.", "unspecified", False),
]
print(f"{'claim':66s}{'defensible?':>12}")
print("-" * 80)
for text, kind, ok in CLAIMS:
    print(f"{text:66s}{str(ok):>12}")
print("\\nClaim 1 is TRUE and misleading — conformance really is 100%.")
print("Claim 4 is the most common and evidences nothing at all.")
'''),
  ("md", "## 4 · The control — evidence with an expiry"),
  ("py", '''DAY = 86400
now = time.time()

@dataclass
class ControlTest:
    cid: str; passed: bool; evidence: str
    tested_at: float; valid_for_days: float
    def state(self, at):
        if (at - self.tested_at)/DAY > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

THRESHOLD = 0.80
test = ControlTest(
    "EV-2",
    passed=r["expert_accuracy"] >= THRESHOLD,
    evidence=(f"expert accuracy {r['expert_accuracy']:.4f} over {r['n']} held-out "
              f"questions; conformance {r['conformance']:.4f} reported separately; "
              f"key never exposed to the harness"),
    tested_at=now, valid_for_days=30)

print(f"EV-2  {test.state(now)}")
print(f"      {test.evidence}")
for age in (10, 45):
    print(f"      at +{age}d → {test.state(now + age*DAY)}")

CHECKLIST = {
 "key held out":         True,
 "accuracy not conformance reported": True,
 "sample size stated":   True,
 "expires":              test.valid_for_days > 0,
 "threshold stated up front": True,
}
print("\\nauditability checklist:")
for k, v in CHECKLIST.items():
    print(f"   {'PASS' if v else 'FAIL'}  {k}")
assert all(CHECKLIST.values())
assert test.state(now + 45*DAY) == "STALE"
'''),

  ("md", "## 6 · The evidence pack, as a skill\n\n"
         "An evaluation result becomes evidence only when it tested the control "
         "that is claimed, ran on the system that is **deployed**, and states "
         "its failure mode. Most evidence fails the second.\n\n"
         "The contract carries a field most packs would rather not have: "
         "`conformance_reported`. Setting it true should be read as a defect in "
         "the evidence, not a feature of it."),
  ("py", SKILL_RUNTIME),
  ("skill", "grc/control-evidence"),

  ("py", '''contract = contract_of(body)

pack = {
 "control": {"id": "AI-07", "claim": "Egress from the agent workload is denied "
                                     "to destinations outside the allowlist, "
                                     "enforced at the gateway",
             "testable": True},
 "binding": {"model": "glm-4.6", "config_hash": "sha256:7f3a1c",
             "tools": ["read_file", "http_get"], "commit": "6a14d8b",
             "matches_deployed": True},
 "sample": {"population": len(TRUTHS), "tested": len(TRUTHS),
            "selection": "risk_based", "independent": False},
 # r came from evaluate() above: conformance and expert accuracy on the same
 # run. Only one of them belongs in an evidence pack as a quality number.
 "results": {"operating_effectiveness": 1.0,
             "outcome_effectiveness": r["expert_accuracy"],
             "accuracy": r["expert_accuracy"],
             # the honest default, and the one line an auditor looks for
             "conformance_reported": False},
 "blind_spots": ["cases not in the corpus",
                 "drift since the run",
                 "the sample was chosen by the team that built the control"],
 "reverification": {"trigger": "on_model_change", "interval_days": 0},
 "conclusion": {"supports_claim": True,
                "limits": "evidences the gateway control only, at this commit"},
}
problems = check(pack, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\\ncontrol      : {pack['control']['id']} (testable={pack['control']['testable']})")
print(f"bound to     : {pack['binding']['model']} @ {pack['binding']['commit']}, "
      f"matches deployed={pack['binding']['matches_deployed']}")
print(f"operating    : {pack['results']['operating_effectiveness']:.0%}   "
      f"outcome: {pack['results']['outcome_effectiveness']:.0%}")
print(f"sample       : {pack['sample']['tested']}/{pack['sample']['population']}, "
      f"independent={pack['sample']['independent']}")
print(f"re-verify on : {pack['reverification']['trigger']}")
print()
print("Operating effectiveness says the gate ran on every request. Outcome")
print("effectiveness says whether anything harmful still got through. Auditors")
print("ask for the first; incidents are caused by the second. Give both,")
print("labelled, or the pack answers a question nobody asked.")
assert pack["results"]["conformance_reported"] is False
assert pack["sample"]["independent"] is False   # stated, not hidden
'''),

  ("md", "## 7 · Where it breaks — the pack that leads with conformance\n\n"
         "The most common overstatement in automated assurance, and it is "
         "usually made in good faith."),
  ("py", '''flattering = dict(pack, results=dict(pack["results"],
                     accuracy=r["conformance"], conformance_reported=True))
print(f"conformance problems: {len(check(flattering, contract))}   <- still zero")
print()
print(f"claimed    : {r['conformance']:.0%} schema-valid output")
print(f"measured   : accuracy {pack['results']['accuracy']:.0%} on "
      f"{pack['sample']['tested']} cases")
print()
print("Schema validity is near-free by construction: an empty result scores")
print("100%. It is a statement about the serialiser, not about whether the")
print("control works. An auditor who notices the substitution discounts every")
print("other number in the pack, which is the expensive part.")
assert not check(flattering, contract), "the flattering pack conforms - that is the point"
assert flattering["results"]["conformance_reported"] is True
'''),
 ],
 "expect": "Conformance is 1.0000 while expert accuracy lands around 0.81 on 24 "
           "held-out questions. Two of four sample claims are defensible. The EV-2 "
           "control test passes against a stated 0.80 threshold, is valid for 30 "
           "days, and reads STALE at 45 days. All five auditability checks pass.",
 "challenge": "Find an eval number your organisation has quoted, internally or "
              "externally, and determine which of the two it was. Then check "
              "whether it has an expiry. Most do not, and are still being cited.",
},

"E1.6": {
 "concept": """
Guardrails come in two kinds, and confusing them is how a programme passes audit
while missing harm.

**Operating guardrails** constrain *how the system runs*: all egress through the
gateway, privileged tools gated below L3, every action logged. They are testable
today, cheap to verify, and produce clean evidence.

**Outcome guardrails** constrain *what results are acceptable*: no unrecoverable
customer data loss, no increase in customer-facing incidents, no disparate
outcomes across segments. They matter more and most need a measurement you do
not yet have.

The failure is not choosing one. It is shipping only the first column, reporting
it as coverage, and never labelling the second column as unmeasured.
""",
 "steps": [
  ("md", "## 2 · Demo — classify a real guardrail set"),
  ("py", '''def classify(rule, constrains_outcome, measurement_exists):
    kind = "outcome" if constrains_outcome else "operating"
    if kind == "operating":
        return {"rule": rule, "kind": kind, "enforceable_today": True,
                "risk": "may satisfy audit while missing real harm"}
    return {"rule": rule, "kind": kind, "enforceable_today": measurement_exists,
            "risk": ("enforceable" if measurement_exists
                     else "needs an agreed measurement before it can be enforced")}

RULES = [
 ("all agent egress goes through the gateway", False, True),
 ("privileged tools require approval below L3", False, True),
 ("every action is logged with the acting identity", False, True),
 ("agent identities are separately revocable", False, True),
 ("no agent action causes unrecoverable customer data loss", True, False),
 ("automated remediation does not increase customer-facing incidents", True, True),
 ("model outputs do not produce disparate outcomes across segments", True, False),
]
print(f"{'rule':60s}{'kind':11s}{'enforceable':>12}")
print("-" * 86)
for rule, outcome, measurable in RULES:
    c = classify(rule, outcome, measurable)
    print(f"{c['rule']:60s}{c['kind']:11s}{str(c['enforceable_today']):>12}")
'''),
  ("md", "## 3 · Where it breaks — the coverage number that lies"),
  ("py", '''operating = [r for r in RULES if not r[1]]
outcome   = [r for r in RULES if r[1]]
enforceable_outcome = [r for r in outcome if r[2]]

print(f"operating guardrails : {len(operating)}  all enforceable today")
print(f"outcome guardrails   : {len(outcome)}  of which enforceable: "
      f"{len(enforceable_outcome)}")

naive = len(operating) / len(RULES)
honest = (len(operating) + len(enforceable_outcome)) / len(RULES)
print(f"\\n'guardrail coverage' if you count only what you shipped: "
      f"{len(operating)}/{len(operating)} = 100%")
print(f"coverage across ALL agreed guardrails: "
      f"{len(operating)+len(enforceable_outcome)}/{len(RULES)} = {honest:.0%}")
print("\\nThe first number is what usually reaches a steering committee.")
'''),
  ("md", "## 4 · The control — define the measurement, or label it unmeasured"),
  ("py", '''def specify_outcome_guardrail(rule, metric, threshold, source, cadence):
    complete = all([metric, threshold is not None, source, cadence])
    return {"rule": rule, "metric": metric, "threshold": threshold,
            "source": source, "cadence": cadence,
            "status": "enforceable" if complete else "ASPIRATION — label it as such"}

SPECS = [
 specify_outcome_guardrail(
   "automated remediation does not increase customer-facing incidents",
   metric="customer-facing SEV1+SEV2 per 1000 remediations",
   threshold=1.2, source="incident management system", cadence="monthly"),
 specify_outcome_guardrail(
   "no agent action causes unrecoverable customer data loss",
   metric="", threshold=None, source="", cadence=""),
]
for s in SPECS:
    print(f"{s['rule']}")
    print(f"   metric   {s['metric'] or '—'}")
    print(f"   threshold {s['threshold'] if s['threshold'] is not None else '—'}")
    print(f"   source   {s['source'] or '—'}")
    print(f"   status   {s['status']}\\n")

def programme_statement(rules, specs):
    enforceable = len([r for r in rules if not r[1]]) + \\
                  len([s for s in specs if s["status"] == "enforceable"])
    aspirations = [s["rule"] for s in specs if s["status"] != "enforceable"]
    return (f"{enforceable}/{len(rules)} guardrails are enforceable today.\\n"
            f"The following are agreed but UNMEASURED, and are not counted as "
            f"coverage:\\n" + "\\n".join(f"   - {a}" for a in aspirations))
print(programme_statement(RULES, SPECS))
assert any(s["status"] != "enforceable" for s in SPECS)
'''),
 ],
 "expect": "Four operating guardrails are all enforceable today; three outcome "
           "guardrails are enforceable only where a measurement exists. Counting "
           "only what shipped gives 100% coverage; counting all agreed guardrails "
           "gives 71%. One outcome guardrail is fully specified and enforceable; "
           "the other is labelled an aspiration and excluded from coverage.",
 "challenge": "Pick one outcome guardrail your programme has agreed and specify "
              "its metric, threshold, source and cadence precisely enough that "
              "someone could dispute the result. If you cannot, say so in the "
              "coverage report rather than counting it.",
},

"E1.7": {
 "concept": """
Continuous control verification is the operating model that follows from E1.1.

The number that matters is not how much passed once. It is **how much is
currently evidenced** — controls whose most recent test is passing *and* within
its freshness window.

Three states, and the third is the one classical GRC tooling cannot express:

- **PASS** — tested, passing, in window.
- **FAIL** — tested, failing. Honest and actionable.
- **STALE** — tested, was passing, out of window. **Not a pass.**

Plus the absence state: no evidence at all, which is different from failing and
is often the largest category in a first assessment.
""",
 "steps": [
  ("md", "## 2 · Demo — the posture, computed honestly"),
  ("py", '''import time
from dataclasses import dataclass

now = time.time(); DAY = 86400

@dataclass
class ControlTest:
    cid: str; passed: bool; evidence: str
    tested_at: float; valid_for_days: float
    def age(self, at): return (at - self.tested_at)/DAY
    def state(self, at):
        if self.age(at) > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]
TESTS = [
 ControlTest("AC-1", True,  "act chain sample",        now -   2*DAY, 30),
 ControlTest("AC-2", True,  "delegation regression",   now -   9*DAY, 30),
 ControlTest("SB-1", True,  "egress denial log",       now -  31*DAY, 30),
 ControlTest("SB-2", True,  "approval gate screenshot",now - 120*DAY, 27),
 ControlTest("EV-1", True,  "audit sample of 50",      now -   5*DAY, 60),
 ControlTest("EV-2", True,  "expert accuracy 0.81",    now -  12*DAY, 30),
 ControlTest("DR-1", False, "drift alerting not deployed", now,       30),
]

def verify(tests, required, at):
    by = {t.cid: t for t in tests}
    rows, evidenced = [], 0
    for cid in required:
        t = by.get(cid)
        if t is None:
            rows.append({"control": cid, "state": "NO EVIDENCE", "age": None})
            continue
        st = t.state(at)
        rows.append({"control": cid, "state": st, "age": round(t.age(at), 1)})
        evidenced += st == "PASS"
    return {"required": len(required), "evidenced": evidenced,
            "coverage": round(evidenced/len(required), 3), "rows": rows}

v = verify(TESTS, REQUIRED, now)
print(f"{'control':9s}{'state':14s}{'age (days)':>12}")
print("-" * 36)
for r in v["rows"]:
    print(f"{r['control']:9s}{r['state']:14s}{str(r['age']):>12}")
print(f"\\ncurrently evidenced {v['evidenced']}/{v['required']} = {v['coverage']:.0%}")
'''),
  ("md", "## 3 · Where it breaks — what a point-in-time report would have said"),
  ("py", '''point_in_time = sum(1 for t in TESTS if t.passed)
print(f"point-in-time  : {point_in_time}/{len(REQUIRED)} = "
      f"{point_in_time/len(REQUIRED):.0%}")
print(f"continuous     : {v['evidenced']}/{v['required']} = {v['coverage']:.0%}")
stale = [r["control"] for r in v["rows"] if r["state"] == "STALE"]
none  = [r["control"] for r in v["rows"] if r["state"] == "NO EVIDENCE"]
fail  = [r["control"] for r in v["rows"] if r["state"] == "FAIL"]
print(f"\\nthe gap: STALE {stale}  NO EVIDENCE {none}  FAIL {fail}")
print("Nobody did anything wrong to produce the STALE rows. Time passed.")
'''),
  ("md", "## 4 · The control — automate one test and watch the posture hold"),
  ("py", '''def automated_test(cid, run_now):
    """A control test that re-runs on a schedule writes its own evidence."""
    passed, evidence = run_now()
    return ControlTest(cid, passed, evidence, tested_at=time.time(),
                       valid_for_days=30)

def check_egress_policy():
    ALLOW = {"api.github.com"}
    attempts = ["https://api.github.com/x", "http://169.254.169.254/",
                "https://collect.example.com/x"]
    from urllib.parse import urlparse
    denied = [u for u in attempts if (urlparse(u).hostname or "") not in ALLOW]
    return len(denied) == 2, f"{len(denied)}/3 destinations denied, run automatically"

fresh = [t for t in TESTS if t.cid != "SB-1"] + [automated_test("SB-1", check_egress_policy)]
v2 = verify(fresh, REQUIRED, now)
print(f"after automating SB-1: {v2['evidenced']}/{v2['required']} = {v2['coverage']:.0%}")
print(f"   SB-1 is now {[r['state'] for r in v2['rows'] if r['control']=='SB-1'][0]}"
      f" and will stay fresh without anyone remembering")
assert v2["coverage"] > v["coverage"]

print("\\nprioritise automation by how often a control goes stale:")
for t in sorted(TESTS, key=lambda t: t.valid_for_days):
    per_year = round(365 / t.valid_for_days, 1)
    print(f"   {t.cid}  window {t.valid_for_days:>3.0f}d → "
          f"{per_year:>4} manual re-tests per year")
'''),
 ],
 "expect": "Four controls are PASS, SB-1 and SB-2 are STALE, DR-1 is FAIL and "
           "ST-1 has NO EVIDENCE — coverage 50%. A point-in-time report would "
           "have claimed 75%. Automating the SB-1 egress test returns it to PASS "
           "and raises coverage to 63%, and the re-test frequency table shows "
           "SB-2 needing roughly 13.5 manual re-tests a year.",
 "challenge": "Automate the control with the shortest freshness window first — it "
              "is the one costing the most manual effort and going stale most "
              "often. One automated test converts an annual assertion into a live "
              "control.",
},

"E1.8": {
 "concept": """
Third-party risk for AI has the ordinary supply-chain problem plus a question
nobody's assessment form asks:

> **Can this component change without telling us?**

For a library the answer is no — you pin a version. For a hosted model the
answer is usually yes, and it changes the risk rating, because every control you
tested was tested against behaviour the vendor can replace on a Tuesday.

Three artefact classes, with genuinely different maturity:

- **Libraries** — signing, version pinning, download signals. Mature.
- **Model weights or a hosted model** — attestation possible and rare; no
  popularity signal that means anything; version stability is a contractual
  question, not a technical one.
- **Prompt and tool packages (MCP, skills)** — no signing convention, and they
  run with your agent's authority.

Saying which signals are unavailable is part of the assessment, not a gap in it.
""",
 "steps": [
  ("md", "## 2 · Demo — the ordinary signals, and where they run out"),
  ("py", '''from dataclasses import dataclass

@dataclass(frozen=True)
class Component:
    name: str; kind: str; signed: bool = False
    pinned: bool = False; can_change_silently: bool = False
    runs_with_agent_authority: bool = False; downloads: int = 0

COMPONENTS = [
 Component("cryptography==42.0.5", "library", True, True, False, False, 900_000),
 Component("langchain==0.2.1", "library", False, True, False, False, 400_000),
 Component("hosted GLM-4.6 endpoint", "hosted model", False, False, True, False),
 Component("local glm-4.6 weights (pinned digest)", "weights", True, True, False, False),
 Component("mcp-jira-connector==0.0.3", "tool package", False, True, False, True, 180),
]
def assess(c):
    flags = []
    if not c.signed:                  flags.append("unsigned")
    if not c.pinned:                  flags.append("not version-pinned")
    if c.can_change_silently:         flags.append("CAN CHANGE WITHOUT NOTICE")
    if c.runs_with_agent_authority:   flags.append("runs with agent authority")
    if c.kind == "library" and c.downloads < 1000: flags.append("little scrutiny")
    tier = ("high" if c.can_change_silently or c.runs_with_agent_authority
            else "medium" if flags else "low")
    return tier, flags

print(f"{'component':40s}{'kind':14s}{'tier':8s}flags")
print("-" * 96)
for c in COMPONENTS:
    tier, flags = assess(c)
    print(f"{c.name:40s}{c.kind:14s}{tier:8s}{', '.join(flags) or '—'}")
'''),
  ("md", "## 3 · Where it breaks — the silent change, priced"),
  ("py", '''import time
now = time.time(); DAY = 86400

CONTROL_TESTS = {"SB-2": now - 20*DAY, "EV-2": now - 20*DAY, "DR-1": now - 20*DAY}
MODEL_CHANGED_AT = now - 5*DAY

print("your controls were tested against a model that changed 5 days ago:")
for cid, tested in CONTROL_TESTS.items():
    valid = tested > MODEL_CHANGED_AT
    print(f"   {cid}  tested {int((now-tested)/DAY)}d ago  "
          f"{'still valid' if valid else 'INVALIDATED by the model change'}")
invalidated = [c for c, t in CONTROL_TESTS.items() if t <= MODEL_CHANGED_AT]
print(f"\\n{len(invalidated)}/{len(CONTROL_TESTS)} control tests invalidated by a "
      f"change you did not make and were not told about.")
assert invalidated
'''),
  ("md", "## 4 · The control — the four questions, and stating the gaps"),
  ("py", '''QUESTIONS = [
 ("Can this component change without notifying us?",
  "if yes, every control test has an implicit expiry tied to the vendor"),
 ("Does it execute with our agent's authority?",
  "if yes, assess it as code, not as a dependency"),
 ("Can we pin a digest, and do we?",
  "the difference between a supply chain and a subscription"),
 ("What is our exit if we stop using it?",
  "DORA Art.11 asks this directly; most AI contracts have no answer"),
]
for q, why in QUESTIONS: print(f"Q: {q}\\n   → {why}\\n")

SIGNALS = {
 "library":      {"signature": True, "downloads": True, "pinning": True, "lineage": True},
 "hosted model": {"signature": False, "downloads": False, "pinning": False, "lineage": False},
 "weights":      {"signature": True, "downloads": False, "pinning": True, "lineage": False},
 "tool package": {"signature": False, "downloads": False, "pinning": True, "lineage": False},
}
print(f"{'artefact class':16s}{'signals available':>20}  unavailable")
print("-" * 74)
for kind, sig in SIGNALS.items():
    have = [k for k, v in sig.items() if v]
    lack = [k for k, v in sig.items() if not v]
    print(f"{kind:16s}{f'{len(have)}/{len(sig)}':>20}  {lack or '—'}")

def assessment_statement(kind):
    sig = SIGNALS[kind]
    lack = [k for k, v in sig.items() if not v]
    return (f"{kind}: assessed on {len(sig)-len(lack)}/{len(sig)} signals. "
            f"{', '.join(lack) or 'none'} unavailable for this artefact class.")
print()
for kind in SIGNALS: print("  " + assessment_statement(kind))
print("\\nThat last sentence is the deliverable. A rating that hides which signals")
print("were unavailable is a number someone will later rely on.")
'''),
 ],
 "expect": "The hosted model and the MCP tool package both tier high — one for "
           "silent change, one for running with agent authority. The silent model "
           "change invalidates all three control tests taken before it. The signal "
           "table shows libraries with 4 of 4 signals available and hosted models "
           "with 0 of 4, and each assessment statement names what was unavailable.",
 "challenge": "Add \"can this change without notifying us?\" to your third-party "
              "assessment form. For hosted models the answer is usually yes, and "
              "it should carry an explicit control-test expiry.",
},

"E1.9": {
 "concept": """
Lifecycle governance is about the events that have no ticket.

A model or agent has a lifecycle — requested, approved, deployed, changed,
retired. Classical governance covers the first, second and third. The events that
actually change your risk are the fourth and fifth, and they mostly happen
outside any process:

| Event | Ticketed? | Why it matters |
|---|---|---|
| new agent deployed | usually | caught by existing process |
| tool added to manifest | no | changes blast radius silently |
| prompt edited | no | changes behaviour, not code |
| provider upgrades the model | no | you may not be told |
| scope widened in IAM | sometimes | depends on your IAM review |
| **agent decommissioned** | rarely | **the identity outlives the agent** |

The last row is the one most first reviews find: a retired agent whose identity
still exists is a standing credential with no owner and nobody watching it,
because everyone believes it is gone.
""",
 "steps": [
  ("md", "## 2 · Demo — the lifecycle, and which events generate a record"),
  ("py", '''EVENTS = {
 "new agent deployed":         ("usually", "existing change process catches it"),
 "tool added to the manifest": ("no",      "changes blast radius; no PR raised"),
 "prompt edited in a console": ("no",      "changes behaviour, not code"),
 "provider upgrades the model":("no",      "you may not be told at all"),
 "scope widened in IAM":       ("sometimes","depends on your access review cadence"),
 "agent decommissioned":       ("rarely",  "the IDENTITY usually outlives the agent"),
}
print(f"{'lifecycle event':30s}{'ticketed?':12s}why it matters")
print("-" * 86)
for e, (t, why) in EVENTS.items():
    print(f"{e:30s}{t:12s}{why}")
untracked = [e for e, (t, _) in EVENTS.items() if t in ("no", "rarely")]
print(f"\\n{len(untracked)}/{len(EVENTS)} events generate no reliable record.")
'''),
  ("md", "## 3 · Where it breaks — the identity that outlived the agent"),
  ("py", '''import time
now = time.time(); DAY = 86400

IDENTITIES = {
 "triage-agent":   {"created": now - 200*DAY, "last_auth": now - 0.2*DAY,
                    "owner": "appsec", "service_running": True},
 "patch-agent":    {"created": now - 180*DAY, "last_auth": now - 1*DAY,
                    "owner": "platform", "service_running": True},
 "legacy-scanner": {"created": now - 900*DAY, "last_auth": now - 400*DAY,
                    "owner": "", "service_running": False},
 "poc-agent-2025": {"created": now - 500*DAY, "last_auth": now - 300*DAY,
                    "owner": "", "service_running": False},
 "sunset-agent":   {"created": now - 300*DAY, "last_auth": now - 2*DAY,
                    "owner": "", "service_running": False},
}
print(f"{'identity':18s}{'last auth (d)':>15}{'service running':>18}{'owner':>12}  finding")
print("-" * 92)
for name, i in IDENTITIES.items():
    age = (now - i["last_auth"])/DAY
    finding = ""
    if not i["service_running"] and age < 30:
        finding = "ACTIVE CREDENTIAL FOR A RETIRED SERVICE"
    elif not i["service_running"]:
        finding = "orphan — decommissioning never finished"
    elif not i["owner"]:
        finding = "no owner"
    print(f"{name:18s}{age:>15.0f}{str(i['service_running']):>18}"
          f"{i['owner'] or '—':>12}  {finding}")
print("\\nRead the sunset-agent row twice. The service was retired. The identity")
print("authenticated two days ago. Somebody or something is still using it.")
'''),
  ("md", "## 4 · The control — two automated checks that close the loop"),
  ("py", '''def lifecycle_checks(identities, now, stale_days=90):
    findings = []
    for name, i in identities.items():
        age = (now - i["last_auth"])/DAY
        if not i["service_running"] and age < stale_days:
            findings.append((name, "critical",
                             "identity active for a decommissioned service"))
        elif age > stale_days:
            findings.append((name, "medium",
                             f"no authentication in {age:.0f}d — decommission it"))
        elif not i["owner"]:
            findings.append((name, "medium", "no named owner"))
    return findings

for name, sev, why in lifecycle_checks(IDENTITIES, now):
    print(f"[{sev:8s}] {name:18s} {why}")

print("\\nand the manifest-diff check, for the events that change behaviour:")
SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n,s,rev in tools if n not in gated)
BEFORE = [("read_file","self",True)]
AFTER  = [("read_file","self",True), ("deploy","org",False)]
d = blast(AFTER) - blast(BEFORE)
print(f"   manifest changed: blast {blast(BEFORE)} → {blast(AFTER)} (+{d})")
print(f"   → requires re-tiering (E1.3) and a fresh SB-2 test (E1.7)")

crit = [f for f in lifecycle_checks(IDENTITIES, now) if f[1] == "critical"]
assert crit
print(f"\\n{len(crit)} critical lifecycle finding(s) — each is a standing credential")
print("for something everyone believes is switched off.")
'''),
 ],
 "expect": "Four of six lifecycle events generate no reliable record. The identity "
           "review flags `sunset-agent` as critical — an active credential for a "
           "decommissioned service — plus two orphans with no authentication in "
           "300+ days. The manifest diff shows the blast radius rising from 0 to "
           "40, requiring re-tiering and a fresh control test.",
 "challenge": "Query your identity provider for non-human identities whose "
              "service is retired but which authenticated in the last 30 days. "
              "Every hit is either an undocumented dependency or someone else's "
              "foothold, and you cannot tell which from the directory alone.",
},

"E1.0": {
 "concept": """
"Trustworthy AI" is used as a value, and values do not have owners. Every
serious framework — NIST AI RMF chief among them — converges on roughly seven
dimensions:

| Dimension | The question it answers |
|---|---|
| **Valid and reliable** | Does it do what it claims, repeatably? |
| **Safe** | Can it cause physical, financial or psychological harm? |
| **Secure and resilient** | Can it be attacked, and does it degrade gracefully? |
| **Accountable and transparent** | Can you say who is responsible, and show your working? |
| **Explainable and interpretable** | Can you say why it produced this output? |
| **Privacy-enhanced** | Whose data is in it, on what basis, for how long? |
| **Fair, with harmful bias managed** | Does it distribute error evenly across people? |

Learning the list is the easy half and takes an afternoon.

The hard half is that **each dimension needs a named owning function**, and in
most organisations two or three of them have either no owner or three. "Everyone
owns trustworthy AI" is operationally identical to nobody owning it, and it fails
in a predictable direction: the dimensions with obvious homes get controls, and
the ones that sit between functions get a policy sentence.

Below, the seven dimensions are assigned across five functions, and then the
assignment is checked — because an ownership map with gaps is more useful than
one without, provided you can see the gaps.
""",
 "steps": [
  ("md", "## 2 · The seven dimensions, and who could own each"),
  ("py", '''DIMENSIONS = {
 "valid_and_reliable":     "does it do what it claims, repeatably",
 "safe":                   "can it cause physical, financial or psychological harm",
 "secure_and_resilient":   "can it be attacked, does it degrade gracefully",
 "accountable_transparent":"who is responsible, and can you show your working",
 "explainable":            "why did it produce this output",
 "privacy_enhanced":       "whose data, on what basis, for how long",
 "fair_bias_managed":      "is error distributed evenly across people",
}
FUNCTIONS = ["legal", "compliance", "privacy", "cyber", "model_risk"]

print(f"{'dimension':26s}the question it answers")
for d in sorted(DIMENSIONS):
    print(f"{d:26s}{DIMENSIONS[d]}")
print(f"\\nfunctions available to own them: {FUNCTIONS}")
'''),

  ("md", "## 3 · Assign, then look for the gaps\\n\\n"
         "A typical assignment in a large organisation. Not a recommended one — "
         "an observed one."),
  ("py", '''OWNERS = {
 "valid_and_reliable":      ["model_risk"],
 "safe":                    [],                       # nobody
 "secure_and_resilient":    ["cyber"],
 "accountable_transparent": ["compliance", "legal", "model_risk"],   # three
 "explainable":             ["model_risk"],
 "privacy_enhanced":        ["privacy"],
 "fair_bias_managed":       [],                       # nobody
}
print(f"{'dimension':26s}{'owners':34s}status")
for d in sorted(DIMENSIONS):
    o = OWNERS[d]
    status = ("UNOWNED" if not o else
              "contested" if len(o) > 1 else "clear")
    print(f"{d:26s}{', '.join(o) or '-':34s}{status}")

unowned = sorted(d for d in DIMENSIONS if not OWNERS[d])
contested = sorted(d for d in DIMENSIONS if len(OWNERS[d]) > 1)
print(f"\\nunowned   : {unowned}")
print(f"contested : {contested}")
assert unowned and contested
'''),

  ("md", "## 4 · Where it breaks — the two failure modes look different and are not\\n\\n"
         "An unowned dimension produces no control. A contested one produces "
         "three partial controls and no complete one."),
  ("py", '''def controls_for(dimension, owners):
    """Each owner builds the part of the control they can see from their seat."""
    coverage = {"legal": 0.3, "compliance": 0.35, "privacy": 0.4,
                "cyber": 0.9, "model_risk": 0.8}
    if not owners:
        return 0.0, "no control exists"
    if len(owners) == 1:
        return coverage[owners[0]], f"{owners[0]} builds it end to end"
    best = max(coverage[o] for o in owners)
    return best, f"{len(owners)} partial controls, none complete, best is {best:.0%}"

print(f"{'dimension':26s}{'coverage':>10s}  what actually got built")
for d in sorted(DIMENSIONS):
    cov, why = controls_for(d, OWNERS[d])
    print(f"{d:26s}{cov:>9.0%}  {why}")
print()
weakest = sorted((controls_for(d, OWNERS[d])[0], d) for d in DIMENSIONS)[:3]
print("weakest three:", [d for _, d in weakest])
print()
print("The unowned dimensions are at zero, which at least is visible. The")
print("contested one is worse: three functions each report that it is covered,")
print("and each is telling the truth about their part.")
'''),

  ("md", "## 5 · The control — one accountable owner, others named as contributors"),
  ("py", '''FIXED = {
 "valid_and_reliable":      ("model_risk", ["cyber"]),
 "safe":                    ("business_owner", ["legal", "compliance"]),
 "secure_and_resilient":    ("cyber", ["model_risk"]),
 "accountable_transparent": ("compliance", ["legal", "model_risk"]),
 "explainable":             ("model_risk", ["compliance"]),
 "privacy_enhanced":        ("privacy", ["cyber", "legal"]),
 "fair_bias_managed":       ("model_risk", ["compliance", "legal"]),
}
print(f"{'dimension':26s}{'accountable':16s}contributors")
for d in sorted(FIXED):
    owner, contrib = FIXED[d]
    print(f"{d:26s}{owner:16s}{', '.join(contrib)}")

still_unowned = [d for d in DIMENSIONS if not FIXED[d][0]]
print(f"\\ndimensions with no accountable owner: {still_unowned or 'none'}")
print()
print("Note the seat that had to be invented: `business_owner`. Safety of a use")
print("case is not a control function's decision - it belongs to whoever chose")
print("to deploy it, and if that seat is empty the other five are governing an")
print("orphan.")
assert not still_unowned
'''),

  ("md", "## 6 · Verify — every dimension resolves to a person who can be asked"),
  ("py", '''def audit_question(dimension):
    owner, contrib = FIXED[dimension]
    return {"dimension": dimension,
            "who_do_i_ask": owner,
            "who_else_must_agree": contrib,
            "answerable": bool(owner)}

for d in sorted(DIMENSIONS):
    q = audit_question(d)
    print(f"   {d:26s}ask {q['who_do_i_ask']:16s}"
          f"agreed with {', '.join(q['who_else_must_agree']) or '-'}")
print()
print(f"answerable for all seven: {all(audit_question(d)['answerable'] for d in DIMENSIONS)}")
print()
print("That is the whole test. An auditor asks one question per dimension, and")
print("every question resolves to a person. E1.10 takes the same five functions")
print("and maps the controls each one actually operates.")
assert all(audit_question(d)["answerable"] for d in DIMENSIONS)
'''),
 ],
 "expect": "The seven trustworthy-AI dimensions print with the question each "
           "answers. A typical assignment leaves two unowned and one contested "
           "between three functions — and the contested one is shown to be worse "
           "than the unowned ones, because three functions each honestly report "
           "their part as covered. The fix names one accountable owner per "
           "dimension and has to invent the business-owner seat to do it.",
 "challenge": "Write your organisation's names against the seven dimensions. The "
              "interesting rows are the blanks and the ones where you wrote "
              "three names — and the second kind is the one that will surprise "
              "you in an audit.",
},

"E1.10": {
 "concept": """
Five functions hold the AI control estate between them, and **none of them holds
all of it.** The programme does not fail inside any one function. It fails at the
seams, where each side reasonably believed the other had it.

| Stakeholder | The question they are actually asking |
|---|---|
| **Legal** | Can we be held liable, and under what theory? |
| **Compliance** | Which obligations apply, and can we demonstrate we meet them? |
| **Data Privacy** | Whose data is in this, on what basis, and for how long? |
| **Cyber Security** | Can this be attacked, and can we contain it if it is? |
| **Model Risk** | Is this fit for its stated purpose, and will we know when it stops being so? |

Two seats are routinely forgotten. The **business or product owner** in the
first line, who defines intended purpose and risk appetite and funds
remediation — if that seat is empty, the other five are governing an orphan. And
**internal audit** in the third line, whose job is independent assurance that the
five are doing what they claim.

What makes this a lesson rather than an org chart is the four gaps below. Each
one is a real failure that happens because *both* sides made a reasonable
assumption about the other.
""",
 "steps": [
  ("md", "## 2 · Who operates which control"),
  ("py", '''STAKEHOLDERS = {
 "legal":      {"asks": "can we be held liable, and under what theory",
                "controls": ["contract clauses", "acceptable-use terms",
                             "IP screening", "e-discovery retention"]},
 "compliance": {"asks": "which obligations apply, can we demonstrate we meet them",
                "controls": ["AI policy", "use-case classification",
                             "attestations", "disclosure triggers"]},
 "privacy":    {"asks": "whose data, on what basis, for how long",
                "controls": ["impact assessment gate", "PII redaction",
                             "retention schedules", "transfer mechanisms"]},
 "cyber":      {"asks": "can this be attacked, can we contain it",
                "controls": ["agent identity and JIT authz", "tool permissions",
                             "sandbox and egress", "guardrails",
                             "telemetry and detections", "kill switch"]},
 "model_risk": {"asks": "is it fit for purpose, will we know when it stops being",
                "controls": ["pre-deployment validation", "performance thresholds",
                             "drift alerting", "revalidation on change"]},
}
ALSO = {"business_owner": "accountable for the use case; defines purpose and risk appetite",
        "internal_audit": "independent assurance that the five do what they claim"}

for name in sorted(STAKEHOLDERS):
    s = STAKEHOLDERS[name]
    print(f"{name:12s}{s['asks']}")
    print(f"            controls: {', '.join(s['controls'])}")
print()
for name, role in sorted(ALSO.items()):
    print(f"{name:16s}{role}")
total = sum(len(s["controls"]) for s in STAKEHOLDERS.values())
print(f"\\n{total} controls across {len(STAKEHOLDERS)} functions")
'''),

  ("md", "## 3 · The four seams, each with two reasonable assumptions"),
  ("py", '''SEAMS = [
 {"gap": "agent traces are full of personal data",
  "a": ("cyber", "privacy owns retention of anything containing personal data"),
  "b": ("privacy", "security owns the log store, so security sets its schedule"),
  "result": "no schedule was set; three years of prompts are discoverable"},
 {"gap": "the model was validated, the tools were not",
  "a": ("model_risk", "validation covered the model, which is our scope"),
  "b": ("cyber", "MRM signed it off, so the deployment was approved"),
  "result": "an agent holds production write access that was never in scope"},
 {"gap": "'no training on our data' was negotiated, never instrumented",
  "a": ("legal", "the clause is in the contract and it is binding"),
  "b": ("cyber", "legal handled the vendor, so the restriction is handled"),
  "result": "nobody built the control that verifies the vendor honours it"},
 {"gap": "the use case was risk-tiered before it had tools",
  "a": ("compliance", "classified low-risk: it was a chatbot when we saw it"),
  "b": ("business_owner", "we shipped features, not a new use case"),
  "result": "it files tickets, sends mail and moves money at the low-risk tier"},
]
for i, s in enumerate(SEAMS, 1):
    print(f"{i}. {s['gap']}")
    print(f"   {s['a'][0]:15s} assumed: {s['a'][1]}")
    print(f"   {s['b'][0]:15s} assumed: {s['b'][1]}")
    print(f"   -> {s['result']}")
    print()
print("Neither assumption in any pair is unreasonable. That is what makes these")
print("seams rather than mistakes - and why naming the handoff is the control.")
'''),

  ("md", "## 4 · Where it breaks — every function reports green"),
  ("py", '''def self_report(function):
    """Each function reports on the controls it operates. All true."""
    if function in STAKEHOLDERS:
        return {"function": function, "controls_operating": len(STAKEHOLDERS[function]["controls"]),
                "status": "green"}
    return {"function": function, "controls_operating": 0, "status": "n/a"}

for f in sorted(STAKEHOLDERS):
    r = self_report(f)
    print(f"   {r['function']:12s}{r['controls_operating']} controls  {r['status']}")
print()
print(f"functions reporting green : {len(STAKEHOLDERS)}/{len(STAKEHOLDERS)}")
print(f"open seams                : {len(SEAMS)}")
print()
print("A dashboard assembled from function self-reports is all green, and four")
print("material gaps are open. The dashboard is not lying - it is asking each")
print("function about the inside of its own box, and every failure here is")
print("between boxes.")
assert len(SEAMS) == 4
'''),

  ("md", "## 5 · The control — name the handoff, give it one owner"),
  ("py", '''HANDOFFS = {
 "trace retention schedule":      {"owner": "privacy",  "consumers": ["cyber", "legal"]},
 "tool scope in validation":      {"owner": "model_risk","consumers": ["cyber", "business_owner"]},
 "vendor no-train verification":  {"owner": "cyber",    "consumers": ["legal", "compliance"]},
 "re-tier on capability change":  {"owner": "compliance","consumers": ["business_owner", "cyber"]},
}
print(f"{'handoff artefact':32s}{'accountable':13s}consumers")
for h in sorted(HANDOFFS):
    v = HANDOFFS[h]
    print(f"{h:32s}{v['owner']:13s}{', '.join(v['consumers'])}")

covered = len(HANDOFFS)
print(f"\\nseams: {len(SEAMS)}   handoffs with a named owner: {covered}")
print()
print("One artefact, many consumers, exactly one owner. The consumers matter as")
print("much as the owner: a handoff nobody consumes was never a handoff, and a")
print("handoff with two owners is the contested case from E1.0 again.")
assert covered == len(SEAMS)
'''),

  ("md", "## 6 · Verify — the two forgotten seats"),
  ("py", '''def governed(use_case):
    missing = [seat for seat in ("business_owner", "internal_audit")
               if seat not in use_case["seats"]]
    five = [f for f in STAKEHOLDERS if f in use_case["seats"]]
    return {"control_functions_present": len(five),
            "missing_seats": missing,
            "is_governed": not missing and len(five) == len(STAKEHOLDERS)}

CASES = [
 {"name": "customer support agent", "seats": list(STAKEHOLDERS) + ["business_owner", "internal_audit"]},
 {"name": "internal code assistant", "seats": list(STAKEHOLDERS)},
]
for c in CASES:
    g = governed(c)
    print(f"   {c['name']:26s}five functions: {g['control_functions_present']}/5   "
          f"missing: {g['missing_seats'] or 'none'}   governed: {g['is_governed']}")
print()
print("The second one has every control function at the table and no accountable")
print("owner. Five functions are governing something nobody has agreed to own,")
print("which is how a use case survives a review and still has no one to fund")
print("the remediation it was told to do.")
assert not governed(CASES[1])["is_governed"]
'''),
 ],
 "expect": "Five stakeholder functions print with the question each is asking "
           "and the controls each operates — 22 controls in total. Four seam "
           "failures are shown as pairs of individually reasonable assumptions, "
           "and every function still self-reports green while all four gaps are "
           "open. Naming one accountable owner per handoff closes them, and a "
           "use case with all five control functions and no business owner is "
           "shown to be ungoverned.",
 "challenge": "Pick one of the four seams and find out, today, who owns it in "
              "your organisation. The answer 'I assume security does' from one "
              "side and 'I assume privacy does' from the other is the finding.",
},

"E1.11": {
 "concept": """
Model risk management is not new. The SR 11-7 lineage has governed models in
regulated institutions for over a decade, and its three pillars are sound:

1. **Conceptual soundness** — is the method appropriate for the purpose?
2. **Ongoing monitoring** — is it still performing as validated?
3. **Independent validation** — did someone other than the builder check?

All three still hold for AI systems. What breaks is not the framework but a
silent assumption underneath it: **that a model produces an output, and a human
decides what to do with it.**

Once the model can call a tool, that assumption is void. Validation scoped to
the model's *predictions* says nothing about the model's *actions*. You can hold
a perfectly valid validation report for a system that has since been granted
write access to a production database, and nothing in the classical process is
required to notice.

So the extension is narrow and specific: the unit of validation becomes the
**model plus its tool surface plus its autonomy level**, and any change to any of
the three triggers revalidation — not just a change to the weights.
""",
 "steps": [
  ("md", "## 2 · The three pillars, and what each assumes"),
  ("py", '''PILLARS = {
 "conceptual_soundness": ("is the method appropriate for the purpose",
                          "assumes the purpose is stable and stated"),
 "ongoing_monitoring":   ("is it still performing as validated",
                          "assumes performance is what changes"),
 "independent_validation":("did someone other than the builder check",
                          "assumes the thing checked is the thing deployed"),
}
print(f"{'pillar':24s}{'what it asks':46s}what it quietly assumes")
for p in sorted(PILLARS):
    asks, assumes = PILLARS[p]
    print(f"{p:24s}{asks:46s}{assumes}")
print()
print("All three survive contact with AI. The assumptions are what break.")
'''),

  ("md", "## 3 · The unit of validation, before and after tools"),
  ("py", '''VALIDATED = {
 "model": "glm-5.2", "version": "2026-03",
 "purpose": "summarise support tickets",
 "tools": [],                       # at validation time it had none
 "autonomy": "L1",                  # suggests; a human acts
}

def validation_covers(deployed, validated):
    diffs = []
    if deployed["model"] != validated["model"]:       diffs.append("model changed")
    if deployed["version"] != validated["version"]:   diffs.append("version changed")
    if deployed["purpose"] != validated["purpose"]:   diffs.append("purpose changed")
    if sorted(deployed["tools"]) != sorted(validated["tools"]):
        diffs.append(f"tool surface changed: {sorted(set(deployed['tools']) - set(validated['tools']))}")
    if deployed["autonomy"] != validated["autonomy"]: diffs.append(
        f"autonomy raised {validated['autonomy']} -> {deployed['autonomy']}")
    return (not diffs), diffs

DEPLOYED = dict(VALIDATED, tools=["read_ticket", "write_ticket", "db_update"],
                autonomy="L3")
ok, diffs = validation_covers(DEPLOYED, VALIDATED)
print(f"validation still covers what is deployed: {ok}")
for d in diffs:
    print(f"   {d}")
print()
print("Same weights. Same version. The validation report is accurate about a")
print("system that no longer exists, and nothing in the classical process is")
print("required to notice, because the classical trigger is a model change.")
assert not ok
'''),

  ("md", "## 4 · Where it breaks — monitoring the wrong thing well"),
  ("py", '''import random
def monitor(metric, runs=200, seed=4):
    rng = random.Random(seed)
    return [round(rng.gauss(0.92, 0.01), 3) for _ in range(runs)]

acc = monitor("summarisation_accuracy")
print(f"summarisation accuracy over 200 runs: mean {sum(acc)/len(acc):.3f}, "
      f"min {min(acc)}, max {max(acc)}")
print("threshold 0.85 -> breaches:", sum(a < 0.85 for a in acc))
print()
UNMONITORED = ["rows written to production", "tools invoked per run",
               "actions taken without human review", "scope of the credential used"]
print("what is NOT on the dashboard:")
for u in UNMONITORED:
    print(f"   {u}")
print()
print("The monitoring is excellent and it is monitoring the prediction. The")
print("risk moved to the action, and the action has no threshold, no baseline")
print("and no alert.")
assert sum(a < 0.85 for a in acc) == 0
'''),

  ("md", "## 5 · The control — revalidate on the triple, not on the weights"),
  ("py", '''TRIGGERS = {
 "model or version change": True,
 "prompt or config change": True,
 "tool added or scope widened": True,
 "autonomy level raised": True,
 "purpose changed": True,
 "calendar year elapsed": True,
}
CLASSICAL = {"model or version change", "calendar year elapsed"}

print(f"{'trigger':32s}{'classical MRM':16s}extended")
for t in TRIGGERS:
    print(f"{t:32s}{'yes' if t in CLASSICAL else 'no':16s}yes")
missed = [t for t in TRIGGERS if t not in CLASSICAL]
print(f"\\ntriggers classical MRM would miss: {len(missed)}")
for m in missed: print(f"   {m}")
print()
ok2, diffs2 = validation_covers(DEPLOYED, VALIDATED)
print(f"under the extended triggers, this deployment requires revalidation: {not ok2}")
print(f"reasons: {diffs2}")
assert len(missed) == 4
'''),

  ("md", "## 6 · Verify — what a validation record must now carry"),
  ("py", '''record = {
 "model": DEPLOYED["model"], "version": DEPLOYED["version"],
 "purpose": DEPLOYED["purpose"],
 "tool_surface": sorted(DEPLOYED["tools"]),
 "autonomy": DEPLOYED["autonomy"],
 "validated_unit": "model + tool surface + autonomy",
 "monitors": ["summarisation_accuracy", "rows_written", "tools_per_run",
              "actions_without_review"],
 "revalidation_triggers": sorted(TRIGGERS),
 "independent_of_builder": True,
}
for k in sorted(record):
    print(f"   {k:24s}{record[k]}")
print()
print("Three fields carry the whole extension: validated_unit, tool_surface and")
print("autonomy. Without them a validation report describes a text generator,")
print("and the thing in production is an actor.")
assert record["validated_unit"].startswith("model + tool")
'''),
 ],
 "expect": "The three SR 11-7 pillars print with the assumption each makes. A "
           "system validated with no tools at L1 is shown deployed with three "
           "tools at L3 — same model, same version — and the validation no "
           "longer covers it. Monitoring reports 200 clean runs of summarisation "
           "accuracy while four action-level metrics have no threshold at all, "
           "and four revalidation triggers classical MRM would miss are named.",
 "challenge": "Take one validated model in your estate and list the tools it "
              "holds today. If any of them post-dates the validation report, "
              "the report is describing a different system.",
},

"E1.12": {
 "concept": """
Everything in this chapter has pointed at the same conclusion: the functions
work, and the **handoffs** are where the programme leaks.

A seam is not a disagreement. Both sides are usually competent, usually right
about their own scope, and usually assuming the other side has the piece in the
middle. Nobody is wrong, and the gap is real.

The control is a **joint runbook** per seam, and it has exactly three
properties:

- **One artefact.** A named, versioned thing that exists — not a meeting, not an
  understanding.
- **One owner.** Accountable for the artefact existing and being current.
  Contributors are named; owners are singular.
- **Named consumers.** Who receives it, and what they are entitled to assume
  once they have. A handoff nobody consumes was never a handoff.

The three seams below are the ones that fail most often, and each is traced
here from producer to consumer to see exactly where it stops.
""",
 "steps": [
  ("md", "## 2 · Three seams, traced end to end"),
  ("py", '''RUNBOOKS = {
 "privacy assessment -> control design": {
   "artefact": "DPIA with a control annex",
   "owner": "privacy",
   "consumers": ["cyber", "model_risk"],
   "consumer_entitled_to_assume": "the data classes and retention limits are settled",
   "delivered_to": ["cyber"]},                       # model_risk never receives it
 "legal position -> system prompt": {
   "artefact": "approved language and refusal set",
   "owner": "legal",
   "consumers": ["cyber", "business_owner"],
   "consumer_entitled_to_assume": "these refusals are contractually required",
   "delivered_to": ["cyber", "business_owner"]},
 "MRM validation -> security evidence": {
   "artefact": "validation report with tool surface and autonomy",
   "owner": "model_risk",
   "consumers": ["cyber", "compliance", "internal_audit"],
   "consumer_entitled_to_assume": "the validated unit matches what is deployed",
   "delivered_to": ["compliance"]},                  # cyber and audit never receive it
}
for name in sorted(RUNBOOKS):
    r = RUNBOOKS[name]
    print(f"{name}")
    print(f"   artefact  : {r['artefact']}")
    print(f"   owner     : {r['owner']}")
    print(f"   consumers : {', '.join(r['consumers'])}")
    print()
'''),

  ("md", "## 3 · Where it breaks — the consumer who never received it"),
  ("py", '''gaps = []
for name in sorted(RUNBOOKS):
    r = RUNBOOKS[name]
    missing = sorted(set(r["consumers"]) - set(r["delivered_to"]))
    status = "complete" if not missing else f"NOT DELIVERED to {', '.join(missing)}"
    print(f"{name[:44]:46s}{status}")
    for m in missing:
        gaps.append((name, m, r["consumer_entitled_to_assume"]))
print()
print(f"undelivered handoffs: {len(gaps)}")
for name, who, assumption in gaps:
    print(f"   {who:14s} is assuming: {assumption}")
    print(f"   {'':14s} and has not received: {RUNBOOKS[name]['artefact']}")
assert gaps
'''),

  ("md", "## 4 · What each undelivered handoff actually costs"),
  ("py", '''CONSEQUENCE = {
 ("privacy assessment -> control design", "model_risk"):
   "validation runs on data the DPIA restricted; the restriction is invisible to it",
 ("MRM validation -> security evidence", "cyber"):
   "security cannot see the validated tool surface, so scope creep is undetectable",
 ("MRM validation -> security evidence", "internal_audit"):
   "third line cannot test the second line's assurance; it audits the artefact it has",
}
for name, who, _ in gaps:
    print(f"   {who:16s}{CONSEQUENCE.get((name, who), 'unknown')}")
print()
print("None of these is a control failing. Each is a control that was built,")
print("works, and is invisible to the function whose decision depends on it.")
'''),

  ("md", "## 5 · The control — deliver, and record the delivery"),
  ("py", '''def close(runbooks):
    out = {}
    for name, r in runbooks.items():
        out[name] = dict(r, delivered_to=sorted(r["consumers"]))
    return out

CLOSED = close(RUNBOOKS)
remaining = [(n, c) for n, r in sorted(CLOSED.items())
             for c in r["consumers"] if c not in r["delivered_to"]]
print(f"{'seam':46s}{'owner':13s}delivered to")
for n in sorted(CLOSED):
    r = CLOSED[n]
    print(f"{n[:44]:46s}{r['owner']:13s}{', '.join(r['delivered_to'])}")
print(f"\\nundelivered handoffs remaining: {len(remaining)}")
print()
print("One owner per artefact, every consumer named, and delivery recorded")
print("rather than assumed. The delivery record is the part people skip, and it")
print("is the only part that makes the seam auditable a year later.")
assert not remaining
'''),

  ("md", "## 6 · Verify — one artefact, many consumers, one owner"),
  ("py", '''def check(runbooks):
    problems = []
    for name, r in sorted(runbooks.items()):
        if not r["artefact"]:                     problems.append(f"{name}: no artefact")
        if not r["owner"]:                        problems.append(f"{name}: no owner")
        if isinstance(r["owner"], list):          problems.append(f"{name}: {len(r['owner'])} owners")
        if not r["consumers"]:                    problems.append(f"{name}: no consumers")
        undel = set(r["consumers"]) - set(r["delivered_to"])
        if undel:                                 problems.append(f"{name}: undelivered to {sorted(undel)}")
    return problems

print("before:", len(check(RUNBOOKS)), "problem(s)")
for p in check(RUNBOOKS): print("   ", p)
print("after :", len(check(CLOSED)), "problem(s)")
print()
print("Four properties, checked mechanically: an artefact exists, one owner is")
print("accountable, consumers are named, delivery is recorded. A governance")
print("programme that can run this check on its own seams is doing something")
print("more useful than another policy document.")
assert check(RUNBOOKS) and not check(CLOSED)
'''),
 ],
 "expect": "Three joint runbooks are traced from owner to consumer, and three "
           "handoffs turn out never to have been delivered — model risk never "
           "receives the privacy assessment, and neither security nor internal "
           "audit receives the validation report. Each undelivered handoff is a "
           "control that was built, works, and is invisible to the function "
           "whose decision depends on it. A four-property check runs over the "
           "seams and goes from several problems to zero.",
 "challenge": "Pick the artefact your function produces for someone else and ask "
              "the recipient when they last received it. The gap between 'we "
              "produce that' and 'we receive that' is the seam, and it is "
              "usually measured in quarters.",
},
}
