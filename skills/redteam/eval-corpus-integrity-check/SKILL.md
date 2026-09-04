---
name: eval-corpus-integrity-check
description: >-
  Attack an evaluation rather than a system: score a deliberately
  zero-capability harness against the corpus and see what the corpus alone
  awards it, then rebalance and re-score. Use before trusting any benchmark
  number, your own included.
allowed-tools: Read, Grep, Glob
---

# Score the null harness first

An evaluation is a claim about a system, and it is only as good as the corpus
underneath it. The cheapest way to find out is to score a harness that has no
capability at all — one that answers from the corpus's own skew. A high score
there is a measurement of the corpus, and every number derived from it inherits
the problem.

## When to use this

Before publishing an evaluation, before believing one, and whenever a benchmark
result is surprisingly good.

## Procedure

**1 — Build the null harness.** No analysis: answer with whatever the corpus's
majority class is. It should be trivial to write, and writing it takes minutes.

**2 — Score it against the corpus as it stands.** Record conformance and
accuracy separately — a null harness usually conforms perfectly, which is itself
worth knowing about conformance as a metric.

**3 — Rebalance and re-score.** Equalise the classes and run the same null
harness. The drop is the portion of the original score that came from skew
rather than capability.

**4 — Check the matcher, not just the corpus.** Score answers that name the
wrong directory. If they still score, the matcher is measuring string similarity
rather than correctness, and it will flatter every harness equally.

**5 — Report the null score alongside every real one.** A harness scoring 0.85
against a null of 0.85 has demonstrated nothing, and that comparison is the only
honest way to read the number.

## Output contract

```json
{
  "corpus": {"n": 0, "skew": 0.0, "classes": {"str": 0}},
  "null_harness": {"conformance": 0.0, "accuracy_skewed": 0.0, "accuracy_balanced": 0.0},
  "matcher": {"kind": "str", "wrong_directory_scores": 0.0},
  "verdict": {"score_from_skew": 0.0, "score_from_capability": 0.0}
}
```

## Failure modes

- **Reporting accuracy without the null baseline.** It is unreadable without
  one.
- **Conflating conformance with accuracy.** The null harness conforms.
- **Trusting a matcher that has never been attacked.** Try to fool it before you
  publish with it.
