"""The five function introductions — one per function, before its first chapter.

Each answers the same question for its own function: what is this part of the
commons for, which of the two directions does it run in, and what will you be
able to do at the end of it. They are deliberately short: one framework, one
small piece of code that makes the framework concrete, and no risk material —
the risks start in the chapter that follows.
"""

from . import diagrams as D

EXERCISES: dict[str, dict] = {

"A1.0": {
 "concept": """
Everything in Cyber Commons runs in one of two directions, and Function A is
almost entirely the second one.

**AI for Security** — the agent is your instrument. It reviews code, triages
alerts, reconstructs an incident. The thing you are protecting is the business,
and the agent is a tool that got fast.

**Security of AI** — the agent is the thing you are protecting. It has an
identity, a set of permissions, a memory, a network path, and an attacker who is
interested in all four.

**Securing an AI architecture is the whole of the second direction, taken at
the layer everything else sits on.** You cannot secure a system you cannot draw.
"Secure the agent" is not an instruction; it becomes one only once you can say
*which component* and *which boundary*.

So this function is one picture and its consequences, in three chapters:

- **Chapter 1 — the architecture, and every risk it carries.** One
  vendor-neutral component map, then one lesson per risk, each naming the
  component it attacks and grounded in the OWASP Agentic AI threat taxonomy.
- **Chapter 2 — securing it: identity and ingress.** Who is calling, on whose
  behalf, and what came in from outside. These two controls close more risks
  than anything else, which is why they come first.
- **Chapter 3 — securing it: runtime and the gateway.** What holds after
  identity has been defeated, and how the controls collapse into one enforcement
  point once you run more than a handful of agents.

Everything downstream names a component from chapter 1. The AI SDLC in Function
B is an agentic system with all of these risks. The red-team campaign in
Function C attacks these components. The detections in Function D watch them.
The control register in Function E lists them.
""",
 "steps": [
  ("md", "## 2 · Where the five functions sit"),
  ("html", D.table(
    ["function", "covers", "direction it runs in"],
    [["A", "Securing AI architectures", "mostly Security of AI"],
     ["B", "Application security with an AI SDLC", "both directions at once"],
     ["C", "Red teaming and security research with AI", "both directions at once"],
     ["D", "AI for SecOps", "both directions at once"],
     ["E", "AI for GRC", "governs both directions"]],
    caption="Nobody takes all five. Everyone takes the common spine first, then "
            "the chapters for the chair they sit in, then one adjacent chapter.")),

  ("md", "## 3 · What the other four borrow from this one\\n\\n"
         "Not a claim about tidiness. It is why the map has to come first: every "
         "later function names a component from it."),
  ("html", D.svg(D.DEFS
    + D.box(240, 10, 220, 48, "chapter 1", sub="the component map", colour=D.SECURE)
    + D.box(6, 124, 158, 66, "Function B", sub="the SDLC is itself an agent")
    + D.box(180, 124, 158, 66, "Function C", sub="its 3 surfaces are here")
    + D.box(354, 124, 158, 66, "Function D", sub="these emit the telemetry")
    + D.box(528, 124, 166, 66, "Function E", sub="the register lists these")
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
 "expect": "A map of the five functions, the direction each runs in, and what "
           "each of the other four borrows from Function A's component map. "
           "Function A itself is three chapters: the architecture and its risks, "
           "then identity and ingress, then runtime and the gateway.",
 "challenge": "Before the next lesson, write down the components of one agentic "
              "system you already run — even as a list of nouns. A1.1 gives you "
              "the standard names; comparing your list to it is the fastest way "
              "to find the component you forgot you had.",
},

"B1.0": {
 "concept": """
Function B rebuilds the **secure development lifecycle** around agents, and it
is where both directions meet on the same system.

**AI for Security.** An SDLC in which agents do the work: ingest a codebase,
model its threats, audit for vulnerabilities, confirm the real ones by
exploiting them in a sandbox, engineer the remediation, and report with a
severity somebody can act on. That is chapter 4, built stage by stage as one
artefact.

**Security of AI.** That pipeline is itself an agentic system. It reads
untrusted input by definition — the code it reviews is the code you do not yet
trust. It holds credentials. It writes to your repository. Every risk in
Function A applies to it, and the fact that it is a *security* tool grants no
exemption.

Underneath it sits the second chapter: **the harness**. Chapter 5 is the loop —
plan, act, verify, stop — and the engineering that makes it reliable enough to
leave alone: tool design, failure taxonomies, replay, evaluation, and the two
numbers that decide whether autonomy is worth paying for.

The relationship is the point. Chapter 4 is a product built out of chapter 5's
material. If you only read one, read the one you are being asked to ship.
""",
 "steps": [
  ("md", "## 2 · Chapter 4 — the lifecycle, with agents doing the work"),
  ("html", D.svg(D.DEFS
    + D.box(2, 26, 96, 46, "ingest", sub="B1.1-2", colour=D.DEFEND)
    + D.box(112, 26, 116, 46, "threat model", sub="B1.3-4", colour=D.DEFEND)
    + D.box(242, 26, 92, 46, "audit", sub="B1.5-7", colour=D.DEFEND)
    + D.box(348, 26, 104, 46, "confirm", sub="B1.8-10", colour=D.DEFEND)
    + D.box(466, 26, 108, 46, "remediate", sub="B1.11", colour=D.DEFEND)
    + D.box(588, 26, 96, 46, "report", sub="B1.12", colour=D.DEFEND)
    + "".join(D.arrow(a, 49, a + 12) for a in (99, 229, 335, 453, 575))
    + D.box(2, 108, 682, 52, "", colour=D.INK, dashed=True)
    + D.label(343, 130, "chapter 5 — the harness underneath every one of those stages",
              anchor="middle", colour=D.INK, size=12, weight="600")
    + D.label(343, 148, "plan · act · verify · stop  ·  tool design  ·  failure "
                        "taxonomy  ·  replay  ·  evals", anchor="middle"),
    height=178,
    caption="Chapter 4 is a product built out of chapter 5's material. If you "
            "only read one, read the one you are being asked to ship.")),

  ("md", "## 3 · The same lifecycle, read as an agentic system\\n\\n"
         "Every stage above runs inside something that has an identity, reads "
         "untrusted input and writes to your repository. These are Function A's "
         "components, and a security tool gets no exemption from them."),
  ("html", D.table(
    ["Function A component", "what it is, in this pipeline"],
    [["ingress", "a pull request, written by anyone with commit access"],
     ["knowledge", "the repository itself — untrusted by definition"],
     ["tools", "the test runner, the sandbox, the ticket API"],
     ["identity", "a service account that can write to your default branch"],
     ["egress", "the report, and anything it happens to contain"]],
    caption="Five components, every one of them a risk surface from Function A.")),
 ],
 "expect": "The five phases of the lifecycle against the lessons that build "
           "them, the harness capabilities underneath them, and the same "
           "pipeline read back as an agentic system with five Function A "
           "components — ingress, knowledge, tools, identity and egress.",
 "challenge": "Name the service account your existing CI security tooling runs "
              "as, and what it can write to. That account is the identity "
              "component of an agentic system whether or not anyone has called "
              "it one.",
},

"C1.0": {
 "concept": """
Function C is red teaming and research, and it is the smallest function in the
commons with the strictest standard of proof.

Two chapters, and one idea holding them together: **an anecdote is not a
result.**

**Chapter 6 — red teaming.** The agent as your instrument, running recon,
foothold, escalation and lateral movement inside a scope you can defend in
writing. Then the agent as the target: red-teaming it across its three attack
surfaces — injection, identity and containment — as a campaign that reports a
rate with a sample size rather than a screenshot.

**Chapter 7 — research.** Model-layer, weight-level, data-layer and
supply-chain work, then the two questions that decide whether any of it is worth
having. Does it reproduce, once you separate the model effect from the harness
effect? And can somebody else deploy it as a control after you have moved on?

Both directions run through here at once, and unusually they run through the
*same* artefact. The harness you attack with is the harness someone will attack.
The scope guard that keeps your engagement lawful is the containment control
Function A teaches. Offensive work on agents is the shortest path to
understanding the defences, which is why this function sits after A and B rather
than before them.
""",
 "steps": [
  ("md", "## 2 · The three surfaces chapter 6 tests"),
  ("html", D.svg(D.DEFS
    + D.box(268, 8, 164, 44, "the agent", colour=D.INK)
    + D.box(6, 108, 206, 74, "injection", colour=D.SECURE,
            sub="what it reads")
    + D.label(109, 158, "direct · indirect · via tool output", anchor="middle")
    + D.box(246, 108, 208, 74, "identity", colour=D.SECURE,
            sub="who it acts as")
    + D.label(350, 158, "delegation · scope · expiry", anchor="middle")
    + D.box(488, 108, 206, 74, "containment", colour=D.SECURE,
            sub="what it can reach")
    + D.label(591, 158, "tools · paths · egress", anchor="middle")
    + D.arrow(320, 52, 130, 104) + D.arrow(350, 52, 350, 104)
    + D.arrow(380, 52, 570, 104),
    height=196,
    caption="A campaign covers all three and scores them the same way. A demo "
            "covers whichever one was interesting that week.")),

  ("md", "## 3 · The same claim, at four standards of proof\\n\\n"
         "Chapter 6 gets you to the second row. Chapter 7 is entirely about the "
         "third and fourth, because a finding nobody can reproduce protects "
         "nobody, however true it was on the day."),
  ("html", D.table(
    ["the claim", "rate", "control arm", "reproduced", "what it is"],
    [["it worked when I tried it", "—", "—", "—", "<b>anecdote</b>"],
     ["7 of 20 attempts, suite attached", "yes", "—", "—", "<b>measurement</b>"],
     ["7/20, and 0/20 on the patched build", "yes", "yes", "—", "<b>result</b>"],
     ["7/20, 0/20 patched, another team got the same", "yes", "yes", "yes",
      "<b>evidence</b>"]],
    emphasise=4)),
 ],
 "expect": "The three attack surfaces of an agent, and the same claim graded as "
           "anecdote, measurement, result or evidence depending on whether it "
           "carries a rate, a control arm and an independent reproduction.",
 "challenge": "Find the last agentic security claim you read — a blog post, a "
              "vendor page, a conference talk — and score it on those three "
              "columns. Most public claims sit on the first row.",
},

"D1.0": {
 "concept": """
Function D is the only function that has to work while something is actively
going wrong, and agents change it at both ends.

**Agents as the instrument.** A triage loop that reads an alert, pulls the
context a human would have pulled, and proposes a disposition. Detection
engineering with a loop that writes and tests the rule. Reconstruction that
reads six months of logs in the time it takes to read a paragraph. The gain is
real and the risk is specific: a loop that closes alerts confidently is a loop
that can close the wrong one at scale.

**Agents as the actor.** An adversary — or your own misbehaving agent — that
acts a thousand times an hour, never gets bored, never repeats a session
verbatim, and leaves a trace shaped nothing like a person's. Detections tuned to
human tempo do not fire on it, and the ones that do fire arrive after it has
finished.

Two chapters:

- **Chapter 8 — detection.** Triage as a loop you supervise, detections written
  *for* agent behaviour, agent telemetry as a first-class data source, and
  telling agent from human when both hold the same credential.
- **Chapter 9 — response.** Scoping an incident whose actor is an agent,
  containment at machine speed, replay as forensics, and the one thing that has
  to stay human: who is allowed to stop it.
""",
 "steps": [
  ("md", "## 2 · One hour of an agent, one hour of a person"),
  ("html", D.table(
    ["signal, over one hour", "person", "agent", "ratio"],
    [["actions taken", "12", "1,400", "117×"],
     ["distinct resources", "5", "260", "52×"],
     ["median gap between calls", "180s", "2s", "1/90×"],
     ["sessions", "1", "96", "96×"],
     ["typo / retry events", "3", "0", "—"]],
    emphasise=3,
    caption="Every detection, baseline and playbook you own was tuned against "
            "the middle column.")),

  ("md", "## 3 · Why a volume rule is not the answer\\n\\n"
         "The obvious rule does fire. The problem is *when* — which is the one "
         "thing a table cannot show you, so this part is worth running."),
  ("py", '''def burst_rule(actions_per_hour, threshold=60):
    return actions_per_hour > threshold

RATE = {"person": 12, "agent": 1400}
for who, n in RATE.items():
    print(f"   {who:8s}{n:>6} actions/hour -> "
          f"{'ALERT' if burst_rule(n) else 'silent'}")

seconds_to_trip = 60 * 3600 / RATE["agent"]
print(f"\\nthe agent crosses the threshold after {seconds_to_trip:.0f} seconds")
print(f"and keeps going for the remaining {3600 - seconds_to_trip:.0f}.")
print()
print("So the rule fires, and it fires after about two and a half minutes of a")
print("sixty-minute run - by which point most of what the actor was going to do")
print("is done. Chapter 8 is about detections that fire on shape rather than")
print("volume; chapter 9 is about who can pull the stop lever without asking.")
assert burst_rule(1400) and not burst_rule(12) and seconds_to_trip < 200
'''),
 ],
 "expect": "Five behavioural signals for a person and an agent over the same "
           "hour, with ratios in the hundreds. The volume rule tuned for human "
           "tempo does fire on the agent — 154 seconds into a sixty-minute run, "
           "with the remaining 3,446 seconds unmonitored.",
 "challenge": "Pull one hour of activity for a service account in your own "
              "environment and compute those five signals. If you cannot, that is "
              "the first finding of chapter 8: the telemetry does not exist yet.",
},

"E1.0": {
 "concept": """
Function E governs autonomy rather than approving tools, and the difference is
not rhetorical. A list of approved products works when there are forty products.
It does not survive a thousand agents, most of them assembled by people who do
not think of themselves as building software.

The vocabulary this function runs on is **trustworthy AI**, and it is worth
being precise about it, because it is used loosely everywhere else. It names
seven properties a system is expected to hold:

| Property | What it means when an agent has it |
|---|---|
| valid and reliable | it does the thing, repeatably, and you measured that |
| safe | it does not cause harm even when it is wrong |
| secure and resilient | it withstands attack and recovers |
| accountable and transparent | someone owns it, and its behaviour is visible |
| explainable and interpretable | the reason for an action can be recovered |
| privacy-enhanced | it does not leak what it was trusted with |
| fair, with harmful bias managed | it does not distribute harm unevenly |

Not one of those belongs to a single team. Security owns part of "secure and
resilient" and almost none of "fair". The three chapters here are all attempts
to answer the same question — **who owns which** — at three different distances:

- **Chapter 10 — risk and control.** The inventory, the risk tiering, the
  control mapping, and evidence that can be re-checked instead of asserted once.
- **Chapter 11 — regulatory and compliance.** The obligations, the documentation
  that survives supervision, and the conversation with an auditor.
- **Chapter 12 — the CISO office.** Sequencing the programme, org design,
  metrics, and how to say no — or yes with conditions.
""",
 "steps": [
  ("md", "## 2 · Seven properties, and the question of who owns each"),
  ("html", D.table(
    ["trustworthy-AI property", "typical owner", "security's share"],
    [["valid and reliable", "engineering + the eval harness", "contributes evidence"],
     ["safe", "product owner + risk", "contributes evidence"],
     ["secure and resilient", "security", "<b>owns it</b>"],
     ["accountable and transparent", "the named system owner", "contributes evidence"],
     ["explainable and interpretable", "engineering + model risk", "contributes evidence"],
     ["privacy-enhanced", "privacy office + engineering", "contributes evidence"],
     ["fair, harmful bias managed", "product owner + legal", "contributes evidence"]],
    emphasise=2,
    caption="Security owns one of the seven outright and contributes evidence "
            "to the other six. That ratio is why this function exists as more "
            "than a security document.")),

  ("md", "## 3 · Three distances from the same question\\n\\n"
         "A trustworthy-AI statement with no owner per property is a statement "
         "that every property is somebody else's job. All three chapters here "
         "are attempts to fix that, at different ranges."),
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
    + D.label(350, 124, "inside the organisation  →  to a regulator  →  to the board",
              anchor="middle", size=11.5),
    height=140)),
 ],
 "expect": "Seven trustworthy-AI properties with a named owner each, security "
           "owning exactly one outright, and the three chapters laid out by how "
           "far from the system each one sits — the register, the regulator, the "
           "board.",
 "challenge": "Write the seven properties down and put a real name against each "
              "one in your own organisation. The properties you cannot assign are "
              "the programme; the ones assigned to 'security' by default are the "
              "argument you are about to have.",
},

}
