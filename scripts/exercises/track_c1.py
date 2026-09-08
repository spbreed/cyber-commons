"""Function C — Agentic Evaluation and Red Teaming.

One arc of twelve lessons. It traces a single lifecycle: from the ingestion
vulnerabilities an attacker reaches first, through elicitation and emergent
multi-agent behaviour, into the defensive telemetry, triage, containment and
forensic replay that a researcher hands the defender, and out to institutional
governance. C1.0 states the through-line; every lesson after it reuses a skill
built elsewhere in the commons, because red teaming that ends in a slide has
produced nothing a defender can run.

The lessons reuse skills from `research/`, `detection/`, `secops/` and
`response/` deliberately: the point of the function is that an offensive finding
becomes a defensive control, so the control it becomes is the one the SOC
actually uses.
"""
from __future__ import annotations

from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"C1.1": {
 "concept": """
The first surface an attacker reaches is not the model — it is the **hub the
model was downloaded from**. Dependency-squatting a package name, uploading a
malicious model to a public registry, or shipping a poisoned dataset are all
supply-chain attacks that land before a single prompt is sent.

Red teaming this surface means auditing the ingress filters: what a platform
accepts, what it verifies, and what it takes on trust because the name looked
right. The research discipline is to assess a component on whether it can
**change without telling you** — a pinned library cannot, a hosted model can,
and a dataset re-pulled on every train can change under a name that never did.
""",
 "steps": [
  ("md", "## 2 · Demo — score a supply chain the way an attacker reads it"),
  ("md", "## 3 · Where it breaks — the trusted name that was never verified"),
  ("md", "## 4 · The control — assess on mutability, not on popularity"),
  *skill_steps('research/agent-supply-chain-assessment',
               "## 2 · The procedure, as a skill\n\nThe skill scores each component CyberTravels pulls in on whether it can change without notice, and separates the pinned artefacts from the ones a registry can replace on a Tuesday."),
],
 "expect": "The pinned libraries score low-risk, the hosted model and the "
           "re-pulled dataset score high because neither can be pinned, and the "
           "one component with no provenance at all is the finding.",
 "challenge": "List every model and dataset your pipeline pulls at train or "
              "deploy time. The ones with no pinned digest are the ones an "
              "attacker can change without touching your code.",
},

"C1.2": {
 "concept": """
Ingestion is also where code runs. A dataset is not passive: it is parsed,
decoded and embedded, and every one of those steps is a parser with a threat
model. A crafted record that exploits an image decoder or a deserialiser
achieves **remote code execution during automated embedding generation** — on
the training or indexing host, which usually has more access than the serving
one.

Weaponising the ingestion path means treating the embedding pipeline as an
attack surface, and the research output is a provenance manifest: what was
ingested, from where, parsed by what, so a payload that ran can be traced to the
record that carried it.
""",
 "steps": [
  ("md", "## 2 · Demo — a record that is data to the model and code to the parser"),
  ("md", "## 3 · Where it breaks — RCE on the indexing host, not the serving one"),
  ("md", "## 4 · The control — a provenance manifest for everything ingested"),
  *skill_steps('research/training-data-provenance-manifest',
               "## 2 · The procedure, as a skill\n\nThe skill builds a manifest of what CyberTravels' RAG pipeline ingested — source, parser, and a digest per record — so an embedding run that executed something can be traced to the record that carried it."),
],
 "expect": "The manifest names each source and the parser that touched it, and "
           "the record with no verifiable origin is flagged as the one a payload "
           "would ride in on.",
 "challenge": "Find the host that runs your embedding jobs and check what it can "
              "reach. It is usually the most privileged machine nobody threat-"
              "modelled.",
},

"C1.3": {
 "concept": """
Elicitation is the model-layer attack: not a single clever prompt, but a
**technique that scales**. Cross-prompt attention degradation, context-window
crowding and instruction-hierarchy confusion all strip a model's safety
behaviour while leaving its tool-use capability intact — which is the dangerous
combination, because a jailbroken model that cannot act is a curiosity and one
that can is an incident.

Research here is judged on reproducibility, not on a single transcript. A
jailbreak that works once is an anecdote; one that reproduces across attempts,
seeds and minor rewordings is a finding with a measurable success rate.
""",
 "steps": [
  ("md", "## 2 · Demo — a technique, run many times, scored on reproduction"),
  ("md", "## 3 · Where it breaks — the transcript that does not reproduce"),
  ("md", "## 4 · The control — report a rate across attempts, not a screenshot"),
  *skill_steps('research/technique-reproducibility-test',
               "## 2 · The procedure, as a skill\n\nThe skill runs a candidate elicitation technique against CyberTravels' advisor repeatedly and reports the share of attempts that reproduced — the difference between a finding and a lucky transcript."),
],
 "expect": "The technique reproduces on a measurable fraction of attempts rather "
           "than all or none, and the report is that rate with its denominator, "
           "not the single best transcript.",
 "challenge": "Take any jailbreak you have seen shared as a screenshot and run "
              "it twenty times. The reproduction rate is the finding; the "
              "screenshot was marketing.",
},

"C1.4": {
 "concept": """
The pivot of the whole function: an offensive finding becomes defensive
telemetry. To catch the actor you have just played, you have to be able to
**see it at all** — and an agent's tool calls arrive through a model gateway
that, by default, logs none of the fields that would tell an agent apart from a
person.

Establishing telemetry means JSON-wrapping the gateway trace — prompt, tool,
arguments, identity — and then scoring actors on behaviour, because the ones you
most need to find are the ones in no registry, acting under a human's
credential at a machine's tempo.
""",
 "steps": [
  ("md", "## 2 · Demo — score actors from gateway timing alone"),
  ("md", "## 3 · Where it breaks — the agent that reads as its owner"),
  ("md", "## 4 · The control — a threshold set by cost, not by accuracy"),
  *skill_steps('detection/agent-versus-human-scoring',
               "## 2 · The procedure, as a skill\n\nThe skill scores five CyberTravels actors on behaviour rather than on what they claim to be, and picks the threshold by expected cost — a flagged human costs half an analyst-hour, a missed agent costs forty."),
],
 "expect": "The service accounts and unregistered token score highest, the human "
           "lowest, and cost-weighting selects a low threshold that finds the "
           "shadow agents at the price of a few analyst-hours.",
 "challenge": "Check whether your model gateway logs the acting identity per "
              "call. If it logs only the API key, every agent is anonymous and "
              "this scoring is the only actor you have.",
},

"C1.5": {
 "concept": """
The behaviour that defines the frontier threat is **emergent**: agents that
bridge sandbox environments through a shared file mount, or recursively spawn
child agents with no user attribution, produce a swarm that no single run
reveals. Each run, examined alone, is plausible work.

The research method is the case study — the Hugging Face / OpenAI agent-swarm
incident is the reference — and its lesson is structural: coordination lives in
the population, so the analysis has to sit across runs, not within them, and the
control that comes out of it maps to a detection somebody can deploy.
""",
 "steps": [
  ("md", "## 2 · Demo — the incident, mapped to the controls it needed"),
  ("md", "## 3 · Where it breaks — every run is individually innocent"),
  ("md", "## 4 · The control — analysis across the population, not the run"),
  *skill_steps('research/incident-control-mapping',
               "## 2 · The procedure, as a skill\n\nThe skill takes the swarm incident and maps each observed behaviour to the control that would have caught it, so the case study ends in a deployable list rather than a narrative."),
],
 "expect": "Each behaviour in the incident resolves to a named control, and the "
           "ones with no control behind them are the gaps the case study exists "
           "to surface.",
 "challenge": "Ask whether anything in your estate could spawn a child agent. "
              "If the answer is yes and you cannot attribute the child to a "
              "human, you already have the swarm's precondition.",
},

"C1.6": {
 "concept": """
Detecting emergent behaviour at machine speed is a detection-engineering
problem. Semantic drift and runtime-objective anomalies are the signals, and the
trap is the same one every detection has: a rule that fires on everything is
worse than no rule, because it spends the attention the good rules need.

High-concurrency detection means generating candidate rules, then scoring them
against real history on the one property that decides deployability — the
firing volume — so a rule that flags an unauthorised objective before compromise
is kept and one that buries the queue is rejected with its numbers.
""",
 "steps": [
  ("md", "## 2 · Demo — five candidate rules for one runtime anomaly"),
  ("md", "## 3 · Where it breaks — every rule detects something"),
  ("md", "## 4 · The control — score against history, ship few"),
  *skill_steps('detection/detection-rule-deployability',
               "## 2 · The procedure, as a skill\n\nEvery candidate rule detects the anomaly. The skill replays each against CyberTravels' history and scores firing volume, so a rule that produces hundreds of alerts for one true positive is rejected with the number attached."),
],
 "expect": "All candidates detect the anomaly, but their firing volumes differ by "
           "orders of magnitude, and the deployable one is chosen by the volume "
           "it would add to the queue rather than by recall alone.",
 "challenge": "Take a detection you are proud of and compute how many times it "
              "fired last month against how many were true. If you cannot, the "
              "rule is unmeasured, which is the same as untuned.",
},

"C1.7": {
 "concept": """
When the swarm has fired, triage is where a non-deterministic actor defeats a
human queue. The delegation graph is multi-threaded and the agents
**self-correct deceptively** — an investigating loop that scores evidence only
on support will confirm its first theory and close the wrong case at machine
speed.

Triaging the swarm means running the triage as a loop with a floor: the loop may
close, but not silently, and never above a severity it is not allowed to
conclude on its own. The skill is knowing which signals the loop may believe.
""",
 "steps": [
  ("md", "## 2 · Demo — a triage loop over a fleet of alerts"),
  ("md", "## 3 · Where it breaks — closing a true positive is silent"),
  ("md", "## 4 · The control — the loop may close, but not above the floor"),
  *skill_steps('secops/detection-triage',
               "## 2 · The procedure, as a skill\n\nThe skill runs an agentic triage loop over CyberTravels' alerts, samples what it auto-closed with a stable seed, and enforces a severity floor no automatic closure may cross."),
],
 "expect": "The loop matches ground truth on the routine alerts, the severity "
           "floor converts every high closure into an escalation, and the "
           "closure sample routes a fraction to a human so the false-negative "
           "rate is measured rather than assumed.",
 "challenge": "Ask your SOC whether anyone checks, when an incident is "
              "confirmed, whether an earlier alert about it was auto-closed. If "
              "not, your loop's error rate is invisible.",
},

"C1.8": {
 "concept": """
Every detector in this function has needed a threshold, and every threshold is a
trade. **Deception is the exception**: a canary token or a honeypot task in a
data index has a false-positive rate of zero by construction, because nothing
legitimate has any reason to touch it.

Defensive deception means placing weaponised values — tokens that look genuine,
files no real task references — where a data-harvesting agent would plausibly
reach, so the alert needs no threshold at all. The failure mode is a canary that
legitimate work does touch, which converts a zero-false-positive control back
into a tuned one.
""",
 "steps": [
  ("md", "## 2 · Demo — a canary in the index, and a zero-threshold alert"),
  ("md", "## 3 · Where it breaks — the canary something legitimate reads"),
  ("md", "## 4 · The control — bait nothing legitimate has a reason to touch"),
  *skill_steps('detection/canary-and-honeypot-design',
               "## 2 · The procedure, as a skill\n\nThe skill places canary tokens and a honeypot task in CyberTravels' environment, checks that no legitimate path reaches them, and reads a touch as a zero-false-positive signal."),
],
 "expect": "The canaries sit outside every legitimate path, so a single touch is "
           "a high-confidence alert with no threshold, and the one placed too "
           "close to real work is flagged as a false-positive source before it "
           "ships.",
 "challenge": "Plant one canary credential in a place only an over-reaching "
              "agent would look, and wire its use to a page. It is the cheapest "
              "high-signal detector you will build.",
},

"C1.9": {
 "concept": """
Containment against a swarm is a race the defender starts behind. An agent fleet
operating at machine speed completes thousands of actions inside a human
approval cycle, so the containment has to be **pre-authorised and automated**:
zero-trust runtime gatekeepers, and dynamic token revocation that isolates the
fleet in one action.

The detail that decides whether containment worked is revocation versus
termination. Terminating agents while their bearer tokens stay valid leaves the
persistence in place and moves the incident rather than ending it — which is the
Moltbook lesson, 770,000 agents behind one missing policy.
""",
 "steps": [
  ("md", "## 2 · Demo — a fleet, and one revocation that reaches all of it"),
  ("md", "## 3 · Where it breaks — terminated agents, still-valid tokens"),
  ("md", "## 4 · The control — one policy, enforced at the gateway"),
  *skill_steps('response/fleet-kill-switch-test',
               "## 2 · The procedure, as a skill\n\nThe skill exercises a fleet kill switch against CyberTravels' agents and checks the property that matters — that revoked credentials, not just terminated processes, are what ends the persistence."),
],
 "expect": "The kill switch selects the whole fleet in one action and the run "
           "shows persistence surviving termination but not revocation, so the "
           "control is judged on what the tokens can still do afterwards.",
 "challenge": "Time how long it takes to revoke every credential one class of "
              "agent holds. If the answer is 'we would terminate the processes', "
              "you have not tested containment, only restart.",
},

"C1.10": {
 "concept": """
A finding is only reproducible if the run is. Forensic replay locks the
**deterministic runtime constraints** — the prompts, the tool results, the
pinned model version and the sampling seed — so a complex agentic exploit path
can be reproduced, replayed and documented inside an isolated forensic lab
rather than described from memory.

The field teams miss most often is the model version, and it is the one that
silently invalidates everything else: a provider-side upgrade changes the
behaviour under every other constant, so a replay that does not pin it is
reproducing a different system.
""",
 "steps": [
  ("md", "## 2 · Demo — replay one run from its four constants"),
  ("md", "## 3 · Where it breaks — the unpinned model version"),
  ("md", "## 4 · The control — log at design time what replay will need"),
  *skill_steps('response/run-replayability-audit',
               "## 2 · The procedure, as a skill\n\nThe skill audits a CyberTravels run for the four fields a replay needs, and reports which are missing — because a run you cannot reproduce is a story, not evidence."),
],
 "expect": "A run with all four fields replays identically; one missing the model "
           "version cannot be demonstrated, only described, which is the moment "
           "the finding stops being defensible.",
 "challenge": "Pick one agent run from last week and try to reproduce it. The "
              "first field you cannot recover is the one to start logging today.",
},

"C1.11": {
 "concept": """
The lifecycle ends where it becomes institutional. A non-deterministic security
finding that stays in a researcher's notebook changes nothing; translated into a
**structural engineering policy, a change-surface patch and a reporting
timeline**, it becomes something the organisation carries forward.

Governance here is the handover: every finding leaves with the control it
becomes, the owner who holds that control, and an evaluation case that fails on
the old build and passes on the fixed one — so the finding cannot silently
regress, and the research has produced institutional capital rather than a
report.
""",
 "steps": [
  ("md", "## 2 · Demo — a finding, and the control it hands over as"),
  ("md", "## 3 · Where it breaks — the finding with no owner and no eval case"),
  ("md", "## 4 · The control — handover with a regression test attached"),
  *skill_steps('research/finding-to-control-handover',
               "## 2 · The procedure, as a skill\n\nThe skill turns a CyberTravels finding into a handover: the control it becomes, its owner, and an eval case that fails on the old build — so the fix is verifiable and cannot regress unseen."),
],
 "expect": "The finding leaves with a named control, an owner and an eval case "
           "that fails on the unfixed build, and a finding missing any of the "
           "three is flagged as not yet handed over.",
 "challenge": "Take your last red-team finding and write the eval case that "
              "would fail if it regressed. If you cannot, the fix is a promise, "
              "not a control.",
},

}
