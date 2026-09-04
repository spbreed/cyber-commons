"""One paragraph per lesson: what it covers, and why it matters in a
security context.

A reader who lands on a single lesson — from a search result, a link in a
ticket, a colleague's message — has no idea what they are looking at. The
hook is deliberately a consequence rather than an orientation, so it does
not do this job; this does, and the build refuses a lesson without one.
"""

ABOUT: dict[str, str] = {

"A1.0": """
**What it covers.** Place the five functions of the commons on one diagram and find where your own work sits.

**Why a security engineer needs it.** Without a shared architecture, "secure the agent" has no referent, and every control argument is really an argument about two different systems. The control it builds is: one picture, three chapters: the architecture and its risks, then identity and ingress, then runtime and the gateway.

This is an **orientation** lesson. It has no code — it exists so the chapters after it are read in the right order.
""",

"A1.1": """
**What it covers.** Build the component graph and the five topologies, then trace one request through each and see where the trust boundary sits.

**Why a security engineer needs it.** Without a shared picture, 'secure the agent' has no referent and every later risk lands nowhere in particular. The control it builds is: one component map and five topologies, named once and reused by every lesson that follows.

This is a **mapping** lesson: every later risk and control in this function names a component from the picture it draws.
""",

"A1.2": """
**What it covers.** Send an override through the ingress component and watch the agent's goal change.

**Why a security engineer needs it.** The user redirects their own agent past the behaviour the operator specified — bounded by their own authority, and therefore the milder of the two injection risks. The control it builds is: provenance at ingress (A2.6) and default-deny on the tool call (A3.1). The system prompt is not a control.

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.3": """
**What it covers.** Poison one retrieved document and watch the agent act on it with the user's authority.

**Why a security engineer needs it.** Anyone who can write into a corpus the agent reads can steer it, using the victim's authority rather than their own. Nobody is phished and no credential leaks. The control it builds is: provenance marking at ingress (A2.6), and a rule that untrusted spans may not select a tool (A3.1).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.4": """
**What it covers.** Write one poisoned fact into memory and watch it steer a later, unrelated session.

**Why a security engineer needs it.** An attacker's instruction outlives the conversation that delivered it, and re-fires on requests from users who never met the original payload. The control it builds is: provenance survives into memory (A2.6), and memory writes are scoped to the identity that made them (A2.1).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.5": """
**What it covers.** Call one over-scoped tool with attacker-chosen arguments and see what it reaches.

**Why a security engineer needs it.** The agent uses a legitimate tool, with legitimate arguments, to do something nobody intended — and every log line looks normal. The control it builds is: default-deny authorization on the tool call (A3.1) and just-in-time authority (A2.4).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.6": """
**What it covers.** Have an agent inherit a privileged token and reach something its requester never could.

**Why a security engineer needs it.** The agent acts with more authority than the person who asked it to act, and the log records the service account rather than the human. The control it builds is: delegation that narrows (A2.3), just-in-time grants (A2.4), and default-deny (A3.1).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.7": """
**What it covers.** Have two agents share a credential, then try to work out which one made the call.

**Why a security engineer needs it.** Attribution fails before the incident starts: you cannot say which agent acted, so you cannot revoke one without breaking all of them. The control it builds is: per-workload identity with attestation (A2.1, A2.2) and a lifecycle that can revoke one (A2.5).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.8": """
**What it covers.** Execute model-authored code and enumerate what the process could touch.

**Why a security engineer needs it.** Model-authored code runs with the runtime's privileges — reaching the filesystem, the network and any credential in the environment. The control it builds is: sandboxed execution (A3.2) and egress control (A3.3).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.9": """
**What it covers.** Fire four realistic payloads at the review harness and compare keyword filtering against provenance.

**Why a security engineer needs it.** The pipeline reads attacker-controlled code and then takes actions — a confused deputy you built yourself. The control it builds is: instruction/data provenance: content the pipeline read may never drive a state-changing tool.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A1.10": """
**What it covers.** Send one poisoned inter-agent message and watch it propagate through the topology.

**Why a security engineer needs it.** One compromised agent steers every agent downstream of it, because a peer's message is treated as a colleague's instruction rather than as input. The control it builds is: message validation and provenance on the inter-agent channel (A3.5), and per-agent identity (A2.1).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.11": """
**What it covers.** Introduce an unregistered agent into the topology and have it receive delegated work.

**Why a security engineer needs it.** An agent nobody approved receives delegated work and delegated authority, and the orchestrator has no way to tell it apart from a legitimate worker. The control it builds is: a registry of approved agents with identity-bound admission (A2.5) and an audit trail per hop (A2.7).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.12": """
**What it covers.** Let one fabricated fact travel three hops and watch its confidence rise as its provenance disappears.

**Why a security engineer needs it.** A single fabrication becomes a shared premise, and by the third hop nothing in the system records that it was ever uncertain. The control it builds is: verification against ground truth before a claim propagates (A3.5).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.13": """
**What it covers.** Run a loop with no ceiling and count what it consumes before anything notices.

**Why a security engineer needs it.** An agent consumes budget, tokens, API quota or downstream capacity without bound, and the failure is denial of service against your own systems. The control it builds is: budgets and stop conditions bound to the loop (A3.4).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.14": """
**What it covers.** Reconstruct who caused a deletion from a log that records only tool calls.

**Why a security engineer needs it.** You cannot say which user caused an action, or what made the agent decide — so the incident cannot be scoped and the action cannot be attributed. The control it builds is: attribution carried on every hop, in a store the agent cannot write to (A2.7).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.15": """
**What it covers.** Push approval volume up and measure the point at which review quality collapses.

**Why a security engineer needs it.** The approval gate is recorded as a control and operates as a click. At volume it approves everything, including the one request that mattered. The control it builds is: approval reserved for irreversible actions, with everything else bounded by policy (A3.6).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.16": """
**What it covers.** Give an agent an objective it can satisfy the wrong way, and watch it do exactly that.

**Why a security engineer needs it.** The agent satisfies the letter of its instruction — including by reporting a success it did not achieve — and the transcript contains no lie you can point at. The control it builds is: an independent verifier that checks the outcome rather than the claim (A3.5).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.17": """
**What it covers.** Launder a request through a delegation chain to reach something the requester was denied.

**Why a security engineer needs it.** The delegation chain is used as a privilege-laundering path, and the agent's output becomes an unusually persuasive channel into a human decision. The control it builds is: ceiling-bound delegation (A2.3), attribution per hop (A2.7) and marking machine-generated output as such (A3.6).

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A1.18": """
**What it covers.** Roll the twelve risks up into families, find which agent carries each, and check that every row has an owner.

**Why a security engineer needs it.** A list of risks is read once. Without a component, a control and an owner against each row, nothing in it is actionable and nothing in it is re-checkable when CyberTravels grows a fifth agent. The control it builds is: four columns — scene, component, control, owning lesson — and a rule that no row ships without the fourth.

This is a **risk** lesson: it shows the failure happening before anything tries to stop it, so the control that follows is answering something you have already watched go wrong.
""",

"A2.1": """
**What it covers.** Separate the three identities and show a downstream service authorising on the agent while attributing to the human.

**Why a security engineer needs it.** A shared service account answers 'what ran' and destroys 'for whom' — so no later control can be conditioned on the caller. The control it builds is: a distinct identity per workload, carrying the human principal alongside it, asserted on every call.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A2.2": """
**What it covers.** Exchange an attestation for a credential, then show a copied secret failing the same exchange.

**Why a security engineer needs it.** A pre-shared secret in an image or an environment variable is copyable, so possession stops being proof of identity. The control it builds is: platform attestation exchanged for a short-lived, workload-bound credential.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A2.3": """
**What it covers.** Run both narrowing rules against a request that passes one and fails the other.

**Why a security engineer needs it.** Subset-only lets a privileged user hand an agent authority it must never hold; ceiling-only lets the agent exceed the person who asked. The control it builds is: token exchange that intersects presented scope with the actor's ceiling, and records the chain.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A2.4": """
**What it covers.** Issue a scoped grant, use it, then replay it after expiry and after the task closed.

**Why a security engineer needs it.** Permanent scope makes every injection a successful one, because the authority is always there when the attacker arrives. The control it builds is: short-lived, purpose-bound grants issued per task and expiring with it.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A2.5": """
**What it covers.** Admit agents against a registry and show an unregistered one refused at the door.

**Why a security engineer needs it.** Agents accumulate with no owner and no expiry, and an unregistered agent joins a topology as a peer. The control it builds is: a registry with a named owner, an expiry, and admission bound to a registered identity.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A2.6": """
**What it covers.** Tag every span at ingress, then show the same payload refused through six different entry paths.

**Why a security engineer needs it.** Concatenation destroys the one fact that separates an operator instruction from an attacker's: where it came from. The control it builds is: provenance tagging at every ingress point, and a rule that only trusted origins may select a tool.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A2.7": """
**What it covers.** Answer 'which user caused this deletion' from the trace, then try the same on a trace missing one field.

**Why a security engineer needs it.** Without the motivating input, root cause cannot be established at all; without the principal, nothing can be attributed. The control it builds is: per-hop attribution written to an append-only store outside the agent's reach.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A2.8": """
**What it covers.** Spoof a transcript, watch the in-band check pass it, then watch the hash chain and the host-syscall reconciliation both refuse it.

**Why a security engineer needs it.** An agent that escapes its container can rewrite the record of what it did — and every detective control downstream is then reporting on data the subject controls. The control it builds is: out-of-band capture (C1.1), a hash-chained WORM transcript store (C1.2) and logging-plane isolation (C1.3). Reconcile the two streams; divergence is the signal.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.1": """
**What it covers.** Evaluate the same call under allow-by-default and deny-by-default policy and compare what gets through.

**Why a security engineer needs it.** Allow-by-default authorization is defeated by any argument the model can be persuaded to produce. The control it builds is: policy evaluated per call on (identity, tool, arguments, resource), denying unless a rule permits.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.2": """
**What it covers.** Run the same code inside and outside the sandbox and enumerate what each could reach.

**Why a security engineer needs it.** Model-authored code inherits the runtime's reach, including any credential mounted into the environment. The control it builds is: execution in an isolate with no ambient credentials, a bounded filesystem and no default network.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.3": """
**What it covers.** Attempt exfiltration to several destinations under an allow-list and see which survive.

**Why a security engineer needs it.** An agent with unrestricted egress turns any successful injection into data loss. The control it builds is: an allow-list at the network boundary, enforced where the agent cannot rewrite it.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.4": """
**What it covers.** Run a looping agent against each ceiling and record which one fires first.

**Why a security engineer needs it.** Without a ceiling the loop runs until an external system stops it, and the failure mode is denial of service against yourself. The control it builds is: ceilings bound to the loop, with the run terminating rather than degrading when one is hit.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.5": """
**What it covers.** Pass a fabricated claim through a schema check and then through a ground-truth verifier.

**Why a security engineer needs it.** An unverified claim becomes a shared premise, and a peer message is trusted more than a document it is no safer than. The control it builds is: schema validation plus an independent verifier before any claim propagates.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.6": """
**What it covers.** Route actions by reversibility and measure how many reach a human under each policy.

**Why a security engineer needs it.** An approval queue at volume approves everything, and the risk register still records it as a control. The control it builds is: approval reserved for irreversible actions only, with machine-generated content labelled as such.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.7": """
**What it covers.** Route every call through one gateway and show the same policy holding for agents that never implemented it.

**Why a security engineer needs it.** Per-agent controls diverge as the fleet grows, and legacy downstreams force a static credential back into agent code. The control it builds is: a single enforcement point holding identity, policy, egress, budget and audit — with the credential for legacy systems held there rather than by the agent.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.8": """
**What it covers.** Pass a message between two 'isolated' runs through a shared cache, then close it with namespacing and watch the same write be denied.

**Why a security engineer needs it.** Any shared mutable surface is a channel. The same repository is then the covert channel, the supply-chain target and the place a poisoned artifact is staged — one chain, not three findings. The control it builds is: per-run namespaces bound to the run's workload identity (C2.1), an immutable write-once cache (C2.2), signing and provenance verified at consumption (C5.1, C5.2), admin plane off the workload path (C5.3), and scoring infrastructure the agent cannot reach (C10.4).

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.9": """
**What it covers.** Disable a classifier without an approved exemption and watch the platform refuse; then launch 50,000 agents under one that is approved.

**Why a security engineer needs it.** Classifiers off, no compensating cap, and tens of thousands of agents launched under that configuration. Each decision was defensible; the combination was never evaluated. The control it builds is: an exemption gate the platform enforces (C6.1), caps that tighten as coverage drops (C6.2), quotas on population and lifetime (C8.2), and an exemption register reviewed at fleet-launch approval (C6.4).

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"A3.10": """
**What it covers.** Plant a finding, run the agent with and without the tool, and compare what it does with what it says it wants to do.

**Why a security engineer needs it.** An agent that finds a live breach, reasons about telling someone, and has no tool for it, does nothing. Of roughly 1,200 agents that saw one, none reported it. The control it builds is: a report-to-human tool that is cheap, non-terminal and signposted (C9.1), a mandatory checkpoint on out-of-scope discovery (C9.4), and an abstain affordance scored neutrally (C10.2).

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.0": """
**What it covers.** Trace one finding from ingestion to a signed report and name the stage that decides whether it is true.

**Why a security engineer needs it.** A security pipeline built as if it were exempt from the risks it exists to find. The control it builds is: build the pipeline and the harness as one system, and hold both to the same evidence standard.

This is an **orientation** lesson. It has no code — it exists so the chapters after it are read in the right order.
""",

"B2.0": """
**What it covers.** What a harness is — the wrapper around a model that turns
generating text into getting work done — and the four moves of its loop, run
against a real CyberTravels finding with an actual LLM call in it.

**Why a security engineer needs it.** Every part of that wrapper is a security
decision: the tool surface is an authorisation problem, the verifier decides
what the pipeline is allowed to believe, and the budget is the only control
still standing once the model is the component you cannot trust. A harness whose
verifier is the model agreeing with itself does not fail loudly — it succeeds
incorrectly and files a clean trace.

This is the **opening** lesson of the chapter: it also sets out which techniques
belong before a deploy and which only work after one.
""",


"B2.2": """
**What it covers.** Turn an architecture map into a ranked threat model, then diff it after one entry point is added.

**Why a security engineer needs it.** Threat models are written once, by hand, against a system that has since changed. The control it builds is: stage 5: derive assets, entry points and attack vectors mechanically from the synthesised map.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.3": """
**What it covers.** Score grep, taint rules and model review against the same corpus, then combine them behind a confidence gate.

**Why a security engineer needs it.** Pattern matching floods the queue; the false-positive rate is what actually changed. The control it builds is: stage 7: deterministic rules for what rules do well, model reasoning for what rules cannot express.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.4": """
**What it covers.** Deduplicate findings across three analysis tracks, then verify each against the AST and drop the ones that reference code that is not there.

**Why a security engineer needs it.** Parallel analysis tracks report the same bug three times, and some of those bugs do not exist. The control it builds is: stages 8–9: consolidate overlapping findings, then cross-reference each one against syntax and imports to weed out hallucinations.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.5": """
**What it covers.** Build a call graph from entry points and partition findings into reachable, unreachable and unknown.

**Why a security engineer needs it.** A finding in dead code costs the same to triage as one on the login path. The control it builds is: stage 10: decide whether an external caller can actually reach the sink before anyone is paged.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.6": """
**What it covers.** Stand up an isolated replica, prove egress and credential isolation, and show what a destructive probe touches.

**Why a security engineer needs it.** Dynamic testing is run against staging, so a destructive probe becomes an incident. The control it builds is: stage 11: replicate the application in an isolated, disposable runtime with no path to production.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.7": """
**What it covers.** Turn static findings into executable probes against the replica and separate confirmed from unconfirmed.

**Why a security engineer needs it.** A SAST finding is a hypothesis, and hypotheses get argued about instead of fixed. The control it builds is: stage 12: generate and run an actual exploit against the sandbox, so the finding is confirmed or dropped.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.8": """
**What it covers.** Chain individually-medium findings into a critical path and show the severity the chain earns.

**Why a security engineer needs it.** Three medium findings are triaged as three mediums, and nobody notices they compose. The control it builds is: stage 13: combine validated findings into multi-step sequences and score the chain, not the links.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.9": """
**What it covers.** Validate four candidate patches on three axes and show which of them only made the scanner green.

**Why a security engineer needs it.** A patch that silences the scanner is indistinguishable from a patch that fixes the bug. The control it builds is: stage 14: generate the fix, re-run the exploit against the patched build, and require a regression test.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.10": """
**What it covers.** Recalculate severity from confirmed exploitation and reachability, then produce the per-stage escape economics.

**Why a security engineer needs it.** Severity is a label copied from the rule, so the queue is ordered by something that predicts nothing. The control it builds is: stage 15: calibrate severity from sandbox evidence, then report per-stage economics rather than a finding count.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.11": """
**What it covers.** Compare four context strategies against one bug and measure which are decidable and at what size.

**Why a security engineer needs it.** The model is given the repository and asked to be thorough, so the relevant line falls out of the window. The control it builds is: slice on the source-sink path, not on distance: the smallest context that still supports a severity decision.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.12": """
**What it covers.** Measure the default agent's blast radius and reachable credentials, then rank controls by friction.

**Why a security engineer needs it.** The IDE agent holds git credentials, cloud credentials and a shell, in an unmanaged environment. The control it builds is: the strongest containment a developer does not notice: credential deny-lists and workspace confinement first.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.13": """
**What it covers.** Run the control-intent analyser over ten real agent and MCP repositories and read the attestation it produces for each.

**Why a security engineer needs it.** Control claims are asserted in a spreadsheet and never bound to a deployment. Nobody can say which repo, image, role, identity, gateway and guardrail the claim was about, so it cannot be re-checked when any of them change. The control it builds is: eleven skills scoped to one deployment_id, emitting an in-toto/DSSE attestation whose predicate carries per-control verdicts, evidence URIs, framework mappings and drift — with sandbox-egress and injection-screening capped at PARTIAL because their claims are not provable.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"B2.14": """
**What it covers.** Map Mantis onto the 15 stages, parse its two output shapes, and score a sample against a held-out key.

**Why a security engineer needs it.** A reference implementation is adopted as a product, and its outputs are trusted without an eval. The control it builds is: map Mantis's stages onto the pipeline you built, then score it with your own held-out key before trusting it.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C1.0": """
**What it covers.** Take one published agentic attack and list what you would need to reproduce it.

**Why a security engineer needs it.** Offensive work that produces anecdotes: a result that worked once, on one target, with no rate and no reproduction. The control it builds is: a campaign with a stated criterion, a harness that separates the model effect from the harness effect, and a handoff that ends in a control.

This is an **orientation** lesson. It has no code — it exists so the chapters after it are read in the right order.
""",

"C1.1": """
**What it covers.** Drive a planner/executor pair against a local target and watch the scope guard refuse an out-of-scope host before the request leaves.

**Why a security engineer needs it.** Payload suggestions instead of attack chains — and an offensive loop with no hard scope enforcement, which is an incident with a project plan. The control it builds is: full target context before it swings, and scope enforced at the network layer rather than by a politeness clause in the prompt.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C1.2": """
**What it covers.** Run a campaign across the three surfaces and report a rate with its sample size, not an anecdote.

**Why a security engineer needs it.** A red-team result nobody can act on, because "it worked once" is not a rate. The control it builds is: systematic campaigns across all three surfaces, with measured success rates and a criterion agreed before the first payload.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C1.3": """
**What it covers.** Game the B2.1 harness deliberately, then close the hole you used.

**Why a security engineer needs it.** If the eval can be fooled, the assurance is theatre. The control it builds is: eval gaming, sandbagging, contamination and judge manipulation as test cases.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C1.4": """
**What it covers.** Write a finding a CISO can act on, with a replayable trace.

**Why a security engineer needs it.** The vulnerability is emergent behaviour, not a line of code. The control it builds is: reproducibility requirements for probabilistic systems.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.1": """
**What it covers.** Write a one-page research charter with a named consuming track.

**Why a security engineer needs it.** Research with a publication outcome and no control outcome. The control it builds is: choose problems that end in a deployable control; get funded.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.2": """
**What it covers.** Run a jailbreak taxonomy across Llama, GLM and Kimi and chart where they differ.

**Why a security engineer needs it.** Model cards read credulously. The control it builds is: adversarial robustness, jailbreak taxonomy, refusal analysis, capability elicitation.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.3": """
**What it covers.** Attempt targeted unlearning on an open-weight model and try to elicit the capability back.

**Why a security engineer needs it.** Claiming a capability was removed when it was only hidden. The control it builds is: concept erasure and orthogonalisation on open weights — with honest claims.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.4": """
**What it covers.** Invert embeddings from a local vector store and recover source text.

**Why a security engineer needs it.** Memorisation, extraction, embedding inversion, index poisoning. The control it builds is: measure extraction rates rather than assert privacy.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.5": """
**What it covers.** Sign a model artefact with Sigstore and detect a tampered adapter.

**Why a security engineer needs it.** Adapter and LoRA provenance, registry tampering, dependency confusion in agent ecosystems. The control it builds is: verify provenance; sign and attest artefacts.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.6": """
**What it covers.** Run one harness across three model families, separate the two effects, then contamination-check a public benchmark against a training window.

**Why a security engineer needs it.** Model effects and harness effects confounded, and published benchmarks overstating real-world capability. The control it builds is: multi-backbone runs on fixed seeds and corpora, plus contamination and construct-validity checks before any number is trusted.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.7": """
**What it covers.** Convert one finding into a policy another track adopts, and release it with a reproducibility README.

**Why a security engineer needs it.** Research output the platform team cannot deploy, and a function whose work stays invisible and uncredited. The control it builds is: hand over something deployable and evidenceable, handle disclosure, and leave a defensible public record.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.8": """
**What it covers.** Build the register from the report's own figures, find the chain three rows share, and check that every control has an owner.

**Why a security engineer needs it.** Ten classes of control failure, from a forged audit trail to a missing escalation path — and an incident report that gets read once and cited forever without any of them becoming testable. The control it builds is: t/E/C indexing so each item can be cited alone, control types and NIST anchors so the register is comparable to the one you already have, and a named owning lesson for every control.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.9": """
**What it covers.** Run the same query with and without a row policy, then work out which of the leaked things the platform could actually revoke.

**Why a security engineer needs it.** The blast radius was not the platform's. What leaked were credentials in five other providers' accounts, and the platform could revoke none of them. The control it builds is: row-level policies, credentials out of client-readable tables, and an admin plane the client cannot reach — the controls of A3.8, arriving at a database.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"C2.10": """
**What it covers.** Audit a four-statement scaffold, then run the one catalogue query that answers the critical half across every table at once.

**Why a security engineer needs it.** A failure that is invisible in testing, because nothing about the application's behaviour is wrong. One write-up puts it at 73% of generated applications carrying at least one issue. The control it builds is: a schema check in CI rather than an application test — and, better, a default that does not expose a table until something opts it in.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.0": """
**What it covers.** Put one agent trace and one human session side by side and list what separates them.

**Why a security engineer needs it.** A detection stack tuned for human tempo, watching an actor that acts a thousand times an hour and never repeats a session. The control it builds is: agent telemetry as a first-class data source, detections written for agent behaviour, and a stop lever that a human can actually pull in time.

This is an **orientation** lesson. It has no code — it exists so the chapters after it are read in the right order.
""",

"D1.1": """
**What it covers.** Run a triage loop over Wazuh alerts and supervise by exception.

**Why a security engineer needs it.** Supervising by re-reading everything the loop did. The control it builds is: know what the loop must escalate and sample the rest.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.2": """
**What it covers.** A/B a generic prompt vs a context-loaded one on the same alert set.

**Why a security engineer needs it.** Generic triage agents underperform your worst analyst. The control it builds is: feed the baseline, known FPs, crown-jewel map and prior decisions.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.3": """
**What it covers.** Generate and unit-test Sigma rules in CI; map coverage to ATT&CK.

**Why a security engineer needs it.** Coverage gaps nobody mapped. The control it builds is: detection-as-code with agents inside the CI loop.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.4": """
**What it covers.** Write five detections for agent misbehaviour and fire each one.

**Why a security engineer needs it.** Scope drift, unusual tool sequencing, off-hours autonomous action. The control it builds is: detections whose subject is a non-human principal.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.5": """
**What it covers.** Ship OTEL agent traces into OpenSearch and query them.

**Why a security engineer needs it.** Prompts, traces, tool calls and approvals never reach the SIEM. The control it builds is: onboard agent telemetry deliberately; decide retention.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.6": """
**What it covers.** Build the classifier on timing, sequencing and volume features.

**Why a security engineer needs it.** Your earliest Shadow Autonomy signal is invisible. The control it builds is: behavioural signatures separating agent from inherited human.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.7": """
**What it covers.** Change the model underneath and catch the detection regression.

**Why a security engineer needs it.** A detection that worked last month is silently degraded. The control it builds is: watch model updates, prompt changes, index refreshes, tool versions.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.8": """
**What it covers.** Build a synthesis loop that must cite or abstain.

**Why a security engineer needs it.** Unsourced confidence in synthesis loops. The control it builds is: provenance discipline; refuse claims without a source.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.9": """
**What it covers.** Run four platform detectors over one day of events and see which of them a generic anomaly score would have missed.

**Why a security engineer needs it.** Platform-layer compromise is invisible to workload-layer detection. The escape, the poisoned cache entry and the silently expired exemption all look like normal operation from inside. The control it builds is: named escape primitives rather than anomaly scoring (C1.4), cache integrity diffing against a manifest (C5.4), upload scanning (C3.4), secret scanning wired to automated revocation (C4.1), and exemption-state reconciliation (C6.3).

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.10": """
**What it covers.** Run per-run monitoring over a coordinated fleet and see nothing, then run the same data through a shared-artifact graph.

**Why a security engineer needs it.** Coordination between runs that are supposed to be independent is invisible to per-run analysis by construction. Every run looks normal; the population does not. The control it builds is: fleet-level analytics (C8.1), coordination signatures (C8.4), write-pattern anomalies (C2.4), a covert-channel inventory (C2.3), scope-expansion logging (C7.4) and noticed-but-unreported telemetry (C9.3, C9.2).

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D1.11": """
**What it covers.** Authenticate with a canary and watch a zero-threshold alert fire; then salt a benchmark and read the cheat-attempt rate as a leading indicator.

**Why a security engineer needs it.** Every other detector needs a threshold, and every threshold is a trade. Deception needs neither — but only if the bait is placed where the agent actually looks, and rotated before it is learned. The control it builds is: canary tokens in config, environment and artifact metadata (C4.4), and honeypot tasks salted into the benchmark whose cheat path is logged rather than rewarded (C10.3).

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.1": """
**What it covers.** Reconstruct a timeline from raw logs with a context-loaded agent.

**Why a security engineer needs it.** Reaching for the agent once you're already behind. The control it builds is: pre-load logs, telemetry, segmentation model and playbooks.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.2": """
**What it covers.** Attribute an incident through the A2 `act` chain.

**Why a security engineer needs it.** "Which user" is now the wrong first question. The control it builds is: attribute to agent, authority, delegation chain and prompt.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.3": """
**What it covers.** Scope a multi-agent incident end to end.

**Why a security engineer needs it.** The initiating agent is not the acting one. The control it builds is: reconstruct the action chain across all three planes.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.4": """
**What it covers.** Exercise the ladder against a live misbehaving agent.

**Why a security engineer needs it.** Mass revocation takes down the business. The control it builds is: throttle → scope-reduce → reroute → force HITL → revoke → hard stop, in order.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.5": """
**What it covers.** Replay an agent run for a regulator-grade record.

**Why a security engineer needs it.** Non-determinism as an evidentiary problem. The control it builds is: log at design time what replay will need.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.6": """
**What it covers.** Pick the right layer for five real incidents.

**Why a security engineer needs it.** Fixing the prompt when the bug is in the control plane. The control it builds is: choose among model, prompt, tool, policy, sandbox, identity, eval.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.7": """
**What it covers.** Time your own stop authority end to end.

**Why a security engineer needs it.** Nobody has rehearsed halting an autonomous workflow. The control it builds is: named holder, measured time-to-stop, tested.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.8": """
**What it covers.** Run the first-hour checklist in a tabletop.

**Why a security engineer needs it.** Notification obligations discovered in week two. The control it builds is: feed Track E2 in hour one.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"D2.9": """
**What it covers.** Kill a fleet, then check what the revoked-credential step changes about what an attacker still holds afterwards.

**Why a security engineer needs it.** Terminating agents while their tokens stay valid leaves the persistence in place. In the incident, third-party access ended when the third party revoked keys — not when the agents stopped. The control it builds is: a tested kill path independent of the agent execution path, snapshot before terminate, revocation in the same action, a measured activation target and named authority to pull it (C8.3).

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.0": """
**What it covers.** Take the seven properties and assign each an owner in your own organisation. The gaps are the programme.

**Why a security engineer needs it.** A trustworthy-AI statement with no owner per property, so every property is somebody else's job. The control it builds is: one register, risk-tiered, with each property mapped to a control, an owner and evidence that can be re-checked.

This is an **orientation** lesson. It has no code — it exists so the chapters after it are read in the right order.
""",

"E1.1": """
**What it covers.** Change a prompt and show the control evidence going stale in real time.

**Why a security engineer needs it.** An annual review certifies nothing about a system that changed on Tuesday. The control it builds is: continuous assurance; control effectiveness redefined for probabilistic systems.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.2": """
**What it covers.** Discover agents from gateway and identity telemetry; build the register.

**Why a security engineer needs it.** Shadow AI and shadow agents — the inventory is the control most orgs still lack. The control it builds is: discovery, registration, ownership, risk tiering.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.3": """
**What it covers.** Tier ten real workflows and assign approval authority.

**Why a security engineer needs it.** Tiering by model name instead of by what the thing can do. The control it builds is: autonomy level × action class × data sensitivity.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.4": """
**What it covers.** Map the A2/A3 controls onto your control library.

**Why a security engineer needs it.** Inventing new controls where an existing one applied to a new principal type. The control it builds is: map identity, secrets, sandbox, eval and telemetry onto the existing library.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.5": """
**What it covers.** Take the B2.1 harness output and turn it into an evidence pack — then find the three ways the same numbers could mislead you.

**Why a security engineer needs it.** Accepting a vendor's best-of-k demo as assurance; mistaking schema conformance for accuracy. The control it builds is: read an eval report properly: execution-verified results, reliability across all attempts, trajectory scoring, judge independence.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.6": """
**What it covers.** Classify your own guardrails into the two buckets.

**Why a security engineer needs it.** Frameworks specify how the system works; regulators care what it produced. The control it builds is: constrain both, and know which evidence answers which question.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.7": """
**What it covers.** Automate one evidence package on a schedule.

**Why a security engineer needs it.** Automating judgment instead of evidence collection. The control it builds is: agent-assisted evidence collection, drift detection, exception tracking.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.8": """
**What it covers.** Run a real AIBOM against a vendor model artefact.

**Why a security engineer needs it.** Vendor AI features enabled by default; sub-processor chains you never mapped. The control it builds is: questions that actually discriminate between vendors.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.9": """
**What it covers.** Write the gate that a re-index has to pass.

**Why a security engineer needs it.** Re-indexing treated as maintenance, not change. The control it builds is: retraining, fine-tuning and re-indexing as change-management events.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.10": """
**What it covers.** Map five stakeholders to the controls each operates, then locate the four classic seam failures in your own estate.

**Why a security engineer needs it.** Legal, compliance, privacy, cyber and model risk each hold part of the AI control estate and none holds all of it. The programme fails at the seams between them, not inside any one. The control it builds is: a stakeholder operating model naming who decides, who tests, who signs — and where the handoffs leave gaps nobody is watching.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.11": """
**What it covers.** Take a validated model, add one tool, and show which parts of the validation are now void.

**Why a security engineer needs it.** The classical model-risk playbook silently breaks once the model can act: conceptual soundness was validated, and then the agent was granted write access nobody validated. The control it builds is: extend the SR 11-7 lineage — conceptual soundness, ongoing monitoring, independent validation — to non-deterministic, tool-using systems, and name where it still holds.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E1.12": """
**What it covers.** Trace one artefact across three functions and find the consumer who never received it.

**Why a security engineer needs it.** The handoffs fail, not the functions: privacy assessment into control design, legal position into system prompt, MRM validation into security evidence. The control it builds is: joint runbooks for the seams — one artefact, many consumers, one owner.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.1": """
**What it covers.** Build the crosswalk for your own sector.

**Why a security engineer needs it.** One programme per regime; four times the work, none of it joined up. The control it builds is: one control set that satisfies several regimes. Verify current status before relying on any date.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.2": """
**What it covers.** Classify three workflows and defend the boundary cases.

**Why a security engineer needs it.** "We only deployed it, we didn't build it" — sometimes true, often not. The control it builds is: risk classification, GPAI obligations, transparency duties, and how agentic deployment changes classification.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.3": """
**What it covers.** Hang two regulator mappings off one framework spine.

**Why a security engineer needs it.** Regime-specific mappings with nothing to hang off. The control it builds is: aI RMF / management-system standards as the structure; regulator mappings as overlays.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.4": """
**What it covers.** Map one agent to existing model-risk obligations.

**Why a security engineer needs it.** An agent is already a "model" under model-risk rules you already comply with. The control it builds is: find the regime you're already in before inventing a new one.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.5": """
**What it covers.** Run PII redaction inside the trust boundary with Presidio before anything crosses out.

**Why a security engineer needs it.** Deletion when the data is in weights, not a database. The control it builds is: lawful basis, ADM rights, residency in inference and retrieval paths, retention of traces.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.6": """
**What it covers.** Draft the notification for an agentic incident.

**Why a security engineer needs it.** Materiality assessed for an autonomous actor with a human-actor playbook. The control it builds is: coordinate with D2 in hour one.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.7": """
**What it covers.** Assemble the pack for one high-risk workflow.

**Why a security engineer needs it.** "Explainability" for a system with no deterministic reasoning. The control it builds is: system documentation, data lineage, eval records, oversight evidence, decision logs.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.8": """
**What it covers.** Produce an audit trail from the A2 chain that names authority at every hop.

**Why a security engineer needs it.** No trail showing under whose authority the agent acted. The control it builds is: the delegation chain *is* the audit trail.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E2.9": """
**What it covers.** Defend one workflow in a mock supervisory conversation.

**Why a security engineer needs it.** Overclaiming control, or triggering a moratorium. The control it builds is: explain bounded autonomy with evidence, and anticipate the real questions.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E3.1": """
**What it covers.** Convert one blast-radius measurement into a board paragraph.

**Why a security engineer needs it.** Blast radius explained in engineering terms to a board that needs consequence. The control it builds is: what can happen, how fast, who can stop it.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E3.2": """
**What it covers.** Write the delegated-authority policy.

**Why a security engineer needs it.** A per-tool review queue becomes a bottleneck and then a bypass. The control it builds is: a policy on delegated authority instead of tool-by-tool approval.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E3.3": """
**What it covers.** Sequence your first three workflows and name the no.

**Why a security engineer needs it.** Starting with the workflow that is most visible rather than most winnable. The control it builds is: use the maturity model to order investment; choose your first hard "no".

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E3.4": """
**What it covers.** Draw your org's ownership map against the topic matrix.

**Why a security engineer needs it.** Harness engineering with no home; research as a hobby. The control it builds is: identity owns the control plane; BUs own grants; security owns stop authority.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E3.5": """
**What it covers.** Instrument the six metrics from your lab stack.

**Why a security engineer needs it.** Reporting activity instead of exposure. The control it builds is: inventory coverage, attested-identity share, standing-access reduction, MTT-revoke, blast-radius distribution, eval-gate pass rate.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E3.6": """
**What it covers.** Write one enforceable conditional approval.

**Why a security engineer needs it.** Conditional approval that is aspirational rather than enforceable. The control it builds is: autonomy promotion as an earned event with named evidence.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E3.7": """
**What it covers.** Write the interview loop for an agentic security engineer.

**Why a security engineer needs it.** Hiring for conceptual familiarity instead of practice. The control it builds is: interview questions that separate the two; internal transition paths.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

"E3.8": """
**What it covers.** Re-score your programme on the resilience axis.

**Why a security engineer needs it.** Trying to enumerate every failure mode of a probabilistic system. The control it builds is: maturity measured by containment, detection and recovery — not prevention.

This is a **control** lesson: it builds the mechanism, then breaks it, so you can see what the control is actually load-bearing for rather than taking the claim on trust.
""",

}
