"""A0 — the introduction. One lesson, and it is about the commons itself.

It exists because of one repeated piece of reader feedback: *nobody could tell
what this was for until somebody explained it.* This lesson is that explanation,
written down, so it does not need a person attached.

It was five lessons for a while — audience, routing, conventions, how to run
one, and the frameworks — and they repeated each other badly: three of the five
explained Day 0/1/2, two explained the personas, and a reader had to open four
pages to learn things that fit on one. They are one page now, and the chapter is
one lesson.
"""

from . import diagrams as D
from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"A0.0": {
 "concept": """
**Start here even if you have never written a line of code.** This lesson
assumes you can use a computer and nothing else. It takes about half an hour,
it costs nothing, and at the end you will have run a real piece of security
work on your own machine.

### What you are about to build, in plain words

An **AI model** is the thing behind a chatbot: you give it words, it gives you
words back. You have almost certainly used one.

This commons is 148 lessons, and every one of them hands a model a **written
procedure** — a page of instructions, in ordinary English, that says how to do
one job in security. Find the weak spot in this code. Work out what an attacker
could reach. Decide whether this alert is real. The model reads those
instructions and does the job.

The written procedures are called **skills**, and they are the point of the
whole thing. You can read every one of them. You can change them and watch the
answer change. There is no hidden part.

So there is exactly one thing you have to set up: **your computer needs to know
which model to ask.** That is all this lesson does.

### Nine words you will meet

You do not need to memorise these. Come back to this table when one of them
turns up and you are not sure.

| word | what it means here |
|---|---|
| **model** | the AI. The thing that reads your words and writes an answer. |
| **prompt** | the words you send it. |
| **token** | roughly three-quarters of a word. Models are measured in these. |
| **context window** | how much the model can hold in its head at once, in tokens. |
| **terminal** | a window where you type commands instead of clicking. Every computer has one. |
| **command** | one line you type into the terminal, then press Enter. |
| **repository** | a folder of files that a whole project lives in. Often shortened to *repo*. |
| **clone** | to copy a repository from the internet onto your computer, in one command. |
| **environment variable** | a setting your terminal remembers, so you do not retype it. |

Two more you will meet only if you choose Route B or C below: an **API key** is
a password that lets your computer talk to somebody else's model, and an
**endpoint** is the web address that model answers on.

### Why this is the first lesson and not an appendix

Nothing here runs without a model. If you skip this and open a later lesson,
the command will stop and print a message instead of doing the work — which is
correct behaviour, and is not your computer being broken. This lesson makes
that message something you have already seen on purpose.

### What you need, and what it costs

Three things: a place to write code, a copy of this repository, and a model that
answers. Only the third one has any real decision in it.

The table below is the honest version of the developer-AI-tool market as it
stands. Two columns matter more than the price. **The context window** is how
much the tool can hold at once — and it is not all yours, because the working
file, the project instructions, the terminal output and the dependencies are all
spending from the same budget. **The free tier** is what you can actually do
without a card.

### A caution about the number in the middle column

A context window is a ceiling, not an allowance. A tool advertising a million
tokens will still lose the thread at a fraction of that, because the window is
shared between your file, the project-root instructions, background command
output and every dependency the agent pulled in. Both Cursor and Claude Code
ship explicit compaction commands for exactly this reason. Treat the figure as
"how much this could hold before it refuses", not "how much it will reason over
well".

The other thing worth knowing before you pick: **flat-rate pricing is mostly
gone.** GitHub Copilot's $10 tier is not unlimited use — it is a baseline of AI
credits that drains faster when you run an agent workflow than when you accept
an autocomplete. Budget by what you run, not by the headline.

### The rule for this lesson

Everything below works on a free tier. You do not need a paid plan to finish
this commons, and if a lesson ever requires one, that is a defect in the lesson.
""",
 "steps": [
  ("md", "## 2 · Pick a tool, against its real numbers\n\n"
         "**You can skim this table.** If you only want to get going, none "
         "of it is required — Route B in the next step but one runs a model "
         "on your own computer for nothing, with no account and no card. The "
         "table is here so that when you *do* choose a paid tool, you choose "
         "it on the two numbers that actually decide it rather than on the "
         "advertising.\n\n"
         "The prices are per month and the free tiers are what you get "
         "without a card. Every name links to its own sign-up page."),
  ("html", D.table(
    ["tool", "free tier", "max context window", "paid, per month"],
    [["<b><a href='https://claude.ai'>Anthropic Claude</a></b> / "
      "<a href='https://console.anthropic.com'>Claude Code</a>",
      "Rolling message caps on the web app, resetting every 5 hours. $5 API "
      "trial credit on phone verification.",
      "<b>1M tokens</b> on paid plans with frontier models; 200k on the free "
      "web plan",
      "$20 Pro · $25 Max · usage-based API"],
     ["<b><a href='https://antigravity.google'>Google Antigravity</a></b>",
      "Perpetual public preview, free. Local orchestration across editor, "
      "terminal and browser.",
      "<b>1M–2M tokens</b> depending on the underlying Gemini model, with "
      "built-in state compression",
      "$0 preview · enterprise seats via Google Cloud"],
     ["<b><a href='https://aistudio.google.com/apikey'>Google AI Studio</a></b>",
      "Free API keys, 60 requests/minute on Gemini Flash, no billing details "
      "required",
      "<b>2M tokens</b> on Gemini Pro models",
      "Pay-as-you-go once the free quota is breached"],
     ["<b><a href='https://build.nvidia.com'>NVIDIA Build</a></b> (NIM)",
      "Free account, no card. One key reaches the whole catalogue of "
      "open-weight models, hosted on NVIDIA's own GPUs. <b>Route C below "
      "walks through it.</b>",
      "Varies by model — the catalogue carries several with 128k and above",
      "Free for development; production via NVIDIA AI Enterprise"],
     ["<b><a href='https://chatgpt.com'>OpenAI ChatGPT</a></b> / "
      "<a href='https://platform.openai.com'>Codex</a>",
      "GPT-4o mini, code execution and data analysis. The legacy $5 API credit "
      "is largely phased out.",
      "128k tokens on standard frontier models; larger on API-only reasoning "
      "tasks",
      "$20 Plus · $200 Pro"],
     ["<b><a href='https://github.com/features/copilot'>GitHub Copilot</a></b>",
      "2,000 completions + 50 chat messages a month. <b>Students get the "
      "premium tier free</b> via the "
      "<a href='https://education.github.com/pack'>Student Developer Pack</a>.",
      "32k–128k, scaled dynamically by which model serves the request",
      "$10 Pro (bundles $15 of AI credits) · $39 Pro+"],
     ["<b><a href='https://cursor.com'>Cursor</a></b>",
      "Hobby: 2,000 completions + 50 slow requests a month. <b>Students get up "
      "to a year of Pro</b> — "
      "<a href='https://cursor.com/students'>cursor.com/students</a>.",
      "128k–200k mapped codebase context; up to 1M with your own API key",
      "$20 Pro · $40 Business"],
     ["<b><a href='https://aws.amazon.com/q/developer/'>Amazon Q Developer</a></b>",
      "50 agentic requests a month + 1,000 lines of code translation",
      "100k+ tokens of indexed codebase, mapped into the IDE panel",
      "$19 per user (Q Pro)"]],
    caption="Every tool name links to its own sign-up page. Free tiers and "
            "context windows as at the time of writing — they move, so check "
            "the terms before you depend on one. If you are a student, start "
            "at the two rows that say so; they are the best value in the table "
            "by a wide margin.")),

  ("md", "## 3 · Open a terminal and get the files\n\n"
         "**First, open a terminal.** It is already on your computer:\n\n"
         "- **Windows** — press the Start button, type `powershell`, open "
         "*Windows PowerShell*.\n"
         "- **macOS** — press Command and the space bar together, type "
         "`terminal`, press Enter.\n"
         "- **Linux** — press Control, Alt and T together.\n\n"
         "A window opens with a blinking cursor. It is waiting for you to type "
         "a line and press Enter. Nothing you type below can damage anything.\n\n"
         "**Second, check two programs are there.** Type each line, press "
         "Enter, and read what comes back:\n\n"
         "```bash\n"
         "git --version          # any 2.x is fine\n"
         "python3 --version      # 3.10 or newer\n"
         "```\n\n"
         "If either says *command not found*, install the missing one — "
         "[git-scm.com/downloads](https://git-scm.com/downloads) and "
         "[python.org/downloads](https://www.python.org/downloads/) — then "
         "close the terminal, open a new one, and check again. A terminal only "
         "notices a new program when it starts.\n\n"
         "**Third, copy this project onto your machine.** The first line "
         "downloads it; the second moves you inside the folder it made, the "
         "way double-clicking a folder moves you inside it:\n\n"
         "```bash\n"
         "git clone --branch master https://github.com/spbreed/cyber-commons.git\n"
         "cd cyber-commons\n"
         "```\n\n"
         "That is the clone. You now have every lesson, every skill and every "
         "line of the example system on your own computer, and none of it "
         "needs the internet again until you ask a hosted model a question.\n\n"
         "There is nothing else to install. Every program here uses only what "
         "comes with Python — the one thing it needs is a model, and that is "
         "the next step.\n\n"
         "## 4 · Tell it which model to ask — three routes, all free\n\n"
         "This is the one step that matters. You are giving your computer the "
         "equivalent of a phone number for a model, so that when a lesson has "
         "a job to do it knows who to call.\n\n"
         "**Read all three, then pick one.** Route A is the shortest and needs "
         "no password at all. Route B keeps everything on your own machine and "
         "never sends a word to anybody. Route C borrows a large model on "
         "somebody else's hardware, free, and is the answer if your computer "
         "is not a powerful one. You can change your mind later by rerunning "
         "one command.\n\n"
         "### Route A — you already have Claude Code, Cursor or Copilot\n\n"
         "**Then you need no API key and no endpoint.** If the `claude` CLI is "
         "installed and signed in, the skill runtime finds it and uses that "
         "session — the same authentication your editor already uses. Nothing "
         "to configure:\n\n"
         "```bash\n"
         "claude --version      # if this prints a version, you are done\n"
         "claude                # run once to sign in, if you have not\n"
         "```\n\n"
         "This is the shortest path and the one to start with. It also matches "
         "how these skills are *meant* to be used: the "
         "[agentskills.io](https://agentskills.io) format exists so an agent "
         "can load a `SKILL.md` and carry out the procedure itself.\n\n"
         "### Route B — a model you run yourself\n\n"
         "[Ollama](https://ollama.com) is the shortest path to a model on your "
         "own machine. Nothing leaves it, and there is no quota:\n\n"
         "```bash\n"
         "curl -fsSL https://ollama.com/install.sh | sh\n"
         "ollama serve &                 # not automatic on every platform\n"
         "ollama pull qwen2.5:1.5b-instruct\n"
         "```\n\n"
         "The cost is your hardware. A 1.5B model answers in seconds on a "
         "laptop and will fill a contract with plausible values it did not "
         "derive; 7B is the size the acceptance criteria in this commons were "
         "established at. If your machine cannot hold that, Route C is the "
         "answer.\n\n"
         "### Route C — NVIDIA's hosted catalogue, on somebody else's GPUs\n\n"
         "A free [NVIDIA](https://build.nvidia.com) account gives you one API "
         "key that reaches a catalogue of open-weight models — 70B and larger "
         "included — running on NVIDIA's GPUs. It speaks the **same "
         "OpenAI-compatible protocol** as Ollama, so it is the same three "
         "variables and not one line of code changes. This is the route to "
         "take if you want a large model and do not have a GPU.\n\n"
         "**Sign up and get a key.** Four steps, no card:\n\n"
         "1. Go to [build.nvidia.com](https://build.nvidia.com) and choose "
         "*Sign in* / *Join*. Creating the account enrols you in the free "
         "[NVIDIA Developer Program](https://developer.nvidia.com/developer-program) "
         "— no company and no payment details.\n"
         "2. Open "
         "[build.nvidia.com/settings/api-keys](https://build.nvidia.com/settings/api-keys) "
         "and generate a personal key. It begins `nvapi-`. **Copy it now** — "
         "the full value is shown once.\n"
         "3. Browse the catalogue and open the model you want. Each model page "
         "carries a code sample, and the string after `model=` on that page is "
         "the exact id to use. They are `publisher/name`, for example "
         "`nvidia/nemotron-3-super-120b-a12b`.\n"
         "4. Allowances are **per model and are not published**, and NVIDIA has "
         "changed the scheme at least once — it was a flat credit count, then "
         "per-model rate limits. Read the current terms on the model's own "
         "page rather than trusting a number in a tutorial, this one included.\n\n"
         "**Call it, and check the key works before you trust it.** One "
         "request, no install — `curl` is enough:\n\n"
         "```bash\n"
         "export NVIDIA_API_KEY=nvapi-...          # your key, from step 2\n"
         "\n"
         "curl -sS https://integrate.api.nvidia.com/v1/chat/completions \\\n"
         "  -H \"Authorization: Bearer $NVIDIA_API_KEY\" \\\n"
         "  -H 'Content-Type: application/json' \\\n"
         "  -d '{\"model\":\"nvidia/nemotron-3-super-120b-a12b\",\n"
         "       \"messages\":[{\"role\":\"user\",\"content\":\"Reply with the "
         "single word: ready\"}],\n"
         "       \"max_tokens\":16}'\n"
         "```\n\n"
         "A JSON reply containing `ready` means the key, the endpoint and the "
         "model id are all correct. A 401 is the key, a 404 is the model id, "
         "and a 429 is the rate limit — three different problems that look "
         "identical if you skip this and go straight to a skill.\n\n"
         "**Then point the commons at it.** The same three variables as any "
         "other route:\n\n"
         "```bash\n"
         "export OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1\n"
         "export OPENAI_API_KEY=$NVIDIA_API_KEY\n"
         "export MODEL=nvidia/nemotron-3-super-120b-a12b\n"
         "```\n\n"
         "**And from your IDE.** Every editor that supports a custom "
         "OpenAI-compatible provider — Cursor, Continue, Cline, Zed, "
         "JetBrains AI — asks for exactly two fields, and you now have both: "
         "the base URL `https://integrate.api.nvidia.com/v1` and the key. Put "
         "the model id in the model field. The editor does not need to know it "
         "is NVIDIA; it is speaking the protocol it already speaks.\n\n"
         "> **The key is a credential.** It goes in your shell profile or your "
         "editor's secret store, never in a file inside this repository and "
         "never in a commit. `check_secrets.py` will stop you, but the habit "
         "is the control and the gate is the backstop.\n\n"
         "### The three settings, for Routes B and C\n\n"
         "These are the environment variables from the word table — three "
         "things your terminal remembers, so every lesson you run afterwards "
         "already knows where to go.\n\n"
         "Typed into a terminal, they last until you close that window. To "
         "make them stick, put the same three lines at the bottom of your "
         "**shell profile**, which is a file your terminal reads every time it "
         "starts: `~/.zshrc` on macOS, `~/.bashrc` on most Linux, and "
         "`$PROFILE` in PowerShell on Windows. Open a new terminal afterwards "
         "to check they took.\n\n"
         "Setting `OPENAI_BASE_URL` **overrides** Route A, because somebody "
         "who set it meant it."),

  ("html", D.table(
    ["variable", "what it is", "example"],
    [["<code>OPENAI_BASE_URL</code>",
      "The chat-completions endpoint. <b>It must end in <code>/v1</code></b> — "
      "leaving it off is the single most common setup error, and it fails with "
      "a 404 that names nothing.",
      "<code>http://127.0.0.1:11434/v1</code>"],
     ["<code>OPENAI_API_KEY</code>",
      "Any non-empty value against a local server. A real key against a hosted "
      "one.",
      "<code>ollama</code>"],
     ["<code>MODEL</code>",
      "Which model to ask for. Must match a name the server actually serves.",
      "<code>qwen2.5:7b-instruct</code>"]],
    caption="One protocol — OpenAI-compatible chat completions — so the same "
            "three variables point at Ollama, llama.cpp, vLLM or a hosted free "
            "tier without a line of code changing.")),

  ("md", "### Either of these works\n\n"
         "```bash\n"
         "# Local, free, offline after the pull, nothing leaves the machine:\n"
         "export OPENAI_BASE_URL=http://127.0.0.1:11434/v1\n"
         "export OPENAI_API_KEY=ollama\n"
         "export MODEL=qwen2.5:7b-instruct\n"
         "\n"
         "# Or a hosted free tier — Google AI Studio gives a key with no card:\n"
         "export OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai\n"
         "export OPENAI_API_KEY=<your AI Studio key>\n"
         "export MODEL=gemini-2.5-flash\n"
         "```\n\n"
         "**Put the key in your shell profile, never in a file inside the "
         "repository.** `scripts/check_secrets.py` runs as a pre-commit hook "
         "and in CI, and it blocks anything credential-shaped from being "
         "committed — but the habit is what protects you, not the gate.\n\n"
         "## 5 · Prove it works — run your first skill"),

  *skill_steps(
    "programme/dev-environment-preflight",
    "Here is your first skill. Everything below the heading is the written "
    "procedure itself — not a description of one — and it is the same text the "
    "model is handed when you run the command underneath it.\n\n"
    "**Read it before you run it.** That order is the one rule this commons is "
    "strictest about, and it is the habit the whole subject rests on: you do "
    "not hand an instruction to something that acts on your behalf without "
    "reading what the instruction says.\n\n"
    "What this one does, in four moves. It says which route it found and which "
    "model it is about to use. It shows your settings **without ever printing "
    "your password**. Then it deliberately breaks itself in a separate process "
    "with the settings removed, so you meet the no-model message here, on "
    "purpose, rather than on lesson forty wondering what went wrong. Then it "
    "asks the model one real question and checks the answer came back in the "
    "shape the skill promised.\n\n"
    "### The skill"),
 ],
 "expect": "Four things, in order. Which route it found and which model it "
           "will use. Your settings, with the password shown as present rather "
           "than printed. Then the deliberate failure: exit code 2, and a "
           "message saying no model is configured — that is the one you were "
           "meant to meet here. Then one real answer from the model, with a "
           "count of how many ways it broke the shape the skill asked for. "
           "Zero is what you want. A different model will answer differently, "
           "and that is the subject of this whole commons rather than a fault "
           "in your setup.",
 "challenge": "Run it again with a different model — change `MODEL`, or pick "
              "another one from the catalogue in Route C — and put the two "
              "answers side by side. Nothing about your computer changed and "
              "the answer did. That is worth sitting with for a moment: every "
              "finding in every later lesson has the same property, which is "
              "why each one names the model that produced it. A result you "
              "cannot attribute to a model is a result you cannot check.",
},

"A0.1": {
 "concept": """
This commons has one subject: **security engineering when the thing you are
securing — or the thing doing the securing — is an agent.** Not prompt
engineering, not model training, not a vendor comparison. An agent is software
that plans, calls tools and acts on what it reads, and every part of that
sentence is both an attack surface and a control point.

It is free, open, and not a product. No account, no paid tier, no GPU and no
API key on the default path through any lesson. Every script is standard
library only.

### Who it is for

Five roles, and each one has a whole function written for it. You need one of
them, not five — and everybody starts in Function A, which builds the system
the other five ask their questions of.

- **Anyone who has never shipped an agent**, including all five roles below.
  You build CyberTravels' platform end to end before a single control is
  argued about. → Function A.
- **A security architect or product engineer** asked whether an agentic feature
  is safe to ship, who needs a component map before a control list. → Function B.
- **An application security engineer or penetration tester** who already runs
  SAST, DAST and manual testing, and now has to review code an agent wrote and
  test a system that answers differently each time. → Function C.
- **A red team operator or AI security researcher** attacking a system with no
  fixed response, who has to report a result that survives being run again.
  → Function D.
- **A SOC analyst, detection engineer or incident responder** whose thresholds
  were tuned against a person doing twelve things an hour, now watching an agent
  do fourteen hundred. → Function E.
- **A GRC lead, risk owner or somebody in the CISO's office** who has to say in
  writing whether the estate is under control, and be right. → Function F.

It assumes you can read a Python function. Not that you can write one, and not
that you have a security background.

### The three questions every page answers

Day 0, Day 1 and Day 2 appear in a table on every lesson. They are **not** a
maturity model and not a timeline — Day 0 is not "first week". They are the
three questions a practitioner asks before reading anything:

| | the question | what a good answer looks like |
|---|---|---|
| **Day 0 — why** | What goes wrong if you do nothing? | A consequence in this lesson's own terms, not a general appeal to risk |
| **Day 1 — how** | What do you actually build or run? | The concrete thing: a rule, a map, a gate, a score |
| **Day 2 — measure** | What number says it worked? | A number the lesson produces — a recall figure, a false-positive rate, an interval in minutes |

Day 2 is easy to fake and the only one a sceptical reader believes. Where a
lesson produces a real number, Day 2 names it; where it does not, Day 2 says
what you count instead and does not pretend. Use them like this: **Day 0
decides whether to read the lesson, Day 1 is what you do, Day 2 is what you put
in the update to whoever asked.**

Getting this funded is the part most material leaves out, and it is hardest in
organisations that cannot buy the capability. A lesson that stops at the
technique gives you nothing to take to the person holding the budget.

### What a lesson is made of

A page is built from a fixed set of sections in a fixed order, and the order is
the argument. **A page shows only the sections it has something for**, so the
set below is what is available rather than a checklist every page satisfies —
this page, for one, has no Risk, no Day table and no CyberTravels scene,
because it is about your machine rather than about a system anybody secures.

1. **Risk and Control** — one sentence each, at the top: what goes wrong here,
   and what closes it. On the lessons that are about a system, which is 146 of
   the 148.
2. **The hook** — a scene, before anything else. Deliberately *not* a summary:
   it is the consequence of not knowing the lesson. The summary is section 3.
3. **What this lesson is** — the plain description, and the Day table.
4. **The framework** — the concept and its diagram, plus in Functions E and F
   an *anchor* line saying which part of that function's single argument the
   lesson moves. This always comes before any code: teaching the how before the
   why is the most common way a good lesson lands badly.
5. **In CyberTravels** — the idea in the running case study.
6. **The skill** — the `SKILL.md` as it exists in
   [`skills/`](https://github.com/spbreed/cyber-commons/tree/master/skills).
   Frontmatter tells an agent when to load the procedure; the markdown reads as
   a checklist for a person.
7. **Run it** — the two commands that execute the skill on your own machine.
   The page holds no procedure of its own: it runs the file in `skills/`, which
   is the only copy that exists. That is why a fix to a procedure is one edit
   to one file rather than a change in 148 places.
8. **What you just proved** — on the lessons that ran something, and only
   those. A reading lesson proves nothing and says nothing here.
9. **Your turn** — one input to change so a number moves. The lesson is in the
   difference between the two numbers, not in either one.

A section that is present on every page regardless of whether it has anything
to say stops being a heading and becomes a form. The set a given lesson renders
is declared in
[`scripts/exercises/layout.py`](https://github.com/spbreed/cyber-commons/blob/master/scripts/exercises/layout.py),
with the reason for each omission, and a check refuses both an empty section
and prose left behind for a section that no longer renders.

**The hook is always CyberTravels.** It sells corporate travel, and its product
is an agentic platform of four agents — a workflow agent that books and refunds,
a retrieval advisor, a coding agent, and a file-system agent reading vendor
documents. Alex is the product engineer who shipped it. One system, every
lesson. That is a deliberate cost — a lesson could always find a sharper
example of its own idea — and the payoff is cumulative: the refund limit an
attacker walks past in Function B is the one a detection watches in Function E
and a report counts in Function F.
""",
 "steps": [
  ("md", "## 2 · Start where your work already is"),
  ("html", D.table(
    ["if your job is", "start at", "then", "what you have at the end"],
    [["<span>Designing or approving an agentic feature</span>",
      "<b>B1.0</b>", "B1 → B2 → B3, in order",
      "A component map, and an index where every risk names the control that "
      "owns it"],
     ["<span>AppSec, code review, penetration testing</span>",
      "<b>C2.0</b>", "C2 in order; B1.1 and B1.2 when a lesson asks",
      "A pipeline with an AI pass in it, and a measured false-positive rate "
      "for that pass"],
     ["<span>Red teaming or AI security research</span>",
      "<b>D1.0</b>", "D1 in order; B1.2 and B1.3 first for the attack classes",
      "An evaluation that reproduces, and a report a defender can act on"],
     ["<span>Detection, alert triage, incident response</span>",
      "<b>E1.0</b>", "E1 → E2 → E3 → E4 → E5; B1.1 for the component names",
      "Five intervals with a number on each, and the rules that shortened them"],
     ["<span>Governance, risk, compliance, the CISO office</span>",
      "<b>F1.0</b>", "F1.1 next, then F1 → F2 → F3",
      "A control indicator computed from the estate rather than asserted "
      "about it"]],
    caption="Reading front to back is the right route only for the architect. "
            "Every other row skips what it does not need and nothing it does.")),

  ("md", "## 3 · Open source first, and then buy something\\n\\n"
         "Every tool named in this commons is one you can install today without "
         "a purchase order. That is a teaching decision before it is a budget "
         "one.\\n\\n"
         "**You cannot specify a product you have not built a bad version of.** "
         "A team that has stood up Wazuh and OpenSearch, written twenty Sigma "
         "rules and watched them fire on their own traffic can ask a vendor the "
         "two questions that matter: what does this do that my rules do not, "
         "and what does it cost to keep it true. A team that has not can only "
         "compare feature lists, and a feature list is written by the seller.\\n\\n"
         "The second reason is that **the gaps are the finding**. Building the "
         "open-source version tells you exactly where it stops. E1.0 names two "
         "out loud: there is no open-source data-loss prevention with the "
         "maturity of the other sensors, and *no product in the list at all* "
         "can tell you which prompt caused a file write. Neither is visible "
         "from a datasheet, and both are the reason to buy — or to build."),
  ("html", D.table(
    ["what you need", "learn it on", "buy when"],
    [["Endpoint and workload sensing", "<b>Wazuh</b>",
      "Estate size or support obligations outgrow what you can operate"],
     ["Somewhere for telemetry to land", "<b>OpenSearch</b>",
      "Retention and query cost stop being a tuning problem"],
     ["Portable, reviewable detections",
      "<b>Sigma</b>, mapped to <b>ATT&amp;CK</b> and <b>ATLAS</b>",
      "Almost never — the rules outlive the platform, which is the point"],
     ["Static analysis in the pipeline", "<b>Semgrep</b>, plus the reasoning "
      "pass from C2.3",
      "Language coverage or triage volume is the constraint"],
     ["Dependency and image inspection", "<b>Trivy</b>, <b>Syft</b>, <b>Grype</b>",
      "You need attestation and provenance rather than a scan"],
     ["Threat intelligence and cases",
      "<b>MISP</b>, <b>OpenCTI</b>, <b>TheHive</b>",
      "Intelligence you cannot source yourself is the gap"],
     ["Orchestration and forensics", "<b>Shuffle</b>, <b>Velociraptor</b>",
      "Response time is bounded by people rather than by tooling"]],
    caption="The right-hand column is the one to argue about. A control you "
            "have never operated has no 'buy when' — it has a demo.")),

  ("md", "## 4 · The four vocabularies, and which question each answers\\n\\n"
         "Every lesson page carries framework labels. Four frameworks are in "
         "use across this field and they answer different questions; a finding "
         "filed under the wrong one reaches nobody.\\n\\n"
         "- **[OWASP's two Top 10s](https://genai.owasp.org/llm-top-10/)** — "
         "*what can go wrong.* The LLM list is application-level; the "
         "[Agentic list](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) "
         "is for systems that plan and call tools. Reach for these reviewing a "
         "feature.\\n"
         "- **[MITRE ATLAS](https://atlas.mitre.org/)** — *what an attacker "
         "did.* ATT&CK's grammar applied to AI. The right lens in an incident "
         "write-up.\\n"
         "- **[NIST AI RMF](https://airc.nist.gov/AI_RMF_Knowledge_Base/AI_RMF)** "
         "— *how you organise to find out.* GOVERN, MAP, MEASURE, MANAGE. A "
         "NIST function in a vulnerability report is a category error.\\n"
         "- **[The EU AI Act](https://artificialintelligenceact.eu/)** — *what "
         "you must be able to show*, by article. Article 15 is accuracy, "
         "robustness and cybersecurity; Article 14 is human oversight. The only "
         "one of the four that can fine you.\\n\\n"
         "A control usually needs one of each: a threat it addresses, a tactic "
         "it frustrates, a function it belongs to, and an obligation it "
         "discharges. The mapping lives in `curriculum/frameworks.json` and "
         "every label on every lesson page is generated from it — these are "
         "indicative mappings, not a certification."),

  ("md", "## 5 · The two ways to run any of it\\n\\n"
         "A lesson's procedure is a file in `skills/`, and there is exactly "
         "one copy of it. Everything runs on your own machine; there is no "
         "hosted kernel and nothing to sign up for.\\n\\n"
         "**Run the script** — clone once, then run any skill against the "
         "fixture committed beside it:\\n\\n"
         "```bash\\n"
         "git clone --branch master https://github.com/spbreed/cyber-commons\\n"
         "cd cyber-commons\\n"
         "python3 skills/programme/dev-environment-preflight/scripts/"
         "dev_environment_preflight.py\\n"
         "```\\n\\n"
         "**Or ask your own agent** — one command links every skill into "
         "whichever CLI you already use, and then you ask for one by name "
         "instead of running a path:\\n\\n"
         "```bash\\n"
         "python3 scripts/install_skills.py --all    # claude, codex, gemini, "
         "cursor, opencode, goose\\n"
         "python3 scripts/install_skills.py --list   # what is linked where\\n"
         "```\\n\\n"
         "Those are **symlinks into your clone**, not copies, so `git pull` "
         "updates every tool at once and an edit you make here is live in all "
         "of them. A copy would be a fork with a friendly name: you would fix "
         "a skill once and the other copies would keep the bug while still "
         "loading, still validating and still answering.\\n\\n"
         "Every skill here is carried out by a **model**, so what you get is "
         "one model's answer, validated against that skill's own output "
         "contract. Run it twice and it will differ — that is the subject of "
         "the whole commons, not a defect. What does not differ is the "
         "harness: `check_determinism.py` runs every skill across several hash "
         "seeds and fails if the deterministic half varies."),

  *skill_steps("programme/dev-environment-preflight",
               "## 6 · The whole mechanism, demonstrated on itself\\n\\n"
               "The rest of this lesson is the mechanism running. The skill "
               "below is a preflight: it reports the runtime and the model "
               "that is about to answer, **causes the unconfigured failure on "
               "purpose** in a child process so you meet that message here "
               "rather than on lesson forty, then makes one real model call "
               "and validates the reply against its own output contract.\\n\\n"
               "That is the shape of every lesson in the commons. The skill "
               "is the procedure, the model carries it out, and the contract "
               "is what decides whether the answer is usable.\\n\\n"
               "### The skill"),
 ],
 # The counts are the reader's checksum against their own run, and
 # scripts/check_claims.py holds them against the tree. They used to live in
 # curriculum/labs.json's Expect box, which printed this same paragraph a
 # second time at the bottom of the page.
 "expect": "The tree, inventoried from disk rather than asserted — 14 areas, "
           "139 skills, 139 of them with a script, counted from what was "
           "fetched rather than claimed. Then "
           "the same procedure failing twice and working once: exit 2 with "
           "`[Errno 2]` when nothing was fetched, exit 1 with "
           "`ModuleNotFoundError` when the runtime is off the path, and exit 0 "
           "with twelve lines and a CRC when both conditions hold. `ready` is "
           "true only because both failures were reproduced; a preflight that "
           "shows only the success has tested one path in three.",
 "challenge": "Run it on the other route. If you ran the script by path, now "
              "run `python3 scripts/install_skills.py --all`, open your agent "
              "anywhere on the machine and ask it for "
              "`dev-environment-preflight` by name; if you started with the "
              "agent, run the script directly. Compare the CRC on the last "
              "line — it should be identical, because the symlink means both "
              "routes execute the same file. If it is not, the link is a copy "
              "and something went wrong at install time.",
},

}
