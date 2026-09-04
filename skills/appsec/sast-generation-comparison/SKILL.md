---
name: sast-generation-comparison
description: >-
  Run pattern rules, taint analysis and a model over the same code and compare
  precision, recall and the class of defect only the third one finds. Use when
  choosing static analysis, justifying a model in the pipeline, or explaining
  why the scanner's output is mostly noise.
allowed-tools: Read, Grep, Glob
---

# Three generations, and they fail differently

Grep-class rules match syntax and cannot see data flow, so they flag the
parameterised query and the constant insert. Taint analysis follows source to
sink and is precise on the bugs it models. A model reads intent and finds the
class neither of the others can express — an authorization defect, where nothing
is malformed and the code is simply wrong about who may do what.

## When to use this

Choosing or defending a static analysis stack, and any time somebody proposes
replacing one generation with another rather than layering them.

## Procedure

**1 — Assemble a corpus with known ground truth.** Real bugs, safe lookalikes
of each bug, and at least one defect with no syntactic signature. The
lookalikes are what produce the precision number; without them every tool looks
perfect.

**2 — Run generation 1: pattern rules.** Record every hit and mark it against
ground truth. Precision here is usually about half, and the false positives are
the safe versions of the true positives.

**3 — Run generation 2: taint rules.** Source, sink, sanitiser. Expect high
precision and recall inside the model it has, and expect it to find nothing in
the file whose defect is not a flow.

**4 — Run generation 3: a model, with confidence.** Give it the same code. Record
what it finds, its confidence, and — separately — anything it asserts that is
not in the file. That last column is the cost of this generation.

**5 — Report per generation and per defect class.** The useful output is not a
winner; it is which class each generation can and cannot express, and the
precision each pays for its recall.

## Output contract

```json
{
  "corpus": [{"file": "str", "defect": "str|null", "cwe": "str|null"}],
  "generations": [{"name": "grep|taint|model", "findings": 0, "true_positives": 0,
                   "precision": 0.0, "recall": 0.0, "hallucinated": 0}],
  "only_found_by": [{"defect": "str", "generation": "str"}],
  "recommendation": {"layers": ["str"], "why": "str"}
}
```

## Failure modes

- **A corpus with no safe lookalikes.** Precision becomes meaningless.
- **Comparing on recall alone.** Grep has excellent recall and unusable
  precision.
- **Not counting the model's hallucinations.** They are the reason generation 3
  needs generation 4 — verification.
