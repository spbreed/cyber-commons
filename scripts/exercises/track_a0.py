"""A0 — the introduction: what this is, who it is for, and how to use it.

The only chapter whose subject is the commons itself rather than the systems the
commons is about. It exists because of one repeated piece of reader feedback:
*nobody could tell what this was for until somebody explained it.* This chapter
is that explanation, written down, so it does not need a person attached.

Five lessons, in the order a new reader needs them:

``A0.1``  who it is for, and the seven sections every lesson is made of
``A0.2``  which of the five functions to read first, by the chair you sit in
``A0.3``  what Day 0, Day 1 and Day 2 mean; how to use the labs and the
          skills; and why every tool named here is one you can install
``A0.4``  how to actually run a lesson, on either of the two free routes
``A0.5``  the four frameworks, and which question each one answers

A0.1 to A0.3 are read. A0.4 is run. A0.5 is a reference you come back to.
"""

from . import diagrams as D
from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"A0.1": {
 "concept": """
This commons has one subject: **security engineering when the thing you are
securing — or the thing doing the securing — is an agent.** Not prompt
engineering, not model training, not a vendor comparison. An agent is software
that plans, calls tools and acts on what it reads, and every part of that
sentence is an attack surface and a control point.

### Who it is for

You will get something out of this if you are one of these five people, and
each one has a whole function written for them:

- **A security architect or a product engineer** who has been asked whether an
  agentic feature is safe to ship, and needs a component map before a control
  list. → Function A.
- **An application security engineer or a penetration tester** who already runs
  SAST, DAST and manual testing, and now has to review code an agent wrote and
  test a system that answers differently each time. → Function B.
- **A red team operator or an AI security researcher** who has to attack a
  system with no fixed response, and report a result that survives being run
  again. → Function C.
- **A SOC analyst, detection engineer or incident responder** whose thresholds
  and playbooks were tuned against a person doing twelve things an hour, and
  who now watches an agent doing fourteen hundred. → Function D.
- **A GRC lead, a risk owner or somebody in the CISO's office** who has to say
  in writing whether the estate is under control, and be right. → Function E.

**Who it is not for.** Anyone looking for jailbreak prompts to paste, a
league table of products, or a certification. Nothing here is a certification;
the framework labels on each lesson are indicative mappings and A0.5 says so
plainly.

**What it assumes.** That you can read a Python function. Not that you can
write one, and not that you have a security background — A0.4 assumes nothing
at all, and every lesson runs on a free host with no install step.

### What a lesson is made of

Every lesson page is the same seven sections in the same order. The order is
the argument, and knowing it is the difference between reading a page and
scanning one.

1. **The hook.** One paragraph, before anything else. It is deliberately *not*
   a summary — it is the consequence of not knowing the lesson, stated as a
   scene. If it makes you want the rest, it worked. If you already know the
   lesson, it is the part you skip.
2. **What this lesson is.** The plain-language paragraph — what it covers, and
   why somebody in a security role needs it — and then the Day 0 / Day 1 /
   Day 2 table. A0.3 defines those three.
3. **The framework.** The idea itself: the concept, a diagram, and in
   Functions D and E one extra line — the *anchor* — saying which part of that
   function's single argument this lesson moves. This section comes before any
   code in every lesson, without exception, because teaching the *how* before
   the *why* is the most common way a good lesson lands badly.
4. **In CyberTravels.** One or two sentences putting the idea in the running
   case study. Every lesson has this, so you are never asked to hold a fresh
   example per page.
5. **The skill.** The `SKILL.md` file, rendered as it exists in the
   repository: frontmatter that tells an agent when to load the procedure, and
   markdown that says what the procedure is. It reads as a checklist for a
   person and as a tool for an agent.
6. **Run it.** One code cell — about twenty lines — followed by **Out**, the
   real recorded output of that cell. Not a pasted transcript: A0.4 explains
   how it is produced and checked on two hosts.
7. **Your turn.** One thing to change and re-run, chosen so the number moves.

Two of those deserve a note now, because they are the ones readers ask about.

**The hook is not the summary.** Section 1 is a scene; section 2 is the
description. A reader who treats the hook as an abstract concludes the lesson
is vague. If you want to know what a lesson contains before committing to it,
read section 2 and the Day table, and ignore section 1 entirely.

**The hook is always CyberTravels.** Every scene in every hook is happening
inside the same company — an agent refunding what it should not, a ticket that
steered a summariser, an alert queue that nobody read. That is why the hooks
accumulate: by Function D you are watching a system you designed in Function A
and attacked in Function C. A0.3 has more on the case study and how to use it.
""",
 "steps": [
  ("md", "## 2 · The page, section by section"),
  ("html", D.table(
    ["on the page", "what it is", "read it when"],
    [["<b>The hook</b>", "A scene inside CyberTravels — the consequence of not "
      "knowing this lesson. Not a summary.",
      "You are deciding whether this matters to you"],
     ["<b>What this lesson is</b>", "The plain description, plus the Day 0 / "
      "Day 1 / Day 2 table.",
      "You want to know what is in it before spending the time"],
     ["<b>The framework</b>", "The concept and its diagram. In Functions D and "
      "E, also the anchor line.",
      "Always. This is the lesson"],
     ["<b>In CyberTravels</b>", "The same idea, in the running case study.",
      "The concept was clear but you cannot picture it"],
     ["<b>The skill</b>", "The <code>SKILL.md</code>, exactly as it exists in "
      "<code>skills/</code>.",
      "You want the procedure rather than the argument"],
     ["<b>Run it, and Out</b>", "One cell, and the real output of running it.",
      "You want the number rather than the claim"],
     ["<b>Your turn</b>", "One change to make, chosen so a number moves.",
      "You have read it and want to know whether you understood it"]],
    caption="The same seven, in the same order, on every lesson page. Three of "
            "them — the framework, CyberTravels, and Out — are the ones that "
            "carry the content; the other four are navigation.")),

  ("md", "## 3 · How long any of this takes\\n\\n"
         "A lesson read is about ten minutes. A lesson read **and run**, with "
         "the challenge attempted, is closer to forty. A chapter is between "
         "four and twenty lessons, so a chapter is an afternoon or a week "
         "depending on which one and how you read it.\\n\\n"
         "Nobody needs all five functions, and A0.2 is the map of which ones "
         "you need. The one thing worth doing before any of it is A0.4 — run "
         "a single lesson end to end, on whichever host you have — because "
         "everything here is claims until one of them executes in front of "
         "you."),

  ("md", "## 4 · What it costs, and what it is\\n\\n"
         "It is free, it is open, and it is not a product. There is no "
         "account, no paid tier, no GPU and no API key on the default path "
         "through every lesson. The scripts are standard library only. A "
         "model is optional in six skills and every one of them falls back to "
         "a labelled offline replay.\\n\\n"
         "It is also incomplete and it says so. Where a lesson has a weak "
         "answer it names the weakness — the open-source data-loss-prevention "
         "row in D1.0 is the clearest example, and it is written as a finding "
         "about the market rather than hidden as a gap in the reading."),
 ],
 "expect": "Nothing runs in this lesson. It is orientation: the audience, the "
           "seven sections of every page, and the difference between the hook "
           "and the description — which is the single thing readers most often "
           "get wrong on a first pass.",
 "challenge": "Open any lesson in a function that is not yours and find all "
              "seven sections on it. If one is missing, that is a build "
              "failure rather than an editorial choice — `check_lessons.py` "
              "enforces every one of them — and it is worth an issue.",
},

"A0.2": {
 "concept": """
The commons is five functions and fourteen chapters. **Nobody reads all of it
in order, and reading it in order is the slowest route for four of the five
audiences.**

The functions are not stages of a course. They are five different jobs done on
the same system, and they were written so that each one stands alone with its
own introduction, its own argument and its own scorecard. What connects them is
CyberTravels: the architecture drawn in Function A is the thing Function C
attacks, Function D watches and Function E reports on.

| function | the job | the chair |
|---|---|---|
| **A** — Securing AI Architectures | draw the system, name its risks, close the controls | architect, product engineer |
| **B** — Security Engineering with AI | put AI into the SDLC you already run, and test agentically | AppSec, penetration tester |
| **C** — Agentic Evaluation and Red Teaming | attack a system with no fixed answer, and report a result that reproduces | red team, AI security research |
| **D** — The Agentic SOC | see it, detect it, understand it, stop it, recover | SOC analyst, detection engineer, IR |
| **E** — Governance and Assurance | measure the estate and say in writing whether it is controlled | GRC, risk, the CISO office |

### Start where your work already is

The rule that works: **start at the function that matches your job, then take
exactly the two lessons from Function A that your function depends on.** Every
function's introduction names them. Reading Function A cover to cover first is
the right route only for the architect.

The one exception is A0.4, which everybody does, because it takes ten minutes
and everything afterwards is a claim until a lesson runs.

### If you are picking for other people

Two paths get asked for repeatedly and neither is a whole function.

**A team that is about to ship an agentic feature** needs the architecture, the
two controls that close the most risks, and the register: A1.0, A1.1, the
identity and ingress chapter, then A1.18. That is a week and it produces a risk
register with a named control per row.

**A leadership audience that has to decide whether to fund any of this** needs
Day 0 rather than Day 1: the introduction of each function, and E1.1. Five
pages, and it produces the argument for the budget rather than the work.
""",
 "steps": [
  ("md", "## 2 · Five chairs, five entry points"),
  ("html", D.table(
    ["if your job is", "start at", "then", "what you have at the end"],
    [["<span>Designing or approving an agentic feature</span>",
      "<b>A1.0</b>", "A1 → A2 → A3, in order",
      "A component map, and a register where every risk names the control "
      "that owns it"],
     ["<span>AppSec, code review, penetration testing</span>",
      "<b>B2.0</b>", "B2 in order; A1.1 and A1.2 when a lesson asks",
      "A pipeline with an AI pass in it, and a measured false-positive rate "
      "for that pass"],
     ["<span>Red teaming or AI security research</span>",
      "<b>C1.0</b>", "C1 in order; A1.2 and A1.3 first for the attack classes",
      "An evaluation that reproduces, and a report a defender can act on"],
     ["<span>Detection, alert triage, incident response</span>",
      "<b>D1.0</b>", "D1 → D2 → D3 → D4 → D5; A1.1 for the component names",
      "Five intervals with a number on each, and the rules that shortened them"],
     ["<span>Governance, risk, compliance, the CISO office</span>",
      "<b>E1.0</b>", "E1.1 next, then E1 → E2 → E3; A0.5 as reference",
      "A control indicator computed from the estate rather than asserted "
      "about it"]],
    caption="Every route is short one thing on purpose: nobody is sent through "
            "another function's argument to reach their own.")),

  ("md", "## 3 · The two questions that decide the order\\n\\n"
         "**Are you building the system, or watching it?** Building is "
         "Functions A and B and they run forward from a design. Watching is "
         "Functions C, D and E and they run backward from something that "
         "happened. Both are real security work and they need different "
         "reading orders, which is why they are not one sequence.\\n\\n"
         "**Do you need the argument or the procedure?** If you need the "
         "argument, read the function introduction and the chapter openers and "
         "stop — that is roughly fifteen pages for the whole commons. If you "
         "need the procedure, the `SKILL.md` in each lesson is it, and you can "
         "run it without reading the lesson at all. A0.3 says how."),

  ("md", "## 4 · Reading it as a team\\n\\n"
         "The functions were written to be split. Two people on different "
         "functions can work the same week and meet on CyberTravels, because "
         "it is the same system in both of their lessons — the agent one of "
         "them is hardening in A3 is the agent the other is writing detections "
         "for in D2.\\n\\n"
         "The place that split goes wrong is the vocabulary. Four different "
         "frameworks are in use across these five functions and they answer "
         "four different questions; a finding filed in the wrong one reaches "
         "nobody. That is what A0.5 is for, and it is worth reading before the "
         "first cross-function conversation rather than after it."),
 ],
 "expect": "Nothing runs in this lesson either. It is the map: five functions, "
           "five entry points, and the two lessons from Function A that each of "
           "the other four depends on.",
 "challenge": "Pick your row in the table above and open the lesson it starts "
              "at. Read only its Day 0 line. If the thing it says goes wrong "
              "is not a thing you recognise, you have picked the wrong row — "
              "and the right one is usually the function whose Day 0 you have "
              "already lived through.",
},

"A0.3": {
 "concept": """
Three conventions run through every lesson. They are the reason the pages are
shaped the way they are, and each one exists because of a specific complaint.

### Day 0, Day 1, Day 2

Every lesson and every function answers the same three questions, in the same
order, in the same words:

| | the question | what a good answer looks like |
|---|---|---|
| **Day 0 — why** | What goes wrong if you do nothing? | A consequence in this lesson's own terms, not a general appeal to risk |
| **Day 1 — how** | What do you actually build or run? | The concrete thing: a rule, a map, a gate, a score |
| **Day 2 — measure** | What number tells you it worked? | A number this lesson produces — a recall figure, a false-positive rate, an interval in minutes |

These are **not** a maturity model and they are not a timeline. Day 0 is not
"first week". They are three questions a practitioner asks before reading
anything, and the commons was illegible until it answered them on every page.

Day 2 is the one that is easy to fake, and the only one a sceptical reader
believes. Where a lesson genuinely produces a number, Day 2 names that number.
Where it does not — an orientation lesson produces nothing — Day 2 says what
you count instead, and does not pretend.

Use them like this: **Day 0 decides whether to read the lesson. Day 1 is what
you do. Day 2 is what you put in the update to whoever asked.**

### The labs and the skills

Each lesson's procedure lives in a `SKILL.md` and a script beside it, in
`skills/`. That file is doing two jobs at once, and you can use either.

**As a person**, it is a checklist. Read the markdown, follow it, ignore the
frontmatter. It is written to be followed by hand.

**As an agent's tool**, it is loadable: the frontmatter says when the procedure
applies, so a coding agent with the repository available will pull the right
one at the right time rather than improvising a procedure.

The lab is that skill running. One cell fetches the tree and runs the script as
a subprocess — the script is standard library only and deterministic, so two
runs can be diffed and a changed number means something changed. The recorded
output on the page is a real run, checked byte for byte against the same
notebook run on a second host. A0.4 is the whole mechanism, demonstrated on
itself.

**How to actually use a lab.** Run it once as written and read **Out**. Then do
the *Your turn* section, which always changes one input so a number moves. The
lesson is in the difference between the two numbers, not in either one.

### The hook, and CyberTravels

The first paragraph of every lesson is a scene, and it is always the same
company. **CyberTravels** sells corporate travel; its product is an agentic
platform of four agents — a workflow agent that books and refunds, a retrieval
advisor, a coding agent, and a file-system agent reading vendor documents.
Alex is the product engineer who shipped it.

There is one system in this commons and every lesson is grounded in it. That is
a deliberate cost: a lesson could always find a sharper example of its own idea,
and instead it uses the one you already know. The payoff is cumulative. The
refund limit an attacker walks past in Function A is the refund limit a
detection watches in Function D and the control indicator a report counts in
Function E — one company, one architecture, five jobs done on it.

So the hook is not decoration and it is not a summary. It is that lesson's idea
happening to CyberTravels before it is named. If you want the summary, the
section under it is the summary.
""",
 "steps": [
  ("md", "## 2 · Open source first, and then buy something"),
  ("md", "Every tool named in this commons is one you can install today without "
         "a purchase order. That is a teaching decision before it is a "
         "budget one.\\n\\n"
         "**You cannot specify a product you have not built a bad version of.** "
         "A team that has stood up Wazuh and OpenSearch, written twenty Sigma "
         "rules and watched them fire on their own traffic can walk into a "
         "vendor conversation and ask the two questions that matter: what does "
         "this do that my rules do not, and what does it cost to keep it true. "
         "A team that has not can only compare feature lists — and a feature "
         "list is written by the seller.\\n\\n"
         "The second reason is that **the gaps are the finding**. Building the "
         "open-source version of a control tells you exactly where it stops. "
         "D1.0 names two of those out loud: there is no open-source data-loss "
         "prevention with the maturity of the other sensors, and *no product in "
         "the list at all* can tell you which prompt caused a file write. "
         "Neither of those is visible from a datasheet. Both are the reason to "
         "buy — or to build — and now you can say which."),
  ("html", D.table(
    ["what you need", "learn it on", "buy when"],
    [["Endpoint and workload sensing",
      "<b>Wazuh</b> — agent, manager, indexer",
      "Estate size or support obligations outgrow what you can operate"],
     ["Somewhere for telemetry to land",
      "<b>OpenSearch</b>, or the Wazuh indexer",
      "Retention and query cost stop being a tuning problem"],
     ["Portable, reviewable detections",
      "<b>Sigma</b>, mapped to <b>ATT&amp;CK</b> and <b>ATLAS</b>",
      "Almost never — the rules outlive the platform, which is the point"],
     ["Static analysis in the pipeline",
      "<b>Semgrep</b>, with the reasoning pass from B2.3",
      "Language coverage or triage volume is the constraint"],
     ["Dependency and image inspection",
      "<b>Trivy</b>, <b>Syft</b>, <b>Grype</b>",
      "You need attestation and provenance rather than a scan"],
     ["Threat intelligence and cases",
      "<b>MISP</b>, <b>OpenCTI</b>, <b>TheHive</b>",
      "Intelligence you cannot source yourself is the gap"],
     ["Orchestration and forensics",
      "<b>Shuffle</b>, <b>Velociraptor</b>",
      "Response time is bounded by people rather than by tooling"]],
    caption="The right-hand column is the one to argue about. A control you "
            "have never operated has no 'buy when' — it has a demo.")),

  ("md", "## 3 · Where each convention is defined\\n\\n"
         "So you do not have to hold this page in your head:\\n\\n"
         "- **Day 0/1/2** — on every lesson, in the table under *What this "
         "lesson is*; per function, in that function's introduction "
         "(A1.0, B2.0, C1.0, D1.0, E1.0).\\n"
         "- **The labs and the skills** — the mechanism is A0.4, demonstrated "
         "by running a real lesson's procedure three times, twice in the ways "
         "it breaks.\\n"
         "- **CyberTravels** — the architecture is A1.1, and the risk register "
         "every function counts against is A1.18.\\n"
         "- **The framework labels** on each page — A0.5, which says which of "
         "four questions each framework answers, and that the mappings are "
         "indicative rather than a certification.\\n\\n"
         "One thing that is *not* a convention, and gets read as one: the "
         "**anchor** line in Functions D and E. Those two functions are single "
         "arguments rather than collections — an interval between an agent "
         "acting and the control being back at target (D1.0), and a control "
         "indicator computed from the estate (E1.1) — so every other lesson in "
         "them says in one line which part of that argument it moves. The other "
         "three functions have no anchor because they are not shaped that way."),
 ],
 "expect": "Nothing runs here. Three conventions, defined once: the three "
           "questions every page answers, what to do with a skill and a lab, "
           "and why every tool named in this commons is one you can install "
           "before you can buy one.",
 "challenge": "Take the Day 2 line of any lesson in your function and try to "
              "write the same sentence about a control you already run. If you "
              "cannot name the number, that control is a Day 1 you never "
              "finished — and that gap is usually worth more than the lesson.",
},

"A0.4": {
 "concept": """
Every lesson in this commons is three things, and only the first of them is on
the page you are reading.

**The lesson** — the hook, the framework, the idea. Prose and a diagram. This
is the part that is read.

**The skill** — a `SKILL.md` in [`skills/`](https://github.com/spbreed/cyber-commons/tree/claude/vulnbench-setup-scheduling-81aqov/skills):
YAML frontmatter that tells an agent *when* to load the procedure, and markdown
that says *what the procedure is*. It is written for an agent and it reads
perfectly well as a checklist for a person. 120 of them.

**The script** — the executable half of the same skill, in
`skills/<area>/<name>/scripts/`. Standard library only, deterministic, and it
runs against a synthetic CyberTravels estate so two runs can be diffed.

The notebook holds **none** of those. It holds one cell, about twenty lines,
that finds the skills tree — cloning it if it is not already there — and runs
the script as a subprocess. That is deliberate and it is the reason the code
in front of you is short: a fix to a procedure is one edit to one file, not a
rebuild of 120 notebooks each carrying its own copy. Before this arrangement
existed the notebooks held 34,112 lines of code, 9,730 of them identical
copies of the same parser. They now hold 2,373.

The consequence you have to know about is that **a lesson has a dependency it
does not show you**. On your own machine the tree is simply there, because you
cloned the repository to get the notebook. On a hosted kernel it is not, and
the cell fetches it — which needs the kernel's network switched on. That is one
checkbox, and it is the only prerequisite in this whole commons that anybody
gets stuck on.

So there are two routes, and they differ in exactly one respect:

- **GitHub** — clone once, run any lesson, nothing to configure. The tree is
  already on disk, so no lesson fetches anything and no lesson needs a network.
- **Kaggle** — nothing to install, a free CPU kernel, and the notebook fetches
  the tree on first run. Needs **Internet on** in the notebook's settings panel,
  which Kaggle gates behind a verified phone number.

Neither needs a paid account, a GPU, a model, or an API key. A model is
optional everywhere: six skills call one, and all six fall back to a
labelled offline replay when no backend is configured, so the default path
through all 120 lessons is free and offline. [MODELS.md](https://github.com/spbreed/cyber-commons/blob/claude/vulnbench-setup-scheduling-81aqov/MODELS.md)
has the open-weight setup if you want the real thing.
""",
 "steps": [
  ("md", "## 2 · What you need, and what you do not"),
  ("html", D.table(
    ["you need", "for what", "cost"],
    [["A browser", "reading all 120 lessons, and the recorded output of every one",
      "free"],
     ["<span>A Kaggle account, <b>Internet on</b> in notebook settings</span>",
      "running a lesson on a hosted CPU kernel, nothing installed",
      "free · needs a verified phone number"],
     ["<span>Or: <code>git</code> and Python 3.11</span>",
      "running any lesson locally", "free"],
     ["An OpenAI-compatible endpoint", "the six skills that call a model, "
      "against a real model instead of the replay", "optional"]],
    caption="There is no fifth row. No GPU, no paid API, no framework, no "
            "install step — every script is standard library only.")),

  ("md", "## 3 · Route one — GitHub\\n\\n"
         "Clone it, run it. `run_notebooks.py` executes a lesson's cells "
         "headless and writes what it printed, which is the same thing CI does "
         "for all 120 before anything ships.\\n\\n"
         "```bash\\n"
         "git clone https://github.com/spbreed/cyber-commons\\n"
         "cd cyber-commons\\n"
         "python3 scripts/run_notebooks.py --session A0.4   # this lesson\\n"
         "python3 scripts/run_notebooks.py                  # or all 120\\n"
         "```\\n\\n"
         "Or open `labs/notebooks/A0.4.ipynb` in Jupyter and run the cells. "
         "Because the tree is already on disk, nothing is fetched and the "
         "lesson runs with the network off.\\n\\n"
         "To run a skill without a notebook at all — which is what the "
         "notebook does anyway:\\n\\n"
         "```bash\\n"
         "PYTHONPATH=skills/_runtime python3 "
         "skills/programme/lesson-preflight/scripts/lesson_preflight.py\\n"
         "```"),

  ("md", "## 4 · Route two — Kaggle\\n\\n"
         "Every lesson page carries a **Run on Kaggle** button. It opens the "
         "notebook on a free CPU kernel with nothing installed.\\n\\n"
         "1. Open the lesson page and press **Run on Kaggle**.\\n"
         "2. In the settings panel on the right, switch **Internet** to *on*. "
         "Kaggle only offers that toggle once the account has a verified phone "
         "number — Settings → Phone Verification, and it takes a minute.\\n"
         "3. Run the cell.\\n\\n"
         "The first run spends about three seconds on the fetch: a shallow, "
         "blobless, sparse clone that takes the `skills` directory and neither "
         "the history nor the other 119 notebooks. Every run after that is "
         "instant.\\n\\n"
         "**If phone verification is not available to you**, the same tree is "
         "published as the Kaggle dataset `cybercommons/cyber-commons-skills`. "
         "Attach it in the same settings panel and the cell finds it at the "
         "mount point instead of fetching anything. The failure message in the "
         "cell says so too, because being told at the point of failure is worth "
         "more than being told here."),

  ("md", "## 5 · Reading a lesson page\\n\\n"
         "Every lesson page shows the output of a real run — not a transcript "
         "somebody pasted. `run_notebooks.py` executes the notebook here and "
         "records what it printed; `kaggle_verify.py` then pushes the same "
         "notebook to Kaggle, runs it there, and compares the two byte for "
         "byte. All 120 currently match. So the block on the page under **Out** "
         "is what you will get, and if you get something else, one of us has a "
         "bug worth reporting."),

  *skill_steps("programme/lesson-preflight",
               "## 6 \u00b7 The whole mechanism, demonstrated on itself\\n\\n"
               "The rest of this lesson is the mechanism running. The skill "
               "below is a preflight: it inventories the tree this host "
               "fetched, then runs a real lesson's procedure three times \u2014 "
               "twice in the two ways it actually breaks, once correctly.\\n\\n"
               "The two failures are the two you will meet. **(a)** is a host "
               "with no network and nothing fetched. **(b)** is a tree that "
               "arrived but a shared library that is not on the import path: "
               "some skills import the runtime rather than carrying a copy, "
               "and the lesson cell is what puts it there.\\n\\n"
               "Every number below is counted from the tree that was actually "
               "fetched rather than written into this page \u2014 which is why "
               "they move as the commons grows, and why a count printed here "
               "would be stale by the time you read it.\\n\\n"
               "The procedure it runs correctly in **(c)** is A1.2's, the next "
               "executable lesson after this one, so what you see below is "
               "literally the next page's output."),
 ],
 "expect": "The tree, inventoried from disk rather than asserted \u2014 14 "
           "areas and 120 skills, 119 of them with a script, at the time of "
           "writing; it is a count of what was fetched, so it grows as the "
           "commons does. Then "
           "the same procedure failing twice and working once — exit 2 with "
           "`[Errno 2]` when nothing was fetched, exit 1 with "
           "`ModuleNotFoundError` when the runtime is off the path, and exit "
           "0 with twelve lines and a CRC when both conditions hold. `ready` "
           "is true only because both failures were reproduced; a preflight "
           "that shows only the success has tested one path in three.",
 "challenge": "Run it on the other route. If you read this on Kaggle, clone "
              "the repository and run the same command locally; if you read it "
              "locally, press **Run on Kaggle**. Compare the CRC on the last "
              "line — it should be identical, because the procedure is the "
              "same file in both cases. If it is not, you have found either a "
              "non-determinism in the procedure or a difference between the "
              "hosts, and both are worth an issue.",
},

}
