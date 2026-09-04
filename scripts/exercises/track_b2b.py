"""B1 (part 2) — The AppSec pipeline, phases 4 and 5, plus the bonus.

    Phase 4 · Dynamic Validation & Remediation
       11 sandbox replication                                      → B2.6
       12 dynamic exploitation (DAST)                              → B2.7
       13 exploit chaining                                         → B2.8
       14 remediation engineering                                  → B2.9
    Phase 5 · Governance & Reporting
       15 severity calibration and reporting                       → B2.10

    Cross-cutting
       context engineering for the pipeline                        → B2.11
       injection in your own pipeline                              → A1.9
       securing the developers' coding agents                      → B2.12
       attesting control intent for agents and MCP servers         → B2.13

    Bonus
       Google Mantis — the pipeline in production                  → B2.14
"""

PIPELINE_NOTE = """
> **Where you are in the pipeline.**
>
> ```
> [Ingestion & Mapping] ──> [Threat Modelling] ──> [Discovery]
>          └─ stages 1-4         └─ stages 5-6        └─ stages 7-10
>                    ──> [Dynamic Validation] ──> [Reporting]
>                              └─ stages 11-14        └─ stage 15
> ```
"""

MODEL_NOTE = """
> **About the model in this notebook.** It runs offline against a deterministic
> stand-in so the lesson executes on a Kaggle kernel with no network. The
> stand-in is not a language model and is labelled as such wherever it appears.
> To run the identical stage against a real open-weight model:
>
> ```bash
> ollama pull glm-4.6            # or kimi-k2, llama3.3
> export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
> ```
"""

from .skills import SKILL_RUNTIME, skill_steps

from . import diagrams as D

EXERCISES: dict[str, dict] = {

"B2.6": {
 "concept": """
Phase 4 turns hypotheses into facts by running the application. That is only
safe if the thing you run it against cannot hurt anyone.

**Stage 11 — Sandbox replication.** Deploy the application in an isolated,
disposable runtime: its own container, its own synthetic data, no route to
production, no real credentials.

The reason this is a *stage* rather than a footnote is that the obvious shortcut
— point the dynamic tests at staging — converts every destructive probe into an
incident. Staging usually shares an identity provider, a message bus, sometimes
a database replica, and always someone's on-call rota.

Four isolation properties, and you need all four:

- **network** — no egress except to the replica itself,
- **credentials** — synthetic secrets, so a leak is worthless,
- **data** — synthetic records, so an exfiltration test exfiltrates nothing,
- **lifetime** — destroyed after the run, so state cannot leak between tests.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 11 — model the replica and its isolation"),
("md", "## 3 · Where it breaks — the same probes against staging"),
("md", "## 4 · The control — the four isolation properties, checked"),
  *skill_steps('appsec/exploit-replica-isolation-check',
               "## 2 · The stage, as a skill\n\nBefore anything is executed against CyberTravels' environment, four checks decide whether it is a replica or staging with a different DNS name. The skill runs them — egress, credentials, data, and the destructive probes you would only run somewhere built to be destroyed."),
],
 "expect": "The replica permits only its own internal hosts and blocks GitHub, "
           "the metadata service and private addresses. Staging holds real "
           "credentials and a real-shaped customer record while the replica holds "
           "synthetic ones. The four isolation checks pass for the replica and "
           "fail for staging on credentials, data and lifetime, and destroying "
           "the replica clears its state.",
 "challenge": "Check whether your dynamic testing currently runs against staging. "
              "If it does, list what staging shares with production — identity "
              "provider, message bus, data replica. Each shared component is a "
              "path from a test probe to a real incident.",
},

"B2.7": {
 "concept": """
**Stage 12 — Dynamic exploitation.** The stage that converts an argument into a
fact.

Everything Phase 3 produced is a hypothesis: the code *looks* vulnerable and the
sink *appears* reachable. Hypotheses get argued about in triage meetings. An
executed exploit does not — either the probe achieved the effect or it did not.

Two things this stage produces that static analysis cannot:

- **Confirmation.** A finding that survives an exploit attempt is real,
  regardless of how the model felt about it.
- **Refutation.** A finding that fails is either not exploitable in this
  configuration or not real, and both are useful answers.

The discipline that makes it trustworthy is that the probe must assert a
**concrete effect** — rows returned that should not be, a file read outside the
root — not merely that the request did not error. "No exception" is the DAST
equivalent of a shape check, and B2.0 already established what those are worth.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · The replica application, running"),
("md", "## 3 · Stage 12 — probes that assert a concrete effect"),
("md", "## 4 · Where it breaks — the probe that asserts nothing\n\n"
         "The most common DAST bug: treating \"the request succeeded\" as "
         "confirmation. Both probes below hit the app and return 200-equivalents; "
         "only one of them proves anything."),
  *skill_steps('appsec/dynamic-exploitation-probe',
               '## 2 · The stage, as a skill\n\nA dynamic probe proves nothing unless its assertion can fail. The skill runs the probes against a live build with a control probe alongside, then re-runs them under a weak assertion so you can watch it flag the control too.'),
],
 "expect": "The SQL injection probe returns rows for three owners when one was "
           "requested, and the traversal probe returns the synthetic token from "
           "outside the document root; the control probe returns a single owner "
           "and is not flagged. The weak assertion confirms all three including "
           "the control. Stage 12 marks two findings CONFIRMED and one "
           "UNVALIDATED for having no probe.",
 "challenge": "Look at your DAST assertions. If any of them checks only for a "
              "non-error response, it is confirming findings it has not tested — "
              "and the control probe above is how you prove that in five minutes.",
},

"B2.8": {
 "concept": """
**Stage 13 — Exploit chaining.** Individual findings are triaged individually,
and that is how three mediums become a critical nobody noticed.

The arithmetic of severity is not additive. A read-only information disclosure
is a medium. A CSRF is a medium. An unauthenticated internal endpoint is a
medium. Chained — leak an ID, forge a request using it, hit the internal
endpoint with the forged session — the outcome is account takeover, which is
not a medium.

The pipeline can find these mechanically because Phase 4 already produced
confirmed findings with known **preconditions** and **effects**. If one
finding's effect satisfies another's precondition, they compose, and the chain's
severity is the severity of its final effect.

This is the stage that most often changes what gets fixed first.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 13 — findings as preconditions and effects"),
("md", "## 3 · Compose them — an effect that satisfies the next precondition"),
("md", "## 4 · Where it breaks — triage the links, miss the chain"),

  ("md", "## 6 · Phase 4 as a skill — and the preconditions that gate it\n\n"
         "Dynamic validation is the one phase that *acts*. Everything before it "
         "reads; this one sends input to a running system. The skill therefore "
         "opens with safety preconditions rather than a procedure, and a "
         "refusal is a first-class output.\n\n"
         "The contract also insists that `reproduced: false` be reported rather "
         "than dropped. A finding that survived Phase 3 and then failed to "
         "reproduce is the most useful signal the pipeline produces about its "
         "own false-positive rate — and it is the one a tidy report deletes."),
  ("skill", "appsec/appsec-exploit-validate"),
  ("skill_script", "appsec/appsec-exploit-validate/scripts/appsec_exploit_validate.py"),


  ("md", "## 7 · Where it breaks — the tidy report\n\n"
         "Now suppose two of these findings do not reproduce, and the pipeline "
         "does the natural thing with them."),
],
 "expect": "Six confirmed findings compose into multiple chains. The highest "
           "individual severity is high while the highest chained severity is "
           "critical, and at least one critical chain is built entirely from "
           "medium-or-lower links — for example SSRF granting internal network "
           "access, then the unauthenticated admin endpoint. Remediation ordering "
           "puts a medium finding first because it breaks the most chains.",
 "challenge": "Take your current open findings and write down each one's "
              "preconditions and effects. The chaining falls out mechanically, "
              "and the finding you should fix first is usually not the one at the "
              "top of the severity-sorted queue.",
},

"B2.9": {
 "concept": """
**Stage 14 — Remediation engineering.** Generate the fix, then prove it.

A model that finds bugs is useful. A model that fixes them is only useful if you
can tell a real fix from a plausible one, and plausible is exactly what language
models are optimised to produce.

There are three ways to make a finding stop firing:

1. **Fix the vulnerability** — behaviour preserved, bug gone.
2. **Remove the code** — finding gone, so is the feature.
3. **Evade the detector** — rewrite until the pattern misses.

All three make the scanner green, and an autonomous loop optimising for a green
scan will find options 2 and 3 on its own because they are cheaper.

The pipeline has an advantage a static workflow does not: Phase 4 already built
a working exploit. So the acceptance test is not "does the scanner still fire?"
It is **"does the exploit still work against the patched build?"** — which is
the only question that cannot be gamed by editing the code around the detector.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
("md", "## 2 · The confirmed finding, with its working exploit"),
("md", "## 3 · Four candidate patches, three of which make CI green"),
("md", "## 4 · The control — validate on three axes, exploit first"),
  *skill_steps('appsec/patch-validation-harness',
               '## 2 · The stage, as a skill\n\nSeveral candidate patches make the scanner green; one of them is a fix. The skill runs all three gates — behaviour unchanged, exploit blocked, and proof of fix against the old build — and reports which gate each rejected candidate died at.'),
],
 "expect": "The vulnerable build passes all four behaviour cases and the exploit "
           "returns 3 rows. Candidates A, B and D make the scanner green. "
           "Validation rejects B for changed behaviour and C for remaining "
           "exploitable, accepting A and D. Proof of fix holds for both accepted "
           "patches — the exploit works on the old build and fails on the new.",
 "challenge": "Candidate D passes every automated gate and is still wrong. Write "
              "the rule that rejects it. You will find it has to be about which "
              "*mechanism* is acceptable, not about outcomes — and that rule "
              "belongs in your secure coding standard, not in the pipeline.",
},

"B2.10": {
 "concept": """
**Stage 15 — Severity calibration and reporting.** The pipeline's output, and
the stage where its credibility is won or lost.

Most severity is a label copied from the rule that fired: this is a CWE-89, so
it is high. That number predicts nothing, because it ignores everything the
pipeline has just learned:

- did stage 12 **confirm it by execution**?
- is it **reachable** from an untrusted entry point (stage 10)?
- what does it **chain into** (stage 13)?
- does it sit in a **historical risk zone** (stage 1)?

Calibrated severity uses all four. A confirmed, reachable finding that chains
into account takeover is not the same as an unvalidated finding in dead code,
even when both are CWE-89.

The second half of this stage is the report, and the useful report is not a
finding count. It is **per-stage economics**: where bugs are caught, where they
escape, and what each escape costs — because that is what decides next
quarter's budget.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 15 — calibrate severity from what the pipeline learned"),
("md", "## 3 · Where it breaks — rule severity as the queue order"),
("md", "## 4 · The report — per-stage economics, not a finding count"),

  ("md", "## 6 · Stage 15 as a skill — severity you can argue with\n\n"
         "The reporting skill carries one rule that decides most of the "
         "credibility of a security report: **a finding that did not reproduce "
         "may not be Critical.** Cap it at Medium and say so in the same "
         "sentence, so the reader never has to cross-reference an appendix to "
         "learn that the headline finding is theoretical.\n\n"
         "The contract enforces the habit by requiring `severity_inputs` next "
         "to every severity. One overclaimed Critical costs more trust than ten "
         "honest Lows."),
  ("skill", "appsec/appsec-triage-report"),
  ("skill_script", "appsec/appsec-triage-report/scripts/appsec_triage_report.py"),


  ("md", "## 7 · Where it breaks — the uncalibrated headline\n\n"
         "Now report the same findings without the cap."),
],
 "expect": "Calibration moves several findings off their rule severity: the "
           "confirmed reachable CWE-89 that chains into account takeover becomes "
           "critical, while the unreachable and unvalidated ones fall. The top-3 "
           "by rule severity and by calibration disagree. The stage table shows "
           "review with the worst precision and highest minutes per finding, and "
           "design carrying the highest escape cost despite only two findings.",
 "challenge": "Recalculate severity for your current open findings using "
              "confirmation and reachability alone — you do not need chaining to "
              "see the effect. The queue reorders, and the items that fall are "
              "usually the ones people have been arguing about.",
},

"B2.11": {
 "concept": """
Cross-cutting, and it applies to every stage that calls a model: stages 3, 4, 5,
7 and 14.

The instinct when a model misses something is to give it more context. Usually
the opposite is correct.

To find a vulnerability, a model needs three things: the **sink**, the
**source**, and the **path** between them. Everything else competes for
attention and for window. A repository dumped into a prompt does not produce a
thorough review — it produces a review of whatever survived truncation, and you
cannot tell which parts those were.

So context engineering is mostly subtraction, with one exception you must not
subtract: the **enclosing signature**, because that is where reachability is
decided. The identical concatenation is critical inside an HTTP handler and
irrelevant inside a migration script that takes a constant.
""",
 "steps": [
  ("md", "## 2 · Demo — four strategies over one bug"),
("md", "## 3 · The control — slice on the source-sink path"),
  *skill_steps('appsec/context-window-sizing',
               '## 2 · The stage, as a skill\n\nContext engineering here is not "send less" — it is finding the slice in which the defect is decidable at all, and only then making it smaller. The skill measures four candidate slices and reports which are decidable and what each carries that the defect does not depend on.'),
],
 "expect": "The whole file is roughly 840 characters, the ±2 window about 200 and "
           "the path slice about 390. The ±2 window is not decidable because it "
           "lacks the signature; the ±6 window and the whole file are decidable "
           "but carry unrelated functions. The path slice is the smallest "
           "decidable context with zero unrelated functions, about 53% smaller "
           "than the whole file.",
 "challenge": "Apply the path-slice rule where the source is three functions away "
              "from the sink. That is the case where text windows break down "
              "entirely and the call graph the threat model derives (B2.2) earns its keep.",
},

"B2.12": {
 "concept": """
The coding agent in a developer's IDE is the most privileged agent in most
organisations and the least governed. It sits upstream of everything this track
has built: it writes the code the pipeline later analyses.

What it holds by default:

- the developer's **git credentials** — push access to everything they can push to,
- the **whole monorepo** on disk, including files they never open,
- a **shell**, usually unrestricted,
- their **cloud credentials** in `~/.aws` or `~/.config/gcloud`,
- whatever **MCP servers** they connected, each with its own authority.

That is a production identity in an unmanaged environment, driven by a model
reading code from the internet.

The binding constraint here is not technical feasibility — it is **developer
tolerance**. A containment scheme that adds friction to the inner loop is
disabled within a week, and a disabled control protects nothing. So the design
goal is the strongest containment a developer does not notice.
""",
 "steps": [
  ("md", "## 2 · Demo — measure the default configuration"),
("md", "## 3 · The control — rank by friction, ship the invisible ones first"),
  ("html", D.table(
    ["control", "friction", "what developers actually experience"],
    [["deny-list credential paths", "0.0",
      "the agent cannot read ~/.aws, ~/.ssh, ~/.env. Developers never noticed."],
     ["workspace confinement", "0.1",
      "the agent sees the open repo only. Occasionally annoying for monorepo hops."],
     ["egress allowlist", "0.2",
      "package registries and your VCS. Breaks the odd curl in a generated script."],
     ["gate <code>git_push</code>", "0.4",
      "one confirmation before code leaves the machine. Noticed, usually accepted."],
     ["gate every write", "0.9",
      "<b>confirmation per file write. Abandoned within a week, every time.</b>"],
     ["no shell at all", "1.0",
      "<b>removes the inner loop. Nobody will use the agent.</b>"]],
    emphasise=1,
    caption="The first four ship today and cost nothing anyone will complain "
            "about. The last two are the ones people propose in meetings, and "
            "they are uninstalled by Friday — a control that gets turned off is "
            "worth less than a weaker one that stays on.")),

  ("md", "## 6 · The audit, as a skill an agent runs on itself\n\n"
         "Everything in this lesson is a review someone has to remember to do. "
         "Written as a skill, it is a review that fires whenever an agent opens "
         "a repository — including this one.\n\n"
         "The skill's central instruction is easy to miss and decides the "
         "outcome: **rate an injection finding by what the allowlist permits, "
         "not by the text of the injection.** The payload is the attacker's "
         "choice and costs nothing to change; the allowlist is yours."),
  ("skill", "appsec/coding-agent-hardening"),
  ("skill_script", "appsec/coding-agent-hardening/scripts/coding_agent_hardening.py"),

],
 "expect": "The default developer agent scores a blast radius of 43 and can reach "
           "all seven paths including AWS, SSH and gcloud credentials. Containment "
           "reduces reachable paths to one source file with zero credentials "
           "reachable, and gating `git_push` drops the blast radius to 37 for 0.4 "
           "friction. The three lowest-friction controls remove every credential "
           "path without touching the inner loop.",
 "challenge": "Ship the credential deny-list first — it is a config file, it takes "
              "an afternoon, and no developer will notice. Then find out how many "
              "agents in your organisation could read `~/.aws/credentials` "
              "yesterday.",
},

"B2.13": {
 "concept": """
Every control claim in this pipeline has the same weakness: it is a sentence in
a document, and nothing binds it to a running system. "We enforce least
privilege" is true of some deployment, at some time, and there is no way to
re-check it when the image, the role or the tool surface changes.

An **attestation** fixes the binding. It is a signed statement about a specific
deployment, carrying per-control verdicts and the evidence behind each one, that
can be re-issued whenever anything it describes changes.

Two design decisions carry the whole idea.

**A `deployment_id` is the join key.** It resolves to a manifest of
content-addressed artefacts — repo at a commit, image by digest, IAM role,
workload identity, gateway route, guardrail ID, downstream services. Without it
an IAM finding, an identity entry and a gateway policy are three unrelated facts
about three things that may not be the same system.

**Eleven skills, not one.** One resolver, nine collectors split along
evidence-source boundaries (code, IAM, network, sandbox, identity, gateway,
ingestion, risk register, entitlements), and one signer. They split there
because each needs different API clients — and they stay separate because a
single mega-skill produces context bloat and verdicts nobody can read.

Then the part that makes it honest. **Not every control is equally verifiable:**

| Control | Confidence | Why |
|---|---|---|
| C1 default-deny / least privilege | HIGH | policy documents plus observed usage are readable |
| C3 identity chain / OBO | HIGH | delegation is impossible without an actor token, so its presence is proof |
| C4 gateway routing | HIGH **if** egress is enforced below the application | otherwise an agent opens a socket and bypasses it |
| C2 sandbox / no egress | **PARTIAL, capped** | absence of a covert channel is not provable; DNS and object-storage bypasses are documented |
| C5 injection screening | **PARTIAL, capped** | detector presence is verifiable; adaptive attacks drive published defences back above 95% success |

A tool that reports PASS on C2 or C5 is wrong, and the cap belongs in the
artefact rather than in a footnote.
""",
 "steps": [
  ("md", "## 2 · The skill that does the static half"),
  ("skill", "attestation/agent-code-surface-analyzer"),
  ("skill_script", "attestation/agent-code-surface-analyzer/scripts/agent_code_surface_analyzer.py"),

  ("md", "## 3 · Control intent, and why it is the honest static claim\\n\\n"
         "Static analysis cannot show that a control **holds**. It can show "
         "that somebody **intended** it — an imported sandbox, a validated "
         "audience claim, a provenance tag. That is a smaller claim and a true "
         "one, so the analyser never emits PASS."),

  ("md", "## 4 · Run against ten real repositories\\n\\n"
         "These are the verdicts the analyser in `labs/attestation/control_intent.py` "
         "produced against the five most-deployed open-source MCP repositories and "
         "five most-used agent frameworks, cloned at HEAD. Not a simulation — the "
         "counts below are what the scan returned."),

  ("md", "## 5 · What the scan actually found\\n\\n"
         "Three findings worth more than the table."),

  ("md", "## 6 · The artefact\\n\\n"
         "An in-toto statement, subject-bound to the deployment, predicate in "
         "assessment-results vocabulary. The signer is a separate skill and a "
         "separate role — an attester that also decides whether it passed is not "
         "an attestation."),
],
 "expect": "Five controls resolve to INTENT_EVIDENCED, PARTIAL or NO_INTENT_FOUND "
           "and never to PASS. Across ten real repositories and fifty control "
           "evaluations the analyser returns 30 INTENT_EVIDENCED, 16 PARTIAL, 4 "
           "NO_INTENT_FOUND and zero PASS — with one widely-deployed MCP server "
           "shipping no tool annotations at all, so all of its tool sites inherit "
           "the specification's destructive, open-world default.",
 "challenge": "Run the analyser against one agent or MCP server you actually "
              "deploy. The interesting output is not the verdicts — it is the "
              "controls that come back NO_INTENT_FOUND, because those are the "
              "ones nobody has started.",
},

"B2.14": {
 "concept": """
**Bonus.** You have now built all fifteen stages. This lesson looks at a real
implementation of the same pipeline — **[Google Mantis](https://github.com/google/mantis)**
— and does the one thing that matters before adopting any of them: maps its
stages onto yours, then **scores it with your own held-out key.**

Two things are worth understanding about Mantis specifically.

**It is model-agnostic.** Mantis ships security-review *skills* for coding
agents rather than a bundled model. That is the same architecture as this track:
the pipeline is the product, the model is a component. It means you can run it
on open weights — GLM-4.6, Kimi K2 — which is what makes it usable without a
frontier account.

**It has two output shapes**, and they serve different stages:

- a **`learning_entry`** — appended to a historical learnings file, feeding
  stage 1 (historical parsing) on the next run;
- a **`finding`** object — a vulnerability report, feeding stages 8–10.

That first shape is the interesting one. It closes the loop from Phase 5 back to
Phase 1, which is the property that turns a pipeline into something that
improves.

The bonus framing is deliberate: a reference implementation is a **starting
point you evaluate**, not a product you trust. C2.6 gave you the tools;
this is where you point them at someone else's pipeline.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Map Mantis onto the fifteen stages\n\n"
         "Adoption starts with the coverage question: which stages does it do, "
         "which does it assume you already have, and which are still yours?"),
("md", "## 3 · Parse the two output shapes\n\n"
         "Before scoring anything you have to ingest it. Both shapes are JSON; "
         "the `history` field on a learning entry is required and is the one most "
         "commonly missing in a first integration."),
("md", "## 4 · Score it against a held-out key\n\n"
         "This is the whole point of the bonus. Conformance is structural — with "
         "structured output it goes to 1.00 and says nothing about quality. The "
         "number that decides adoption is expert accuracy against a key the tool "
         "never saw, matched on **parent directory plus filename**."),
  *skill_steps('appsec/reference-pipeline-scoring',
               "## 2 · The stage, as a skill\n\nGoogle's Mantis is a set of claims: these stages, this output shape, this accuracy. The skill checks all three — maps it onto the stage model, conformance-checks its published samples, and scores its findings against a held-out key."),
],
 "expect": "The stage map shows Mantis covering stage 7 strongly with a stage-1 "
           "learning loop, and not covering Phase 4 at all. Three of five sample "
           "outputs conform — one learning entry is missing the required "
           "`history` field, one finding has a null CWE, and one is prose. "
           "Scored against the held-out key, expert accuracy is below 1.0: one "
           "correct, one half credit for the null class, and one missed finding "
           "Mantis never reported. The learning entry then feeds the next run's "
           "risk zones.",
 "challenge": "Run the real thing: clone `google/mantis`, point it at a "
              "repository you have ground truth for, and score its output with "
              "a scoring harness. The gap between its conformance and its "
              "expert accuracy on *your* code is the only number that should "
              "decide whether you adopt it.",
},
}
