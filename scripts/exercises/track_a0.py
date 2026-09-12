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
   [`skills/`](https://github.com/spbreed/cyber-commons/tree/claude/vulnbench-setup-scheduling-81aqov/skills).
   Frontmatter tells an agent when to load the procedure; the markdown reads as
   a checklist for a person.
6. **Run it → Out** — one cell of about twenty lines, and the real recorded
   output of running it. The notebook holds no procedure: it finds the skills
   tree, cloning it if needed, and runs the script as a subprocess. That is why
   a fix to a procedure is one edit to one file rather than a rebuild of every
   notebook.
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
         "A lesson's procedure is a file in `skills/`, and the notebook fetches "
         "and runs it. On your own machine the tree is already there because "
         "you cloned it. On a hosted kernel it is not, and the fetch needs the "
         "kernel's network switched on — one checkbox, and the only "
         "prerequisite anybody gets stuck on.\\n\\n"
         "**GitHub** — clone once, run anything, nothing to configure, no "
         "network needed:\\n\\n"
         "```bash\\n"
         "git clone https://github.com/spbreed/cyber-commons\\n"
         "cd cyber-commons\\n"
         "python3 scripts/run_notebooks.py --session A0.1   # this lesson\\n"
         "python3 scripts/run_notebooks.py                  # or all of them\\n"
         "```\\n\\n"
         "**Kaggle** — every lesson page carries a **Run on Kaggle** button. "
         "Open it, switch **Internet** to *on* in the settings panel, run the "
         "cell. Kaggle gates that toggle on a verified phone number; without "
         "one, attach the dataset `cybercommons/cyber-commons-skills` in the "
         "same panel and the cell finds the tree at the mount point instead. "
         "The first run spends about three seconds on a shallow sparse clone; "
         "every run after that is instant.\\n\\n"
         "The **Out** block on every lesson page is a real run, not a pasted "
         "transcript: `run_notebooks.py` executes the notebook here, "
         "`kaggle_verify.py` runs the same notebook on Kaggle, and the two are "
         "compared byte for byte. If you get something else, one of us has a "
         "bug worth reporting."),

  *skill_steps("programme/lesson-preflight",
               "## 6 · The whole mechanism, demonstrated on itself\\n\\n"
               "The rest of this lesson is the mechanism running. The skill "
               "below is a preflight: it inventories the tree this host "
               "fetched, then runs a real lesson's procedure three times — "
               "twice in the two ways it actually breaks, once correctly.\\n\\n"
               "The two failures are the two you will meet. **(a)** is a host "
               "with no network and nothing fetched. **(b)** is a tree that "
               "arrived but a shared library that is not on the import path: "
               "some skills import the runtime rather than carrying a copy, "
               "and the lesson cell is what puts it there.\\n\\n"
               "Every number below is counted from the tree that was actually "
               "fetched rather than written into this page — which is why "
               "they move as the commons grows.\\n\\n"
               "The procedure it runs correctly in **(c)** is A1.2's, so what "
               "you see below is literally a later lesson's output."),
 ],
 "expect": "The tree, inventoried from disk rather than asserted — fourteen "
           "areas and every skill in them, counted from what was fetched. Then "
           "the same procedure failing twice and working once: exit 2 with "
           "`[Errno 2]` when nothing was fetched, exit 1 with "
           "`ModuleNotFoundError` when the runtime is off the path, and exit 0 "
           "with twelve lines and a CRC when both conditions hold. `ready` is "
           "true only because both failures were reproduced; a preflight that "
           "shows only the success has tested one path in three.",
 "challenge": "Run it on the other route. If you read this on Kaggle, clone the "
              "repository and run the same command locally; if you read it "
              "locally, press **Run on Kaggle**. Compare the CRC on the last "
              "line — it should be identical, because the procedure is the same "
              "file in both cases. If it is not, you have found either a "
              "non-determinism in the procedure or a difference between the "
              "hosts, and both are worth an issue.",
},

}
