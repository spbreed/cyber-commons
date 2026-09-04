---
name: supervisory-documentation-score
description: >-
  Score written documentation on how many of its sentences are checkable — each
  naming a control, an artefact and a date — and test it against the follow-up
  questions a supervisor actually asks. Use before submitting anything to an
  assessor.
allowed-tools: Read, Grep, Glob
---

# Count the checkable sentences

Documentation that survives supervision is not better written; it is
differently written. Each load-bearing sentence names a control, the artefact
that evidences it, and a date. A paragraph with none of those reads well, passes
internal review, and produces four follow-ups you cannot answer.

## When to use this

Before submitting documentation to a regulator, an auditor or a customer's
assurance team.

## Procedure

**1 — Split the text into sentences and score each.** Does it name a control
identifier, an artefact, and a date? Three marks per sentence, and the count of
sentences scoring all three is the headline.

**2 — Report the weak version's score.** Usually zero. Showing it beside the
strong version is what changes how the next document gets written.

**3 — Rewrite so the load-bearing claims carry all three.** Not every sentence —
the ones an assessor would test. The rest can be prose.

**4 — Generate the follow-up questions and try to answer them from the text
alone.** "Which control", "show me the artefact", "when was it last tested",
"who owns it". A question you cannot answer from the document is a question you
will answer live, badly.

**5 — Attach the artefacts.** A checkable sentence with an unattached artefact
is one email away from being unevidenced.

## Output contract

```json
{
  "sentences": [{"text": "str", "names_control": false, "names_artefact": false, "has_date": false}],
  "score": {"checkable": 0, "total": 0},
  "comparison": {"weak_checkable": 0, "strong_checkable": 0},
  "followups": [{"question": "str", "answerable_from_text": false}],
  "artefacts_attached": ["str"]
}
```

## Failure modes

- **Editing for tone.** The problem is not the prose.
- **Making every sentence checkable.** Only the load-bearing ones need it.
- **Naming an artefact you did not attach.** The follow-up arrives immediately.
