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
Every skill in this commons is **executed by a language model**. The Python
script is not the procedure — it is the harness: it assembles the skill's
documented steps, sends them to a model with the input, and validates the
reply against the skill's output contract. So there is exactly one prerequisite,
and it is not a Python package. It is a model endpoint.

Get that wrong and nothing works, in a way that reads as a broken repository
rather than an unconfigured machine. That is what this lesson prevents.

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
  ("md", "## 2 · Pick a tool, against its real numbers"),
  ("html", D.table(
    ["tool", "free tier", "max context window", "paid, per month"],
    [["<b>Anthropic Claude</b> / Claude Code",
      "Rolling message caps on the web app, resetting every 5 hours. $5 API "
      "trial credit on phone verification.",
      "<b>1M tokens</b> on paid plans with frontier models; 200k on the free "
      "web plan",
      "$20 Pro · $25 Max · usage-based API"],
     ["<b>Google Antigravity</b>",
      "Perpetual public preview, free. Local orchestration across editor, "
      "terminal and browser.",
      "<b>1M–2M tokens</b> depending on the underlying Gemini model, with "
      "built-in state compression",
      "$0 preview · enterprise seats via Google Cloud"],
     ["<b>Google AI Studio</b>",
      "Free API keys, 60 requests/minute on Gemini Flash, no billing details "
      "required",
      "<b>2M tokens</b> on Gemini Pro models",
      "Pay-as-you-go once the free quota is breached"],
     ["<b>OpenAI ChatGPT</b> / Codex",
      "GPT-4o mini, code execution and data analysis. The legacy $5 API credit "
      "is largely phased out.",
      "128k tokens on standard frontier models; larger on API-only reasoning "
      "tasks",
      "$20 Plus · $200 Pro"],
     ["<b>GitHub Copilot</b>",
      "2,000 completions + 50 chat messages a month. <b>Students get the "
      "premium tier free.</b>",
      "32k–128k, scaled dynamically by which model serves the request",
      "$10 Pro (bundles $15 of AI credits) · $39 Pro+"],
     ["<b>Cursor</b>",
      "Hobby: 2,000 completions + 50 slow requests a month. <b>Students get up "
      "to a year of Pro.</b>",
      "128k–200k mapped codebase context; up to 1M with your own API key",
      "$20 Pro · $40 Business"],
     ["<b>Amazon Q Developer</b>",
      "50 agentic requests a month + 1,000 lines of code translation",
      "100k+ tokens of indexed codebase, mapped into the IDE panel",
      "$19 per user (Q Pro)"]],
    caption="Free tiers and context windows as at the time of writing. If you "
            "are a student, start at the two rows that say so — they are the "
            "best value in the table by a wide margin.")),

  ("md", "## 3 · Install what you actually need\n\n"
         "```bash\n"
         "# git and python3. Almost certainly already there.\n"
         "git --version          # any 2.x\n"
         "python3 --version      # 3.10 or newer\n"
         "\n"
         "# the repository. master is the trunk; every link on the site\n"
         "# points at it.\n"
         "git clone --branch master https://github.com/spbreed/cyber-commons.git\n"
         "cd cyber-commons\n"
         "```\n\n"
         "There is nothing to `pip install`. Every script here is standard "
         "library only — the one dependency is a model, and that is the next "
         "step.\n\n"
         "## 4 · Give it a model — two routes, both free\n\n"
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
         "### Route B — a model you run or a free hosted tier\n\n"
         "```bash\n"
         "curl -fsSL https://ollama.com/install.sh | sh\n"
         "ollama serve &                 # not automatic on every platform\n"
         "ollama pull qwen2.5:1.5b-instruct\n"
         "```\n\n"
         "Then set the three variables below. Setting `OPENAI_BASE_URL` "
         "**overrides** Route A, because somebody who set it meant it.\n\n"
         "### The three variables, for Route B"),

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
         "## 5 · Prove it, by running one"),

  *skill_steps(
    "programme/dev-environment-preflight",
    "The skill below is the proof. It reports the runtime, reports the "
    "configuration without ever printing your key, **causes the unconfigured "
    "failure on purpose in a child process** so you meet that message here "
    "rather than on lesson forty, then makes one real model call and validates "
    "the reply against its own output contract.\n\n"
    "Read what it does before you run it — that order is the house rule, and "
    "it is the one this commons is strictest about.\n\n"
    "### The skill"),
 ],
 "expect": "The runtime resolving from skills/_runtime, your endpoint and model "
           "named, and the key reported as present rather than printed. Then "
           "exit code 2 from the deliberate unconfigured run, with the refusal "
           "as its first line. Then one real model call: the model that "
           "answered, the number of contract violations in its reply, and the "
           "filled-in contract as JSON. A different model will fill it in "
           "differently — that is the subject of the whole commons, not a fault "
           "in the setup.",
 "challenge": "Run it a second time with a different MODEL and diff the two "
              "JSON blocks. Nothing about your machine changed, and the answer "
              "did. Every finding in every later lesson carries that same "
              "property, which is why each one names the model that produced "
              "it.",
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
them, not five.

- **A security architect or product engineer** asked whether an agentic feature
  is safe to ship, who needs a component map before a control list. → Function A.
- **An application security engineer or penetration tester** who already runs
  SAST, DAST and manual testing, and now has to review code an agent wrote and
  test a system that answers differently each time. → Function B.
- **A red team operator or AI security researcher** attacking a system with no
  fixed response, who has to report a result that survives being run again.
  → Function C.
- **A SOC analyst, detection engineer or incident responder** whose thresholds
  were tuned against a person doing twelve things an hour, now watching an agent
  do fourteen hundred. → Function D.
- **A GRC lead, risk owner or somebody in the CISO's office** who has to say in
  writing whether the estate is under control, and be right. → Function E.

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

Every page is the same seven sections in the same order, and the order is the
argument:

1. **The hook** — a scene, before anything else. Deliberately *not* a summary:
   it is the consequence of not knowing the lesson. The summary is section 2.
2. **What this lesson is** — the plain description, and the Day table.
3. **The framework** — the concept and its diagram, plus in Functions D and E
   an *anchor* line saying which part of that function's single argument the
   lesson moves. This always comes before any code: teaching the how before the
   why is the most common way a good lesson lands badly.
4. **In CyberTravels** — the idea in the running case study.
5. **The skill** — the `SKILL.md` as it exists in
   [`skills/`](https://github.com/spbreed/cyber-commons/tree/master/skills).
   Frontmatter tells an agent when to load the procedure; the markdown reads as
   a checklist for a person.
6. **Run it** — the two commands that execute the skill on your own machine.
   The page holds no procedure of its own: it runs the file in `skills/`, which
   is the only copy that exists. That is why a fix to a procedure is one edit
   to one file rather than a change in 135 places.
7. **Your turn** — one input to change so a number moves. The lesson is in the
   difference between the two numbers, not in either one.

**The hook is always CyberTravels.** It sells corporate travel, and its product
is an agentic platform of four agents — a workflow agent that books and refunds,
a retrieval advisor, a coding agent, and a file-system agent reading vendor
documents. Alex is the product engineer who shipped it. One system, every
lesson. That is a deliberate cost — a lesson could always find a sharper
example of its own idea — and the payoff is cumulative: the refund limit an
attacker walks past in Function A is the one a detection watches in Function D
and a report counts in Function E.
""",
 "steps": [
  ("md", "## 2 · Start where your work already is"),
  ("html", D.table(
    ["if your job is", "start at", "then", "what you have at the end"],
    [["<span>Designing or approving an agentic feature</span>",
      "<b>A1.0</b>", "A1 → A2 → A3, in order",
      "A component map, and an index where every risk names the control that "
      "owns it"],
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
      "<b>E1.0</b>", "E1.1 next, then E1 → E2 → E3",
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
         "open-source version tells you exactly where it stops. D1.0 names two "
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
      "pass from B2.3",
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
 "expect": "The tree, inventoried from disk rather than asserted — fourteen "
           "areas and every skill in them, counted from what was fetched. Then "
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
