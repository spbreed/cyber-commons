# lessons/ — per-lesson notes

Optional long-form notes for any lesson. Drop a file named after the session id
and it appears on that lesson's page under the lab:

```
lessons/M0.2.md   →  https://spbreed.github.io/cyber-commons/lessons/M0.2.html
lessons/A2.5.md   →  .../lessons/A2.5.html
```

Nothing here is required. A lesson page already renders its risk, control,
runnable commands, tool chips, GitHub exercise link and video slot straight from
the curriculum data — these notes are for the extra depth you want to write after
recording (the lightboard script, gotchas, further reading).

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
git add lessons/ site/lessons/ && git commit -m "notes: M0.2" && git push
```

CI rebuilds and deploys automatically. If you forget to run the build, the Pages
workflow fails with a message telling you to — the site can never drift from the
source.

## Where each part of a lesson page comes from

| Part of the page | Edit this |
|---|---|
| Title, risk, control, tools, models | `site/data/curriculum.json` |
| The runnable command block + "Expect" | `curriculum/labs.json` |
| Long-form notes (this folder) | `lessons/<ID>.md` |
| Video embed | `site/data/videos.json` — written for you by the recording pipeline |
| Exercise button | derived from the lab's `cd labs/...` line |
