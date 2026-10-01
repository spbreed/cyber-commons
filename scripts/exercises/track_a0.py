"""A0 — set up, how to use the commons, and the words for an agent.

It exists because of one repeated piece of reader feedback: *nobody could tell
what this was for until somebody explained it.* These lessons are that
explanation, written down, so it does not need a person attached.

It was five lessons for a while — audience, routing, conventions, how to run
one, and the frameworks — and they repeated each other badly: three of the five
explained Day 0/1/2, two explained the personas, and a reader had to open four
pages to learn things that fit on one.

It is two now. A0.0 is the whole front door: what the commons is, who it is
for, the machine, the model, the one preflight run, and how to read a lesson
page. A0.1 owns the vocabulary of the thing being built.

The front door was two pages for a while — the machine, then the commons — and
the second kept re-explaining the first: it re-ran the preflight, then, once
that was removed, opened by pointing back at the page before it for what a
skill is. A reader had to finish two pages before opening a lesson, and the
split was asked to go more than once before it went. One page, read once.
"""

from . import diagrams as D
from .skills import skill_steps

# A0.1's figure: the nine words for an agent, one card each. The colours rotate
# through the defensive hues only. Amber means the adversary on every page of
# the commons, and none of these nine is an attack; red appears once, on the
# guardrail's refused path, because that is what red means everywhere else.
_C, _B, _G, _V = D.DEFEND, "#1d4ed8", D.GOOD, "#6d28d9"

_NINE = D.grid([
 D.term(1, "Harness", "The loop that lets a model act. Context in, tool call "
        "out, result back, repeat.", D.mini(
   D.box(2, 16, 54, 26, "context", colour=_C)
   + D.arrow(56, 29, 64) + D.box(64, 16, 46, 26, "model", colour=_C)
   + D.arrow(110, 29, 118) + D.box(118, 16, 58, 26, "tool call", colour=_C)
   + D.arrow(176, 29, 184) + D.box(184, 16, 54, 26, "result", colour=_C)
   + f'<path d="M211 42 V64 H29 V44" fill="none" stroke="{D.LINE}" '
     f'stroke-width="1.4" marker-end="url(#a)"/>'
   + D.label(120, 78, "repeat until done", anchor="middle")
   + D.label(4, 102, "in:  skills · memory · prompts")
   + D.label(4, 118, "out: shell · APIs · browser"), "t1"),
        "Built in A1.1, and wrapped in A2.0", colour=_C),

 D.term(2, "Memory & state", "What it remembers between runs, and where it "
        "is in the task right now.", D.mini(
   D.box(2, 8, 80, 38, "short-term", sub="context window", colour=_B)
   + D.box(94, 14, 52, 26, "agent", colour=_B)
   + D.arrow(94, 27, 84) + D.arrow(146, 27, 156)
   + D.box(158, 8, 80, 38, "long-term", sub="saved to disk", colour=_B)
   + D.arrow(120, 40, 120, 62)
   + D.box(40, 64, 160, 40, "state", sub="current step · open tasks",
           colour=_B), "t2"),
        "Built in A1.5", colour=_B),

 D.term(3, "RAG", "Retrieval-augmented generation: pull the right documents "
        "into the prompt, so answers come with sources.", D.mini(
   D.box(2, 6, 64, 26, "question", colour=_G)
   + D.arrow(66, 19, 80) + D.box(80, 6, 74, 26, "search docs", colour=_G)
   + D.arrow(154, 19, 166) + D.box(166, 6, 72, 26, "top chunks", colour=_G)
   + D.arrow(200, 32, 170, 52)
   + D.box(60, 52, 120, 26, "model + context", colour=_G)
   + D.arrow(120, 78, 120, 92)
   + D.box(50, 92, 140, 26, "answer + sources", colour=_G), "t3"),
        "In CyberTravels from the start", colour=_G),

 D.term(4, "MCP", "Model Context Protocol. One standard plug for tools and "
        "data, so a tool is written once and any agent can call it.", D.mini(
   D.box(2, 50, 44, 26, "agent", colour=_V)
   + D.arrow(46, 63, 56) + D.box(56, 50, 54, 26, "client", colour=_V)
   + D.arrow(110, 63, 120) + D.box(120, 50, 56, 26, "server", colour=_V)
   + D.arrow(176, 63, 190, 29) + D.arrow(176, 63, 190)
   + D.arrow(176, 63, 190, 97)
   + D.box(190, 16, 48, 26, "tools", colour=_V)
   + D.box(190, 50, 48, 26, "data", colour=_V)
   + D.box(190, 84, 48, 26, "prompts", colour=_V), "t4"),
        "Built in A1.2", colour=_V),

 D.term(5, "Skills", "Reusable know-how in a SKILL.md file. Only the name "
        "and description load until a task needs the rest.", D.mini(
   f'<rect x="4" y="4" width="150" height="112" rx="6" fill="none" '
   f'stroke="{_C}" stroke-width="1.4"/>'
   + D.label(14, 24, "SKILL.md", colour=_C, size=12, weight="bold")
   + f'<rect x="12" y="34" width="134" height="22" rx="4" '
     f'fill="{_C}" fill-opacity=".12" stroke="{_C}"/>'
   + D.label(20, 49, "name + description", colour=_C)
   + f'<rect x="12" y="62" width="134" height="46" rx="4" fill="none" '
     f'stroke="{D.LINE}" stroke-dasharray="4 3"/>'
   + D.label(20, 80, "instructions") + D.label(20, 98, "scripts & files")
   + D.label(162, 49, "always loaded", colour=_C)
   + D.label(162, 80, "loaded when") + D.label(162, 94, "a task needs it"),
   "t5"),
        "Every lesson here is one — A0.0", colour=_C),

 D.term(6, "Guardrails", "Permissions, a sandbox, and a human sign-off "
        "before anything risky.", D.mini(
   D.box(2, 30, 46, 26, "action", colour=_G)
   + D.arrow(48, 43, 56) + D.box(56, 30, 72, 26, "permissions", colour=_G)
   + D.arrow(128, 43, 136)
   + f'<path d="M164 21 L192 43 L164 65 L136 43 Z" fill="none" '
     f'stroke="{D.BAD}" stroke-width="1.4"/>'
   + D.label(164, 47, "risky?", colour=D.BAD, anchor="middle")
   + D.arrow(192, 43, 200) + D.box(200, 30, 38, 26, "run", colour=_G)
   + D.label(196, 26, "no", anchor="middle")
   + D.arrow(164, 65, 164, 80) + D.label(170, 76, "yes")
   + D.box(106, 80, 120, 26, "human sign-off", colour=_G)
   + D.label(120, 124, "least access · every action logged",
             anchor="middle"), "t6"),
        "Built in A1.4 and A1.7", colour=_G),

 D.term(7, "Evals", "Score outputs against what you expected, before your "
        "users find the gap for you.", D.mini(
   D.box(10, 8, 64, 26, "agent", colour=_B)
   + D.arrow(74, 21, 150) + D.box(150, 8, 84, 26, "output", colour=_B)
   + D.arrow(192, 34, 192, 66)
   + D.box(150, 66, 84, 26, "expected", colour=_B)
   + D.arrow(150, 79, 74) + D.box(10, 66, 64, 26, "score", colour=_B)
   + D.arrow(42, 66, 42, 34)
   + D.label(112, 58, "compared", anchor="middle")
   + D.label(120, 116, "test sets before launch · traces after",
             anchor="middle"), "t7"),
        "Built in A2.3 and A2.4", colour=_B),

 D.term(8, "A2A", "Agent2Agent. How agents from different vendors find each "
        "other and hand work over.", D.mini(
   D.box(2, 30, 54, 28, "agent A", colour=_V)
   + D.arrow(56, 44, 80)
   + D.box(80, 18, 80, 52, "agent card", sub="skills · endpoint",
           colour=_V)
   + D.arrow(184, 44, 160)
   + D.box(184, 30, 54, 28, "agent B", colour=_V)
   + f'<path d="M29 58 V90 H211 V60" fill="none" stroke="{D.LINE}" '
     f'stroke-width="1.4" stroke-dasharray="4 4" marker-end="url(#a)"/>'
   + D.label(120, 108, "tasks · messages · artifacts", anchor="middle"),
   "t8"),
        "Built in A1.6", colour=_V),

 D.term(9, "Multi-agent", "An orchestrator splits the job. Specialist "
        "agents run in parallel.", D.mini(
   D.box(66, 4, 108, 26, "orchestrator", colour=_C)
   + D.arrow(120, 30, 38, 50) + D.arrow(120, 30, 120, 50)
   + D.arrow(120, 30, 202, 50)
   + D.box(2, 50, 72, 26, "retrieval", colour=_C)
   + D.box(84, 50, 72, 26, "workflow", colour=_C)
   + D.box(166, 50, 72, 26, "coding", colour=_C)
   + D.arrow(38, 76, 96, 96) + D.arrow(120, 76, 120, 96)
   + D.arrow(202, 76, 144, 96)
   + D.box(66, 96, 108, 26, "final result", colour=_C), "t9"),
        "Drawn in A1.0 — four agents", colour=_C),
], caption="The nine words for an agent. Each card's footer names the lesson "
           "in Function A where you build it; section 3 names the file it "
           "ends up in and the lesson that attacks it.")


EXERCISES: dict[str, dict] = {

"A0.0": {
 "concept": """
**Start here even if you have never written a line of code.** This lesson
assumes you can use a computer and nothing else. It takes about half an hour,
it costs nothing, and at the end you will have run a real piece of security
work on your own machine and know which lesson to open next.

### What this is

This commons has one subject: **security engineering when the thing you are
securing — or the thing doing the securing — is an agent.** Not prompt
engineering, not model training, not a vendor comparison. An agent is software
that plans, calls tools and acts on what it reads, and every part of that
sentence is both an attack surface and a control point. It is free, open, and
not a product.

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

This page asks for nothing but a computer. From A1.0 on, a lesson assumes you
can read a Python function — not that you can write one, and not that you have
a security background.

### What a skill is

Every lesson in this commons hands a model a **written procedure** — plain English that says how to do one job in security: find the
weak spot in this code, work out what an attacker could reach, decide whether
this alert is real. The model reads the instructions and does the job. Those
instructions are called **skills**. You can read every one, change them, and
watch the answer change. There is no hidden part.

### How to execute a skill

Near the bottom of every lesson page is a run block with the ways to do that
lesson — in your AI assistant, as one Python command, or by reading the code.
This page has one too. The rest of this lesson gets your computer ready for
it.

### Why this is a new way of working

For most of computing, the instructions a person read and the code a computer
ran were two different things, kept in step by nobody. A skill collapses that:
**the document and the instruction are the same bytes**, so what you read is
what executes. For a cybersecurity practitioner, that is the shift worth
understanding before anything else here — development is moving from writing
code to writing skill files, and the job in front of you becomes judging what
a model produced from one, not only producing it yourself.

A skill does not make a model correct. It makes the procedure explicit and the
output checkable — a smaller claim, and the one this whole curriculum is
about.

### Words you will meet

You do not need to memorise these. Come back to this table when one of them
turns up and you are not sure. These are the words for your computer; the
nine for agents themselves — harness, MCP, A2A and the rest — are A0.1.

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

### What you need

Three things: a place to write code, a copy of this repository, and a model
that answers. Everything below works on a free tier — you do not need a paid
plan to finish this commons.
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
         "## 4 · Tell it which model to ask\n\n"
         "This is the one step that matters. You are giving your computer the "
         "equivalent of a phone number for a model, so that when a lesson has "
         "a job to do it knows who to call.\n\n"
         "**There is an easy way and a complicated way, and you only need one "
         "of them.** Take the easy one unless you have a reason not to.\n\n"
         "### Route A — use a commercial code-generation LLM (the easiest)\n\n"
         "**Use an AI coding assistant.** Claude Code, Codex, GitHub Copilot "
         "and Cursor all work, and each has a free way to start — the table "
         "in step 2 compares them and links every sign-up page. This is the "
         "easiest route by a wide margin, and the one to start with: **you "
         "need no API key, no endpoint and no settings.** The assistant is "
         "the model. When you pick a lesson's skill, it reads the lesson, does "
         "the work and answers the check itself.\n\n"
         "1. **Get one.** Any of the four. If you already use one, use that.\n"
         "2. **Sign in once**, the way the assistant tells you to.\n"
         "3. **Open it in the `cyber-commons` folder** you cloned in step 3.\n\n"
         "That is the whole route. The run block at the foot of this page "
         "does your first lesson. If you chose "
         "Claude Code you can check it from the terminal:\n\n"
         "```bash\n"
         "claude --version      # if this prints a version, you are done\n"
         "claude                # run once to sign in, if you have not\n"
         "```\n\n"
         "This is also how these skills are *meant* to be used: the "
         "[agentskills.io](https://agentskills.io) format exists so an agent "
         "can load a `SKILL.md` and carry out the procedure itself.\n\n"
         "**Routes B and C are the complicated way.** They are for the case "
         "where you cannot or would rather not use a commercial assistant: no "
         "account, no network, or nothing allowed to leave your machine. They "
         "are folded away just below. Open them only if you need one.\n\n"
         ""),

  ("fold", ("Route B and Route C — the complicated way. Open only if you "
            "need to run a model yourself.", [
  ("md",          "### Route B — a model you run yourself\n\n"
         "[Ollama](https://ollama.com) is the shortest path to a model on your "
         "own machine. Nothing leaves it, and there is no quota:\n\n"
         "```bash\n"
         "curl -fsSL https://ollama.com/install.sh | sh\n"
         "ollama serve &                 # not automatic on every platform\n"
         "ollama pull <a model from ollama.com/library>\n"
         "```\n\n"
         "The name you pull is the name you give to `MODEL` below. The cost is "
         "your hardware. A 1.5B model answers in seconds on a "
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
      "<code>the name you pulled</code>"]],
    caption="One protocol — OpenAI-compatible chat completions — so the same "
            "three variables point at Ollama, llama.cpp, vLLM or a hosted free "
            "tier without a line of code changing.")),

  ("md", "### Either of these works\n\n"
         "```bash\n"
         "# Local, free, offline after the pull, nothing leaves the machine:\n"
         "export OPENAI_BASE_URL=http://127.0.0.1:11434/v1\n"
         "export OPENAI_API_KEY=ollama\n"
         "export MODEL=<the name you pulled>\n"
         "\n"
         "# Or a hosted free tier — Google AI Studio gives a key with no card:\n"
         "export OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai\n"
         "export OPENAI_API_KEY=<your AI Studio key>\n"
         "export MODEL=gemini-2.5-flash\n"
         "```\n\n"
         "**Put the key in your shell profile, never in a file inside the "
         "repository.** `scripts/check_secrets.py` runs as a pre-commit hook "
         "and in CI, and it blocks anything credential-shaped from being "
         "committed — but the habit is what protects you, not the gate."),
  ])),

  # Sections 5 to 9 were a page of their own, A0.1, and are the half of the
  # front door that is about the commons rather than the machine. They sit
  # after the setup on purpose: a reader who has a model answering reads how
  # the pages are laid out with somewhere to go next, and one who only wants
  # the setup has finished it by here.
  ("md", "## 5 · How to read a lesson page\n\n"
         "Every page is built from a fixed set of sections in a fixed order, "
         "and the order is the argument. **A page shows only the sections it "
         "has something for**, so the set below is what is available rather "
         "than a checklist every page satisfies — this page, for one, has no "
         "Risk, no Day table and no CyberTravels scene, because it is about "
         "your machine rather than about a system anybody secures.\n\n"
         "1. **Risk and Control** — one sentence each, at the top: what goes "
         "wrong here, and what closes it. On the lessons that are about a "
         "system.\n"
         "2. **The hook** — a scene, before anything else. Deliberately *not* "
         "a summary: it is the consequence of not knowing the lesson. The "
         "summary is section 3.\n"
         "3. **What this lesson is** — the plain description, and the Day "
         "table.\n"
         "4. **The framework** — the concept and its diagram, plus in "
         "Functions E and F an *anchor* line saying which part of that "
         "function's single argument the lesson moves. This always comes "
         "before any code: teaching the how before the why is the most common "
         "way a good lesson lands badly.\n"
         "5. **In CyberTravels** — the idea in the running case study.\n"
         "6. **The skill** — the `SKILL.md` as it exists in "
         "[`skills/`](https://github.com/spbreed/cyber-commons/tree/master/skills), "
         "pasted in rather than copied out, so a fix is one edit to one file.\n"
         "7. **Run it** — the run block, the same on every page.\n"
         "8. **What you just proved** — on the lessons that ran something, and "
         "only those. A reading lesson proves nothing and says nothing here.\n"
         "9. **Your turn** — one input to change so a number moves. The lesson "
         "is in the difference between the two numbers, not in either one.\n\n"
         "Deciding whether to read a lesson takes section 3 alone. If you "
         "already know the idea, section 7 alone.\n\n"
         "A section that is present on every page regardless of whether it has "
         "anything to say stops being a heading and becomes a form. The set a "
         "given lesson renders is declared in "
         "[`scripts/exercises/layout.py`](https://github.com/spbreed/cyber-commons/blob/master/scripts/exercises/layout.py), "
         "with the reason for each omission, and a check refuses both an empty "
         "section and prose left behind for a section that no longer renders.\n\n"
         "**The hook is always CyberTravels.** It sells corporate travel, and "
         "its product is an agentic platform of four agents — a workflow agent "
         "that books and refunds, a retrieval advisor, a coding agent, and a "
         "file-system agent reading vendor documents. Alex is the product "
         "engineer who shipped it. One system, every lesson. That is a "
         "deliberate cost — a lesson could always find a sharper example of "
         "its own idea — and the payoff is cumulative: the refund limit an "
         "attacker walks past in Function B is the one a detection watches in "
         "Function E and a report counts in Function F.\n\n"
         "### The three questions every page answers\n\n"
         "Day 0, Day 1 and Day 2 appear in a table on every lesson about the "
         "system. They are **not** a maturity model and not a timeline — Day "
         "0 is not \"first week\". They are the three questions a practitioner "
         "asks before reading anything:\n\n"
         "| | the question | what a good answer looks like |\n"
         "|---|---|---|\n"
         "| **Day 0 — why** | What goes wrong if you do nothing? | A "
         "consequence in this lesson's own terms, not a general appeal to "
         "risk |\n"
         "| **Day 1 — how** | What do you actually build or run? | The "
         "concrete thing: a rule, a map, a gate, a score |\n"
         "| **Day 2 — measure** | What number says it worked? | A number the "
         "lesson produces — a recall figure, a false-positive rate, an "
         "interval in minutes |\n\n"
         "Day 2 is easy to fake and the only one a sceptical reader believes. "
         "Where a lesson produces a real number, Day 2 names it; where it does "
         "not, Day 2 says what you count instead and does not pretend. Use "
         "them like this: **Day 0 decides whether to read the lesson, Day 1 is "
         "what you do, Day 2 is what you put in the update to whoever "
         "asked.**\n\n"
         "Getting this funded is the part most material leaves out, and it is "
         "hardest in organisations that cannot buy the capability. A lesson "
         "that stops at the technique gives you nothing to take to the person "
         "holding the budget.\n\n"
         "## 6 · Start where your work already is\n\n"
         "Everybody builds the system first — A0.1, then A1 and A2. After "
         "that, find your row. Open the lesson in its \"start at\" column and "
         "read only its Day table: those three lines are enough to decide "
         "whether it is worth an afternoon."),
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

  ("md", "## 7 · Open source first, and then buy something\n\n"
         "Every tool named in this commons is one you can install today without "
         "a purchase order. That is a teaching decision before it is a budget "
         "one.\n\n"
         "**You cannot specify a product you have not built a bad version of.** "
         "A team that has stood up Wazuh and OpenSearch, written twenty Sigma "
         "rules and watched them fire on their own traffic can ask a vendor the "
         "two questions that matter: what does this do that my rules do not, "
         "and what does it cost to keep it true. A team that has not can only "
         "compare feature lists, and a feature list is written by the seller.\n\n"
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

  ("md", "## 8 · The four vocabularies, and which question each answers\n\n"
         "Every lesson page carries framework labels. Four frameworks are in "
         "use across this field and they answer different questions; a finding "
         "filed under the wrong one reaches nobody.\n\n"
         "- **[OWASP's two Top 10s](https://genai.owasp.org/llm-top-10/)** — "
         "*what can go wrong.* The LLM list is application-level; the "
         "[Agentic list](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) "
         "is for systems that plan and call tools. Reach for these reviewing a "
         "feature.\n"
         "- **[MITRE ATLAS](https://atlas.mitre.org/)** — *what an attacker "
         "did.* ATT&CK's grammar applied to AI. The right lens in an incident "
         "write-up.\n"
         "- **[NIST AI RMF](https://airc.nist.gov/AI_RMF_Knowledge_Base/AI_RMF)** "
         "— *how you organise to find out.* GOVERN, MAP, MEASURE, MANAGE. A "
         "NIST function in a vulnerability report is a category error.\n"
         "- **[The EU AI Act](https://artificialintelligenceact.eu/)** — *what "
         "you must be able to show*, by article. Article 15 is accuracy, "
         "robustness and cybersecurity; Article 14 is human oversight. The only "
         "one of the four that can fine you.\n\n"
         "A control usually needs one of each: a threat it addresses, a tactic "
         "it frustrates, a function it belongs to, and an obligation it "
         "discharges. The mapping lives in `curriculum/frameworks.json` and "
         "every label on every lesson page is generated from it — these are "
         "indicative mappings, not a certification."),

  # scripts/check_claims.py holds the counts below against the tree.
  ("md", "## 9 · What sits behind a lesson skill\n\n"
         "Behind each lesson skill is an **audit skill** — the written "
         "procedure the lesson runs, in `skills/`. There are 14 areas, "
         "140 skills, 140 of them with a script, and exactly one copy of "
         "each. Eighteen audits are shared by two or three lessons, which is "
         "why a lesson skill calls one rather than carrying its own copy.\n\n"
         "You can install a whole function at once rather than a lesson at a "
         "time, and ask what is currently linked:\n\n"
         "```bash\n"
         "python3 scripts/install_skills.py --all --lessons A   # this function's lesson skills\n"
         "python3 scripts/install_skills.py --list              # what is linked where\n"
         "```\n\n"
         "Those are **links into your clone**, not copies — symlinks, or "
         "junctions on Windows — so `git pull` updates every tool at once and "
         "an edit you make here is live in all of them. A copy would be a fork "
         "with a friendly name: you would fix a skill once and the other copies "
         "would keep the bug while still loading and still answering."),

  # No "Do your first lesson" section here. It walked through install, pick
  # and read-the-readback — which is exactly what the run block below this
  # prose prints, generated, for every lesson. Two copies of the same
  # three steps on one page, and the hand-written one was the copy that
  # could go stale. The run block is the only one now.

  # The audit still runs (lesson.py reads it from these two steps); its
  # SKILL.md is not printed on this page. See layout.PROCEDURE_NOT_SHOWN.
  ("skill", "programme/dev-environment-preflight"),
  ("skill_script", "programme/dev-environment-preflight/scripts/"
                   "dev_environment_preflight.py"),
 ],
 "expect": "One skill did a whole lesson, whichever way you started it: it "
           "set up the example system, ran a check against a model, and told "
           "you what happened. Three things are now true. Your computer can reach a "
           "model, and the readback names which one — a different model will "
           "answer differently, which is the subject of this whole commons "
           "and not a fault in your setup. The number of ways the answer "
           "broke its contract was counted by the program, not by the model, "
           "so it deserves more trust than anything the model says about "
           "itself. And zero violations means the answer came back in the "
           "right shape, not that it is right; every later lesson keeps those "
           "two apart. If it stopped with \"no model configured\" instead, "
           "that is the other useful result: the message says what to set, "
           "and no answer was made up in its place.",
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
Nine words carry most conversations about agents, and most arguments about
agent security are two people using one of them for different things. This
lesson fixes the nine before Function A builds them, so that when A1.2 says
*MCP server* or A1.6 says *A2A* you already know what the box is.

They are not nine separate ideas. They stack:

- **The harness is the agent.** Everything else is something the harness
  reads from, calls, or is checked by. A model with no harness writes text; a
  model in a harness changes things.
- **Memory, RAG, MCP and skills are how things get into the context** the
  harness hands the model: what it remembered, what it retrieved, what tools
  it can reach, and what procedures it can follow. Every one of them is
  therefore also a way for text you did not write to reach the model.
- **Guardrails sit on the way out**, between the model proposing a tool call
  and the call happening. They are the only one of the nine that says *no*.
- **Evals sit beside the whole thing** and score what it did against what you
  meant.
- **A2A and multi-agent are several harnesses at once** — one handing work to
  another, or an orchestrator splitting a job between specialists. Each
  hand-over is a place where one agent's authority can quietly become
  another's.

That last point is the reason for the list. Each of the nine is a component
you build in Function A and a surface an attacker reaches for in Function B, so
learning them once, here, is learning the map both functions are drawn on.

Three of them are also **open standards** — MCP, A2A and the Agent Skills
format. What you build on them is not tied to one vendor: a skill written for
Claude Code loads in Codex, Cursor and Copilot, and an MCP server written for
one agent serves any other. It also means a flaw in how you use one is
portable in the same way.
""",
 "steps": [
  ("md", "## 2 · The nine, on one page\n\n"
         "One card per word: what it is in a line, and a picture of the "
         "mechanism, which is the part worth recognising later."),
  ("html", _NINE),
  ("md", "## 3 · Where each one lives, and where it goes wrong\n\n"
         "Every one of the nine is a real file in CyberTravels by the end of "
         "Function A, and every one has a lesson in Function B or D about "
         "breaking it. The right-hand column is the reason the commons "
         "teaches the words at all."),
  ("html", D.table(
    ["word", "in CyberTravels", "where it goes wrong"],
    [["<b>Harness</b>", "<code>runtime.py</code> — the loop, and "
      "<code>execute_tool</code>, the line where the model stops proposing",
      "B1.13 — a loop with no budget runs until something else stops it"],
     ["<b>Memory &amp; state</b>", "<code>memory.py</code>",
      "B1.4 — an instruction written into memory is read back as fact"],
     ["<b>RAG</b>", "<code>agents/rag_advisor.py</code> and "
      "<code>knowledge/retriever.py</code>",
      "B1.3 — a retrieved document steers the agent with the user's "
      "authority"],
     ["<b>MCP</b>", "<code>mcp/internal_server.py</code> and "
      "<code>mcp/vendor_server.py</code>",
      "B1.5 — a tool used within its grant for something nobody meant"],
     ["<b>Skills</b>", "<code>skills/</code> and <code>lesson-skills/</code> "
      "in this repository — the commons is built from them",
      "D1.1 — whatever an agent ingests as a procedure is supply chain"],
     ["<b>Guardrails</b>", "<code>identity.py</code> for delegation, the "
      "human gate and budget in <code>runtime.py</code>, and later "
      "<code>policy.py</code> and <code>sandbox.py</code>",
      "B1.15 — a human gate that approves everything because it sees too "
      "much"],
     ["<b>Evals</b>", "<code>tests/smoke_test.py</code>, growing with every "
      "lesson that adds a control",
      "D1.0 — an eval with an adversary is a red team"],
     ["<b>A2A</b>", "<code>a2a/protocol.py</code>",
      "B1.10 — a message from a peer agent treated as trusted"],
     ["<b>Multi-agent</b>", "<code>orchestrator/router.py</code> and the four "
      "agents in <code>agents/</code>",
      "B1.11 — one compromised agent among several that trust each other"]],
    caption="Paths are under <code>cybertravels/</code> except for skills. "
            "A file that appears later than Function A is named for where "
            "the guardrail ends up, not where it starts.")),
 ],
 "challenge": "Open `cybertravels/` and find all nine without this table: a "
              "file, and ideally the line, for each word. Count how many you "
              "placed. The ones you could not place are the lessons in "
              "Function A to read most carefully, and the count is worth "
              "taking again at the end of A2.5, when every one of them should "
              "be something you wrote.",
},

}
