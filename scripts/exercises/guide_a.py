"""The Function A course guide — the teaching notes only.

**Two readers, one page.** Somebody working through Function A on their own,
and somebody running it for a room. The page was written for the second alone
and renamed for both, which is a content change rather than a title change:
instructions addressed to a trainer ("project the component table", "run this
as a demo") are useless to a solo learner and were the bulk of several labs.

So each lab holds two lists. `notes` is what both readers need — predict
before you run, what the output means, which bug this really was. `teach` is
the room-only half, rendered in its own labelled block so a solo reader can
skip it and a trainer can find it. The same split runs through the pre-work,
the pitfalls and the capstone.

**What is in here and what is not.** This file holds what a reader needs and
the tree cannot know: the Claude prompt for each lab, what to say in the
debrief, the quick-check questions. Everything else on the generated page —
lesson titles, Risk, Control, the lab line, how many lessons there are, the
counts inside the expected outputs, the reading volume — is read from
`curriculum.json`, from `cybertravels/`, or by calling the skill's own
functions.

That split exists because of a specific failure. A hand-written draft of this
guide reached review with three numbers already stale: it said fifteen lessons
when there were sixteen, "seven to nine components" after A1.0 had settled on
nine, and A2.4's output accuracy at 0.600 after the scorer was corrected to
0.400. This page is read by somebody standing in front of a class or working
alone with nobody to correct them, so a stale number here is worse than a
stale number in a design document.

`build_guide.py --check` is the gate: it fails if a lab here names a lesson the
curriculum does not carry, if a Function A lesson has no lab entry, or if the
committed page has drifted from this source.
"""

# ------------------------------------------------------------------ the course

COURSE = {
 "duration": "about four hours taught",
 "audience": "Anyone new to cybersecurity — career changers, developers, "
             "analysts, students. No security background is assumed.",
 "prereq": "A computer and a Claude account. Reading Python helps from Module "
           "1 on; writing it is not required.",
 "solo": "Work through it in order, one module per sitting if four hours in "
         "one go is too much. The module boundaries are the natural stopping "
         "points: each one ends with something printed that you can look at.",
 "room": "1 trainer per ~15 learners, working in pairs — one driver prompts "
         "Claude, one checker compares the output against this page.",
 "board": "The model proposes, your code decides",
 "short": "Keep Modules 0, 1 and 4 whole. A1.5–A1.7 can be read rather than "
          "run, and A2.0–A2.4 collapse into one pass at the question \"what "
          "would an investigator ask?\". Do not cut the capstone: it is the "
          "only part that shows whether anything stuck.",
 "short_room": "Run A1.5–A1.7 as a single 15-minute demo from your machine, "
               "and teach A2.0–A2.4 as one 20-minute discussion rather than "
               "five labs.",
}

# The six outcomes. `proves` names the lessons that evidence each one, and the
# generator checks every id against the curriculum.
OUTCOMES = [
 ("Name the nine parts of an agent and point to the file each lives in",
  ["A0.1", "A2.5"], "Your own guess sheet, ticked against the finished tree"),
 ("Explain the core security idea: the model proposes, your code decides",
  ["A1.1"], "You can say why a verifier must not be the model"),
 ("Demonstrate five controls with real output",
  ["A1.1", "A1.4", "A1.5", "A1.6", "A1.7"],
  "Five printed refusals or labels, not five claims"),
 ("Put the four investigation questions to an audit record, and say which fails",
  ["A2.2"], "The question-4 answer naming the retrieved document"),
 ("Read an evaluation score critically — denominator, matcher, interval, judge",
  ["A2.3", "A2.4"], "Three questions you now ask of any \"90% accurate\""),
 ("State the blast radius of what you built, and hand it to Function B",
  ["A2.5"], "A number, and the map of what each component becomes"),
]

# window, title, lesson ids, what you leave with. The generator checks that
# these cover every Function A lesson exactly once.
MODULES = [
 ("0:00–0:15", "Framing", [],
  "The \"chatbot says, agent does\" distinction"),
 ("0:15–0:45", "Setup and the nine words", ["A0.0", "A0.1"],
  "A working lab, and a nine-word guess sheet"),
 ("0:45–1:50", "Build the agent core",
  ["A1.0", "A1.1", "A1.2", "A1.3", "A1.4"],
  "Trust map, verifier rejection, token refusal"),
 ("1:50–2:00", "Break", [], ""),
 ("2:00–2:45", "Memory, peers, and stopping the loop",
  ["A1.5", "A1.6", "A1.7"],
  "Untrusted label, forged envelope, budget hit"),
 ("2:45–3:40", "Harness engineering",
  ["A2.0", "A2.1", "A2.2", "A2.3", "A2.4"],
  "Audit gaps, eval score with its caveats"),
 ("3:40–3:50", "Break", [], ""),
 ("3:50–4:20", "Capstone and handover", ["A2.5"],
  "Blast radius, marked sheet, three answers"),
]

# Module 0 has no lesson of its own: it is the idea the rest hangs off, and a
# solo reader needs it stated rather than delivered.
FRAMING = [
 "**A chatbot that is wrong says something wrong. An agent that is wrong "
 "does something wrong** — it cancels a booking or moves money. The verb is "
 "the whole difference, and everything in Function A follows from it.",
 "You are going to build the agent first and secure it second, in that order, "
 "because every control in the five functions after this one attaches to a "
 "mechanism you will have written yourself. There is no adversary in Function "
 "A. That is deliberate: you cannot reason about an attack on a system you "
 "cannot describe.",
 "Hold one sentence through all sixteen lessons: **the model proposes, your "
 "code decides.** Most of what follows is the second half of that sentence.",
]

MODULE_INTRO = {
 "Setup and the nine words":
   "You leave this module with Claude running the repo and a written guess for "
   "where each of the nine agent parts lives. Keep the sheet — it is marked in "
   "Module 4, and the difference between your guess and the answer is the "
   "point.",
 "Build the agent core":
   "In 65 minutes you see the four things that sit between a model's "
   "suggestion and a real action: a verifier, a process boundary, an identity "
   "per actor, and one token per action.",
 "Memory, peers, and stopping the loop":
   "The theme is that **untrusted text travels** — into memory, between "
   "agents, and round a loop that never stops. Each lab shows the label or the "
   "limit that contains it.",
 "Harness engineering":
   "The agent works. This module asks whether anyone else could investigate "
   "it, and whether its scores mean anything. Hold one scenario across all "
   "five labs: a traveller disputes a cancellation three weeks later, and the "
   "only log line says `run completed`.",
 "Capstone and handover":
   "You switch from builder to attacker's-eye view, put a number on what your "
   "agent could damage, and prove to yourself what you now know. **The final "
   "tasks are done without Claude, on purpose** — and the lesson page says so "
   "in those words.",
}

# The cast, read from cybertravels/config.py by the generator; this is only the
# "and so" column, which is a teaching judgement rather than a fact in the tree.
CAST_NOTE = {
 "dana":  "books and cancels her own trips. Cannot refund anything",
 "alex":  "runs the platform. Can write bookings, cannot refund",
 "priya": "the only one of the three who may approve a refund",
}

# ------------------------------------------------------------------- the labs
# minutes · key idea · the prompt to paste · what to expect · notes for every
# reader · notes only a trainer needs · the debrief question and its answer.
#
# `expect` and the notes may contain {placeholders} the generator fills from
# the tree. Any placeholder it cannot fill is an error rather than a silent
# gap, which is how a number here stops being able to go stale.
LABS = {
"A0.0": {
 "minutes": 15,
 "idea": "A skill is a written procedure (`SKILL.md`) the model follows. The "
         "document and the instruction are the same bytes, so you can read "
         "exactly what runs.",
 "prompt": "Run scripts/doctor.py and explain each ok / FAIL / -- line to me.\n"
           "Then run scripts/lesson.py A0.0 and tell me exactly what happened.",
 "expect": "The doctor ends with a \"ready\" summary; `--` lines are fine. "
           "`lesson.py` either completes and names the model, or stops with "
           "\"no model configured\". **Both are correct.**",
 "notes": ["**If it stops, that is the lesson, not a failure.** The program "
           "refused to invent an answer rather than print something "
           "plausible, and that is the first security behaviour of the day. "
           "Way 3 of every lesson needs no model at all.",
           "**Your operating system matters here and almost nowhere else.** "
           "The page gives Windows and Mac their own lines throughout. On "
           "Windows the command is `python`, not `python3` — typing `python3` "
           "opens the Microsoft Store."],
 "teach": ["Celebrate the stop out loud when a learner's machine produces it. "
           "Left unexplained it reads as a broken repository, and that reader "
           "stops.",
           "Collect the doctor's last line from every learner before the "
           "session if you can — it is the one failure that costs the whole "
           "room time."],
 "debrief": ("Zero contract violations means the answer had the right shape. "
             "Does it mean the answer is right?",
             "No. Shape is not truth."),
},
"A0.1": {
 "minutes": 10,
 "idea": "Each of the nine is a component to a builder and an attack surface "
         "to an attacker.",
 "prompt": "Explain the nine words (harness, memory & state, RAG, MCP, skills, "
           "guardrails,\nevals, A2A, multi-agent) as if to a beginner, one line "
           "each, using a\ntravel-booking example. Do not tell me which files "
           "they live in.",
 "expect": "Nine one-line explanations and no file names. The lesson's own "
           "exercise is six numbered steps on paper, and it tells you to write "
           "a question mark where you have no idea.",
 "notes": ["**You are guessing on purpose.** Six of the nine files do not "
           "exist on your computer yet — `runtime.py`, `memory.py`, "
           "`identity.py`, `observability.py`, `mcp/internal_server.py` and "
           "`a2a/protocol.py` get created across Modules 1–3, by you. There "
           "is nothing to look up, and a wrong guess costs nothing.",
           "**How the nine stack up.** The harness is the agent. Memory, RAG, "
           "MCP and skills feed context in. Guardrails sit on the way out and "
           "are the only one that says no. Evals sit beside it. A2A and "
           "multi-agent are several harnesses at once."],
 "teach": ["Print the guess sheet beforehand: one page, nine blank rows, "
           "columns *word* and *guessed file*. Collect them and hand them "
           "back in Module 4.",
           "Say the \"six of these do not exist yet\" line explicitly. "
           "Without it the room spends ten minutes searching the tree for "
           "files nobody has written."],
 "debrief": ("Every arrow into the harness is a way for text you did not write "
             "to reach the model. Which of the nine worries you most, and why?",
             None),
},
"A1.0": {
 "minutes": 10,
 "idea": "Map the system before arguing about its security. The edges where "
         "trust changes are where every control will go.",
 "prompt": "Run lesson A1.0's checkpoint diff, then draw me a simple diagram "
           "of\nCyberTravels' components and mark which edges cross a trust "
           "boundary.",
 "expect": "**{components} components, {present} present.** {absent} is "
           "absent, and that absence is a finding rather than a gap.",
 "notes": ["**It is not nine components to nine skills**, and the page says "
           "so. One skill covers four of them, and {absent} has none, because "
           "you cannot check a component nobody built.",
           "The lesson's component table names, for each component, the file "
           "you write, the lesson that builds it and the skill that checks "
           "it. It is worth keeping open for the rest of Module 1."],
 "teach": ["Project the component table and leave it up for the whole module. "
           "It is the only place the shape of the build is visible at once."],
 "debrief": ("Why mark a box that doesn't exist?",
             "So nobody later argues about controls for a component nobody "
             "built."),
},
"A1.1": {
 "minutes": 15,
 "idea": "The loop's third stage is the one most systems skip. Plan, act, "
         "verify — with the verifier independent of the model.",
 "prompt": "Open cybertravels/runtime.py, show me _verify_result, and run the "
           "two refund\nchecks from lesson A1.1 (asked 140, got 1400; asked "
           "140, got 140).",
 "expect": "First check prints `asked to refund 140, resource server refunded "
           "1400`. Second prints `None`, which in this function means "
           "*nothing wrong here*.",
 "notes": ["**Predict before you run the \"Your turn\".** Replace "
           "`_verify_result`'s body with `return None` and rerun. The 1400 "
           "refund now passes silently. Nothing errors, no span says anything "
           "is wrong, and **the trace is tidier than before** — a reviewer "
           "reading it sees a clean run. That is what a missing verifier "
           "looks like from the outside."],
 "teach": ["This is the lab to slow down on. If the room only remembers one "
           "thing from four hours, it should be the tidier-trace point."],
 "debrief": ("Why not just ask the model whether its answer was right?",
             "That is a second opinion, not a verification."),
},
"A1.2": {
 "minutes": 15,
 "idea": "A tool called in-process shares the agent's authority, leaving "
         "nowhere to put a check. One resource server per trust domain, each "
         "with its own audience.",
 "prompt": "Install cybertravels/requirements.txt, then print "
           "config.TOOL_POLICY as in\nlesson A1.2 and explain the audience and "
           "HIGH RISK columns.",
 "expect": "{tools} tools: {internal} `mcp:internal`, {vendor} "
           "`mcp:vendor`. {high_risk} marked HIGH RISK — {high_risk_names}.",
 "notes": ["**Starting an MCP server shows a blank cursor and nothing else.** "
           "A1.2 says so explicitly: *\"It will look like nothing happened… "
           "silence means it is running and waiting.\"* Without that line this "
           "is ten minutes of thinking you broke it. Control-C stops it."],
 "teach": ["Have the two servers already running on your machine. The install "
           "step is the most common place a room desynchronises."],
 "debrief": ("A tool's description says read-only. Should you believe it?",
             "No. Annotations are hints, not guarantees, and B1.9 is the "
             "lesson on what that enables."),
},
"A1.3": {
 "minutes": 10,
 "idea": "Three principals in every action: the human who asked, the workload "
         "that acted, and the individual call.",
 "prompt": "Mint Dana's user token and the workflow agent's token as in lesson "
           "A1.3,\ndecode both, and compare them side by side.",
 "expect": "Two different kinds of identity. Dana's token carries exactly one "
           "scope, `agent:invoke` — she may *ask* an agent to act, not act "
           "herself.",
 "notes": ["**Meet the cast here.** Dana, Alex and Priya appear on this page "
           "and in every example to the end of Module 3. The table above is "
           "worth a second read before moving on — A1.4 turns on the "
           "difference between Dana and Priya."],
 "teach": [],
 "debrief": ("Three principals: the human, the workload, the call. Which "
             "question can't you answer if you only log one?", None),
},
"A1.4": {
 "minutes": 15,
 "idea": "A long-lived, all-scope token is one ambiguous sentence from misuse. "
         "Exchange a token per action, keyed to the human's role.",
 "prompt": "Run lesson A1.4's loop that asks for payments:refund as Dana and "
           "then as Priya.\nExplain why the results differ.",
 "expect": "`dana -> REFUSED: role 'traveller' may not delegate "
           "'payments:refund'` and `priya -> minted`.",
 "notes": ["**Where the refusal happened matters more than that it "
           "happened**, and the page lists all three: Dana's request stopped "
           "before the model was asked anything, before any booking was "
           "looked up, and before the payment server was contacted at all. "
           "Two independent things must fail for a refund to go through, and "
           "the second does not depend on the model."],
 "teach": [],
 "debrief": ("Is Dana's refusal a broken button?",
             "No: same code, same request, different person."),
},
"A1.5": {
 "minutes": 15,
 "idea": "Text an agent read becomes a fact it learned, unless the origin "
         "travels with it.",
 "prompt": "Run lesson A1.5's memory example: save the policy sentence and "
           "the\nvendor-document sentence for owner 1, then print the prompt "
           "block for\nowner 1 and owner 2.",
 "expect": "Owner 1 shows `[trusted, origin=policy]` and `[UNTRUSTED, "
           "origin=vendor-document]`. Owner 2 prints `''` — an empty string.",
 "notes": ["**Two things to look at, in this order.** The labels survived the "
           "write, so the two sentences do not arrive with equal weight. And "
           "owner 2's block is empty: same call, different owner, nothing "
           "shared. The page's words — *\"closed here by storage, not by "
           "cleverness.\"*",
           "**Predict before you run the \"Your turn\".** If the origin "
           "column is dropped, what does the model see? Both sentences now "
           "carry equal weight, and nothing errors."],
 "teach": [],
 "debrief": ("Why is the label the control, rather than an instruction telling "
             "the model to ignore untrusted text?",
             "An instruction is a request; a label is structure."),
},
"A1.6": {
 "minutes": 15,
 "idea": "A peer's message read as a colleague's instruction turns one "
         "poisoned document into four compromised agents.",
 "prompt": "Run both experiments in lesson A1.6: tamper with a signed "
           "envelope, then\nforward a message in a loop. Explain each error.",
 "expect": "Experiment 1 raises `A2AError: signature does not match`. "
           "Experiment 2 prints hops 1, 2, 3 — each still carrying `dana` and "
           "`tr-1` — then stops with `hop ceiling reached ({max_hops})`.",
 "notes": ["**Both errors are the result**, which the page says up front: "
           "*\"in both cases, the error message is the result you are looking "
           "for, not a sign something went wrong.\"*",
           "**The \"Your turn\" is a bug that really shipped.** Replace "
           "`forward(...)` with a fresh `envelope(...)` and the hops print 0 "
           "forever — the ceiling never fires. That was the real state of "
           "this code for one release: nothing incremented the counter, so "
           "`MAX_HOPS` was unreachable. Only a test that forwards for real "
           "would have caught it."],
 "teach": [],
 "debrief": ("The error message was the result we wanted. Where else in "
             "security is a refusal the success case?", None),
},
"A1.7": {
 "minutes": 15,
 "idea": "Two ceilings on one loop, failing in opposite directions: a gate "
         "nobody can keep up with, and a budget that spends until somebody "
         "notices.",
 "prompt": "Run lesson A1.7's budget snippet and explain what the final word "
           "it prints means.",
 "expect": "`{max_steps} {max_calls}`, then `{max_calls} tool_calls`. The run "
           "ends *saying which limit it hit* — an unfinished answer that "
           "admits it is unfinished.",
 "notes": ["**The gate, in your browser.** Run `./cybertravels/run.sh`, sign "
           "in as Dana, ask to cancel `CT-4417`. The lesson's steps are "
           "numbered: watch it stop and name the scope it wants, approve "
           "once, then ask again and refuse. Both decisions are recorded — a "
           "gate that only logs the yeses cannot answer *what did it try to "
           "do*.",
           "**Worth sitting with.** At 10 approvals a day a person reads each "
           "one; at 400 they approve the queue. Coverage stays at 100% while "
           "real review falls to zero. That is B3.9, and it is why a human "
           "gate is a control with a capacity rather than a control."],
 "teach": ["Run the browser half from your machine if learner setups are "
           "uneven — it is the one lab that needs the web app running."],
 "debrief": ("{max_calls} calls is a ceiling on the run. What stops all "
             "{max_calls} hitting one traveller's booking?",
             "Nothing yet. That is the per-target ceiling, and it is built in "
             "B3.4."),
},
"A2.0": {
 "minutes": 10,
 "idea": "Measure the gap before building anything.",
 "prompt": "Run the audit-answerability-check skill from lesson A2.0 and show "
           "me which of\nthe three questions the sample log cannot answer.",
 "expect": "`answerable_count: 0` — all {a20_questions} unanswerable. Every "
           "row says `agent-svc`, and there is no motivating input at all.",
 "notes": ["**Two triples, and they are not the same triple.** The three "
           "*capabilities* this chapter builds — a trace, an audit trail, an "
           "evaluation — are not the three *questions* the skill scores. The "
           "skill asks: which human, what motivated it, which hop. It is a "
           "number out of {a20_questions}."],
 "teach": [],
 "debrief": ("Is the agent identity the same as the principal?",
             "No. It answers what ran, never who wanted it."),
},
"A2.1": {
 "minutes": 10,
 "idea": "A trace of only successes hides what is worth alerting on, and a "
         "token pasted into a span is a leaked credential.",
 "prompt": "List the {spans} span kinds in cybertravels/observability.py and "
           "explain why\nstart and done matter.",
 "expect": "**{spans} span kinds**: {span_list}. The four at the edges — "
           "`start`, `error`, `final` and `done` — are the ones a hand-rolled "
           "tracer leaves out, and they are what make a *missing* span "
           "visible.",
 "notes": ["**Four refusal points, four different incidents**, and the page "
           "names all four: `policy` is a control working as designed; "
           "`human` is somebody saying no; `verifier` means the call was "
           "authorised, ran, and came back unacceptable; `resource server` "
           "means a token that should never have existed reached a boundary — "
           "**that is the one that wakes people up**.",
           "**Predict before you run the \"Your turn\".** What happens if the "
           "whole token is logged instead of its claims? The trace gets more "
           "useful, and the credential is now in every log backup."],
 "teach": [],
 "debrief": ("A trace with no `done` span: is that a run still going, or a run "
             "that died?",
             "You cannot tell, which is why the pair exists."),
},
"A2.2": {
 "minutes": 10,
 "idea": "Every audit row must answer four questions: which human, which "
         "workload, which call, and what motivated it. The fourth is almost "
         "always missing.",
 "prompt": "Run the attribution-ledger-check skill from lesson A2.2 and "
           "explain question 4\nin its output.",
 "expect": "4/4 answered, and question 4 reads roughly: *the traveller asked "
           "about a double charge, but `wiki/473` — a retrieved document, "
           "origin `knowledge` — is what triggered the `DELETE`*.",
 "notes": ["**The count changed, and that is the point.** A2.0 scored out of "
           "{a20_questions}; this is out of four. The fourth question — which "
           "call, with its audience and scope — is the one A2.0's three did "
           "not include. It is deliberately the same incident as A2.0, told "
           "by a record designed to answer."],
 "teach": [],
 "debrief": ("Without question 4, how does this incident get closed?",
             "\"The agent misbehaved\", which fixes nothing."),
},
"A2.3": {
 "minutes": 10,
 "idea": "A score needs an interval, cases that fail on the old build, and "
         "protection from dilution.",
 "prompt": "Run the eval-suite-health-check skill from lesson A2.3. Then "
           "explain how adding\n30 easy cases would change the aggregate "
           "score.",
 "expect": "Per-case rates with 95% intervals, for example `INJ-01 0.055 "
           "(0.033, 0.077)`. Then the diluted aggregate, with the build "
           "unchanged and the skill saying so — *\"The build did not change. "
           "The number improved by 60%.\"*",
 "notes": [],
 "teach": [],
 "debrief": ("Conformance versus accuracy: an empty result matches every "
             "schema. Is it correct?", None),
},
"A2.4": {
 "minutes": 15,
 "idea": "Three matchers give three numbers from the same runs. Quote exact "
         "match, with `n`.",
 "prompt": "Run skills/research/agent-eval-scoring/scripts/"
           "agent_eval_scoring.py and explain\nwhy name-only and "
           "order-ignored scores are higher than exact match.",
 "expect": "Exact **{exact}**, name-only **{name_only}**, order-ignored "
           "**{order_ignored}**, `n={n}`. Output accuracy **{accuracy}** — "
           "{correct} correct, {incorrect} incorrect, {unscoreable} "
           "unscoreable.",
 "notes": ["**What each weaker matcher forgives.** Name-only forgives R2, "
           "which refunded 1400 where 140 was owed. Order-ignored forgives "
           "R4, which booked the new seat before releasing the old one so the "
           "traveller held two. **Different failures, hidden by each** — "
           "which is why quoting one of them alone is worse than quoting "
           "neither.",
           "**If you have an older copy of this guide:** output accuracy is "
           "{accuracy}, not 0.600. The scorer previously used substring "
           "matching and scored R2's 1400 as correct, because \"140\" sits "
           "inside \"1400.00\" — the lesson was committing the error it "
           "teaches. It compares numbers as numbers now, and R2 fails both "
           "surfaces."],
 "teach": [],
 "debrief": ("Someone says our agent is 90% accurate. What three things do you "
             "ask?",
             "Accurate on which matcher, over how many runs, and who judged "
             "it?"),
},
"A2.5": {
 "minutes": 10,
 "idea": "Blast radius = what one run can reach × how irreversible its actions "
         "are × how long until a human can stop it.",
 "prompt": "Run the blast-radius-review skill from lesson A2.5 and explain "
           "which actions are\nirreversible and which need human approval.",
 "expect": "A table of actions with reversibility and routing. "
           "{irreversible} are irreversible — {irreversible_names} — and "
           "{external} of those are also external: {external_names}. Those are "
           "the ones routed to human approval.",
 "notes": ["**Nothing in the Function B column is a criticism of what you "
           "built.** It is what the build looks like to somebody who wants it "
           "to fail, which is a different question from whether you built it "
           "well."],
 "teach": ["Say that out loud before showing the handover table. A room that "
           "reads it as a list of their mistakes disengages from Function B "
           "before it starts."],
 "debrief": ("Which number decides how much autonomy this agent can be given?",
             "The blast radius, which is why it is the last thing Function A "
             "produces and the first thing Function B argues with."),
},
}

# What each component becomes in Function B. The generator checks every lesson
# id named here exists.
HANDOVER = [
 ("Ingress accepting traveller text", "B1.2", "prompt injection"),
 ("The vendor MCP server", "B1.3",
  "indirect injection, through a document you fetched"),
 ("Tool descriptions you trusted", "B1.9", "a rug-pull after approval"),
 ("Memory with origin recorded", "B1.4",
  "what happens when the origin is dropped"),
 ("Agent-to-agent envelopes", "B1.7",
  "one injection reaching four agents"),
 ("The per-action token exchange", "B2.3",
  "and systems that log it without enforcing it"),
 ("The human gate", "B3.9", "at four hundred approvals a day"),
 ("The audit trail", "B1.14",
  "and the question it still cannot answer"),
]

CAPSTONE = [
 "**Mark your guess sheet.** Run the A2.5 checkpoint into `work/finished`, "
 "open the folder, and tick each correct guess from Module 0. All nine words "
 "now have a file, and you wrote every one. The guesses you got wrong are the "
 "useful half — write down why you expected it somewhere else.",
 "**One unguided task — pick one.** Make the agent refuse an action it "
 "currently allows and name which of the four refusal points you used. Or "
 "name a tenth word CyberTravels has that the list does not, and its file. Or "
 "cut the blast radius by one irreversible action without turning the feature "
 "off. Claude may be used here, but **you have to explain the result**.",
 "**Three answers, in your own words, without re-reading the pages.** What "
 "can your agent do? What stops it doing something it should not, in the "
 "order a request meets them? What would you look at first if it misbehaved "
 "at 3am?",
]

CAPSTONE_ROOM = [
 "Pairs swap guess sheets and each shares one thing they got wrong and what "
 "they learned from it. The wrong guesses are more interesting than the right "
 "ones and a room will not volunteer them unprompted.",
 "Take the three answers verbally, one pair at a time, against the table "
 "below. Written answers get copied from the pages; spoken ones do not.",
]

QUICK_CHECK = [
 ("In \"the model proposes, your code ___\", what is the missing word?",
  "Decides (or disposes)"),
 ("Why must the verifier not be the model?",
  "A model grading itself is an opinion, not a check"),
 ("Why put tools behind a separate MCP server?",
  "So a check can run outside the agent, and tokens bind to one audience"),
 ("Dana asks for a refund. What stops it, and before what?",
  "The token exchange refuses her role's scope — before the model is asked, "
  "before any booking is read, and before the payment server is contacted"),
 ("What makes a vendor sentence in memory safe to read back?",
  "Its origin label travels with it: `UNTRUSTED, origin=vendor-document`"),
 ("What does a hop ceiling protect against, and what breaks it?",
  "Endless agent-to-agent loops; building a new envelope instead of forwarding "
  "resets the count to zero"),
 ("Which of the four audit questions is usually missing?",
  "What motivated the action — the input and its origin"),
 ("\"90% accurate\": name three things missing from that claim",
  "The matcher, `n`, and judge validation (or the interval)"),
]

CAPSTONE_GUIDE = [
 ("What can it do?",
  "Names the tools, the high-risk ones, and that it acts on behalf of a named "
  "human rather than as itself."),
 ("What stops it?",
  "In order: delegation refused by role → human gate on irreversible actions → "
  "resource server verifies the token → verifier checks the result → budget "
  "stops the loop. An answer that gets the *order* right counts even if a "
  "name is fuzzy; the order is the understanding."),
 ("Where would you look at 3am?",
  "The trace, by trace id. Then the audit rows, starting with any `denied` "
  "span — and which of the four places it was denied, because that alone tells "
  "you whether it is a control working or a credential that should not exist."),
]

PITFALLS = [
 ("Accepting Claude's narration as the result",
  "Find the actual printed output and compare it against this page. This is "
  "the course's own lesson applied to the course, and it is the single "
  "easiest way to come out of four hours having learned nothing.",
  "Make the checker in each pair responsible for exactly this."),
 ("Reading \"no model configured\" as failure",
  "It is the program refusing to make something up. Way 3 of every lesson "
  "needs no model, so an unconfigured machine is not a blocked reader.",
  "Reframe it out loud every time it appears in the room."),
 ("Edits from a \"Your turn\" blocking the next lesson",
  "The run prints `stopped`, not `FAILED`, says the edits are safe, and "
  "offers two choices. Use `--out` for a fresh folder; do not `--force` away "
  "work you wanted to keep.",
  ""),
 ("Rushing past the predictions",
  "The predict-then-run step is where the learning happens — a prediction you "
  "got wrong teaches more than output you expected.",
  "Protect the time even where a lab finishes early."),
 ("Turning it into an attack class",
  "Function A has no adversary by design. An attack question is a Function B "
  "question, and arriving there with a system you can describe is the whole "
  "point of doing this first.",
  "Keep a visible parking lot and put them in it."),
 ("An expected output here not matching the run",
  "Trust the run, not this guide, and correct the source. Every number on "
  "this page is generated from the tree for exactly this reason, but a "
  "prompt's wording can still drift.",
  ""),
]

# Pre-work, split by reader. The solo list is what one person needs before
# starting; the room list is everything that only matters with fifteen people
# and one projector.
PREWORK_SOLO = [
 "Install Git and Python 3.10 or newer, clone the repository, install the "
 "Claude desktop app and sign in.",
 "Run the doctor and read its last line: `python3 scripts/doctor.py`, or "
 "`python scripts\\doctor.py` on Windows. If the summary says ready, you are "
 "ready — `--` lines are optional things that are absent, not faults.",
 "Install the application's own dependencies before Module 1: "
 "`python3 -m pip install -r cybertravels/requirements.txt`. This brings in "
 "PyJWT, which A1.3 and A1.4 need.",
 "Keep paper beside you. Two exercises — the nine-word guess sheet in A0.1 "
 "and the three answers in A2.5 — are deliberately done away from the "
 "machine.",
]

PREWORK_ROOM = {
 "One week before": [
  "Send the setup list above as the session's pre-work, and ask every learner "
  "to reply with the doctor's last line. It is the one failure that costs the "
  "whole room time.",
  "Point under-18 learners at A0.0's age guidance — broadly 13 is the floor "
  "and 18 the default, and between the two a parent or guardian sets the "
  "account up. For a class, one adult account or a local model beats thirty "
  "sign-ups.",
  "Dry-run every lab. Note any output that differs from this page and correct "
  "`scripts/exercises/guide_a.py`.",
 ],
 "Day before": [
  "Confirm `./cybertravels/run.sh` serves `http://127.0.0.1:8000` on your "
  "machine. A1.7's human-gate demo needs it; run it yourself if learner "
  "machines struggle.",
  "Print the nine-word guess sheet: one page, nine blank rows, columns *word* "
  "and *guessed file*.",
  "Record a screen capture of each lab's output as a fallback for learners "
  "whose setup fails.",
 ],
 "In the room": [
  "Projector on the lesson index.",
  "**Pairs, not solo.** One driver prompts Claude, one checker compares "
  "output against this page. Swap each module.",
  "A visible parking lot for questions that belong to Functions B–F.",
 ],
}

FAILURES = [
 ("`python3` opens the Microsoft Store", "Windows uses `python`",
  "`python` or `py -3`"),
 ("`command not found` right after installing", "Old terminal session",
  "Close the terminal and open a new one"),
 ("Python 3.9 or older", "Too old for the repo",
  "Install 3.10+; on Windows tick **Add python.exe to PATH**"),
 ("`import jwt` fails", "PyJWT missing", "`pip install PyJWT`"),
 ("A lesson prints **stopped**", "You edited code in a \"Your turn\"",
  "`--out` a fresh folder to keep the work, or `--force` to reset"),
 ("`main.py does not exist at this checkpoint yet`",
  "Tree from before A1.1", "Run the checkpoint command the message prints"),
 ("The doctor shows `--` lines", "Something optional is absent",
  "Nothing to fix. If the summary says ready, you are ready"),
]

PROMPT_BANK = [
 ("Starting a lesson",
  "Summarise lesson <id>'s Risk, Control and Day 0/1/2 in plain English, under "
  "100 words."),
 ("See what changed",
  "Run scripts/checkpoint.py --at <id> --diff and explain the changed lines "
  "like I'm new to Python."),
 ("Predict before \"Your turn\"",
  "Before you run it: here is my prediction for the Your turn change: "
  "<prediction>. Now run it and tell me if I was right."),
 ("Stuck on an error",
  "Show me the exact error, what it means, and the smallest fix. Don't change "
  "anything else."),
 ("Check understanding",
  "Quiz me with 3 questions on lesson <id>. Don't give answers until I reply."),
 ("Connect to the attack side",
  "Which Function B lesson attacks what I built in <id>, and how, in two "
  "sentences?"),
 ("When something will not run",
  "Run scripts/doctor.py and tell me only the lines that are not ok, with the "
  "fix for my operating system."),
]

GLOSSARY = [
 ("Agent", "Software that plans, calls tools and acts on what it reads"),
 ("Harness", "The loop around the model: context in, tool call out, result back"),
 ("Verifier", "Code, not a model, that checks a result before it is accepted"),
 ("MCP", "Model Context Protocol — a standard way for agents to reach tools"),
 ("Sink", "Somewhere data can do damage"),
 ("Audience (`aud`)", "The one server a token is valid at"),
 ("Scope", "The one permission a token grants"),
 ("Workload identity",
  "A name for a piece of software, e.g. `spiffe://…/agent/workflow`"),
 ("Token exchange",
  "Swapping a user token plus an agent identity for a short, narrow, "
  "per-action token"),
 ("A2A", "Agent-to-agent messaging"),
 ("Span / trace id",
  "One recorded step of a run / the id that joins all of them"),
 ("Canary token",
  "A credential that looks real and that nothing legitimate ever uses"),
 ("Blast radius",
  "What one run can reach and damage before a human can stop it"),
 ("Conformance vs. accuracy",
  "Whether the answer has the right shape vs. whether it is right"),
]

OPENER_PROMPT = """You are my tutor for Cyber Commons Function A. The repo is in my connected folder.
For each lesson I name: (1) explain the Risk and Control in plain English in 3 sentences,
(2) run the lesson's "Do this" steps and checkpoint diff for me and show the real output,
(3) ask me one question to check I understood before moving on.
Never invent output. If a command fails, show me the error and what it means."""

WAYS = [
 ("1 — in your AI agent", "The agent reads the lesson, teaches it, runs the check",
  "No — Claude is the agent", "The default for every lab"),
 ("2 — `scripts/lesson.py <id>`",
  "Runs the lesson, prints a five-heading readback",
  "Yes, or it exits 2 saying \"no model configured\"",
  "Worth doing once in A0.0, to meet that message on purpose"),
 ("3 — `scripts/checkpoint.py --at <id> --diff`",
  "Shows the code this lesson added", "No",
  "Any \"what actually changed?\" question"),
]

ROLE_STARTS = [
 ("architects", "B1.0"), ("AppSec", "C2.0"), ("red team", "D1.0"),
 ("SOC", "E1.0"), ("governance", "F1.0"),
]
