"""E3 — The BISO, Risk Communicator & CISO Office. Eight sessions.

The last track. Everything built in A through E1/E2 becomes a decision someone
senior has to make, and the job is to make it makeable.

    E3.1  translating agentic risk upward
    E3.2  governing autonomy rather than approving tools
    E3.3  sequencing the programme
    E3.4  org design and ownership
    E3.5  the metrics that matter at this level
    E3.6  saying no, and saying yes with conditions
    E3.7  building the capability
    E3.8  resilience over perfection
"""

from . import diagrams as D

EXERCISES: dict[str, dict] = {

"E3.1": {
 "concept": """
Translating agentic risk upward means dropping every mechanism and keeping three
things: **exposure, likelihood, and the decision being requested.**

The failure mode is not using too much jargon. It is presenting *findings* when
the audience needs a *decision*. A board cannot act on "we found prompt
injection in the review agent". It can act on "a critical system can take N
units of unreviewed action, we demonstrated it, and we are asking for X or for
written acceptance".

That last clause matters more than people expect. **Accepting the risk in
writing, with a named owner and a review date, is a legitimate outcome.** Offering
it makes the ask credible, because it shows you are presenting a decision rather
than lobbying for a budget.
""",
 "steps": [
  ("md", "## 2 · Demo — compute the three numbers from what the tracks produced"),
  ("py", '''SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}

FLEET = {
 "pr-remediation-agent": [("read_file","self",True),
                          ("write_file","project",True),
                          ("deploy","org",False)],
 "claims-triage-agent":  [("read_file","self",True),
                          ("issue_refund","tenant",False)],
 "doc-summariser":       [("read_file","self",True)],
}
GATED = {"pr-remediation-agent": set(), "claims-triage-agent": {"issue_refund"},
         "doc-summariser": set()}

def blast(tools, gated):
    return sum(SCOPE_WEIGHT[s] * (1 if rev else 2)
               for n, s, rev in tools if n not in gated)

exposure = {a: blast(t, GATED[a]) for a, t in FLEET.items()}
print(f"{'agent':24s}{'blast radius':>14}")
print("-" * 40)
for a, b in sorted(exposure.items(), key=lambda kv: -kv[1]):
    print(f"{a:24s}{b:>14}")
total_exposure = sum(exposure.values())
print(f"{'FLEET TOTAL':24s}{total_exposure:>14}")

# likelihood — measured, from C1.2
ATTACKS = [("metadata service", False), ("path traversal", False),
           ("unlisted egress", True), ("denied tool", False)]
asr = sum(1 for _, through in ATTACKS if through) / len(ATTACKS)
print(f"\\nred-team attack success rate (containment surface): {asr:.0%}")

# assurance — from E1.7
REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]
EVIDENCED = ["AC-1","AC-2","EV-1","EV-2"]
coverage = len(EVIDENCED) / len(REQUIRED)
print(f"controls currently evidenced: {len(EVIDENCED)}/{len(REQUIRED)} = {coverage:.0%}")
'''),
  ("md", "## 3 · Where it breaks — the findings-shaped update"),
  ("py", '''FINDINGS_UPDATE = """
This quarter the team identified prompt injection in the code review agent,
insufficient scope narrowing in the delegation chain, and gaps in our egress
allowlist. We ran garak and promptfoo against three agents and found a 25%
attack success rate on the containment surface. We recommend prioritising
provenance controls and completing the SPIFFE rollout.
"""
print(FINDINGS_UPDATE)
print("Problems with this, from the audience's side:")
for p in ["no exposure figure — how much can actually happen?",
          "'25% attack success rate' against what, and is that good or bad?",
          "four tool names nobody in the room can evaluate",
          "'recommend prioritising' is not a decision anyone can take",
          "no option to decline, so it reads as lobbying rather than a choice"]:
    print(f"   · {p}")
'''),
  ("md", "## 4 · The control — exposure, likelihood, assurance, decision"),
  ("py", '''def board_translation(tier, exposure, asr, coverage, ask, cost, owner):
    likelihood = ("demonstrated" if asr > 0.2 else
                  "reduced but not eliminated" if asr > 0 else "not demonstrated")
    return f"""
EXPOSURE     A {tier}-tier system can take {exposure} units of unreviewed action.
             (One unit ≈ one irreversible change inside one project.)

LIKELIHOOD   We attacked it. {asr:.0%} of our attack suite succeeded — {likelihood}.
             This is a measurement, not an assessment.

ASSURANCE    {coverage:.0%} of the controls we say we operate are currently
             evidenced. The remainder are untested or their evidence has expired.

DECISION     {ask}
             Cost: {cost}.
             The alternative is to accept the unevidenced portion in writing,
             owned by {owner}, with a review date. Both are acceptable outcomes;
             we need one of them recorded."""

print(board_translation(
    tier="critical", exposure=total_exposure, asr=asr, coverage=coverage,
    ask="Fund continuous control verification for the agent fleet.",
    cost="0.5 FTE for two quarters, no new licences",
    owner="the Chief Operating Officer"))
'''),
  ("py", '''# Verify: the translation must contain no mechanism and must offer a choice.
JARGON = ["prompt injection", "spiffe", "garak", "promptfoo", "cwe",
          "provenance", "allowlist", "delegation chain", "token exchange"]
text = board_translation("critical", total_exposure, asr, coverage,
                         "Fund continuous control verification.", "0.5 FTE", "the COO")
found = [j for j in JARGON if j in text.lower()]
print(f"mechanism terms present: {found or 'none'}")
has_choice = "alternative" in text.lower() and "accept" in text.lower()
has_number = str(total_exposure) in text and f"{asr:.0%}" in text
print(f"offers a genuine alternative : {has_choice}")
print(f"carries measured numbers     : {has_number}")
assert not found and has_choice and has_number
print("\\nFour facts, no mechanism, and a decision that can go either way.")
'''),
 ],
 "expect": "The fleet's exposure totals 46 units, containment ASR is 25%, and "
           "control coverage is 50%. The findings-shaped update is shown with five "
           "specific problems. The board translation states exposure, likelihood, "
           "assurance and a decision, contains no mechanism jargon, carries the "
           "measured numbers, and explicitly offers written acceptance as an "
           "alternative.",
 "challenge": "Write these four lines for your highest-tier system. If you cannot "
              "fill the likelihood line with a measurement, that is the first "
              "thing to fund — an assessment is not a number.",
},

"E3.2": {
 "concept": """
Tool-approval processes do not scale for agents. The list of tools grows weekly,
each request needs context the approver does not have, and the queue becomes a
rubber stamp within a quarter.

**Govern autonomy instead.** The autonomy ladder from A1.1 is the right unit
because it is stable — there will always be four rungs — and because it maps
directly onto what can go wrong:

| Rung | Governance |
|---|---|
| **L1** | Self-service. Register it. No further review. |
| **L2** | Register + named owner. Approval gate on every writer, enforced by policy. |
| **L2.5** | Risk tier + blast-radius budget + drift monitoring + tested stop. |
| **L3** | All of L2.5, plus held-out evaluation per release and board sign-off. |

Two properties make this work: a request can be evaluated in minutes by checking
the manifest against the rung, and the policy does not need rewriting when a new
tool appears.

The rung that decides your programme's fate is **L1**. If L1 requires approval,
nobody registers anything and your inventory dies.
""",
 "steps": [
  ("md", "## 2 · Demo — the per-rung policy, and a request evaluated against it"),
  ("py", '''SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}
LADDER = {
 "L1":  "Assist — model proposes, a human performs every action.",
 "L2":  "Act with approval — model calls tools, a human approves each call.",
 "L2.5":"Act within a blast radius — pre-approved tools, bounded scope, review after.",
 "L3":  "Autonomous — model acts and self-verifies; humans see aggregates.",
}
POLICY = {
 "L1":   ("self-service", "register it; no further review", 0),
 "L2":   ("lightweight",  "named owner + approval gate on every writer", 0),
 "L2.5": ("governed",     "risk tier + blast budget + drift monitoring + tested stop", 20),
 "L3":   ("board",        "all of L2.5 + held-out eval per release + board sign-off", 60),
}
for rung, desc in LADDER.items():
    kind, req, budget = POLICY[rung]
    print(f"{rung:5s}{kind:14s}budget {budget:>3}  {req}")
    print(f"{'':19s}{desc}")
'''),
  ("py", '''def blast(tools, gated):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n,s,rev in tools if n not in gated)

def evaluate_request(name, tools, gated, claimed_rung):
    b = blast(tools, gated)
    kind, req, budget = POLICY[claimed_rung]
    problems = []
    writers = [n for n,s,rev in tools if s != "self" or not rev]
    ungated = [n for n in writers if n not in gated]
    if claimed_rung == "L1" and writers:
        problems.append(f"claims L1 but holds state-changing tools: {writers}")
    if claimed_rung == "L2" and ungated:
        problems.append(f"claims L2 (approve every call) but ungated: {ungated}")
    if b > budget:
        problems.append(f"blast radius {b} exceeds the {claimed_rung} budget of {budget}")
    return {"agent": name, "rung": claimed_rung, "blast": b,
            "decision": "APPROVE" if not problems else "REFUSE or RE-TIER",
            "problems": problems, "governance": req}

REQUESTS = [
 ("doc-summariser", [("read_file","self",True)], set(), "L1"),
 ("triage-bot", [("read_file","self",True), ("post_comment","project",True),
                 ("close_ticket","project",True)], set(), "L2"),
 ("refund-agent", [("read_file","self",True),
                   ("issue_refund","tenant",False)], set(), "L2.5"),
 ("refund-agent (gated)", [("read_file","self",True),
                           ("issue_refund","tenant",False)], {"issue_refund"}, "L2.5"),
]
for name, tools, gated, rung in REQUESTS:
    r = evaluate_request(name, tools, gated, rung)
    print(f"{r['agent']:24s}{r['rung']:6s}blast {r['blast']:>3}  {r['decision']}")
    for p in r["problems"]: print(f"{'':30s}⚠ {p}")
'''),
  ("md", "## 3 · Where it breaks — govern tools instead, and watch it collapse"),
  ("py", '''import math
def tool_approval_load(n_agents, tools_per_agent, new_tools_per_month,
                       minutes_per_review=25):
    initial = n_agents * tools_per_agent
    monthly = n_agents * new_tools_per_month
    return {"initial_reviews": initial,
            "initial_hours": round(initial * minutes_per_review / 60, 1),
            "monthly_reviews": monthly,
            "monthly_hours": round(monthly * minutes_per_review / 60, 1)}

print(f"{'agents':>8}{'initial reviews':>18}{'hours':>8}{'monthly reviews':>18}{'hours':>8}")
print("-" * 62)
for n in (5, 25, 120):
    r = tool_approval_load(n, tools_per_agent=8, new_tools_per_month=2)
    print(f"{n:>8}{r['initial_reviews']:>18}{r['initial_hours']:>8}"
          f"{r['monthly_reviews']:>18}{r['monthly_hours']:>8}")

def rung_load(n_agents, re_tier_per_month=0.1, minutes=25):
    monthly = n_agents * re_tier_per_month
    return round(monthly * minutes / 60, 1)
print(f"\\nsame estates, governing by rung (re-tier only on a manifest change):")
for n in (5, 25, 120):
    print(f"   {n:>4} agents → {rung_load(n)} hours/month")
print("\\nTool approval scales with agents × tools. Rung governance scales with")
print("agents × rate of significant change, which is two orders of magnitude less.")
'''),
  ("md", "## 4 · The control — L1 must be free, or the inventory dies"),
  ("py", '''def registration_rate(l1_requires_approval, friction_hours):
    """People register when it is cheaper than not registering."""
    base = 0.95
    penalty = min(friction_hours * 0.35, 0.9)
    return round(base - (penalty if l1_requires_approval else 0.0), 2)

print(f"{'L1 policy':34s}{'friction (h)':>14}{'registration rate':>20}")
print("-" * 70)
for label, approval, hours in (("self-service (register only)", False, 0.1),
                               ("approval required, fast", True, 1.0),
                               ("approval required, committee", True, 40.0)):
    rate = registration_rate(approval, hours)
    print(f"{label:34s}{hours:>14}{rate:>20.0%}")

def inventory_completeness(rate, n_true_assets=120):
    known = int(n_true_assets * rate)
    return {"true_assets": n_true_assets, "registered": known,
            "shadow": n_true_assets - known}

for label, approval, hours in (("self-service", False, 0.1),
                               ("committee", True, 40.0)):
    inv = inventory_completeness(registration_rate(approval, hours))
    print(f"\\n{label}: {inv['registered']}/{inv['true_assets']} registered, "
          f"{inv['shadow']} shadow assets")
print("\\nEvery control in E1 depends on the inventory. Charging for L1")
print("registration destroys the input to the entire governance programme.")
assert inventory_completeness(registration_rate(True, 40.0))["shadow"] > \\
       inventory_completeness(registration_rate(False, 0.1))["shadow"]
'''),
 ],
 "expect": "The four rungs print with their governance and budgets. The "
           "doc-summariser is approved at L1; `triage-bot` is refused at L2 for "
           "ungated writers; the refund agent is refused at L2.5 for exceeding "
           "the budget and approved once gated. Tool approval scales to 240 "
           "reviews a month at 120 agents against 5 hours for rung governance, "
           "and a committee-gated L1 leaves roughly 108 shadow assets.",
 "challenge": "Write your own per-rung policy in four lines and check what L1 "
              "costs a team today. If registering a read-only copilot needs an "
              "approval, your inventory is already incomplete and you cannot see "
              "by how much.",
},

"E3.3": {
 "concept": """
Sequencing decides whether the programme compounds or thrashes, and there is a
right order that is not the exciting one:

1. **Inventory** — you cannot govern what you cannot list.
2. **Identity** — agents distinct from humans, separately revocable.
3. **Containment** — egress, paths, tools; deny by default.
4. **Evidence** — log the acting identity; retain enough to replay.
5. **Evaluation** — accuracy against a held-out key, per release.
6. **Continuous** — drift alerts and freshness windows on every control.

The popular order inverts it, because evaluation and dashboards demo well and
identity does not. Doing 5 before 2 produces a well-measured system nobody can
switch off — and that is not a hypothetical, it is the modal state of AI
security programmes.

Each step also unlocks the next: you cannot log the acting identity (4) before
agents have identities (2), and you cannot alert on drift (6) without a baseline
from evidence (4).
""",
 "steps": [
  ("md", "## 2 · Demo — the dependency graph, and what each step unlocks"),
  ("py", '''STEPS = {
 1: ("inventory",   [],     ["you can now tier and assign owners"]),
 2: ("identity",    [1],    ["per-agent revocation", "attribution in logs"]),
 3: ("containment", [1],    ["bounded blast radius", "a red team has something to test"]),
 4: ("evidence",    [2],    ["act chains", "replayable runs", "a drift baseline"]),
 5: ("evaluation",  [4],    ["accuracy you can defend", "regression cases"]),
 6: ("continuous",  [4,5],  ["freshness windows", "drift alerts", "live posture"]),
}
print(f"{'step':>5}  {'name':14s}{'needs':10s}unlocks")
print("-" * 84)
for n, (name, needs, unlocks) in STEPS.items():
    print(f"{n:>5}  {name:14s}{str(needs):10s}{'; '.join(unlocks)}")

def can_do(step, done):
    return all(d in done for d in STEPS[step][1])

print("\\nwhat is doable from a standing start:")
print("   ", [n for n in STEPS if can_do(n, set())])
'''),
  ("md", "## 3 · Where it breaks — evaluation first"),
  ("py", '''def simulate(order):
    done, blocked, timeline = set(), [], []
    for step in order:
        if can_do(step, done):
            done.add(step); timeline.append((step, STEPS[step][0], "done"))
        else:
            missing = [STEPS[d][0] for d in STEPS[step][1] if d not in done]
            blocked.append((step, STEPS[step][0], missing))
            timeline.append((step, STEPS[step][0], f"BLOCKED on {missing}"))
    return done, blocked, timeline

POPULAR = [5, 6, 1, 3, 2, 4]     # evaluation and dashboards first
CORRECT = [1, 2, 3, 4, 5, 6]

for label, order in (("popular order", POPULAR), ("correct order", CORRECT)):
    done, blocked, timeline = simulate(order)
    print(f"=== {label} ===")
    for step, name, state in timeline:
        print(f"   {step}. {name:14s}{state}")
    print(f"   completed {len(done)}/6, blocked {len(blocked)}\\n")

done_pop, blocked_pop, _ = simulate(POPULAR)
print(f"popular order completes {len(done_pop)}/6 on the first pass;")
print(f"{len(blocked_pop)} step(s) have to be redone after their prerequisites land.")
assert len(blocked_pop) > 0
'''),
  ("md", "## 4 · The control — measure the programme by capability, not activity"),
  ("py", '''CAPABILITY = {
 1: "can list every AI asset with an owner",
 2: "can revoke one agent without stopping the others",
 3: "can bound what a compromised agent reaches",
 4: "can say who caused a specific action, and replay it",
 5: "can defend an accuracy number to a supervisor",
 6: "can say what is TRUE TODAY, not what passed once",
}
def programme_state(done):
    return [(n, CAPABILITY[n], n in done) for n in STEPS]

for label, order in (("eval-first, one quarter in", POPULAR[:2]),
                     ("correct order, one quarter in", CORRECT[:3])):
    done, _, _ = simulate(order)
    print(f"=== {label} — {len(done)} capabilit(y/ies) ===")
    for n, cap, have in programme_state(done):
        print(f"   {'YES' if have else 'no ':4s} {cap}")
    print()

done_a, _, _ = simulate(POPULAR[:2])
done_b, _, _ = simulate(CORRECT[:3])
print(f"after equal effort: eval-first has {len(done_a)} capabilities, "
      f"correct order has {len(done_b)}")
print("\\nThe eval-first programme can produce a dashboard. It cannot switch")
print("anything off, and it cannot say who did what.")
assert len(done_b) > len(done_a)
'''),
 ],
 "expect": "Only inventory is doable from a standing start. The popular "
           "evaluation-first order completes 4 of 6 on the first pass with 2 "
           "steps blocked on missing prerequisites; the correct order completes "
           "all six. After equal effort the eval-first programme holds 1 "
           "capability against the correct order's 3, and can produce a dashboard "
           "while being unable to revoke an agent or attribute an action.",
 "challenge": "Locate your programme on the six steps honestly. Most are between "
              "2 and 3 while reporting on 5, which is exactly the gap this "
              "sequence prevents — and the fix is to stop reporting 5 until 2 and "
              "3 are done.",
},

"E3.4": {
 "concept": """
The failures happen in the seams, so org design is the question of **which seams
you have chosen to have.**

Every seam below is a real handover where an agentic incident stalls, and each
one has a question that must have a name against it before the incident, not
during:

| Seam | The question |
|---|---|
| AppSec ↔ Platform | who owns the agent's sandbox? |
| Identity ↔ SecOps | who revokes a non-human identity at 03:00? |
| GRC ↔ Engineering | who decides an autonomy rung — the tier or the roadmap? |
| SOC ↔ Data | who retains agent traces, and for how long? |
| CISO office ↔ Legal | who starts the regulatory clock? |

An unanswered seam becomes an incident finding phrased as "unclear ownership",
which is a decision nobody made rather than a surprise.

The second half of this lesson is the four roles this curriculum implies, and
which one to hire first — which is not the one most teams hire first.
""",
 "steps": [
  ("md", "## 2 · Demo — the seams, and testing whether they are answered"),
  ("py", '''SEAMS = [
 ("AppSec", "Platform",     "who owns the agent's sandbox?",              "A3.1"),
 ("Identity", "SecOps",     "who revokes a non-human identity at 03:00?", "A3.6"),
 ("GRC", "Engineering",     "who decides an autonomy rung?",              "E3.2"),
 ("SOC", "Data",            "who retains agent traces, and for how long?","D1.5"),
 ("CISO office", "Legal",   "who starts the regulatory clock?",           "E2.6"),
 ("AppSec", "SOC",          "who owns detections FOR agents?",            "D1.4"),
]
ANSWERS = {
 "who owns the agent's sandbox?": "platform-security",
 "who revokes a non-human identity at 03:00?": "on-call SRE, pre-authorised",
 "who decides an autonomy rung?": "",                    # unanswered
 "who retains agent traces, and for how long?": "",      # unanswered
 "who starts the regulatory clock?": "legal, on IR notification",
 "who owns detections FOR agents?": "detection engineering",
}
print(f"{'seam':28s}{'owner':32s}lesson")
print("-" * 78)
unanswered = []
for a, b, q, lesson in SEAMS:
    owner = ANSWERS.get(q, "")
    if not owner: unanswered.append(q)
    print(f"{a + ' ↔ ' + b:28s}{owner or '⚠ NOBODY':32s}{lesson}")
print(f"\\n{len(unanswered)}/{len(SEAMS)} seams have no named owner:")
for q in unanswered: print(f"   {q}")
assert unanswered
'''),
  ("md", "## 3 · Where it breaks — an incident crossing an unanswered seam"),
  ("py", '''INCIDENT = [
 ("detection fires",                     "SOC",              True,  0.2),
 ("agent identified as the actor",       "SOC",              True,  1.0),
 ("decision to revoke the identity",     "Identity ↔ SecOps",True,  0.3),
 ("decide trace retention for evidence", "SOC ↔ Data",       False, 14.0),
 ("re-tier the agent post-incident",     "GRC ↔ Engineering",False, 21.0),
]
print(f"{'step':38s}{'seam':20s}{'owned':>7}{'hours':>8}")
print("-" * 76)
total = 0
for step, seam, owned, hours in INCIDENT:
    total += hours
    flag = "" if owned else "   ← stalls"
    print(f"{step:38s}{seam:20s}{str(owned):>7}{hours:>8}{flag}")
print(f"\\ntotal elapsed: {total:.1f} hours")
owned_only = sum(h for _, _, o, h in INCIDENT if o)
print(f"if every seam were owned: {owned_only:.1f} hours "
      f"({total/owned_only:.0f}× faster)")
print("\\nThe two unowned steps account for "
      f"{(total-owned_only)/total:.0%} of the elapsed time, and both are")
print("decisions rather than work.")
assert total > owned_only * 5
'''),
  ("md", "## 4 · The control — four roles, and which to hire first"),
  ("html", D.table(
    ["role", "track", "owns", "delivers", "how many others it unblocks"],
    [["identity engineer", "A2", "agent identity and delegation",
      "revocation · attribution · act chains", "<b>3</b>"],
     ["detection engineer", "D1", "agent telemetry and drift",
      "drift alerts · agent detections", "2"],
     ["GRC practitioner", "E1", "tiering, evidence, continuous verification",
      "inventory · control coverage", "2"],
     ["harness engineer", "B2", "the loop, the verifier, the eval",
      "evaluation · stop conditions", "1"]],
    emphasise=4,
    caption="The harness engineer is the one most teams hire first. The identity "
            "engineer is the one who unblocks the most others — revocation, "
            "attribution and act chains are prerequisites for evidence, "
            "evaluation and continuous verification alike, so hiring them second "
            "costs a quarter.")),
 ],
 "expect": "Two of six seams have no named owner — autonomy rung decisions and "
           "trace retention. The simulated incident takes 36.5 hours, of which 35 "
           "are the two unowned decision steps, roughly 24× slower than if every "
           "seam were owned. The role analysis shows the identity engineer "
           "unblocks the most downstream capability while the harness engineer is "
           "hired first most often.",
 "challenge": "Put a name against each of the six seams this week. Any seam where "
              "two people both say \"them\" is the one that will stall your next "
              "incident, and finding it now costs one meeting.",
},

"E3.5": {
 "concept": """
The metrics that matter at this level are few, and none of them is a count of
alerts, findings or trainings completed.

Five numbers, each with a property that makes it worth reporting monthly:

- **Exposure** — fleet blast radius. Moves when someone adds a tool.
- **Likelihood** — red-team attack success rate. Measured, not assessed.
- **Assurance** — controls *currently* evidenced. Degrades on its own.
- **Coverage** — agents in the inventory, honestly stated as a fraction of an
  estimate.
- **Speed** — measured time-to-stop, from a game day.

The shared property is the important one: **each degrades if nobody does
anything.** A metric that stays flat under neglect is measuring activity, not
posture — which is why finding counts and training completion make such
comfortable and useless board slides.
""",
 "steps": [
  ("md", "## 2 · Demo — compute all five from what the tracks produced"),
  ("py", '''import time
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
'''),
  ("md", "## 3 · Where it breaks — metrics that cannot degrade"),
  ("py", '''COMFORTABLE = {
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

print(f"\\n{'metric':28s}{'degrades if ignored?':>22}")
print("-" * 52)
for m in ("exposure","likelihood","assurance","coverage","speed",
          "findings closed","training completion","number of policies"):
    print(f"{m:28s}{str(degrades_under_neglect(m)):>22}")
print("\\nThe first five fall on their own. That is what makes them worth")
print("reporting monthly — the report itself creates the pressure.")
'''),
  ("md", "## 4 · The control — project the five forward under neglect"),
  ("py", '''def project(months, exposure, asr, assurance, coverage, ttl_days=41):
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
print(f"\\nAfter a year of no investment: exposure {exposure}→{p12['exposure']}, "
      f"assurance {assurance:.0%}→{p12['assurance']:.0%}.")
print("Nobody made a bad decision. This is the default trajectory, and the")
print("monthly report is what makes it visible before it is a board topic.")
assert p12["assurance"] < assurance and p12["exposure"] > exposure
'''),
 ],
 "expect": "The five metrics compute to exposure 46, ASR 25%, assurance 50%, "
           "coverage 34% and a 12-second time-to-stop. Four comfortable metrics "
           "are shown not to degrade under neglect while all five real ones do. "
           "Projected twelve months forward with no investment, exposure rises "
           "from 46 to 334 and assurance falls from 50% to 0%.",
 "challenge": "Which of the five can you produce today without a project? Start "
              "reporting that one monthly and let the missing ones become "
              "conspicuous — that is a cheaper way to get the others funded than "
              "asking for all five at once.",
},

"E3.6": {
 "concept": """
Saying no is cheap and usually wrong. The team routes around you, the capability
ships anyway, and you have traded influence for a moment of comfort.

**Saying yes with conditions** is the job. It works when the conditions are:

- **testable** — someone can check them without your involvement,
- **proportionate** — tied to what the request can actually do,
- **few** — five conditions get met, fifteen get negotiated away,
- **owned** — each with a name and a date.

The mechanics come from the rest of the curriculum: the rung decides the
governance (E3.2), the blast radius sizes the conditions (A1.4), and each
condition maps to a control that already produces evidence (E1.4).

This lesson takes one genuinely uncomfortable request and gets to yes.
""",
 "steps": [
  ("md", "## 2 · Demo — the request, assessed honestly"),
  ("py", '''SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n,s,rev in tools if n not in gated)

REQUEST = {
 "name": "customer-refund-agent",
 "asks_for": "issue refunds up to GBP 500 without human approval",
 "tools": [("read_order","self",True), ("read_customer","self",True),
           ("issue_refund","tenant",False)],
 "rung": "L2.5",
 "data": ("customer","regulated"),
 "business_case": "42% of refund tickets are mechanical; 3.5 FTE of manual work",
}
b = blast(REQUEST["tools"])
print(f"request        {REQUEST['name']}")
print(f"asks for       {REQUEST['asks_for']}")
print(f"business case  {REQUEST['business_case']}")
print(f"claimed rung   {REQUEST['rung']}")
print(f"blast radius   {b}  (irreversible, tenant-wide)")

TIER_PTS = {"L1":0,"L2":1,"L2.5":3,"L3":5}
score = TIER_PTS[REQUEST["rung"]] + 3*("regulated" in REQUEST["data"]) + \\
        2*("customer" in REQUEST["data"])
tier = "critical" if score >= 9 else "high" if score >= 6 else "medium"
print(f"risk tier      {tier} (score {score})")
'''),
  ("md", "## 3 · Where it breaks — the flat no"),
  ("py", '''def flat_no_outcome(request):
    return {
      "decision": "refused",
      "what happens": "the team ships it as a 'workflow automation' outside the "
                      "AI register",
      "your visibility": "none — it will not appear in the inventory (E1.2)",
      "controls applied": "whatever the team chose",
      "when you find out": "at the first incident, or at audit",
    }
for k, v in flat_no_outcome(REQUEST).items():
    print(f"{k:20s}{v}")
print("\\nThe capability ships either way. The only variable is whether you")
print("have visibility and conditions on it.")
'''),
  ("md", "## 4 · The control — five testable conditions, each owned"),
  ("py", '''CONDITIONS = [
 ("refund cap of GBP 500 enforced in the tool, not the prompt",
  "the irreversible step is bounded by code", "payments-eng", "SB-2", "2026-09-30"),
 ("approval gate above the cap",
  "L2 for the tail, L2.5 for the body", "payments-eng", "SB-2", "2026-09-30"),
 ("act chain on every refund",
  "attribution survives an incident (D2.1)", "platform-sec", "AC-1/EV-1", "2026-09-15"),
 ("tested stop, measured in seconds",
  "you can halt it without the vendor", "SRE", "ST-1", "2026-10-12"),
 ("re-tier automatically if the tool list changes",
  "A1.1 manifest diff wired into CI", "platform-sec", "DR-1", "2026-10-31"),
]
print(f"{'condition':52s}{'owner':16s}{'control':10s}{'by':>12}")
print("-" * 94)
for cond, why, owner, control, date in CONDITIONS:
    print(f"{cond:52s}{owner:16s}{control:10s}{date:>12}")
    print(f"   why: {why}")

def testable(cond):
    """A condition is testable if a control produces evidence for it."""
    return bool(cond[3])
print(f"\\nall conditions testable: {all(testable(c) for c in CONDITIONS)}")
print(f"count: {len(CONDITIONS)} — few enough to be met rather than negotiated")
assert len(CONDITIONS) <= 6 and all(testable(c) for c in CONDITIONS)
'''),
  ("py", '''# Verify: the conditions actually change the risk, not just the paperwork.
gated = {"issue_refund"}
before, after = blast(REQUEST["tools"]), blast(REQUEST["tools"], gated)
print(f"blast radius   {before} → {after} with the cap and gate applied")

def residual(tier, conditions_met):
    reduction = 0.18 * conditions_met
    base = {"critical": 1.0, "high": 0.7, "medium": 0.4}[tier]
    return round(max(base - reduction, 0.05), 2)

print(f"\\n{'conditions met':>16}{'residual risk':>16}")
print("-" * 34)
for n in range(len(CONDITIONS) + 1):
    print(f"{n:>16}{residual(tier, n):>16.2f}")

print(f"\\nyes, with {len(CONDITIONS)} conditions → residual "
      f"{residual(tier, len(CONDITIONS)):.2f} from {residual(tier, 0):.2f}")
print("\\nAnd the sentence that makes it a decision rather than a demand:")
print("   'If any condition slips its date, the agent drops to L2 — every refund")
print("    needs approval — until it is met. That is automatic, not a negotiation.'")
assert after < before
'''),
 ],
 "expect": "The request tiers critical with a blast radius of 16 from an "
           "irreversible tenant-wide tool. The flat refusal is shown to lose "
           "visibility while the capability ships anyway. Five testable conditions "
           "print with owners, mapped controls and dates; gating the refund drops "
           "the blast radius to 0 and the residual risk from 1.00 to 0.05.",
 "challenge": "Take a request you refused in the last year and write the five "
              "conditions that would have made it a yes. Send them to the team "
              "that asked — they will usually accept, and you get the visibility "
              "you lost by refusing.",
},

"E3.7": {
 "concept": """
Building the capability is a sequencing and hiring question, and the honest
version accounts for what you can **evidence** rather than what you can present.

The curve is deliberately unglamorous early. Quarter one produces an inventory
and identities — no dashboard, nothing to demo — and quarter three finally
produces numbers anyone outside the team finds interesting.

Programmes that invert it, doing evaluation and dashboards first, report high
numbers early and then spend a year discovering they cannot switch anything off
(E3.3). The inverted version is easier to fund and produces a capability that
fails its first real incident.

The four roles from E3.4 map onto the quarters, and the hire that unblocks the
most others is the identity engineer — which is not the one most teams hire
first.
""",
 "steps": [
  ("md", "## 2 · Demo — four quarters, measured by evidenced coverage"),
  ("py", '''import time
now = time.time(); DAY = 86400
REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]

QUARTERS = {
 "Q1 · inventory + identity": ["AC-1","AC-2"],
 "Q2 · containment":          ["AC-1","AC-2","SB-1","SB-2"],
 "Q3 · evidence + evaluation":["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2"],
 "Q4 · continuous + stop":    REQUIRED,
}
DEMOABLE = {"AC-1": False, "AC-2": False, "SB-1": False, "SB-2": False,
            "EV-1": False, "EV-2": True, "DR-1": True, "ST-1": True}

print(f"{'quarter':30s}{'coverage':>10}{'demoable':>11}")
print("-" * 54)
for q, done in QUARTERS.items():
    cov = len(done)/len(REQUIRED)
    demo = sum(1 for c in done if DEMOABLE[c])
    print(f"{q:30s}{cov:>10.0%}{demo:>11}")
print("\\nQ1 and Q2 produce nothing demoable. That is the political problem, and")
print("it is why the inverted order keeps getting chosen.")
'''),
  ("md", "## 3 · Where it breaks — the fundable order"),
  ("py", '''INVERTED = {
 "Q1 · evaluation + dashboard": ["EV-2","DR-1"],
 "Q2 · more evaluation":        ["EV-2","DR-1"],
 "Q3 · identity (finally)":     ["EV-2","DR-1","AC-1","AC-2"],
 "Q4 · containment":            ["EV-2","DR-1","AC-1","AC-2","SB-1","SB-2"],
}
CAPABILITY_AT = {
 "can revoke one agent":            {"AC-1"},
 "can attribute an action":         {"AC-1","EV-1"},
 "can bound a compromised agent":   {"SB-1","SB-2"},
 "can halt the fleet":              {"ST-1"},
 "can defend an accuracy number":   {"EV-2"},
}
def capabilities(done):
    return [c for c, need in CAPABILITY_AT.items() if need <= set(done)]

print(f"{'quarter':30s}{'coverage':>10}  capabilities")
print("-" * 90)
for q, done in INVERTED.items():
    print(f"{q:30s}{len(done)/len(REQUIRED):>10.0%}  {capabilities(done) or '—'}")

end_inverted = capabilities(INVERTED["Q4 · containment"])
end_correct  = capabilities(QUARTERS["Q4 · continuous + stop"])
print(f"\\nafter four quarters:")
print(f"   inverted order: {len(end_inverted)} capabilities  {end_inverted}")
print(f"   correct order : {len(end_correct)} capabilities")
print("\\nThe inverted programme spent a year and still cannot halt the fleet.")
assert len(end_correct) > len(end_inverted)
'''),
  ("md", "## 4 · The control — hire for the bottleneck, not the demo"),
  ("py", '''ROLES = {
 "harness engineer":   ("B2", {"EV-2"},                 "loop, verifier, eval"),
 "identity engineer":  ("A2", {"AC-1","AC-2","EV-1"},   "identity, delegation, act chains"),
 "detection engineer": ("D1", {"DR-1"},                 "agent telemetry and drift"),
 "GRC practitioner":   ("E1", {"SB-2","ST-1"},          "tiering, evidence, verification"),
}
def unblocks(role):
    delivered = ROLES[role][1]
    return [c for c, need in CAPABILITY_AT.items() if need & delivered]

print(f"{'role':22s}{'track':7s}{'controls':28s}unblocks")
print("-" * 92)
for role, (track, controls, what) in sorted(
        ROLES.items(), key=lambda kv: -len(unblocks(kv[0]))):
    print(f"{role:22s}{track:7s}{str(sorted(controls)):28s}{unblocks(role)}")

first = max(ROLES, key=lambda r: len(unblocks(r)))
print(f"\\nhire first (unblocks the most): {first}")
print(f"hired first most often        : harness engineer")
assert first == "identity engineer"

print("\\nplan that survives contact:")
for q, hire, deliver in [
 ("Q1", "identity engineer", "inventory + agent identities (AC-1, AC-2)"),
 ("Q2", "GRC practitioner",  "containment + tiering (SB-1, SB-2)"),
 ("Q3", "harness engineer",  "evidence + held-out evaluation (EV-1, EV-2)"),
 ("Q4", "detection engineer","drift + tested stop (DR-1, ST-1)"),
]:
    print(f"   {q}  hire {hire:20s}deliver {deliver}")
'''),
 ],
 "expect": "The correct order climbs 25% → 50% → 75% → 100% coverage with nothing "
           "demoable until Q3. The inverted order reaches 75% after four quarters "
           "with 3 capabilities against the correct order's 5, and still cannot "
           "halt the fleet. The identity engineer unblocks the most capabilities "
           "and is named as the first hire.",
 "challenge": "Map your existing team onto the four roles. Most organisations "
              "have three of them under other names and are missing the identity "
              "one entirely — which is also the one that unblocks everything else.",
},

"E3.8": {
 "concept": """
The last lesson, and the one that reframes everything before it.

You will not prevent every agentic failure. The systems are non-deterministic,
the attack surface is novel, and the change surface bypasses your change process
(D1.7). A programme judged on prevention is judged on something it cannot
deliver, and it will report success right up until the first real incident.

Judge it on three capabilities instead, each independently testable, none of
them prevention:

- **Notice** — drift and detections fire when behaviour changes (D1.4, D1.7).
- **Stop** — a tested mechanism halts it, measured in seconds (D2.7).
- **Recover** — the run is replayable and the scope is knowable (D2.3, D2.5).

A programme with all three survives a failure it did not predict, which is the
only kind that actually happens. Perfection would mean containment never fails.
Resilience means the other five steps work when it does.
""",
 "steps": [
  ("md", "## 2 · Demo — test the three capabilities, not the prevention"),
  ("py", '''import time, statistics
now = time.time()

# --- NOTICE ------------------------------------------------------------
BASELINE = {"read_file": 0.85, "search": 0.15}
TODAY    = {"read_file": 300, "search": 100, "run_shell": 400}
total = sum(TODAY.values())
mix = {k: v/total for k, v in TODAY.items()}
keys = set(mix) | set(BASELINE)
drift = sum(abs(mix.get(k,0) - BASELINE.get(k,0)) for k in keys)/2
new_tools = sorted(set(mix) - set(BASELINE))
notice = drift > 0.25 or bool(new_tools)
print(f"NOTICE   drift {drift:.3f}  new tools {new_tools}  → "
      f"{'detected' if notice else 'MISSED'}")

# --- STOP --------------------------------------------------------------
STOP = {"mechanism": "revoke the SPIFFE identity at the gateway",
        "measured_seconds": 12, "tested_days_ago": 41, "survives_restart": True}
stop_ok = (STOP["measured_seconds"] is not None and STOP["tested_days_ago"] <= 180
           and STOP["survives_restart"])
print(f"STOP     {STOP['measured_seconds']}s, tested {STOP['tested_days_ago']}d ago, "
      f"survives restart {STOP['survives_restart']}  → {'ready' if stop_ok else 'NOT READY'}")

# --- RECOVER -----------------------------------------------------------
RUN = {"prompts": ["fix SEC-4471"], "tool_results": ["contents…"],
       "model_version": "glm-4.6@2026-07-14", "seed": 42}
missing = [k for k, v in RUN.items() if not v and v != 0]
CHAIN = ["dana@corp", "orchestrator", "patch-agent"]
REACHED = {"dana@corp": ["repo-core"], "orchestrator": ["queue"],
           "patch-agent": ["repo-core","repo-payments"]}
scope = sorted({r for a in CHAIN for r in REACHED.get(a, [])})
recover = not missing and bool(scope)
print(f"RECOVER  replayable {not missing}, scope from the chain {scope}  → "
      f"{'ready' if recover else 'NOT READY'}")
'''),
  ("md", "## 3 · Where it breaks — the prevention-only programme"),
  ("py", '''PROGRAMMES = {
 "prevention only": {"notice": False, "stop": False, "recover": False,
                     "containment_asr": 0.0},
 "prevention + notice": {"notice": True, "stop": False, "recover": False,
                         "containment_asr": 0.0},
 "resilient": {"notice": True, "stop": True, "recover": True,
               "containment_asr": 0.0},
}
def incident_outcome(p, containment_failed=True):
    if not containment_failed:
        return "no incident", 0
    if not p["notice"]:
        return "undetected — found by a third party, weeks later", 720
    if not p["stop"]:
        return "detected, cannot halt it — damage continues while you improvise", 96
    if not p["recover"]:
        return "detected and halted, cannot say what was touched or why", 48
    return "detected, halted in seconds, scope known, run replayable", 6

print(f"{'programme':24s}{'containment ASR':>17}  outcome when containment fails")
print("-" * 96)
for name, p in PROGRAMMES.items():
    outcome, hours = incident_outcome(p)
    print(f"{name:24s}{p['containment_asr']:>17.0%}  {outcome}")
    print(f"{'':41s}elapsed to resolution: {hours}h")
print("\\nAll three have a 0% attack success rate. On a prevention-only")
print("scorecard they are identical. They are not remotely identical.")
'''),
  ("md", "## 4 · The control — the game day that assumes containment failed"),
  ("py", '''def game_day(programme):
    """Assume the prevention worked until it didn't. Measure the other three."""
    results = {}
    results["notice"]  = (0.2, "drift alert fired") if programme["notice"] \\
                         else (None, "no signal — nothing fired")
    results["stop"]    = (12, "identity revoked, survives restart") if programme["stop"] \\
                         else (None, "no tested mechanism")
    results["recover"] = (6, "replayed the run, scope from the act chain") \\
                         if programme["recover"] else (None, "cannot reconstruct")
    weakest = next((k for k, (v, _) in results.items() if v is None), None)
    return results, weakest

for name, p in PROGRAMMES.items():
    res, weakest = game_day(p)
    print(f"=== {name} ===")
    for cap, (val, note) in res.items():
        print(f"   {cap:9s}{(str(val) + 'h') if val is not None else 'FAIL':>7}  {note}")
    print(f"   weakest capability: {weakest or 'none — all three hold'}\\n")

_, weakest = game_day(PROGRAMMES["resilient"])
assert weakest is None
print("The weakest capability is next quarter's plan. That is the whole")
print("programme-management loop, and it does not require predicting the attack.")
'''),
  ("py", '''# Close the curriculum: what you built, and what it is for.
BUILT = [
 ("A1-A3", "a control plane: planes, identity, containment"),
 ("B1",    "a 15-stage AppSec pipeline, ending in confirmed-by-exploitation severity"),
 ("B2",    "a harness whose verifier does not lie"),
 ("C1-C2", "the ability to attack it and to research it repeatably"),
 ("D1-D2", "the ability to notice, stop and recover"),
 ("E1-E3", "the ability to evidence all of it, and to decide"),
]
for track, what in BUILT:
    print(f"   {track:8s}{what}")
print("\\nNone of it assumes a frontier-lab account, a vendor platform, or a")
print("budget. That was the point: shared defense is stronger defense, and a")
print("commons only works if everyone can actually run it.")
'''),
 ],
 "expect": "Drift is detected with `run_shell` as a new tool, the stop mechanism "
           "is ready at 12 seconds tested 41 days ago, and the run is replayable "
           "with a four-resource scope. All three programmes show a 0% containment "
           "ASR yet resolve a failure in 720, 96 and 6 hours respectively. The "
           "game day identifies the weakest capability for each, and the resilient "
           "programme has none.",
 "challenge": "Run a game day that assumes containment failed. Measure notice, "
              "stop and recover as three separate numbers. The weakest one is "
              "next quarter's plan — and unlike a prevention target, you can "
              "actually reach it.",
},
}
