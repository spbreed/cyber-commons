<h1>Cyber Commons</h1>

**Democratizing defensive AI cyber knowledge, before the hackers outrun us.**

A free, open commons for Cyber AI — the skills to defend *with* AI, and to
secure the AI *itself*.

**148 lessons across 16 chapters.** Every lesson is the idea, the diagram, the
control, and what it looks like in one running system — and then it **runs a
skill**. 147 of the 148 do, and the skill is the deliverable: the page shows the
`SKILL.md` as prose and you run that skill's own script out of
[`skills/`](skills/), on your own machine, in whichever agent CLI you already
use. Every skill is executed in CI before it ships. **Every skill is executed
by a language model** — the
script is the harness, not the procedure — so there is one prerequisite, and
[A0.0](https://cybercommons.ai/lessons/A0.0.html) sets it up on a free tier. No
licence, no vendor, no paid plan required.

🌐 **[cybercommons.ai](https://cybercommons.ai)** · 📚 [Curriculum](curriculum/) · 🛠 [Skills](skills/) · 🤖 [Models](MODELS.md) · 🎙 [Recording scripts](LIGHTBOARD.md)

---

# Start training

Three steps. The first two take about five minutes, and nothing is installed
until you decide you want it local.

## 1 · Set your machine up — this is the one that blocks everything

**[A0.0 — Set up your machine](https://cybercommons.ai/lessons/A0.0.html)**
compares the developer AI tools on the two things that decide the choice (real
context window, and what the free tier gets you), then installs, clones, and
points the skill runtime at a model. It ends by running one skill end to end
and printing which model answered.

**If you already use Claude Code, you need no API key and no endpoint.** The
runtime finds the signed-in `claude` CLI and runs every skill on that session —
the same authentication your editor uses.

```bash
git clone --branch master https://github.com/spbreed/cyber-commons.git
cd cyber-commons

claude --version        # prints a version? then there is nothing to configure

PYTHONPATH=skills/_runtime python3 \
  skills/programme/dev-environment-preflight/scripts/dev_environment_preflight.py
```

**Or bring your own model** — a local one, or any hosted free tier. Setting
`OPENAI_BASE_URL` overrides the CLI, because somebody who set it meant it:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve & ollama pull qwen2.5:1.5b-instruct
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1   # the /v1 is not optional
export OPENAI_API_KEY=ollama
export MODEL=qwen2.5:1.5b-instruct
```

**With neither, every skill exits 2 and says so.** Nothing here substitutes a
canned answer for a model's: an answer of that kind has the right shape, passes
the contract, and is not a model result.

## 2 · Read one page, then run a lesson

**[A0.1](https://cybercommons.ai/lessons/A0.1.html)** is the whole introduction
on one page: who this is for, what a lesson is made of, which track to open
first, and what Day 0/1/2 mean. Then
**[B1.0](https://cybercommons.ai/lessons/B1.0.html)**, which introduces
CyberTravels — the one system every lesson is grounded in.

Every lesson page carries the exact command. Run it against the skill's
committed fixture:

```bash
python3 skills/threats/instruction-channel-check/scripts/instruction_channel_check.py   # B1.2, prompt injection
```

**Or install the skills into your own agent and ask in your own words.** Each
is a real agent skill in the [agentskills.io](https://agentskills.io) format,
which any skills-compatible agent loads. One command links all of them into
every CLI you have:

```bash
python3 scripts/install_skills.py --all     # Claude Code, Codex, Gemini, Cursor, opencode, goose
python3 scripts/install_skills.py --list    # what is linked where
```

These are **symlinks into this repository**, not copies — `git pull` updates
every tool at once, and a fix you make here is live in all of them with no sync
step. Then open your agent in any directory and ask for the skill by name:

```
> use instruction-channel-check on this MCP tool description
```

Standard library only — there is nothing to `pip install`. The dependency is
the model, not a package tree.

## 3 · Then take the spine, then your chapter

Nobody takes all 148. Everyone takes the **common spine** first — twenty-four
lessons, in order, that carry the vocabulary the rest runs on. It opens by
setting your machine up and building the agent, because every control in the
five functions after it attaches to a mechanism you will have written. Then the
chapters for the chair you sit in, then one adjacent chapter, because the
failures happen in the seams.

> **Spine:** **A0.0** → A0.1 → **A1.0** → A1.1 → A1.3 → A1.4 → A2.0 →
> **A2.4** → B1.0 → B1.1 → B1.2 → **B1.10** → **B1.12** → B2.1 → B2.3 →
> B2.4 → B3.1 → B3.2 → B3.5 → **C2.0** → C2.3 → **E1.0** → **F1.0** → F1.10

| If you are… | after the spine, open |
|---|---|
| building an agentic feature, and new to all of it | **A1** and **A2** — the loop and the tools, then the harness around them |
| a security architect, or you own the design review | **B2** and **B3** — identity and ingress, then runtime and the gateway |
| an AppSec engineer or you review agent-written code | **C2** — the AI SDLC, fifteen stages, built end to end |
| a red teamer or an eval engineer | **D1** — one red-team lifecycle, start to finish |
| in the SOC — detection, IR, threat hunting | **E1**→**E5** — discover, detect, understand, respond, recover |
| in GRC, risk, audit, or you carry the regulator | **F1**→**F3** — risk and control, regulatory, running the programme |

**Recording or teaching this?** [LIGHTBOARD.md](LIGHTBOARD.md) is a
**word-for-word** script for every lesson — open it and talk. Read every plain
line as written; never read a line in square brackets, which are the stage
directions. Five beats each, about two minutes, four hours in total, generated
from the same sources the lessons are. It tells you to record the seven entry
points first: those carry an extra ground-rules beat for somebody who has never
shipped an agent, and every lesson after them assumes you said it.

---

## What a lesson is

Every page draws from the **same sections in the same order**, each with its own
colour and icon, so the shape of a page is learnable: read two and you know
where the framework is on the third without reading a heading. A page shows a
section where the lesson has something to put in it and leaves it out where it
does not — the dev-environment setup page has no Risk, no Day table and no
CyberTravels scene, because its subject is your laptop.

| | section | what it does |
|---|---|---|
| ◉ | **Use case relevance** | a scene, not a summary — the consequence first |
| ◴ | **What this lesson is — Day 0, Day 1, Day 2** | why it matters · what you build · the number that says it worked |
| ▦ | **The framework, and how it works** | the diagram, then the idea it names |
| ▶ | **Real time execution as skill** | the `SKILL.md`, and the run |
| ✓ | **What you just proved** | what the output actually supports |
| ✎ | **Your turn** | the variation you run yourself |
| → | **Where this leaves you** | the gap this lesson leaves, and what answers it |

**Day 0, Day 1, Day 2 on every lesson about the system** — 146 of the 148 —
because training that stops at the technique leaves you with nothing to take to
the person holding the budget.
Day 0 is why it is worth an afternoon. Day 1 is the concrete thing you stand
up. Day 2 is the number that keeps saying it worked. Where a lesson produces no
real number, it says so and names what you count instead — an invented figure
costs more credibility than an absent one.

**The framework comes before any code.** Teaching the how before the why is the
most common way a good lesson lands badly, so
[`check_lessons.py`](scripts/check_lessons.py) fails CI if a code step ever
precedes the framework. [LESSON_DESIGN.md](LESSON_DESIGN.md) is the full
contract.

**The prose lives on the page and nowhere else.** It was duplicated into a
generated artefact once, and the copy nobody could correct was the one readers
found first.

## What you actually build

A skill, in the sense this repository means it, is a **procedure an agent can
execute and you can check** — not a topic you have read about. So every lesson
ends in something that runs, and the curriculum ends in artefacts you keep.

Every procedure is packaged as a real agent skill in [`skills/`](skills), in
the [agentskills.io](https://agentskills.io) format — `SKILL.md` with
frontmatter, which any skills-compatible agent loads. Each declares an **output
contract**, which is what makes a skill checkable rather than aspirational, and
every one of the 139 carries a script the lesson runs.

**The script is the harness, not the procedure.** It assembles the fixture,
hands the model that skill's own `SKILL.md` and contract, and validates the
reply against the same contract. The documentation and the prompt are the same
bytes, so a skill cannot be well written and do something else. Every lesson
embeds its skill verbatim at build time, so the page cannot drift either.

Several build the contract shape from the data they just produced and validate
it, then show what the contract *cannot* see: **an empty result conforms
perfectly.** Conformance is a statement about the serialiser; accuracy is the
expensive part.

```bash
python3 scripts/check_skills.py --check  # parses, names, tools, contracts, routing
python3 scripts/test_skills.py  --check  # runs every script, offline, stripped env
```

Both gate CI, and the second one changed meaning when every skill became
model-backed. **CI is given no model endpoint on purpose**, so what it proves
now is that no skill answers without one: each script must exit 2 *having said
why*. Exiting 0 with output fails, and exiting 2 with no explanation fails too
— a reader who sees a bare traceback concludes the repository is broken rather
than that their machine is unconfigured.

A stand-in that is allowed to answer is the one failure nothing downstream
catches: it has the right shape, it passes the contract, and it is not a model
result. So there is no stand-in.

| area | what it holds |
|---|---|
| [`threats/`](skills/threats) | 16 — one check per risk in the OWASP-grounded chapter: instruction channels, memory scope, tool abuse, blast radius, attribution |
| [`identity/`](skills/identity) | 5 — attestation, delegation, the non-human identity lifecycle, tamper-evident logging |
| [`runtime/`](skills/runtime) | 6 — sandbox containment, budgets, return validation, shared surfaces, exemptions, escalation |
| [`appsec/`](skills/appsec) | 20 — the AI SDLC pipeline, stage by stage, including real Semgrep scoring and supply-chain decompilation |
| [`redteam/`](skills/redteam) · [`research/`](skills/research) | 14 — campaigns, reproducibility, corpus integrity, supply chain, published incidents |
| [`detection/`](skills/detection) · [`response/`](skills/response) · [`secops/`](skills/secops) | 21 — agent tempo, drift, fleet correlation, canaries, containment, stop authority |
| [`grc/`](skills/grc) · [`regulatory/`](skills/regulatory) · [`programme/`](skills/programme) | 27 — tiering, control mapping, obligations, disclosure, sequencing, metrics |
| [`attestation/`](skills/attestation) · [`architecture/`](skills/architecture) | 14 — turn a control claim into a signed statement bound to one deployment ([C2.18](https://cybercommons.ai/lessons/C2.18.html), run against 10 real OSS agent/MCP repos) |

## The programme

**One system, taught five ways.** Everything in the commons is grounded in
**CyberTravels** — a fictional corporate travel company whose agentic platform
is four agents, two MCP servers, a set of direct APIs, agent-to-agent messaging
and a local std-I/O path on a developer's laptop. Every lesson says what its
idea looks like in that system, and a twelve-row risk register ties the whole
curriculum together.

That is a deliberate constraint, not a shortage of examples. The refund limit
an attacker walks past in B1.2 is the same one a detection watches in Function
D and a report counts in Function E. By the fourth function you are not
learning a fourth example — you are watching a system you already understand
fail in a new way.

Five functions, fourteen chapters. **Each function opens with an introduction
lesson** that meets CyberTravels and asks its own question of it.

| Function | The question it asks of CyberTravels | Chapters | Lessons |
|---|---|---|---|
| **A · Securing AI Architectures** | what can go wrong here, and what closes it | [A0](curriculum/track-a0.md) Introduction · [B1](curriculum/track-b1.md) Architecture and every risk · [B2](curriculum/track-b2.md) Identity and ingress · [B3](curriculum/track-b3.md) Runtime and the gateway | 40 |
| **B · Application Security with an AI SDLC** | how do we review its code, at its speed | [C2](curriculum/track-c2.md) The AI SDLC pipeline, and agentic pentesting | 20 |
| **C · Agentic Evaluation and Red Teaming** | can we break it before somebody else does | [D1](curriculum/track-d1.md) One red-team lifecycle, end to end | 12 |
| **D · The Agentic SOC** | would we see it happening, and could we stop it | [E1](curriculum/track-e1.md) Discover · [E2](curriculum/track-e2.md) Detect · [E3](curriculum/track-e3.md) Understand · [E4](curriculum/track-e4.md) Respond · [E5](curriculum/track-e5.md) Recover and root cause | 31 |
| **E · AI Governance for Agentic Systems** | who signed off, and can they still evidence it | [F1](curriculum/track-f1.md) Risk and control · [F2](curriculum/track-f2.md) Regulatory and compliance · [F3](curriculum/track-f3.md) Running the programme | 31 |
| | | **14 chapters** | **134** |

Chapters are cited by id and never by number — the ordinal is rendered nowhere
and goes stale the moment one is inserted.

Two chapters carry a single artefact end to end:

- **[B1](curriculum/track-b1.md)** opens on CyberTravels as built, then the agentic
  reference architecture — drawn rather than coded — then one risk per lesson
  grounded in the OWASP Agentic Top 10, each naming the component of CyberTravels it
  attacks. It closes on the **CyberTravels risk register**: twelve risks, each
  with a scene, a component, a control and the lesson that owns it. Chapters B2
  and B3 are those controls.
- **[C2](curriculum/track-c2.md)** is the AI SDLC itself — a five-phase,
  fifteen-stage agentic AppSec pipeline built over seventeen sessions, attested in
  [C2.18](https://cybercommons.ai/lessons/C2.18.html) and closed in
  [C2.19](https://cybercommons.ai/lessons/C2.19.html) by scoring Google's Mantis against a
  held-out key — a reference implementation is something you evaluate, not
  something you trust.

Both directions run through every function: **AI for Security** (agents as your
instrument) and **Security of AI** (agents as the thing you defend). Teaching
only one produces a practitioner who gets surprised.

Every lesson is mapped to **OWASP**, **MITRE ATLAS**, **NIST AI RMF** and the
**EU AI Act** in [`curriculum/frameworks.json`](curriculum/frameworks.json),
and every label links to a real authoritative source — CI checks both that the
label exists upstream and that the link resolves.

## Why you can trust the output

**Every one of the 139 skills executes in CI, and none of them is allowed to
answer without a model.**

That second half is the claim worth making. CI is given no model endpoint on
purpose, so every skill refuses there — legibly, with the reason — and
`test_skills.py` fails any script that exits 0 with output instead. A canned
answer returned in a model's place is the one failure nothing downstream can
catch: it has the right shape, it passes the contract, and it is not a model
result. So there is no canned answer.

**What this repository no longer claims.** It used to say every lesson had
been run twice, on two machines, and printed exactly the same bytes. That was
true when the skills computed their own answers. It is not true now: a model is
not deterministic, and two runs of the same skill against the same fixture will
differ. Saying otherwise would be the most misleading thing on this page.

What is still checked, and still worth checking:

- **The harness is deterministic.** Ordering, formatting, seeding, and the
  refusal itself. [`check_determinism.py`](scripts/check_determinism.py) runs
  every skill script across four hash seeds and compares — a refusal that varies
  means something unordered reached the message. Seed from `zlib.crc32`, not
  `hash()`; give every sort a full tiebreak.
- **Every reply is validated against the skill's own output contract**, and the
  violations are printed rather than raised. What the model actually said is
  the evidence; hiding it behind a traceback removes the only thing worth
  looking at.
- **Every finding names the model that produced it.** A result that does not say
  which model answered cannot be reproduced or compared — and the whole point is
  that a different model answers differently.

Where a lesson names a tool you would really deploy — SPIRE, OPA, Falco,
Keycloak, garak — the skill models the *decision* that tool makes, and
[`curriculum/labs.json`](curriculum/labs.json) keeps the real invocation
underneath as the full-infrastructure variant. Those variants are **not**
executed in CI and are labelled as such.

**Two backends, no paid path.** A signed-in Claude Code CLI answers with no key
and no endpoint — which is also how the [agentskills.io](https://agentskills.io)
format is meant to be used, an agent loading a `SKILL.md` and carrying out the
procedure. For everything else, one protocol:

```bash
# llama.cpp, Ollama, vLLM, or a hosted free tier — pick one
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1 OPENAI_API_KEY=ollama MODEL=qwen2.5:1.5b-instruct
```

**There is no paid backend, and no silent substitute.** A curriculum that is
free to read should be free to run, so the default path is an open-weight model
you serve yourself. If the endpoint is missing the skill exits 2 and says so; if
the call fails it raises with what the server actually returned. It never
answers in the model's place.

**Small models are part of the lesson, not a compromise.** A 1.5B model will
fill a contract with plausible values it did not derive, and will sometimes
return prose where JSON was asked for. That is visible in the output, it is
counted in the contract violations, and it is the reason every finding names
the model that produced it.

See [MODELS.md](MODELS.md) for which model suits which lab, and what each one
costs you in contract violations.

## Contributing, or changing a lesson

[CLAUDE.md](CLAUDE.md) is the operational entry point — what is generated, the
build order, the gates, and the failures each one exists to prevent. Read it
before your first change.

There is **one source of truth** and the chapters, site pages and recording
script are all generated from it. Never hand-edit a `curriculum/*.md`, a
`site/lessons/*.html` or `LIGHTBOARD.md`.

| To change… | Edit |
|---|---|
| Title, risk, control, tools, models | `site/data/curriculum.json` |
| The exercise: concept, steps, "Your turn" | `scripts/exercises/track_<id>.py` |
| The hook, or the ASCII diagram | `scripts/exercises/framing*.py` |
| Day 0 / Day 1 / Day 2 | `scripts/exercises/days.py` |
| The CyberTravels grounding line | `scripts/exercises/cybertravels.py` |
| The skill a lesson teaches | `skills/<area>/<name>/SKILL.md` |
| The goal and the "Expect" line | `curriculum/labs.json` |
| The framework mapping | `curriculum/frameworks.json` |

Dependencies run downhill — after changing a source, run from its row down:

```bash
python3 scripts/render_diagrams.py     # emitted DOT     -> site/assets/diagrams/
python3 scripts/build_curriculum.py    # curriculum.json -> curriculum/track-*.md
python3 scripts/build_site.py          # everything      -> site/lessons/
python3 scripts/build_lightboard.py    # lessons         -> LIGHTBOARD.md
```

CI re-runs all of it with `--check`. It runs 21 scripts, each of which
exists because of a specific failure: the secret scan, the determinism gate
across four hash seeds, skill contracts and a
real offline run of every skill script, every diagram rendered by actual
Graphviz and PlantUML, a clarity pass over the *rendered* page, a contrast pass
that measures text against the background actually painted behind it, and
[`check_claims.py`](scripts/check_claims.py), which compares every counted
claim in this file against the tree it describes. Prose that counts the
repository goes stale silently; that gate exists because it kept happening.

Pushing to `main` or `claude/**` deploys the site.

**Credentials and personal identifiers never go in this repository.** An API
key for a hosted model lives in your shell, sourced per command, and never in a
file inside the tree. Install the guard once:

```bash
./scripts/install-hooks.sh        # pre-commit scan; also gate 1 in CI
```

## Layout

```
site/data/curriculum.json   source of truth: 148 sessions, 14 chapters
curriculum/                 generated chapter docs + labs.json + frameworks.json
scripts/exercises/          the lessons themselves, one module per track
cybertravels/               the sample repository: B1.1's architecture as source,
                            with cybertravels/LABELS.md as the ground truth
skills/                     139 agent skills, plus _runtime/ — the one shared library
labs/                       attestation · incident-register · b2.10-eval-harness · b2-delegation
labs/evidence/              the recorded offline run of every skill script
site/                       the website (index + generated lesson pages)
scripts/                    build_* · check_* · install_skills.py
CLAUDE.md                   how to work in this repo · LESSON_DESIGN.md — the authoring contract
LIGHTBOARD.md               generated recording script, one per lesson
```

`labs/b2.10-eval-harness/` is a **separate subsystem**: *vulnbench*, which
scores an AI security harness's findings against ground truth. It has its own
entrypoint and its own rules — see §8 of [CLAUDE.md](CLAUDE.md).

## Licence & credits

Curriculum and site are open — contribute by PR. Tooling referenced throughout
belongs to its respective projects (CNCF, Linux Foundation, OWASP and others).
Model weights carry their own licences — Kimi K2 (modified MIT), GLM (MIT),
Llama (Meta Community Licence, read the restrictions). See [MODELS.md](MODELS.md).
