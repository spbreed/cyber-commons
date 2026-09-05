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

  ("md", """## 2 · The file, and the key written before anything ran

This is a real pull request from CyberTravels' Coding Agent, in
[`labs/tools/semgrep-sast/booking.py`](https://github.com/spbreed/cyber-commons/tree/claude/vulnbench-setup-scheduling-81aqov/labs/tools/semgrep-sast).
Six defects, enumerated by hand **before** any scanner saw it — because a key
written after the scan is a description of the scan.

```python
def find_booking(reference):                                    # 7  CWE-862
    cur.execute("SELECT * FROM bookings WHERE reference LIKE '%" + reference + "%'")   # 9  CWE-89
def render_itinerary(template, booking):
    return eval(template, {"booking": booking})                 # 14 CWE-95
def sync_vendor(vendor_host):
    subprocess.run("curl -s https://" + vendor_host + "/manifest", shell=True)  # 17 CWE-78
def notify(url, payload):
    return requests.post(url, json=payload, verify=False)       # 20 CWE-295
API_KEY = "sk-live-4f9a2b1c8e7d6a5b3c2d1e0f9a8b7c6d"            # 22 CWE-798
```

Five of the six are the *presence* of a pattern. The sixth, on line 7, is the
**absence** of one: `find_booking` returns a booking to whoever asks, and the
Workflow Agent calls it holding `payments.refund`. Hold on to that line — it is
the whole reason this lesson has two skills in it."""),

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

The model returned 0.82 on the real defect and 0.71 on the invented one. It is
tempting to read a threshold into that gap, and every pipeline that does it
ships one.

Two reasons not to. The number is **uncalibrated** — 0.82 does not mean the
claim is right 82% of the time, it means nothing in particular. And it is
**unstable**: the same slice, the same model, ten runs, and the confidence
moves further than the distance between your accept and reject bands. Sort a
human's queue with it if you like. Do not let it decide anything on its own.

What killed the false positive instead cost nothing and required no judgement:
the model quoted a line that is not in the file. That check generalises, and
B2.4 is where it becomes a stage."""),

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
 "expect": "Semgrep's precision is 1.00 at all three widths and its recall is "
           "not: 0.17 on the default Python pack, 0.67 across seven registry "
           "packs, 0.33 on the custom taint rule — same file, same engine, and "
           "both scans exit 0. Two defects survive every width, and the skill "
           "separates them: the hardcoded key is a coverage gap somebody fixes "
           "by writing a rule, and the missing authorisation check on line 7 is "
           "not expressible as a pattern at any width. The model pass then finds "
           "exactly that one, at 0.82 confidence, recorded as a hypothesis and "
           "not a finding — and its claim about the already-authorised control "
           "function is rejected for nothing more than quoting a line that is "
           "not in the file. Zero hypotheses are promoted, because the audit "
           "stage does not promote its own output.",
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

That distinction decides the response. The instinct is to **suppress** — it
empties the queue, and it is the wrong fix for a reason that only appears
months later: a suppression is keyed to a file, a line and a rule, and *none of
those change when somebody wires the function back up*. The code becomes live,
the finding does not come back, and the entry that was hiding a false positive
is now hiding a real one.

**Attack surface reduction — ASR, which here means deleting the code — closes
both halves at once.** The finding goes because the code is gone, and so does
the latent risk of it being reconnected. It is the only response to a dead-code
finding that cannot rot, and the pleasant surprise is that the security queue
turns out to be the cheapest to-delete list in the building: already
enumerated, already ranked by what each line would cost if it ever became
reachable again.

One caution that does most of the work: "unreachable" and "dead" are not
synonyms. A test fixture and a feature flag that has been off for two years are
both unreachable *under a condition*, and both become reachable the day
somebody changes one line. Only code with no caller anywhere is a deletion
candidate.
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

  *skill_steps("appsec/dead-code-attack-surface",
               "## 10 · Dead code, suppression and ASR, as a skill\n\n"
               "The same eight findings from CyberTravels' booking service, "
               "partitioned into the three buckets — then the part that decides "
               "what to do with the unreachable ones.\n\n"
               "It compares the three available responses to a single dead "
               "`os.system` finding on three axes: does the finding go, does the "
               "risk go, and does the decision **rot**. Then it applies one "
               "commit six weeks later that re-imports the dead function, and "
               "shows which of the three responses is still protecting anything."),

  ("md", """## 11 · The commit six weeks later

That last block is the argument, and it is worth restating plainly because it
is the part that gets waved through in a triage meeting.

A suppression matched on `(file, line, rule)`. The re-enabling commit changed
none of the three — it added an import in a different file. So the suppression
still matches, the scanner still stays quiet, and a `sev 9` command injection is
now reachable from the vendor webhook with no finding attached to it.

The deletion cannot fail that way. The import does not resolve, the build breaks
at the moment somebody tries to bring the code back, and the failure is loud and
immediate rather than silent and eighteen months old.

If you must suppress, bind the suppression to **reachability** rather than to a
line, and give it an expiry. A suppression with neither is a permanent decision
recorded against temporary evidence."""),
],
 "expect": "The call graph identifies three entry points, one of which uses "
           "dynamic dispatch. `load_report` is reachable, `debug_dump` and "
           "`legacy_export` are unknown rather than unreachable because runtime "
           "handler resolution cannot be ruled out. Two-bucket filtering silently "
           "drops both, and the three-bucket routing sends the unknowns to Phase 4 "
           "instead of paging or discarding them. On the eight-finding queue, "
           "reachability takes 8 down to 2, and three of the remainder are dead "
           "with no caller anywhere \u2014 a deletion rather than a triage. "
           "Suppressing that dead `os.system` and marking it won't-fix both "
           "clear the finding and neither clears the risk: one commit six weeks "
           "later re-imports the function, the suppression still matches on "
           "file, line and rule, and the finding never comes back. Deleting it "
           "breaks that commit's build instead.",
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
