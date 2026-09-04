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
("md", "## 3 · Where it breaks — the findings-shaped update"),
("md", "## 4 · The control — exposure, likelihood, assurance, decision"),
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
("md", "## 3 · Where it breaks — govern tools instead, and watch it collapse"),
("md", "## 4 · The control — L1 must be free, or the inventory dies"),
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
("md", "## 3 · Where it breaks — evaluation first"),
("md", "## 4 · The control — measure the programme by capability, not activity"),
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
("md", "## 3 · Where it breaks — an incident crossing an unanswered seam"),
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
("md", "## 3 · Where it breaks — metrics that cannot degrade"),
("md", "## 4 · The control — project the five forward under neglect"),
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
("md", "## 3 · Where it breaks — the flat no"),
("md", "## 4 · The control — five testable conditions, each owned"),
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
("md", "## 3 · Where it breaks — the fundable order"),
("md", "## 4 · The control — hire for the bottleneck, not the demo"),
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
("md", "## 3 · Where it breaks — the prevention-only programme"),
("md", "## 4 · The control — the game day that assumes containment failed"),
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
