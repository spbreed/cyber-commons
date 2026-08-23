<h1>Cyber Commons</h1>

**A free, open commons for Cyber AI — the skills to defend *with* AI, and to
secure the AI *itself* — organised the way a CISO org actually is, and provable
on the laptop you already own.**

Twelve tracks, **126 lessons — each with its own page and its own self-contained
Python notebook**. Every notebook opens in your browser in one click, carries
every line of code it runs, works on the **standard library alone**, and is
**executed in CI before it ships**.
Every lab is built on **open-source tooling (CNCF / Linux Foundation)** and
**open-weight models (Llama, Kimi, GLM)**. No licence, no vendor, **no
frontier-lab account**. Total cost to complete the curriculum: nothing.

🌐 **[cyber-commons live site](https://spbreed.github.io/cyber-commons/)** · 📓 [The 126 notebooks](labs/notebooks/) · 📚 [Curriculum](curriculum/) · 🤖 [Get the models free](MODELS.md) · 🎥 [Recording pipeline](#recording-pipeline)

---

## Why this exists

Security knowledge about AI is being locked behind vendor training, frontier-lab
credits and enterprise budgets — at exactly the moment when a two-person NGO
faces the same attackers as a global bank. A commons is the opposite bet:
**shared defense is stronger defense.**

Two promises make it usable by anyone:

- **Everything executes.** No pseudo-code, no screenshots of a demo. Every one of
  the 126 sessions ships a Python notebook that runs top to bottom and prints
  real output — and CI runs all 126 on every push, committing the result to
  [`labs/notebooks/_results.json`](labs/notebooks/_results.json). A lesson that
  claims an output has actually produced it.
- **Concept first, then the risk.** Each lesson introduces the idea and
  demonstrates it *working* before it raises what goes wrong. The build enforces
  this: a lesson without a `concept` section fails to generate.
- **Everything is open.** The control plane is CNCF/LF projects you'd actually
  deploy — SPIFFE/SPIRE, OPA, Falco, Kyverno, Cilium, Keycloak, OpenTelemetry,
  Sigstore, kagent, kmcp, agentgateway. The intelligence is open weights you can
  download. Commercial models are named where relevant but **never required**.

## The training programme

**Twelve chapters across five functions.** Nobody takes all of it. Everyone
takes the **common spine** first — twenty lessons, in order, that carry the
shared vocabulary the rest runs on. Then the chapters for the chair you sit in,
then one adjacent chapter, because the failures happen in the seams.

| Function | Chapters | Lessons |
|---|---|---|
| **A · Security Architecture & Platform** | [1](curriculum/track-a1.md) Security Architect · [2](curriculum/track-a2.md) Identity & NHI Engineer · [3](curriculum/track-a3.md) Platform & Cloud Security | 30 |
| **B · Product & Application Security** | [4](curriculum/track-b1.md) AppSec / Code Reviewer — the **15-stage pipeline** · [5](curriculum/track-b2.md) Security Automation & Harness Engineer | 34 |
| **C · Offensive Security & Research** | [6](curriculum/track-c1.md) Pentester / Red Teamer · [7](curriculum/track-c2.md) Security Researcher | 16 |
| **D · Security Operations** | [8](curriculum/track-d1.md) SOC Analyst & Detection Engineer · [9](curriculum/track-d2.md) Incident Responder | 16 |
| **E · Governance, Risk, Compliance & the CISO Office** | [10](curriculum/track-e1.md) GRC Practitioner · [11](curriculum/track-e2.md) Regulatory & Compliance · [12](curriculum/track-e3.md) BISO / CISO Office | 30 |
| | **12 chapters** | **126** |

### The common spine — start here, whoever you are

> A1.1 → A1.2 → A1.5 → **A1.9** → **A1.10** → **A1.11** → A2.1 → A2.3 → A2.4 →
> A3.2 → A3.5 → A3.6 → **B2.0** → B2.1 → B2.2 → D1.5 → **E1.0** → E1.2 →
> **E1.10** → E3.2

Bolded are the ones people most often skip and most often regret skipping: the
injection surface, the model-layer attack taxonomy, guardrail layering, what a
harness actually is, what trustworthy AI actually means, and who owns which
control.

Every session is shaped the same way — **concept → demo → where it breaks →
control → verify**. Every track ends in a **real artefact**: a delegation-chain trace, a blast-radius measurement, an
eval report, a risk-tiered register. Not a certificate.

Both directions run through every track: **AI for Security** (agents as your
instrument) and **Security for AI** (agents as the thing you defend). A track
that teaches only one produces a practitioner who gets surprised.

### The AppSec pipeline (track B1)

B1 is one artefact built over sixteen sessions: a five-phase, fifteen-stage
automated application-security pipeline.

```
[Ingestion & Mapping] ──> [Threat Modelling] ──> [Discovery]
     └─ stages 1-4              └─ stages 5-6       └─ stages 7-10
               ──> [Dynamic Validation] ──> [Reporting]
                        └─ stages 11-14         └─ stage 15
```

| Phase | Stages | Sessions |
|---|---|---|
| **1 · Ingestion & structural mapping** | historical parsing · structural indexing · component summarisation · architecture synthesis | B1.1–B1.2 |
| **2 · Threat modelling & strategy** | threat modelling · strategic planning | B1.3–B1.4 |
| **3 · Analysis & filtering** | vulnerability auditing · deduplication · contextual verification · feasibility filtering | B1.5–B1.7 |
| **4 · Dynamic validation & remediation** | sandbox replication · dynamic exploitation · exploit chaining · remediation engineering | B1.8–B1.11 |
| **5 · Governance & reporting** | severity calibration and reporting | B1.12 |

Three cross-cutting sessions cover context engineering, injection in your own
pipeline, and securing developers' coding agents. The track closes with
**[B1.16 — Google Mantis as a bonus](labs/notebooks/B1.16.ipynb)**: a real
implementation mapped stage by stage onto the pipeline you just built, its two
output shapes parsed, and its findings scored against a held-out key *before*
you adopt it. A reference implementation is a starting point you evaluate, not a
product you trust.

### Seniority overlay

The topics don't change with grade; the accountability does.

| Depth | Typical grade | What you do with the material | Assessment |
|---|---|---|---|
| **Practitioner** | Analyst, Engineer I–II | Operate loops others built; recognise failure modes; escalate correctly | Run the lab, explain what the trace shows |
| **Engineer** | Senior Engineer, Lead | Build the harness, control, detection, eval; own a component end to end | Ship the deliverable to production |
| **Principal** | Principal, Architect, Head of | Decide what is structurally possible; set promotion criteria; hold stop authority | Defend the design in an adversarial review |

## How a session works

1. **Concept first** — the idea is introduced and *demonstrated working* before
   any risk is raised. Leading with the threat teaches people to fear a
   mechanism they cannot yet describe.
2. **Then where it breaks** — the failure is reproduced, in code, from the
   mechanism you just saw.
3. **Then the control, and a check that it holds** — usually a property test, so
   the fix is proven rather than asserted.
4. **A notebook you keep** — self-contained, so you can lift any cell into your
   own repository without inheriting a dependency.

## Quick start

**Nothing to install. Nothing to pay for. Start in a browser.**

1. Open a lesson page — [A1.1](https://spbreed.github.io/cyber-commons/lessons/A1.1.html)
   is the first one.
2. Press **▶ Run on Kaggle**. The notebook opens in *your* Kaggle account.
3. Press **Run All**.

That is the whole setup. Every one of the 126 notebooks is self-contained and
standard-library only, so it runs on a free Kaggle CPU kernel **with the
internet switched off** — no model to download, no API key, no GPU, no quota to
burn. A lesson takes seconds, not minutes.

Two worth starting with:

| | |
|---|---|
| [**A1.1**](https://spbreed.github.io/cyber-commons/lessons/A1.1.html) | What an agent actually is, and where the risk lives |
| [**B2.2**](https://spbreed.github.io/cyber-commons/lessons/B2.2.html) | The whole curriculum in miniature — the loop reports success, the code is wrong, and the trace looks clean. Learning to measure that gap is what the rest of the commons is for. |

### Running them anywhere else

The same notebooks run unchanged in Jupyter, or headless:

```bash
git clone https://github.com/spbreed/cyber-commons && cd cyber-commons
python3 scripts/run_notebooks.py --session A1.1
python3 scripts/run_notebooks.py              # all 126, refreshes the evidence
```

Browse the site locally: `python3 -m http.server 8000 --directory site`

### Pointing a lesson at a real model

You do not need one — every lesson runs against a deterministic stand-in that
is labelled as a stand-in wherever it appears, never presented as a model's
output. When you *want* real inference, each of those notebooks prints the
exact command:

```bash
ollama pull glm-4.6            # or kimi-k2, llama3.3
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
```

See [MODELS.md](MODELS.md) for hosted and free-tier options, and
[labs/kimi/](labs/kimi) for what actually happened when these skills were run
against a Kimi-family model on Kaggle — including the parts that did not work.

## Agent skills

The procedures the curriculum teaches exist as real agent skills — `SKILL.md`
files with frontmatter, the format a coding agent loads — in
[`skills/`](skills). Eleven of them, and the first five compose into the
fifteen-stage AppSec pipeline the B1 track builds.

Each declares an **output contract**, which is what makes a skill checkable
rather than aspirational. Eleven lessons end by building that shape from the
data they just produced and validating it — and then showing what the contract
*cannot* see: an empty result conforms perfectly. Conformance is a statement
about the serialiser; accuracy is the expensive part.

```bash
python3 scripts/check_skills.py --check   # parses, names, contracts, routing
cp -r skills/appsec/appsec-vuln-audit ~/.claude/skills/
```

Skills are embedded into the notebooks verbatim at build time, so a lesson can
never drift from the skill it teaches.

## Labs

**Every one of the 126 sessions has a notebook, every notebook is
self-contained, every notebook runs — and every notebook has been run a second
time on Kaggle, on a different machine, where all 126 printed exactly what they
print here.**

That second run is the claim worth making. A kernel that finishes reports
`complete` even if it printed nothing at all, so
[`scripts/kaggle_verify.py`](scripts/kaggle_verify.py) compares each kernel's
remote stdout line-for-line against a fresh local run
([`_kaggle_verified.json`](labs/notebooks/_kaggle_verified.json), with the raw
remote output in [`_kaggle_output/`](labs/notebooks/_kaggle_output)). It found
two lessons that printed different things on the two machines because their
output depended on `PYTHONHASHSEED`; both are fixed, and
[`scripts/check_determinism.py`](scripts/check_determinism.py) now gates CI on
running every notebook under several hash seeds so the next one is caught in
nine seconds instead of after 126 remote pushes.

| | |
|---|---|
| [`labs/notebooks/`](labs/notebooks) | 126 notebooks, one per session — generated, executed in CI, rendered on the lesson pages |
| [`labs/b2.10-eval-harness`](labs/b2.10-eval-harness) | The full eval harness with real corpora and committed evidence (B2.10, E1.5, C1.6) |
| [`labs/a2-delegation`](labs/a2-delegation) | The deeper standalone version of the A2 delegation lab, with a real Keycloak variant |

Open any lesson page and press **▶ Run on Kaggle** — the notebook is created in
*your own* Kaggle account and runs there. Or locally:

```bash
jupyter notebook labs/notebooks/A2.5.ipynb
python3 scripts/run_notebooks.py            # all 126, headless, refreshes the evidence
```

**Self-contained is the load-bearing property.** A notebook carries every line
of code it runs — no shared library, nothing to clone, no `pip install`. That is
what lets it execute on a Kaggle kernel with the internet switched off, on an
air-gapped laptop, and in CI, and it means you can lift one cell into your own
repository without inheriting a dependency. The build refuses any notebook that
imports something outside the standard library.

Where a lesson names a real tool you would actually deploy — SPIRE, OPA, Falco,
Keycloak, garak — the notebook models the *decision* that tool makes, and
[`curriculum/labs.json`](curriculum/labs.json) keeps the real invocation
underneath as the full-infrastructure variant. Those variants have **not** been
executed in the build sandbox (its container registry is blocked), and they are
labelled as such rather than presented as results.

## Credentials

Nothing credential-shaped goes in this repository, ever. Kaggle tokens live in
`~/.kaggle/kaggle.json` or in `$KAGGLE_USERNAME`/`$KAGGLE_KEY`;
`scripts/kaggle_push.py` refuses to read a credential file located inside the
repo. Three layers enforce it:

```bash
./scripts/install-hooks.sh      # pre-commit hook — blocks the commit
python3 scripts/check_secrets.py  # same scan, runnable any time; also runs in CI
```

plus `.gitignore` entries for `kaggle.json`, `*.pem`, `*.key` and `.env`.

## Contributing

The syllabus has **one source of truth**:
[`site/data/curriculum.json`](site/data/curriculum.json) (structure) and
[`curriculum/labs.json`](curriculum/labs.json) (the runnable command blocks).
Edit those, then:

```bash
python3 scripts/build_curriculum.py    # regenerates curriculum/*.md
```

The website reads the same JSON, so the docs and the site can never drift.

## Updating a lesson (the daily loop)

Every lesson has its own page — `site/lessons/<ID>.html` — generated from data.
**Never edit the generated HTML.** Change the source and rebuild:

| To change… | Edit |
|---|---|
| Title, risk, control, tools, models | `site/data/curriculum.json` |
| The exercise: concept, code cells, "Your turn" | `scripts/exercises/track_<id>.py` |
| The goal + "Expect" line | `curriculum/labs.json` |
| Long-form notes under the lab | `lessons/<ID>.md` (optional, plain Markdown) |
| The video | drop `recordings/<ID>.mp4` — see below |

```bash
python3 scripts/build_notebooks.py   # regenerate all 126 notebooks
python3 scripts/run_notebooks.py     # prove they run; refreshes _results.json
python3 scripts/build_site.py        # regenerate all 109 pages (fast, idempotent)
git add -A && git commit -m "lesson: A2.5 notes" && git push
```

CI runs the secret scan, all 126 notebooks, the determinism gate, and both `--check` modes, so the notebook you read on the site is always the notebook
that ran.

That's the whole loop. Pushing triggers the Pages deploy, and the workflow
rebuilds too — so if you forget the build step the site is still correct, and CI
leaves a warning telling you to commit the regenerated pages next time.

Each page carries a **video slot** (a placeholder until the recording exists),
the **risk/control cards**, a **▶ Run on Kaggle** button, the lesson's **full
notebook rendered inline** (the same `.ipynb` that Kaggle opens, so the page and
the exercise cannot drift apart), an **✓ Executed** badge citing the real run,
tool/model chips, your notes, and prev/next navigation.

## Recording pipeline

Recordings publish themselves and appear on the right lesson page.

**One-time:** enable the YouTube Data API, create an OAuth desktop client, mint a
refresh token (`python3 scripts/youtube_upload.py --auth-setup`), then add repo
secrets `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.

**Per recording — name the file after the lesson and push:**

```bash
cp ~/lightboard/final.mp4 recordings/A2.5.mp4
git add recordings/A2.5.mp4 && git commit -m "record A2.5" && git push
```

The workflow uploads it with a title and description generated from that
lesson's own risk/control/lab text, registers it in `site/data/videos.json`,
**rebuilds the lesson pages so the embed replaces the placeholder**, and commits
— which deploys. Already uploaded elsewhere? Skip the upload:

```bash
python3 scripts/link_video.py --session A2.5 --youtube-id <id>
python3 scripts/build_site.py
```

`python3 scripts/link_video.py --list` shows which of the 126 lessons still need
recording.

## The site

Live at **<https://spbreed.github.io/cyber-commons/>**, deployed straight from
[`site/`](site) by [`pages.yml`](.github/workflows/pages.yml) on every push.

The workflow validates the curriculum data before publishing — it fails the build
if `videos.json` references a session id that doesn't exist in
`curriculum.json`, so a bad video link can never reach the site. The page renders
its curriculum from that same JSON, which is why the docs and the site cannot
drift apart.

## Repository layout

```
curriculum/          12 track chapters (generated from the JSON source of truth) + labs.json
lessons/             Optional per-lesson notes — lessons/<ID>.md renders on that page
labs/notebooks/      The 126 lesson notebooks (generated, self-contained) + evidence
labs/                b2.10-eval-harness · a2-delegation (deeper standalone labs)
site/                The website: index.html, lessons/<ID>.html (generated), data/, assets/
MODELS.md            How to get Llama / Kimi / GLM free — local, hosted, or self-hosted
scripts/exercises/   Per-session notebook exercises, one module per track (track_a1 … track_e3)
scripts/             build_notebooks · run_notebooks · build_site · kaggle_push ·
                     check_secrets · relink_labs · link_video · youtube_upload
recordings/          Drop lightboard recordings here (see recordings/README.md)
.github/             Pages deploy · recording pipeline · Copilot prompts
.claude/skills/      Agent skills, so Claude Code can run the labs for you
AGENTS.md            Cross-agent instructions (Copilot, Cursor, any AGENTS.md tool)
```

## Licence & credits

Curriculum and site are open — contribute by PR. Tooling referenced throughout
belongs to its respective projects (CNCF, Linux Foundation, OWASP and others).
Model weights carry their own licences — Kimi K2 (modified MIT), GLM (MIT), Llama
(Meta Community Licence, read the restrictions). See [MODELS.md](MODELS.md).
