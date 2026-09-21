# lessons/ — per-lesson notes

Optional long-form notes for any lesson. Drop a file named after the session id
and it appears on that lesson's page under the lab:

```
lessons/B2.5.md   →  https://cybercommons.ai/lessons/B2.5.html
lessons/E1.0.md   →  https://cybercommons.ai/lessons/E1.0.html
```

Nothing here is required, and nothing here is currently written — the folder is
empty on purpose. A lesson page already renders its sections straight from
`scripts/exercises/`: use case relevance, Day 0/1/2, the framework, the skill and
its run, what you just proved, your turn, and where it leaves you — whichever of
those the lesson has, per `scripts/exercises/layout.py`. These notes
are for depth that does not belong in any of those — a gotcha you only hit on
particular hardware, further reading, a longer worked example.

**The recording script is not this.** That is [LIGHTBOARD.md](../LIGHTBOARD.md),
generated for all 134 lessons by `scripts/build_lightboard.py`. Do not hand-write
one here; it will go stale against the lesson and nothing will tell you.

## Writing one

Plain Markdown. Headings, lists, tables, fenced code, links, blockquotes and
images all work. Optional front-matter is stripped, so you can keep private notes
at the top:

```markdown
---
recorded: 2026-08-18
takes: 3
---

## What the board looked like

Draw the three planes first, left to right...

## Gotchas when you run it live

- `pytest` caches bytecode, so the oracle can lag a step — the lab deletes
  `__pycache__` for exactly this reason.
```

## Publish it

```bash
python3 scripts/build_site.py     # regenerate the lesson pages
git add lessons/ site/lessons/ && git commit -m "notes: B2.5" && git push
```

CI rebuilds and deploys automatically. If you forget to run the build,
`build_site.py --check` fails with a message telling you to — the site can never
drift from its source.

## Where each part of a lesson page comes from

| Part of the page | Edit this |
|---|---|
| Title, risk, control, tools, models | `site/data/curriculum.json` |
| The sections — hook, Day 0/1/2, framework, skill, proof, your turn | `scripts/exercises/` |
| Which sections a given lesson renders | `scripts/exercises/layout.py` |
| The run block (pick the lesson's skill) | derived: `scripts/exercises/lessonskills.py` |
| The OWASP / ATLAS / NIST / EU AI Act labels | `curriculum/frameworks.json` |
| The procedure the lesson runs | `skills/<area>/<name>/` |
| Long-form notes (this folder) | `lessons/<ID>.md` |
| Video embed | `site/data/videos.json` — written for you by `scripts/link_video.py` |

[CLAUDE.md](../CLAUDE.md) is the full map of what is generated and what is hand
written. Never hand-edit a `site/lessons/*.html`; it is overwritten.
