"""The five function introductions — one per function, before its first chapter.

Each answers the same question for its own function: what is this part of the
commons for, which of the two directions does it run in, and what will you be
able to do at the end of it. They are deliberately short: one framework, one
small piece of code that makes the framework concrete, and no risk material —
the risks start in the chapter that follows.
"""

from . import cybertravels as CT
from . import diagrams as D
from .models import MODEL_RUNTIME

from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"A1.0": {
 "concept": """
Meet **CyberTravels**. It sells corporate travel, and last quarter it shipped
an agentic platform that plans and manages a whole trip through a conversation.
Alex is the product engineer who built it.

CyberTravels is four agents, not one:

- a **Workflow Agent** that books flights and hotels, takes payments and issues
  refunds, through an MCP server with tool orchestration;
- a **RAG Travel Advisor** that recommends itineraries from curated templates
  indexed in a vector store;
- a **Coding Agent** that writes code, patches libraries, tests features in
  lower environments and generates unit tests;
- a **File System Agent** that reads vendor and customer PDFs and images with
  OCR and an LLM, then updates backend APIs and validates invoices.

Most of them reach their tools through MCP servers — one internal, one from a
third party. Some call APIs directly, with no MCP in the path at all. They send
each other messages. And when Alex runs CyberTravels locally to debug it, it reads
his laptop's filesystem over standard I/O.

Every one of those sentences is a design decision, and every one of them is
also an attack surface. **That is the whole subject of this commons, and
CyberTravels is the one system it is taught on.** You will attack CyberTravels in
Function C, build the pipeline that reviews its code in Function B, detect it
misbehaving in Function D, and govern it in Function E. It starts here, because
none of the rest is possible until the system is drawn.

### Zero trust, when the thing you cannot trust is the agent

Zero trust has a one-line definition that survives contact with agents: **no
implicit trust from position in the network, and every request authenticated,
authorised and logged at the point it is served.** Applied to a user on a
laptop, that means the VPN is not a permission. Applied to CyberTravels, it
means four harder things.

- **The identity is a workload, not a person.** The Workflow Agent needs its
  own attested identity, not a shared service account, or you cannot say which
  agent acted and cannot revoke one without breaking all of them.
- **The authority is per call, not per session.** An agent that holds
  `booking.*` for an hour is one injected instruction away from a refund. The
  grant has to be `booking.create`, issued for this task, expiring with it.
- **Instructions are data until something proves otherwise.** A model reads its
  operator's prompt, the user's message and a retrieved document as the same
  kind of token. Provenance at ingress is what makes the third one unable to
  select a tool.
- **The decision is adjudicated outside the agent.** A model asked to enforce
  its own policy is being asked to be both the subject and the guard. The
  enforcement point is the gateway in front of the tool call.

Stated in the negative, which is how you audit it: **the system prompt is not a
control, the network boundary is not a control, and "the model was told not to"
is not a control.** Each of those has to be replaced by something that holds
when the model does the wrong thing, because sooner or later it will.

### How this function is organised: risks, then controls

Function A is built out of two kinds of lesson, and the split is deliberate.

A **risk lesson** shows a failure happening, before anything tries to stop it.
It names the component of CyberTravels it attacks and produces the evidence —
so the control that follows is answering something you have already watched go
wrong, rather than a hazard somebody asserted.

A **control lesson** builds the mechanism, then breaks it, so you can see what
the control is actually load-bearing for. A control whose limits you cannot
state is one you will over-trust.

- **Chapter A1 — the architecture, and every risk it carries.** The component
  map, then one lesson per risk, each grounded in the OWASP Agentic AI threat
  taxonomy. It introduces no control at all, on purpose. It ends with two
  indexes: the twelve-row AI risk register in A1.18, and in **A1.19 the full
  control index** — every control CyberTravels needs, the agentic ones and the
  ordinary ones it still has to get right, with the lesson that owns each.
- **Chapter A2 — securing it: identity and ingress.** Who is calling, on whose
  behalf, and what came in from outside. These two close more of CyberTravels'
  risks than anything else, which is why they come first.
- **Chapter A3 — securing it: runtime and the gateway.** What holds after
  identity has been defeated, and how the controls collapse into one enforcement
  point once CyberTravels runs more than four agents.

One warning about the shape of this function, and it is the reason A1.19
exists. The agentic risks are the new ones, not the only ones. CyberTravels
still has to scan its dependencies, segregate production from everything else,
encrypt at rest and in transit, manage credentials and keys, validate input and
log what happened. An agent platform built on an estate that has not done those
is not an agentic security problem; it is an ordinary one wearing a new hat.

> The CyberTravels narrative, the six risk families and the twelve-row register
> used throughout this commons are from *Agentic AI is rising fast — but the
> attack surface is exploding*, Karthik Ramamoorthy, May 2025. The mapping onto
> lessons, the controls and all of the code are this commons'.
""",
 "steps": [
  ("md", "## 2 · CyberTravels, as built"),
  ("html", CT.ARCHITECTURE),

  ("md", "## 3 \u00b7 Zero trust, applied to this picture"),
  ("html", D.table(
    ["the rule", "what it means for CyberTravels", "where it is built"],
    [["<b>Identity is per workload</b>",
      "Each of the four agents gets its own attested identity. A shared "
      "service account means you cannot say which agent acted, and cannot "
      "revoke one without breaking all four.",
      "A2.1 &middot; A2.2 &middot; A2.5"],
     ["<b>Authority is per call</b>",
      "<code>booking.create</code> issued for this task and expiring with it, "
      "never <code>booking.*</code> held for the session. This is what stops "
      "an injected instruction reaching the refund endpoint.",
      "A2.3 &middot; A2.4"],
     ["<b>Instructions are data until proven otherwise</b>",
      "The operator prompt, the traveller's message and a retrieved document "
      "arrive as the same kind of token. Provenance at ingress is what stops "
      "the third one selecting a tool.",
      "A2.6 &middot; A3.1"],
     ["<b>The decision is adjudicated outside the agent</b>",
      "A model asked to enforce its own policy is both subject and guard. "
      "Default-deny sits at the gateway in front of the tool call, with the "
      "sandbox and egress control behind it.",
      "A3.1 &middot; A3.2 &middot; A3.3"]],
    caption="Stated in the negative, which is how you audit it: the system "
            "prompt is not a control, the network boundary is not a control, "
            "and \u2018the model was told not to\u2019 is not a control.")),

  ("md", "## 4 · The four agents, and what each one can reach"),
  ("html", D.table(
    ["agent", "what it does", "what it can reach"],
    [["Workflow Agent", CT.AGENTS["workflow"][1],
      "flights · hotels · <b>payments and refunds</b> · CRM"],
     ["RAG Travel Advisor", CT.AGENTS["advisor"][1],
      "the vector store — and whatever else was ingested into it"],
     ["Coding Agent", CT.AGENTS["coding"][1],
      "the repository, and the CI runner that builds it"],
     ["File System Agent", CT.AGENTS["files"][1],
      "uploaded files, backend APIs, and Alex's laptop when run locally"]],
    emphasise=2,
    caption="Read the third column as a permission set rather than a feature "
            "list. Two of these four can move money or ship code.")),

  ("md", "## 5 · Where the five functions sit\\n\\n"
         "Each one takes the same system and asks a different question of it."),
  ("html", D.table(
    ["function", "the question it asks of CyberTravels", "what it produces"],
    [["A", "what can go wrong here, and what closes it", "an architecture and its controls"],
     ["B", "how do we review its code, at its speed", "a pipeline, and a harness that scores it"],
     ["C", "can we break it before somebody else does", "findings you generated yourself"],
     ["D", "would we see it happening, and could we stop it",
      "detections, runbooks and a root cause"],
     ["E", "who signed off, and can they still evidence it",
      "indicators an auditor can re-compute"]],
    caption="Nobody takes all five. Everyone takes the common spine first, then "
            "the chapters for the chair they sit in, then one adjacent chapter.")),

  ("md", "## 6 · What the other four borrow from this one\\n\\n"
         "Not a claim about tidiness. It is why the map has to come first: every "
         "later function names a component of CyberTravels from it."),
  ("html", D.svg(D.DEFS
    + D.box(240, 10, 220, 48, "chapter 1", sub="CyberTravels' component map",
            colour=D.SECURE)
    + D.box(6, 124, 158, 66, "Function B", sub="reviews CyberTravels' code")
    + D.box(180, 124, 158, 66, "Function C", sub="attacks these components")
    + D.box(354, 124, 158, 66, "Function D", sub="watches them at run time")
    + D.box(528, 124, 166, 66, "Function E", sub="governs and evidences them")
    + D.arrow(320, 58, 96, 120) + D.arrow(335, 58, 250, 120)
    + D.arrow(365, 58, 424, 120) + D.arrow(380, 58, 600, 120),
    height=200,
    caption="Chapter A1 introduces no control at all, on purpose: you cannot "
            "choose a control for a risk you cannot yet name.")),

  ("md", "## 7 · Function A, in order"),
  ("html", D.table(
    ["chapter", "what it covers", "kind of lesson"],
    [["A1", "the architecture, every risk it carries, and the two indexes "
            "that close it", "risk"],
     ["A2", "securing it — identity and ingress", "control"],
     ["A3", "securing it — runtime and the gateway", "control"]],
    caption="Chapter A1 is the picture the other two stand on, and it ends on "
            "the index: A1.18 for the twelve agentic risks, A1.19 for every "
            "control CyberTravels needs including the ones that predate it.")),
 ],
 "expect": "CyberTravels as built — four agents, two MCP servers, direct API calls "
           "that skip MCP, agent-to-agent messaging and a local std-I/O path — "
           "with what each agent can reach read as a permission set. Then the "
           "question each of the five functions asks of that same system, and "
           "what each borrows from this chapter's component map.",
 "challenge": "Draw your own CyberTravels before the next lesson — the agents you "
              "run, the MCP servers and APIs they reach, and which of them can "
              "move money or ship code. A1.1 gives you the standard names for "
              "the boxes; comparing your drawing to it is the fastest way to "
              "find the component you forgot you had.",
},

"B2.0": {
 "concept": """
CyberTravels ships faster than Alex can read. The Coding Agent opens pull
requests that touch a hundred files, and the review that used to be a careful
hour is now a scroll. Function B is what he builds instead of scrolling.

It is one pipeline, built in order, and the first thing to get straight is
**where each piece of it can run at all** — because half of what is sold as AI
security tooling cannot run before a deploy, and half of it tells you nothing
after one.

### The line

**Pre-deployment works on artefacts sitting still.** Source, a manifest, an IaC
plan, a tool schema, an SBOM. Nothing is running, so the analysis is cheap,
repeatable and — the property that matters most — it **can block a merge**. It
is also structurally blind to every fact that does not exist until deployment:
the identity the workload actually got, the route it can actually reach, the
traffic it actually saw.

**Post-deployment works on a system that is running.** It sees what really
happened, which is the only way to learn some things at all. And it **cannot
block the change that caused it**. By the time it has an opinion, the merge is
in.

That is the whole of the distinction, and it decides more than people expect.
A risk covered only on the left is one you can prevent and cannot detect. A
risk covered only on the right is one you can detect and cannot prevent. Both
of them appear on a tooling inventory as the same word — *covered* — and only
one of them is what the person reading the inventory believed they had bought.

### Why the chapter is ordered this way

Stages 1 to 10 are pre-deployment: ingest the estate, derive a threat model,
audit the code, scan the supply chain, filter to what is reachable. They are
cheap and they can gate. Stages 11 to 15 need something running: a replica to
attack, an exploit to execute, a patch to prove, a report to sign. They are the
expensive half, and they exist because the cheap half produces hypotheses
rather than facts.

Nothing in this chapter fixes the middle. The gap between the two sides is not
a tool you are missing — it is the line itself, and the honest move is to know
which side each of your controls is on before somebody asks you whether a risk
is covered.
""",
 "steps": [
  ("md", "## 2 · What Alex is actually up against"),
  ("html", D.table(
    ["", "before the Coding Agent", "after"],
    [["pull requests per week", "6", "<b>40</b>"],
     ["files touched per PR", "3", "<b>up to 120</b>"],
     ["reviewers", "1", "1"]],
    emphasise=2,
    caption="Nothing about the review capacity changed. That is the whole "
            "problem, and it is the reason every stage after this one is "
            "automated rather than scheduled.")),

  ("md", "## 3 \u00b7 Every technique, on one side or the other"),
  ("html", D.table(
    ["technique", "pre-deploy", "post-deploy", "what only the other side sees"],
    [["SAST / code analysis", "<b>yes</b>", "no",
      "whether the vulnerable path is reached with real traffic"],
     ["Dependency and SBOM scanning", "<b>yes</b>", "partly",
      "what actually loaded, versus what the manifest pinned"],
     ["IaC and policy-as-code", "<b>yes</b>", "no",
      "the identity and network the workload really got"],
     ["Threat modelling", "<b>yes</b>", "re-run on drift",
      "entry points added by a config change, not a commit"],
     ["Tool-schema and MCP surface review", "<b>yes</b>", "<b>yes</b>",
      "a description edited by a server after review"],
     ["DAST / attack simulation", "against a replica", "<b>yes</b>",
      "responses only a live system produces"],
     ["Guardrails and egress enforcement", "config only", "<b>yes</b>",
      "the request that was actually attempted"],
     ["Runtime posture and drift", "no", "<b>yes</b>",
      "a guardrail switched off after the demo \u2014 A3.9"],
     ["Detection and canaries", "no", "<b>yes</b>",
      "somebody using a credential nothing legitimate touches"],
     ["Attestation", "signs the claim", "re-checks it",
      "whether the deployment still matches what was signed"]],
    emphasise=1,
    caption="Read the last column rather than the ticks. It is the sentence "
            "that says what each technique is structurally unable to see, and "
            "it is the one that decides whether two tools are coverage or two "
            "invoices.")),

  *skill_steps("appsec/sdlc-control-placement",
               "## 4 \u00b7 The placement, as a skill\n\nThe table above is a "
               "reference. This is the same question asked of CyberTravels' own "
               "inventory, which is the version that produces an answer somebody "
               "has to do something about.\n\nIt counts three things separately: "
               "how many of the techniques can actually block a merge, which "
               "risks are covered only on the side that can prevent them, and "
               "which only on the side that can merely observe. All three read "
               "as \u201ccovered\u201d on a tooling inventory."),

  ("md", """## 5 \u00b7 What the counts are for

Three numbers come out of that run and each one has a different owner.

**Gate-capable.** Four of ten. Everything else produces a ticket, and a ticket
is a request rather than a control. If your security posture depends on tickets
being worked, it depends on next quarter's headcount.

**Post-only risks.** These are the ones that get signed off in a review,
because a control exists, it runs, and it reports. It reports *afterwards*. The
sign-off is not wrong about the control; it is wrong about what the control
does.

**Uncovered.** One, and it is the subject of B2.7: an artefact in the build with
no manifest entry has no identifier, so the SCA pass on the left never had
anything to look up and the report was clean about it. That is a gap nothing on
either side is currently pointed at."""),
 ],
 "expect": "Four of ten techniques can block a merge; the other six produce "
           "tickets. Two risks are covered only before the deploy \u2014 "
           "preventable, and invisible once shipped \u2014 and three only after "
           "it, where detection is the whole of the control and the merge that "
           "caused it already went through. One is covered by nothing on either "
           "side, and that one is the undeclared vendored binary B2.7 goes "
           "after.",
 "challenge": "Write your own inventory into the same two columns, then delete "
              "every row that is deployed and muted. What is left is your "
              "coverage. The row that will start an argument is the one somebody "
              "believes is preventative and is in the right-hand column.",
},

"C1.0": {
 "concept": """
Traditional security validation relies on deterministic attack paths — exploits
with predictable signatures targeting static software vulnerabilities. The
emergence of autonomous, frontier-scale AI agents introduces a completely novel
threat surface. When an advanced model breaks out of an unisolated container or
coordinates an unauthorised, multi-agent deployment, it does not rely on classic
exploit payloads. Instead, it navigates systems through non-deterministic
reasoning loops, runtime code generation, and rapid tool-use execution.

This function bridges the gap between offensive exploitation and architectural
control engineering. By analysing real-world agentic failures — unisolated data
pipelines, covert multi-sandbox communication relays, and cascading resource
delegation loops — it prepares security researchers to systematically evaluate
the entire machine-learning lifecycle. Red teaming in this paradigm shifts from
simple text-filtering bypasses to auditing the boundaries of machine-speed code
execution, context-window deception, and ephemeral authorisation models.
Conversely, the research component translates these probabilistic discoveries
into rigid defensive telemetry, automated triage playbooks, and structural
engineering policies.

The twelve lessons trace this integrated lifecycle sequentially, moving from
initial ingestion vulnerabilities to active swarm containment and long-term
forensic governance. Every lesson after this one ends in a control the defender
can run — a red team that produces only a slide has produced nothing.
""",
 "steps": [
  ("md", "## 2 · The lifecycle, in order\n\n"
         "Each lesson is a turn of the same loop: reach a surface, weaponise it, "
         "prove it reproduces, then translate it into something the SOC deploys."),
  ("html", D.table(
    ["stage", "the lessons", "what it produces"],
    [["reach", "C1.1-C1.3 ingestion, elicitation",
      "findings on the surfaces an attacker meets first"],
     ["see", "C1.4-C1.6 telemetry, swarms, detection",
      "the signals that make an agent observable"],
     ["respond", "C1.7-C1.9 triage, deception, containment",
      "playbooks that hold at machine speed"],
     ["carry forward", "C1.10-C1.11 forensic replay, governance",
      "reproducible evidence and institutional policy"]],
    caption="Deterministic validation stops at 'reach'. The novelty of an "
            "agentic threat is that the other three stages are where the work "
            "now is.")),

  ("md", "## 3 · Two rows of the CyberTravels register this function owns\n\n"
         "**R7**, where a jailbroken advisor kept its booking tools, and **R8**, "
         "where an agent spawned a child nobody could attribute. Both are red-"
         "team findings first and governance items last."),
 ],
 "expect": "The four stages of the agentic red-team lifecycle, from the "
           "ingestion and elicitation surfaces an attacker reaches first through "
           "to the forensic replay and governance a finding ends in — each stage "
           "producing something the defender can run rather than a transcript.",
 "challenge": "Take one finding you have reported and ask how far along this "
              "lifecycle it travelled. Most stop at 'reach'; the value is in the "
              "three stages after it.",
},

"D1.0": {
 "concept": """
CyberTravels has a SOC. It was built for people.

It watches for a login from an unusual country, a burst of failed
authentications, an employee downloading the customer list on their last day. It
is good at those, and none of them describes CyberTravels.

**An agentic SOC watches a different actor.** One hour of CyberTravels' Workflow
Agent is roughly 1,400 tool calls across 260 resources in 96 sessions. One hour
of Alex is twelve actions. Every threshold, baseline and playbook CyberTravels
owns was tuned against the second number.

And the actor is not only the adversary. It is also the instrument: chapter D2
puts an agent on detection engineering and chapter D3 puts one on the alert
queue. Both work, and both bring the same failure mode — a loop that concludes
confidently can conclude wrongly at machine speed.

### The unit this function is written in

A ratio of 117× is not a fact you can act on. **The unit is an interval**, and
there are five of them between an agent doing something it should not and the
control that stopped it being back at target:

| interval | from | to | chapter |
|---|---|---|---|
| **discover** | the behaviour happens | somebody could see it at all | D1 |
| **detect** | it is visible | an alert exists | D2 |
| **understand** | the alert exists | a conclusion you can act on | D3 |
| **contain** | the conclusion | the actor stopped | D4 |
| **recover** | stopped | the control measurably back at target | D5 |

Every lesson in this function shortens one of those five, or spends one
deliberately to buy something else — and each says which, in a line under its
own concept. The intervals are where the numbers live: CyberTravels' detection
interval is 194 minutes against a 15-minute target, and its manual containment
runbook finishes in 34 minutes against a measured breakout time of 29. Neither
of those is an opinion about tooling.

### The stack that runs it

Nothing in this function needs a product you do not have. Every phase below has
a working open-source reference, and the lessons are written against these
rather than against a vendor's diagram — so you can build the whole thing and
find out what it does not cover, which is the part that matters.

| phase | what has to exist | open source that does it |
|---|---|---|
| **discover** | endpoint and workload sensing | **Wazuh** (agent, manager, indexer) |
| | cloud posture, on a schedule | **Prowler**, **ScoutSuite** |
| | container runtime and image contents | **Falco**, **Trivy** |
| | sensitive content in motion | regex plus Wazuh file integrity monitoring |
| | **agent** traces — prompts, tools, decisions | **OpenTelemetry**, instrumented at the gateway |
| **detect** | somewhere for all of it to land | **OpenSearch** (or the Wazuh indexer) |
| | rules, portable and reviewable | **Sigma**, mapped to **ATT&CK** and **ATLAS** |
| | deception with no threshold | canary tokens and honeypot tasks you write |
| **understand** | third-party intelligence | **MISP**, **OpenCTI** |
| | correlation and hunting | notebooks over the lake |
| | case management | **TheHive**, enrichment via **Cortex** |
| **respond** | orchestration and runbooks | **Shuffle** |
| | revocation | your own IdP and gateway, driven from the runbook |
| **recover** | host and memory forensics | **Velociraptor** |
| | run replay | the harness from B2.1, pinned per D5.1 |

Two honest notes about that table.

**The DLP row is the weakest.** There is no open-source DLP with the maturity of
the other three, which is why the row names a pattern rather than a product —
and why D1.1 scores DLP at almost no coverage of an agent's day. That is a real
finding about the market, not a gap in the reading.

**The agent-telemetry row does not exist in any of the products.** Wazuh will
tell you a process wrote a file. Nothing in the list tells you which prompt
caused it. That row is instrumentation you write, it lands in the lake D2.1
designs, and its absence is what D1.1 measures.

### The five chapters

**D1 — discover.** The four sensor classes you already own, scored against what
an agent actually does; drift, the failure with no adversary at all; and a bonus
on finding the agents nobody registered and keeping what they emit.

**D2 — detect.** The lake every rule is written against, then detections for two
subjects that are not the same subject — the agent, and the platform running it
— mapped to ATT&CK and ATLAS, plus the loop that writes rules, the benign corpus
that decides whether they ship, and the one detector that needs no threshold.

**D3 — understand.** An investigation an agent can run: bounded before it
starts, given the fields an agent alert needs, willing to abandon its first
theory in the open, scoped along the delegation graph, widened to the
population — and then the two proactive halves, third-party intelligence that
has to become a rule and a hunt for behaviour no rule covers.

**D4 — respond.** A response whose blast radius is known before it fires.
Actions classified on reversibility and radius, tiers derived from that rather
than from their author, containment timed against the attacker, and a fleet stop
that revokes as well as terminates.

**D5 — recover and root cause.** A run you can reproduce, a root cause that
names a control rather than a person, the fix put at the layer it belongs in,
the indicators re-measured to see which actually came back — and a regulatory
clock that started before anyone knew.

Two rows of the CyberTravels register are this function's whole reason to exist:
**R9**, where holding one agent reaches CRM, payroll and the cloud resource
manager, and **R10**, where passport numbers are in the logs that would have
told you.
""",
 "steps": [
  ("md", "## 2 · One hour of CyberTravels, one hour of Alex"),
  ("html", D.table(
    ["signal, over one hour", "Alex", "CyberTravels' Workflow Agent", "ratio"],
    [["actions taken", "12", "1,400", "117×"],
     ["distinct resources touched", "5", "260", "52×"],
     ["median gap between calls", "180s", "2s", "1/90×"],
     ["sessions", "1", "96", "96×"],
     ["typo / retry events", "3", "0", "—"]],
    emphasise=3,
    caption="Every detection, baseline and playbook CyberTravels owns was tuned "
            "against the second column.")),

  ("md", "## 3 · Why a volume rule is not the answer\n\n"
         "The obvious rule does fire. The problem is *when* — which is the one "
         "thing a table cannot show you, so this part is worth running."),

  ("md", "## 4 · What CyberTravels has to emit before any of this works"),
  ("html", D.table(
    ["what the SOC needs", "is it in an application log?", "which lesson gets it"],
    [["the prompt that motivated the action", "<b>no</b>", "D1.3"],
     ["the tool call, with arguments", "<b>no</b>", "D1.3"],
     ["the decision, and what it was based on", "<b>no</b>", "D5.1"],
     ["which agent acted", "<b>no</b>", "D1.3"],
     ["which human it acted for", "<b>no</b>", "A2.7 · D1.3"],
     ["the HTTP request the tool made", "yes", "already there"]],
    emphasise=1,
    caption="Five of six do not exist yet. R10 in the register is the sixth "
            "one's twin problem — the log you do have is full of passport "
            "numbers.")),
   *skill_steps('detection/agent-tempo-baseline',
               "## 2 · The procedure, as a skill\n\nAlex and CyberTravels' Workflow Agent, over the same hour. The skill measures the five signals that separate them, then runs the existing volume rule against the agent's run — where it fires 154 seconds in and stays silent for the remaining fifty-seven minutes."),
],
 "expect": "Five behavioural signals for Alex and for CyberTravels' Workflow Agent "
           "over the same hour, with ratios in the hundreds. The volume rule "
           "tuned for human tempo does fire — 154 seconds into a sixty-minute "
           "run, leaving 3,446 seconds unmonitored. Five of the six things an "
           "agentic SOC needs are not in any application log.",
 "challenge": "Pull one hour of activity for a service account in your own "
              "environment and compute those five signals. If you cannot, that "
              "is the first finding of chapter 8 and it is a telemetry problem "
              "rather than a detection one.",
},

"E1.0": {
 "concept": """
Someone at CyberTravels signed off on the platform. Function E is about whether
that signature still means anything.

It has to, because the sign-off happened when CyberTravels was a chatbot. It now
issues refunds, writes code, reads invoices and indexes contracts. Nothing about
the approval was wrong on the day; everything about it is stale, and the
approval process has no step that notices.

**Governing autonomy rather than approving tools** is the shift. A list of
approved products works at forty products. CyberTravels will not stop at four
agents, and neither will the list.

The vocabulary is **trustworthy AI**, and it is worth being precise about,
because it is used loosely everywhere else. Seven properties, and not one of
them belongs to a single team:

| property | what it means for CyberTravels |
|---|---|
| valid and reliable | it recommends hotels that exist, repeatably, and somebody measured that |
| safe | a wrong recommendation does not become a $5,000 refund |
| secure and resilient | it withstands the twelve risks in the register, and recovers |
| accountable and transparent | a named person owns it, and its actions are visible |
| explainable | the reason it issued a refund can be recovered afterwards |
| privacy-enhanced | passport numbers do not end up in a log or a vector store |
| fair, harmful bias managed | it does not quietly serve some travellers worse |

Security owns one of the seven outright. That ratio is the whole reason this
function exists as more than a security document.

Contributing evidence to six properties you do not own only works if the
evidence is in a form the other six owners can use, which is why the whole of
Function E is written in one unit: a **key control indicator**. E1.1 defines it
— a number computed from the estate, with a denominator, and a target set before
the measurement is taken — and the three chapters are that one unit built,
evidenced and run:

- **Chapter E1 — risk and control.** Where the indicators come from. The
  register supplies the denominator, risk tiering supplies the target, control
  mapping supplies the subject, and E1.13 computes six of them against the
  CyberTravels repository and reports the gaps.
- **Chapter E2 — regulatory and compliance.** The same indicators read as
  evidence. A travel company holds passports, payment data and health
  information, and each regime asks for a reading rather than a description —
  quotable to several of them because it was computed once.
- **Chapter E3 — the CISO office.** The indicators run as a programme:
  sequenced by distance from target, owned by name, and reported to a board in
  numbers somebody in the room can re-compute.

Every lesson in this function carries a line under its concept saying what it
contributes to that indicator or takes from it. Where a lesson looks like it
belongs to a different argument, that line is the place to check.

Two rows of the register belong to this function outright: **R2**, where a
guardrail was disabled for a demo and nobody had to approve it, and **R12**,
where contracts were indexed for better answers and became searchable by
contractors.
""",
 "steps": [
  ("md", "## 2 · Seven properties, and who at CyberTravels owns each"),
  ("html", D.table(
    ["trustworthy-AI property", "who owns it at CyberTravels", "security's share"],
    [["valid and reliable", "engineering + the eval harness (B2.19)",
      "contributes evidence"],
     ["safe", "the CyberTravels product owner + risk", "contributes evidence"],
     ["secure and resilient", "security", "<b>owns it</b>"],
     ["accountable and transparent", "the named system owner",
      "contributes evidence"],
     ["explainable and interpretable", "engineering + model risk",
      "contributes evidence"],
     ["privacy-enhanced", "privacy office + engineering", "contributes evidence"],
     ["fair, harmful bias managed", "product owner + legal",
      "contributes evidence"]],
    emphasise=2,
    caption="Security owns one of the seven and contributes evidence to the "
            "other six. A trustworthy-AI statement with no owner per property is "
            "a statement that every property is somebody else's job.")),

  ("md", "## 3 · What the sign-off actually covered\n\n"
         "The approval was accurate when it was given. This is what changed "
         "underneath it, and which of those changes raised a ticket."),
  ("html", D.table(
    ["at approval", "today", "did it go through change management?"],
    [["one agent, answers questions", "four agents", "<b>no</b>"],
     ["read-only", "issues refunds", "<b>no</b>"],
     ["no repository access", "opens and self-approves pull requests",
      "<b>no</b>"],
     ["no document store", "indexes contracts and pricing models", "<b>no</b>"],
     ["hosted model, fixed version", "provider upgrades it silently",
      "<b>no — you may not be told</b>"]],
    emphasise=2,
    caption="Five material changes, none of them ticketed. This is R2 and the "
            "lifecycle problem of E1.9 in one table, and it is why chapter 10 "
            "starts with an inventory rather than a policy.")),

  ("md", "## 4 · Three distances from the same question"),
  ("html", D.svg(D.DEFS
    + D.box(6, 14, 218, 84, "chapter 10", sub="risk and control", colour=D.INK)
    + D.label(115, 62, "inventory · tiering", anchor="middle")
    + D.label(115, 78, "mapping · evidence", anchor="middle")
    + D.box(242, 14, 218, 84, "chapter 11", sub="regulatory", colour=D.INK)
    + D.label(351, 62, "obligations · documentation", anchor="middle")
    + D.label(351, 78, "supervision", anchor="middle")
    + D.box(478, 14, 216, 84, "chapter 12", sub="the CISO office", colour=D.INK)
    + D.label(586, 62, "sequencing · org design", anchor="middle")
    + D.label(586, 78, "metrics · stop authority", anchor="middle")
    + D.arrow(224, 56, 240) + D.arrow(460, 56, 476)
    + D.label(350, 124, "inside CyberTravels  →  to a regulator  →  to the board",
              anchor="middle", size=11.5),
    height=140)),
 ],
 "expect": "Seven trustworthy-AI properties with a named owner each and security "
           "owning exactly one outright. Five material changes to CyberTravels since "
           "its approval, none of which raised a ticket. The three chapters laid "
           "out by how far from the system each one sits.",
 "challenge": "Find the approval record for one agent you run and compare it to "
              "what that agent does today. The gap is the programme, and the "
              "reason nobody noticed it is what chapter 10 is for.",
},

}
