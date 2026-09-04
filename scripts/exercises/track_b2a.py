"""B1 (part 1) — The AppSec pipeline, phases 1 to 3. Sessions B2.1–B2.5.

The whole track is one artefact built in order: a five-phase, fifteen-stage
automated application-security pipeline, and the lessons run in exactly the
order the stages do.

    [Ingestion & Mapping] → [Threat Modelling] → [Discovery]
        → [Dynamic Validation] → [Reporting]

    Phase 1 · Ingestion & Structural Mapping
        1 historical parsing        2 structural indexing
        3 component summarisation   4 architecture synthesis       → B2.1
    Phase 2 · Threat Modelling
        5 threat modelling, from six static inputs                 → B2.2
    Phase 3 · Analysis & Filtering
        7 vulnerability auditing, three generations of SAST        → B2.3
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

"B2.1": {
 "concept": """
Most review starts at the diff. That is the smallest possible context, and it
throws away the single best predictor you have: **this repository has already
told you where it breaks.**

Phase 1 is four stages, and they run before any analysis. They take a
repository and produce the one artefact everything downstream consumes — a map.

**Stage 1 — Historical parsing.** Extract prior vulnerabilities, the commits
that fixed them, and pull-request history. Files that have been fixed for
security reasons before are dramatically more likely to be fixed again. It is
one of the oldest empirical results in software engineering, and almost nobody
wires it into a scanner.

**Stage 2 — Structural indexing.** Break the code into *semantic units* —
functions, classes, modules — and index how they call each other. Not lines,
not files. A scanner that reasons over lines cannot answer "who reaches this?",
and every later stage needs that answer.

**Stage 3 — Component summarisation.** One short summary per directory: what it
is for, what it talks to, what data passes through it. *Local* is the important
word — summarise the whole repository at once and you get a paragraph that is
true of every repository.

**Stage 4 — Architecture synthesis.** Compile the summaries into a single map
carrying three things: **entry points** where untrusted input arrives, **data
flows** between components, and **trust boundaries** where data crosses from
less trusted to more trusted.

The map is the artefact. Stage 5 reads its boundaries, stage 7 prioritises
against them, stage 10 walks its flows. And because it is derived rather than
drawn, it changes when the code changes — which is the property the last cell
in this lesson demonstrates and the reason the next lesson works at all.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
  ("md", "## 2 · Stage 1 — historical parsing\n\n"
         "A slice of the CyberTravels bookings repository: commits, their "
         "subjects, and which of them were security fixes. Nothing has been "
         "scanned yet."),
("md", "## 3 · Stage 2 — structural indexing\n\n"
         "Index the code into semantic units. `ast` does the work here; in a "
         "polyglot repository this is what tree-sitter is for."),
("md", "## 5 · Stage 3 — summarise each component, locally\n\n"
         "The model call above is what stage 3 looks like in production. Below "
         "is the deterministic version, so the rest of the lesson has a fixed "
         "input to work from."),
("md", "## 6 · Stage 4 — synthesise the map, and find the boundaries\n\n"
         "A trust boundary is any edge where data crosses from a less-trusted "
         "component into a more-trusted one. Those edges are where every "
         "finding in the rest of the pipeline turns out to live."),
("md", "## 7 · The map changes when the code changes\n\n"
         "This is the whole reason for deriving it. One function is added; the "
         "map is regenerated; the delta is the thing the next lesson threat-models."),
("md", "## 8 · Write the four stages down as an agent skill\n\n"
         "You have just run Phase 1 by hand. The next repository needs the same "
         "four stages and so does the next agent, so the procedure belongs in a "
         "file rather than in your head. This is the one in this repository:"),
  ("skill", "appsec/appsec-repo-recon"),
  ("skill_script", "appsec/appsec-repo-recon/scripts/appsec_repo_recon.py"),
 ],
 "expect": "Four of ten commits match the security markers, and `src/api/"
           "bookings.py` ranks highest on decayed risk purely from history — "
           "with the most recent security commit scoring nothing, because it "
           "matches no marker. The structural index extracts five functions and "
           "identifies two entry points. Component summaries name what each "
           "directory touches, and the synthesised map shows both entry points "
           "reaching the database and the filesystem across a trust boundary. "
           "Adding one function adds a third entry point and two more boundary "
           "crossings.",
 "challenge": "Run stage 1 against a repository you own: `git log --name-only "
              "--grep='CVE\\|security\\|injection'`, then rank the files by how "
              "often they appear. That list usually surprises people, and it is "
              "free. Then check how many of your recent security fixes your "
              "markers would have missed.",
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
**Stage 7 — Vulnerability auditing.** The deep-dive analysis stage, and the one
people think of as "SAST". It has had three generations, and knowing what each
can and cannot see is what stops you buying the wrong one.

**Generation 1 — grep.** Pattern-match dangerous constructs. Fast, zero setup,
fires on every occurrence whether reachable or not. Precision is poor, so it gets
muted.

**Generation 2 — rules with dataflow.** Semgrep, CodeQL, OpenGrep. Parse to an
AST or graph and track *taint*: does untrusted input reach a dangerous sink?
Precision improves enormously. The cost is that a rule only finds the pattern
someone wrote it for.

**Generation 3 — model review.** An open-weight model reads the code and reasons.
No rule needs to exist first, which is exactly its value — and it also invents
bugs that are not there, confidently.

The mistake is treating generation 3 as a replacement for generation 2. The
combination that works: rules for what rules do well, deterministically; the
model for what rules cannot express; and everything the model says treated as a
**hypothesis** until stages 8–12 confirm it.
""",
 "steps": [
  ("md", PIPELINE_NOTE),
("md", "## 2 · Generation 1 — grep, and why it gets muted\n\n"
         "The safe functions in this corpus matter more than the buggy ones: a "
         "scanner that fires on parameterised SQL is one nobody runs twice."),
("md", "## 3 · Generation 2 — taint rules\n\n"
         "The improvement is not a better pattern. It is a different question: "
         "*does untrusted input reach this sink?* A function parameter is "
         "untrusted; a string literal is not."),
("md", "## 4 · Generation 3 — what rules structurally cannot see\n\n"
         "Generation 2 is perfect on this corpus. So why involve a model? Because "
         "a rule only finds what someone wrote it for. Here is a bug with no "
         "rule: an authorization check that is *present* and wrong."),
("md", """## 5 · Generation 2, as the tool you would actually run

The taint engine above is forty lines so it fits in a lesson. In production
generation 2 is Semgrep, CodeQL or OpenGrep, and a rule is a file. This is the
Semgrep rule for the same taint property the engine above implements:

```yaml
rules:
  - id: cybertravels-sql-concat
    languages: [python]
    severity: ERROR
    message: >-
      Traveller-controlled input is concatenated into a SQL string. Use a
      parameterised query.
    mode: taint
    pattern-sources:
      - pattern: $REQ.args[...]
      - pattern: $REQ.files[...]
    pattern-sinks:
      - pattern: $CONN.execute(...)
    pattern-sanitizers:
      - pattern: sqlite3.paramstyle
```

[`labs/tools/semgrep-sast/`](https://github.com/spbreed/cyber-commons/tree/main/labs/tools/semgrep-sast)
installs Semgrep 1.176.0 and runs it against a pull request from the Coding
Agent. Two things came out of that run and both matter here.

**Coverage is a configuration decision, and it is invisible.** The same file,
two ruleset widths:

```
  p/python + p/secrets: 1 finding
    line  17  ERROR   subprocess-shell-true

  seven packs: 4 findings
    line   9  ERROR   sqlalchemy-execute-raw-query
    line  14  WARNING eval-detected
    line  17  ERROR   subprocess-shell-true
    line  20  ERROR   disabled-cert-validation
```

Nothing about the file changed. On the narrow setting three real defects were
simply not looked for, and the scan exits 0 either way.

**And two defects survived both widths:**

```
  line  22  MISSED a live-looking API key on a module-level constant
  line   7  MISSED find_booking performs no authorisation check of any kind
```

The first is lexical — `p/secrets` was enabled and did not fire, because the
string matches no known provider's format. A rule could catch it, once someone
writes that rule. The second cannot be caught by any rule, because the defect is
the **absence** of a call in a function whose caller holds payments scope. That
is the boundary generation 3 exists to cross, and it is why the answer is
"both" rather than "the newer one"."""),
  ("md", """## 6 · An agent drives both, because you cannot afford to run both everywhere

Generation 2 is cheap enough to run over the whole repository. Generation 3 is
not — at four million lines the model pass costs more than the finding is
worth, and a model asked to review everything reviews nothing carefully.

So neither generation is the interesting part. **The allocation is.** An agent
sits above both, and its policy is three rules:

1. run the deterministic scanner everywhere, with the widest ruleset that is
   not noisy, because it is nearly free;
2. spend the model pass only where stage 1 said risk lives **and** the rules
   were silent — silence in a high-risk zone is the signal, not the noise;
3. mark everything the model says as a hypothesis, never a finding, because
   stages 8 to 12 are what turn one into the other."""),
  *skill_steps('appsec/sast-generation-comparison',
               '## 2 · The stage, as a skill\n\nThree generations of analysis over the same CyberTravels code, and they fail differently: grep flags the safe queries, taint finds the real flows and nothing in `authz.py`, and the model finds the authorization defect that has no syntactic signature — along with the hallucination that is the price of it. The skill runs all three and reports precision, recall and that last column.'),
],
 "expect": "Grep produces 6 findings at 50% precision, flagging the parameterised "
           "query, the constant insert and the safe subprocess call. Taint rules "
           "find exactly the 3 real injection bugs at 100% precision and recall "
           "and find nothing in `authz.py`. The model finds the authorization bug "
           "at 0.82 confidence and hallucinates one SQL injection at 0.41. The "
           "audit agent then runs the rules everywhere and spends the model pass "
           "on one file of four — the one where history says risk lives and the "
           "rules were silent — emitting 4 findings with zero false positives, "
           "every model finding marked as a hypothesis. The last cell shows what "
           "the allocation costs when it loses: give `authz.py` no history and "
           "the authorization bug is never reviewed.",
 "challenge": "Two things, and the second is the one people skip. Point the "
              "stand-in at a real GLM-4.6 or Kimi K2 through Ollama and run it on "
              "`authz.py` ten times — the variance in what it reports, and in its "
              "confidence, decides whether you can gate on confidence at all. "
              "Then run Semgrep against one of your own repositories at your "
              "current ruleset and at seven packs, and count the difference. "
              "Whatever that number is, it has been the number all year.",
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
],
 "expect": "The call graph identifies three entry points, one of which uses "
           "dynamic dispatch. `load_report` is reachable, `debug_dump` and "
           "`legacy_export` are unknown rather than unreachable because runtime "
           "handler resolution cannot be ruled out. Two-bucket filtering silently "
           "drops both, and the three-bucket routing sends the unknowns to Phase 4 "
           "instead of paging or discarding them.",
 "challenge": "Count how many `unknown` cases your own reachability analysis "
              "produces, and find out what your tooling does with them. If it "
              "reports them as clean, the number of real bugs you are dropping is "
              "the size of that bucket.",
},
}
