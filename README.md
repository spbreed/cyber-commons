<h1>Cyber Commons</h1>

**A free, open commons for Cyber AI — the skills to defend *with* AI, and to
secure the AI *itself*.**

**120 lessons across 12 chapters.** Most are reading lessons — the idea, the
diagram, the control, and what it looks like in one running system — and then
they **run a skill**. 117 of the 120 do, and the code is not in the notebook:
the lesson shows the `SKILL.md` as prose and runs that skill's own script from
[`skills/`](skills/). Every one of the 120 is executed in CI before it ships,
and so is every skill. No licence, no vendor, no paid model account.

🌐 **[Live site](https://spbreed.github.io/cyber-commons/)** · 📓 [Notebooks](labs/notebooks/) · 📚 [Curriculum](curriculum/) · 🛠 [Skills](skills/) · 🤖 [Models](MODELS.md)

---

## Start here

1. Open [**A0.1**](https://spbreed.github.io/cyber-commons/lessons/A0.1.html) —
   the two free routes through the commons, what each one needs, and what the
   single code cell in every lesson is doing. Then
   [**A1.0**](https://spbreed.github.io/cyber-commons/lessons/A1.0.html).
2. On a lesson that carries a skill, press **▶ Run on Kaggle** — the notebook
   opens in *your* Kaggle account.
3. Switch **Internet** on in the settings panel, then press **Run All**.

That is the whole setup. A lesson fetches the skills tree — a shallow, sparse
clone, about three seconds — and runs one script out of it. Standard library
only, free CPU kernel, no model download, no API key, no GPU, no quota.

The clone needs **Internet on** in the notebook settings, which Kaggle gates on
a verified phone number. Without one, attach the dataset
[`cybercommons/cyber-commons-skills`](https://www.kaggle.com/datasets/cybercommons/cyber-commons-skills)
instead: same tree, no network, and the cell tells you so if the clone fails.

Locally, if you prefer: `python3 scripts/run_notebooks.py --session A1.0`

## What you actually build

A skill, in the sense this repository means it, is a **procedure an agent can
execute and you can check** — not a topic you have read about. So every lesson
ends in something that runs, and the curriculum ends in artefacts you keep.

**A lesson is shaped the same way every time:**

> **hook → framework → practical application**

A hook that is a consequence rather than a definition. Then the framework, as a
**diagram first** and the idea it names second — the why and the what belong to
a picture, only the how belongs to a terminal. Then the application: the idea
working, where it breaks, the control, and a check that it holds. Every chapter
closes on the gap it leaves, and names the next chapter as the answer.

The build **fails** on a lesson missing a hook, a diagram or a concept, and
[`check_lessons.py`](scripts/check_lessons.py) fails CI if a code cell ever
precedes the framework. [LESSON_DESIGN.md](LESSON_DESIGN.md) is the contract.

**Every one of those procedures is packaged as a real agent skill** in
[`skills/`](skills) — `SKILL.md` files with frontmatter, the format a coding
agent loads:

```bash
cp -r skills/appsec/appsec-vuln-audit ~/.claude/skills/
python3 scripts/check_skills.py --check   # parses, names, tools, contracts, routing
```

Each declares an **output contract**, which is what makes a skill checkable
rather than aspirational. Every skill lesson embeds its skill verbatim at build
time — so the lesson can never drift from the skill — and every one of the 120 carries
a script the lesson runs. Several build the contract shape from the data they
just produced and validate it, then show what the contract *cannot* see: **an
empty result conforms perfectly.** Conformance is a statement about the
serialiser; accuracy is the expensive part.

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
| [`appsec/`](skills/appsec) | 18 — the AI SDLC pipeline, stage by stage, including real Semgrep scoring and supply-chain decompilation |
| [`redteam/`](skills/redteam) · [`research/`](skills/research) | 14 — campaigns, reproducibility, corpus integrity, supply chain, published incidents |
| [`detection/`](skills/detection) · [`response/`](skills/response) · [`secops/`](skills/secops) | 21 — agent tempo, drift, fleet correlation, canaries, containment, stop authority |
| [`grc/`](skills/grc) · [`regulatory/`](skills/regulatory) · [`programme/`](skills/programme) | 27 — tiering, control mapping, obligations, disclosure, sequencing, metrics |
| [`attestation/`](skills/attestation) · [`architecture/`](skills/architecture) | 13 — turn a control claim into a signed statement bound to one deployment ([B2.13](labs/notebooks/B2.13.ipynb), run against 10 real OSS agent/MCP repos) |

## The programme

**One system, taught five ways.** Everything in the commons is grounded in
**CyberTravels** — a corporate travel company whose agentic platform is four
agents, two MCP servers, a set of direct APIs, agent-to-agent messaging
and a local std-I/O path on a developer's laptop. Every lesson says what its
idea looks like in that system, and a twelve-row risk register ties the whole
curriculum together.

Five functions, twelve chapters. **Each function opens with an introduction
lesson** that meets CyberTravels and asks its own question of it.

| Function | The question it asks of CyberTravels | Chapters | Lessons |
|---|---|---|---|
| **A · Securing AI Architectures** | what can go wrong here, and what closes it | [0](curriculum/track-a0.md) Running the commons · [1](curriculum/track-a1.md) CyberTravels' architecture and every risk it carries · [2](curriculum/track-a2.md) Identity and ingress · [3](curriculum/track-a3.md) Runtime and the gateway | 39 |
| **B · Application Security with an AI SDLC** | how do we review its code, at its speed | [4](curriculum/track-b2.md) The AI SDLC pipeline, before and after deploy | 15 |
| **C · Red Teaming and Security Research with AI** | can we break it before somebody else does | [5](curriculum/track-c1.md) Red teaming with AI · [6](curriculum/track-c2.md) Security research with AI | 15 |
| **D · The Agentic SOC** | would we see it happening, and could we stop it | [7](curriculum/track-d1.md) Detection · [8](curriculum/track-d2.md) Response | 21 |
| **E · AI Governance for Agentic Systems** | who signed off, and can they still evidence it | [9](curriculum/track-e1.md) The governance framework · [10](curriculum/track-e2.md) The governance platform · [11](curriculum/track-e3.md) Running the programme | 30 |
| | | **12 chapters** | **120** |

Nobody takes all of it. Everyone takes the **common spine** first — twenty
lessons, in order, that carry the vocabulary the rest runs on. Then the chapters
for the chair you sit in, then one adjacent chapter, because the failures happen
in the seams.

> **Spine:** A0.1 → A1.0 → A1.1 → A1.2 → A1.5 → **A1.10** → **A1.12** → A2.1 →
> A2.3 → A2.4 → A3.1 → A3.2 → A3.5 → **B2.0** → **B2.1** → B2.3 → **D1.0** →
> D1.5 → **E1.0** → E1.10

Two chapters carry a single artefact end to end:

- **[A1](curriculum/track-a1.md)** opens on CyberTravels as built, then the agentic
  reference architecture — drawn rather than coded — then one risk per lesson
  grounded in the OWASP Agentic Top 10, each naming the component of CyberTravels it
  attacks. It closes on the **CyberTravels risk register**: twelve risks, each
  with a scene, a component, a control and the lesson that owns it. Chapters 2
  and 3 are those controls.
- **[B2](curriculum/track-b2.md)** is the AI SDLC itself — a five-phase,
  fifteen-stage agentic AppSec pipeline built over seventeen sessions, attested in
  [B2.13](labs/notebooks/B2.13.ipynb) and closed in
  [B2.14](labs/notebooks/B2.14.ipynb) by scoring Google's Mantis against a
  held-out key — a reference implementation is something you evaluate, not
  something you trust.

Both directions run through every function: **AI for Security** (agents as your
instrument) and **Security of AI** (agents as the thing you defend). Teaching
only one produces a practitioner who gets surprised.

## Why you can trust the output

**Every one of the 120 notebooks has been run twice — here, and again on Kaggle
on a different machine — and printed exactly the same bytes.**

That second run is the claim worth making, because a kernel that prints nothing
also reports `complete`.
[`scripts/kaggle_verify.py`](scripts/kaggle_verify.py) compares each kernel's
remote stdout line-for-line against a fresh local run
([evidence](labs/notebooks/_kaggle_verified.json)). It caught two lessons whose
output depended on `PYTHONHASHSEED`; both are fixed, and
[`check_determinism.py`](scripts/check_determinism.py) now gates CI so the next
one is caught in nine seconds instead of after 120 remote pushes.

Two properties make that possible, and both are enforced by the build:

- **The code is in the repository.** A notebook shows the `SKILL.md` as prose
  and carries one cell that runs that skill's script out of the skills tree —
  the dataset attached to the Kaggle kernel, or the checkout. No
  library, nothing to clone, no `pip install`. So it runs air-gapped, and you
  can lift one cell into your own repository without inheriting a dependency.
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

## Changing a lesson

There is **one source of truth** and the notebooks, chapters and site pages are
all generated from it. Never hand-edit an `.ipynb`, a `curriculum/*.md` or a
`site/lessons/*.html`.

| To change… | Edit |
|---|---|
| Title, risk, control, tools, models | `site/data/curriculum.json` |
| The exercise: concept, code cells, "Your turn" | `scripts/exercises/track_<id>.py` |
| The skill a lesson teaches | `skills/<area>/<name>/SKILL.md` |
| The goal and the "Expect" line | `curriculum/labs.json` |
| Long-form notes under a lab | `lessons/<ID>.md` (optional) |
| The video | drop `recordings/<ID>.mp4` and push |

```bash
python3 scripts/build_notebooks.py && python3 scripts/build_curriculum.py
python3 scripts/run_notebooks.py     # prove they run; refreshes _results.json
python3 scripts/build_site.py
git add -A && git commit -m "lesson: A2.5" && git push
```

CI re-runs all of it with `--check` — secret scan, 120 notebooks, determinism
gate, skill contracts, every diagram rendered by real Graphviz and PlantUML, and
[`check_claims.py`](scripts/check_claims.py), which compares the counted claims
in this file against the tree they describe. Prose that counts the repository
goes stale silently; that one exists because it kept happening. CI fails on any
of it, so the notebook you read on the site is always the notebook that ran.
Pushing deploys the site.

**Credentials never go in this repository.** Kaggle tokens live in
`~/.kaggle/kaggle.json` or `$KAGGLE_USERNAME`/`$KAGGLE_KEY`; the push client
refuses to read a credential file inside the repo. Install the guard once:

```bash
./scripts/install-hooks.sh        # pre-commit secret scan; also runs in CI
```

## Layout

```
site/data/curriculum.json   source of truth: 120 sessions, 12 chapters
curriculum/                 generated chapter docs + labs.json (runnable commands)
scripts/exercises/          the lessons themselves, one module per track
skills/                     120 agent skills, plus _runtime/ — the one shared library
labs/notebooks/             120 generated notebooks + execution and Kaggle evidence
labs/                       attestation · incident-register · b2.10-eval-harness · a2-delegation · kimi
site/                       the website (index + generated lesson pages)
scripts/                    build_* · run_notebooks · check_{lessons,skills,secrets,determinism,register} · kaggle_*
```

## Licence & credits

Curriculum and site are open — contribute by PR. Tooling referenced throughout
belongs to its respective projects (CNCF, Linux Foundation, OWASP and others).
Model weights carry their own licences — Kimi K2 (modified MIT), GLM (MIT),
Llama (Meta Community Licence, read the restrictions). See [MODELS.md](MODELS.md).
