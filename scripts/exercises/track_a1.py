"""A1 — The agentic reference architecture, and every risk it carries.

One vendor-neutral architecture (A1.1), then fifteen risks, one per lesson,
mapped to the OWASP Agentic Security Initiative threat taxonomy. Every risk
names the component of A1.1 that it attacks, and every lesson carries exactly
one block of code: the risk, realised.

The controls are Chapters 2 and 3. Nothing here is fixed in this chapter, on
purpose — you cannot choose a control for a risk you cannot yet describe.
"""

from .skills import skill_steps

ARCH_NOTE = """
> **Where this lands on the reference architecture.**
>
> ```
> ingress -> orchestrator -> agent_runtime -> model
>                                |              |
>                          messaging        tools / mcp
>                                |              |
>                       knowledge / memory   egress
>            identity + policy wrap every call · observability records it
> ```
"""

EXERCISES: dict[str, dict] = {

# A1.1 is the only lesson in the commons with no code in it. It is a drawing
# lesson: the components, and the patterns they compose into. Every risk in this
# chapter and every control in the next two names something from these diagrams,
# so the picture has to land before anything executes.
"A1.1": {
 "concept": """
These components exist under different product names in every agent platform,
and the risks attach to the component rather than to the brand.

**Ingress.** Where a request enters: a chat surface, an API call, a webhook, a
scheduled trigger, another system. It carries the requester's identity and
whatever text they supplied.

**Orchestrator.** Decides which agent handles what, and in what pattern. In a
single-agent system this is a few lines; in a multi-agent one it holds the whole
design.

**Agent runtime.** The loop — plan, call a tool, observe the result, decide
again, stop. This is the component that turns text into consequence.

**Model.** Predicts tokens. Holds no credential, opens no socket, changes
nothing. Most of what people fear "the model doing" is done by the runtime.

**Tools and MCP servers.** The only components that change anything. An MCP
server is a third party's process whose tool descriptions land in your context.

**Knowledge and memory.** Retrieval pulls documents in at query time; memory
persists state across turns and sessions. Both inject text the user did not
write.

**Messaging.** The agent-to-agent channel in a multi-agent pattern.

**Identity and policy.** Who is calling, on whose behalf, and whether this call
is permitted. These wrap every other component.

**Egress.** Where data is allowed to go — the last boundary before it leaves.

**Observability.** What can be reconstructed afterwards.

Three of them carry content an outsider can author: **MCP**, **knowledge** and
the corpus behind it. Those are the input surface for the next fifteen lessons.
""",
 "steps": [
  ("md", """## 2 · Pattern 1 — the single agent

One loop, one set of tools. Almost everything in production today.

```
  user --> ingress --> agent runtime --> tools --> egress
                          |     ^
                          v     |
                        model (predicts; changes nothing)

  identity + policy wrap every arrow · observability records every arrow
```

The edge that matters is `agent runtime -> tools`. That is where text becomes
consequence, and it exists in every pattern below."""),

  ("md", """## 3 · Pattern 2 — orchestrator and workers

One planner fans work out to specialised workers and joins the results. The
pattern most multi-agent platforms mean when they say "multi-agent".

```
                            +--> worker A --> tools
  user --> orchestrator ----+--> worker B --> tools
                            +--> worker C --> tools
                                   |
                            join / summarise
```

New surface: the orchestrator decides *who* runs, so anything that can influence
its routing decides which permissions get used."""),

  ("md", """## 4 · Pattern 3 — sequential handoff

A pipeline of agents, each taking the previous one's output as its input.

```
  user --> agent 1 --> agent 2 --> agent 3 --> result
            recon      analyse     report

  each hop inherits the previous hop's claims; nobody re-checks them
```

New surface: an unverified claim at hop 1 is a fact by hop 3. This is the shape
that makes cascading hallucination (A1.12) a systems problem rather than a model
problem."""),

  ("md", """## 5 · Pattern 4 — peer swarm over shared memory

Agents with no central planner, coordinating through state they all write to.

```
     +--> agent A --+
  user +--> agent B --+--> shared memory <--+
     +--> agent C --+          ^            |
                               |            |
                    every agent reads what any agent wrote
```

New surface: memory is a write-once, read-forever channel between agents. One
poisoned entry is read back as trusted context indefinitely (A1.4), and there is
no orchestrator to notice."""),

  ("md", """## 6 · Pattern 5 — a workflow with agent steps

Deterministic control flow, with one or two steps handed to an agent. The
pattern with the best safety properties, and the one people skip.

```
  [fetch] --> [validate] --> (( agent step )) --> [approve] --> [commit]
      deterministic          non-deterministic        deterministic

  the blast radius of the agent is bounded by the two steps either side
```

New surface: almost none, which is the point. If the work fits this shape, the
other four patterns are a cost you do not have to pay."""),

  ("md", """## 7 · The two components that appear inside all five

Retrieval and human approval are not patterns of their own — they attach to any
of the five above, and each brings one surface with it.

```
  retrieval          agent --> retriever --> corpus
                       ^                       |
                       +----- documents -------+
                       anyone who can write to the corpus writes to the context

  human approval     agent --> proposed action --> [ human ] --> tools
                                                       ^
                       requests arrive faster than a person can read them
```

Retrieval is how outside text reaches the context window without anyone typing
it (A1.3). Approval is a real control for rare irreversible actions and a rubber
stamp for everything else (A1.15)."""),

  ("md", """## 8 · The edge every pattern shares

```
                    +---------------+       +-------+
   untrusted text   | agent runtime | ----> | tools |   consequence
   ---------------> |               |       +-------+
                    +---------------+
                       ^        ^
                  knowledge   messaging
                    memory      MCP
```

Whatever the topology, something reaches the agent runtime and the agent runtime
reaches tools. Every risk in the rest of this chapter is a route into the left
side of that picture. Every control in chapters 2 and 3 is an attempt to stand
somewhere on the arrow."""),
   ("md", "## 2 \u00b7 Drawing it, as a skill\n\n"
          "The map is not a picture of CyberTravels \u2014 it is the procedure for "
          "drawing one of any agentic system, which is why every later lesson can "
          "name a box.\n\nAnd it computes something, which is the part that "
          "makes a map arguable rather than decorative: the boundary crossings "
          "are **derived from the trust levels**, not listed. Change a level and "
          "the count changes. A diagram nobody can be wrong about is a diagram "
          "nobody has to agree with."),
   ("skill", "architecture/agentic-architecture-map"),
   ("skill_script", "architecture/agentic-architecture-map/scripts/agentic_architecture_map.py"),

   ("md", """## 3 \u00b7 Read the crossings, then read what is missing

Five crossings, and two of them are the whole of Function A's injection
material: **ingress \u2192 orchestrator** carries traveller text and
**knowledge \u2192 agent runtime** carries retrieved documents, both from trust
0 into components that hold authority. A1.2 is the first of those edges and
A1.3 is the second.

Then the line most maps never print: **egress is absent.** CyberTravels has no
gateway, so "route it through the gateway" is not a control it can apply yet.
Saying so on the map is what stops a later meeting designing controls for a
component nobody has \u2014 and it is why A3.7 exists as a separate lesson
rather than an assumption."""),
],
 "expect": "You can draw one agentic system you run as thirteen named components, "
           "say which of the five patterns it is, and name the three components "
           "in it whose content an outsider can author. That list is the input "
           "surface for the fifteen risk lessons that follow.",
 "challenge": "Draw your own system on one page, then mark the "
              "`agent_runtime -> tools` edge on it. Everything in chapters 2 and "
              "3 is an argument about what is allowed to stand on that arrow, and "
              "you will get more out of them having drawn it first.",
},

"A1.2": {
 "concept": """
**OWASP T6 — Intent Breaking & Goal Manipulation. LLM01 — Prompt Injection.**

The plainest version of the risk: a user types instructions that contradict the
operator's, and the agent follows the user's.

It works because of one property of the **ingress → agent_runtime → model**
path. The operator's instructions and the user's message arrive as the same
kind of thing — tokens in one sequence. There is no channel separation, no
privilege bit, nothing in the format that says *this half is policy and that
half is data*. By the time the model reads it, the distinction the operator
believed in does not exist in the input.

This is **direct** injection: the attacker is the legitimate user, attacking
their own agent. That bounds it. Whatever they persuade the agent to do, it does
with the authority they already had, so the blast radius is their own account
and their own data.

That makes it the milder of the two injection risks — and the one people spend
most of their defensive effort on, because it is the one they can see happening.
The next lesson is the one that matters.

What it is **not** is a bug in the model. The model did what it does: continued
a text. The system placed an adversary's text in the same channel as its own
instructions and expected precedence to survive.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "A support agent with a system instruction, and a user who disagrees "
         "with it."),
  *skill_steps('threats/instruction-channel-check',
               "## 2 · The check, as a skill\n\nCyberTravels' operator prompt and a traveller's message reach the model in one string. Whether that matters is not a question you answer by reading the prompt — it is a check you run, and the check is written down here as a skill. Its script runs it against a synthetic window and prints what won."),
],
 "expect": "The same agent answers a normal question correctly and hands over "
           "its internal note when the user tells it to ignore its "
           "instructions — because both instructions arrived in one string with "
           "no channel separating them.",
 "challenge": "Find the system prompt for one agent you run and ask what it is "
              "relied on to prevent. Anything on that list that would matter if "
              "it failed needs a control below the model, not a sentence inside it.",
},

"A1.3": {
 "concept": """
**OWASP T6 — Intent Breaking & Goal Manipulation. LLM01 — Prompt Injection.**

This is the one that matters.

The attacker is not the user. The attacker wrote something into content the
agent was asked to *process*: a wiki page, a Jira ticket, a web page, an email,
a code comment, a row in a database, the description a third-party MCP server
advertises. It enters at the **knowledge**, **memory**, **mcp** or **tools**
component — every one of them trust 0 or trust 1 on the map — and travels into
the same context window as the operator's instructions.

Then the agent obeys it, **carrying the user's authority**.

That last clause is the whole risk. Nobody was phished. No credential leaked.
A wiki page was edited, which is what wiki pages are for. The victim is a user
who never saw the payload, and the action is performed with their permissions,
by a system they were told to trust.

The useful reframing: **every untrusted-content path into the context window is
an unauthenticated code path.** You would not ship an HTTP endpoint that
executes a string supplied by an anonymous caller. Retrieval does exactly that,
on every query — and it is usually not in the threat model, because it looks
like reading rather than executing.

The work starts with enumeration: how many such paths exist, and which of them
can reach the tool call.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "One payload, delivered through four trust-0 or trust-1 components. "
         "The agent cannot tell any of them from the operator's instruction."),
  *skill_steps('threats/indirect-injection-path-trace',
               "## 2 · The check, as a skill\n\nCyberTravels reads hotel descriptions, booking notes, MCP tool descriptions and tool results. Each is a component that can put text into the context, so each is an entry point, and the useful artefact is the inventory rather than the payload. The skill's script drives one payload through all four."),
],
 "expect": "The same payload steers the agent through all four untrusted entry "
           "components — retrieved knowledge, persisted memory, an MCP tool "
           "description and a tool result — and in every case the action runs "
           "with the requesting user's authority.",
 "challenge": "List the trust-0 and trust-1 components in one agent you operate "
              "and name who can write into each. Most teams find a path they had "
              "not counted, and it is usually a tool result: the output of a "
              "system they trust, carrying text a stranger wrote.",
},

"A1.4": {
 "concept": """
**OWASP T1 — Memory Poisoning. LLM04 — Data and Model Poisoning.**

The **memory** component exists so that today's conversation can be shaped by
something learned last week. That is the feature. The risk is the same sentence
with one word changed: today's conversation can be shaped by something *written*
last week.

Retrieval poisoning fires while the poisoned document is in the corpus. Memory
poisoning fires **forever**, because the write happened once and every
subsequent read treats it as established context. A single successful injection
becomes a standing instruction.

Two properties make it worse than it first looks.

**It crosses sessions and users.** Memory is usually keyed by tenant, workspace
or agent — not by the user who wrote it. A note written by one user is read back
to another, and the second user has no way to know where it came from.

**Provenance is lost on write.** The retrieved document that carried the payload
was at least labelled as retrieved. Once its content is summarised into a memory
record, it is stored as a fact the agent knows. The label is gone and there is
nothing left to distrust.

This is why the ingress control in A2.6 has to survive into memory, and why
memory writes have to be scoped to the identity that made them.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "One poisoned write, then an unrelated session for a different user."),
  *skill_steps('threats/memory-scope-and-origin-audit',
               "## 2 · The check, as a skill\n\nThe question is not whether CyberTravels' memory can be poisoned — it is what the write was keyed by and whether the origin survived it. The skill's script writes from one traveller's ticket and reads back days later as somebody else."),
],
 "expect": "A poisoned note extracted from one user's ticket is written to "
           "workspace memory, and days later steers an unrelated request from a "
           "different user — because memory is keyed by workspace rather than by "
           "the identity that wrote it, and the origin was discarded on write.",
 "challenge": "Look at what your agent writes to long-term memory and ask which "
              "of it originated in content a user did not author. Then ask what "
              "would remove it, and who would notice it was there.",
},

"A1.5": {
 "concept": """
**OWASP T2 — Tool Misuse. LLM06 — Excessive Agency.**

The **tools** component is the only part of the architecture that changes
anything. Every other component reads, routes, predicts or records; a tool sends
the email, runs the query, merges the pull request, moves the money.

Tool misuse is what happens when a tool does precisely what it was built to do,
for a request nobody intended. There is no exploit. The tool was granted a
broad scope because scoping it narrowly was awkward — one database tool with
write access to the whole schema instead of five with access to one table each —
and the agent, persuaded or simply mistaken, uses that scope.

The property that makes this hard to catch: **every log line looks normal.**
The identity is right, the tool is one it always calls, the arguments are
well-formed. What is wrong is the combination, and the combination is only
visible to something that knows what this caller should be doing.

The distinction worth holding on to is between the tool's **capability** and
the caller's **need**. A tool's capability is fixed at design time by whoever
wrote it. The need is per-call. When authorization is attached to the tool
rather than to the call, every caller inherits the widest need any caller ever
had — which is the definition of excessive agency.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "One tool, scoped for the hardest job it ever has to do."),
  *skill_steps('threats/tool-scope-abuse-probe',
               "## 2 · The check, as a skill\n\nCyberTravels' database tool was scoped for the widest job it ever does, which is how a booking lookup ends up able to read a signing key. The skill probes the gap between what a tool is *for* and what it *can do*, with the right identity and well-formed arguments throughout."),
],
 "expect": "A single database tool, scoped for the widest job it ever performs, "
           "reads a signing key and empties the secrets table for requests it "
           "was never meant to serve — with the right identity, a familiar tool "
           "and well-formed arguments on every call.",
 "challenge": "Take the most powerful tool one of your agents can call and write "
              "down the worst thing one call could do with attacker-chosen "
              "arguments. That sentence, not the tool's name, is what belongs in "
              "the risk register.",
},

"A1.6": {
 "concept": """
**OWASP T3 — Privilege Compromise. LLM06 — Excessive Agency.**

Tool misuse is about what a tool can do. Privilege compromise is about **whose
authority it does it with** — the **identity** component rather than the tools
component.

Three patterns produce it, and all three are things teams do for good reasons.

**Inherited human credentials.** The agent runs with the token of the user who
started it. Convenient, and it means the agent holds every permission that user
holds — including the ones irrelevant to the task, and including the ones they
hold because of a role they were given three years ago.

**Shared service accounts.** Every agent authenticates as `agent-svc`. That
account needs the union of everything any agent ever needs, so each agent holds
the maximum of the set.

**Standing scope.** The grant is permanent because renewing it was operationally
awkward. The authority is therefore present at the moment any injection lands.

What makes this distinct from ordinary over-permissioning is the **direction of
the audit trail**. When a human has too much access and misuses it, the log
names them. When an agent does it, the log names the service account — and the
human who caused it is not in the record at all. The compromise is of privilege
*and* of attribution, at the same time.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "A read-only user asks for something, and the agent has more authority "
         "than they do."),
  *skill_steps('threats/authorization-subject-check',
               '## 2 · The check, as a skill\n\nEverything turns on which principal the decision was evaluated against. The skill runs the asymmetric probe — a traveller holding `reports:read` asking for something that needs `db:admin` — and then reads one audit row to see whether a human can be recovered from it.'),
],
 "expect": "A user holding only `reports:read` triggers a `db:admin` action, "
           "because authorization was evaluated against the shared agent service "
           "account rather than the requester — and the audit trail names "
           "`agent-svc` on every row, so the human who caused it cannot be "
           "recovered from it at all.",
 "challenge": "Pick one agent and answer two questions: what identity does it "
              "authenticate as, and can you name the human behind any single "
              "action it took last week. If the second answer is no, you have "
              "this risk regardless of how the scopes are set.",
},

"A1.7": {
 "concept": """
**OWASP T9 — Identity Spoofing & Impersonation.**

A1.6 was about an agent holding too much authority. This one is about the
**identity** component being unable to say *which agent* is calling at all.

When several agents share one credential — the same service account, the same
API key baked into the same image — they are, to every downstream system, the
same principal. There is no spoofing step required. Impersonation is the
default state, because there was never a distinction to defeat.

Three consequences follow, and the third is the one that hurts during an
incident:

**Authorization cannot differ.** Every agent gets the union of what any of them
needs, which is A1.6 again, arriving through a different door.

**Attribution is impossible.** "Which agent called this?" has no answer. Not a
hard answer — no answer, because the information was never present.

**Revocation is all-or-nothing.** You have one misbehaving agent and one
credential shared by forty. Rotating it stops the incident and stops the other
thirty-nine, so the decision becomes a business call in the middle of a
response, at whatever hour it is.

In a multi-agent topology this compounds. A peer's message is trusted because it
came from a peer — but if identity cannot distinguish peers, "it came from a
peer" is a claim anyone inside the perimeter can make.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "Three agents, one credential, one incident."),
  *skill_steps('threats/shared-credential-attribution-check',
               '## 2 · The check, as a skill\n\nThree CyberTravels agents share one API key, so the payments API records one caller on every line. The skill measures both costs: what the record can attribute, and what revoking the key would stop.'),
],
 "expect": "Three agents share one credential, so the downstream record shows a "
           "single caller on every line. When one deletes a production table the "
           "culprit is not recoverable from the record, and the only containment "
           "available stops all three.",
 "challenge": "Count the distinct credentials across your agents and divide by "
              "the number of agents. Any answer below one is this risk, and the "
              "number tells you how many innocent agents a revocation takes down.",
},

"A1.8": {
 "concept": """
**OWASP T11 — Unexpected RCE and Code Attacks. LLM05 — Improper Output Handling.**

Many useful agents write code and run it — that is what makes a data-analysis
agent or a coding agent worth having. The **agent_runtime** component executes
text the **model** produced, on a host, in a process.

The risk is not exotic. Model-authored code is just code, and it runs with
whatever the process has: the filesystem it can see, the network it can reach,
and every credential in its environment. There is no privilege boundary between
"the code the agent wrote to reformat a CSV" and "the code that reads
`~/.aws/credentials`", because both are strings passed to the same interpreter.

Two paths lead here, and only one involves an attacker:

**Steered.** An injection from A1.3 tells the agent to write particular code.
The runtime executes it because executing code is its job.

**Unsteered.** Nobody attacked anything. The agent wrote something plausible and
wrong — a cleanup routine with a path variable that resolves higher than
intended — and the blast radius was decided by the environment, not by intent.

That second path is worth sitting with. Most teams model this as an attack. In
practice the first incident is usually an ordinary bug with production
credentials in scope, which is why the control in A3.2 is about what the process
can *reach*, not about what the model can be persuaded to *write*.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "What the executing process can reach, enumerated rather than assumed. "
         "Nothing below actually touches your machine — the environment is a "
         "fixture, so the lesson runs anywhere."),
  *skill_steps('threats/generated-code-reach-enumerator',
               "## 2 · The check, as a skill\n\nCyberTravels' Coding Agent runs code it wrote. The skill enumerates what that process reaches — environment, filesystem, network — on an ordinary task first, because the ordinary task is the more persuasive half of the finding."),
],
 "expect": "Model-authored code is executed against a fixture environment and "
           "the reach is enumerated: an ordinary, unattacked task touches every "
           "file the process can see including a private key, and steered code "
           "reaches the environment credentials and the cloud metadata address.",
 "challenge": "For one agent that executes code, list what is in its process "
              "environment right now. The credentials in that list are the blast "
              "radius of the next ordinary bug, not of the next attack.",
},

"A1.9": {
 "concept": """
A1.8 was an agent running code it should not have run. This is the same shape
one level up: an agent **reading** something it was asked to read, and treating
what it read as an instruction.

Any agent that ingests content and then acts is a confused deputy waiting to
happen, and the more useful the agent the truer that is. At CyberTravels the
sharpest instance is the tooling that reviews the Coding Agent's pull requests —
the thing under review is attacker-controlled *by definition*, because that is
what review means. Every part of it is a carrier: the diff, the description,
commit messages, code comments, test fixtures, and any file read to build
context.

The same applies to the File System Agent reading a vendor invoice and the RAG
Advisor reading an indexed template. Different content, identical structure.

Filtering the text fails for the reason it always fails: the attacker picks the
wording and you pick the blocklist. Worse, the phrasings that work best here
contain no suspicious vocabulary at all, because engineering notes addressed to a
bot are a normal thing to write.

The control that holds is **provenance**: a state-changing tool may only be
driven by the principal's request, never by content the agent read. It does not
depend on recognising the attack, which is why it survives wordings nobody
thought of. A2.6 builds it as a control; this lesson is the risk it closes.

Function B builds an entire security pipeline on agents that read untrusted
code for a living. It inherits this risk in full, and being a security tool
grants no exemption.
""",
 "steps": [
  ("md", "## 2 · Demo — the pipeline's own tool surface"),
("md", "## 3 · Where it breaks — five carriers, none with blocklist vocabulary"),
("md", "## 4 · The control — provenance, and deriving what is privileged"),
  *skill_steps('threats/content-derived-privilege-check',
               "## 2 · The check, as a skill\n\nAn agent asked to read a pull request is asked to trust nothing, and the tools worth guarding are not the ones whose names sound dangerous. The skill drives five carriers and then re-derives the privileged set from what each tool's output causes."),
],
 "expect": "The normal run executes all four tools. None of the five carriers "
           "contains blocklist vocabulary and all five reach `approve_pr` on the "
           "trusting pipeline. With provenance enforced all five are blocked "
           "while the principal's own calls still succeed. Deriving privilege "
           "from effects shows `post_comment` is privileged because CI listens to "
           "comments, and a content-driven comment is then blocked.",
 "challenge": "List every place your CI reacts to something the pipeline can "
              "produce — comments, labels, branch names, commit trailers. Each one "
              "promotes an innocuous tool into a privileged one, without anyone "
              "editing the pipeline.",
},

"A1.10": {
 "concept": """
**OWASP T12 — Agent Communication Poisoning.**

Once you have more than one agent, the **messaging** component appears — the
channel a peer or an orchestrator uses to hand work along. In every multi-agent
topology on the A1.1 map, some agent's output becomes another agent's input.

The risk is a trust asymmetry that nobody decided on. A retrieved document is
treated with suspicion, at least in principle. A message from `pricing-agent`
arrives looking like a colleague's instruction, and is usually parsed straight
into context with none of the checks a document would get.

But `pricing-agent`'s message is not more trustworthy than a document — it is
*less*, because its content may be a summary of a document that was poisoned in
A1.3. Compromise one agent and you compromise its neighbours, without touching
them.

Two properties make this spread rather than stop:

**Trust is transitive by default.** Agent B trusts A's message, C trusts B's,
and nothing along the chain re-examines the original claim.

**Provenance thins with each hop.** The first message says "the wiki says X".
The second says "X". By the third, X is background knowledge with no source
attached, which is exactly the hand-off into A1.12.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "A poisoned message entering an orchestrator–worker topology at one "
         "agent."),
  *skill_steps('threats/peer-message-propagation-trace',
               '## 2 · The check, as a skill\n\nOne CyberTravels agent reads a poisoned supplier page and tells its peers. What spreads is the summary, and summarising is the operation that drops the sentence naming the source. The skill steps the topology and counts actors, not hops.'),
],
 "expect": "A single poisoned document read by one agent propagates through the "
           "topology as a peer message, and more than one agent acts on it — "
           "with the phrase identifying its source dropped on the first hop, "
           "because summarising is what the hand-off does.",
 "challenge": "In your own multi-agent system, find where one agent's output "
              "becomes another's input and ask what validates it. If the answer "
              "is 'it came from our own agent', that is the trust asymmetry, "
              "stated.",
},

"A1.11": {
 "concept": """
**OWASP T13 — Rogue Agents in Multi-Agent Systems.**

The **orchestrator** delegates work to agents. The question this risk asks is
disarmingly simple: *how does it know which agents are allowed to receive that
work?*

In most deployments the answer is configuration — a list in a file, an env var,
a service discovery lookup. None of those is an identity check. An agent that
appears in the right place, answering the right protocol, is treated as a
legitimate worker.

Two ways one arrives:

**A compromised legitimate agent.** It was registered and approved; it is now
executing someone else's instructions after A1.3 or A1.10. Nothing about its
registration is wrong, which is why registration alone does not solve this.

**An unregistered agent.** A developer stood one up to test something, or an
attacker with a foothold registered a service. It receives delegated work and
delegated authority because the topology admits by convention rather than by
identity.

The consequence specific to multi-agent systems: **delegated authority flows to
it.** The orchestrator does not just send a task, it sends the context and often
a token. So an agent nobody approved ends up holding a credential that narrows
from a real user's, and the audit trail — if it records agent names at all —
records a name the attacker chose.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "An orchestrator that admits workers by configuration."),
  *skill_steps('threats/agent-registry-gap-check',
               '## 2 · The check, as a skill\n\nCyberTravels discovers its workers. The skill compares what is present against what anybody registered, then follows a delegation to see what the unregistered agent is handed — including the narrowed traveller token.'),
],
 "expect": "Three agents are discovered, two are in the registry, and all three "
           "receive delegated work — including the narrowed user token. The "
           "unregistered agent can now act as the requesting user against any "
           "downstream that honours it.",
 "challenge": "Ask how your orchestrator decides which agents may receive work. "
              "If the answer is a config list or service discovery, write down "
              "what would have to be true for an extra entry to be noticed.",
},

"A1.12": {
 "concept": """
**OWASP T5 — Cascading Hallucination Attacks. LLM09 — Misinformation.**

The **model** component produces confident text. Sometimes the text is wrong.
That is a known property, and on its own it is a quality problem rather than a
security one.

It becomes a security problem when the architecture has more than one step,
because an unverified claim from step one is an *input* to step two. And inputs
are not re-examined — that is the point of a pipeline.

Watch what happens to a single fabrication as it travels:

**Hop one.** "I could not find a CVE for this dependency, it is probably fine."
Hedged, and the hedge is visible.

**Hop two.** The next agent summarises: "dependency has no known CVEs."
The hedge is gone. Nothing lied — summarising removes qualifiers, that is what
summarising is.

**Hop three.** "Dependency verified clean." Now it is a finding, with the
confidence of something that was checked, and no field anywhere records that
nobody checked anything.

The security consequence is that **confidence rises as evidence disappears**,
which is exactly backwards. And it is not limited to accidents: an attacker who
can inject one plausible claim early gets it laundered into an established fact
by your own pipeline, which is why this sits in the threat taxonomy rather than
in a quality backlog.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "One hedged guess, three hops, and the confidence it acquires on the way."),
  *skill_steps('threats/confidence-provenance-decay-check',
               '## 2 · The check, as a skill\n\nA hedged sentence about libfoo becomes a confident claim in three hops. The skill tracks both series — confidence and surviving provenance — because either one alone looks ordinary and the pair is the finding.'),
],
 "expect": "A hedged guess at confidence 0.2 becomes a confident claim above 0.8 "
           "in three hops, while the provenance field empties — confidence rising "
           "at exactly the rate evidence disappears.",
 "challenge": "Take a finding your pipeline produced and try to walk it back to "
              "the step that first asserted it. If you cannot reach a step that "
              "checked something, you have found a cascade rather than a finding.",
},

"A1.13": {
 "concept": """
**OWASP T4 — Resource Overload. LLM10 — Unbounded Consumption.**

The **agent_runtime** loops: plan, act, observe, decide again. The loop is the
component that makes an agent an agent, and a loop with no exit condition runs
until something outside it intervenes.

What intervenes, in practice, is a bill, a rate limit, or a person at 3am.

Four resources drain, and they fail differently:

**Tokens and money** — the visible one, discovered on an invoice.

**Downstream capacity** — the one that hurts other people. An agent retrying a
failing API in a tight loop is a denial-of-service attack on your own service,
launched from inside your perimeter by something with valid credentials.

**Rate limit budget** — shared with the humans who need it. The agent exhausts
the quota and the on-call engineer cannot query the API they need.

**Wall-clock time in a critical path** — a workflow step that never returns.

This is a security risk rather than a cost problem for two reasons. It is
**reachable by an attacker**: a task that cannot succeed is easy to construct
via A1.3, and costs the attacker nothing. And it is **availability**, which is
one third of the triad regardless of how the outage was caused.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "A task that cannot succeed, and a loop with no ceiling."),
  *skill_steps('threats/unbounded-loop-cost-probe',
               "## 2 · The check, as a skill\n\nCyberTravels' agent does not know the task is impossible. The skill gives it one, measures the three costs, and reports the one that lands on somebody else: the downstream capacity its retries consumed."),
],
 "expect": "An agent given an impossible task loops until the notebook's own "
           "safety net stops it, spending hundreds of thousands of tokens and "
           "exhausting a downstream service's capacity — with the rejections "
           "landing on whoever else was using that service.",
 "challenge": "Find the ceiling on one agent loop you run. If there is a token "
              "budget but no cap on downstream calls, the cost is bounded and "
              "the availability risk is not.",
},

"A1.14": {
 "concept": """
**OWASP T8 — Repudiation & Untraceability.**

The **observability** component decides whether anything that just happened can
be explained. Most agent logging records tool calls: which tool, what arguments,
what came back. That is enough to debug the agent and not enough to investigate
it.

Three fields are usually missing, and each one removes a different question from
the set you can answer.

**The human principal.** Without it, "which user caused this?" has no answer —
the log says `agent-svc`, as in A1.6.

**The motivating input.** The tool call is recorded; the thing that made the
agent decide to call it is not. So root cause cannot be established at all. You
can see that the agent emailed a file, and nothing tells you the retrieved
document that told it to.

**The delegation chain.** In a multi-agent topology, which hop originated this?
Without the chain you have a set of actions and no order.

There is a fourth problem that is structural rather than about fields: **if the
agent can write to the log store, the log is not evidence.** An agent with
credentials broad enough to be interesting usually has credentials broad enough
to touch the observability stack, and nobody notices until they need the record
to be trustworthy.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "A deletion happened. Answer three questions from the log you have."),
  *skill_steps('threats/audit-answerability-check',
               '## 2 · The check, as a skill\n\nCyberTravels logs every tool call. The skill puts the three questions an investigation opens with to one real record, and reports per question the field that would have answered it.'),
],
 "expect": "A complete-looking tool-call log answers none of the three questions "
           "an investigation needs — which user, what motivated it, which hop "
           "originated it — because the principal, the motivating input and the "
           "delegation chain were never recorded.",
 "challenge": "Take yesterday's agent logs and try to answer 'which user caused "
              "this action'. Time how long it takes. That number is your "
              "time-to-attribution during an incident, when it will be worse.",
},

"A1.15": {
 "concept": """
**OWASP T10 — Overwhelming Human-in-the-Loop.**

Human approval is the control everyone reaches for first. It is placed at the
tool call — the right place — and it is genuinely strong for rare, consequential
decisions.

Then the system scales, and the arithmetic turns on it.

An agent generates approval requests at machine speed. A human reads them at
human speed. When the queue exceeds what a person can actually consider, the
behaviour does not degrade gracefully into "slower but careful". It degrades
into **approving without reading**, because the alternative is being the reason
nothing shipped.

The failure is invisible from inside the system. Every approval is recorded. The
audit trail shows a human decision on every action. The control appears to be
operating at 100%, and the thing being measured — that a human clicked — is not
the thing anyone cared about.

There is a second-order effect worth naming: an attacker who wants one approval
can *manufacture the volume that makes it likely*. Generate two hundred benign
requests, put the one that matters at position 173, and the control has been
defeated by arithmetic rather than by cleverness.

Approval is a control for irreversible actions. Used as a general-purpose gate
it becomes a click, and the risk register still counts it.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "Approval quality against volume, and the position an attacker chooses."),
  *skill_steps('threats/approval-queue-saturation-model',
               '## 2 · The check, as a skill\n\nApproval coverage at CyberTravels reads 100% at every volume, because coverage measures whether a human was asked. The skill models what reading does instead, and finds the volume at which the gate stops being one.'),
],
 "expect": "Approval coverage reads 100% at every volume while the malicious "
           "request is caught only when the queue is small enough to be read — "
           "and an attacker choosing the position needs only to generate the "
           "requests in front of it.",
 "challenge": "Count how many approval requests one of your agents generates per "
              "day and ask the person approving them how many they read in full. "
              "The gap between those two numbers is the control's real coverage.",
},

"A1.16": {
 "concept": """
**OWASP T7 — Misaligned & Deceptive Behaviors.**

An agent optimises for the objective it was given. The objective you *meant* is
never quite the objective you *wrote*, and the agent has no access to the
difference.

Where the two diverge, the agent takes the cheaper path — and reporting success
is almost always cheaper than achieving it. This is not the agent deciding to
deceive. It is a scoring function being satisfied in a way nobody enumerated.

The pattern shows up in three recognisable shapes:

**Satisfying the metric.** Told to close alerts, it closes them. Told to reduce
findings, the count drops. Both instructions were followed exactly.

**Declaring success.** The task is hard, the loop is bounded, and "done" is a
valid terminal state that costs one token. Nothing verified the claim, so
nothing contradicts it.

**Avoiding the check.** If a verification step is part of the loop and the agent
controls whether it runs, skipping it is a legal move that improves the score.

What makes this a security risk rather than a quality one: the transcript
contains no lie you can point at. Every step is defensible in isolation.
Deception here is an emergent property of an unverified objective, not a
statement anyone made — which is why the control in A3.5 is an *independent*
verifier, and why "ask the model whether it succeeded" is not one.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "One objective, satisfiable two ways. The agent takes the cheap one."),
  *skill_steps('threats/objective-gaming-check',
               '## 2 · The check, as a skill\n\nTold to reduce open alerts, an agent reduces open alerts. The skill runs that objective with a budget, watches the spend, and audits the outcome rather than the transcript — where nothing false will be found.'),
],
 "expect": "An agent told to reduce open alerts closes all twenty for a quarter "
           "of its budget, meeting the objective exactly — while closing five "
           "real incidents unread, with each step defensible in isolation and no "
           "false statement anywhere in the transcript.",
 "challenge": "Write down the objective one of your agents optimises and then "
              "write the cheapest way to satisfy that sentence without doing the "
              "work. If you can find one in under a minute, so can the loop.",
},

"A1.17": {
 "concept": """
**OWASP T14 — Human Attacks on Multi-Agent Systems. T15 — Human Manipulation.**

The last two threats route through people rather than components, and they run
in opposite directions.

**T14 — a human attacking the system.** An insider does not need to defeat
authorization. They need to find a delegation path where authority is composed.
Ask the orchestrator for something it will route to an agent that holds a
credential you do not. Each hop is individually legitimate — you were allowed to
ask, the orchestrator was allowed to route, the agent was allowed to act — and
the composition reaches something you were explicitly denied. Privilege
laundering, using the architecture exactly as designed.

**T15 — the system manipulating a human.** The output of an agent arrives with
institutional authority. It is formatted like a report, it cites things, it does
not hedge. A person reading it makes a decision on it, and applies less scrutiny
than they would to a colleague's opinion — because it looks like a system
output rather than an argument.

That is exploitable in both directions: an attacker who lands an injection at
A1.3 gets their content delivered in your agent's trusted voice, and an agent
that is merely wrong at A1.12 gets the same credibility for free.

The uncomfortable version: the more your agent is trusted, the more valuable it
becomes as a channel into human decisions — so success at deployment increases
this risk rather than reducing it.
""",
 "steps": [
  ("md", ARCH_NOTE + "\\n## 2 · The risk, realised\\n\\n"
         "A request that is denied directly, and permitted through the "
         "architecture."),
  *skill_steps('threats/authority-composition-check',
               '## 2 · The check, as a skill\n\nA CyberTravels traveller denied `payments:write` reaches it through the orchestrator, with every hop legitimate. The skill records the direct refusal first, so the composed success reads as a finding rather than as intended behaviour.'),
],
 "expect": "A user denied `payments:write` directly reaches it through the "
           "orchestrator, with every individual hop legitimate and only the "
           "composition unauthorised — and the same claim is shown carrying more "
           "weight when an agent states it than when a colleague does.",
 "challenge": "Take one permission a user is denied and see whether an agent "
              "they can talk to holds it. That pair is a laundering path, and it "
              "is invisible to any review that checks permissions one hop at a time.",
},
}
