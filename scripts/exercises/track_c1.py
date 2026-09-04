"""C1 — The Pentester / Red Teamer. Five sessions.

    C1.0  what AI security research means, and the standard of proof it holds to
    C1.1  the offensive workflow, and the containment that makes it lawful
    C1.2  red-teaming an agent: one campaign across all three surfaces
    C1.3  attacking evaluation itself
    C1.4  reporting agentic findings so they get fixed

Every attack in this track is fired at a *defence you build in the notebook*.
Nothing here targets a third party, and nothing needs a network.
"""

MODEL_NOTE = """
> **About the model in this notebook.** It runs offline against a deterministic
> replay so the lesson executes on a Kaggle kernel with no network. The replay
> is not a language model and is labelled as such. To run the same harness
> against a real open-weight model:
>
> ```bash
> ollama pull glm-4.6            # or kimi-k2, llama3.3
> export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
> ```
"""

from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"C1.1": {
 "concept": """
Penetration testing has always been a loop: **recon → hypothesis → test →
escalate → report.** What has changed is who runs each turn.

**Manual (still the baseline).** A human runs `nmap`, reads the output, forms a
hypothesis, tries it. Slow, and the quality is entirely the tester's.

**Scripted.** The recon is automated — Nuclei templates, a Burp scan. The
hypothesis and the escalation are still human. This is where most teams are.

**Semi-autonomous.** An open-weight model reads the recon output and *proposes*
which findings are worth chasing and what to try next. The human approves each
action. The gain is triage speed on a large surface: 400 findings ranked in
minutes rather than a day.

**Autonomous.** The model proposes and the harness executes, within a
pre-approved scope and tool set, verifying its own results. This is real and it
works, and it is also where the engagement becomes a safety problem — because an
agent that has not understood the scope will happily test something outside it
at machine speed.

The professional obligations do not change with autonomy. They get harder,
because scope enforcement can no longer live in the tester's attention — it has
to live in the harness, and then underneath the harness in the network.

That second half is why containment belongs in this lesson rather than in a
later one. An offensive harness has a property no other agent has: **everything
it reads is hostile by design.** Banner strings, error bodies, file contents —
all of it comes from a system you are attacking, which may itself already be
attacker-controlled. Containment there protects three parties at once: the
client (scope and rate limits, so you do not break their production), everyone
else (egress control, so a compromised harness cannot pivot outward), and you
(findings and client data must not leave by a route the agent chooses).
""",
 "steps": [
("md", "## 2 · Demo — the four generations on the same recon output\n\n"
         "Realistic scan output from an authorised engagement against hosts you "
         "own. The question at every generation is the same: what do I chase first?"),
("md", "## 3 · Where it breaks — generation 4, and the scope problem\n\n"
         "The model's top-ranked item is correct. Its reasoning on F-06 is also "
         "correct — *out of scope, do not touch*. Now make it autonomous and "
         "remove the human from the loop. What stops it acting on a finding it "
         "has correctly identified as out of scope?\n\n"
         "Nothing in the model. Its judgement about scope is a *proposal*, on the "
         "decision plane, exactly like everything else it produces."),

  ("md", "## 5 · The control — and the layer underneath it\\n\\n"
         "The scope check above lives in the harness, which is one process away "
         "from the loop it constrains. On an engagement a single control is a "
         "single point of failure, and the failure is a professional incident. "
         "The same rule therefore gets restated where the agent cannot reach it: "
         "the sandbox's own request path."),
  *skill_steps('redteam/offensive-agent-containment',
               "## 2 · The procedure, as a skill\n\nModel triage beats severity sorting on CyberTravels' findings and correctly calls the partner CDN out of scope — and can be argued into calling it critical. The skill runs both, then re-runs with scope enforced outside the model, where the persuaded model still proposes the call and nothing acts on it."),
],
 "expect": "Severity sorting puts 2 of 3 exploitable findings in the top 3; model "
           "triage puts 3 of 3, and correctly reasons that the partner CDN is out "
           "of scope. With the model adversarially convinced that the "
           "out-of-scope host is critical, the unenforced harness acts on it and "
           "the enforced harness refuses. Underneath the harness the sandbox "
           "refuses three requests for three different reasons — rate limit, "
           "engagement boundary, and cloud metadata — without consulting the model "
           "at all.",
 "challenge": "Write your engagement scope as a data structure your harness reads, "
              "not as a paragraph in a PDF. Then ask what your current tooling "
              "would do if a target redirected to a host you were not authorised "
              "to touch.",
},

"C1.2": {
 "concept": """
An agent has three attack surfaces, and a red-team engagement has to cover all
three: **injection** (what it reads), **identity** (who it acts as), and
**containment** (what it can reach). What makes the engagement a campaign rather
than a demo is that all three are scored the same way.

So abandon the question "can this chatbot be jailbroken?" — which is
unfalsifiable and always yes — and replace it with one you can put a number on:

> **What fraction of a defined attack suite reaches a privileged tool?**

That is attack success rate (ASR). It is measurable, comparable between builds,
and it goes down when you fix something. Injection is the worked example below
because it is the surface people get wrong most often; the last section runs the
identical scoring across all three.

The suite has to contain two categories that teams usually omit:

- **Keyword-free attacks.** Payloads with none of the vocabulary a filter looks
  for. These are the ones that get through, and they are easy to write.
- **Benign controls.** Ordinary security discussion that *contains* alarming
  words. If your defence flags these, it is not safe, it is unusable — and
  measuring only ASR will never tell you.
""",
 "steps": [
  ("md", "## 2 · Demo — a suite with both categories"),
("md", "## 3 · Demo — score three defences, on both axes"),
("md", "## 4 · Where it breaks — reading the keyword row honestly\n\n"
         "The keyword filter blocks the two loud attacks and lets all four quiet "
         "ones through, so ASR is 0.67. Worse, it fires on two of the four benign "
         "cases — ordinary security writing. A defence with 67% ASR *and* a 50% "
         "false-alarm rate on legitimate traffic is not a partial win; it is "
         "strictly worse than nothing, because it costs trust while providing "
         "little.\n\n"
         "Provenance blocks everything at 0.00 ASR with no false alarms — which "
         "should make you suspicious. A perfect score usually means the suite is "
         "not testing the right thing."),
("md", "## 6 · The same scoring across all three surfaces\\n\\n"
         "Injection was the worked example. Identity and containment are scored "
         "with the same two numbers, against the same criterion, and the campaign "
         "report is one table — because a defender needs to know which surface "
         "buys the most, not which one you found most interesting."),
  *skill_steps('redteam/attack-success-rate-campaign',
               '## 2 · The procedure, as a skill\n\nA block rate with no false-alarm rate is half a measurement. The skill runs a fixed suite against each defence, counts what each does to benign security writing, and then delivers the payload through the channel provenance trusts by construction.'),
],
 "expect": "No defence gives ASR 1.00. The keyword filter gives ASR 0.67 with "
           "false alarms on 2 of 4 benign security-writing cases. Provenance "
           "gives ASR 0.00 with no false alarms — until the payload is delivered "
           "through the principal channel, where ASR returns to 1.00. The same "
           "two numbers then score all three surfaces in one table.",
 "challenge": "Run the campaign on all three surfaces against one agent you own, "
              "and publish the table rather than the best finding. Start with the "
              "list of channels your agent treats as principal-supplied: task "
              "descriptions, ticket titles and chat messages usually qualify, and "
              "a much wider group can write into them than you expect.",
},

"C1.3": {
 "concept": """
If you can make a harness score well without being good, so can the vendor whose
benchmark you are reading — and so can your own team, without meaning to.

Three exploits work on almost every published security-harness result:

1. **Report conformance as quality.** Schema validity is ~100% by construction
   with structured output. It measures nothing about correctness (B2.1).
2. **Exploit class imbalance.** If 80% of a corpus is one CWE, always guessing
   that CWE scores 0.8 with no capability at all.
3. **Exploit basename collisions.** If the matcher compares bare filenames and
   the corpus reuses `1.py` across directories, scores become partly random —
   and random noise on a leaderboard looks like a small improvement.

Red-teaming evaluation means running these three against your own numbers before
someone else does.
""",
 "steps": [
  ("md", "## 2 · Demo — build a harness with zero capability"),
("md", "## 3 · Exploit 2 and 3 — balance the corpus, then break the matcher"),
("md", "## 4 · The control — a benchmark checklist you run on yourself"),
  *skill_steps('redteam/eval-corpus-integrity-check',
               '## 2 · The procedure, as a skill\n\nBefore believing an evaluation, score a harness with no capability at all. The skill does exactly that against the skewed corpus, then rebalances and re-scores — and separately checks whether the matcher rewards answers naming the wrong directory.'),
],
 "expect": "On the skewed corpus the zero-capability harness scores conformance "
           "1.00 and expert accuracy around 0.85. Balancing the corpus drops "
           "expert accuracy to roughly 0.25. Answers naming the wrong directory "
           "score near zero under `path_key` and near 1.00 under a basename "
           "matcher. The audit reports the majority-class share, the trivial "
           "baseline, the matcher collisions, and near-zero lift.",
 "challenge": "Run the audit against a benchmark result your organisation "
              "relies on. Two questions decide it: what does always guessing the "
              "majority class score, and does the matcher collide? Most published "
              "numbers answer neither.",
},

"C1.4": {
 "concept": """
Agentic findings fail in review for a predictable reason: they describe a clever
prompt instead of a broken control.

A defender reading "the agent can be made to approve a PR by putting a comment
in the diff" reasonably concludes that the fix is to filter that comment. They
ship the filter, the finding closes, and the class recurs with different wording
next quarter — because the actual defect was that content could drive a
privileged tool at all.

A report that gets fixed properly has five parts, and two of them are unusual:

1. **Reproduction** the defender can run on their own build.
2. **Observed** — what actually happened, not what could happen.
3. **Missing control** — the thing that should have existed.
4. **Not a fix** — pre-empting the reviewer's first instinct, explicitly.
5. **Proof of fix** — a regression case that fails on the current build and
   passes on the fixed one.

Parts 4 and 5 are what stop the finding from being closed cosmetically.
""",
 "steps": [
  ("md", "## 2 · Demo — the same finding, written two ways"),
("md", "## 3 · The proof-of-fix clause, demonstrated\n\n"
         "This is the part that makes the report checkable rather than "
         "persuasive. Build both versions and show the regression case behaving "
         "as the report claims it must."),
("md", "## 4 · Coverage — never let silence read as safety"),
  *skill_steps('redteam/agentic-finding-report',
               '## 2 · The procedure, as a skill\n\nA weak report describes a payload and predicts its own outcome. The skill writes the strong one: the missing control, the fixes that are not fixes, and a regression case verified to fail on the old build and pass on the new one.'),
],
 "expect": "The weak report is shown with its predicted outcome. The strong "
           "report names the missing control, states explicitly what is not a "
           "fix, and specifies a regression case. That case then returns False on "
           "the current build and True on the fixed one, while the principal's "
           "own approval still succeeds. The coverage statement flags "
           "supply-chain as untested.",
 "challenge": "Rewrite your most recently closed agentic finding in this format, "
              "then check whether the fix that shipped satisfies the proof-of-fix "
              "clause. If it only blocks the payload you reported, reopen it.",
},
}
