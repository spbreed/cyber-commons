"""Lessons added with the five-phase Function D restructure, plus E1.13.

These live in one file rather than being scattered into the five `track_d*`
modules because they were written together and read as a set: the discover →
detect → investigate → respond → recover loop, and the two governance lessons
that the recover phase depends on.

Every lesson here is built the same way — a short framing, then the skill, run.
The skill is the lesson; the prose exists to say why you would load it.
"""
from __future__ import annotations

from .skills import skill_steps

EXERCISES: dict[str, dict] = {

# ---------------------------------------------------------------- D3.10
"D3.10": {
 "concept": """
A detection encodes a behaviour somebody already understood. Hunting goes the
other way: you state a hypothesis about behaviour that *would* be suspicious,
run it over stored traces, and find out whether it happens.

Over agent telemetry the hypothesis is not the endpoint one. It is not "has
something malicious executed" — it is **"has an agent done something its stated
purpose does not explain"**. A tool it never needs. An hour it never runs. A
volume no task requires.

The failure mode is specific and expensive: a hypothesis that describes the job
rather than the anomaly. It fires constantly, everyone stops reading it, and the
quarter is gone.
""",
 "steps": [
  ("md", """## 2 · A hypothesis is a sentence with a subject

"A workflow agent called a payments tool outside a booking flow" can be
falsified. "Look for anomalies" cannot — it is a wish.

And it needs a population before it runs. Without one, a hit rate has no
denominator, and five hits is not a result until you know five out of how
many."""),
  *skill_steps('detection/agent-telemetry-hunt',
               "## 3 · Three hypotheses, scored\\n\\n"
               "Watch the middle row. It matches fourteen runs to find two, "
               "because twelve of the matches are CyberTravels' overnight batch "
               "doing exactly its job."),
 ],
 "expect": "Three hypotheses scored on precision and recall against a labelled "
           "corpus, each ending in promote, tune or discard — and the "
           "working-hours hypothesis rejected at precision 0.14.",
 "challenge": "Write a fourth hypothesis for CyberTravels and score it. If its "
              "precision is near the base rate, you have described normal work.",
},

# ---------------------------------------------------------------- D2.5
"D2.5": {
 "concept": """
The fastest source of a good detection is an incident you have just had. The
trap is that **every candidate rule catches the incident** — that is how it was
generated — so catching it cannot be the property you select on.

What separates a rule worth deploying is what it does to traffic that is not the
incident. That means a benign corpus containing the hard cases: for a refund
rule, legitimate refunds. A corpus of unrelated traffic proves nothing, because
the naive rule looks clean against it.
""",
 "steps": [
  ("md", """## 2 · Write the bad candidates on purpose

Two rules are worth writing precisely because they will be rejected.

The **naive generalisation** takes the tool that appeared in the incident:
`any refund`. The **over-fitted** one takes the identifier: `refund on BK-772`.
Both catch the incident. One buries the queue and the other is worthless
tomorrow, and seeing them scored beside the good rule is what makes the good
rule a choice rather than an assumption."""),
  *skill_steps('detection/detection-rule-synthesis',
               "## 3 · Generate, then measure before shipping\\n\\n"
               "Three candidates, one benign corpus, one number each. A rule "
               "with no measured false-positive rate is a guess with syntax."),
 ],
 "expect": "All three candidates catch the incident; only the sequence rule ships. "
           "The naive rule fires on 18 legitimate refunds — a 21% false-positive "
           "rate on a business that runs on refunds.",
 "challenge": "Add a benign run that the shipped rule fires on. If you cannot "
              "construct one, your corpus is too easy.",
},

# ---------------------------------------------------------------- D3.2
"D3.2": {
 "concept": """
An investigating agent is handed broad read across the estate so it can find the
problem. Broad read across the estate is frequently what the problem *was*.

Admission rules decide, per investigation class and **before anything runs**,
which sources the agent may reach, which fields it may never see, and how much
it may pull. The volume cap is the one people leave out: the same query over the
same fields is an investigation at four hundred rows and a copy at ninety
thousand.
""",
 "steps": [
  ("md", """## 2 · Refusals are evidence, not errors

A refused query carries the exact query text, so a human can grant it
deliberately and the grant is on the record.

That matters twice. The investigator can escalate precisely rather than asking
for "more access", and the refusal log is what shows afterwards that the
response did not become the second incident — which is a question a regulator
will ask about an agent that read production during an outage."""),
  *skill_steps('secops/investigation-admission-rules',
               "## 3 · One admission set, six queries\\n\\n"
               "Three are refused. Look at the third: same source and same "
               "fields as an allowed query, refused on volume alone."),
 ],
 "expect": "Three queries allowed and three refused — one on an inadmissible "
           "source, one on a denied field, and one on volume alone.",
 "challenge": "Write the admission set for a data-exfiltration investigation. It "
              "is not the same set, and working out why is the exercise.",
},

# ---------------------------------------------------------------- D3.6
"D3.6": {
 "concept": """
Every investigator is wrong at step one. What separates an investigator from an
expensive autocomplete is what happens when the evidence stops fitting.

The way agents fail here is specific. They score evidence on whether it
**supports** a hypothesis — so evidence that supports nothing reads as noise,
when refutation is exactly what should force the replan. The agent keeps
gathering support for a theory the evidence already killed.
""",
 "steps": [
  ("md", """## 2 · The abandoned branch stays in the trace

A reviewer needs to see that a hypothesis was considered and dropped, not that
it was never raised. A conclusion with no visible alternatives looks inevitable,
and an investigation that looks inevitable is one nobody can audit.

In CyberTravels the branch that gets abandoned is the obvious one: the workflow
agent issued the refund, so the workflow agent did it. The evidence that kills
that theory supports nothing at all — the agent's own plan for that run contains
no refund step."""),
  *skill_steps('secops/investigation-replan-trace',
               "## 3 · An investigation that changes its mind\\n\\n"
               "Six pieces of evidence, three hypotheses, one replan. Step 4 is "
               "the one an eager investigator skips."),
 ],
 "expect": "One replan, from agent-misuse to indirect-injection, with the neutral "
           "evidence at step 4 marked as refuting nothing — and the abandoned "
           "branch still visible in the trace.",
 "challenge": "Add evidence that refutes the final hypothesis too. An "
              "investigation that cannot end undecided is not investigating.",
},

# ---------------------------------------------------------------- D4.1
"D4.1": {
 "concept": """
If each runbook picks its own automation tier, the blast radius of your response
is unknown until the response happens.

Two properties of the **action** decide it, and neither is a property of the
person writing the runbook. Is it reversible without a human decision? And does
it touch one agent, one tenant, or the estate?

Reversibility outranks radius, and that ordering is the whole content of the
policy. Deleting one agent's working directory touches a single agent and is
still manual, because there is no undo. Forcing human-in-the-loop across the
entire estate touches everyone and is not, because it is one flag and it can be
turned back off.
""",
 "steps": [
  ("md", """## 2 · Write it down once

Every runbook then cites a row rather than restating it. If you find yourself
arguing for an exception, the two properties are wrong — not the policy.

The honest test for reversibility is time. An undo that takes six hours of
manual work is not reversible for an incident that lasts twenty minutes."""),
  *skill_steps('response/remediation-policy-check',
               "## 3 · Nine actions, three tiers\\n\\n"
               "The tier is derived, not assigned. Read the two estate-wide rows "
               "against the two single-agent ones."),
 ],
 "expect": "Nine actions split three, three and three — with every irreversible "
           "action manual regardless of how small its radius is.",
 "challenge": "Add an action your team performs during an incident. If you cannot "
              "answer 'reversible without a human', that is the finding.",
},

# ---------------------------------------------------------------- D4.2
"D4.2": {
 "concept": """
The three tiers are not levels of ambition. They are three different trades
between **time to contain** and **the cost of acting on a bad signal** — and
which trade is right depends on the detection's measured false-positive rate,
not on taste.

There is no single score that ranks them, and this lesson refuses to print one.
Seconds of exposure and wrongly-contained agents are in different units. Any
number that ranks them has an exchange rate hidden inside it, chosen by whoever
wrote the formula.
""",
 "steps": [
  ("md", """## 2 · Both tiers fail; they fail differently

Fully automated contains in fourteen seconds and is wrong eight times in a
hundred, with nobody between the mistake and the estate.

Manual is wrong far less often and takes thirty-four minutes — which, against a
29-minute breakout time, means containment lands after the attacker has
finished. "Keep a human in it" is a risk decision too. It is just usually an
unstated one."""),
  *skill_steps('response/runbook-tier-assignment',
               "## 3 · One incident, three tiers\\n\\n"
               "Two columns, deliberately unranked. Choose the exchange rate "
               "openly, per incident class, or do not choose it."),
 ],
 "expect": "14s / 253s / 2072s to contain, against 8.0 / 1.2 / 0.2 wrong actions "
           "per hundred — and no third column ranking them.",
 "challenge": "Put your own detection's false-positive rate in and see whether the "
              "tier you already ship still looks right.",
},

# ---------------------------------------------------------------- D5.2
"D5.2": {
 "concept": """
"The on-call engineer missed the alert" is true and useless — it will happen
again next quarter to a different engineer. "We should have been more careful"
names no control and no change anyone can make.

A usable root cause names **the control that should have caught this and did
not**, in a form the next change can act on and the KCIs can later measure. The
test is mechanical, and it should be: does the statement name a control?
""",
 "steps": [
  ("md", """## 2 · Present, absent, or present-but-wrong

Three categories, and the third is the one that gets missed.

In the CyberTravels incident, stop authority was **present** and the incident
still ran 194 minutes. A control that exists but is never reached is not a
mitigating factor — it is evidence that the detection in front of it was the
gap, which is a different finding and a different fix."""),
  *skill_steps('response/root-cause-record',
               "## 3 · Three candidate statements, one usable\\n\\n"
               "The rejections are the lesson. Both rejected statements are "
               "true; neither can be built, tested or measured."),
 ],
 "expect": "One of three statements accepted. The first absent control in the "
           "chain is the root cause; the later absences are contributing.",
 "challenge": "Take your last postmortem's root cause and run the test on it. If "
              "it names a person or an intention, rewrite it as a control.",
},

# ---------------------------------------------------------------- D5.4
"D5.4": {
 "concept": """
A fix is a claim. The key control indicators built in E1.1 are how the claim
gets checked: re-measure the indicators the incident moved, and see which came
back to target.

Doing it automatically is the point. Done by hand, it happens for the incidents
somebody remembers — which are not the ones where it matters.
""",
 "steps": [
  ("md", """## 2 · Improvement is not restoration

The uncomfortable row in this run is detection time. It improved from 194
minutes to 118 and is still eight times its target, so the control the root
cause record named has been *partially* built.

Partially built is not built. Without the re-measurement it reads as done, and
the incident record would have said "remediated" for every indicator the
incident touched."""),
  *skill_steps('response/kci-fix-validation',
               "## 3 · Six indicators, three readings each\\n\\n"
               "Healthy, during the incident, and after the fix. Restored and "
               "not-restored are reported separately, and untouched indicators "
               "are kept out of the report entirely."),
 ],
 "expect": "Three indicators restored and two not, against an incident record that "
           "would have called all five remediated.",
 "challenge": "Add a sixth indicator that regressed — better than target before, "
              "worse after. The report has nowhere to put it yet.",
},

# ---------------------------------------------------------------- D5.5
"D5.5": {
 "concept": """
Most incidents end with a change to what is **deployed**. The policy that
permitted the incident is usually untouched — so the next system built under it
reproduces the conditions.

Stated as a diff, with the clause as it stands, the new text, and the incident
as the reason, the change can be argued with. Stated as a postmortem paragraph,
it cannot.
""",
 "steps": [
  ("md", """## 2 · Name what the diff does not fix

The proposal here changes three clauses and explicitly fails to address one
indicator — because no policy change can. The policy already required detection
within fifteen minutes; the control was simply never built to meet it.

That is an engineering item, not a policy item, and saying so in the proposal is
what stops it falling between the two functions forever."""),
  *skill_steps('grc/policy-change-proposal',
               "## 3 · A root cause record becomes a diff\\n\\n"
               "Every 'why' column is a measured number from the incident. A "
               "proposal argued on opinions gets decided by whoever is loudest."),
 ],
 "expect": "Three clauses changed with the incident as evidence, and KCI-04 named "
           "as unaddressed because it is an engineering gap rather than a policy "
           "one.",
 "challenge": "Write the fourth clause — the one your organisation would refuse. "
              "A proposal whose every line is easy did not come from a real "
              "incident.",
},

# ---------------------------------------------------------------- E1.13
"E1.13": {
 "concept": """
A control indicator is only an indicator if something measures it. Otherwise it
is a sentence in a policy, and the first evidence that a control was missing is
the incident.

The test is mechanical: can you compute this number from the estate, today,
without asking anyone? "Object handlers that compare an owner" passes.
"Is authorisation adequate" does not.

So these are computed from `cybertravels/` — the same tree B2.3 scans and A1.1
draws — and the output is a **gap list**, not a maturity score. A governance
report whose only artefact is a percentage changes nothing, because nobody can
action 72%.
""",
 "steps": [
  ("md", """## 2 · Every gap names where the fix is taught

A gap with no next step is a complaint. Each one here carries the lesson that
closes it — the ownership check, the rule that names your own HTTP wrapper,
default-deny on the tool call, the gateway.

One indicator in the set is deliberately one CyberTravels passes. A set that
always reports GAP cannot be shown to discriminate, and a reader has no way to
tell the instrument works."""),
  *skill_steps('grc/kci-control-measurement',
               "## 3 · Six indicators, measured now\\n\\n"
               "KCI-05 is the one worth arguing about: it measures a component "
               "that does not exist, so it reads zero and always will until "
               "somebody builds a gateway."),
 ],
 "expect": "One indicator met and five gaps, each with a named mitigation — and "
           "every number computed from the tree at run time rather than read from "
           "a register.",
 "challenge": "Write a seventh indicator for a control CyberTravels does have, and "
              "check it reads as met. An instrument that only ever says GAP is not "
              "measuring.",
},

}
