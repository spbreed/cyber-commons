---
name: horizontal-requirement-to-control
description: >-
  Turn horizontal AI-regulation themes into named controls with concrete
  evidence artefacts, and apply the show-me test to the prose answers a policy
  currently offers. Use when a regulation is being answered with paragraphs.
allowed-tools: Read, Grep, Glob
---

# Every prose answer fails the show-me test

Horizontal AI regulation resolves to a small number of recurring themes — risk
management, data governance, human oversight, record keeping, transparency,
accuracy and robustness. Each maps to controls you can operate. A policy that
answers them in prose passes reading and fails the first follow-up, which is
always "show me".

## When to use this

Responding to a horizontal AI regulation, and auditing an existing response
before somebody external does.

## Procedure

**1 — Extract the themes rather than the article numbers.** Article numbers
change between drafts and jurisdictions; the themes are stable and map to
controls you already have.

**2 — Map each theme to named controls from your catalogue.** If a theme has no
control, that is the finding — record it as a gap rather than writing a
paragraph.

**3 — Attach the evidence artefact per control.** The specific thing that would
be handed over: a log export, a test result, an approval record, a signed
attestation.

**4 — Apply the show-me test to the current prose answers.** For each sentence,
is there an artefact behind it? Count the sentences that survive. It is usually
none, and the count is more persuasive than the argument.

**5 — Check freshness.** An artefact older than the control's freshness window
evidences the past. Report themes as fully evidenced, stale, or unevidenced —
three states, not two.

## Output contract

```json
{
  "themes": [{"theme": "str", "controls": ["str"], "gap": false}],
  "evidence": [{"control": "str", "artefact": "str", "as_of": "str", "fresh": true}],
  "prose_answers": [{"text": "str", "survives_show_me": false}],
  "status": [{"theme": "str", "state": "evidenced|stale|unevidenced"}]
}
```

## Failure modes

- **Mapping article numbers.** They move; the themes do not.
- **Answering a gap with a paragraph.** It reads as coverage and is not.
- **Two-state reporting.** Stale is the state most of your evidence is in.
