"""E2 — The Regulatory & Compliance Lead. Nine sessions.

    E2.1  the regulatory map — three layers, and which one bites first
    E2.2  horizontal AI regulation as controls, not clauses
    E2.3  voluntary frameworks as the spine
    E2.4  sector overlays, which already applied
    E2.5  privacy: the context window is a disclosure
    E2.6  incident and disclosure obligations
    E2.7  documentation that survives supervision
    E2.8  auditability of autonomous action
    E2.9  regulator and auditor conversations
"""

from . import diagrams as D

from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"E2.1": {
 "concept": """
The regulatory picture for an AI system has three layers, and confusing them is
how programmes end up heavily invested in one while blind to another.

1. **Horizontal AI regulation** — applies *because it is AI*, regardless of what
   you do. The EU AI Act is the archetype.
2. **Sector overlays** — apply *because of what you do*, and mostly predate AI
   entirely: DORA for financial services, HIPAA for health, PCI DSS for card
   data, NIS2 for critical infrastructure.
3. **Cross-cutting law** — applies to the *data and the outcome*: GDPR and
   privacy law, consumer protection, sectoral incident reporting.

The common mistake is treating layer 1 as the whole map. For most organisations
layers 2 and 3 bite first and harder, because they already apply, they already
have supervisors, and their clocks are shorter.

The useful exercise is never "what does the AI Act say". It is: **locate one
system on all three layers and find the shortest clock.**
""",
 "steps": [
  ("md", "## 2 · Demo — the three layers, and what triggers each"),
  ("html", D.table(
    ["layer", "instruments", "triggered by", "lead time"],
    [["1 · horizontal AI regulation",
      "EU AI Act, national AI acts in progress",
      "the system being AI, and its risk classification",
      "months to years of transition"],
     ["2 · sector overlays",
      "DORA (financial), HIPAA (health), PCI DSS (cards), NIS2 (CNI)",
      "what your organisation does",
      "<b>none — already applies</b>"],
     ["3 · cross-cutting",
      "GDPR and privacy law, consumer protection, incident reporting",
      "the data processed and the outcome produced",
      "<b>none — already applies</b>"]],
    emphasise=3,
    caption="Layer 1 is the one that gets written about and the one with time "
            "left on it. Layers 2 and 3 were already in force before anyone "
            "deployed an agent.")),
  ("md", "## 3 · Locate one system on all three layers"),
("md", "## 4 · The control — the shortest-clock register\n\n"
         "Your real deadline is not the one you have read about. It is the "
         "shortest one that applies."),
  *skill_steps('regulatory/obligation-mapping',
               "## 2 · The procedure, as a skill\n\nCyberTravels' claims-triage agent attracts obligations from all three layers at once. The skill resolves each layer independently and registers the shortest clock among them, because that is the one the incident runbook has to meet."),
],
 "expect": "The three layers print with what triggers each. The claims-triage "
           "agent attracts obligations from all three — EU AI Act, DORA, a "
           "HIPAA-equivalent and GDPR. The shortest-clock register identifies "
           "DORA's 4-hour initial notification as the binding deadline, and "
           "layers 2 and 3 together produce more obligations than the horizontal "
           "AI regulation.",
 "challenge": "Build the shortest-clock register for your highest-tier AI system. "
              "Most teams discover the binding deadline is a sector overlay or a "
              "customer contract, not the AI regulation they have been reading.",
},

"E2.2": {
 "concept": """
Horizontal AI regulation is, in practice, mostly about **documented process and
human oversight**. That is good news, because those map onto controls you can
build and evidence mechanically.

The trap is answering a clause with a policy document. "We maintain appropriate
human oversight" satisfies nobody who asks the follow-up question, and the
follow-up question is always the same: *show me*.

So the working method is to resolve each regulatory theme down to a control from
your own catalogue (E1.4), and let the control's evidence be the answer. Four
themes cover most of it:

- risk management system,
- record-keeping,
- human oversight,
- accuracy and robustness.

Each one resolves to controls you already built in tracks A, B and D.
""",
 "steps": [
  ("md", "## 2 · Demo — resolve each theme to a control with evidence"),
("md", "## 3 · Where it breaks — the clause answered with prose"),
("md", "## 4 · The control — produce the evidence, then check it is fresh"),
  *skill_steps('regulatory/horizontal-requirement-to-control',
               '## 2 · The procedure, as a skill\n\nThe skill maps four regulatory themes to named controls with concrete artefacts, then applies the show-me test to the prose answers a policy currently offers — and counts how many sentences survive it.'),
],
 "expect": "Four regulatory themes resolve to named controls, each with a concrete "
           "evidence artefact. All four prose answers fail the show-me test. "
           "Checking freshness, two themes are fully evidenced — human oversight "
           "fails on a stale SB-2 and risk management on a failing DR-1 — giving a "
           "smaller but defensible statement.",
 "challenge": "Take one clause your programme claims to satisfy and trace it to "
              "an artefact with a date. If the trail ends at a policy document, "
              "the clause is ticked and undefended.",
},

"E2.3": {
 "concept": """
Voluntary frameworks make a better spine than regulation, for two reasons that
have nothing to do with enthusiasm for standards.

**They are written as controls.** NIST AI RMF and ISO 42001 describe things you
*do*. Regulation describes outcomes you must achieve, which is harder to
operationalise and easier to satisfy on paper.

**They change more slowly than the law.** Building against a framework and
mapping outward to regulation means new regulation is a mapping exercise rather
than a programme.

The method: pick one spine with the best coverage of the controls you actually
operate, map outward, and be explicit about what the spine does **not** reach —
because every spine has gaps, and the gaps are where the sector overlay lives.
""",
 "steps": [
  ("md", "## 2 · Demo — which spine covers your control set best"),
("md", "## 3 · Where it breaks — one framework per regulation"),
("md", "## 4 · The control — one spine, mapped outward, gaps named"),
  *skill_steps('regulatory/framework-spine-selection',
               '## 2 · The procedure, as a skill\n\nThe skill computes coverage per framework against your own control catalogue, selects the widest as a spine, and supplies the remaining three controls from the others — then costs that against building a programme per framework.'),
],
 "expect": "NIST AI RMF covers the most controls (4 of 8) and is selected as the "
           "spine, leaving SB-2, EV-1 and ST-1 as gaps supplied by ISO 42001, the "
           "EU AI Act and DORA. Building per-framework would produce 14 control "
           "implementations for 8 distinct controls — a 1.8× duplication factor "
           "with controls claimed by several frameworks drifting apart.",
 "challenge": "Pick your spine and justify it in one sentence to an assessor. "
              "\"It has the best coverage of the controls we actually operate\" is "
              "far stronger than \"it is the one our regulator mentioned\".",
},

"E2.4": {
 "concept": """
Sector overlays usually bite first, and the reason is structural: they already
applied before anyone deployed an agent, they already have a supervisor who
knows your organisation, and several of their clauses cover autonomous action
without ever using the word AI.

Four clause types that catch agents without naming them:

- **ICT third-party risk** (DORA) — your model provider is an ICT third party.
- **Exit strategy** (DORA) — can you stop using this provider? Most AI contracts
  have no answer.
- **Scope containment** (PCI DSS) — an agent with access to the cardholder data
  environment expands that environment.
- **Minimum necessary** (HIPAA) — the agent's context window is a disclosure.

Citing an existing clause is also far more effective internally than proposing a
new AI policy: it needs no new governance, and somebody already owns it.
""",
 "steps": [
  ("md", "## 2 · Demo — map agent facts onto pre-existing clauses"),
("md", "## 3 · Where it breaks — the exit-strategy clause"),
("md", "## 4 · The control — cite the existing clause, not a new policy"),
  *skill_steps('regulatory/sector-overlay-assessment',
               '## 2 · The procedure, as a skill\n\nSeven clauses already bind the claims-triage agent and none of them mentions AI. The skill searches on function rather than on technology, and assesses whether the hosted frontier API could be exited at all.'),
],
 "expect": "Seven pre-existing clauses apply to the claims-triage agent across "
           "DORA, HIPAA and PCI DSS, none of which mentions AI. The exit-strategy "
           "assessment marks the hosted frontier API as not defensible on all "
           "three counts, the hosted open-weight API on one, and self-hosted "
           "weights as defensible. Three cases show how to route the requirement "
           "to an existing owner rather than a new policy.",
 "challenge": "Find the clause in your own sector overlay that already covers "
              "autonomous action without naming AI. Citing it is faster, cheaper "
              "and more persuasive than any new AI policy you could write.",
},

"E2.5": {
 "concept": """
Privacy for agents turns on one fact that surprises most teams: **the context
window is a disclosure, and the trace is a record.**

When an agent reads a customer record to do its job, that record enters the
model's context. If the trace is retained — and it usually is, for forensics
(D1.5) — then personal data now exists in a system that was never in the privacy
review, with a retention period nobody set, in a place the erasure process does
not reach.

Three obligations attach, and the third is the one that bites:

- **Lawful basis** for the processing that put it there.
- **Retention limit** on the trace itself, separately from the source system.
- **Erasure** — and this reaches into traces, eval corpora, fine-tuning sets and
  backups.

The capability that makes erasure possible is the same one C2.4 built for poison
removal: per-record hashes. Without them you cannot locate the record, so you
cannot delete it.
""",
 "steps": [
  ("md", "## 2 · Demo — personal data arriving in a trace nobody reviewed"),
("md", "## 3 · Where it breaks — the erasure request"),
("md", "## 4 · The control — index the trace, and set retention per field"),
  *skill_steps('regulatory/trace-personal-data-audit',
               "## 2 · The procedure, as a skill\n\nFive items of personal data are in the agent trace and nobody put them there deliberately. The skill maps every system holding a copy and runs a real erasure request through all of them — three of which cannot delete one subject's records."),
],
 "expect": "Five items of personal data appear in the agent trace — name, email, "
           "account number and payment card — none placed there deliberately. The "
           "erasure request fails in three systems that cannot locate the record, "
           "two of which retain indefinitely. Building a subject index locates the "
           "affected steps, erasure leaves no personal data while retaining the "
           "hash, and per-field retention drops the sensitive field at 7 days.",
 "challenge": "Time-box this to an hour: can you delete one customer's data from "
              "your agent traces today? The answer usually arrives in ten minutes "
              "and is usually no — and the eval corpus is the system people forget "
              "entirely.",
},

"E2.6": {
 "concept": """
Incident and disclosure obligations meet agentic incidents badly, for one
specific reason: **broken attribution consumes the clock.**

The clock starts at *awareness* — when you know a reportable event may have
occurred. It does not pause while you work out who did it. So if your logs
attribute an agent's actions to the human whose credential it borrowed (D2.1),
the days you spend establishing what actually happened are deadline days.

Two consequences worth internalising:

1. **Containing fast does not buy reporting time.** You can contain in an hour
   and still miss a 72-hour deadline.
2. **You will have to disclose before attribution is complete.** So the sentence
   you send when you know an agent acted but cannot yet say which one needs to
   be drafted *now*, not during the incident.
""",
 "steps": [
  ("md", "## 2 · Demo — the clock, and what attribution costs it"),
("md", "## 3 · The control — fix attribution, and pre-draft the hard sentence"),
  *skill_steps('regulatory/disclosure-phase-breakdown',
               '## 2 · The procedure, as a skill\n\nContainment takes an hour and establishing who acted takes forty-eight, on a seventy-two hour clock. The skill breaks the deadline into phases, finds the dominant one, and re-runs it with delegation chains recorded.'),
],
 "expect": "One-hour containment still misses the 72-hour deadline when scoping is "
           "slow. The phase breakdown totals 92 hours, of which establishing who "
           "acted is 48 — two-thirds of the entire deadline. Recording act chains "
           "cuts the total to 44.5 hours and meets the deadline. The runbook check "
           "flags a shared owner, a late clock start and a missing pre-drafted "
           "disclosure.",
 "challenge": "Draft the disclosure sentence you would send when you know an "
              "agent acted but cannot say which one. Getting legal to agree that "
              "wording takes weeks in peacetime and is impossible at hour 60.",
},

"E2.7": {
 "concept": """
Documentation survives supervision when it points at machine-generated evidence
rather than restating intent.

The difference is not length or formality. It is whether each sentence names
three things:

- a **control** that operates,
- an **artefact** it produces,
- a **date** on which that artefact was last produced.

A sentence with all three can be checked. A sentence with none of them is a
statement of intent, and a supervisor's next question makes that visible
immediately.

Intent statements are not forbidden — some things genuinely are aspirations. The
failure is presenting them as controls. Label them, and the rest of the document
becomes more credible rather than less.
""",
 "steps": [
  ("md", "## 2 · Demo — the same policy paragraph, two ways"),
("md", "## 3 · Where it breaks — the follow-up question"),
  ("html", D.table(
    ["the follow-up question", "answerable from the document?"],
    [["“appropriate oversight” — show me the last time it operated.", "<b>no</b>"],
     ["“reviewed periodically” — what period, and when was the last one?", "<b>no</b>"],
     ["“comprehensive logging” — produce one action's full record.", "<b>no</b>"],
     ["“act chain for every action” — produce the August sample.", "yes"]],
    emphasise=1,
    caption="Three of four cannot be answered, and by the time the fourth is "
            "asked the person asking doubts that one too. Vague language does "
            "not fail on its own line; it fails the lines around it.")),
  ("md", "## 4 · The control — verify the document against live control state"),
  *skill_steps('regulatory/supervisory-documentation-score',
               '## 2 · The procedure, as a skill\n\nThe skill counts the sentences that name a control, an artefact and a date. The weak paragraph scores zero and reads perfectly well; the strong one scores three and answers the follow-ups a supervisor actually asks.'),
],
 "expect": "The weak paragraph has zero checkable sentences; the strong one has "
           "three, each naming a control, an artefact and a date. Three of four "
           "supervisor follow-ups are unanswerable from the weak version. "
           "Verifying the strong document against live control state finds SB-2 "
           "stale, so one of its claims is no longer true — which is only "
           "detectable because the document named a control.",
 "challenge": "Rewrite one paragraph of your AI policy in the strong shape. Any "
              "sentence that cannot name an artefact is intent — label it as "
              "such rather than deleting it, and the document gets more credible.",
},

"E2.8": {
 "concept": """
Auditability of autonomous action reduces to one question:

> For any single action, can you produce **who caused it** and **what they were
> allowed to do**?

Answering it needs two capabilities that must both be present at the moment the
action happens, because neither can be reconstructed afterwards:

- **Attribution** — the acting identity, the principal, and the chain between
  them (A2.5, EV-1).
- **Replay** — the prompts, the tool results, the pinned model version and the
  seed (D2.5).

Attribution without replay tells you who acted but not why. Replay without
attribution tells you what happened but not on whose authority. Regulators and
auditors ask both, usually in that order.
""",
 "steps": [
  ("md", "## 2 · Demo — the record, complete and incomplete"),
("md", "## 3 · Where it breaks — the two half-answers"),
("md", "## 4 · The control — the auditability test, run as a drill"),
  *skill_steps('regulatory/autonomous-action-auditability',
               '## 2 · The procedure, as a skill\n\nA record can name the acting identity, the principal, the chain and the scopes, be internally consistent, and be false. The skill scores three cases and adds the check that separates delegation from impersonation.'),
],
 "expect": "The complete record names the acting identity, principal, chain and "
           "scopes and is replayable, so it is answerable. Impersonation produces "
           "a complete, consistent and false record attributing the merge to the "
           "human. Missing replay fields break the other half. The drill reports 1 "
           "of 3 sampled actions fully answerable.",
 "challenge": "Run the drill on three real production actions from last week. The "
              "field you cannot fill is your auditability gap, stated precisely — "
              "and a number like \"1 of 3\" is far more useful to a supervisor than "
              "a paragraph about comprehensive logging.",
},

"E2.9": {
 "concept": """
Conversations with regulators and auditors go well when you bring the number
that is weakest and explain it, and badly when you bring the strongest and let
them find the other one.

That is not a moral point, it is a practical one. A supervisor who discovers a
weakness you did not disclose now doubts everything else you said, and the rest
of the engagement is spent re-establishing credibility you had at the start.

Three things to bring, in this order:

1. **The distinction you understand.** Conformance versus accuracy (B2.1).
   Volunteering it demonstrates you know what your own numbers mean.
2. **Your current coverage, honestly stated**, including stale and unevidenced
   controls (E1.7).
3. **The control you have not deployed, and the date you will.**

The third one is the one people omit, and it is the one that most reliably
converts scepticism into a working relationship.
""",
 "steps": [
  ("md", "## 2 · Demo — produce the two numbers, then the coverage"),
("md", "## 3 · Where it breaks — leading with the strongest number"),
  ("html", D.table(
    ["how you open", "what it is", "what happens next"],
    [["“Our harness scores 100%.”", "conformance quoted as quality",
      "<b>the follow-up “against what key?” ends the meeting's credibility</b>"],
     ["“We have full coverage of our AI controls.”",
      "stale and untested counted as passing",
      "<b>one request for dates exposes it</b>"],
     ["“Conformance is 100%; expert accuracy is 50% against a held-out key of "
      "20. Coverage is 63%, with SB-1 stale at 45 days and two controls not yet "
      "deployed.”", "both numbers, honestly",
      "nothing left for them to discover — the conversation moves to the plan"]],
    emphasise=2,
    caption="The third opening is the only one that survives a follow-up, and it "
            "is the one that sounds worst when you rehearse it.")),
  ("md", "## 4 · The control — the disclosure script, generated from live state"),
  *skill_steps('regulatory/assurance-conversation-prep',
               '## 2 · The procedure, as a skill\n\nConformance 1.0000, expert accuracy 0.5000, against a held-out key. The skill reports both to the same precision, splits control coverage into evidenced, stale and unevidenced, and rehearses the three openings that get used.'),
],
 "expect": "Conformance is 1.0000 while expert accuracy is 0.5000 on a 20-question "
           "held-out key. Coverage is 5 of 8 with SB-1 stale and DR-1 and ST-1 "
           "unevidenced. The three openings show conformance-as-quality and "
           "inflated coverage failing on the first follow-up, and the generated "
           "disclosure script states both numbers, the stale and missing "
           "controls, and a date for each.",
 "challenge": "Generate this script from your own live control state rather than "
              "writing it. If it cannot be generated, your coverage number is "
              "being assembled by hand for each meeting — which is why it differs "
              "between meetings.",
},
}
