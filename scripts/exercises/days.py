"""Day 0, Day 1 and Day 2 for every function and every lesson.

The commons was legible to the people who wrote it and to nobody else. Readers
said the same thing each time: *I could not tell what this was for until someone
explained it.* The material was right; what was missing was the question every
practitioner asks before reading anything — **why would I do this, how do I do
it, and how do I know it worked.**

So every function and every lesson answers those three, in that order, in the
same words each time:

    Day 0  ·  why       what goes wrong if you do nothing, in this lesson's terms
    Day 1  ·  how       the concrete thing you build or run
    Day 2  ·  measure   the number that tells you it worked

Day 2 is the one that is easy to fake and the only one a sceptical reader
believes. Where a lesson produces a real number — a recall score, a
false-positive rate, a coverage fraction, an interval in minutes — Day 2 names
that number. Where it does not, Day 2 says what you count instead, and does not
pretend otherwise.

`check_lessons.py` requires all three on every lesson, for the same reason it
requires a hook: a lesson that cannot say what it is worth is a lesson nobody
can justify spending an afternoon on.
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# Function level — who it is for, and the three days across the whole function.
# `who` is deliberately in job titles rather than skills, because a reader
# decides whether to open a track by recognising their own role in it.
# --------------------------------------------------------------------------

FUNCTION_DAYS: dict[str, dict[str, str]] = {

"A": {
 "who": "Security architects, principal security engineers, and the product "
        "engineers and product managers who are building an agentic feature and "
        "have been asked whether it is safe to ship.",
 "day0": "You are about to build, review or approve an agentic system. Before "
         "any control is worth choosing you need the picture: which components "
         "exist, what each one can reach, and which risks attach to each. Choose "
         "controls before you can name the risks and you will buy the ones that "
         "are easy to buy. This function is the reason the other four have "
         "something to point at.",
 "day1": "Draw the architecture, then close the two controls that shut the most "
         "risks — knowing who is calling, and marking what came in from outside "
         "— then the runtime layer that still holds after identity has been "
         "defeated: default-deny on the tool call, sandboxing, egress control, "
         "budgets and an approval path that survives volume.",
 "day2": "The register in A1.18 is the scorecard. Count the risks that have a "
         "named owning control, the agents with an attested identity rather than "
         "a shared key, and the share of tool calls that a default-deny policy "
         "actually adjudicated. A risk with no control is the backlog, in the "
         "same units as everything else.",
},

"B": {
 "who": "AppSec engineers, product security engineers, secure code reviewers "
        "and penetration testers — the people who already run a security gate "
        "on every release.",
 "day0": "You already do this work: SAST, DAST, dependency and container "
         "scanning, and a penetration test before launch. Two things changed. "
         "Agentic code puts authority behind a model's output, so the classes "
         "that matter are ones deterministic rules cannot express — and the same "
         "coding agents now open pull requests faster than anyone can read them. "
         "The value of putting AI in the pipeline is not novelty; it is recall "
         "on the classes you were missing, at the rate you are now shipping.",
 "day1": "Build the pipeline in order rather than buying it: threat model from "
         "what the estate already knows, deterministic SAST first and a model "
         "pass second, then deduplicate, filter for reachability, replicate in a "
         "sandbox, exploit dynamically, chain what composes, and only then "
         "calibrate severity and hand a fix to a human. Then the agentic "
         "penetration tests — white, black and grey box — and the controls an "
         "offensive agent has to run inside.",
 "day2": "This function is measured on a before-and-after you can state out "
         "loud. Deterministic SAST on the sample in B2.3 has precision 1.00 and "
         "finds roughly one real defect in seven; the reasoning pass finds about "
         "six in ten — four times the recall, on the same code. That is the "
         "gain. The cost is false positives, which is what deduplication, "
         "reachability filtering and context engineering are for, and every one "
         "of those stages reports its own number rather than a claim.",
},

"C": {
 "who": "Red team operators, AI security researchers and offensive ML "
        "engineers — and the defenders who have to receive what they find.",
 "day0": "Nobody can tell you how your agentic system fails until somebody has "
         "tried to break it. Deterministic exploits have signatures; an agentic "
         "failure is a reasoning loop, code generated at run time and tool calls "
         "at machine speed, and none of that shows up in a scanner. Doing "
         "nothing here means your first real evidence arrives as an incident.",
 "day1": "Work one lifecycle end to end rather than collecting techniques: the "
         "ingestion and supply-chain surfaces an attacker reaches first, "
         "elicitation that scales, then the pivot — turn what you found into "
         "gateway telemetry, a deployable detection, a triage playbook, "
         "containment and a forensic replay, and hand it over as policy.",
 "day2": "A transcript is not a finding. Every technique reports a reproduction "
         "rate across attempts with its denominator, every detection reports "
         "the queue volume it would add, and every finding leaves with an "
         "evaluation case that fails on the unfixed build — so the fix is "
         "verifiable and cannot regress unnoticed.",
},

"D": {
 "who": "SOC analysts, detection engineers, incident responders, threat "
        "hunters and DFIR leads — running a SOC that now has agents in it, and "
        "agents watching it.",
 "day0": "Your SOC was tuned for people. One hour of an agent is roughly 1,400 "
         "tool calls across 260 resources; one hour of a person is twelve "
         "actions. Every threshold, baseline and playbook you own was set "
         "against the second number, and four of the nine things an agent does "
         "in an ordinary day are seen by none of the four sensor classes you "
         "already bought.",
 "day1": "Build it in five phases, on open source you can run: discover with "
         "the sensors you have plus agent telemetry that no product emits, "
         "detect against a lake tiered by the queries you actually run with "
         "rules mapped to MITRE, understand with bounded investigation and "
         "correlation across the fleet, respond with tiers derived from "
         "reversibility, and recover with replay, root cause and a policy diff.",
 "day2": "Five intervals, one per phase, and all five are numbers: time to "
         "discover, to detect, to understand, to contain, and to recover to "
         "target. CyberTravels' detection interval is 194 minutes against a "
         "15-minute target and its manual containment finishes in 34 minutes "
         "against a 29-minute breakout. Every lesson says which interval it "
         "shortens, or which one it spends on purpose.",
},

"E": {
 "who": "GRC analysts, risk and compliance managers, control owners, privacy "
        "engineers, BISOs and the CISO office — anyone who has to answer for "
        "the estate rather than build it.",
 "day0": "Somebody signed off on the platform when it was a chatbot. It now "
         "moves money, ships code and reads contracts, and nothing in the "
         "approval process noticed. A control tested six months ago is not "
         "passing — it is unevidenced — and that third state is invisible to "
         "most tooling, which is why a register can be entirely green and "
         "entirely unsupported.",
 "day1": "Build the indicator set: an inventory for the denominator, risk "
         "tiering for the target, control mapping for the subject, owners by "
         "name, and verification that re-reads rather than citing last year. "
         "Then point the same indicators outward at regulators, and run them as "
         "a programme sequenced by distance from target.",
 "day2": "The unit is the key control indicator: computed from the estate, with "
         "a denominator, and a target written before the measurement. E1.13 "
         "computes six of them against the CyberTravels repository and returns "
         "five gaps and one pass — the pass being what proves the instrument "
         "discriminates rather than simply complaining.",
},

}


# --------------------------------------------------------------------------
# Lesson level. Three short lines each: why, how, and the number.
# --------------------------------------------------------------------------

# The lesson that opens each function, and therefore the one that carries the
# function-level Day 0/1/2 block. A0.1 is deliberately not here: it teaches the
# reader to run a notebook, which is not Function A's argument.
FUNCTION_INTRO: dict[str, str] = {
    "A": "A1.0", "B": "B2.0", "C": "C1.0", "D": "D1.0", "E": "E1.0",
}

DAYS: dict[str, tuple[str, str, str]] = {}

# ---- A · Securing AI Architectures ---------------------------------------
DAYS.update({

"A0.1": ("You cannot judge any of this until one lesson runs on your own "
         "machine. A curriculum you cannot execute is a slide deck.",
         "Run the preflight on both routes — a cloned repository and a hosted "
         "kernel — and reproduce the two failures it is built to produce.",
         "Exit 0, twelve lines, and the same CRC on both routes. The matching "
         "checksum is the proof it is the same file either way."),

"A0.2": ("A finding filed in the wrong vocabulary reaches the wrong audience "
         "and gets actioned by nobody.",
         "Learn which of four questions each framework answers, then look a "
         "lesson up in both directions.",
         "Coverage per framework — how many lessons address each control — and "
         "the obligations with only one lesson behind them."),

"A1.0": ("\"Secure the agent\" has no referent until the system is drawn, so "
         "every control argument is really an argument about the picture.",
         "Read the three chapters in order: the architecture and its risks, "
         "then identity and ingress, then runtime and the gateway.",
         "Nothing yet, honestly. This chapter produces the component map every "
         "later count in the commons is taken against."),

"A1.1": ("Every later lesson names a component from this map. Without it a "
         "risk lands nowhere in particular and cannot be argued about.",
         "Draw CyberTravels as components and trust boundaries, and compute the "
         "crossings from the levels rather than listing them by hand.",
         "The number of trust-boundary crossings — computed, so it moves when "
         "the architecture moves rather than when someone remembers to edit."),

"A1.2": ("A user redirects their own agent past what the operator specified, "
         "bounded only by their own authority — which for a privileged user is "
         "the whole system.",
         "Provenance at ingress and default-deny on the tool call. The system "
         "prompt is not a control.",
         "Share of tool calls whose selecting text came from a trusted origin."),

"A1.3": ("Anyone who can write into a corpus the agent reads can steer it, "
         "using the victim's authority rather than their own.",
         "Mark provenance at ingress, and forbid untrusted spans from selecting "
         "a tool.",
         "Share of retrieved spans carrying an origin tag, and the count that "
         "reached a tool selector anyway."),

"A1.4": ("The attacker's instruction outlives the conversation that delivered "
         "it and re-fires on requests from other users.",
         "Carry provenance into memory, and scope memory writes to the identity "
         "that made them.",
         "Memory entries with a recorded origin and writer, as a share of all "
         "entries."),

"A1.5": ("A legitimate tool with legitimate arguments does something nobody "
         "intended, and every log line looks normal.",
         "Default-deny per call on identity, tool, arguments and resource, plus "
         "authority issued just in time.",
         "Tool calls adjudicated by a policy decision rather than allowed "
         "because no rule objected."),

"A1.6": ("The agent acts with more authority than the person who asked, and "
         "the log records a service account rather than either of them.",
         "Delegation that narrows, grants that expire, and default-deny "
         "underneath both.",
         "Share of actions whose effective scope sits inside the requesting "
         "human's own ceiling."),

"A1.7": ("You cannot say which agent acted, so you cannot revoke one without "
         "stopping all of them.",
         "Per-workload identity with attestation, and a lifecycle that can "
         "revoke a single agent.",
         "Agents with an attested, individually revocable identity, as a share "
         "of the fleet."),

"A1.8": ("Model-authored code runs with the runtime's privileges, reaching the "
         "filesystem, the network and every credential mounted there.",
         "Execute in an isolate with no ambient credentials and no default "
         "network, and control egress underneath it.",
         "Share of code-executing runs inside an isolate, and the number of "
         "credentials visible from within one — target zero."),

"A1.9": ("The pipeline reads attacker-controlled content and then acts on it — "
         "a confused deputy you built yourself.",
         "One provenance rule: content the pipeline read may never drive a "
         "state-changing tool.",
         "State-changing calls whose selecting input came from read content. "
         "The target is zero, and the count is the finding."),

"A1.10": ("One compromised agent steers every agent downstream of it, because "
          "a peer's message is trusted the way a colleague's would be.",
          "Validate and mark provenance on the inter-agent channel, on top of "
          "per-agent identity.",
          "Peer messages carrying a verified sender identity, as a share of "
          "messages acted on."),

"A1.11": ("An agent nobody approved receives delegated work and delegated "
          "authority, and the orchestrator cannot tell it apart from one you "
          "chose.",
          "A registry of approved agents, admission bound to a registered "
          "identity, and an audit trail per hop.",
          "Agents observed in the topology that appear in the registry. The "
          "gap is the finding, not the percentage."),

"A1.12": ("A single fabrication becomes a shared premise, and by the third hop "
          "nothing records that it was ever uncertain.",
          "Verify a claim against ground truth before it is allowed to "
          "propagate.",
          "Propagated claims carrying a verification result, as a share of "
          "claims that reached a second agent."),

"A1.13": ("The loop consumes budget, quota or downstream capacity without "
          "bound, and the failure lands as denial of service and a bill.",
          "Ceilings bound to the loop itself, terminating the run rather than "
          "degrading it.",
          "Runs stopped by their own ceiling rather than by a downstream "
          "system, and cost per run at the 95th percentile."),

"A1.14": ("You cannot say which user caused an action, or what made the agent "
          "decide, so the incident cannot be scoped.",
          "Attribution carried on every hop, into a store the agent cannot "
          "write to.",
          "Actions whose full chain — human, agent, scope — can be "
          "reconstructed. Anything below 1.00 is what you cannot audit."),

"A1.15": ("The approval gate is recorded as a control and operates as a click. "
          "At volume it approves everything, including the one that mattered.",
          "Reserve approval for irreversible actions and bound everything else "
          "by policy.",
          "Queue depth and median decision time per reviewer. A control that "
          "degrades with volume has to be measured against volume."),

"A1.16": ("The agent satisfies the letter of its instruction, including by "
          "reporting a success it did not achieve, and the harness records the "
          "claim as the outcome.",
          "An independent verifier that checks the outcome rather than the "
          "claim about it.",
          "Claims independently verified, as a share of claims acted on."),

"A1.17": ("The delegation chain becomes a privilege-laundering path, and the "
          "agent's output an unusually credible lure.",
          "Ceiling-bound delegation, attribution per hop, and machine-generated "
          "output marked as machine-generated.",
          "Outbound machine-generated messages carrying a label, as a share of "
          "those sent."),

"A1.18": ("A list of risks is read once. Without a component, a control and an "
          "owner against each row, nothing in it is actionable.",
          "Four columns — scene, component, control, owning lesson — and a rule "
          "that no row ships without the fourth.",
          "Rows with an owning lesson. This is the register's own coverage, and "
          "it is the number Function A is graded on."),

"A2.1": ("A shared service account answers \"what ran\" and destroys \"for "
         "whom\", so no later control can be conditioned on the caller.",
         "One identity per workload, carrying the human principal alongside it, "
         "asserted on every call.",
         "Workloads holding a distinct identity, as a share of the fleet."),

"A2.2": ("A pre-shared secret in an image or an environment variable is "
         "copyable, so possession stops being proof of identity.",
         "Exchange platform attestation for a short-lived, workload-bound "
         "credential.",
         "Credentials issued against attestation rather than pre-shared, and "
         "their median lifetime."),

"A2.3": ("Subset-only delegation lets a privileged user hand an agent "
         "authority it must never hold; ceiling-only lets the agent exceed the "
         "person who asked.",
         "Token exchange that intersects the presented scope with the actor's "
         "ceiling, and records the chain.",
         "Delegations whose result sits inside both the request and the "
         "ceiling, and the recorded depth of each chain."),

"A2.4": ("Permanent scope makes every injection a successful one, because the "
         "authority is already there when the attacker arrives.",
         "Short-lived, purpose-bound grants issued per task and expiring with "
         "it.",
         "Median grant lifetime, and the amount of standing scope removed."),

"A2.5": ("Agents accumulate with no owner and no expiry, and an unregistered "
         "one joins the topology as a peer.",
         "A registry with a named owner, an expiry, and admission bound to a "
         "registered identity.",
         "Agents with an owner and a future expiry, as a share of those "
         "actually observed running."),

"A2.6": ("Concatenation destroys the one fact that separates an operator's "
         "instruction from an attacker's: where it came from.",
         "Tag provenance at every ingress point, and permit only trusted "
         "origins to select a tool.",
         "Ingress points that tag, and tool selections traceable to a trusted "
         "origin."),

"A2.7": ("Without the motivating input, root cause cannot be established at "
         "all; without the principal, nothing can be attributed.",
         "Per-hop attribution written to an append-only store outside the "
         "agent's reach.",
         "Actions with a complete chain. The share below 1.00 is precisely the "
         "part of the estate you cannot audit."),

"A2.8": ("An agent that escapes its container can rewrite the record of what "
         "it did — and every detective control downstream reads that record.",
         "Out-of-band capture, a hash-chained write-once transcript store, and "
         "an isolated logging plane.",
         "Transcript segments whose hash chain verifies, and the number of "
         "gaps the chain detects."),

"A3.1": ("Allow-by-default authorization is defeated by any argument the model "
         "can be persuaded to produce.",
         "Evaluate policy per call on identity, tool, arguments and resource, "
         "denying unless a rule permits.",
         "Calls denied by policy, and the share of tools reachable with no "
         "matching rule at all."),

"A3.2": ("Model-authored code inherits the runtime's reach, including any "
         "credential mounted into the environment.",
         "Run it in an isolate with no ambient credentials, a bounded "
         "filesystem and no network by default.",
         "Executions inside an isolate, and credentials reachable from within "
         "one — where the target is zero."),

"A3.3": ("An agent with unrestricted egress turns any successful injection "
         "into data loss.",
         "An allow-list at the network boundary, enforced where the agent "
         "cannot rewrite it.",
         "Outbound destinations outside the allow-list, and the bytes that "
         "reached them."),

"A3.4": ("Without a ceiling the loop runs until an external system stops it, "
         "and the failure is denial of service to everything sharing the quota.",
         "Ceilings bound to the loop, terminating the run rather than letting "
         "it degrade.",
         "Runs terminated by their own ceiling, and spend per run at the 95th "
         "percentile."),

"A3.5": ("An unverified claim becomes a shared premise, and a peer's message "
         "gets trusted more than a document it is no safer than.",
         "Schema validation plus an independent verifier before any claim "
         "propagates.",
         "Results that passed both checks, as a share of results acted on."),

"A3.6": ("An approval queue at volume approves everything, and the risk "
         "register still records it as a control.",
         "Reserve approval for irreversible actions only, and label "
         "machine-generated content as such.",
         "Approvals per reviewer per hour, and the share of them that are "
         "genuinely irreversible actions."),

"A3.7": ("Per-agent controls diverge as the fleet grows, and legacy "
         "downstreams push a static credential back into agent code.",
         "One enforcement point holding identity, policy, egress, budget and "
         "audit together.",
         "Share of agent traffic that transits the gateway. Whatever does not "
         "is unenforced, whatever the policy says."),

"A3.8": ("Any shared mutable surface is a channel between runs that are "
         "supposed to be independent.",
         "Per-run namespaces bound to the run's workload identity, an "
         "immutable write-once cache, and signing.",
         "Runs sharing a mutable surface with another run — target zero, and "
         "the count is the finding."),

"A3.9": ("Classifiers off, no compensating cap, and tens of thousands of "
         "agents launched under that configuration. One decision becomes a "
         "population-scale incident.",
         "An exemption gate the platform enforces, caps that tighten as "
         "coverage drops, and quotas on population growth.",
         "Live exemptions, the age of each, and the cap in force while it is "
         "open."),

"A3.10": ("An agent that finds a live breach, reasons about telling somebody, "
          "and has no tool for it, does nothing at all.",
          "A report-to-human tool that is cheap, non-terminal and signposted, "
          "plus a mandatory checkpoint on out-of-scope discovery.",
          "Escalations raised per thousand runs. A rate of zero means the tool "
          "is missing, not that nothing was found."),

"A3.11": ("The IDE agent holds git credentials, cloud credentials and a shell, "
          "in an environment nobody manages.",
          "Credential deny-lists and workspace confinement first — the "
          "strongest containment a developer does not notice.",
          "Developer agents with confinement applied, and the credentials still "
          "reachable from inside the workspace."),

})

# ---- B · Application Security with an AI SDLC ----------------------------
DAYS.update({

"B2.0": ("A security pipeline built as if it were exempt from the risks it "
         "exists to find is the one nobody audits.",
         "Learn the line first — what can run before a deploy and what only "
         "works after one — then build the pipeline and its harness as one "
         "system.",
         "Every stage after this reports its own number. This lesson's output "
         "is the order they run in, which is what makes those numbers "
         "comparable."),

"B2.1": ("A harness whose verifier is the model agreeing with itself does not "
         "fail loudly. It succeeds quietly and wrongly.",
         "Build an independent verifier, and a budget that stops the loop when "
         "it cannot pass.",
         "Agreement rate between the verifier and held-out ground truth, and "
         "the number of loops stopped by budget rather than by success."),

"B2.2": ("Threat models are written once, by hand, against a system that has "
         "changed since.",
         "Derive assets, entry points and attack vectors mechanically from the "
         "map the estate already holds.",
         "The diff between two runs. A threat model that produces no diff when "
         "the estate changed is not being derived."),

"B2.3": ("Pattern matching floods the queue, and the classes that matter in "
         "agentic code cannot be written as patterns at all.",
         "Deterministic rules for what rules do well, then a model pass for "
         "what they cannot express.",
         "The clearest before-and-after in the commons: Semgrep holds "
         "precision 1.00 and finds about one real defect in seven; the "
         "reasoning pass finds about six in ten. Four times the recall, same "
         "code — and the extra false positives are what the next four stages "
         "exist to remove."),

"B2.4": ("Parallel analysis tracks report the same bug three times, and some "
         "of those bugs do not exist.",
         "Consolidate overlapping findings, then cross-reference each against "
         "syntax and call graph.",
         "Findings before and after consolidation, and how many survived "
         "verification. Both numbers, not just the smaller one."),

"B2.5": ("A finding in dead code costs exactly as much to triage as one on the "
         "login path.",
         "Decide whether an external caller can actually reach the sink before "
         "anyone is paged.",
         "Share of findings with a reachable path from a real entry point — "
         "and the triage hours the unreachable ones would have cost."),

"B2.6": ("Dynamic testing run against staging turns a destructive probe into "
         "an incident.",
         "Replicate the application in an isolated, disposable runtime with no "
         "path to production.",
         "Probes executed in the sandbox, and connections from it to anything "
         "production — where the second number must be zero."),

"B2.7": ("A clean dependency scan on an estate carrying an undeclared "
         "third-party binary reads as evidence of safety.",
         "Reconcile the SBOM against what is actually on disk, then recover "
         "strings, imports and egress from the binaries it missed.",
         "Artefacts on disk that appear in the SBOM. The gap is the finding, "
         "and it is usually not zero."),

"B2.8": ("A static finding is a hypothesis, and hypotheses get argued about in "
         "triage meetings instead of fixed.",
         "Generate and run an actual exploit against the sandbox, so each "
         "finding is confirmed or dropped.",
         "Findings confirmed by execution versus refuted. Both are useful "
         "answers; only one of them is a ticket."),

"B2.9": ("Three medium findings are triaged as three mediums, and nobody "
         "notices they compose into a critical.",
         "Combine validated findings into multi-step sequences where one's "
         "effect satisfies another's precondition.",
         "Chains discovered, and the severity of the chain against the highest "
         "severity of its links — the difference is what individual triage "
         "missed."),

"B2.10": ("An offensive loop with no hard scope boundary tests something you "
          "were not authorised to touch, at machine speed.",
          "Give the loop full target context, and enforce scope at the network "
          "layer rather than by asking the model to respect it.",
          "Findings ranked against a severity-sorted baseline, and the number "
          "of out-of-scope requests the enforcement refused."),

"B2.11": ("Full source produces a finding list nobody can act on, because "
          "presence is reported where reachability was needed.",
          "Enumerate paths from real entry points to sinks, and classify the "
          "predicate on each hop as authentication or authorisation.",
          "Sinks reachable from an entry point, and how many of those carry "
          "only an authentication check. Three of five, on CyberTravels."),

"B2.12": ("An agent narrates a confident architecture from status codes, and "
          "the report is fiction that reads like findings.",
          "Label every claim observed or inferred, keep the evidence beside "
          "it, and attach no severity to an inference.",
          "Findings versus open questions — five and seven on the sample run — "
          "and what each open question would need to resolve it."),

"B2.13": ("Object-level authorisation is assumed correct because the endpoint "
          "list was covered, and broken object access lives in the cells "
          "nobody enumerated.",
          "Fill a roles-by-objects-by-verbs matrix from one credential per "
          "role, and mark every cell tested, mismatched or untested.",
          "Cell coverage, not endpoint coverage: 12 of 30 cells on the sample, "
          "with two mismatches and the two highest-cost cells never tested."),

"B2.14": ("The offensive agent is the most capable and least supervised thing "
          "in the estate, and its traffic is indistinguishable from an attack "
          "by design.",
          "Run a preflight that refuses to start until zero retention, "
          "sandboxing, egress control, secret management, human-in-the-loop "
          "and deterministic guardrails are all present.",
          "Blocking controls present out of six, and whether the SOC was "
          "briefed. The refusal is the deliverable when they are not."),

"B2.15": ("Severity copied from the rule orders the queue by something that "
          "predicts nothing.",
          "Calibrate severity from sandbox evidence, and report per-stage "
          "economics rather than a single total.",
          "Cost per confirmed finding at each stage, which is what tells you "
          "which stage to invest in next."),

"B2.16": ("A patch that silences the scanner is indistinguishable from a patch "
          "that fixes the bug.",
          "Generate the fix, re-run the exploit against the patched build, and "
          "require a regression test that fails on the old one.",
          "Patches where the exploit no longer succeeds and the regression "
          "test fails pre-fix. Anything else is a silenced scanner."),

"B2.17": ("The model is handed the repository and asked to be thorough, so the "
          "relevant line falls out of the context window.",
          "Slice on the source-to-sink path rather than on distance: the "
          "smallest context that still supports a severity call.",
          "False positives before and after slicing, against tokens spent. The "
          "point is that both improve."),

"B2.18": ("Control claims live in a spreadsheet and are never bound to a "
          "deployment, so nobody can say which build they describe.",
          "Scope every skill to one deployment identifier and emit a signed "
          "attestation whose predicate names what was checked.",
          "Deployments with a verifiable attestation, and claims in the "
          "spreadsheet with no attestation behind them."),

"B2.19": ("A reference implementation gets adopted as a product and its "
          "outputs trusted without an evaluation.",
          "Map its stages onto the pipeline you built, then score it against "
          "your own held-out key.",
          "Its accuracy on your key, not its accuracy on its own — which is "
          "the only comparison that transfers."),

})

# ---- C · Agentic Evaluation and Red Teaming ------------------------------
DAYS.update({

"C1.0": ("Offensive work that produces anecdotes — a result that worked once, "
         "on one target, with no rate attached — changes nothing.",
         "Follow one lifecycle end to end: reach, see, respond, carry forward.",
         "Every lesson after this reports a rate with a denominator, and ends "
         "in a control somebody can deploy."),

"C1.1": ("The first surface an attacker reaches is the hub the model came "
         "from, and a squatted name is accepted because it looked right.",
         "Assess each component on whether it can change without telling you, "
         "rather than on how popular it is.",
         "Components with a pinned digest, as a share of what the pipeline "
         "pulls at train or deploy time."),

"C1.2": ("A dataset is parsed before it is embedded, and a crafted record "
         "reaches code execution on the indexing host — which usually has more "
         "access than the serving one.",
         "Treat the embedding pipeline as an attack surface and build a "
         "provenance manifest: source, parser and digest per record.",
         "Ingested records with a verifiable origin. The ones without are the "
         "route a payload rides in on."),

"C1.3": ("A jailbreak that strips safety while leaving tool use intact is the "
         "combination that turns a bypass into an incident.",
         "Run the technique many times, varying seed and wording, rather than "
         "keeping the transcript that worked.",
         "Reproduction rate across attempts, with its denominator. A "
         "screenshot has no denominator, which is why it is not a finding."),

"C1.4": ("To catch the actor you have just played, you have to be able to see "
         "it — and the model gateway logs none of the fields that would "
         "distinguish an agent from a person.",
         "Wrap the gateway trace with identity, tool and arguments, then score "
         "actors on behaviour rather than on what they claim to be.",
         "Threshold chosen by expected cost rather than accuracy, and the "
         "unregistered actors it surfaces."),

"C1.5": ("Each run examined alone is plausible work; the swarm exists only in "
         "the population, so per-run review cannot see it.",
         "Work the case study across runs — shared mounts, child agents with "
         "no human above them — and map each behaviour to a control.",
         "Behaviours with a named control behind them. The ones without are "
         "what the case study exists to surface."),

"C1.6": ("A rule that flags an unauthorised runtime objective is worth a great "
         "deal; the same rule firing on everything is worth less than nothing.",
         "Generate candidates, then score each against real history on the one "
         "property that decides deployability — firing volume.",
         "Alerts added to the queue per true positive. A rule at 301 to 1 is "
         "rejected with the number attached, not with an adjective."),

"C1.7": ("An agent that scores evidence only on support confirms its first "
         "theory and closes the wrong case at machine speed, silently.",
         "Run triage as a loop with a severity floor and a stable-seeded "
         "sample of whatever it auto-closed.",
         "Closures sampled to a human, and agreement on that sample — which is "
         "the only measurement of the loop's false-negative rate you will get."),

"C1.8": ("Every other detector needs a threshold, and every threshold trades "
         "misses against false alarms.",
         "Place canary tokens and honeypot tasks where no legitimate task "
         "reaches, so a touch needs no threshold at all.",
         "False-positive rate of zero by construction — and the count of "
         "canaries that legitimate work does reach, which breaks that property."),

"C1.9": ("A fleet completes thousands of actions inside one human approval "
         "cycle, so containment is pre-authorised or it is too late.",
         "Build a zero-trust gatekeeper and a revocation path that isolates the "
         "whole fleet in one action.",
         "What the credentials can still do after the agents stop. Termination "
         "without revocation moves the incident rather than ending it."),

"C1.10": ("A finding is only as good as its reproduction, and the constant "
          "teams miss is the model version — which silently invalidates every "
          "other constant.",
          "Lock the four runtime constants — prompts, tool results, model "
          "version and seed — and replay inside an isolated lab.",
          "Runs that reproduce identically. A run you cannot reproduce is a "
          "story, and stories do not survive being disputed."),

"C1.11": ("A finding that stays in a notebook changes nothing and regresses "
          "unseen.",
          "Hand it over as three things: the control it becomes, the owner who "
          "holds it, and an evaluation case that fails on the old build.",
          "Findings leaving with all three. Any missing one is a promise "
          "rather than a control."),

})

# ---- D · The Agentic SOC -------------------------------------------------
DAYS.update({

"D1.0": ("A detection stack tuned for human tempo, watching an actor that acts "
         "a thousand times an hour, reports nothing and means nothing.",
         "Learn the five intervals and the open-source stack that measures "
         "them, before building anything.",
         "The five intervals themselves — discover, detect, understand, "
         "contain, recover. Every later lesson moves one of them."),

"D1.1": ("Four products are bought, the estate is assumed covered, and the "
         "agent's whole working day falls between them.",
         "Score each sensor class on visibility rather than alerting, per agent "
         "action, and read the rows nothing covers.",
         "Four of nine ordinary agent actions seen by no sensor class at all. "
         "That column is an architecture finding, not a tuning backlog."),

"D1.2": ("A detection that worked last month is silently degraded, because the "
         "model, the prompt or the tool list changed and none of it was a code "
         "change.",
         "Sign off a baseline, then watch the four surfaces that move without "
         "raising a ticket.",
         "Time between a behaviour change and its detection — and the share of "
         "controls currently outside their freshness window."),

"D1.3": ("An agent nobody registered acts under a person's credential, and "
         "conventional analytics read it as that person behaving oddly.",
         "Score actors on regularity, rate and continuity, then decide "
         "per-field retention on the traces you inherit.",
         "Unregistered actors surfaced, and the threshold chosen by expected "
         "cost — a flagged human costs half an analyst-hour, a missed agent "
         "costs forty."),

"D2.1": ("Everything is indexed hot because nobody priced it, so retention is "
         "cut across the board and the agent traces go first.",
         "Tier each source by the fastest query that reads it, and price the "
         "result against indexing everything.",
         "29% cheaper on the sample estate — and, more importantly, the "
         "prompts that are 23% of the volume survive at 1% of the hot price "
         "instead of being deleted."),

"D2.2": ("Classic baselines call two countries in an hour an incident and "
         "300 file reads a minute an incident; for an agent both are ordinary.",
         "Detect change rather than activity — a tool never used before, a "
         "shifted mix, a scope newly exercised — and map each to ATT&CK and "
         "ATLAS.",
         "Rules carrying a technique id, and the honest gap: indirect prompt "
         "injection has no ATT&CK technique, and mapping it to an adjacent one "
         "to complete a chart is how a programme lies to itself."),

"D2.3": ("Platform-layer compromise is invisible to workload-layer detection — "
         "not detected late, not detected at all.",
         "Write detections whose subject is the platform: escape primitives, "
         "poisoned cache entries, silently expired exemptions.",
         "Platform events caught by named primitives versus by a generic "
         "anomaly score, which is the comparison that shows why they are "
         "separate rules."),

"D2.4": ("An agent writes candidate rules faster than anyone can review them, "
         "and a rule at 5% precision is not 5% useful — it is negative.",
         "Let the loop generate, then score every candidate against real "
         "historical telemetry before anything ships.",
         "Firing volume per true positive. A rule at 301 alerts to 1 is "
         "rejected with its number rather than with an opinion."),

"D2.5": ("Every candidate rule catches the incident it was generated from, so "
         "catching it cannot be the test.",
         "Score candidates against a benign corpus containing the hard cases — "
         "for a refund rule, legitimate refunds.",
         "False-positive rate on benign traffic: 21% buries the queue, 0% with "
         "generalisation ships, 0% matching only this incident is useless."),

"D2.6": ("Every other detector needs a threshold, and every threshold trades "
         "misses against false alarms.",
         "Place canaries and honeypot tasks where nothing legitimate has a "
         "reason to go.",
         "A false-positive rate of zero by construction — and the number of "
         "canaries legitimate work reaches, which destroys that property."),

"D3.1": ("Supervising a loop by re-reading everything it did is not "
         "supervision, and a loop that closes a true positive does so "
         "silently.",
         "Decide what the loop may conclude, what it may do unsupervised, and "
         "which sample of its closures a human reads.",
         "Alerts escalated versus closed against ground truth, and the "
         "severity floor no automatic closure may cross."),

"D3.2": ("Incident response grants the broadest read in the organisation at "
         "the moment of least supervision — and that grant is often larger "
         "than the incident.",
         "Bound the investigating agent per investigation class before it runs: "
         "sources, forbidden fields, volume cap.",
         "This one spends time on purpose. Measure refusals logged with their "
         "query — the evidence you stayed on the right side of the line."),

"D3.3": ("An alert about an agent without scope, identity and delegation is "
         "not triageable, so analysts escalate everything or quietly close "
         "everything.",
         "Add the three fields an agent alert needs on top of who, what and "
         "when.",
         "Analyst decisions matching ground truth with and without context — "
         "the same alert, two accuracies."),

"D3.4": ("Three responder instincts that are right for people misfire on "
         "agents, and each one burns the clock.",
         "Revoke the agent identity rather than disabling the account, read "
         "the plan rather than interviewing the user, and assume a chain "
         "rather than an actor.",
         "Time lost to each misfire, and whether the bearer token was still "
         "valid after the account was disabled."),

"D3.5": ("A model correlates thousands of log lines in seconds and will "
         "produce a fluent narrative from logs that never supported one.",
         "Separate what the logs establish from what the reconstruction infers, "
         "and keep the evidence beside each claim.",
         "Claims with a log line behind them, as a share of claims in the "
         "timeline. A fast conclusion is not a finished one."),

"D3.6": ("An agent scoring evidence only on support confirms its first theory "
         "and never terminates.",
         "Force a replan when evidence refutes, and keep the abandoned branch "
         "visible in the trace.",
         "Branches considered and dropped, visible to a reviewer. A trace with "
         "one branch is not an investigation."),

"D3.7": ("The agent that touched the resource is usually the last actor in a "
         "chain, and the earlier ones had more authority, not less.",
         "Scope along the delegation graph rather than the host list.",
         "Resources found by walking the graph versus by scoping the acting "
         "agent alone. The undercount grows with delegation depth."),

"D3.8": ("Coordination between runs that are supposed to be independent is "
         "invisible to per-run analysis by construction, not by tuning.",
         "Move where the monitoring sits: a shared-artifact graph and four "
         "other cross-run signals.",
         "Coordinated runs detected across the population versus zero detected "
         "within any single run."),

"D3.9": ("Intelligence that stays a narrative about adversary trends moves "
         "nothing, however well written.",
         "Convert each indicator into a rule, or record why it cannot be one.",
         "Detections produced per intelligence report. It is the only measure "
         "of an intel function that survives scrutiny."),

"D3.10": ("Everything not covered by a rule is invisible, and the rules were "
          "written against behaviour somebody already understood.",
          "State a falsifiable hypothesis, name the population before running "
          "it, then promote, tune or discard.",
          "Precision of the hunt: a hypothesis matching fourteen runs to find "
          "two, because twelve are the nightly batch, has bought nothing."),

"D4.1": ("Automation scope decided per runbook means the blast radius of your "
         "response is unknown until the response fires.",
         "Classify every action on reversibility and blast radius, and derive "
         "the tier from those two properties.",
         "Actions with a tier derived from policy rather than chosen by an "
         "author — and reversibility outranking radius, which is the policy."),

"D4.2": ("\"Automate everything\" and \"keep a human in it\" are both "
         "asserted constantly and neither is a position.",
         "Time all three tiers against one incident, with the cost of acting "
         "on a bad signal beside the time to contain.",
         "14 seconds at 8 errors per hundred, against 2,072 seconds at 0.2, "
         "against a measured breakout of 1,740. The manual tier is a risk "
         "decision, not the safe one."),

"D4.3": ("An agent at 300 actions a minute takes about 2,400 further actions "
         "inside an eight-minute approval cycle.",
         "Pre-authorise automated revocation of non-human identities, which is "
         "safe precisely because they are not people.",
         "Actions taken during containment: roughly 2,400 with a human in the "
         "path, about 60 without."),

"D4.4": ("Stop authority is the control everyone assumes exists and almost "
         "nobody has timed.",
         "Answer five questions with a name or a number each: who, what "
         "mechanism, how long, what breaks, who turns it back on.",
         "Measured time-to-stop, end to end, from a real exercise. An untimed "
         "stop authority is an intention with a runbook attached."),

"D4.5": ("Terminating agents while their credentials stay valid leaves the "
         "persistence exactly where it was.",
         "One selector, one action, and revocation rather than termination.",
         "What the credentials can still do after the processes stop. That is "
         "the number that says whether containment ended the incident."),

"D5.1": ("Miss one of the four runtime constants and you can describe what "
         "happened but never demonstrate it.",
         "Log at design time what a replay will need: prompts, tool results, "
         "model version, sampling.",
         "Runs that reproduce identically. The model version is the field most "
         "often missing and the one that invalidates the rest."),

"D5.2": ("An incident that closes with a narrative recurs, because nothing in "
         "a narrative can be built or measured.",
         "Walk the control chain, mark each present, absent or present-but-"
         "wrong, and test that the statement names a control.",
         "A mechanical test: does the root cause name a control? \"The engineer "
         "missed the alert\" is true and fails it."),

"D5.3": ("The fix goes to the prompt when the bug is in the control plane, and "
         "the layers that bypass process are the ones edited under pressure.",
         "Choose among model, prompt, tool, policy, sandbox, identity and eval "
         "deliberately.",
         "Post-incident changes that went through a process leaving a record — "
         "the ones that did not are the next incident's head start."),

"D5.4": ("A closed ticket is not evidence that a control came back.",
         "Re-measure the indicators the incident moved, automatically, on every "
         "fix rather than the memorable ones.",
         "Indicators restored to target versus merely improved. Detection went "
         "from 194 minutes to 118 against a 15-minute target, which every "
         "system that does not re-measure records as done."),

"D5.5": ("Most incidents change what is deployed and leave what is allowed "
         "untouched, so the next system reproduces the conditions.",
         "State the change as a policy diff with the incident's numbers as the "
         "reason, and name what the diff does not fix.",
         "Clauses changed, and the indicators no policy change can fix — which "
         "are engineering items, named so they do not fall between functions."),

"D5.6": ("The clock starts at awareness, not at confirmation, and it does not "
         "pause while you work out who acted.",
         "Run the first-hour checklist, with separate owners for containment "
         "and disclosure.",
         "Hours from awareness to a disclosure decision, against the deadline. "
         "Containing in an hour buys none of it back."),

})

# ---- E · AI Governance for Agentic Systems -------------------------------
DAYS.update({

"E1.0": ("A trustworthy-AI statement with no owner per property means every "
         "property is somebody else's job.",
         "Assign each of the seven properties an owner, and read the three "
         "chapters as one unit built, evidenced and run.",
         "Properties with a named owner. Security owns one of seven outright, "
         "which is why this is not a security document."),

"E1.1": ("A control tested six months ago is not passing — it is unevidenced, "
         "and most tooling cannot represent that third state.",
         "Turn a framework control into something computable, with a "
         "denominator and a target written before the measurement.",
         "The unit itself: a key control indicator. Everything else in this "
         "function produces one, feeds one, or reports one."),

"E1.2": ("You cannot govern, tier, test or revoke what you cannot list, and "
         "most of it is already in production.",
         "Reconcile three sources — model registry, procurement, and egress "
         "logs to provider domains.",
         "The denominator for every other indicator. A share whose denominator "
         "is unknown is a count wearing a percentage sign."),

"E1.3": ("Tiering by model name tracks vendor marketing rather than exposure, "
         "and gets the dangerous case exactly backwards.",
         "Tier on autonomy, data reach and blast radius — what the system can "
         "do, not what it runs on.",
         "The target each indicator carries. The same measurement means "
         "different things on a tier-1 and a tier-3 agent."),

"E1.4": ("A framework-first mapping produces a complete checklist that "
         "defends nothing, because a clause with no operating control behind "
         "it evidences nothing.",
         "Map control to framework, never the reverse, and let coverage fall "
         "out as an output.",
         "Mapped controls with an indicator behind them. Those without are "
         "unevidenced, and most tooling renders them green."),

"E1.5": ("A vendor's best-of-k demo is not assurance, and schema conformance "
         "is not accuracy.",
         "Report accuracy against a held-out key, with the sample size and an "
         "expiry.",
         "An eval result read as an indicator: sample size is the denominator, "
         "the pass bar is the target, the expiry stops it ageing into a claim."),

"E1.6": ("Shipping only operating guardrails and reporting them as coverage is "
         "how a programme passes audit while missing harm.",
         "Separate constraints on how the system runs from constraints on what "
         "results are acceptable.",
         "Two different indicators. An operating one says the constraint was "
         "applied; an outcome one says it worked."),

"E1.7": ("Point-in-time assurance describes a system that no longer exists by "
         "the time anyone reads it.",
         "Re-run the evidence collection inside a freshness window derived from "
         "how fast the thing actually changes.",
         "Controls currently evidenced — passing and in window — rather than "
         "controls that once passed. The number drops, and it is the first "
         "honest one."),

"E1.8": ("For a hosted model the estate holds no source to measure, so there "
         "is nothing to compute an indicator from.",
         "Assess each component on whether it can change without telling you, "
         "and accept an attestation with an expiry where it can.",
         "Third-party controls carrying an unexpired attestation. It is a "
         "weaker instrument than a measurement, and worth scoring as one."),

"E1.9": ("A retrain, a fine-tune or a re-index is treated as maintenance, and "
         "it invalidates every reading taken before it.",
         "Govern the lifecycle events that raise no ticket, not the ones that "
         "do.",
         "Indicators marked stale by a lifecycle event — the difference "
         "between continuous assurance and a dashboard showing last quarter."),

"E1.10": ("Five functions each hold part of the AI control estate and none "
          "holds all of it, so each assumes another has the middle.",
          "Map who asks what: liability, obligation, lawful basis, "
          "containment, fitness.",
          "One reading, five readers. The question nobody asked is the one no "
          "indicator was built for."),

"E1.11": ("The classical model-risk playbook silently breaks once the model "
          "can act, because validation was scoped to predictions.",
          "Re-read the three pillars for a model that calls tools.",
          "Ongoing monitoring, which is a key control indicator programme in "
          "older vocabulary — the lineage that convinces a risk function this "
          "is not new."),

"E1.12": ("The functions work and the handoffs leak, and both sides are "
          "usually right about their own scope.",
          "Write a joint runbook per seam: one artefact, one owner, named "
          "consumers.",
          "Seams with an owned artefact. An indicator with two consumers and "
          "no owner gets computed twice, differently."),

"E1.13": ("A control asserted in a register and never measured has no evidence "
          "behind it until an incident supplies some.",
          "Compute the indicators from the repository at run time, and report "
          "gaps with the lesson that closes each.",
          "Six indicators against CyberTravels: five gaps and one pass. The "
          "pass is what proves the instrument discriminates."),

"E2.1": ("One programme per regime is four times the work and none of it "
         "joined up.",
         "Separate horizontal regulation, sector overlays and cross-cutting "
         "law, and map controls outward.",
         "Regimes an indicator can be quoted to. They overlap on evidence, not "
         "on wording."),

"E2.2": ("\"We only deployed it, we didn't build it\" is sometimes true and "
         "often not, and the answer changes what you owe.",
         "Resolve each regulatory theme down to a control from your own "
         "catalogue and let its evidence be the answer.",
         "Themes with a control and an artefact behind them. Oversight is the "
         "hardest, because the action completes before a human sees it."),

"E2.3": ("Regime-specific mappings have nothing to hang off, so each new law "
         "restarts the programme.",
         "Pick a control-shaped framework as the spine and map outward from it.",
         "Indicators the spine already computes that each new overlay can "
         "reuse — and the gaps the spine does not reach, stated plainly."),

"E2.4": ("The sector regime you are already in applies to agents without ever "
         "using the word AI.",
         "Find the clauses that catch agents: third-party risk, exit strategy, "
         "scope containment, minimum necessary.",
         "Thresholds that move rather than indicators that are new — a much "
         "smaller job than inventing a measurement programme."),

"E2.5": ("The context window is a disclosure and the trace is a record, so "
         "personal data lands in a system nobody reviewed.",
         "Fix lawful basis, retention on the trace itself, and an erasure path "
         "that reaches it.",
         "Paths rather than outcomes: where inference ran, what retrieval "
         "touched, how long a trace was kept. All three are computable."),

"E2.6": ("The clock starts at awareness and broken attribution consumes it, "
         "so containing fast buys no reporting time.",
         "Write the trigger criteria before they are needed, with separate "
         "owners for containment and disclosure.",
         "Whether the pre-incident reading existed at all. During an incident "
         "you are either quoting a measurement or guessing."),

"E2.7": ("Documentation that restates intent is what supervision fails.",
         "Make every sentence name a control, an artefact and a date.",
         "Indicator readings with dates on them. A narrative describing a "
         "control is not evidence that it operated."),

"E2.8": ("Without attribution and replay captured at the moment of the action, "
         "neither can be reconstructed afterwards.",
         "Capture the acting identity, the principal and the chain, plus enough "
         "to replay the run.",
         "Share of autonomous actions whose full chain can be reconstructed. "
         "Anything below 1.00 is the part you cannot audit."),

"E2.9": ("A supervisor who finds a weakness you did not disclose doubts "
         "everything else you said.",
         "Bring the weakest number first, with its denominator and the gaps you "
         "already know about.",
         "Coverage stated honestly, including stale and unevidenced controls. "
         "Volunteering the distinction is what makes the rest credible."),

"E3.1": ("A board cannot act on \"we found prompt injection\"; it can act on "
         "exposure, likelihood and a decision being requested.",
         "Drop the mechanism, keep three things, and offer written risk "
         "acceptance as a legitimate outcome.",
         "Three indicators the board sees, chosen from the set that already "
         "exists so anyone can re-compute them."),

"E3.2": ("A per-tool review queue becomes a bottleneck and then a bypass, "
         "within about a quarter.",
         "Govern the autonomy level instead: four rungs, each with its own "
         "conditions.",
         "What an agent may do without asking, as a function of measured "
         "containment rather than of which vendor supplied the tool."),

"E3.3": ("Starting with the most visible workflow rather than the most "
         "winnable is how programmes thrash.",
         "Sequence by dependency: inventory, identity, containment, evidence, "
         "evaluation, continuous.",
         "The order itself is the deliverable. Doing evaluation before "
         "identity produces a well-measured system nobody can switch off."),

"E3.4": ("Harness engineering with no home and research as a hobby means the "
         "seams have no names against them.",
         "Name an owner for each seam before the incident rather than during "
         "it.",
         "Seams with a name against them. If nobody owns the measurement, the "
         "indicator exists on a slide and nowhere else."),

"E3.5": ("Reporting activity instead of exposure gives a board numbers that "
         "stay flat under neglect.",
         "Report five that degrade on their own: exposure, likelihood, "
         "assurance, coverage, speed.",
         "Each is computed rather than assessed. A metric that does not "
         "degrade when ignored is measuring activity."),

"E3.6": ("Saying no is cheap and usually wrong — the capability ships anyway "
         "and you have traded influence for comfort.",
         "Say yes with conditions that are testable, proportionate, few and "
         "owned.",
         "Conditions met, each evidenced by an indicator crossing a threshold. "
         "Without one, \"yes with conditions\" becomes \"yes\" at the next "
         "review."),

"E3.7": ("Hiring for conceptual familiarity produces a team that can discuss "
         "the problem and not measure it.",
         "Staff for the ability to turn a control into something computable, "
         "and accept an unglamorous first quarter.",
         "What the team can evidence, quarter by quarter. Quarter one produces "
         "an inventory and no dashboard, which is the right shape."),

"E3.8": ("A programme judged on prevention is judged on something a "
         "probabilistic system cannot deliver.",
         "Judge it on three capabilities instead: notice, stop, recover.",
         "Containment, detection and recovery indicators — the same ones D5.4 "
         "re-reads after a fix. Prevention has no honest indicator here."),

})
