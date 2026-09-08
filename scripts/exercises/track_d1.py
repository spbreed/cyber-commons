"""Eight Function D lessons, from the two-track era of the Agentic SOC.

    D1.3  agent telemetry as a log source
    D1.3  distinguishing agent from human
    D3.9  threat intelligence that becomes a detection
    D1.2  drift monitoring
    D2.2  detections whose subject is the agent
    D2.4  agent-assisted detection engineering
    D3.1  from alert queue to loop operator
    D3.3  the context that makes agent triage work

The file name is historical: Function D was two tracks when these were written
and is now five, so the lessons here span three chapters. Nothing depends on
which module a lesson lives in — `exercises/__init__.py` merges them and
`site/data/curriculum.json` is what decides order and chapter. Splitting these
into five files is a tidy-up nobody has needed yet; do not infer structure from
the filename.
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

from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"D3.1": {
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
("md", "## 2 · Demo — the queue, and the loop that reads it"),
("md", "## 3 · Where it breaks — closing a true positive is silent\n\n"
         "Every triage decision has two error directions and they are not "
         "symmetric. Escalating a false positive costs an analyst ten minutes. "
         "**Closing a true positive costs you the incident**, and nothing tells "
         "you it happened."),
("md", "## 4 · The control — the loop may close, but not silently\n\n"
         "Three rules make an agentic triage loop safe to run, and none of them "
         "is about model quality."),
  *skill_steps('detection/triage-loop-with-floor',
               '## 2 · The procedure, as a skill\n\nThe skill scores a triage loop against ground truth, sweeps the confidence bar so the trade between analyst minutes and missed incidents is made explicitly, and adds the severity floor that no automatic closure may cross whatever its confidence.'),
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

"D3.3": {
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
  ("skill_script", "secops/detection-triage/scripts/detection_triage.py"),

],
 "expect": "The bare alert is identical for both agents. Enriched, the "
           "secrets-rotation agent is within remit and the patch agent is not. "
           "Context-free triage escalates both — generating a nightly false "
           "positive — while scope-aware triage matches ground truth on both.",
 "challenge": "Check which of the six fields your agent telemetry carries today. "
              "Scopes-held is the one almost nobody logs, and it is the one that "
              "decides the alert.",
},

"D2.4": {
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
("md", "## 2 · Demo — five candidate rules for one concern"),
("md", "## 3 · Where it breaks — every rule 'works'\n\n"
         "All five detect something. R1 has perfect recall on http traffic and "
         "would put 301 alerts a day in the queue. R4 has 100% precision on "
         "nothing useful. The deployable set is decided by a threshold nobody "
         "writes down."),
("md", "## 4 · The control — generate many, score against history, ship few"),
  *skill_steps('detection/detection-rule-deployability',
               '## 2 · The procedure, as a skill\n\nEvery candidate rule detects something. The skill replays each against real history and scores the third property nobody checks — firing volume — so a rule that produces 301 alerts for one true positive is rejected with its numbers rather than with an adjective.'),
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

"D2.1": {
 "concept": """
Every rule in this chapter is written against something. This lesson is that
something, and it is designed twice if you are not careful: once on a whiteboard
where everything is indexed, and once when the bill arrives and retention is cut
across the board by whoever is holding the invoice.

The second design is the one you run, and it is made with no information about
what the SOC actually asks.

**Derive the tier from the queries.** Write down what the SOC runs and how fast
each needs an answer — triage in seconds, a hunt in minutes, a forensic replay
in hours — then tier each source by the *fastest* query that reads it. Nothing
else about the source decides it: not its volume, not how interesting it feels,
not who asked for it.

| tier | answers in | what belongs there |
|---|---|---|
| hot | seconds | anything triage or scoping reads |
| warm | minutes | anything a hunt reads |
| cold | hours | anything only forensics reads |
| drop | never | anything no query reads at all |

That last row is the one people skip. A source no query reads is not cheap
storage — it is a liability with a bill attached.

The saving is the headline. What the tiering *protects* is the point: agent
prompts are the single largest source in most estates and are read by exactly
one query, which can wait hours. Priced hot they are the line that gets cut, and
cutting them removes the only thing D5.1 can replay a run from.
""",
 "steps": [
  ("md", "## 2 · Demo — five real SOC queries, and what each one reads"),
("md", "## 3 · Where it breaks — index everything, then read the bill"),
("md", "## 4 · The control — one tier per source, derived and defensible"),
  *skill_steps('detection/telemetry-tiering-cost',
               '## 2 · The procedure, as a skill\n\nThe skill tiers six CyberTravels sources by the fastest query that reads each, prices hot against tiered, and names the source that would have been cut.'),
],
 "expect": "Four sources go hot because triage and scoping read them in seconds, "
           "host EDR goes warm, and agent prompts go cold — read by one query "
           "that can wait hours. Tiering costs about 29% less than indexing "
           "everything hot, and the prompts that are 23% of the volume survive "
           "at 1% of the hot price rather than being deleted.",
 "challenge": "List the five queries your SOC actually ran last month, then tier "
              "your sources from them. Any source that appears in no query is "
              "the finding — you are paying to store something nobody asks.",
},

"D2.2": {
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

### Where each one sits in MITRE

A rule with no technique against it cannot be gap-analysed, cannot be handed to
another team, and cannot be argued about with an auditor. Two matrices are
needed and they are not interchangeable: **ATT&CK** describes what the actor did
to your estate, **ATLAS** describes what was done to the model.

| agent signal | ATT&CK | ATLAS tactic |
|---|---|---|
| a tool it has never used, on inherited credentials | T1078 Valid Accounts | ML Attack Staging |
| bulk reads across a repository it has no task in | T1213 Data from Information Repositories | Exfiltration |
| output posted to an allowed SaaS domain | T1567 Exfiltration Over Web Service | Exfiltration |
| shell spawned from a model-produced string | T1059 Command and Scripting Interpreter | ML Attack Staging |
| instruction arriving in retrieved content | — | Initial Access · AML.T0051 |

Read the last row twice. Indirect prompt injection has **no ATT&CK technique**,
because ATT&CK has no notion of an instruction channel that is also a data
channel. Mapping it to something adjacent to make the coverage chart look
complete is the single most common way an agent detection programme lies to
itself.

ATLAS technique identifiers move faster than ATT&CK's, so re-check any specific
`AML.T####` against the live matrix before you put it in a report.
""",
 "steps": [
  ("md", "## 2 · Demo — classic baselines against agent traffic"),
("md", "## 3 · The control — detect change, not activity"),
("md", "## 4 · Verify — the alert text an analyst can act on\n\n"
         "\"Anomaly detected\" fails both tests: it does not say what changed, and "
         "it does not say what to do."),
  *skill_steps('detection/agent-aware-rule-review',
               "## 2 · The procedure, as a skill\n\nAll three classic rules fire on CyberTravels' patch agent doing exactly its job, and only the rate rule fires on the human. The skill runs both, then measures drift from a signed-off baseline week by week — naming the new tool rather than reporting a distance."),
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

"D1.3": {
 "concept": """
The two questions in this lesson are one question asked twice: **which of the
actors in your logs is software, and what does its trace contain once you keep
it?** Neither has an answer in a standard SIEM, and the second only becomes
urgent once the first one works.

### Finding the actor

The agents you most need to find are the ones in no registry (A3.7), and they
act under a person's authority in a person's name — so conventional UEBA reads
them as that person behaving strangely. Three behavioural signals separate them,
none sufficient alone:

- **Regularity** — the coefficient of variation of inter-arrival times. People
  are irregular; loops are metronomic.
- **Rate** — sustained multi-action-per-second activity is not typing.
- **Continuity** — software has no evenings.

The error directions are not symmetric, and that is what sets the threshold. A
**human misclassified as an agent** triggers an investigation: mild, and
self-correcting. An **agent misclassified as human** stays invisible, which is
the entire risk you were trying to address. Cost-weighting therefore picks a
lower threshold than accuracy-maximisation would.

### Keeping its trace

Once you have found it, agent telemetry turns out to have a property no other
log source has: it contains the **reasoning**, not just the action. The trace
records what the agent was trying to do, what it considered, and what the
verifier said.

That is enormously useful for investigation and it is a retention and privacy
problem, because reasoning traces contain whatever was in the context window —
routinely customer data, source code and secrets the agent read legitimately.
So retention is decided **per field**, not per record:

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
  ("md", "## 2 · Demo — score actors from timing alone"),
("md", "## 3 · Where it breaks — sweep the threshold and read both errors"),
("md", "## 4 · The control — pick the threshold from the cost, not from accuracy"),
  *skill_steps('detection/agent-versus-human-scoring',
               '## 2 · Finding the actor, as a skill\n\nThe skill scores five actors on behaviour rather than on what they claim to be, sweeps the threshold, and then picks it by expected cost — because a flagged human costs half an analyst-hour and a missed agent costs forty.'),

  ("md", "## 3 · What the trace you just started keeping contains"),
  *skill_steps('detection/agent-telemetry-retention',
               '## 4 · Keeping the trace, as a skill\n\nThe run record contains a payment-card pattern, in a source file the agent read legitimately. The skill scans every field, then sets retention per field so timestamps and verdicts survive for 400 days and prompts do not survive 30.'),
],
 "expect": "First: the service indexer and unknown token score highest, the human "
           "lowest, with the IDE user and the politely-jittered agent in between. "
           "The threshold sweep shows humans flagged rising and agents missed "
           "falling as it drops, cost-weighting selects a low one, and joining "
           "against the registry names the unregistered actors as shadow agents. "
           "Then the trace of one of them: a payment-card pattern in a source "
           "file it read legitimately, and per-field retention that keeps "
           "timestamps, tool, target and verifier for 400 days while dropping "
           "prompts at 30 and tool results at 7. After 90 days no sensitive "
           "content remains and the record still answers what the agent did.",
 "challenge": "Run the scoring against a week of your own authentication logs and "
              "count the actors it flags that are not in your registry. Then check "
              "the retention period on whatever traces you keep for them: if it "
              "matches your firewall logs, one of those two numbers was chosen "
              "without anyone looking at what the traces contain.",
},

"D1.1": {
 "concept": """
Nobody starts an agentic SOC from nothing. Four classes of sensor are already
deployed, already paid for, and already producing alerts:

| class | what it watches | open-source reference |
|---|---|---|
| **EDR** | processes, files and network on a host | Wazuh agent |
| **DLP** | sensitive content leaving a monitored channel | regex + file integrity monitoring |
| **CSPM** | cloud configuration, evaluated on a schedule | Prowler, ScoutSuite |
| **CNAPP** | container runtime and image contents | Falco, Trivy |

All four work. The question is not whether they are good — it is **which parts
of an agent's working day they are in the path of at all.**

That is a matrix, and it is worth building before a roadmap rather than after,
because the answer decides whether the next quarter is spent tuning or spent
building a source that does not exist yet.

The distinction that makes the matrix honest is **visibility, not alerting**.
"Would this fire" is a tuning question. "Is this sensor in the path" is a fact
about architecture, and a sensor that is not in the path cannot be tuned into
one that is.

Read the uncovered rows rather than the percentage. If they are arbitrary, tune.
If they share a property — every one inside the reasoning loop, or behind an API
the host never observes — then a fifth product of the same four kinds will not
move them.
""",
 "steps": [
  ("md", "## 2 · Demo — four sensors against nine ordinary agent actions"),
("md", "## 3 · Where it breaks — the combined column, and the four rows in it"),
("md", "## 4 · The control — derive the next source from the uncovered set"),
  *skill_steps('detection/sensor-coverage-matrix',
               '## 2 · The procedure, as a skill\n\nThe skill scores four sensor classes against nine things CyberTravels\' agents do in an ordinary day, takes the union per row rather than summing the columns, and prints the actions no class sees at all.'),
],
 "expect": "EDR and CNAPP each cover about a third of the agent's day, DLP and "
           "CSPM almost none of it, and all four combined still leave four of "
           "the nine actions seen by nothing: reading a customer record through "
           "an internal API, placing it in a prompt, calling a vendor MCP tool, "
           "and issuing a refund. Those four share a property, and it is the "
           "argument for D1.3 and D2.1 rather than for a fifth product.",
 "challenge": "Build the same matrix for your estate with your own actions in "
              "the rows. The number that matters is not the percentage — it is "
              "whether the uncovered rows have something in common.",
},

"D1.2": {
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
  *skill_steps('detection/behavioural-drift-monitor',
               "## 2 · The procedure, as a skill\n\nFour of six things that change an agent's behaviour never reach change management. The skill counts them, then tracks drift across a quarter and attributes the rise that coincides with the model upgrade — and the one that does not."),
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

"D3.9": {
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
     ["your drift monitor (D1.2)", "<b>80%</b>",
      "baseline changes are leading indicators"],
     ["vendor advisories", "50%", "useful for the supply chain (C2.5)"],
     ["commercial feed", "30%",
      "generic indicators; little agent-specific content yet"]],
    emphasise=1,
    caption="The highest-converting sources are all internal. For agentic "
            "threats the intel programme is mostly a feedback loop out of C1 and "
            "D1.2, not a purchase.")),
   *skill_steps('detection/threat-intel-to-rules',
               '## 2 · The procedure, as a skill\n\nFour of seven indicators convert; the two narratives and the low-confidence host are dropped with reasons. The skill then reports the three numbers a renewal conversation needs: converted, alerted, actioned.'),
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
