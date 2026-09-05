"""B1 (part 1) — The AppSec pipeline, phases 1 to 3. Sessions B2.1–B2.5.

The whole track is one artefact built in order: a five-phase, fifteen-stage
automated application-security pipeline, and the lessons run in exactly the
order the stages do.

    [Ingestion & Mapping] → [Threat Modelling] → [Discovery]
        → [Dynamic Validation] → [Reporting]

    Before any stage: what a harness is                        → B2.1
    Phase 1 · Ingestion & Structural Mapping
        1 historical parsing        2 structural indexing
        3 component summarisation   4 architecture synthesis
    Phase 2 · Threat Modelling
        5 threat modelling, from six static inputs                 → B2.2
    Phase 3 · Analysis & Filtering
        7 vulnerability auditing: real Semgrep, then the model pass → B2.3
        8 deduplication             9 contextual verification      → B2.4
       10 feasibility filtering                                    → B2.5

Stage 6 (strategic planning) is not a lesson of its own. Allocation is a
property of the stage that spends the budget rather than a stage that spends
none, so it is taught where the money actually goes: the audit agent in B2.3
decides where to run the model pass, and B2.5 decides what is worth
reproducing.

Phases 4 and 5 continue in track_b1b.py, and B2.14 closes the track with Google
Mantis as a bonus: a real implementation of this pipeline, mapped stage by stage
onto what you built.
"""

from .skills import SKILL_RUNTIME, skill_steps, runtime_step

RUNTIME_STEP = runtime_step()

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
> To run the identical pipeline stage against a real open-weight model:
>
> ```bash
> ollama pull glm-4.6            # or kimi-k2, llama3.3
> export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
> ```
"""

from . import diagrams as D

EXERCISES: dict[str, dict] = {

# Deliberately the shortest lesson in the chapter. It exists to define one word
# that the next thirteen lessons use constantly, and a definition lesson that
# runs long stops being a definition.
"B2.1": {
 "concept": """
**Building a harness, in security engineering, is building everything around a
model that turns generating text into getting work done: what it sees, what it
may do, how you know whether it worked, and when it stops.** A model on its own
is a text generator — no memory, no actions, no notion of success. The wrapper
is what makes it a control, and every part of that wrapper is a security
decision: the tool surface is an authorisation problem, the verifier decides
what your pipeline is allowed to believe, and the budget is the only thing
still holding once the model is the component you cannot trust.

You already run several, whether or not anyone calls them that:

- **The CI security scan.** Sees the changed files, may only read, "worked"
  means a zero exit and a finding that parses, stops on a timeout.
- **An autofix bot.** Sees the finding and the file, may open a branch, and
  "worked" should mean *the exploit no longer reproduces* — not *the scanner
  went quiet*.
- **A SOC triage assistant.** Sees the alert and its enrichment, may query the
  SIEM read-only, and "worked" means its disposition matched an analyst's on a
  held-out sample.

The third field is where harnesses fail, and they fail quietly. A harness whose
verifier is the model agreeing with itself does not stop and report an error —
it **succeeds incorrectly**, files a clean trace, and the bug is found later by
whoever merged the patch.
""",
 "steps": [
  ("md", "## 2 · The four moves"),
  ("html", D.table(
    ["move", "who does it", "the security decision in it"],
    [["<b>plan</b>", "the model", "none — this is the part you did not write"],
     ["<b>act</b>", "the harness", "the tool surface: what is even expressible"],
     ["<b>verify</b>", "something independent",
      "<b>what the pipeline is allowed to believe</b>"],
     ["<b>stop</b>", "the harness", "the budget — the last control still standing"]],
    emphasise=2,
    caption="Frameworks make plan and act easy and leave verify and stop as "
            "your problem, usually defaulting to “the model says it is "
            "done” and “loop forever”.")),

  *skill_steps("appsec/agentic-harness-loop",
               "## 3 · One loop, run twice\n\nThe simplest harness that shows "
               "the point: about twenty lines, one real model call, one SQL "
               "injection from CyberTravels' booking service. It runs with no "
               "verifier and then with one — same model, same prompt.\n\n"
               "Offline the model is a labelled replay; against a served "
               "open-weight endpoint it is the identical code."),

  ("md", """## 4 · The part worth keeping

Read the last block of that output again. The answer it rejects —
`ref=" + escape(ref)` — is the one that matters: it reads like a fix, it would
pass a human skim, and it is still concatenation. Without a verifier the loop
accepts it, reports success and files a clean trace.

That is the whole reason this chapter defines the word before it builds
anything. Every stage after this one is a harness, and for each of them the
question is the same: **what, other than the model, decided that this worked?**"""),
 ],
 "expect": "The loop runs with a real model behind `ask()` — a labelled replay "
           "offline, a real open-weight call when one is served. With no "
           "verifier it accepts whatever came back and reports "
           "`verified: None`. With the verifier the same model and prompt "
           "produce an accepted, parameterised line; a narrow verifier that "
           "only accepts `?` is shown rejecting a correct psycopg fix, and a "
           "plausible answer wrapping the input in `escape()` is refused, "
           "because it is still concatenation.",
 "challenge": "Name your pipeline's verifier out loud. If the sentence contains "
              "\"the model checks\" or \"it looks right\", you have a judge, and "
              "a judge approves confident prose — including prose that "
              "contradicts the finding it is attached to.",
},

"B2.2": {
 "concept": """
Stage 5 is the one everybody claims to do and almost nobody re-runs.

A threat model produced in a workshop describes the system as it was on the day
of the workshop. It is stale the moment an entry point is added, and adding an
entry point is a Tuesday. So this stage does not *write* a threat model — it
**derives** one, from evidence the estate already holds, and the useful artefact
is the diff between two runs.

**STRIDE** gives six questions. Against an agentic system each has a shape a
web-application threat model does not:

| STRIDE | In an agentic system |
|---|---|
| **S**poofing | agents share a service account, so "which agent" is unanswerable |
| **T**ampering | untrusted content the agent read becomes an instruction it follows |
| **R**epudiation | the delegation chain is not on the token, so no log answers "on whose behalf" |
| **I**nformation disclosure | an over-broad tool return, or egress that permits anything |
| **D**enial of service | an unbounded loop, or a budget nobody set |
| **E**levation of privilege | a role assumable by `*`, or a scope that included refunds because it included payments |

### Derived from five inputs, not one

The architecture map says what the code *could* reach. It cannot say whether
that path is exposed, what identity walks it, or whether anything can leave at
the end of it — and those three decide whether a finding is a fire.

| Input | What only it can tell you |
|---|---|
| **architecture** | components, flows, sinks, trust levels |
| **CSPM** | that the bucket behind that sink is public *today* |
| **IAM** | who can assume the role, and whether MFA is required |
| **network** | is it internet-facing, and can anything leave |
| **entitlements** | what the identity may do once it is through |

Read only the first and you produce a model that is identical for two
deployments of the same repository — one behind a private load balancer with no
egress, one on the internet with a wildcard trust policy. It is wrong about
both.

This lesson runs the `threat-model-stride` skill. You do not write the code;
you read the procedure, execute it, and read what it produced.
""",
 "steps": [
  ("md", "## 2 · The skill\n\nThis is `skills/appsec/threat-model-stride/SKILL.md`, "
         "verbatim. The frontmatter is what routes a request to it; the body is "
         "the procedure a model follows."),
  ("skill", "appsec/threat-model-stride"),
  ("md", "## 3 · Its script\n\nThe deterministic half of the skill — the part "
         "that has to give the same answer twice so two runs can be diffed. "
         "Embedded from `skills/appsec/threat-model-stride/scripts/`."),
  ("skill_script", "appsec/threat-model-stride/scripts/threat_model.py"),
  ("md", "## 4 · Execute it against CyberTravels\n\nFive synthetic inputs, "
         "standing in for what a real estate already holds."),
("md", "## 5 · The diagram it emits\n\nMermaid, so it renders here and on "
         "the lesson page without a library. Double arrows are trust-boundary "
         "crossings — the edges every finding turned out to live on."),
("md", "## 6 · The same code, a hardened estate\n\nNot one line of "
         "CyberTravels\' source changes. Only the four evidence inputs around "
         "it do."),
],
 "expect": "The skill loads with its routing description and procedure, then "
           "derives twelve threats across all six STRIDE categories from five "
           "synthetic inputs, each carrying the evidence line that set its "
           "score. It emits a mermaid diagram marking the two trust-boundary "
           "crossings. Re-running against a hardened estate — same code, four "
           "different evidence inputs — keeps every row and drops the maximum "
           "severity from 11 to 1.",
 "challenge": "Point the skill at one of your own services. The work is not the "
              "model, it is collecting the five inputs: if any of them is \"in "
              "somebody\'s head\", that is the input your threat model is "
              "currently guessing at, and the guess is always the optimistic one.",
},

"B2.3": {
 "concept": """
**Stage 7 — Vulnerability auditing.** The stage people mean when they say
"SAST", and the one where the two halves of this pipeline are easiest to
confuse with each other.

**The deterministic half is a real scanner with real rules.** Semgrep, CodeQL,
OpenGrep. Parse the code to a graph, ask a rule a question about it, and get
the same answer every time. That repeatability is what lets you gate a merge on
it — a probabilistic check cannot block a build, because the same commit would
pass on Tuesday and fail on Wednesday.

Its limit is not accuracy. On the file below Semgrep's precision is **1.00 at
every ruleset width**; it does not report bugs that are not there. Its limit is
that a rule only finds the pattern somebody wrote, so its **recall is a
configuration decision** — and one that is invisible, because a narrow scan and
a wide scan both exit `0`.

**The probabilistic half reads the code and reasons.** No rule needs to exist
first, which is exactly its value, and it is the only thing that reaches a
defect that is the **absence** of a call. It also invents defects, confidently,
with a similar-looking confidence number attached.

So the two are not competing generations where the newer one wins. They answer
different questions and fail in opposite directions, and this lesson runs each
as its own skill:

| | deterministic — Semgrep | probabilistic — the model pass |
|---|---|---|
| same answer twice | yes | no |
| can gate a merge | **yes** | no |
| finds what no rule expresses | no | **yes** |
| typical failure | missed it entirely | reported it and it was not there |
| output is a | **finding** | **hypothesis** |

That last row is the load-bearing one. Everything the model says enters the
pipeline as a hypothesis, and stages 8–12 are what turn one into a finding.
""",
 "steps": [
  ("md", PIPELINE_NOTE),

  ("md", """## 2 · The repository, and the key written before anything ran

Everything this chapter scans is one tree:
[`cybertravels/`](https://github.com/spbreed/cyber-commons/tree/claude/vulnbench-setup-scheduling-81aqov/cybertravels)
— the reference architecture from A1.1, as source. Ingress, orchestrator, the
four agents, the tools, both MCP servers, knowledge, messaging. `egress/` is
absent, because CyberTravels has no gateway.

Eight defects, enumerated by hand in
[`LABELS.md`](https://github.com/spbreed/cyber-commons/blob/claude/vulnbench-setup-scheduling-81aqov/cybertravels/LABELS.md)
**before** any scanner saw it — a key written afterwards is a description of
the scan. Four correct functions are in the key too, because a corpus where
everything is broken cannot measure precision.

```python
# tools/bookings_api.py
def get_booking(session, booking_id):          # 20  CWE-639  no owner check
def get_my_booking(session, booking_id):       #     the same read, authorised
def cancel_booking(session, booking_id):       # 34  CWE-639  and it writes
def search_bookings(session, reference):       # 41  CWE-89 + CWE-639
# tools/payments_api.py
def issue_refund(session, booking_id, amount): #  8  CWE-639  on the money path
def download_invoice(session, path):           # 23  CWE-22 + CWE-639
```

Look at `get_booking` and `get_my_booking`. They are four lines apart and
almost identical; one of them is a critical finding. The difference is a call
that is **present in the second and absent in the first**, and holding that in
mind is the whole of this lesson."""),

  ("md", """## 3 · Real Semgrep, at three widths, with the rule as a file

Not a forty-line taint engine written to fit in a lesson. Semgrep **1.176.0**,
against that file, three configurations —
[`run.sh`](https://github.com/spbreed/cyber-commons/tree/claude/vulnbench-setup-scheduling-81aqov/labs/tools/semgrep-sast)
reproduces all three and the raw JSON is committed beside the skill.

The third is a custom taint rule, which is what a real one looks like:

```yaml
rules:
  - id: cybertravels-sql-concat
    languages: [python]
    severity: ERROR
    message: >-
      Caller-controlled input is concatenated into a SQL string. Use a
      parameterised query.
    mode: taint
    pattern-sources:
      - pattern: |
          def $F(..., $X, ...):
            ...
    pattern-sinks:
      - pattern: $CUR.execute(...)
```

`mode: taint` is the whole difference between generations of scanner: not a
better pattern, a different question — *does caller-controlled input reach this
sink?*"""),

  *skill_steps('appsec/sast-semgrep-deterministic',
               "## 4 · The deterministic half, as a skill\n\n"
               "The skill scores each of the three real runs against the "
               "six-defect key and reports precision and recall **separately**, "
               "because merging them into one \"accuracy\" number hides the only "
               "one that moves. Then it partitions what every width missed into "
               "the two classes that matter: a defect a rule *could* match and "
               "nobody wrote (write the rule) and a defect no rule can express "
               "(the next skill)."),

  ("md", """## 5 · What changed when SAST learned to reason

For twenty years the answer to "can a scanner find this?" was decided by one
question: **is there a pattern?** Everything else followed. Rules were written
per defect class and per library, coverage was a config decision, and a class
with no syntax to match — a missing check, a wrong comparison, an absent expiry
— was simply outside the tool.

That boundary moved. Systems that *reason about a class* rather than match a
pattern now find defects that no rule expresses, and IDOR is the honest place to
look at it: the class is defined by absence, so it is the case where pattern
matching scores exactly zero and any number above that is new capability.

Semgrep published a benchmark for it in 2026 — 275 hand-reviewed labels across
four repositories, the same revisions for every system
([write-up](https://semgrep.dev/blog/2026/idor-detection-benchmark-semgrep-multimodal/)):

| system | recall | precision | F1 |
|---|---|---|---|
| Semgrep Multimodal | **59.9%** | 57.5% | 57.1% |
| Claude Security with Mythos | 13.9% | **80.1%** | 23.7% |
| Codex Security | 11.3% | — | 17.7% |

**Read it as a recall table, because that is what it is.** The two bold cells
are the argument. The most *precise* system on that board found roughly **one
IDOR in seven** — it is right when it speaks and it stays quiet about six of
every seven real defects. The best recall is **six in ten**, four times as many,
from a system reasoning about the class.

Three things follow, and the third is the one that changes what you do on
Monday.

**Precision is the easy half.** A detector that reports nothing is perfectly
precise. Any access-control tool that leads with its precision number is leading
with the metric that improves when it finds less.

**Recall needs a key, which is why nobody publishes it.** You cannot compute
what fraction of the real defects were found without knowing the real defects.
That is expensive, it is manual, and it is the only thing that turns "the scan
was clean" into a statement with content. This is why `cybertravels/LABELS.md`
exists and why it was written before anything ran.

**Six in ten is a real change and it is not a solved problem.** It is the
difference between a class you could not scan for at all and one you can scan
for imperfectly — and at 57.5% precision it means roughly two in five reports
are wrong. That is a hypothesis stream, not a finding stream, which is exactly
how B2.4 and B2.5 are going to treat it."""),

  ("md", """## 5 · Which of the two misses justifies a model

One of them does not. Line 22 is a hardcoded key — lexical, and `p/secrets` was
enabled and did not fire only because the string matches no known provider's
format. That is a rule somebody writes this afternoon, and reaching for a model
to find it is buying a language model to do a regex's job.

Line 7 is different in kind. There is no syntax for "this function should have
called `require_owner` and did not", and there is no width of ruleset that
reaches it — the defect only exists relative to the authority the caller holds,
which is in a different file. That is the boundary, and it is narrow. Cross it
deliberately and you have a reason to spend the model pass; cross it because
the deterministic scan felt disappointing and you have bought noise."""),

  *skill_steps("appsec/idor-detection-recall",
               "## 6 \u00b7 IDOR on the CyberTravels tree, scored on recall\n\n"
               "The same repository, the class that has no pattern. The skill "
               "builds the **denominator** first \u2014 every unit that takes an "
               "identifier and touches a record \u2014 because recall without a "
               "denominator is not a number. Then it runs two detectors over "
               "it: what a rule can express, and the ownership comparison it "
               "cannot see.\n\nWatch the row where two of the five were "
               "already in a scanner's output, for a different defect in the "
               "same function."),

  ("md", """## 7 \u00b7 The finding count went down and the risk did not

`search_bookings` concatenates its reference into SQL **and** returns every
owner's bookings. Semgrep finds the first at the widest width. Nothing finds the
second.

So the ticket says *SQL injection in search_bookings*, somebody parameterises
the query, the finding closes, and the scan is green. The authorisation defect
is untouched and now has no finding attached to it at all. The count went to
zero and the risk did not move.

That is the failure mode this section exists for, and it is not exotic — it is
what happens by default whenever one function carries a defect a rule can see
and a defect it cannot. The fix is not a better rule. It is running the second
detector over a denominator, and reporting recall against a key."""),

  *skill_steps('appsec/sast-model-pass',
               "## 6 · The probabilistic half, as a skill\n\n"
               "The same adapter every model-facing skill in this commons uses: "
               "offline a labelled replay, and against a served open-weight model "
               "the identical code. It is asked one question with a checkable "
               "answer, over the smallest slice in which the defect is decidable "
               "— the function, its signature, and the authority its caller "
               "holds.\n\n"
               "It reviews two functions. One has the defect. The other is "
               "already parameterised and already authorised, and it is in there "
               "because a review pass that is never wrong has not been tested."),

  ("md", """## 7 · Where it breaks — gating on the confidence number

In the offline run the replay returns 0.82 on the real defect and 0.71 on the
invented one. It is tempting to read a threshold into that gap, and every
pipeline that does it ships one.

Two reasons not to. The number is **uncalibrated** — 0.82 does not mean the
claim is right 82% of the time, it means nothing in particular. And it is
**unstable**: the same slice, the same model, ten runs, and the confidence moves
further than the distance between your accept and reject bands. Sort a human's
queue with it if you like. Do not let it decide anything on its own.

What kills a fabricated claim instead costs nothing and requires no judgement:
**the quoted line is not in the file**. That check generalises, and B2.4 is
where it becomes a stage.

> **A result from running this against a real model, worth keeping.** The skill
> is written so the verifier is tested directly, against a quote known not to be
> in the slice — rather than by waiting for the model to fabricate one. That is
> not fastidiousness. An earlier version asserted that the model *would* invent
> a defect in the already-authorised control function, and against a served
> Qwen2.5-7B it did not: it read the function correctly and declined. The
> assertion failed because the model behaved well, which is a bug in the
> assertion. A pipeline check has to hold whether or not the model misbehaves on
> the day you run it."""),

  ("md", """## 8 · An agent drives both, because you cannot afford both everywhere

Semgrep is cheap enough to run over the whole repository. The model pass is
not — at four million lines it costs more than the finding is worth, and a
model asked to review everything reviews nothing carefully.

So neither half is the interesting part. **The allocation is**, and the policy
is three rules:

1. run the deterministic scanner everywhere, at the widest ruleset that is not
   noisy, because it is nearly free and it can gate the merge;
2. spend the model pass only where stage 1 says risk lives **and** the rules
   were silent — silence in a high-risk zone is the signal, not the noise;
3. mark everything the model says as a hypothesis, never a finding.

Get rule 2 wrong in the cheap direction and the authorisation defect on line 7
is never reviewed by anything, because the deterministic scan was green and
nobody was surprised by that."""),
],
 "expect": "Semgrep\u2019s precision is 1.00 at all three widths and its "
           "recall is not: 0.12 on the default Python pack, 0.38 across seven "
           "registry packs, 0.25 on the custom taint rule \u2014 same tree, "
           "same engine, every scan exits 0. Five of the eight defects survive "
           "every width, in three classes: one coverage gap somebody fixes by "
           "writing a rule; one where the defect is textbook and the rule is "
           "written against `requests` while CyberTravels calls its own HTTP "
           "wrapper; and three IDORs that no pattern reaches at any width. The "
           "IDOR skill then builds the denominator \u2014 seven units that take "
           "an identifier and touch a record, two of them correctly authorised "
           "\u2014 and scores two detectors on it: the pattern rule finds 0 of "
           "5, the ownership-comparison analysis finds 5 of 5. Two of those "
           "five were already in a scanner\u2019s output for a *different* "
           "defect in the same function. The model pass then finds the "
           "missing-authorisation defect at 0.82 confidence, recorded as a "
           "hypothesis, and its claim about the already-authorised control "
           "function is rejected for quoting a line that is not in the file.",
 "challenge": "Two things, and the second is the one people skip. Run Semgrep "
              "against one of your own repositories at your current ruleset and "
              "at seven packs, and count the difference — whatever that number "
              "is, it has been the number all year. Then point the model pass at "
              "a real GLM-4.6 or Kimi K2 through Ollama and run one slice ten "
              "times. The variance in what it reports, and in its confidence, is "
              "what decides whether you can gate on confidence at all, and you "
              "cannot learn it from one run.",
},

"B2.4": {
 "concept": """
Stage 7 ran several analysers in parallel. That produces two problems this stage
exists to solve, and they are different problems.

**Stage 8 — Deduplication.** Three analysers find the same bug and report it
three times. Worse, they report it at slightly different line numbers with
different CWE labels, so naive matching does not collapse them. An engineer who
sees the same bug three times stops trusting the count.

**Stage 9 — Contextual verification.** Cross-reference each finding against the
actual syntax and imports to weed out hallucinations. This is the cheapest,
highest-yield filter in the whole pipeline, because a model finding that
references a function that does not exist, or a module that was never imported,
is *provably* wrong — no judgement required.

The order matters: deduplicate first, then verify, or you spend verification
effort on three copies of the same claim.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · The raw output of three parallel tracks"),
("md", "## 3 · Stage 8 — deduplicate on the defect, not the report\n\n"
         "Two findings are the same defect if they name the same sink in the same "
         "function, even at different lines and under different CWE labels. "
         "Cluster on that, and keep the *best-evidenced* member."),
("md", "## 4 · Stage 9 — contextual verification against the real syntax\n\n"
         "Now check each surviving claim against the code. Three checks, all "
         "mechanical, none requiring judgement."),
  *skill_steps('appsec/finding-dedup-and-verification',
               "## 2 · The stage, as a skill\n\nSeven raw findings, four defects. The skill normalises the CWE aliases, keys each finding by its enclosing function rather than a line number, and then rejects the survivors whose symbols are not in the file — because a finding about `os.system` in a file that never imports `os` should die here rather than in a maintainer's inbox."),
],
 "expect": "Seven raw findings collapse to four distinct defects, with the "
           "CWE-943 alias merging into CWE-89 and the taint result kept over grep "
           "and model duplicates. Contextual verification then rejects the "
           "hallucinated `DB_PASSWORD` and `os.system` findings because neither "
           "symbol appears in the file and `os` is never imported, leaving the "
           "real SQL injection.",
 "challenge": "Add a fourth verification check: does the CWE class match the sink "
              "type? A CWE-22 finding on a `conn.execute` call is provably "
              "mislabelled, and that check costs nothing to run.",
},

"B2.5": {
 "concept": """
**Stage 10 — Feasibility filtering.** The last stage of Phase 3, and the one
that decides whether anyone gets paged.

A verified finding is a real bug in the code. It is not necessarily a real risk,
because the code may be unreachable: dead code, a test fixture, an internal
function no external caller can drive, a branch behind a feature flag that has
been off for two years.

Triaging an unreachable finding costs exactly as much as triaging one on the
login path, and there are usually far more of them. So this stage partitions
findings into three buckets — and the third bucket is the honest one:

- **reachable** — a path exists from an untrusted entry point to the sink,
- **unreachable** — no path exists,
- **unknown** — the analysis cannot decide, usually because of dynamic dispatch,
  reflection, or a framework that wires callers at runtime.

Reporting `unknown` as `unreachable` is how a pipeline quietly drops real bugs.

### Dead code, and the two different claims a finding makes

The largest single class in that unreachable bucket is **dead code**, and it is
worth being precise about what is wrong with such a finding, because teams act
on the wrong half.

The finding is a **true positive about the code**. The concatenation is there,
the sink is real, and any reviewer who opens the file will agree. It is a
**false positive about the risk**, because nothing untrusted reaches it. Two
different claims, and only the second one is wrong.

### Deciding which is which needs the AST

You cannot answer it with grep. `def report`, `report(` and `# report` are the
same string to a regex, and a function called `run` appears in every file you
own. The question — *which functions call this one* — is about structure, so it
needs the **abstract syntax tree**.

Parsing gives you exactly the two node types the question needs:

| AST node | what it gives you |
|---|---|
| `FunctionDef` | every function that exists, with its real nesting and its decorators |
| `Call` | every invocation, attributable to the function it sits inside |

Nodes and edges. Walk from the entry points and everything you reach is
reachable; everything you do not is dead **or** undecided.

The resolver should be deliberately naive. `Call.func` is a `Name` for `f()`
and an `Attribute` for `obj.f()`; take `.id` or `.attr` and accept that two
methods with the same name merge. That over-reports reachability, which is the
safe error. A cleverer resolver that guesses wrong marks a live function dead,
and that error is silent.

### And the AST is honest about what it cannot see

This is the more useful half, and it is where the third bucket comes from. The
AST resolves a literal call. It cannot resolve

```python
handler = getattr(HANDLERS, name)   # the callee is a runtime value
return handler(arg)
```

nor a dispatch dictionary, nor a handler a framework registers by decorator at
import time. None of those are unreachable — they are **undecided**, and the
rule that follows is the one that keeps the analysis honest: if a module
contains a call the AST could not follow, *every* unreached function in that
module is `unknown`, not `unreachable`.

Deleting is the right resolution for the genuinely dead ones, and it is the only
one that cannot rot: a suppression is keyed to a file, a line and a rule, and
none of those change when somebody wires the function back up.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 10 — build the call graph from entry points"),
("md", "## 3 · Where it breaks — collapsing `unknown` into `unreachable`\n\n"
         "The tempting simplification. It makes the queue shorter and it is how "
         "real bugs get dropped, because dynamic dispatch is exactly where "
         "framework-wired handlers live."),
("md", "## 4 · The control — route each bucket to a different place"),

  ("md", "## 6 · Phase 3 as a skill — and the counts that police it\n\n"
         "Stages 7 to 10 only ever *shrink* the list. That is a property worth "
         "enforcing rather than trusting, so the skill's contract carries a "
         "`counts` object and the rule that it must never increase.\n\n"
         "A pipeline whose `verified` count exceeds its `deduped` count has "
         "invented findings somewhere after the audit stage — and that is far "
         "easier to do by accident than it sounds, because a verification step "
         "that expands one finding per code path looks perfectly reasonable "
         "from the inside."),
  ("skill", "appsec/appsec-vuln-audit"),
  ("skill_script", "appsec/appsec-vuln-audit/scripts/appsec_vuln_audit.py"),


  ("md", "## 7 · Where it breaks — deduplicating on the wrong key\n\n"
         "The skill says to collapse on the **defect identity**, "
         "`(cwe, file, unit, sink_expression)`, and never on the message text. "
         "Here is why that sentence is in the procedure."),

  ("md", "## 8 · The same failure, from a real model\n\n"
         "Everything above is constructed. Here is the identical failure "
         "produced by an actual open-weight model — **Moonlight-16B-A3B**, "
         "Moonshot AI's MoE from the Kimi team — run on a Kaggle CPU kernel "
         "against this skill's output contract.\n\n"
         "It was given the contract and two vulnerable functions: an `open()` "
         "on a caller-supplied path, and an `os.system()` on a caller-supplied "
         "argument. Its answer is reproduced verbatim below "
         "([full run](https://github.com/spbreed/cyber-commons/blob/"
         "claude/vulnbench-setup-scheduling-81aqov/labs/kimi/"
         "moonlight-16b-completion-prompt.txt))."),

  ("md", "## 9 · Read that output again\n\n"
         "It passes the contract with zero problems, and almost nothing in it "
         "is true."),

  *skill_steps("appsec/dead-code-ast-reachability",
               "## 10 \u00b7 The call graph, parsed rather than grepped\n\n"
               "The whole `cybertravels/` tree \u2014 the same repository B2.3 "
               "scanned \u2014 parsed for real with `ast.parse`. The skill "
               "collects `FunctionDef` nodes and `Call` edges, marks the two "
               "decorated ingress handlers as entry points, and walks.\n\n"
               "Then watch what happens at the orchestrator. CyberTravels' "
               "router dispatches through `AGENTS[intent](message, session)`, "
               "and a table lookup is not something the AST can follow \u2014 "
               "so almost everything below it is undecided rather than dead."),

  ("md", """## 11 \u00b7 The bucket that is work rather than a result

Read the middle column rather than the total: **4 reachable, 8 unreachable, 10
undecided.**

The eight unreachable ones are the easy win, and they are a deletion rather
than a triage — the finding goes because the code goes, and unlike a
suppression that cannot rot. The security queue turns out to be the cheapest
to-delete list in the building: already enumerated, already ranked by what each
line would cost if it ever became reachable again.

The ten undecided ones are the point. They include the command injection in the
Coding Agent, the traversal on the File System Agent's invoice path, and the
refund tool — every one of them behind a table lookup the AST cannot resolve. A
two-bucket pipeline files all ten as unreachable and reports the queue clean.

One caution that does most of the remaining work: **"unreachable" and "dead"
are not synonyms.** A test fixture and a feature flag that has been off for two
years are both unreachable *under a condition*, and both become reachable the
day somebody changes one line. Only code with no caller anywhere, in a module
the AST fully resolved, is a deletion candidate."""),

],
 "expect": "The AST pass parses the whole `cybertravels/` tree: 22 "
           "functions, 14 resolved call edges, and the two decorated ingress "
           "handlers as entry points. It records one unresolvable call \u2014 "
           "the router\u2019s `AGENTS[intent](...)` table lookup \u2014 and "
           "that single line decides the shape of everything else: 4 reachable, "
           "8 unreachable, 10 undecided. The undecided ten include the command "
           "injection, the invoice traversal and the refund tool, all behind "
           "the lookup. Of the six findings the audit stage handed over, three "
           "are false positives about the risk and three are unresolved work "
           "that a two-bucket pipeline would report as zero.",
 "challenge": "Two counts, and the second is the uncomfortable one. Count how "
              "many `unknown` cases your own reachability analysis produces and "
              "find out what your tooling does with them \u2014 if it reports "
              "them as clean, the number of real bugs you are dropping is the "
              "size of that bucket. Then open your suppression file and find the "
              "oldest entry. Check whether the code it covers is still "
              "unreachable, and whether anything in your pipeline would have "
              "told you if it stopped being."
},
}
