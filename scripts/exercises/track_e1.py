"""E1 — The GRC Practitioner (Risk & Control). Nine sessions.

The governing insight for the whole E function: **point-in-time control testing
fails for AI**, because the thing you tested is not the thing running next week
and none of the changes that break it are code changes.

    E1.1  why point-in-time testing fails
    E1.2  the inventory — you cannot govern what you cannot list
    E1.3  risk tiering by authority and data, not by model
    E1.4  control mapping (control → framework, never the reverse)
    E1.5  evaluation output as audit evidence
    E1.6  operating vs outcome guardrails
    E1.7  continuous control verification
    E1.8  third-party and model supply chain
    E1.9  model and agent lifecycle governance
"""

from .skills import SKILL_RUNTIME, runtime_step

from . import diagrams as D

RUNTIME_STEP = runtime_step()

EXERCISES: dict[str, dict] = {

"E1.1": {
 "concept": """
Classical control testing has a simple shape: a control is designed, an auditor
tests it once or twice a year, and a passing test is recorded for the period.

That works when the thing being tested changes only through a process that
generates evidence. For an agent, the four things that change its behaviour are:

- the **model version** — changed by your provider, possibly without notice,
- the **prompt** — edited in a console,
- the **tool manifest** — a config change,
- the **approval settings** — a toggle in an admin UI.

None of them is a code change. None generates a change record. All of them
invalidate the conditions the control was tested under.

The honest consequence is that a control tested six months ago is not passing —
it is **unevidenced**, which is a third state most GRC tooling cannot represent.
Introducing that third state is the whole of this lesson.
""",
 "steps": [
  ("md", "## 2 · Demo — the same evidence, two ways of reading it"),
("md", "## 3 · Where it breaks — the two numbers those readings produce"),
("md", "## 4 · The control — a freshness window per control, derived from drift\n\n"
         "The window is not an audit-calendar choice. It comes from **how fast "
         "the thing the control tests actually changes.**"),

  ("md", "## 5 · What replaces the annual test, as a skill\n\n"
         "If the window is short, something has to re-run inside it, and that "
         "something is an attestation: collect each control's verdict, resolve "
         "every evidence pointer, compute drift against the image digest and the "
         "tool manifest, and sign the result. Two rules in the procedure are the "
         "whole difference between an attestation and a slide — a missing "
         "verdict is not a pass, and a capped verdict does not get raised "
         "because the other evidence looked good. This is the file in this "
         "repository:"),
  ("skill", "attestation/attestation-signer-lifecycle"),
],
 "expect": "The skill loads and reports its shape, and its failure modes are the "
           "governance lesson stated as engineering: the relying party must fail "
           "closed on a missing attestation, because reading absence as a pass "
           "is exactly the annual-test habit arriving in a new format. Drift "
           "against the digest and the manifest is what re-triggers it, not the "
           "calendar.",
 "challenge": "Pick your three most important AI controls and set a freshness "
              "window for each from the observed change rate of what it tests. "
              "Then recompute your posture. The number will drop, and it will be "
              "the first honest one you have had.",
},

"E1.2": {
 "concept": """
You cannot govern, tier, test or revoke what you cannot list. The AI inventory is
therefore the first control, not a documentation exercise.

The honest finding of every first inventory is the same: **most of it was already
in production.** Not because anyone was reckless, but because AI features arrive
inside products you already bought, and agents get created programmatically by
other agents.

Three sources, and the third finds what the first two miss:

1. the **model registry** — what your ML team registered,
2. **procurement and expense** — what someone bought,
3. **egress logs to model-provider domains** — what is actually being used.

Source 3 is the one that discovers the department using a frontier API on a
personal card, and the SaaS product that quietly added an AI feature.
""",
 "steps": [
  ("md", "## 2 · Demo — build the inventory from three sources"),
("md", "## 3 · Where it breaks — the gap distribution is always like this"),
("md", "## 4 · The control — a discovery query you can re-run"),

  ("md", "## 5 · Resolving one row into a deployment, as a skill\n\n"
         "Discovery finds that a thing exists. Governing it needs the row "
         "resolved into artefacts: which repository at which commit, which image "
         "**digest** rather than which tag, which IAM role and SPIFFE ID, which "
         "gateway and guardrail, and every downstream its tools call. Every "
         "other attestation skill consumes this graph, which is why it runs "
         "first. This is the file in this repository:"),
  ("skill", "attestation/deployment-inventory-resolver"),
],
 "expect": "The skill loads and reports its shape. Two of its rules are what "
           "make an inventory hold: resolve digests rather than tags, because a "
           "tag is mutable and the thing you attested is not the thing running; "
           "and never record an unresolvable artefact as absent — \"no gateway "
           "configured\" and \"could not read the gateway\" are different "
           "findings with different owners.",
 "challenge": "Run the egress query for real: one week of traffic to model-"
              "provider domains, joined against your inventory. It takes an hour "
              "and it always finds something.",
},

"E1.3": {
 "concept": """
Risk-tier by what the system **can do**, not by which model it uses.

Tiering on model capability is the common mistake and it tracks vendor marketing
rather than exposure: every GPT-class deployment becomes "high" and every small
model "low". That gets the answer exactly backwards for the case that matters —
a small local model with production deploy rights and regulated data.

Three inputs determine consequence, and none of them is the model:

- **Autonomy** — what its output can trigger without a human.
- **Data** — what it can read, especially regulated or customer data.
- **Reach** — whether it can act externally.

The model matters for *likelihood* of a bad output, which is a different and
smaller term than consequence.
""",
 "steps": [
  ("md", "## 2 · Demo — tier by authority and data"),
("md", "## 3 · Where it breaks — tier by model instead, and compare"),
("md", "## 4 · The control — the four questions the questionnaire should ask"),
],
 "expect": "The public read-only chatbot tiers low; the small local model with "
           "deploy rights and regulated data tiers critical at score 12. Tiering "
           "by model disagrees on 4 of 5 assets, most sharply inverting the small "
           "local model from low to critical. The worked example tiers the refund "
           "agent as high.",
 "challenge": "Re-tier your top ten AI use cases using only the four questions. "
              "Note which ones move, and be ready to explain the movement to "
              "whoever wrote the original questionnaire — the model question is "
              "usually question one.",
},

"E1.4": {
 "concept": """
Control mapping runs one way: **control → framework.**

Starting from the framework produces a checklist that is complete, satisfies an
assessor, and defends nothing — because it enumerates clauses rather than
capabilities, and a clause with no operating control behind it evidences nothing.

Starting from controls produces the opposite: a smaller list of things you
actually do, each of which happens to satisfy several framework clauses. The
framework coverage is an **output**, and that is the only mapping that survives a
supervisor asking "show me".
""",
 "steps": [
  ("md", "## 2 · Demo — the control catalogue, and what it satisfies"),
("md", "## 3 · Where it breaks — start from the framework instead"),
("md", "## 4 · The control — evidence flows from the control, not the clause"),
],
 "expect": "The catalogue's 8 controls map to framework clauses across NIST AI "
           "RMF, ISO 42001, ISO 27001, the EU AI Act and DORA. Critical tier "
           "requires all 8 and satisfies 12 clauses; medium requires 5. Working "
           "framework-first leaves 3 of 7 clauses with no operating control. The "
           "evidence pack shows one artefact satisfying several clauses.",
 "challenge": "Take one framework clause your programme claims to satisfy and ask "
              "which operating control produces its evidence. If the answer is a "
              "policy document, the clause is ticked and undefended.",
},

"E1.5": {
 "concept": """
Evaluation output is the strongest audit evidence an AI programme can produce,
and it only works if you present the right number.

B2.1 established the distinction; this lesson turns it into evidence:

- **Conformance** — schema validity. ~100% by construction. A build-health
  signal, not a quality claim.
- **Expert accuracy** — correctness against a held-out key. The number that
  evidences anything.

Four properties make an eval result auditable:

1. the key was **held out** — the harness never saw it,
2. the number reported is **accuracy**, not conformance,
3. the **sample size** is stated,
4. it **expires**, so it cannot silently age into a claim.

Miss the fourth and you have produced a number that will be quoted three years
from now about a system that has since had six model upgrades.
""",
 "steps": [
  ("md", "## 2 · Demo — produce the evidence"),
("md", "## 3 · Where it breaks — the number that gets quoted"),
  ("html", D.table(
    ["the claim, as written", "what it measures", "defensible?"],
    [["Our AI security harness scores 100%.", "conformance", "<b>no</b>"],
     ["Our harness achieves 100% schema conformance.", "conformance", "yes"],
     ["Our harness scores 0.81 expert accuracy on a 24-question held-out set.",
      "accuracy", "yes"],
     ["Our harness passes all automated checks.", "unspecified", "<b>no</b>"]],
    emphasise=2,
    caption="The first is true and misleading — conformance really is 100%. The "
            "last is the most common of the four and evidences nothing at all.")),
  ("md", "## 4 · The control — evidence with an expiry"),

  ("md", "## 6 · The evidence pack, as a skill\n\n"
         "An evaluation result becomes evidence only when it tested the control "
         "that is claimed, ran on the system that is **deployed**, and states "
         "its failure mode. Most evidence fails the second.\n\n"
         "The contract carries a field most packs would rather not have: "
         "`conformance_reported`. Setting it true should be read as a defect in "
         "the evidence, not a feature of it."),
  ("skill", "grc/control-evidence"),


  ("md", "## 7 · Where it breaks — the pack that leads with conformance\n\n"
         "The most common overstatement in automated assurance, and it is "
         "usually made in good faith."),
],
 "expect": "Conformance is 1.0000 while expert accuracy lands around 0.81 on 24 "
           "held-out questions. Two of four sample claims are defensible. The EV-2 "
           "control test passes against a stated 0.80 threshold, is valid for 30 "
           "days, and reads STALE at 45 days. All five auditability checks pass.",
 "challenge": "Find an eval number your organisation has quoted, internally or "
              "externally, and determine which of the two it was. Then check "
              "whether it has an expiry. Most do not, and are still being cited.",
},

"E1.6": {
 "concept": """
Guardrails come in two kinds, and confusing them is how a programme passes audit
while missing harm.

**Operating guardrails** constrain *how the system runs*: all egress through the
gateway, privileged tools gated below L3, every action logged. They are testable
today, cheap to verify, and produce clean evidence.

**Outcome guardrails** constrain *what results are acceptable*: no unrecoverable
customer data loss, no increase in customer-facing incidents, no disparate
outcomes across segments. They matter more and most need a measurement you do
not yet have.

The failure is not choosing one. It is shipping only the first column, reporting
it as coverage, and never labelling the second column as unmeasured.
""",
 "steps": [
  ("md", "## 2 · Demo — classify a real guardrail set"),
("md", "## 3 · Where it breaks — the coverage number that lies"),
("md", "## 4 · The control — define the measurement, or label it unmeasured"),
],
 "expect": "Four operating guardrails are all enforceable today; three outcome "
           "guardrails are enforceable only where a measurement exists. Counting "
           "only what shipped gives 100% coverage; counting all agreed guardrails "
           "gives 71%. One outcome guardrail is fully specified and enforceable; "
           "the other is labelled an aspiration and excluded from coverage.",
 "challenge": "Pick one outcome guardrail your programme has agreed and specify "
              "its metric, threshold, source and cadence precisely enough that "
              "someone could dispute the result. If you cannot, say so in the "
              "coverage report rather than counting it.",
},

"E1.7": {
 "concept": """
Continuous control verification is the operating model that follows from E1.1.

The number that matters is not how much passed once. It is **how much is
currently evidenced** — controls whose most recent test is passing *and* within
its freshness window.

Three states, and the third is the one classical GRC tooling cannot express:

- **PASS** — tested, passing, in window.
- **FAIL** — tested, failing. Honest and actionable.
- **STALE** — tested, was passing, out of window. **Not a pass.**

Plus the absence state: no evidence at all, which is different from failing and
is often the largest category in a first assessment.
""",
 "steps": [
  ("md", "## 2 · Demo — the posture, computed honestly"),
("md", "## 3 · Where it breaks — what a point-in-time report would have said"),
("md", "## 4 · The control — automate one test and watch the posture hold"),

  ("md", "## 5 · Collecting the runtime evidence, as a skill\n\n"
         "Automating a control means something has to go and look. For the "
         "network and logging controls that underwrite every default-deny claim "
         "CyberTravels makes, that is a posture collector: egress rules, private "
         "endpoints, route tables, key policies, and whether the audit trail is "
         "not merely enabled but **delivering**. It collects; it does not "
         "conclude. This is the file in this repository:"),
  ("skill", "attestation/aws-runtime-posture-collector"),
],
 "expect": "The skill loads and reports its shape, and the line to take from it "
           "is the boundary it draws: configuration is not enforcement. A "
           "private endpoint next to a route table with a NAT gateway is a "
           "recorded fact and an open path at the same time, and logging that is "
           "switched on but not delivering evidences nothing at all.",
 "challenge": "Automate the control with the shortest freshness window first — it "
              "is the one costing the most manual effort and going stale most "
              "often. One automated test converts an annual assertion into a live "
              "control.",
},

"E1.8": {
 "concept": """
Third-party risk for AI has the ordinary supply-chain problem plus a question
nobody's assessment form asks:

> **Can this component change without telling us?**

For a library the answer is no — you pin a version. For a hosted model the
answer is usually yes, and it changes the risk rating, because every control you
tested was tested against behaviour the vendor can replace on a Tuesday.

Three artefact classes, with genuinely different maturity:

- **Libraries** — signing, version pinning, download signals. Mature.
- **Model weights or a hosted model** — attestation possible and rare; no
  popularity signal that means anything; version stability is a contractual
  question, not a technical one.
- **Prompt and tool packages (MCP, skills)** — no signing convention, and they
  run with your agent's authority.

Saying which signals are unavailable is part of the assessment, not a gap in it.
""",
 "steps": [
  ("md", "## 2 · Demo — the ordinary signals, and where they run out"),
("md", "## 3 · Where it breaks — the silent change, priced"),
("md", "## 4 · The control — the four questions, and stating the gaps"),
],
 "expect": "The hosted model and the MCP tool package both tier high — one for "
           "silent change, one for running with agent authority. The silent model "
           "change invalidates all three control tests taken before it. The signal "
           "table shows libraries with 4 of 4 signals available and hosted models "
           "with 0 of 4, and each assessment statement names what was unavailable.",
 "challenge": "Add \"can this change without notifying us?\" to your third-party "
              "assessment form. For hosted models the answer is usually yes, and "
              "it should carry an explicit control-test expiry.",
},

"E1.9": {
 "concept": """
Lifecycle governance is about the events that have no ticket.

A model or agent has a lifecycle — requested, approved, deployed, changed,
retired. Classical governance covers the first, second and third. The events that
actually change your risk are the fourth and fifth, and they mostly happen
outside any process:

| Event | Ticketed? | Why it matters |
|---|---|---|
| new agent deployed | usually | caught by existing process |
| tool added to manifest | no | changes blast radius silently |
| prompt edited | no | changes behaviour, not code |
| provider upgrades the model | no | you may not be told |
| scope widened in IAM | sometimes | depends on your IAM review |
| **agent decommissioned** | rarely | **the identity outlives the agent** |

The last row is the one most first reviews find: a retired agent whose identity
still exists is a standing credential with no owner and nobody watching it,
because everyone believes it is gone.
""",
 "steps": [
  ("md", "## 2 · Demo — the lifecycle, and which events generate a record"),
  ("html", D.table(
    ["lifecycle event", "does it raise a ticket?", "why it matters"],
    [["new agent deployed", "usually", "the existing change process catches it"],
     ["tool added to the manifest", "<b>no</b>",
      "changes blast radius, and no pull request is raised"],
     ["prompt edited in a console", "<b>no</b>",
      "changes behaviour, not code"],
     ["provider upgrades the model", "<b>no</b>",
      "you may not be told at all"],
     ["scope widened in IAM", "sometimes",
      "depends entirely on your access-review cadence"],
     ["agent decommissioned", "<b>rarely</b>",
      "the identity usually outlives the agent"]],
    emphasise=1,
    caption="Four of six generate no reliable record. A lifecycle you cannot "
            "observe is a lifecycle you are not governing.")),
  ("md", "## 3 · Where it breaks — the identity that outlived the agent"),
("md", "## 4 · The control — two automated checks that close the loop"),
],
 "expect": "Four of six lifecycle events generate no reliable record at all. The identity "
           "review flags `sunset-agent` as critical — an active credential for a "
           "decommissioned service — plus two orphans with no authentication in "
           "300+ days. The manifest diff shows the blast radius rising from 0 to "
           "40, requiring re-tiering and a fresh control test.",
 "challenge": "Query your identity provider for non-human identities whose "
              "service is retired but which authenticated in the last 30 days. "
              "Every hit is either an undocumented dependency or someone else's "
              "foothold, and you cannot tell which from the directory alone.",
},

"E1.10": {
 "concept": """
Five functions hold the AI control estate between them, and **none of them holds
all of it.** The programme does not fail inside any one function. It fails at the
seams, where each side reasonably believed the other had it.

| Stakeholder | The question they are actually asking |
|---|---|
| **Legal** | Can we be held liable, and under what theory? |
| **Compliance** | Which obligations apply, and can we demonstrate we meet them? |
| **Data Privacy** | Whose data is in this, on what basis, and for how long? |
| **Cyber Security** | Can this be attacked, and can we contain it if it is? |
| **Model Risk** | Is this fit for its stated purpose, and will we know when it stops being so? |

Two seats are routinely forgotten. The **business or product owner** in the
first line, who defines intended purpose and risk appetite and funds
remediation — if that seat is empty, the other five are governing an orphan. And
**internal audit** in the third line, whose job is independent assurance that the
five are doing what they claim.

What makes this a lesson rather than an org chart is the four gaps below. Each
one is a real failure that happens because *both* sides made a reasonable
assumption about the other.
""",
 "steps": [
  ("md", "## 2 · Who operates which control"),
  ("html", D.table(
    ["function", "the question it is asking", "the controls it holds"],
    [["legal", "can we be held liable, and under what theory",
      "contract clauses · acceptable-use terms · IP screening · e-discovery retention"],
     ["compliance", "which obligations apply, can we demonstrate we meet them",
      "AI policy · use-case classification · attestations · disclosure triggers"],
     ["privacy", "whose data, on what basis, for how long",
      "impact-assessment gate · PII redaction · retention schedules · transfers"],
     ["cyber", "can this be attacked, can we contain it",
      "agent identity and JIT authz · tool permissions · sandbox and egress · "
      "guardrails · telemetry · kill switch"],
     ["model risk", "is it fit for purpose, will we know when it stops being",
      "pre-deployment validation · thresholds · drift alerting · revalidation"]],
    caption="Plus two more that hold no controls and decide everything: the "
            "business owner, accountable for the use case and its risk appetite, "
            "and internal audit, independently assuring that the five above do "
            "what they claim. 22 controls across five functions, and no function "
            "holds more than a quarter of them.")),

  ("md", "## 3 · The four seams, each with two reasonable assumptions"),
  ("html", D.table(
    ["the seam", "one side assumed…", "the other assumed…", "what happened"],
    [["agent traces are full of personal data",
      "<i>cyber:</i> privacy owns retention of anything containing personal data",
      "<i>privacy:</i> security owns the log store, so security sets its schedule",
      "<b>no schedule was set; three years of prompts are discoverable</b>"],
     ["the model was validated, the tools were not",
      "<i>model risk:</i> validation covered the model, which is our scope",
      "<i>cyber:</i> MRM signed it off, so the deployment was approved",
      "<b>an agent holds production write access that was never in scope</b>"],
     ["“no training on our data” was negotiated, never instrumented",
      "<i>legal:</i> the clause is in the contract and it is binding",
      "<i>cyber:</i> legal handled the vendor, so the restriction is handled",
      "<b>nobody built the control that verifies the vendor honours it</b>"],
     ["the use case was risk-tiered before it had tools",
      "<i>compliance:</i> classified low-risk — it was a chatbot when we saw it",
      "<i>business owner:</i> we shipped features, not a new use case",
      "<b>it files tickets, sends mail and moves money at the low-risk tier</b>"]],
    emphasise=3,
    caption="Neither assumption in any pair is unreasonable. That is what makes "
            "these seams rather than mistakes — and why naming the handoff is "
            "the control.")),

  ("md", "## 4 · Where it breaks — every function reports green"),

  ("md", "## 5 · The control — name the handoff, give it one owner"),

  ("md", "## 6 · Verify — the two forgotten seats"),
],
 "expect": "Five control functions, the question each is asking and the "
           "controls each operates — 22 in total. Four seam failures laid out as "
           "pairs of individually reasonable assumptions, "
           "and every function still self-reports green while all four gaps are "
           "open. Naming one accountable owner per handoff closes them, and a "
           "use case with all five control functions and no business owner is "
           "shown to be ungoverned.",
 "challenge": "Pick one of the four seams and find out, today, who owns it in "
              "your organisation. The answer 'I assume security does' from one "
              "side and 'I assume privacy does' from the other is the finding.",
},

"E1.11": {
 "concept": """
Model risk management is not new. The SR 11-7 lineage has governed models in
regulated institutions for over a decade, and its three pillars are sound:

1. **Conceptual soundness** — is the method appropriate for the purpose?
2. **Ongoing monitoring** — is it still performing as validated?
3. **Independent validation** — did someone other than the builder check?

All three still hold for AI systems. What breaks is not the framework but a
silent assumption underneath it: **that a model produces an output, and a human
decides what to do with it.**

Once the model can call a tool, that assumption is void. Validation scoped to
the model's *predictions* says nothing about the model's *actions*. You can hold
a perfectly valid validation report for a system that has since been granted
write access to a production database, and nothing in the classical process is
required to notice.

So the extension is narrow and specific: the unit of validation becomes the
**model plus its tool surface plus its autonomy level**, and any change to any of
the three triggers revalidation — not just a change to the weights.
""",
 "steps": [
  ("md", "## 2 · The three pillars, and what each assumes"),

  ("md", "## 3 · The unit of validation, before and after tools"),

  ("md", "## 4 · Where it breaks — monitoring the wrong thing well"),

  ("md", "## 5 · The control — revalidate on the triple, not on the weights"),

  ("md", "## 6 · Verify — what a validation record must now carry"),
],
 "expect": "The three SR 11-7 pillars, each with the assumption it quietly makes. A "
           "system validated with no tools at L1 is shown deployed with three "
           "tools at L3 — same model, same version — and the validation no "
           "longer covers it. Monitoring reports 200 clean runs of summarisation "
           "accuracy while four action-level metrics have no threshold at all, "
           "and four revalidation triggers classical MRM would miss are named.",
 "challenge": "Take one validated model in your estate and list the tools it "
              "holds today. If any of them post-dates the validation report, "
              "the report is describing a different system.",
},

"E1.12": {
 "concept": """
Everything in this chapter has pointed at the same conclusion: the functions
work, and the **handoffs** are where the programme leaks.

A seam is not a disagreement. Both sides are usually competent, usually right
about their own scope, and usually assuming the other side has the piece in the
middle. Nobody is wrong, and the gap is real.

The control is a **joint runbook** per seam, and it has exactly three
properties:

- **One artefact.** A named, versioned thing that exists — not a meeting, not an
  understanding.
- **One owner.** Accountable for the artefact existing and being current.
  Contributors are named; owners are singular.
- **Named consumers.** Who receives it, and what they are entitled to assume
  once they have. A handoff nobody consumes was never a handoff.

The three seams below are the ones that fail most often, and each is traced
here from producer to consumer to see exactly where it stops.
""",
 "steps": [
  ("md", "## 2 · Three seams, traced end to end"),

  ("md", "## 3 · Where it breaks — the consumer who never received it"),

  ("md", "## 4 · What each undelivered handoff actually costs"),

  ("md", "## 5 · The control — deliver, and record the delivery"),

  ("md", "## 6 · Verify — one artefact, many consumers, one owner"),
],
 "expect": "Three joint runbooks are traced from owner to consumer, and three "
           "handoffs turn out never to have been delivered — model risk never "
           "receives the privacy assessment, and neither security nor internal "
           "audit receives the validation report. Each undelivered handoff is a "
           "control that was built, works, and is invisible to the function "
           "whose decision depends on it. A four-property check runs over the "
           "seams and goes from several problems to zero.",
 "challenge": "Pick the artefact your function produces for someone else and ask "
              "the recipient when they last received it. The gap between 'we "
              "produce that' and 'we receive that' is the seam, and it is "
              "usually measured in quarters.",
},
}
