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
}
