<h1>Cyber Commons</h1>

**Democratizing defensive AI cyber knowledge, before the hackers outrun us.**

A free, open commons for Cyber AI — the skills to defend *with* AI, and to
secure the AI *itself*.

**134 lessons across 14 chapters.** Every lesson is the idea, the diagram, the
control, and what it looks like in one running system — and then it **runs a
skill**. 131 of the 134 do, and the code is not in the notebook: the page shows
the `SKILL.md` as prose and the notebook runs that skill's own script out of
[`skills/`](skills/). Every one of the 134 is executed in CI before it ships,
and so is every skill. No licence, no vendor, no paid account, nothing to buy.

🌐 **[cybercommons.ai](https://cybercommons.ai)** · 📓 [Notebooks](labs/notebooks/) · 📚 [Curriculum](curriculum/) · 🛠 [Skills](skills/) · 🤖 [Models](MODELS.md) · 🎙 [Recording scripts](LIGHTBOARD.md)

---

# Start training

Three steps. The first two take about five minutes, and nothing is installed
until you decide you want it local.

## 1 · Read one page, so the rest makes sense

**[A0.1 — Start here](https://cybercommons.ai/lessons/A0.1.html)** is the whole
introduction on one page: who this is for, what a lesson is made of, which
track to open first, and what Day 0/1/2 mean. Then
**[A1.0](https://cybercommons.ai/lessons/A1.0.html)**, which introduces
CyberTravels — the one system every lesson is grounded in.

## 2 · Run your first lesson

Pick whichever route matches how you like to work. All three run the *same*
skill script; none of them need a paid account.

**Route A — in the browser, nothing installed.** Open any lesson page and press
**▶ Run on Kaggle**. The notebook opens as a new kernel in *your* Kaggle
account. Switch **Internet** on in the settings panel, then **Run All**. The
copy is yours to edit and nothing is written back here.

**Route B — locally. One clone, no dependencies.**

```bash
git clone https://github.com/spbreed/cyber-commons.git
cd cyber-commons
python3 scripts/run_notebooks.py --session A1.2   # prompt injection — well under a second
python3 scripts/run_notebooks.py                  # or all 134, about seven seconds
```

**Route C — in your own coding agent.** Skip the lessons and take the
procedures. Each is a real agent skill with frontmatter, in the format an agent
loads:

```bash
cp -r skills/appsec/appsec-vuln-audit ~/.claude/skills/
python3 scripts/check_skills.py --check   # what CI checks them against
```

Standard library only, free CPU kernel, no model download, no API key, no GPU,
no quota. A lesson fetches the skills tree — a shallow, sparse clone, about
three seconds — and runs one script out of it.

> **If the Kaggle clone fails with `Could not resolve host: github.com`**, that
> is the kernel, not the lesson: a Kaggle kernel starts with no network.
> Internet is gated on a verified phone number. Without one, attach the dataset
> [`cybercommons/cyber-commons-skills`](https://www.kaggle.com/datasets/cybercommons/cyber-commons-skills)
> instead — same tree, nothing fetched at all.

## 3 · Then take the spine, then your chapter

Nobody takes all 134. Everyone takes the **common spine** first — twenty
lessons, in order, that carry the vocabulary the rest runs on. Then the
chapters for the chair you sit in, then one adjacent chapter, because the
failures happen in the seams.

> **Spine:** A0.1 → A1.0 → A1.1 → A1.2 → A1.5 → **A1.10** → **A1.12** → A2.1 →
> A2.3 → A2.4 → A3.1 → A3.2 → A3.5 → **B2.0** → **B2.1** → B2.3 → **D1.0** →
> D1.3 → **E1.0** → E1.10

| If you are… | after the spine, open |
|---|---|
| a security architect, or you own the design review | **A2** and **A3** — identity and ingress, then runtime and the gateway |
| an AppSec engineer or you review agent-written code | **B2** — the AI SDLC, fifteen stages, built end to end |
| a red teamer or an eval engineer | **C1** — one red-team lifecycle, start to finish |
| in the SOC — detection, IR, threat hunting | **D1**→**D5** — discover, detect, understand, respond, recover |
| in GRC, risk, audit, or you carry the regulator | **E1**→**E3** — risk and control, regulatory, running the programme |

**Recording or teaching this?** [LIGHTBOARD.md](LIGHTBOARD.md) is a
**word-for-word** script for every lesson — open it and talk. Read every plain
line as written; never read a line in square brackets, which are the stage
directions. Five beats each, about two minutes, four hours in total, generated
from the same sources the lessons are. It tells you to record the six entry
points first: those carry an extra ground-rules beat for somebody who has never
shipped an agent, and every lesson after them assumes you said it.

---

## What a lesson is

Every page has the **same seven sections in the same order**, each with its own
colour and icon, so the shape of a page is learnable: read two and you know
where the framework is on the third without reading a heading.

| | section | what it does |
|---|---|---|
| ◉ | **Use case relevance** | a scene, not a summary — the consequence first |
| ◴ | **What this lesson is — Day 0, Day 1, Day 2** | why it matters · what you build · the number that says it worked |
| ▦ | **The framework, and how it works** | the diagram, then the idea it names |
| ▶ | **Real time execution as skill** | the `SKILL.md`, and the run |
| ✓ | **What you just proved** | what the output actually supports |
| ✎ | **Your turn** | the variation you run yourself |
| → | **Where this leaves you** | the gap this lesson leaves, and what answers it |

**Day 0, Day 1, Day 2 on every lesson**, because training that stops at the
technique leaves you with nothing to take to the person holding the budget.
Day 0 is why it is worth an afternoon. Day 1 is the concrete thing you stand
up. Day 2 is the number that keeps saying it worked. Where a lesson produces no
real number, it says so and names what you count instead — an invented figure
costs more credibility than an absent one.

**The framework comes before any code.** Teaching the how before the why is the
most common way a good lesson lands badly, so
[`check_lessons.py`](scripts/check_lessons.py) fails CI if a code step ever
precedes the framework. [LESSON_DESIGN.md](LESSON_DESIGN.md) is the full
contract.

**Notebooks are code only.** The prose lives on the page and nowhere else — it
was in both once, and the copy inside the notebook was the one nobody could
correct.

## What you actually build

A skill, in the sense this repository means it, is a **procedure an agent can
execute and you can check** — not a topic you have read about. So every lesson
ends in something that runs, and the curriculum ends in artefacts you keep.

Every procedure is packaged as a real agent skill in [`skills/`](skills) —
`SKILL.md` files with frontmatter, the format a coding agent loads. Each
declares an **output contract**, which is what makes a skill checkable rather
than aspirational. Every skill lesson embeds its skill verbatim at build time —
so the lesson can never drift from the skill — and every one of the 139 carries
a script the lesson runs.

Several build the contract shape from the data they just produced and validate
it, then show what the contract *cannot* see: **an empty result conforms
perfectly.** Conformance is a statement about the serialiser; accuracy is the
expensive part.

```bash
python3 scripts/check_skills.py --check  # parses, names, tools, contracts, routing
python3 scripts/test_skills.py  --check  # runs every script, offline, stripped env
```

Both gate CI. The second one exists because loading a skill is not running it:
it executes each script in a subprocess with the model and cloud variables
removed, and a script that runs and prints nothing counts as a failure.

| area | what it holds |
|---|---|
| [`threats/`](skills/threats) | 16 — one check per risk in the OWASP-grounded chapter: instruction channels, memory scope, tool abuse, blast radius, attribution |
| [`identity/`](skills/identity) | 5 — attestation, delegation, the non-human identity lifecycle, tamper-evident logging |
| [`runtime/`](skills/runtime) | 6 — sandbox containment, budgets, return validation, shared surfaces, exemptions, escalation |
| [`appsec/`](skills/appsec) | 20 — the AI SDLC pipeline, stage by stage, including real Semgrep scoring and supply-chain decompilation |
| [`redteam/`](skills/redteam) · [`research/`](skills/research) | 14 — campaigns, reproducibility, corpus integrity, supply chain, published incidents |
| [`detection/`](skills/detection) · [`response/`](skills/response) · [`secops/`](skills/secops) | 21 — agent tempo, drift, fleet correlation, canaries, containment, stop authority |
| [`grc/`](skills/grc) · [`regulatory/`](skills/regulatory) · [`programme/`](skills/programme) | 27 — tiering, control mapping, obligations, disclosure, sequencing, metrics |
| [`attestation/`](skills/attestation) · [`architecture/`](skills/architecture) | 14 — turn a control claim into a signed statement bound to one deployment ([B2.18](labs/notebooks/B2.18.ipynb), run against 10 real OSS agent/MCP repos) |

## The programme

**One system, taught five ways.** Everything in the commons is grounded in
**CyberTravels** — a fictional corporate travel company whose agentic platform
is four agents, two MCP servers, a set of direct APIs, agent-to-agent messaging
and a local std-I/O path on a developer's laptop. Every lesson says what its
idea looks like in that system, and a twelve-row risk register ties the whole
curriculum together.

That is a deliberate constraint, not a shortage of examples. The refund limit
an attacker walks past in A1.2 is the same one a detection watches in Function
D and a report counts in Function E. By the fourth function you are not
learning a fourth example — you are watching a system you already understand
fail in a new way.

Five functions, fourteen chapters. **Each function opens with an introduction
lesson** that meets CyberTravels and asks its own question of it.

| Function | The question it asks of CyberTravels | Chapters | Lessons |
|---|---|---|---|
| **A · Securing AI Architectures** | what can go wrong here, and what closes it | [A0](curriculum/track-a0.md) Introduction · [A1](curriculum/track-a1.md) Architecture and every risk · [A2](curriculum/track-a2.md) Identity and ingress · [A3](curriculum/track-a3.md) Runtime and the gateway | 40 |
| **B · Application Security with an AI SDLC** | how do we review its code, at its speed | [B2](curriculum/track-b2.md) The AI SDLC pipeline, and agentic pentesting | 20 |
| **C · Agentic Evaluation and Red Teaming** | can we break it before somebody else does | [C1](curriculum/track-c1.md) One red-team lifecycle, end to end | 12 |
| **D · The Agentic SOC** | would we see it happening, and could we stop it | [D1](curriculum/track-d1.md) Discover · [D2](curriculum/track-d2.md) Detect · [D3](curriculum/track-d3.md) Understand · [D4](curriculum/track-d4.md) Respond · [D5](curriculum/track-d5.md) Recover and root cause | 31 |
| **E · AI Governance for Agentic Systems** | who signed off, and can they still evidence it | [E1](curriculum/track-e1.md) Risk and control · [E2](curriculum/track-e2.md) Regulatory and compliance · [E3](curriculum/track-e3.md) Running the programme | 31 |
| | | **14 chapters** | **134** |

Chapters are cited by id and never by number — the ordinal is rendered nowhere
and goes stale the moment one is inserted.

Two chapters carry a single artefact end to end:

- **[A1](curriculum/track-a1.md)** opens on CyberTravels as built, then the agentic
  reference architecture — drawn rather than coded — then one risk per lesson
  grounded in the OWASP Agentic Top 10, each naming the component of CyberTravels it
  attacks. It closes on the **CyberTravels risk register**: twelve risks, each
  with a scene, a component, a control and the lesson that owns it. Chapters A2
  and A3 are those controls.
- **[B2](curriculum/track-b2.md)** is the AI SDLC itself — a five-phase,
  fifteen-stage agentic AppSec pipeline built over seventeen sessions, attested in
  [B2.18](labs/notebooks/B2.18.ipynb) and closed in
  [B2.19](labs/notebooks/B2.19.ipynb) by scoring Google's Mantis against a
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

**Every one of the 134 notebooks has been run twice — here, and again on Kaggle
on a different machine — and printed exactly the same bytes.**

That second run is the claim worth making, because a kernel that prints nothing
also reports `complete`.
[`scripts/kaggle_verify.py`](scripts/kaggle_verify.py) compares each kernel's
remote stdout line-for-line against a fresh local run
([evidence](labs/notebooks/_kaggle_verified.json)). It caught two lessons whose
output depended on `PYTHONHASHSEED`; both are fixed, and
[`check_determinism.py`](scripts/check_determinism.py) now gates CI so the next
one is caught in nine seconds instead of after 134 remote pushes.

Two properties make that possible, and both are enforced by the build:

- **The code is in the repository.** A notebook carries one cell that runs a
  skill's script out of the skills tree — the dataset attached to the Kaggle
  kernel, or the checkout. No library, nothing to install, no `pip install`. So
  it runs air-gapped, and you can lift one cell into your own repository
  without inheriting a dependency.
- **Deterministic.** Seed from `zlib.crc32`, not `hash()`; give every sort a
  full tiebreak. Byte-identical output from two machines is what makes drift a
  finding rather than noise.

Where a lesson names a tool you would really deploy — SPIRE, OPA, Falco,
Keycloak, garak — the notebook models the *decision* that tool makes, and
[`curriculum/labs.json`](curriculum/labs.json) keeps the real invocation
underneath as the full-infrastructure variant. Those variants are **not**
executed in CI and are labelled as such.

**Where a skill calls a model, the same code runs two ways.** Offline it uses a
deterministic stand-in, labelled as a stand-in everywhere it appears and never
presented as a model's output — which is what lets it run on Kaggle with the
replay and keeps the determinism gate meaningful. Set one environment
variable and the identical code calls a real model:

```bash
# any OpenAI-compatible endpoint — llama.cpp, Ollama, vLLM, a free hosted tier
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1 OPENAI_API_KEY=local MODEL=qwen2.5-7b-instruct
```

**There is no paid backend.** A curriculum that is free to read should be free
to run, so there is one protocol and the weights come from Kaggle Models. The
adapter is standard library only, lives inside the seven skill scripts that
call a model rather than in any lesson, and **never silently substitutes**: if a
backend is configured and the call fails, the lesson says so and labels what it
used. `scripts/live_model_test.py` runs all seven against a served endpoint and
records what came back.

See [MODELS.md](MODELS.md) for which model suits which lab, and
[labs/kimi/](labs/kimi) for what happened when these skills were run against a
Kimi-family model on Kaggle — including the parts that did not work.

## Contributing, or changing a lesson

[CLAUDE.md](CLAUDE.md) is the operational entry point — what is generated, the
build order, the gates, and the failures each one exists to prevent. Read it
before your first change.

There is **one source of truth** and the notebooks, chapters and site pages are
all generated from it. Never hand-edit an `.ipynb`, a `curriculum/*.md`, a
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
python3 scripts/build_notebooks.py     # exercises       -> labs/notebooks/
python3 scripts/run_notebooks.py       # notebooks       -> recorded output
python3 scripts/render_diagrams.py     # emitted DOT     -> site/assets/diagrams/
python3 scripts/build_curriculum.py    # curriculum.json -> curriculum/track-*.md
python3 scripts/build_site.py          # everything      -> site/lessons/
python3 scripts/build_lightboard.py    # lessons         -> LIGHTBOARD.md
```

CI re-runs all of it with `--check`. It runs 18 scripts, each of which
exists because of a specific failure: the secret scan, all 134 notebooks
executed, the determinism gate across four hash seeds, skill contracts and a
real offline run of every skill script, every diagram rendered by actual
Graphviz and PlantUML, a clarity pass over the *rendered* page, a contrast pass
that measures text against the background actually painted behind it, and
[`check_claims.py`](scripts/check_claims.py), which compares every counted
claim in this file against the tree it describes. Prose that counts the
repository goes stale silently; that gate exists because it kept happening.

Pushing to `main` or `claude/**` deploys the site.

**Credentials and personal identifiers never go in this repository.** Kaggle
tokens live in `~/.kaggle/kaggle.json` or `$KAGGLE_USERNAME`/`$KAGGLE_KEY`, and
the push client refuses to read a credential file inside the tree. Install the
guard once:

```bash
./scripts/install-hooks.sh        # pre-commit scan; also gate 1 in CI
```

## Layout

```
site/data/curriculum.json   source of truth: 134 sessions, 14 chapters
curriculum/                 generated chapter docs + labs.json + frameworks.json
scripts/exercises/          the lessons themselves, one module per track
cybertravels/               the sample repository: A1.1's architecture as source,
                            with cybertravels/LABELS.md as the ground truth
skills/                     139 agent skills, plus _runtime/ — the one shared library
labs/notebooks/             134 generated notebooks + execution and Kaggle evidence
labs/                       attestation · incident-register · b2.10-eval-harness · a2-delegation · kimi
site/                       the website (index + generated lesson pages)
scripts/                    build_* · run_notebooks · check_* · kaggle_*
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
