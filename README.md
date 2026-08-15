<h1>Cyber Commons</h1>

**A free, open commons for Cyber AI — the skills to defend *with* AI, and to
secure the AI *itself* — organised the way a CISO org actually is, and provable
on the laptop you already own.**

Twelve tracks, one shared core, 104 sessions. Every lab runs on **open-source
tooling (CNCF / Linux Foundation)** and **open-weight models (Llama, Kimi, GLM)**.
No licence, no vendor, **no frontier-lab account**. Total cost to complete the
curriculum: **$0**.

📚 [Curriculum](curriculum/) · 🧪 [Labs](labs/) · 🤖 [Getting the models free](MODELS.md) · 🌐 [Website](site/) · 🎥 [Recording pipeline](#recording-pipeline)

---

## Why this exists

Security knowledge about AI is being locked behind vendor training, frontier-lab
credits and enterprise budgets — at exactly the moment when a two-person NGO
faces the same attackers as a global bank. A commons is the opposite bet:
**shared defense is stronger defense.**

Two things make it usable by anyone:

- **Everything executes.** No pseudo-code, no screenshots of a demo. Every
  session ships commands that run against real targets and print real output.
- **Everything is open.** The control plane is CNCF/LF projects you'd actually
  deploy — SPIFFE/SPIRE, OPA, Falco, Kyverno, Cilium, Keycloak, OpenTelemetry,
  Sigstore, kagent, kmcp, agentgateway. The intelligence is open weights you can
  download. Commercial models are named where relevant but **never required**.

## How it's organised

**Module 0 — the shared core (everyone, 5 sessions, no substitutions).** A
common vocabulary so twelve tracks can hold one conversation: the *three planes*
(decision / control / action), the *autonomy ladder* (L1 → L2 → L2.5 → L3), and
prompt injection taught once, properly.

**Then twelve tracks across five functions.** Nobody takes all of it. You take
the track for the chair you sit in, plus two sessions from a neighbouring track
— because the failures happen in the seams.

| Function | Tracks |
|---|---|
| **A · Architecture & Platform** | [A1](curriculum/track-a1.md) Security Architect · [A2](curriculum/track-a2.md) Identity & NHI Engineer · [A3](curriculum/track-a3.md) Platform & Cloud Security |
| **B · Product & AppSec** | [B1](curriculum/track-b1.md) AppSec / Code Reviewer · [B2](curriculum/track-b2.md) Security Automation & Harness Engineer |
| **C · Offensive & Research** | [C1](curriculum/track-c1.md) Pentester / Red Teamer · [C2](curriculum/track-c2.md) Security Researcher |
| **D · Security Operations** | [D1](curriculum/track-d1.md) SOC Analyst & Detection Engineer · [D2](curriculum/track-d2.md) Incident Responder |
| **E · GRC & CISO Office** | [E1](curriculum/track-e1.md) GRC Practitioner · [E2](curriculum/track-e2.md) Regulatory & Compliance · [E3](curriculum/track-e3.md) BISO / CISO Office |

Every session is shaped the same way: **Risk → Control → Lab**. Every track ends
in a **real artefact** — a delegation-chain trace, a blast-radius measurement, an
eval report, a risk-tiered register — not a certificate.

Both directions run through every track: **AI for Security** (agents as your
instrument) and **Security for AI** (agents as the thing you defend). A track
that teaches only one produces a practitioner who gets surprised.

## What's in the box

```
curriculum/       Module 0 + 12 track chapters (generated from the JSON source of truth)
labs/             Runnable labs — start with labs/m0-agent-loop
site/             The website (GitHub Pages) + data/curriculum.json + data/videos.json
MODELS.md         How to get Llama / Kimi / GLM free, local or hosted
scripts/          build_curriculum.py · vulnbench.sh · link_video.py · youtube_upload.py
.github/          Pages deploy + lightboard recording pipeline + agent prompts
.claude/skills/   Agent skills so Claude Code can run the labs for you
bench/ ingest/ questions/ ground-truth/ work_mantis/   ← Lab B2.10's implementation
docs/             Evidence: model comparison, real harness run, CyberGym integration
```

## Quick start

```bash
git clone <this repo> && cd cybercommons

# 1. get a model — local and free (see MODELS.md for hosted/free-tier options)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.3            # or glm-4.6 / a smaller variant on a light laptop
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=llama3.3

# 2. Module 0 — the loop, and why the verifier is the security control
cd labs/m0-agent-loop && pip install pytest
python3 loop.py --verifier pytest      # deterministic oracle → succeeds honestly
python3 loop.py --verifier llm-judge   # self-grading → declares success on broken code
```

The second command is the whole curriculum in miniature: the loop reports
success, the code is wrong, and the trace looks clean. Measuring that gap is what
the rest of the commons is for.

Browse the site locally:

```bash
python3 -m http.server 8000 --directory site   # → http://localhost:8000
```

## Where evaluation fits

Evaluation is **one chapter**, not the whole project — [B2.10](curriculum/track-b2.md)
builds the harness, [E1.5](curriculum/track-e1.md) reads its output as audit
evidence, and [C1.6](curriculum/track-c1.md) attacks it. That chapter happens to
be the most fully-built lab here, with committed evidence:

| Task | Metric | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| SAST — synthetic code | Expert Acc | **0.90** | 0.75 | 0.61 |
| CVE — real-world code | Expert Acc | 0.87 | **0.95** | 0.47 |
| IaC — TerraGoat vs Checkov | micro-F1 | **0.76** | 0.66 | 0.58 |

Same harness, same prompt — the backbone alone swings accuracy from 0.47 to 0.95,
and the ranking flips between corpora. Details in [`labs/b2.10-eval-harness`](labs/b2.10-eval-harness/README.md)
and [`docs/MODEL_COMPARISON.md`](docs/MODEL_COMPARISON.md). The harness is
model-agnostic: point it at Ollama to compare Llama / GLM / Kimi instead.

## Contributing to the curriculum

The syllabus has **one source of truth**: [`site/data/curriculum.json`](site/data/curriculum.json)
(structure) and [`curriculum/labs.json`](curriculum/labs.json) (the runnable
command blocks). Edit those, then:

```bash
python3 scripts/build_curriculum.py    # regenerates curriculum/*.md
```

The website reads the same JSON, so docs and site can never drift.

## Recording pipeline

Lightboard recordings publish themselves to YouTube and attach to the right
chapter on the site.

**One-time setup:** enable the YouTube Data API, create an OAuth desktop client,
mint a refresh token (`python3 scripts/youtube_upload.py --auth-setup`), then add
repo secrets `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` and repo
variable `SITE_URL`.

**Then, per recording — just drop the file in:**

```bash
cp ~/recordings/a2.5-final.mp4 recordings/A2.5.mp4   # filename = session id
git add recordings/A2.5.mp4 && git commit -m "record A2.5" && git push
```

The [publish-video workflow](.github/workflows/publish-video.yml) uploads it with
a title/description generated from the chapter's own risk/control/lab text,
registers it in `site/data/videos.json`, and commits — which triggers the
[Pages deploy](.github/workflows/pages.yml) so a **▶ Watch** link appears on that
chapter. Already uploaded elsewhere? Link it without re-uploading:

```bash
python3 scripts/link_video.py --session A2.5 --youtube-id <id>
python3 scripts/link_video.py --list        # coverage: which chapters still need recording
```

## Publishing the site

Settings → Pages → **Source: GitHub Actions**. Push to `main` and
[`pages.yml`](.github/workflows/pages.yml) validates the curriculum data (it
fails the build if `videos.json` references a session that doesn't exist) and
deploys `site/`.

## Status — what's real today

Being honest about coverage, because "everything executes" is a promise:

- ✅ **Fully built and tested:** the eval harness (B2.10/E1.5/C1.6) with committed
  evidence; the Module 0 loop lab; the site; the curriculum generator; the video
  pipeline (`link_video.py` tested end to end, `youtube_upload.py` dry-run tested).
- 🟡 **Specified with real commands, not yet executed in this environment:** the
  infra-heavy labs (SPIRE/Keycloak delegation, sandbox tiers, SOC stack). The
  commands are real and the tools are the right ones, but this build sandbox
  blocks the container registry, so they have not been run here. Treat them as
  reviewed specs until someone runs them on a normal machine and files the output.
- ⬜ **38 of 104 sessions** currently carry a full command block; the rest carry
  risk/control/lab and are being filled in. `curriculum/labs.json` is where they go.

Contributions that turn a 🟡 into a ✅ — with the output pasted in — are the most
valuable thing you can send.

## Licence & credits

Curriculum and site: open, contribute by PR. Tooling referenced throughout
belongs to its respective projects (CNCF, Linux Foundation, OWASP and others).
Model weights carry their own licences — Kimi K2 (modified MIT), GLM (MIT),
Llama (Meta Community Licence, read the restrictions). See [MODELS.md](MODELS.md).
