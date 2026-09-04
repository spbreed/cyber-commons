"""D1 — The SOC Analyst & Detection Engineer. Eight sessions.

Two directions run through this track and they are not the same job:

    detection WITH agents   — the analyst's loop gets faster   (D1.1–D1.3)
    detection FOR agents    — the agent is now the subject      (D1.4–D1.8)

The second is the new work, and it inverts several classic baselines.
"""

MODEL_NOTE = """
> **About the model in this notebook.** It runs offline against a deterministic
> replay so the lesson executes on a Kaggle kernel with no network. To run the
> same triage against a real open-weight model:
>
> ```bash
> ollama pull glm-4.6            # or kimi-k2, llama3.3
> export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
> ```
"""

from .skills import SKILL_RUNTIME

from . import diagrams as D

EXERCISES: dict[str, dict] = {

"D1.1": {
 "concept": """
The classic SOC job is a queue: alerts arrive, an analyst reads each one,
decides, and moves on. The constraint is human attention, and it does not scale
— which is why tier-1 burnout and alert fatigue are structural rather than
cultural problems.

The agentic version replaces "read every alert" with "operate a loop that reads
every alert". The analyst's job becomes:

- deciding **what the loop is allowed to conclude** (the verifier, B2.0),
- deciding **what it may do about it** (the tool policy, A3.5),
- and handling the cases it escalates.

The skill that transfers is not triage speed. It is knowing which signals the
loop may believe — because a triage loop with a weak verifier closes true
positives at machine speed, and closing a true positive is silent.
""",
 "steps": [
  ("model", {
   "title": 'The model backend, and the disposition it proposes',
   "task": 'Triage this alert to one of: escalate, close-benign, needs-context.\n\nAlert: service account svc-reports authenticated from 203.0.113.9 at 03:14 and listed all S3 buckets. svc-reports normally runs hourly from 10.2.0.0/16 and touches one bucket.',
   "replay": "escalate - the source range and the breadth of the list call are both outside this account's established pattern.",
   "system": 'You are a SOC triage assistant. One line: disposition, then why.',
   "check": '("returned one of the three dispositions", any(d in answer.lower() for d in ("escalate", "close-benign", "needs-context")))'}),
  ("md", "## 2 · Demo — the queue, and the loop that reads it"),
("md", "## 3 · Where it breaks — closing a true positive is silent\n\n"
         "Every triage decision has two error directions and they are not "
         "symmetric. Escalating a false positive costs an analyst ten minutes. "
         "**Closing a true positive costs you the incident**, and nothing tells "
         "you it happened."),
("md", "## 4 · The control — the loop may close, but not silently\n\n"
         "Three rules make an agentic triage loop safe to run, and none of them "
         "is about model quality."),
],
 "expect": "The triage loop escalates 4 alerts and closes 4, matching ground "
           "truth on all 8. Lowering the confidence bar trades analyst minutes "
           "against missed incidents. The severity floor converts any high or "
           "critical closure into an escalation, and the closure sampling routes "
           "a fraction of routine closures to a human for quality measurement.",
 "challenge": "Ask your SOC one question: when an incident is confirmed, does "
              "anyone check whether an earlier alert about it was closed? If "
              "nobody does, you have no measurement of your false-negative rate — "
              "with or without an agent.",
},

"D1.2": {
 "concept": """
An alert about a human is triageable with three facts: who, what, when. An alert
about an agent needs three more, and without them every analyst has to guess.

- **The acting identity** and the principal it acted for (A2.1).
- **The scopes it held** at the time. This is the decisive field: reading
  `.env` is alarming for an agent scoped `repo:read` and routine for a
  secrets-rotation agent.
- **The delegation chain**, so the analyst can see who caused the task.

Without scope in the alert, the analyst's only options are to escalate
everything or to develop a habit of closing agent alerts. Both happen, and the
second one happens quietly.
""",
 "steps": [
  ("md", "## 2 · Demo — the same alert, with and without context"),
("md", "## 3 · Where it breaks — measure the analyst's decision quality"),
("md", "## 4 · The control — the six fields, and what each one decides"),

  ("md", "## 6 · Triage as a skill — and the sample that keeps it honest\n\n"
         "Context turns a guess into a verdict. Automating the verdict without "
         "automating the audit of it is how a closing rule quietly starts "
         "closing real incidents.\n\n"
         "The skill therefore requires a sampling rule over anything "
         "auto-closed, and requires its seed to come from something **stable**. "
         "Sampling seeded from `hash()` picks a different subset on every run, "
         "so you can never tell whether a change in findings came from the rule "
         "or from the dice."),
  ("skill", "secops/detection-triage"),

],
 "expect": "The bare alert is identical for both agents. Enriched, the "
           "secrets-rotation agent is within remit and the patch agent is not. "
           "Context-free triage escalates both — generating a nightly false "
           "positive — while scope-aware triage matches ground truth on both.",
 "challenge": "Check which of the six fields your agent telemetry carries today. "
              "Scopes-held is the one almost nobody logs, and it is the one that "
              "decides the alert.",
},

"D1.3": {
 "concept": """
Using an agent to write detections is genuinely effective: it produces candidate
rules quickly, across more log sources than a human would attempt.

What it cannot supply is the judgement that decides whether a rule ships, because
that judgement depends on a cost the telemetry does not contain: **analyst
trust**. A rule with 5% precision is not 5% useful — it is negatively useful,
because it spends attention that the good rules need.

So the workflow is: the agent generates candidates, and a scoring step against
real historical telemetry decides which survive. The scoring step is the job, and
it is the part teams skip.
""",
 "steps": [
  ("model", {
   "title": 'The model backend, and the detection it writes',
   "task": 'Write the detection condition for: a non-human identity listing more than 20 distinct buckets within 5 minutes, from outside its usual CIDR. Pseudocode, at most four lines.',
   "replay": "actor.type == 'service_account'\nand count_distinct(event.bucket, window='5m') > 20\nand not cidr_match(source.ip, actor.baseline_cidr)",
   "system": 'You write detection logic. Condition only, no prose.',
   "check": '("expresses a threshold", any(t in answer for t in (">", ">=", "20")))'}),
  ("md", "## 2 · Demo — five candidate rules for one concern"),
("md", "## 3 · Where it breaks — every rule 'works'\n\n"
         "All five detect something. R1 has perfect recall on http traffic and "
         "would put 301 alerts a day in the queue. R4 has 100% precision on "
         "nothing useful. The deployable set is decided by a threshold nobody "
         "writes down."),
("md", "## 4 · The control — generate many, score against history, ship few"),
],
 "expect": "All five rules detect something. R1 fires 301 times for 1 true "
           "positive; R5 fires twice for 2 true positives with perfect precision "
           "and recall. The deployability check rejects the broad rules and the "
           "failed-action rule, shipping only the precise ones with a small daily "
           "queue impact.",
 "challenge": "Set your own alerts-per-true-positive budget and apply it to the "
              "rules already in production. Most SOCs discover that several "
              "long-standing rules would not pass the bar they would set today.",
},

"D1.4": {
 "concept": """
This is the new work, and it starts by discarding baselines that have served the
SOC well for twenty years.

Human behavioural detection assumes irregularity, working hours, and a rate
ceiling set by typing speed. An agent violates all three *while behaving
correctly*:

| Classic signal | For a human | For an agent |
|---|---|---|
| two countries in an hour | incident | routine (multi-region) |
| 300 file reads a minute | incident | idle |
| activity at 03:00 | suspicious | meaningless |
| the same action 500 times | suspicious | a stuck loop — but not malicious |

Applying human baselines to agents produces an alert on every session, so the
rule gets tuned down, and then it never fires again — including when something
is genuinely wrong.

The signals that *do* work for agents are about **change**: a tool it has never
used, a mix that has shifted, a scope exercised that was never needed before.
""",
 "steps": [
  ("md", "## 2 · Demo — classic baselines against agent traffic"),
("md", "## 3 · The control — detect change, not activity"),
("md", "## 4 · Verify — the alert text an analyst can act on\n\n"
         "\"Anomaly detected\" fails both tests: it does not say what changed, and "
         "it does not say what to do."),
],
 "expect": "All three classic rules fire on an agent doing its job and only the "
           "rate rule fires on the human. Drift is within tolerance at week 1, "
           "significant at week 4 with `write_file` and `repo:write` new, and "
           "larger at week 8 with `run_shell` and an `exec` scope. The alert text "
           "names what changed, why it matters and what to do.",
 "challenge": "Take one human-baseline rule in your SIEM and check how it behaves "
              "against a service account. If it fires nightly, it is already "
              "tuned off for that actor — which means you have no detection there "
              "at all.",
},

"D1.5": {
 "concept": """
Agent telemetry has a property no other log source has: it contains the
**reasoning**, not just the action. The trace records what the agent was trying
to do, what it considered, and what the verifier said.

That is enormously useful for investigation and it is a retention and privacy
problem, because reasoning traces contain whatever was in the context window —
which routinely includes customer data, source code and secrets that were read
legitimately.

So retention has to be decided **per field**, not per record:

| Field | Forensic value | Sensitivity |
|---|---|---|
| timestamps, tool, target | high | low |
| verifier detail | high | low |
| acting identity + chain | high | low |
| model prompts | medium | **high** |
| tool results | high | **high** |

The first three are cheap and should be kept long. The last two are where the
retention conversation actually is.
""",
 "steps": [
  ("md", "## 2 · Demo — one agent run, as a telemetry record"),
("md", "## 3 · Where it breaks — what is actually in there"),
("md", "## 4 · The control — retention per field, and a hash for the rest"),
],
 "expect": "The full record contains a payment-card pattern found in a source file "
           "the agent read legitimately. Per-field retention keeps timestamps, "
           "tool, target and verifier for 400 days while dropping prompts at 30 "
           "days and tool results at 7, replacing them with hashes. After 90 days "
           "no sensitive content remains and the record can still answer what the "
           "agent did and what the harness believed.",
 "challenge": "Check the retention period on your agent traces. If it is the same "
              "as your firewall logs, one of those two numbers was chosen without "
              "anyone looking at what the traces contain.",
},

"D1.6": {
 "concept": """
Distinguishing agent from human in telemetry matters because the ones you most
need to find are the ones not in any registry (A3.7).

Three signals, none sufficient alone:

- **Regularity** — the coefficient of variation of inter-arrival times. Humans
  are irregular; loops are metronomic.
- **Rate** — sustained multi-action-per-second activity is not typing.
- **Continuity** — software has no evenings.

The honest part of this lesson is the error analysis, because the two error
directions are not symmetric:

- A **human misclassified as an agent** triggers an investigation. Mild cost,
  self-correcting.
- An **agent misclassified as human** stays invisible, which is the entire risk
  you were trying to address.

That asymmetry decides the threshold, and it argues for a lower one than
accuracy-maximisation would give you.
""",
 "steps": [
  ("md", "## 2 · Demo — score actors from timing alone"),
("md", "## 3 · Where it breaks — sweep the threshold and read both errors"),
("md", "## 4 · The control — pick the threshold from the cost, not from accuracy"),
],
 "expect": "The service indexer and unknown token score highest, the human lowest, "
           "with the IDE user and the politely-jittered agent in between. The "
           "threshold sweep shows humans flagged rising and agents missed falling "
           "as the threshold drops. Cost-weighting selects a low threshold, and "
           "joining against the registry identifies the unregistered actors as "
           "shadow agents.",
 "challenge": "Set COST_FN honestly for your organisation — it is the expected "
              "cost of an unmanaged agent operating undetected for a quarter. "
              "That number, not model accuracy, is what should set your threshold.",
},

"D1.7": {
 "concept": """
Drift monitoring exists because an agent's behaviour changes **without a code
change**. A new model version, an edited prompt, an added tool — none of these
pass through the change management process built for code, and all of them
invalidate the testing your controls were signed off against.

That is the precise claim: the control was tested against a behaviour that no
longer exists. It has not failed; it is *unevidenced*, which is a different and
more honest state.

Two things are needed:

1. A **signed-off baseline** — what normal looked like when the control passed.
2. A **freshness window** on the control test, derived from how fast the thing
   it tests actually drifts.

E1.7 turns the second into a compliance posture. This lesson produces the signal.
""",
 "steps": [
  ("md", "## 2 · Demo — drift across a quarter"),
("md", "## 3 · Where it breaks — none of these was a code change"),
  ("html", D.table(
    ["change surface", "in change management?", "what happens today"],
    [["application code", "yes", "pull request, review, CI"],
     ["agent prompt", "<b>no</b>", "edited in a console"],
     ["tool manifest", "<b>no</b>", "a config change, with no threat-model diff"],
     ["model version", "<b>no</b>", "provider-side; you may not be told"],
     ["policy", "yes", "if it is in git — often it is not"],
     ["approval settings", "<b>no</b>", "a toggle in an admin UI"]],
    emphasise=1,
    caption="Four of six surfaces bypass change management entirely. Drift is "
            "the failure mode with no adversary, and this table is why it is "
            "also the failure mode with no ticket.")),
  ("md", "## 4 · The control — freshness derived from the observed drift rate"),
],
 "expect": "Drift rises across the quarter from 0.0 at sign-off to roughly 0.35 "
           "after the model upgrade, with `run_shell` appearing as a new tool. "
           "Four of six change surfaces bypass change management. The observed "
           "drift rate yields a freshness window, and the 90-day-old control test "
           "is reported STALE rather than passing.",
 "challenge": "Compute the drift rate for one production agent from three months "
              "of telemetry, and set its control freshness window from that "
              "number rather than from the audit calendar.",
},

"D1.8": {
 "concept": """
Threat intel is judged by exactly one thing: **how many detections came out of
it.** Everything else — feed volume, report quality, briefing frequency — is
input, not outcome.

An indicator is actionable when two things are true:

- it is a **type you can match on** (a host, a hash, a specific technique with a
  concrete precondition), and
- its **confidence justifies the false-positive cost** of the rule it becomes.

A narrative about adversary trends is not intelligence you can operate. It may
be genuinely useful for planning and it should not be counted as detection
coverage, because counting it that way makes a programme look covered when it is
not.
""",
 "steps": [
  ("md", "## 2 · Demo — a feed, converted"),
("md", "## 3 · Where it breaks — conversion is only the first of three numbers"),
("md", "## 4 · The control — agent-specific intel is mostly internal"),
  ("html", D.table(
    ["intel source", "converts to a detection", "why"],
    [["your own incidents", "<b>100%</b>", "the technique that worked against you"],
     ["your red team (C1)", "<b>90%</b>",
      "attack-suite results become detections directly"],
     ["your drift monitor (D1.7)", "<b>80%</b>",
      "baseline changes are leading indicators"],
     ["vendor advisories", "50%", "useful for the supply chain (C2.5)"],
     ["commercial feed", "30%",
      "generic indicators; little agent-specific content yet"]],
    emphasise=1,
    caption="The highest-converting sources are all internal. For agentic "
            "threats the intel programme is mostly a feedback loop out of C1 and "
            "D1.7, not a purchase.")),
 ],
 "expect": "Four of seven indicators convert to rules — the two narratives and "
           "the low-confidence host are dropped with reasons. The rules fire on "
           "three of five events with concrete responses. The three-number "
           "summary shows a 57% conversion rate and 67% of alerts actioned, and "
           "the source table ranks internal sources highest.",
 "challenge": "Compute your own three numbers for last quarter: indicators "
              "received, rules deployed, alerts actioned. The ratio between the "
              "first and third is the honest value of the programme.",
},
}
