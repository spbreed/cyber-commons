"""The five function introductions — one per function, before its first chapter.

Each answers the same question for its own function: what is this part of the
commons for, which of the two directions does it run in, and what will you be
able to do at the end of it. They are deliberately short: one framework, one
small piece of code that makes the framework concrete, and no risk material —
the risks start in the chapter that follows.
"""

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

**Agentic AI architecture is the foundation of the second direction.** You
cannot secure a system you cannot draw. "Secure the agent" is not an
instruction; it is a sentence that becomes an instruction only once you can say
*which component* and *which boundary*.

So this function is one picture and its consequences, in three chapters:

- **Chapter 1 — the architecture, and every risk it carries.** One
  vendor-neutral component map, then one lesson per risk, each naming the
  component it attacks and grounded in the OWASP Agentic AI threat taxonomy.
- **Chapter 2 — identity and ingress.** Who is calling, on whose behalf, and
  what came in from outside. These two controls close more risks than anything
  else, which is why they come first.
- **Chapter 3 — runtime and the gateway.** What holds after identity has been
  defeated, and how the controls collapse into one enforcement point once you
  run more than a handful of agents.

Everything downstream names a component from chapter 1. The AppSec pipeline in
Function B is an agentic system with all of these risks. The red-team campaign
in Function C attacks these components. The detections in Function D watch them.
The control register in Function E lists them.
""",
 "steps": [
  ("md", "## 2 · Where the five functions sit, and what depends on this one"),
  ("py", '''FUNCTIONS = {
 "A": ("AI architecture, risks and mitigations", "mostly Security of AI"),
 "B": ("Product and application security with AI", "both directions at once"),
 "C": ("AI for security research", "both directions at once"),
 "D": ("AI for SecOps", "both directions at once"),
 "E": ("AI for GRC", "governs both directions"),
}
# What each later function needs from the component map built in chapter 1.
DEPENDS_ON_A = {
 "B": "the pipeline it builds is itself an agentic system with these components",
 "C": "the three attack surfaces it tests are components on this map",
 "D": "the telemetry it detects on is emitted by these components",
 "E": "the register it maintains lists these components and their controls",
}

print(f"{'function':4s}{'covers':44s}direction")
for f in sorted(FUNCTIONS):
    name, direction = FUNCTIONS[f]
    print(f"{f:4s}{name:44s}{direction}")

print("\\nwhat each later function borrows from Function A")
for f in sorted(DEPENDS_ON_A):
    print(f"   {f} -> {DEPENDS_ON_A[f]}")

CHAPTERS = {
 1: ("the architecture, and every risk it carries", "17 lessons"),
 2: ("controls - identity and ingress",             "7 lessons"),
 3: ("controls - runtime and the gateway",          "7 lessons"),
}
print("\\nFunction A, in order")
for n in sorted(CHAPTERS):
    what, size = CHAPTERS[n]
    print(f"   chapter {n}  {what:46s}{size}")

print()
print("Chapter 1 is the only one that introduces no control at all. That is")
print("deliberate: you cannot choose a control for a risk you cannot yet name,")
print("and naming the risk requires the picture.")
assert set(DEPENDS_ON_A) == set(FUNCTIONS) - {"A"}
'''),
 ],
 "expect": "The five functions print with the direction each runs in, and every "
           "one of the other four names something it borrows from Function A's "
           "component map. Function A itself is three chapters: the architecture "
           "and its risks, then identity and ingress, then runtime and the "
           "gateway.",
 "challenge": "Before the next lesson, write down the components of one agentic "
              "system you already run — even as a list of nouns. A1.1 gives you "
              "the standard names; comparing your list to it is the fastest way "
              "to find the component you forgot you had.",
},

"B1.0": {
 "concept": """
Function B is where both directions meet on the same system, and the reason it
is the largest function in the commons.

**AI for Security.** An agentic pipeline that ingests a codebase, models its
threats, audits for vulnerabilities, confirms the real ones by exploiting them
in a sandbox, engineers the remediation, and reports with a severity somebody
can act on. That is chapter 4, built stage by stage as one artefact.

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
  ("md", "## 2 · The pipeline, the harness, and the fact that they are the same kind of thing"),
  ("py", '''PIPELINE = {
 1: ("ingestion and structural mapping",   "B1.1-B1.2"),
 2: ("threat modelling and strategy",      "B1.3-B1.4"),
 3: ("analysis and filtering",             "B1.5-B1.7"),
 4: ("dynamic validation and remediation", "B1.8-B1.11"),
 5: ("governance and reporting",           "B1.12"),
}
HARNESS = ["the loop: plan, act, verify, stop", "tool design",
           "failure taxonomy", "replay and rollback",
           "one skeleton per domain, not one per team",
           "evaluation, reliability and cost"]

print("chapter 4 - the pipeline, as five phases")
for n in sorted(PIPELINE):
    what, where = PIPELINE[n]
    print(f"   phase {n}  {what:38s}{where}")

print("\\nchapter 5 - the harness underneath every one of those stages")
for h in HARNESS:
    print(f"   . {h}")

# The pipeline read as an agentic system, with the Function A components it uses.
AS_AN_AGENT = {
 "ingress":       "a pull request, written by anyone with commit access",
 "knowledge":     "the repository itself - untrusted by definition",
 "tools":         "the test runner, the sandbox, the ticket API",
 "identity":      "a service account that can write to your default branch",
 "egress":        "the report, and anything it happens to contain",
}
print("\\nthe same pipeline, read as an agentic system")
for c in sorted(AS_AN_AGENT):
    print(f"   {c:14s}{AS_AN_AGENT[c]}")
print()
print("Five components, every one of them a risk surface from Function A. A")
print("security pipeline is not exempt from the risks it exists to find - it is")
print("the clearest example of them.")
assert len(PIPELINE) == 5 and len(AS_AN_AGENT) == 5
'''),
 ],
 "expect": "The five pipeline phases print against the lessons that build them, "
           "the harness capabilities underneath them print as a list, and the "
           "same pipeline reads back as an agentic system with five Function A "
           "components — ingress, knowledge, tools, identity and egress.",
 "challenge": "Name the service account your existing CI security tooling runs "
              "as, and what it can write to. That account is the identity "
              "component of an agentic system whether or not anyone has called "
              "it one.",
},

"C1.0": {
 "concept": """
Function C is the smallest function in the commons and the one with the
strictest standard of proof.

Two chapters, and one idea holding them together: **an anecdote is not a
result.**

**Chapter 6 — offensive.** The agent as your instrument, running recon,
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
  ("md", "## 2 · What separates a finding from an anecdote"),
  ("py", '''SURFACES = {
 "injection":   "what the agent reads - direct, indirect, and via tool output",
 "identity":    "who it acts as - delegation, scope, expiry, impersonation",
 "containment": "what it can reach - tools, paths, egress, metadata",
}
print("the three surfaces of an agent, and chapter 6 tests all three")
for s in sorted(SURFACES):
    print(f"   {s:14s}{SURFACES[s]}")

# The same claim, at four standards of proof.
CLAIMS = [
 ("it worked when I tried it",                    False, False, False),
 ("it worked 7 times out of 20, suite attached",   True, False, False),
 ("7/20, and 0/20 on the patched build",           True,  True, False),
 ("7/20, 0/20 patched, reproduced by another team", True, True,  True),
]
print(f"\\n{'claim':50s}{'rate':>6}{'control':>9}{'reproduced':>12}  verdict")
for text, rate, control, repro in CLAIMS:
    score = sum((rate, control, repro))
    verdict = ("anecdote", "measurement", "result", "evidence")[score]
    print(f"{text:50s}{str(rate):>6}{str(control):>9}{str(repro):>12}  {verdict}")

print()
print("Chapter 6 gets you to the second row. Chapter 7 is entirely about the")
print("third and fourth, because a finding that nobody can reproduce protects")
print("nobody, however true it was on the day.")
assert len(SURFACES) == 3 and len(CLAIMS) == 4
'''),
 ],
 "expect": "The three attack surfaces of an agent print with what each covers, "
           "and the same claim scores as anecdote, measurement, result or "
           "evidence depending on whether it carries a rate, a control "
           "comparison and an independent reproduction.",
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
  ("py", '''HOUR = {
 "actions taken":            ("person", 12,   "agent", 1400),
 "distinct resources":       ("person", 5,    "agent", 260),
 "median gap between calls": ("person", 180,  "agent", 2),
 "sessions":                 ("person", 1,    "agent", 96),
 "typo/retry events":        ("person", 3,    "agent", 0),
}
print(f"{'signal':28s}{'person':>9}{'agent':>9}{'ratio':>9}")
for sig in sorted(HOUR):
    _, p, _, a = HOUR[sig]
    ratio = f"{a / p:.0f}x" if p else "-"
    print(f"{sig:28s}{p:>9}{a:>9}{ratio:>9}")

# A rule tuned for a person, evaluated against both.
def burst_rule(actions_per_hour, threshold=60):
    return actions_per_hour > threshold

print(f"\\nrule 'more than 60 actions in an hour'")
for who, n in (("person", 12), ("agent", 1400)):
    print(f"   {who:8s}{n:>6} actions -> {'ALERT' if burst_rule(n) else 'silent'}")

print()
print("That rule fires. The problem is the next one: at 1400 actions an hour the")
print("alert arrives after roughly 150 seconds of activity, and everything the")
print("actor was going to do is already done. Chapter 8 is about detections that")
print("fire on shape rather than volume; chapter 9 is about who can pull the")
print("stop lever without asking permission first.")
assert burst_rule(1400) and not burst_rule(12)
'''),
 ],
 "expect": "Five behavioural signals print for a person and an agent over the "
           "same hour, with ratios in the hundreds. A volume rule tuned for human "
           "tempo does fire on the agent — roughly 150 seconds in, by which point "
           "the actor has finished.",
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
  ("py", '''PROPERTIES = {
 "valid and reliable":          "engineering + the eval harness",
 "safe":                        "product owner + risk",
 "secure and resilient":        "security",
 "accountable and transparent": "the named system owner",
 "explainable":                 "engineering + model risk",
 "privacy-enhanced":            "privacy office + engineering",
 "fair, bias managed":          "product owner + legal",
}
SECURITY_OWNS = {"secure and resilient"}

print(f"{'property':30s}{'typical owner':34s}security's share")
for p in sorted(PROPERTIES):
    share = "owns it" if p in SECURITY_OWNS else "contributes evidence"
    print(f"{p:30s}{PROPERTIES[p]:34s}{share}")

print(f"\\nproperties in scope           : {len(PROPERTIES)}")
print(f"owned by security             : {len(SECURITY_OWNS)}")
print(f"needing somebody else to act  : {len(PROPERTIES) - len(SECURITY_OWNS)}")

CHAPTERS = {
 10: "risk and control - inventory, tiering, mapping, evidence",
 11: "regulatory and compliance - obligations, documentation, supervision",
 12: "the CISO office - sequencing, org design, metrics, stop authority",
}
print("\\nthree distances from the same question")
for n in sorted(CHAPTERS):
    print(f"   chapter {n}  {CHAPTERS[n]}")

print()
print("A trustworthy-AI statement with no owner per property is a statement that")
print("every property is somebody else's job. The register in chapter 10 exists")
print("to make that assignment explicit and re-checkable.")
assert len(PROPERTIES) == 7 and SECURITY_OWNS < set(PROPERTIES)
'''),
 ],
 "expect": "Seven trustworthy-AI properties print with a typical owner each. "
           "Security owns exactly one outright and contributes evidence to the "
           "other six — which is the reason this function exists as more than a "
           "security document.",
 "challenge": "Write the seven properties down and put a real name against each "
              "one in your own organisation. The properties you cannot assign are "
              "the programme; the ones assigned to 'security' by default are the "
              "argument you are about to have.",
},

}
