"""The five function introductions — one per function, before its first chapter.

Each answers the same question for its own function: what is this part of the
commons for, which of the two directions does it run in, and what will you be
able to do at the end of it. They are deliberately short: one framework, one
small piece of code that makes the framework concrete, and no risk material —
the risks start in the chapter that follows.
"""

from . import cybertravels as CT
from . import diagrams as D

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

So this function is one picture and its consequences, in three chapters:

- **Chapter 1 — the architecture, and every risk it carries.** The component
  map, then one lesson per risk, each naming the component of CyberTravels it
  attacks and grounded in the OWASP Agentic AI threat taxonomy.
- **Chapter 2 — securing it: identity and ingress.** Who is calling, on whose
  behalf, and what came in from outside. These two controls close more of
  CyberTravels' risks than anything else, which is why they come first.
- **Chapter 3 — securing it: runtime and the gateway.** What holds after
  identity has been defeated, and how the controls collapse into one enforcement
  point once CyberTravels runs more than four agents.

> The CyberTravels narrative, the six risk families and the twelve-row register
> used throughout this commons are from *Agentic AI is rising fast — but the
> attack surface is exploding*, Karthik Ramamoorthy, May 2025. The mapping onto
> lessons, the controls and all of the code are this commons'.
""",
 "steps": [
  ("md", "## 2 · CyberTravels, as built"),
  ("html", CT.ARCHITECTURE),

  ("md", "## 3 · The four agents, and what each one can reach"),
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

  ("md", "## 4 · Where the five functions sit\\n\\n"
         "Each one takes the same system and asks a different question of it."),
  ("html", D.table(
    ["function", "the question it asks of CyberTravels", "direction"],
    [["A", "what can go wrong here, and what closes it", "mostly Security of AI"],
     ["B", "how do we review its code, at its speed", "both directions at once"],
     ["C", "can we break it before somebody else does", "both directions at once"],
     ["D", "would we see it happening, and could we stop it",
      "both directions at once"],
     ["E", "who signed off, and can they still evidence it",
      "governs both directions"]],
    caption="Nobody takes all five. Everyone takes the common spine first, then "
            "the chapters for the chair they sit in, then one adjacent chapter.")),

  ("md", "## 5 · What the other four borrow from this one\\n\\n"
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
    caption="Chapter 1 introduces no control at all, on purpose: you cannot "
            "choose a control for a risk you cannot yet name.")),

  ("md", "## 4 · Function A, in order"),
  ("html", D.table(
    ["chapter", "what it covers", "lessons"],
    [["1", "the architecture, and every risk it carries", "17"],
     ["2", "securing it — identity and ingress", "8"],
     ["3", "securing it — runtime and the gateway", "10"]],
    caption="Chapters 2 and 3 are controls. Chapter 1 is the picture they "
            "stand on.")),
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

"B1.0": {
 "concept": """
CyberTravels has a problem that is not about its users. It is about its own
code.

The Coding Agent opens pull requests. Some of them touch a hundred files. Alex
is one engineer, the release cadence has not slowed down, and the review that
used to be a careful hour is now a scroll. Function B is what he builds instead
of scrolling: **an SDLC in which agents do the reviewing**, and the harnesses
that make their output worth acting on.

Both directions of this commons meet here, on the same system.

**AI for Security.** A pipeline that ingests the CyberTravels repository, models its
threats, audits for vulnerabilities, confirms the real ones by exploiting them
in a replica, engineers the fix and reports a severity somebody acts on. That
is chapter 4, built stage by stage as one artefact.

**Security of AI.** That pipeline is itself an agentic system with all of
CyberTravels' risks. It reads untrusted input by definition — the code it reviews is
the code nobody trusts yet. It holds a credential that can write to the default
branch. Every risk in Function A applies to it, and being a security tool grants
no exemption.

Chapter 5 asks the question chapter 4 cannot ask of itself: **is any of this
worth acting on?** The pipeline is a harness — a model with a loop, tools, a
context, a verifier, state, budgets, an orchestrator and telemetry around it —
and four things decide whether Alex can leave it running:

1. **what a harness actually is**, because most arguments about agent
   reliability turn out to be arguments about which of those eight parts is
   missing, and the missing one is almost always the verifier;
2. **evaluation**, on a corpus whose answers you already know, because a
   hallucinated finding looks exactly like a real one until something checks;
3. **reliability and cost**, because a harness that is right 80% of the time is
   33% reliable across five unattended runs, and somebody is paying per finding;
4. **deception**, because a canary in the pipeline's own environment is the one
   detection with no false positives — nothing legitimate ever touches it.

Then the awkward part: **that pipeline is itself an agentic system with all of
CyberTravels' risks.** It reads untrusted input by definition and holds a
credential that can write to the default branch. Chapter 4 closes on exactly
that (A1.9, B1.12), because being a security tool grants no exemption.
""",
 "steps": [
  ("md", "## 2 · What Alex is actually up against"),
  ("html", D.table(
    ["", "before the Coding Agent", "after"],
    [["pull requests per week", "6", "<b>40</b>"],
     ["files touched per PR", "3", "<b>up to 120</b>"],
     ["review time available", "unchanged", "unchanged"],
     ["what review becomes", "reading", "<b>scrolling</b>"],
     ["what gets through", "the occasional bug",
      "<b>an IDOR that exposes card details by booking ID</b>"]],
    emphasise=2,
    caption="Nothing in the left column was wrong. The volume changed and the "
            "review process did not, which is the whole argument for building "
            "the pipeline in chapter 4.")),

  ("md", "## 3 · Chapter 4 — the lifecycle, with agents doing the work"),
  ("html", D.svg(D.DEFS
    + D.box(2, 26, 96, 46, "ingest", sub="B1.1-2", colour=D.DEFEND)
    + D.box(112, 26, 116, 46, "threat model", sub="B1.2-4", colour=D.DEFEND)
    + D.box(242, 26, 92, 46, "audit", sub="B1.3-7", colour=D.DEFEND)
    + D.box(348, 26, 104, 46, "confirm", sub="B1.6-10", colour=D.DEFEND)
    + D.box(466, 26, 108, 46, "remediate", sub="B1.9", colour=D.DEFEND)
    + D.box(588, 26, 96, 46, "report", sub="B1.10", colour=D.DEFEND)
    + "".join(D.arrow(a, 49, a + 12) for a in (99, 229, 335, 453, 575))
    + D.box(2, 108, 682, 52, "", colour=D.INK, dashed=True)
    + D.label(343, 130, "chapter 5 — the harness underneath every one of those stages",
              anchor="middle", colour=D.INK, size=12, weight="600")
    + D.label(343, 148, "plan · act · verify · stop  ·  tools · budgets · replay  ·  "
                        "one skeleton, four oracles  ·  evals · cost",
              anchor="middle"),
    height=178,
    caption="Chapter 4 is a product built out of chapter 5's material. Alex "
            "needs the product; he cannot ship it without the material.")),

  ("md", "## 4 · The harnesses, in the order you have to build them\n\n"
         "Each row is a thing CyberTravels needs and a chapter-5 lesson that "
         "builds it. The order is not preference — each one is unusable without "
         "the one above it."),
  ("html", D.table(
    ["question", "what it decides for CyberTravels", "answered in"],
    [["what a harness even is",
      "which of the eight parts the pipeline actually has — and the one nobody "
      "can name is almost always the verifier", "B2.0"],
     ["is its output true",
      "recall and precision against a corpus whose answers you already know, "
      "because a hallucinated finding looks exactly like a real one", "B2.1"],
     ["can it be left alone",
      "pass^k across a run nobody watched, and dollars per confirmed finding",
      "B2.2"],
     ["would you know if it were attacked",
      "canaries and honeypot tasks in CyberTravels' own environment — the "
      "detection with no false positives", "D1.11"]],
    emphasise=2,
    caption="Skip to evaluation and you will measure a harness whose verifier "
            "you never built. That is the most common way this goes wrong.")),

  ("md", "## 5 · The same pipeline, read as an agentic system\n\n"
         "Every stage above runs inside something that has an identity, reads "
         "untrusted input and writes to CyberTravels' repository. These are "
         "Function A's components, and a security tool gets no exemption."),
  ("html", D.table(
    ["Function A component", "what it is, in this pipeline"],
    [["ingress", "a pull request, opened by CyberTravels' own Coding Agent"],
     ["knowledge", "the CyberTravels repository — untrusted by definition"],
     ["tools", "the test runner, the sandbox replica, the ticket API"],
     ["identity", "a service account that can write to the default branch"],
     ["egress", "the report, and anything it happens to contain"]],
    caption="Five components, every one of them a risk surface from Function A. "
            "R7 and R8 in the CyberTravels register are exactly this pipeline "
            "going wrong.")),
 ],
 "expect": "The volume problem stated plainly — 6 pull requests a week becoming "
           "40, touching up to 120 files, with review time unchanged — then the "
           "five phases of the lifecycle, the seven harnesses in the order they "
           "have to be built, and the same pipeline read back as an agentic "
           "system with five Function A components.",
 "challenge": "Count your own numbers for the first table: pull requests per "
              "week before and after, files touched, and review minutes "
              "available. If the third number has not moved, you are already in "
              "the situation this function is for.",
},

"C1.0": {
 "concept": """
CyberTravels' security team has a standing question from the board, and it is
not "is CyberTravels secure". It is **"how would we know"**.

Function C answers it twice. Chapter 6 attacks CyberTravels the way somebody else
eventually will. Chapter 7 asks whether what you found survives contact with
a second person, a second week and a second model.

**Chapter 6 — red teaming.** The agent as your instrument first: recon,
foothold, escalation and lateral movement run as a loop, inside a scope you can
defend in writing — because an offensive harness pointed at CyberTravels'
staging estate is the most dangerous thing in the building. Then the agent as
the target: CyberTravels has three attack surfaces and a campaign has to cover all
three.

- **injection** — what the Workflow Agent reads. A booking note, a hotel
  description, an OCR'd invoice. R3 in the register.
- **identity** — who it acts as. Delegation from Alex, scope, expiry,
  impersonation. R1, R5 and R11.
- **containment** — what it can reach once you hold it. The refund endpoint,
  the CRM, the CI runner, Alex's laptop. R6, R7 and R9.

**Chapter 7 — research.** Model-layer, weight-level, data-layer and supply-chain
work, then the two questions that decide whether any of it was worth doing.
Does it reproduce once you separate the model effect from the harness effect?
And can somebody else deploy it as a control after you have moved on?

The chapter closes on three real incidents, because the most useful red-team
finding is often one that already happened to somebody else — including one
where a swarm of agents compromised a third party's production systems, which is
the shape of a bad week CyberTravels has not had yet.

One idea holds all of it together: **an anecdote is not a result.** "CyberTravels
refunded a booking when I asked it to" is a story. "7 of 20 attempts, 0 of 20
against the patched build, reproduced by the platform team" is a finding
somebody can act on.
""",
 "steps": [
  ("md", "## 2 · CyberTravels' three attack surfaces"),
  ("html", D.svg(D.DEFS
    + D.box(268, 8, 164, 44, "CyberTravels", colour=D.INK)
    + D.box(6, 108, 206, 84, "injection", colour=D.SECURE,
            sub="what it reads")
    + D.label(109, 158, "booking notes · hotel copy", anchor="middle")
    + D.label(109, 173, "OCR'd invoices · templates", anchor="middle")
    + D.box(246, 108, 208, 84, "identity", colour=D.SECURE,
            sub="who it acts as")
    + D.label(350, 158, "delegation from Alex", anchor="middle")
    + D.label(350, 173, "scope · expiry · lineage", anchor="middle")
    + D.box(488, 108, 206, 84, "containment", colour=D.SECURE,
            sub="what it can reach")
    + D.label(591, 158, "refunds · CRM · CI runner", anchor="middle")
    + D.label(591, 173, "the local filesystem", anchor="middle")
    + D.arrow(320, 52, 130, 104) + D.arrow(350, 52, 350, 104)
    + D.arrow(380, 52, 570, 104),
    height=206,
    caption="Nine of the twelve risks in the CyberTravels register land on one "
            "of these three. A campaign that covers one surface has covered a "
            "third of the register and will read as though it covered all of "
            "it.")),

  ("md", "## 3 · The same claim, at four standards of proof\n\n"
         "Chapter 6 gets you to the second row. Chapter 7 is entirely about the "
         "third and fourth, because a finding nobody can reproduce protects "
         "nobody — however true it was on the day."),
  ("html", D.table(
    ["what the report says about CyberTravels", "rate", "control arm", "reproduced",
     "what it is"],
    [["it refunded a booking when I asked it to", "—", "—", "—",
      "<b>anecdote</b>"],
     ["7 of 20 attempts, suite attached", "yes", "—", "—", "<b>measurement</b>"],
     ["7/20, and 0/20 against the patched build", "yes", "yes", "—",
      "<b>result</b>"],
     ["7/20, 0/20 patched, platform team got the same", "yes", "yes", "yes",
      "<b>evidence</b>"]],
    emphasise=4)),
 ],
 "expect": "CyberTravels' three attack surfaces, with the parts of the platform that "
           "sit behind each, and nine of twelve register risks landing on one of "
           "them. Then the same claim graded as anecdote, measurement, result or "
           "evidence depending on whether it carries a rate, a control arm and "
           "an independent reproduction.",
 "challenge": "Take the last security claim anyone made about an agent you run "
              "and score it on those three columns. Most claims — including "
              "vendor ones — sit on the first row.",
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

And the actor is not only the adversary. It is also the instrument: chapter 8
puts an agent on the alert queue and on detection engineering, which works, and
brings its own failure mode — a loop that closes alerts confidently can close
the wrong one at machine speed.

**Chapter 8 — detection.** Triage as a loop you supervise, with the context that
makes it correct. Detections written *for* an actor with no human rhythm.
CyberTravels' telemetry as a first-class data source, because you cannot detect on
what was never emitted — prompts, tool calls, decisions, identities, none of
which appear in an application log. Telling agent from human when both hold
Alex's authority. And drift, the failure with no adversary at all: the model was
upgraded, a prompt was edited, and the baseline moved.

**Chapter 9 — response.** Scope an incident whose actor moved at machine speed
on delegated credentials. Contain faster than it acts. Replay what it saw and
what it decided. And decide, in advance, who is allowed to stop all four agents
at three in the morning without asking anyone.

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
  ("py", '''def burst_rule(actions_per_hour, threshold=60):
    return actions_per_hour > threshold

RATE = {"Alex": 12, "workflow agent": 1400}
for who, n in RATE.items():
    print(f"   {who:16s}{n:>6} actions/hour -> "
          f"{'ALERT' if burst_rule(n) else 'silent'}")

seconds_to_trip = 60 * 3600 / RATE["workflow agent"]
print(f"\\nthe agent crosses the threshold after {seconds_to_trip:.0f} seconds")
print(f"and keeps going for the remaining {3600 - seconds_to_trip:.0f}.")
print()
print("So the rule fires, about two and a half minutes into a sixty-minute run -")
print("by which point most of what the actor was going to do is done. If those")
print("were refunds, the alert arrives after the money has moved.")
print()
print("Chapter 8 is about detections that fire on shape rather than volume.")
print("Chapter 9 is about who can pull the stop lever without asking.")
assert burst_rule(1400) and not burst_rule(12) and seconds_to_trip < 200
'''),

  ("md", "## 4 · What CyberTravels has to emit before any of this works"),
  ("html", D.table(
    ["what the SOC needs", "is it in an application log?", "which lesson gets it"],
    [["the prompt that motivated the action", "<b>no</b>", "D1.5"],
     ["the tool call, with arguments", "<b>no</b>", "D1.5"],
     ["the decision, and what it was based on", "<b>no</b>", "D2.5"],
     ["which agent acted", "<b>no</b>", "D1.6"],
     ["which human it acted for", "<b>no</b>", "A2.7 · D1.6"],
     ["the HTTP request the tool made", "yes", "already there"]],
    emphasise=1,
    caption="Five of six do not exist yet. R10 in the register is the sixth "
            "one's twin problem — the log you do have is full of passport "
            "numbers.")),
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
function exists as more than a security document, and three chapters follow
from it:

- **Chapter 10 — risk and control.** The register of every agent CyberTravels
  runs, risk-tiered by autonomy, data and blast radius, mapped to controls, with
  evidence that can be re-checked rather than asserted once.
- **Chapter 11 — regulatory and compliance.** What CyberTravels owes and to
  whom. A travel company holds passports, payment data and health information;
  layer 2 and 3 obligations were in force before CyberTravels existed.
- **Chapter 12 — the CISO office.** Sequencing, org design, metrics, and how to
  tell the board what the exposure is without either alarming them or misleading
  them.

Two rows of the register belong to this function outright: **R2**, where a
guardrail was disabled for a demo and nobody had to approve it, and **R12**,
where contracts were indexed for better answers and became searchable by
contractors.
""",
 "steps": [
  ("md", "## 2 · Seven properties, and who at CyberTravels owns each"),
  ("html", D.table(
    ["trustworthy-AI property", "who owns it at CyberTravels", "security's share"],
    [["valid and reliable", "engineering + the eval harness (B2.1)",
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
