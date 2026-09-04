---
name: finding-dedup-and-verification
description: >-
  Collapse raw findings from several tools into distinct defects across CWE
  aliases and duplicate reports, then reject the ones whose symbols do not
  appear in the file. Use when a pipeline produces more findings than defects,
  or when a scanner reports something that is not in the code.
allowed-tools: Read, Grep, Glob
---

# Findings are not defects, and some of them are not real

A pipeline running three analyses over one file produces findings that overlap
in two different ways — the same defect reported under an alias, and the same
defect reported by three tools — and, if a model is one of the tools, findings
about symbols that do not exist. Both have to be resolved before a human sees
the list, or the human resolves them by ignoring the list.

## When to use this

Between analysis and triage, in any pipeline with more than one analyser, and
always when a model is one of them.

## Procedure

**1 — Normalise the CWE.** Maintain an alias map — CWE-943 is CWE-89 for this
purpose — and normalise before comparing. Aliases are why the same defect
appears twice with different identifiers.

**2 — Key each finding by defect, not by report.** File, enclosing function,
normalised CWE. Line numbers move; the enclosing function does not, and it is
what makes two reports of one defect collapse.

**3 — When duplicates disagree, keep the one with the best evidence.** A taint
result carries a path; a grep hit carries a line; a model result carries a
sentence. Prefer in that order, and record which tools agreed — agreement is
useful signal even though it is not proof.

**4 — Verify each survivor against the source.** Does the symbol it names appear
in the file? Is the module it blames imported? A finding about `os.system` in a
file that never imports `os` is a hallucination, and it is rejected here rather
than in a maintainer's inbox.

**5 — Report both counts and the rejects.** Raw findings, distinct defects, and
the rejected list with the reason. Discarding hallucinations silently loses the
measurement of how often the analyser produces them.

## Output contract

```json
{
  "raw": 0,
  "defects": [{"key": "str", "file": "str", "function": "str", "cwe": "str",
               "reported_by": ["str"], "kept_from": "str"}],
  "rejected": [{"finding": "str", "reason": "symbol absent|module not imported"}],
  "counts": {"raw": 0, "distinct": 0, "rejected": 0}
}
```

## Failure modes

- **Keying on the line number.** One edit and the same defect is two.
- **Merging by CWE alone.** Two real SQL injections in one file are two defects.
- **Dropping hallucinations without counting them.** That count is how you know
  whether to keep the analyser.
