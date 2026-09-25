"""One paragraph per lesson: what it covers, and why it matters in a
security context.

A reader who lands on a single lesson — from a search result, a link in a
ticket, a colleague's message — has no idea what they are looking at. The
hook is deliberately a consequence rather than an orientation, so it does
not do this job; this does, and the build refuses a lesson without one.
"""

ABOUT: dict[str, str] = {

"A0.0": """
**What it covers.** Six things, in order: setting up your computer, installing Git, installing Python, what a skill is, how to execute one, and why this is a new way of working. Then you run one real skill and read back which model answered.

**Who it is for.** Anyone who can use a computer. It assumes no programming, no security background and no paid account, and it is written to be followed by a capable thirteen-year-old — which is a deliberate floor, not a simplification, because the thing being taught is hard enough without the setup being hard too.

**Why it is first.** Nothing in the commons runs without a model. Skip this and a later lesson stops with a message instead of doing the work — correct behaviour, and easy to misread as a broken download. This lesson makes you meet that message once, on purpose, before it can confuse you.
""",

"A0.1": """
**What it covers.** Who this commons is written for — six functions, one per role, with everybody starting in the one that builds the system — and the sections a lesson page is built from, in the order they appear and with the rule for which of them a given page shows.

**Why a security engineer needs it.** A reader who lands mid-curriculum reads the hook as an abstract, finds it vague, and leaves. The hook is a scene rather than a summary, and the description sits under it. The control it builds is: knowing which section answers the question you actually arrived with, and that a section missing from a page is missing on purpose.

This is the **first** lesson to read. It has no code and takes ten minutes.
""",

"B1.0": """
**What it covers.** Place the six functions of the commons on one diagram and find where your own work sits.

**Why a security engineer needs it.** Without a shared architecture, "secure the agent" has no referent, and every control argument is really an argument about two different systems. The control it builds is: one picture, three chapters: the architecture and its risks, then identity and ingress, then runtime and the gateway.

This is an **orientation** lesson. It has no code — it exists so the chapters after it are read in the right order.
""",

"B1.1": """
**What it covers.** Build the component graph and the five topologies, then trace one request through each and see where the trust boundary sits.

**Why a security engineer needs it.** Without a shared picture, 'secure the agent' has no referent and every later risk lands nowhere in particular. The control it builds is: one component map and five topologies, named once and reused by every lesson that follows.

This is a **mapping** lesson: every later risk and control in this function names a component from the picture it draws.
""",

"B1.2": """
**What it covers.** Send an override through the ingress component and watch the agent's goal change.

**Why a security engineer needs it.** The user redirects their own agent past the behaviour the operator specified — bounded by their own authority, and therefore the milder of the two injection risks. The control it builds is: provenance at ingress (B2.6) and default-deny on the tool call (B3.1). The system prompt is not a control.

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.3": """
**What it covers.** Poison one retrieved document and watch the agent act on it with the user's authority.

**Why a security engineer needs it.** Anyone who can write into a corpus the agent reads can steer it, using the victim's authority rather than their own. Nobody is phished and no credential leaks. The control it builds is: provenance marking at ingress (B2.6), and a rule that untrusted spans may not select a tool (B3.1).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.4": """
**What it covers.** Write one poisoned fact into memory and watch it steer a later, unrelated session.

**Why a security engineer needs it.** An attacker's instruction outlives the conversation that delivered it, and re-fires on requests from users who never met the original payload. The control it builds is: provenance survives into memory (B2.6), and memory writes are scoped to the identity that made them (B2.1).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.5": """
**What it covers.** Call one over-scoped tool with attacker-chosen arguments and see what it reaches.

**Why a security engineer needs it.** The agent uses a legitimate tool, with legitimate arguments, to do something nobody intended — and every log line looks normal. The control it builds is: default-deny authorization on the tool call (B3.1) and just-in-time authority (B2.4).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.6": """
**What it covers.** Have an agent inherit a privileged token and reach something its requester never could.

**Why a security engineer needs it.** The agent acts with more authority than the person who asked it to act, and the log records the service account rather than the human. The control it builds is: delegation that narrows (B2.3), just-in-time grants (B2.4), and default-deny (B3.1).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.7": """
**What it covers.** Have two agents share a credential, then try to work out which one made the call.

**Why a security engineer needs it.** Attribution fails before the incident starts: you cannot say which agent acted, so you cannot revoke one without breaking all of them. The control it builds is: per-workload identity with attestation (B2.1, B2.2) and a lifecycle that can revoke one (B2.5).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.8": """
**What it covers.** Execute model-authored code and enumerate what the process could touch.

**Why a security engineer needs it.** Model-authored code runs with the runtime's privileges — reaching the filesystem, the network and any credential in the environment. The control it builds is: sandboxed execution (B3.2) and egress control (B3.3).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.9": """
**What it covers.** Fire four realistic payloads at the review harness and compare keyword filtering against provenance.

**Why a security engineer needs it.** The pipeline reads attacker-controlled code and then takes actions — a confused deputy you built yourself. The control it builds is: instruction/data provenance: content the pipeline read may never drive a state-changing tool.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B1.10": """
**What it covers.** Send one poisoned inter-agent message and watch it propagate through the topology.

**Why a security engineer needs it.** One compromised agent steers every agent downstream of it, because a peer's message is treated as a colleague's instruction rather than as input. The control it builds is: message validation and provenance on the inter-agent channel (B3.5), and per-agent identity (B2.1).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.11": """
**What it covers.** Introduce an unregistered agent into the topology and have it receive delegated work.

**Why a security engineer needs it.** An agent nobody approved receives delegated work and delegated authority, and the orchestrator has no way to tell it apart from a legitimate worker. The control it builds is: a registry of approved agents with identity-bound admission (B2.5) and an audit trail per hop (B2.7).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.12": """
**What it covers.** Let one fabricated fact travel three hops and watch its confidence rise as its provenance disappears.

**Why a security engineer needs it.** A single fabrication becomes a shared premise, and by the third hop nothing in the system records that it was ever uncertain. The control it builds is: verification against ground truth before a claim propagates (B3.5).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.13": """
**What it covers.** Run a loop with no ceiling and count what it consumes before anything notices.

**Why a security engineer needs it.** An agent consumes budget, tokens, API quota or downstream capacity without bound, and the failure is denial of service against your own systems. The control it builds is: budgets and stop conditions bound to the loop (B3.4).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.14": """
**What it covers.** Reconstruct who caused a deletion from a log that records only tool calls.

**Why a security engineer needs it.** You cannot say which user caused an action, or what made the agent decide — so the incident cannot be scoped and the action cannot be attributed. The control it builds is: attribution carried on every hop, in a store the agent cannot write to (B2.7).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.15": """
**What it covers.** Push approval volume up and measure the point at which review quality collapses.

**Why a security engineer needs it.** The approval gate is recorded as a control and operates as a click. At volume it approves everything, including the one request that mattered. The control it builds is: approval reserved for irreversible actions, with everything else bounded by policy (B3.6).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.16": """
**What it covers.** Give an agent an objective it can satisfy the wrong way, and watch it do exactly that.

**Why a security engineer needs it.** The agent satisfies the letter of its instruction — including by reporting a success it did not achieve — and the transcript contains no lie you can point at. The control it builds is: an independent verifier that checks the outcome rather than the claim (B3.5).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.17": """
**What it covers.** Launder a request through a delegation chain to reach something the requester was denied.

**Why a security engineer needs it.** The delegation chain is used as a privilege-laundering path, and the agent's output becomes an unusually persuasive channel into a human decision. The control it builds is: ceiling-bound delegation (B2.3), attribution per hop (B2.7) and marking machine-generated output as such (B3.6).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.18": """
**What it covers.** Roll the twelve risks up into families, find which agent carries each, and check that every row has an owner.

**Why a security engineer needs it.** A list of risks is read once. Without a component, a control and an owner against each row, nothing in it is actionable and nothing in it is re-checkable when CyberTravels grows a fifth agent. The control it builds is: four columns — scene, component, control, owning lesson — and a rule that no row ships without the fourth.

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"B1.19": """
**What it covers.** The full control index for CyberTravels: the twelve controls that were required before agents existed, the ten the agents added, what each is scored at today, and the lesson that owns it.

**Why a security engineer needs it.** A control list written the week after shipping agents covers the new rows and reports coverage against the wrong denominator. Vulnerability scanning, supply chain, environment segregation, encryption at rest and in transit, input validation, change management, DMZ termination, credentials, PKI, key lifecycle and logging did not stop applying — several of them are what the agents broke. The control it builds is: one index with an era column, a three-valued status measured against what runs, an owner per row, and coverage reported per era rather than blended.

This is an **index** lesson. It is the reference you come back to, and the place a programme gets sequenced from.
""",

"E2.6": """
**What it covers.** Authenticate with a canary and watch a zero-threshold alert fire; then salt a benchmark and read the cheat-attempt rate as a leading indicator.

**Why a security engineer needs it.** Every other detector needs a threshold, and every threshold is a trade. Deception needs neither — but only if the bait is placed where the agent actually looks, and rotated before it is learned. The control it builds is: canary tokens in config, environment and artifact metadata (C4.4), and honeypot tasks salted into the benchmark whose cheat path is logged rather than rewarded (C10.3).

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

}

# The lessons added with the five-phase Function E restructure — see
# about_new.py, kept separate for the same reason framing_new.py is.
from .about_new import ABOUT as _NEW      # noqa: E402
for _k, _v in _NEW.items():
    assert _k not in ABOUT, f"{_k} already has an entry"
    ABOUT[_k] = _v

# Function D rebuild.
from .framing_d import ABOUT as _C_ABOUT  # noqa: E402
ABOUT.update(_C_ABOUT)

# ---------------------------------------------------------------- Function G
ABOUT.update({
 "A1.0": "What an agent is — software that plans, calls tools and acts on what "
         "it reads — and a map of the seven components you build across this "
         "chapter, with the edges where trust changes marked before any of them "
         "is written.",
 "A1.1": "The reasoning loop in three stages: the model proposes, your code "
         "disposes, and something independent of the model verifies. Plus the "
         "exit condition, which cannot be the model agreeing that it is done.",
 "A1.2": "Two MCP resource servers behind a process boundary, split by trust "
         "domain rather than by convenience, each with its own audience — and "
         "why a tool called in-process leaves nowhere to put a check.",
 "A1.3": "Three principals in every agent action: the human who asked, the "
         "workload that acted, and the individual call. Each gets a name, and "
         "the human's token is shown to grant nothing downstream.",
 "A1.4": "RFC 8693 token exchange: one audience, one scope, two minutes, minted "
         "after the model has chosen and verified at the resource server — "
         "with least privilege keyed to the human's role rather than the "
         "agent's.",
 "A1.5": "Agent memory built so it cannot become a persistence mechanism: "
         "origin recorded with content, recall scoped to one person, and delete "
         "and export both present.",
 "A1.6": "Agent-to-agent messaging with a signed envelope that names its "
         "sender, carries the human through every hop, labels a peer's text as "
         "data, and stops at a hop ceiling.",
 "A1.7": "The two ceilings on an agent loop — a human gate on irreversible "
         "actions, and budgets on steps and tool calls — including what a run "
         "returns when it hits one, and why a present-but-saturated gate is not "
         "a control.",
 "A2.0": "What separates a demo from a system: a trace, an audit trail and an "
         "evaluation. The lesson measures the gap before building any of them, "
         "because the list is shorter and more useful than \"add logging\".",
 "A2.1": "The agent run as spans — which agent, which step, which tool, what "
         "the delegated token said — with one trace id joining reasoning to "
         "action, secrets summarised rather than carried, and refusals recorded "
         "with the boundary that produced them.",
 "A2.2": "The four questions an audit trail has to answer — which human, which "
         "workload, which call, what motivated it — and what append-only "
         "actually requires beyond a convention not to issue an UPDATE.",
 "A2.3": "An evaluation suite over the agent you built: cases that fail on the "
         "old build, scores with intervals, and a test for the dilution that "
         "lifts a number without changing a system.",
 "A2.4": """
**What it covers.** The three surfaces of one agentic run that can be scored separately — the tool-call trajectory, the answer, and the answers no recorded truth reaches — and which of the three actually needs a model. Exact-match tool-call accuracy against the two weaker matchers that score higher on the same runs, output accuracy with unscoreable runs kept out of the denominator, and a model used as judge with a rubric, an `undetermined` verdict and a validation pass against the labelled subset.

**Why a security engineer needs it.** Every later function quotes an agent number at somebody: a recall figure in Function C, an attack success rate in D, a detection rate in E, a control indicator in F. All of them are this lesson's problem in a different costume — a rate is not a measurement until the matcher, the denominator and, where a model graded it, the judge's agreement with ground truth are stated beside it. The control it builds is the habit of publishing those three before the number they qualify.
""",

 "A2.5": "The handover into Function B. Every component built in this function "
         "re-read as an attack surface, every control re-read as something with "
         "a bypass, and the agent's blast radius measured as the number the "
         "next function argues with.",
})

ABOUT.update({
 "B2.6": "Marking untrusted text where it enters, in the file the reader "
         "already wrote: a Span carrying its origin, assigned at the boundary "
         "because that is the only place that honestly knows, and rendered to "
         "the model with delimiters a span cannot forge. Including the part "
         "people skip — marking is not filtering, and this closes nothing on "
         "its own.",
 "B2.8": "Turning an append-only convention into a detectable property: each "
         "audit row carries the hash of the one before it, so an edit, a "
         "deletion or an insertion anywhere breaks every hash after it and is "
         "visible in one pass. What it does not do is stop the write, which is "
         "why B3.8 moves the log somewhere the workload cannot reach.",
})

ABOUT.update({
 "B2.1": "Replacing a hand-edited set of agent names with a registry: "
         "identities as records that carry an approver, a registration time "
         "and a state, so the system can answer when an identity started "
         "existing and whether it still should.",
 "B2.2": "The bootstrap problem — a workload needs a credential to prove who "
         "it is and has to prove who it is to get one — answered by not "
         "issuing a first secret at all. Attestation against properties the "
         "platform already observes, for a short-lived identity document.",
 "B2.3": "Making a delegation chain narrow rather than merely exist: each hop "
         "bounded by what the hop before it held, and the actor claim nested "
         "so an investigator reads every hop instead of the last one.",
 "B2.4": "Binding a delegated token to the exact call it was minted for, so a "
         "captured token cannot be replayed against different arguments — "
         "including a clear statement of what that does not close, which is "
         "whether the object belongs to the caller.",
 "B2.5": "The non-human identity lifecycle: rotation, revocation that takes "
         "effect at the next call rather than the next restart, and finding "
         "orphans in both directions.",
 "B2.7": "Recording what motivated an action, not only who took it — the "
         "fourth investigation question, answerable only once ingress marks "
         "where text came from, and recorded as a digest rather than the text.",
})

# Chapter B3, rewired onto the tree the reader built. Each entry names the
# mechanism rather than restating the risk, because by B3 the reader has the
# system in front of them and the question is what changes in it.
ABOUT.update({
 "B3.1": "Replacing a lookup table that answers yes or no with a decision that "
         "answers why: one call per tool, evaluated on identity, tool and "
         "arguments, returning a reason and any obligations. Including what "
         "default-deny actually means — the default *branch* is a denial, not "
         "merely that the list is an allow-list with a permissive fallback.",
 "B3.2": "A sandbox profile as an allow-list in three dimensions — paths, "
         "environment, hosts — and the half teams skip: measuring what the "
         "running process actually has and reporting the gap. A profile "
         "deployed without the isolation that enforces it keeps describing a "
         "containment that was never applied.",
 "B3.3": "Egress control for a destination chosen at run time by a model, "
         "which is what makes it different from a firewall rule written "
         "against a deployment. Both halves: the destination, and what is "
         "being sent to it — because a vendor API the agent is supposed to "
         "call is a perfectly good channel for data to leave through.",
 "B3.4": "Ceilings that bound what the loop does to any one place, not only "
         "how long it runs: per-target call limits and a token budget, with "
         "the exhausted ceiling named so the incident is actionable rather "
         "than just a stopped run.",
 "B3.5": "The return path, which every outbound control leaves open: a schema "
         "per tool for the shape, and an independent verifier for the content, "
         "because a result that conforms perfectly can still answer a question "
         "nobody asked. Conformance is a statement about the serialiser.",
 "B3.6": "Measuring an approval gate rather than enabling one — approvals per "
         "reviewer per hour against what reading one takes — and the trap that "
         "makes it necessary: coverage stays at 100% while review collapses, "
         "and the risk register records a control that has stopped being one.",
 "B3.7": "Moving controls that each live where they were convenient to write "
         "behind a single entry point, and the number that finds the agent "
         "still holding a direct route. Plus the cost, stated rather than "
         "hidden: one choke point is a single point of failure and a queue.",
 "B3.8": "The channel no per-run check can see: an artefact one run writes and "
         "an unrelated run reads. Per-run namespaces, a write-once cache, "
         "provenance verified at consumption, and a query that reports the "
         "surfaces actually crossing between runs.",
 "B3.9": "Turning a control off as a recorded, scoped, expiring decision — a "
         "reference, a reason, a named approver and an end date, none of them "
         "optional — and counting the exemptions that have run out and are "
         "still in the file, which is a control set describing a system nobody "
         "is running.",
 "B3.10": "Building the third option for an agent that notices something "
          "outside its task, and the three properties that decide whether it "
          "is ever used: cheap, non-terminal, signposted in the prompt. Get "
          "one wrong and the tool is present and never called, which is "
          "indistinguishable from an agent that noticed nothing.",
 "B3.11": "Containment for the coding agent in the developer's own IDE, which "
          "has none of the controls it helped build and holds git credentials, "
          "cloud credentials and a shell. Ordered by the friction a developer "
          "feels — credential deny-list, then workspace confinement, then "
          "command review — because the guard they notice is the one that "
          "gets switched off, and a configuration with everything disabled "
          "still reports as compliant.",
})

# Function C, rewired onto the pipeline the reader builds in cybertravels/appsec/.
# Each entry names the stage's mechanism and what that stage is allowed to
# claim, because by B the reader has a pipeline and the question is what its
# output means.
ABOUT.update({
 "C2.0": "The pipeline as one system, split by what each half can honestly "
         "assert: before a deploy there is source and no running thing, so "
         "every finding is a hypothesis; after it there is a disposable "
         "replica, so a finding can be demonstrated. Including where the "
         "pipeline lives, and why exempting it from its own stages is the "
         "expensive choice.",
 "C2.1": "What separates a harness from a loop with a model in it: structured "
         "output, a verifier that is not the producer, and a budget that stops "
         "with the work unfinished. Built around the failure that does not "
         "announce itself — a model grading its own findings files a clean "
         "trace either way.",
 "C2.2": "A threat model derived from the tree rather than remembered from a "
         "workshop: assets from the schema, entry points from the code, trust "
         "boundaries from the layout — plus the column a machine cannot fill "
         "in, and a drift check that turns 'this is out of date' into a list.",
 "C2.3": "Two passes, and why the split follows from the defects rather than "
         "from taste: deterministic rules for what a pattern can express, a "
         "model for the class where the defect is the absence of a call and "
         "there is nothing to match at any ruleset width. Including the case "
         "in between — a house wrapper that makes every rule naming the "
         "library blind.",
 "C2.4": "Two cheap stages that decide whether the queue is usable: collapsing "
         "the reports of one defect into one row while keeping how many "
         "independent tracks reached it, and refuting the finding that names a "
         "function nobody wrote — which is otherwise perfectly formed.",
 "C2.5": "Asking whether an external caller can reach the sink before anybody "
         "is paged, with the property that decides how the answer may be used: "
         "the walk over-approximates, so it is safe to rank with and unsafe to "
         "delete with, and an unreachable sink is reported as unreachable.",
 "C2.6": "A disposable replica, and the refusal that makes it one — a stage "
         "that quietly downgrades to something safe-looking produces output "
         "nobody can interpret. Plus the isolation bug the stage finds in "
         "itself, because a replica has to be checked rather than assumed.",
 "C2.7": "What a dependency scan actually says — nothing declared has a known "
         "vulnerability — and the two checks that say something about the "
         "system: reconciling the manifest against what the code imports, and "
         "reading the compiled artefact that no manifest entry covers.",
 "C2.8": "Turning hypotheses into demonstrations against the replica, and the "
         "half that matters as much: a hypothesis that cannot be demonstrated "
         "is dropped rather than shipped as a medium somebody has to carry. An "
         "exploit that does not fire is undetermined, not refuted.",
 "C2.9": "Composing confirmed findings into sequences and scoring the chain "
         "rather than the links, because a chain is invisible from inside a "
         "queue row — with the rule that keeps it a finding: every link "
         "confirmed, or what you have is a story.",
 "C2.10": "The offensive loop, and the control that has to sit outside it. "
          "Scope enforced at the request boundary rather than requested in a "
          "prompt, because a prompt-level rule is addressed to the component "
          "an attacker is trying to influence.",
 "C2.11": "What full source actually buys, which is not a longer list: every "
          "candidate carrying the path that reaches it and the authorisation "
          "predicate on that path, so presence stops being reported where "
          "reachability was the question.",
 "C2.12": "Keeping observation and inference apart structurally rather than "
          "editorially — an inference cannot carry a severity, an observation "
          "cannot exist without evidence — and publishing the ratio, which is "
          "what makes the observed part worth acting on.",
 "C2.13": "Why endpoint coverage is the wrong denominator for object-level "
          "authorisation, and the grid that is the right one: roles by objects "
          "by verbs, with the untested cells ranked by blast radius rather "
          "than listed.",
 "C2.14": "The preflight an offensive agent starts behind: a gate rather than "
          "a checklist, refusing until every control is present — including "
          "telling the SOC, because unannounced offensive traffic is "
          "indistinguishable from the real thing by design.",
 "C2.15": "Calibrating severity from what this run established rather than "
          "copying it from the rule that fired, and reporting per-stage "
          "economics instead of a finding count — what each stage cost and "
          "what it removed.",
 "C2.16": "The stage whose wrong outcome looks exactly like the right one. "
          "Three pieces of evidence for a patch, none of them the scanner "
          "going quiet, and the one that is usually skipped: a regression test "
          "that fails against the unpatched code.",
 "C2.17": "Slicing context on the source-to-sink path rather than on distance, "
          "and the case that decides the rule — a defect that is the "
          "difference between two functions needs both of them in the window, "
          "and the cut is measured rather than claimed.",
 "C2.18": "Binding control claims to a deployment so they can be re-checked "
          "rather than re-asserted: per-control verdicts with evidence URIs, "
          "framework mappings gathered once, drift against the last "
          "attestation — and two controls capped at PARTIAL because this "
          "pipeline cannot prove them.",
 "C2.19": "A reference implementation read as a reference rather than bought "
          "as a product: mapping its stages onto the ones you built, finding "
          "what it does not have, and scoring it against a key it has never "
          "seen before trusting its output.",
})

# Function D, rewired onto cybertravels/redteam/. Each entry names what the
# lesson builds and the claim it is allowed to make, because by C the reader
# has a running system and the question is what an attack result means.
ABOUT.update({
 "D1.0": "The arithmetic an offensive result needs before it is a finding: a "
         "criterion stated before the run and applied by something that is not "
         "the model under test, a rate with an interval that behaves at the "
         "ends, benign cases so a technique that fires on everything cannot "
         "report a perfect score, and an ablation that separates what the "
         "model did from what the scaffolding did.",
 "D1.1": "Inventorying the paths by which text somebody else wrote reaches the "
         "agent, with the column an integration list does not have — who can "
         "write here, and does it arrive labelled. Including the path people "
         "miss, which is memory: an ingestion path with a delay.",
 "D1.2": "Writing into one of those paths and measuring how far it gets, with "
         "the criterion set on effect rather than on the model's reply — plus "
         "the gate that keeps the measurement honest when somebody tidies the "
         "planted instruction away and every trial silently measures nothing.",
 "D1.3": "What it takes to report a technique rather than a transcript: the "
         "same technique across phrasings and seeds, the seed spread published "
         "beside the rate, and the distinction between a technique and one "
         "phrasing that happens to work.",
 "D1.4": "Separating an agent from a person using only the shape of the trace "
         "— rate, gap variance, tool breadth, burst — and choosing the "
         "threshold by the cost of each mistake rather than by accuracy, since "
         "the two mistakes are never equally expensive.",
 "D1.5": "The signals that exist only across runs: an artefact one run wrote "
         "and another read, trajectories converging, a token appearing "
         "everywhere and in no baseline. Every run passes its own checks; the "
         "finding is between them.",
 "D1.6": "Why a rule's precision is the wrong thing to report to the people "
         "who have to work it. The same rule at two volumes, with the alert "
         "count and the analyst-days it implies — and the rule that gets "
         "muted while coverage still counts it.",
 "D1.7": "Triage when the queue is longer than the day: ranking, an explicit "
         "capacity cut, and the sample taken from below the line so the rule "
         "that closes most of the queue is itself measured rather than "
         "trusted.",
 "D1.8": "Deception as the one alert with no triage step, and the placement "
         "rule that keeps it that way — if you cannot name why nothing reads "
         "it, it is not a canary. Plus the two things canary write-ups skip: "
         "decay, and a volume threshold that swallows the conclusive alert.",
 "D1.9": "The second question about a kill switch, which is the one that gets "
         "asked on the night: what is still able to act after it is thrown. "
         "Measured as coverage over the act-paths, with the conflict between "
         "containment and evidence decided in advance rather than at 3am.",
 "D1.10": "Whether a finished run can be reconstructed from the record or only "
          "summarised — the four investigation questions put to the audit "
          "rows, the difference between replay and rerun, and the property "
          "that decides whether any of it is worth anything: that the actor "
          "cannot amend it.",
 "D1.11": "What has to exist before a finding is finished — an eval case, a "
          "control and a detection, each with a named owner — and the check "
          "that makes the eval case real: it must fail against the old build. "
          "A test that passes both ways is testing the weather.",
})

# Function E, rewired onto cybertravels/soc/. Each entry names the mechanism
# and the stage of the incident clock it sits on.
ABOUT.update({
 "E1.0": "The SOC as one system with a clock, and the observation the whole "
         "function turns on: the estate's detection content was written for "
         "an actor that acts a few times a minute and is now watching one "
         "that acts a thousand times an hour. Including where the clock "
         "actually goes, which is establishing who acted.",
 "E1.1": "Changing the denominator of a coverage report from products "
         "deployed to agent actions observable, so the uncovered rows come "
         "back named rather than as a percentage — and each product states "
         "what it cannot see, in its own row.",
 "E1.2": "The surfaces that change an agent's behaviour without a commit — "
         "model version, system prompt, retrieval index, tool descriptions, "
         "memory — baselined and diffed, with the column that makes it a "
         "finding: which of them anybody approves.",
 "E1.3": "Onboarding what the agent already emits, and settling the retention "
         "argument at the granularity where it can be won: per field, so the "
         "parts that make a run attributable outlive the parts that are "
         "somebody's prose.",
 "E2.1": "Tiering each telemetry source by the queries the SOC runs against "
         "it rather than by how important it feels, with the cost of each "
         "tier stated — because the alternative to a tiering decision is a "
         "retention cut applied everywhere at once.",
 "E2.2": "Detections whose subject is a non-human principal, mapped to ATT&CK "
         "and ATLAS, and written about relationships rather than volumes: a "
         "widened scope, an unseen tool pair, an action with no human behind "
         "it, an approval faster than reading.",
 "E2.3": "Why a workload-layer detection cannot see a platform-layer "
         "compromise, and the named primitives that can — a spawn under a "
         "profile that forbids it, a cache entry that differs from its "
         "manifest, an exemption that expired while the control stayed off.",
 "E2.4": "The gate between a model-written detection and a deployed one: a "
         "measured false-positive rate at the volume it will actually see, a "
         "technique mapping so coverage can be reasoned about, and a human "
         "who accepts it.",
 "E2.5": "Why a rule generated from an incident always matches that incident, "
         "and the benign corpus that tells an overfitted rule from a "
         "generalising one — the measurement that turns a guess into a rule.",
 "E3.1": "Supervising a triage loop rather than re-reading it: the list of "
         "alerts that bypass ranking entirely, and a sample of what the loop "
         "closed, so the closing rule is measured rather than trusted.",
 "E3.2": "Scoping the investigation itself, because an agent granted broad "
         "read to find the problem moves more data than most incidents do — "
         "a declared admission set per class, enforced at the tool boundary, "
         "with named human grants for anything beyond it.",
 "E3.3": "What a triage agent has to be given before it beats a junior "
         "analyst: the baseline, the known false positives, the crown-jewel "
         "map and the prior decisions — all of which the system already holds.",
 "E3.4": "The three responder instincts that are correct for a person and "
         "wrong for an agent, and the four questions that replace 'which "
         "user' — with the record answering them or naming which it cannot.",
 "E3.5": "Reconstruction as something pre-loaded rather than reached for once "
         "you are already behind, and the difference between a timeline built "
         "from inputs and one built from the agent's account of them.",
 "E3.6": "An investigation that is structurally allowed to change its mind: a "
         "plan record, a replan trigger that counts contradicting evidence, "
         "and abandoned branches that stay visible in the trace.",
 "E3.7": "Scoping an agentic incident by walking the delegation graph, "
         "because the agent that made the call is not the one that started "
         "the work, and the difference is one edge back.",
 "E3.8": "Correlation at fleet level, where coordination between runs that "
         "are supposed to be independent becomes visible — every run normal, "
         "the population not.",
 "E3.9": "Provenance discipline on intelligence intake: a claim with no "
         "source cannot carry a severity and cannot become a detection, "
         "because a synthesis loop's output is formatted identically whether "
         "anything backs it or not.",
 "E3.10": "A standing hunt over agent traces for what no rule was written "
          "against, hypothesis-first, with an explicit rule for when a "
          "finding graduates into a detection and when it means an existing "
          "rule is muted.",
 "E4.1": "One remediation policy keyed on blast radius and reversibility, "
         "from which every runbook's tier is derived rather than chosen by "
         "whoever wrote it — including why wide-and-reversible should be "
         "automated.",
 "E4.2": "What separates a human-in-the-loop tier from a confirmation dialog: "
         "specificity, an explicit statement of what cannot be undone, and a "
         "narrower option, so the choice is not act-or-abandon.",
 "E4.3": "Containment as a ladder climbed in order — throttle, scope-reduce, "
         "reroute, force approval, revoke, hard stop — so a response can "
         "start immediately with something reversible and escalate only as "
         "far as it has to.",
 "E4.4": "Stop authority as something rehearsed and timed rather than "
         "assigned: a named holder, a deputy, out-of-hours reachability that "
         "was tested by calling them, and a time-to-stop from a real attempt.",
 "E4.5": "A kill path independent of the agent's own execution path, in the "
         "order that matters — snapshot before terminate, revoke in the same "
         "action rather than after it, because terminating agents whose "
         "tokens stay valid leaves the persistence in place.",
 "E5.1": "Replay as reconstruction from the record rather than a rerun, with "
         "the two things that are explicitly not evidence about the run that "
         "happened: a second run, and the agent's own account of the first.",
 "E5.2": "A root cause record that names a control rather than a person or a "
         "narrative, with all three fields required — what failed, what "
         "should have detected it, and the specific change proposed.",
 "E5.3": "Choosing the layer a fix belongs in, ordered by how long a fix "
         "there survives, and the specific trap: fixing the prompt when the "
         "model can be argued out of the prompt.",
 "E5.4": "Closing a remediation on a re-measurement rather than on a ticket, "
         "with the before and after attached to the incident — and an "
         "indicator that cannot be measured reported as unmeasured rather "
         "than as a pass.",
 "E5.5": "The policy change as a diff generated from the root cause record, "
         "carrying the incident as its evidence and stating what it does not "
         "fix — because a change presented as closing everything is one "
         "nobody scrutinises.",
 "E5.6": "Which notification clocks a given incident starts, counted from "
         "awareness rather than from confirmation, and why 'we were still "
         "investigating' describes the period the clock was running rather "
         "than excusing it.",
})

# Function F, rewired onto cybertravels/governance/ — the package that
# measures the controls the other functions built, by calling them.
ABOUT.update({
 "F1.0": "Governance stated as a table rather than a value: each property a "
         "trustworthy-AI claim makes, the function that owns it, and the "
         "artefact that evidences it — because a property with no artefact "
         "is a value, and values do not survive an audit.",
 "F1.1": "Turning a framework control into a key control indicator that can "
         "be computed this week without asking anybody, since the only "
         "alternative is a measurement taken once, at audit time, by "
         "somebody who knows what answer is wanted.",
 "F1.2": "Why an AI inventory built by survey returns the complement of the "
         "set you want, and how to derive one instead — plus the two "
         "directions of orphan, because teams check one.",
 "F1.3": "Tiering by what a deployment can do — autonomy, data reach, "
         "external effect — and the comparison that makes the case: what "
         "tiering by model name would have said about the same system.",
 "F1.4": "Mapping controls outward to frameworks rather than inward from "
         "them, so the output is which clauses nothing covers — and the "
         "prior question, which is whether an existing control already "
         "applies to a new principal type.",
 "F1.5": "What an evaluation result is and is not evidence of: a best-of-k "
         "demonstration, a rate with no interval, a score against tuned-on "
         "cases, and conformance reported where accuracy was asked for.",
 "F1.6": "Separating guardrails that something enforces from outcomes that "
         "something measures, and refusing to file the third kind — enforced "
         "by nothing, measured by nothing — as a control.",
 "F1.7": "What continuous control verification can automate, which is "
         "gathering the artefact, and what it cannot, which is the adequacy "
         "judgement and the name that goes on it.",
 "F1.8": "The vendor assessment's two blind spots: AI features that arrive "
         "enabled by default so no purchase event triggers a review, and the "
         "sub-processor chain behind the vendor, which is where the data "
         "actually goes.",
 "F1.9": "Which changes to an agentic system are changes for governance "
         "purposes, decided on whether they alter behaviour rather than on "
         "whether they touched code — which is how re-indexing gets filed as "
         "maintenance.",
 "F1.10": "Where the estate is held, and the distinction that matters: a "
          "part two functions share is not safer than one nobody holds, "
          "because it is a gap that looks covered from both sides.",
 "F1.11": "How the classical model-risk playbook breaks once the model can "
          "act — a validation complete on conceptual soundness, accuracy and "
          "monitoring, and silent on authority, reversibility, blast radius, "
          "reachability and containment.",
 "F1.12": "Tracing each handoff to the artefact the receiving function should "
          "now be holding, because a handoff is nobody's deliverable and "
          "therefore nobody's deadline.",
 "F1.13": "Measuring the control set against the running system rather than "
          "against the register, so removing a control moves the number — "
          "with the known absences shipped alongside, since a register "
          "reporting no gaps on a system with gaps is one nobody should "
          "believe.",
 "F2.1": "One control set mapped to many regimes instead of one programme "
         "per regime, with the reuse counted — the number that argues "
         "against quadrupling the work for an eighty per cent overlap.",
 "F2.2": "The four specific things that move a deployer into a provider's "
         "obligations, each of which an engineering team does without "
         "thinking of it as a regulatory event — and the show-me test for "
         "turning prose requirements into controls.",
 "F2.3": "Choosing the framework that covers the most of the controls you "
         "actually have as a spine and supplying the remainder from the "
         "others, rather than building a programme shaped like a document.",
 "F2.4": "Finding the sector rules you are already complying with under "
         "another name, which is usually the cheapest control in the "
         "programme — an agent that decides is a model, and model rules "
         "already have inventory, validation and change requirements.",
 "F2.5": "Where personal data actually is once an agent has touched it, and "
         "how far an erasure request reaches — including the two surfaces it "
         "does not reach, one of which has no good answer.",
 "F2.6": "Breaking a disclosure deadline into its phases to find the one "
         "that consumes it, which for an agentic incident is establishing "
         "who acted rather than containment.",
 "F2.7": "What supervisory documentation can contain for a system with no "
         "deterministic reasoning — purpose, authority, bounds, a run "
         "record, decisions and known limitations — none of which is an "
         "explanation of the model and all of which a supervisor can use.",
 "F2.8": "Whether the record can say under whose authority an autonomous "
         "action was taken, asked as a governance question in advance rather "
         "than as an investigation question afterwards.",
 "F2.9": "Preparing the assurance conversation as arithmetic rather than "
         "rhetoric: accuracy and conformance reported separately, coverage "
         "with the gaps named first, and the three openings that actually "
         "get used.",
 "F3.1": "Translating blast radius into consequence, so the sentence a board "
         "hears is about what one compromised run can move rather than about "
         "which scope the agent holds.",
 "F3.2": "Approving a rung of autonomy rather than a tool, because a "
         "per-tool review queue becomes a bottleneck and then a bypass — "
         "with the top rung left ungranted and the reason stated.",
 "F3.3": "Sequencing by winnability rather than visibility, weighting the "
         "workflow whose controls the next one inherits over the one the "
         "sponsor mentioned.",
 "F3.4": "The two functions that fall between org charts — harness "
         "engineering and research — and the failure mode of both, which is "
         "not dramatic: they quietly do not happen.",
 "F3.5": "Replacing activity metrics with exposure ones, starting from the "
         "observation that an activity metric moves in the right direction "
         "when the work gets bigger.",
 "F3.6": "What a flat no costs in visibility, and what makes a conditional "
         "yes enforceable rather than aspirational — testable, time-bound, "
         "owned, and with a stated consequence.",
 "F3.7": "A build order in which each stage's output is the next stage's "
         "input, and the comparison with the order that produces demos — "
         "including why the red team comes last.",
 "F3.8": "Organising around recovery rather than around enumerating the "
         "failure modes of a probabilistic system, using four numbers this "
         "curriculum has already produced.",
})
