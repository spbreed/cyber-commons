<h1>Cyber Commons</h1>

**A free, open commons for Cyber AI — the skills to defend *with* AI, and to
secure the AI *itself* — organised the way a CISO org actually is, and provable
on the laptop you already own.**

Twelve tracks, one shared core, **104 lessons, each with its own page and a runnable lab**.
Every lab runs on **open-source tooling (CNCF / Linux Foundation)** and
**open-weight models (Llama, Kimi, GLM)**. No licence, no vendor, **no
frontier-lab account**. Total cost to complete the curriculum: nothing.

🌐 **[cyber-commons live site](https://spbreed.github.io/cyber-commons/)** · 📚 [Curriculum](curriculum/) · 🧪 [Labs](labs/) · 🤖 [Get the models free](MODELS.md) · 🎥 [Recording pipeline](#recording-pipeline)

---

## Why this exists

Security knowledge about AI is being locked behind vendor training, frontier-lab
credits and enterprise budgets — at exactly the moment when a two-person NGO
faces the same attackers as a global bank. A commons is the opposite bet:
**shared defense is stronger defense.**

Two promises make it usable by anyone:

- **Everything executes.** No pseudo-code, no screenshots of a demo. Every one of
  the 104 sessions ships commands that run against real targets and print real
  output.
- **Everything is open.** The control plane is CNCF/LF projects you'd actually
  deploy — SPIFFE/SPIRE, OPA, Falco, Kyverno, Cilium, Keycloak, OpenTelemetry,
  Sigstore, kagent, kmcp, agentgateway. The intelligence is open weights you can
  download. Commercial models are named where relevant but **never required**.

## The training programme

**Module 0 — the shared core.** Everyone, five sessions, no substitutions. A
common vocabulary so twelve tracks can hold one conversation: the *three planes*
(decision / control / action), the *autonomy ladder* (L1 → L2 → L2.5 → L3), and
prompt injection taught once, properly.
→ [`curriculum/module-0.md`](curriculum/module-0.md)

**Then twelve tracks across five functions.** Nobody takes all of it. You take
the track for the chair you sit in, plus two sessions from a neighbouring track
— because the failures happen in the seams.

| Function | Tracks |
|---|---|
| **A · Architecture & Platform**<br><sub>decide what is structurally possible</sub> | [A1](curriculum/track-a1.md) Security Architect · [A2](curriculum/track-a2.md) Identity & NHI Engineer · [A3](curriculum/track-a3.md) Platform & Cloud Security |
| **B · Product & AppSec**<br><sub>first to meet agents at scale</sub> | [B1](curriculum/track-b1.md) AppSec / Code Reviewer · [B2](curriculum/track-b2.md) Security Automation & Harness Engineer |
| **C · Offensive & Research**<br><sub>find out what is actually true</sub> | [C1](curriculum/track-c1.md) Pentester / Red Teamer · [C2](curriculum/track-c2.md) Security Researcher |
| **D · Security Operations**<br><sub>machine-speed decisions</sub> | [D1](curriculum/track-d1.md) SOC Analyst & Detection Engineer · [D2](curriculum/track-d2.md) Incident Responder |
| **E · GRC & CISO Office**<br><sub>make it defensible</sub> | [E1](curriculum/track-e1.md) GRC Practitioner · [E2](curriculum/track-e2.md) Regulatory & Compliance · [E3](curriculum/track-e3.md) BISO / CISO Office |

Every session is shaped the same way — **Risk → Control → Lab**. Every track ends
in a **real artefact**: a delegation-chain trace, a blast-radius measurement, an
eval report, a risk-tiered register. Not a certificate.

Both directions run through every track: **AI for Security** (agents as your
instrument) and **Security for AI** (agents as the thing you defend). A track
that teaches only one produces a practitioner who gets surprised.

### Seniority overlay

The topics don't change with grade; the accountability does.

| Depth | Typical grade | What you do with the material | Assessment |
|---|---|---|---|
| **Practitioner** | Analyst, Engineer I–II | Operate loops others built; recognise failure modes; escalate correctly | Run the lab, explain what the trace shows |
| **Engineer** | Senior Engineer, Lead | Build the harness, control, detection, eval; own a component end to end | Ship the deliverable to production |
| **Principal** | Principal, Architect, Head of | Decide what is structurally possible; set promotion criteria; hold stop authority | Defend the design in an adversarial review |

## How a session works

1. **Lightboard, not lecture** — the concept is drawn so the mental model lands
   before any code does.
2. **Live demo, real execution** — an actual agent against an actual target, on
   an open-weight model.
3. **A repo you keep** — every lab is source you clone, break and adapt.

## Quick start

```bash
git clone https://github.com/spbreed/cyber-commons && cd cyber-commons

# 1. get a model — local and free (see MODELS.md for hosted/free-tier options)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.3            # or glm-4.6 / a smaller variant on a light laptop
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=llama3.3

# 2. Module 0 — the loop, and why the verifier is the security control
cd labs/m0-agent-loop && pip install pytest
python3 loop.py --verifier pytest      # deterministic oracle → succeeds honestly
python3 loop.py --verifier llm-judge   # self-grading → declares success on broken code
```

That second command is the whole curriculum in miniature: the loop reports
success, the code is wrong, and the trace looks clean. Learning to measure that
gap is what the rest of the commons is for.

**Then pick your chair:**

```bash
# A2 — identity, the most genuinely new material. No infra needed.
cd labs/a2-delegation
python3 delegate.py chain && python3 delegate.py verify
python3 delegate.py impersonate   # why your audit trail is already wrong
```

Browse the site locally: `python3 -m http.server 8000 --directory site`

## Labs

| Lab | Chapters | Status |
|---|---|---|
| [`labs/m0-agent-loop`](labs/m0-agent-loop) | M0.1–M0.3, B2.1, B2.4 | ✅ runs anywhere (stdlib + pytest) |
| [`labs/a2-delegation`](labs/a2-delegation) | A2.3, A2.4, A2.5, B2.6, C1.4 | ✅ runs anywhere (stdlib only) |
| [`labs/b2.10-eval-harness`](labs/b2.10-eval-harness) | B2.10, E1.5, C1.6 | ✅ fully built, with committed evidence |
| a1-control-plane · a3-sandbox · b1-appsec · c1-redteam · c2-research · d1-soc · d2-ir · e1-grc · e2-compliance · e3-ciso | remaining tracks | 🟡 real commands, need a machine with a container registry |

**All 104 sessions carry a runnable command block** naming the real tool and the
exact invocation. The 🟡 labs above are specified and reviewed but have not been
executed in the build sandbox (its container registry is blocked) — treat them as
specs until someone runs them and files the output. Where a lesson can be taught
without infrastructure, we ship a **no-infra variant**; `a2-delegation` is the
model for that, and adding one to a 🟡 lab is the most valuable contribution you
can make.

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
| The runnable commands + "Expect" line | `curriculum/labs.json` |
| Long-form notes under the lab | `lessons/<ID>.md` (optional, plain Markdown) |
| The video | drop `recordings/<ID>.mp4` — see below |

```bash
python3 scripts/build_site.py     # regenerate all 105 pages (fast, idempotent)
git add -A && git commit -m "lesson: A2.5 notes" && git push
```

That's the whole loop. Pushing triggers the Pages deploy, and the workflow
rebuilds too — so if you forget the build step the site is still correct, and CI
leaves a warning telling you to commit the regenerated pages next time.

Each page carries a **video slot** (a placeholder until the recording exists),
the **risk/control cards**, the **runnable commands**, tool/model chips, an
**↗ Open the exercise on GitHub** button pointing at that lesson's lab folder,
your notes, and prev/next navigation.

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

`python3 scripts/link_video.py --list` shows which of the 104 lessons still need
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
curriculum/       Module 0 + 12 track chapters (generated from the JSON source of truth)
lessons/          Optional per-lesson notes — lessons/<ID>.md renders on that page
labs/             Runnable labs, one folder per lab — start with m0-agent-loop
site/             The website: index.html, lessons/<ID>.html (generated), data/, assets/
MODELS.md         How to get Llama / Kimi / GLM free — local, hosted, or self-hosted
scripts/          build_site.py · build_curriculum.py · link_video.py · youtube_upload.py
recordings/       Drop lightboard recordings here (see recordings/README.md)
.github/          Pages deploy · recording pipeline · Copilot prompts
.claude/skills/   Agent skills, so Claude Code can run the labs for you
AGENTS.md         Cross-agent instructions (Copilot, Cursor, any AGENTS.md tool)
```

## Licence & credits

Curriculum and site are open — contribute by PR. Tooling referenced throughout
belongs to its respective projects (CNCF, Linux Foundation, OWASP and others).
Model weights carry their own licences — Kimi K2 (modified MIT), GLM (MIT), Llama
(Meta Community Licence, read the restrictions). See [MODELS.md](MODELS.md).
