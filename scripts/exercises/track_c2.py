"""C2 — The Security Researcher. Seven sessions.

    C2.1  what research means in a CISO org (it ends in a control, not a paper)
    C2.2  model-layer research: rates, not anecdotes
    C2.3  weight-level access, and what the defender loses with it
    C2.4  data-layer research: provenance beats volume
    C2.5  supply-chain research, including the two artefacts with no process
    C2.6  benchmarks, reproducibility, and the harness that separates the two
          effects — model and scaffolding — that everyone confounds
    C2.7  from finding to control, and to something that still holds without you
"""

from . import diagrams as D

EXERCISES: dict[str, dict] = {

"C2.1": {
 "concept": """
Research inside a CISO org is not publication. It is the function that converts
**uncertainty into controls other people can operate**, and it is judged on how
much of that conversion actually happens.

That gives it a specific shape. A finding is not finished when it is
interesting; it is finished when it has become one of four things:

- a **preventive control** that makes the problem structurally impossible,
- a **detection** that fires when the precondition recurs,
- an **eval case** that fails if the fix regresses,
- or a **written accepted risk**, with an owner and a review date.

The fourth is a legitimate outcome and is usually missing from the list, which
is why research backlogs fill with findings nobody will ever action.

The artefact that makes any of this possible is a **repro card**: a claim, the
exact conditions it holds under, and the observed rate. Without conditions, a
finding is folklore.
""",
 "steps": [
  ("md", "## 2 · Demo — the repro card"),
("md", "## 3 · Where it breaks — the finding that never becomes anything\n\n"
         "A good repro card is necessary and not sufficient. Here is a backlog of "
         "real-shaped findings, and what happened to each."),
("md", "## 4 · The control — a finding is closed when it has become something"),
],
 "expect": "The folklore card is reported as not actionable with three gaps; the "
           "research card passes. The backlog scores 50% programme durability, "
           "with three findings landing as controls or detections and three "
           "effectively lost. The closure check accepts a finding with a control "
           "and one with a written accepted risk, and rejects the one that only "
           "has notes.",
 "challenge": "Score your own last ten findings on the durability table. Anything "
              "that landed below a repro card is work you will pay for twice — "
              "and an accepted risk with an owner scores higher than an open "
              "ticket nobody is working.",
},

"C2.2": {
 "concept": """
Model-layer research means treating the model as an object of study rather than
a demo subject. The discipline is one rule: **report rates, not anecdotes.**

"I got it to do X" is not a result. Language models are stochastic; with enough
attempts you can get almost anything once. The result is the *rate*, with an
interval, because the rate is what changes when a mitigation lands and the
interval is what tells you whether the change was real.

This matters practically. A mitigation that moves a technique from 62% to 48%
sounds like progress. With n=20 the confidence intervals overlap so heavily that
you have demonstrated nothing, and you are about to tell a board you reduced
risk by 23%.
""",
 "steps": [
  ("md", "## 2 · Demo — three techniques, measured properly"),
("md", "## 3 · Where it breaks — the underpowered before/after"),
("md", "## 4 · The control — compute the sample size before you run\n\n"
         "The question is not \"how many attempts should I do?\" It is: **how "
         "small an effect do I need to be able to detect?**"),
],
 "expect": "Direct override is not reproduced, context reframe is flaky, task "
           "nesting is reproducible. The before/after comparison shows overlapping "
           "intervals at n=20 and n=100 and separation at n=1000, for an identical "
           "true effect. Sample-size calculation shows detecting 62%→48% needs "
           "roughly 200 trials while 62%→58% needs thousands.",
 "challenge": "Take the last jailbreak or injection result your team reported. "
              "Ask for n. If the answer is a single-digit number or 'we tried it "
              "a few times', the finding is real but the number attached to it is "
              "not.",
},

"C2.3": {
 "concept": """
Open weights are what make this curriculum possible: you can study a model
properly without a frontier-lab account. That is the whole premise of a commons.

The defensive point of this lesson is the other half of that trade. When a model
runs locally under your control, **every provider-side safety control
disappears** — and those controls were doing real work:

| Control | Who provides it | Present locally? |
|---|---|---|
| rate limiting | provider | no |
| abuse monitoring | provider | no |
| refusal training | provider | yes, but removable by fine-tuning |
| logging you cannot delete | provider | no |
| model version stability | provider | you now own it |

An attacker with open weights gets unlimited probing, no rate limit, no abuse
signal reaching anyone, and the ability to fine-tune refusals away cheaply.

That is not an argument against open weights. It is an argument that **your
control plane has to supply what the provider used to** — which is what every
other track in this curriculum has been building.
""",
 "steps": [
  ("md", "## 2 · Demo — what changes with access level"),
  ("html", D.table(
    ["capability", "hosted API", "open weights, running locally"],
    [["unlimited probing", "no", "<b>yes</b>"],
     ["no abuse signal reaches the provider", "no", "<b>yes</b>"],
     ["can remove refusals", "no", "<b>yes</b>"],
     ["controls its own version", "no", "<b>yes</b>"],
     ["activation-level access", "no", "<b>yes</b>"]],
    emphasise=2,
    caption="An attacker gains all five. A defender gains exactly the same five "
            "— which is the whole argument for a commons built on open weights, "
            "and the reason the asymmetry people expect here does not exist.")),
  ("md", "## 3 · Where it breaks — measure the probing asymmetry"),
("md", "## 4 · The control — replace what the provider was doing\n\n"
         "Map each lost control to the thing in your own stack that has to supply "
         "it. Every row points at a lesson you have already done."),
],
 "expect": "Local weights grant five capabilities the hosted API does not. The "
           "probing comparison shows roughly 24,000 hosted attempts against 5.5 "
           "million local ones in 24 hours — a 230× ratio — turning a 0.5% "
           "technique into tens of thousands of successes. Each lost provider "
           "control maps to a lesson in this curriculum, and gating the shell "
           "reduces the local agent's blast radius from 19 to 3.",
 "challenge": "List the controls you currently rely on that are actually your "
              "model provider's. For each, name your replacement if the model "
              "moved on-prem next quarter. Most teams find rate limiting and "
              "abuse monitoring have no owner at all.",
},

"C2.4": {
 "concept": """
Data-layer research has one governing result: **provenance beats volume.**

Published data-poisoning attacks succeed at contamination rates well under 1%,
and some at a few hundred documents regardless of corpus size. That breaks the
intuition most teams operate on — "we have a lot of clean data, a few bad
records will be drowned out". They will not.

If volume does not protect you, the only thing that does is knowing **exactly
what is in the corpus**: per-record hashes, a signed manifest, and the ability to
answer "which records changed since the snapshot we signed off?"

That capability also happens to be what a privacy erasure request needs, which
is why E2.5 depends on this lesson.
""",
 "steps": [
  ("md", "## 2 · Demo — how little poison is needed"),
("md", "## 3 · Where it breaks — a corpus you cannot describe\n\n"
         "The practical failure is not that poisoning is undetectable. It is that "
         "most teams cannot answer basic questions about the corpus that trained "
         "the model currently in production."),
("md", "## 4 · The control — a hashed, signed manifest"),
],
 "expect": "Poison rates of 0.01%, 0.1% and 1% print for a 100,000-record corpus. "
           "The capability table shows only hashed manifests can answer the four "
           "questions. The manifest root changes when three records are appended "
           "and the three new records are identified by hash, including the "
           "injected one, which is then located and removed exactly.",
 "challenge": "For one dataset feeding a production model, try to produce the "
               "hash of the exact snapshot that trained the deployed version. "
               "Time-box it to an hour. The answer usually arrives in ten minutes "
               "and is usually no.",
},

"C2.5": {
 "concept": """
Supply-chain research for AI systems is the ordinary software problem plus two
artefacts that have no mature process at all.

The ordinary part transfers directly: typosquatting, unsigned packages, new
packages with no soak time. The signals that predict a bad dependency have not
changed.

The two new artefacts:

- **Model weights.** Sigstore and in-toto attestation are technically possible
  and rare in practice. There is no download-count equivalent — "popular
  checkpoint" is not provenance, and a fine-tune of a fine-tune has a lineage
  nobody records.
- **Prompt and tool packages.** MCP servers, agent skill bundles, prompt
  libraries. These run *inside* your agent with your agent's authority, and
  there is no signing convention for them at all.

The honest output of this lesson includes stating where no answer currently
exists, because a risk assessment that invents one is worse than a gap.
""",
 "steps": [
  ("md", "## 2 · Demo — the ordinary signals still work"),
("md", "## 3 · Where it breaks — the two artefacts with no process"),
("md", "## 4 · The control — state the gap rather than inventing a number"),
],
 "expect": "The two legitimate packages are allowed or reviewed; both typosquats "
           "are blocked with the distance and the package they imitate. The MCP "
           "connector trips three ordinary signals and is escalated to block once "
           "agent authority is weighted in. The final assessments state explicitly "
           "which signals are unavailable for model weights and tool packages.",
 "challenge": "Add one question to your third-party assessment: \"does this "
              "artefact execute with our agent's authority?\" Anything answering "
              "yes should not be assessed on the same scale as a library.",
},

"C2.6": {
 "concept": """
The difference between a person who finds things and a capability that keeps
finding them is a harness: a suite, a target adapter, and recorded rates that
are comparable across runs.

Three properties make it a harness rather than a script:

1. **The suite is data, not code.** Adding a case must not require editing the
   runner.
2. **The target is an adapter.** Pointing it at a new build, a new model or a
   competitor's product should be one function.
3. **Results are comparable.** Same seed, same n, same scoring — so a delta
   means something.

The failure mode to avoid is a harness that only ever produces a number going
down, because the suite is only ever extended with cases the current build
already passes.

The same three properties are what let you **critique somebody else's
benchmark**, which is the other half of this job. Three questions decide whether
a published security number means anything, and all three are answerable from
the benchmark's own data:

1. **What is the class balance?** If one class dominates, a constant answer
   scores well. Report lift over the majority baseline, never the raw number.
2. **Is the key held out?** If the harness has seen the answers — through
   training, through prompt examples, through its own logs — the number is a
   training metric.
3. **How are files matched?** Bare-basename matching on a corpus that reuses
   filenames turns accuracy into a partly random variable.
""",
 "steps": [
  ("md", "## 2 · Demo — suite as data, target as adapter"),
("md", "## 3 · The comparison a harness exists to produce"),
("md", "## 4 · Where it breaks — a suite that only ever grows easier\n\n"
         "The metric that makes a research programme look productive while "
         "measuring nothing: add cases the current build already passes, and the "
         "aggregate ASR falls every quarter."),

  ("md", "## 6 · The same discipline, pointed at somebody else's benchmark\\n\\n"
         "Dilution is one way a number lies. Three more are structural, and all "
         "three are checkable from the benchmark's own key: class balance, "
         "whether the key was held out, and how answers are matched to files."),
],
 "expect": "The baseline suite reports per-case rates with intervals. Provenance "
           "reduces every injection case to about 0.02 with non-overlapping "
           "intervals, while identity and containment are unchanged. Adding 12 "
           "trivially-blocked cases cuts aggregate ASR by roughly 60% with no "
           "change to the build, and the suite-health check flags that suite as "
           "diluted. On the critique side: a skewed key gives a 0.875 floor before "
           "anyone answers anything, a leaked key scores a perfect 1.000, and "
           "answers naming the wrong directory score 1.000 under basename matching "
           "against 0.250 under path matching.",
 "challenge": "Check your own security regression suite for dilution — what "
              "fraction of its cases have ever failed? Under 30% and the aggregate "
              "number is mostly measuring how many easy cases you added. Then take "
              "the last benchmark someone quoted at you and find its majority "
              "baseline. Most published numbers are never reported against one.",
},

"C2.7": {
 "concept": """
A finding becomes institutional capital only when it ships as something. C2.1
listed the four endings; this lesson builds all four for one finding, so the
handover is code rather than a promise.

The clause that makes it real is the **proof of fix**: an eval case that fails
on the old build and passes on the new one. Without it you have a claim that
something was fixed, and claims regress silently.

The order also matters. Build the eval case *first*, before the control, because
a test written after the fix tends to test the fix rather than the property.

That is also the whole answer to "what is a research function worth". The test
of a programme is not what it discovered; it is **what still protects you after
the person who discovered it has left**. Findings land in artefacts of very
different durability, and only the bottom two rows here are institutional
capital:

| Landed as | Survives staff turnover? | Survives a refactor? |
|---|---|---|
| a chat thread | no | no |
| a slide deck | technically | no |
| a repro card | yes | no |
| a regression case in CI | yes | **yes — it fails the build** |
| a control + its eval case | yes | yes |
""",
 "steps": [
  ("md", "## 2 · The finding, and the four artefacts it must become"),
("md", "## 3 · Artefact 1 — the eval case, written against the property"),
("md", "## 4 · Artefacts 2 and 3 — the control, and the detection for what it misses"),

  ("md", "## 7 · Score a year of findings by what still holds\\n\\n"
         "One finding handed over properly is the unit. A research programme is "
         "the sum of them — and the honest measure is not how much was found, but "
         "how much of it would still stop the same problem next year with nobody "
         "watching."),
],
 "expect": "The eval case returns False on the old build and True on the new one, "
           "covering 12 privileged/source combinations while leaving the "
           "principal path working. The control blocks the payload; the detection "
           "fires at critical severity on the old build and at info severity on "
           "the new one as coverage evidence. The handover package permits "
           "closure only when the proof of fix is valid and something shipped. "
           "Scored across a year of eight findings the programme lands 20 of a "
           "possible 40 durability points, with only three still holding without "
           "a person behind them.",
 "challenge": "Take a finding your team closed last quarter and check whether its "
              "eval case would fail on the pre-fix build. If nobody wrote one, "
              "you cannot currently tell whether the fix is still in place. Then "
              "score last year's findings on the ladder and report the durability "
              "number instead of the count.",
},

}
