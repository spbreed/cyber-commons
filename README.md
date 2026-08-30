<h1>Cyber Commons</h1>

**A free, open commons for Cyber AI — the skills to defend *with* AI, and to
secure the AI *itself*.**

**121 lessons across 12 chapters.** Every lesson is a self-contained Python
notebook that runs in a browser on the standard library alone, and is executed
in CI before it ships. No licence, no vendor, no frontier-lab account.

🌐 **[Live site](https://spbreed.github.io/cyber-commons/)** · 📓 [Notebooks](labs/notebooks/) · 📚 [Curriculum](curriculum/) · 🛠 [Skills](skills/) · 🤖 [Models](MODELS.md)

---

## Start here

1. Open [**A1.0**](https://spbreed.github.io/cyber-commons/lessons/A1.0.html).
2. Press **▶ Run on Kaggle** — the notebook opens in *your* Kaggle account.
3. Press **Run All**.

That is the whole setup. The notebooks are standard-library only, so they run on
a free CPU kernel **with the internet switched off** — no model download, no API
key, no GPU, no quota. A lesson takes seconds.

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

**Twenty-two of those procedures are packaged as real agent skills** in
[`skills/`](skills) — `SKILL.md` files with frontmatter, the format a coding
agent loads:

```bash
cp -r skills/appsec/appsec-vuln-audit ~/.claude/skills/
python3 scripts/check_skills.py --check   # parses, names, tools, contracts, routing
```

Each declares an **output contract**, which is what makes a skill checkable
rather than aspirational. Ten lessons embed their skill verbatim at build time —
so the lesson can never drift from the skill — then build that contract shape
from the data they just produced and validate it. And then show what the
contract *cannot* see: **an empty result conforms perfectly.** Conformance is a
statement about the serialiser; accuracy is the expensive part.

| | |
|---|---|
| [`skills/appsec/`](skills/appsec) | 6 — repo recon, threat model, vuln audit, exploit validation, triage report, coding-agent hardening |
| [`skills/attestation/`](skills/attestation) | 11 — turn a control claim into a signed statement bound to one deployment ([B1.16](labs/notebooks/B1.16.ipynb), run against 10 real OSS agent/MCP repos) |
| [`skills/architecture/`](skills/architecture) · [`identity/`](skills/identity) · [`secops/`](skills/secops) · [`grc/`](skills/grc) | 5 — blast radius, delegation chains, alert triage, incident scoping, control evidence |

## The programme

Five functions, twelve chapters. **Each function opens with an introduction
lesson** that says what it is for and which direction it runs in.

| Function | Chapters | Lessons |
|---|---|---|
| **A · Securing AI Architectures** | [1](curriculum/track-a1.md) The architecture and every risk it carries · [2](curriculum/track-a2.md) Securing it: identity and ingress · [3](curriculum/track-a3.md) Securing it: runtime and the gateway | 31 |
| **B · Application Security with an AI SDLC** | [4](curriculum/track-b1.md) The AI SDLC, as an agentic AppSec pipeline · [5](curriculum/track-b2.md) The harness that runs it | 31 |
| **C · Red Teaming and Security Research with AI** | [6](curriculum/track-c1.md) Red teaming with AI · [7](curriculum/track-c2.md) Security research with AI | 12 |
| **D · AI for SecOps** | [8](curriculum/track-d1.md) Detection · [9](curriculum/track-d2.md) Response | 17 |
| **E · AI for GRC** | [10](curriculum/track-e1.md) Risk and control · [11](curriculum/track-e2.md) Regulatory · [12](curriculum/track-e3.md) The CISO office | 30 |
| | **12 chapters** | **121** |

Nobody takes all of it. Everyone takes the **common spine** first — twenty
lessons, in order, that carry the vocabulary the rest runs on. Then the chapters
for the chair you sit in, then one adjacent chapter, because the failures happen
in the seams.

> **Spine:** A1.0 → A1.1 → A1.2 → A1.5 → **A1.9** → **A1.11** → A2.1 → A2.3 →
> A2.4 → A3.1 → A3.2 → A3.5 → **B1.0** → **B2.0** → B2.1 → B2.2 → **D1.0** →
> D1.5 → **E1.0** → E1.10

Two chapters carry a single artefact end to end:

- **[A1](curriculum/track-a1.md)** opens with the agentic reference
  architecture — thirteen components and five patterns, drawn rather than coded
  — then one risk per lesson grounded in the OWASP Agentic Top 10, each naming
  the component it attacks. Chapters 2 and 3 are the controls that close them.
- **[B1](curriculum/track-b1.md)** is the AI SDLC itself — a five-phase,
  fifteen-stage agentic AppSec pipeline built over seventeen sessions, attested in
  [B1.16](labs/notebooks/B1.16.ipynb) and closed in
  [B1.17](labs/notebooks/B1.17.ipynb) by scoring Google's Mantis against a
  held-out key — a reference implementation is something you evaluate, not
  something you trust.

Both directions run through every function: **AI for Security** (agents as your
instrument) and **Security of AI** (agents as the thing you defend). Teaching
only one produces a practitioner who gets surprised.

## Why you can trust the output

**Every one of the 121 notebooks has been run twice — here, and again on Kaggle
on a different machine — and printed exactly the same bytes.**

That second run is the claim worth making, because a kernel that prints nothing
also reports `complete`.
[`scripts/kaggle_verify.py`](scripts/kaggle_verify.py) compares each kernel's
remote stdout line-for-line against a fresh local run
([evidence](labs/notebooks/_kaggle_verified.json)). It caught two lessons whose
output depended on `PYTHONHASHSEED`; both are fixed, and
[`check_determinism.py`](scripts/check_determinism.py) now gates CI so the next
one is caught in nine seconds instead of after 121 remote pushes.

Two properties make that possible, and both are enforced by the build:

- **Self-contained.** A notebook carries every line of code it runs — no shared
  library, nothing to clone, no `pip install`. So it runs air-gapped, and you
  can lift one cell into your own repository without inheriting a dependency.
- **Deterministic.** Seed from `zlib.crc32`, not `hash()`; give every sort a
  full tiebreak. Byte-identical output from two machines is what makes drift a
  finding rather than noise.

Where a lesson names a tool you would really deploy — SPIRE, OPA, Falco,
Keycloak, garak — the notebook models the *decision* that tool makes, and
[`curriculum/labs.json`](curriculum/labs.json) keeps the real invocation
underneath as the full-infrastructure variant. Those variants are **not**
executed in CI and are labelled as such. Where a lesson involves a model, it
runs against a **deterministic stand-in**, labelled as a stand-in everywhere it
appears, never presented as a model's output. To use a real one:

```bash
ollama pull glm-4.6            # or kimi-k2, llama3.3
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
```

See [MODELS.md](MODELS.md), and [labs/kimi/](labs/kimi) for what happened when
these skills were run against a Kimi-family model on Kaggle — including the
parts that did not work.

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

CI re-runs all of it with `--check` — secret scan, 121 notebooks, determinism
gate, skill contracts — and fails on drift, so the notebook you read on the site
is always the notebook that ran. Pushing deploys the site.

**Credentials never go in this repository.** Kaggle tokens live in
`~/.kaggle/kaggle.json` or `$KAGGLE_USERNAME`/`$KAGGLE_KEY`; the push client
refuses to read a credential file inside the repo. Install the guard once:

```bash
./scripts/install-hooks.sh        # pre-commit secret scan; also runs in CI
```

## Layout

```
site/data/curriculum.json   source of truth: 121 sessions, 12 chapters
curriculum/                 generated chapter docs + labs.json (runnable commands)
scripts/exercises/          the lessons themselves, one module per track
skills/                     22 agent skills, embedded verbatim into notebooks
labs/notebooks/             121 generated notebooks + execution and Kaggle evidence
labs/                       attestation · b2.10-eval-harness · a2-delegation · kimi
site/                       the website (index + generated lesson pages)
scripts/                    build_* · run_notebooks · check_{skills,secrets,determinism} · kaggle_*
```

## Licence & credits

Curriculum and site are open — contribute by PR. Tooling referenced throughout
belongs to its respective projects (CNCF, Linux Foundation, OWASP and others).
Model weights carry their own licences — Kimi K2 (modified MIT), GLM (MIT),
Llama (Meta Community Licence, read the restrictions). See [MODELS.md](MODELS.md).
