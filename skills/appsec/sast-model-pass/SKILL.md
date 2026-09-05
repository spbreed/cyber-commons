---
name: sast-model-pass
description: >-
  Run a language model over a slice that deterministic rules structurally cannot
  reach, and record what it says as a hypothesis rather than a finding. Use
  after a rule-based scan has been scored, when a defect is the absence of a
  call rather than the presence of a pattern, or when deciding whether an
  unverified model confidence score may gate a pipeline.
allowed-tools: Read, Grep, Glob
---

# The pass that finds what no rule can express — and the price of it

A rule matches syntax that is present. Some defects are the **absence** of
something: no authorisation check, no ownership comparison, no expiry. There
is nothing to match, so no ruleset finds them at any width, and that is the
only defensible reason to put a model in an audit pipeline.

The price is that a model also reports defects that are not there, in the same
tone, with a similar confidence number. So the output of this pass is not a
finding list. It is a **hypothesis list**, and something else promotes a
hypothesis to a finding.

## When to use this

After the deterministic scan is scored, on the files where the key says a
defect exists and the rules were silent — never as a first pass over the whole
repository. A model asked to review everything reviews nothing carefully, and
at four million lines the pass costs more than the finding is worth.

## Procedure

**1 — Take only the slice where the defect is decidable.** The function, its
signature, and the authority its caller holds. The signature is the part
people drop and it is the part that decides the answer.

**2 — Ask a question with a checkable answer.** "Review this for security"
returns an essay. "Does this function verify that the caller owns the record
it returns — yes or no, and quote the line that does it" returns something you
can check without a second opinion.

**3 — Verify the quote against the file.** If the model quotes a line, the
line must exist. If it names a symbol, the symbol must be in the file. This
costs nothing and kills the largest class of model error before a human sees
it.

**4 — Record every survivor as `hypothesis`, never `finding`.** Carry the
model, the prompt slice and the confidence with it, so the promotion decision
downstream can be argued with rather than inherited.

**5 — Do not gate on the confidence number.** It is not calibrated and it is
not stable across runs. Run the same slice ten times before you let any
threshold into a pipeline; the variance is usually wider than the gap between
your accept and reject bands.

## Output contract

```json
{
  "backend": {"kind": "replay|open-weight", "model": "str"},
  "hypotheses": [{"unit": "str", "cwe": "str", "confidence": 0.0,
                  "quote_verified": true, "status": "hypothesis"}],
  "rejected": [{"unit": "str", "why": "quote-not-in-file|symbol-absent"}],
  "promoted": 0
}
```

`promoted` is 0 here on purpose. This skill does not promote anything —
deduplication, contextual verification, reachability and dynamic validation
do, and a pipeline that lets the audit stage promote its own output has no
independent step in it at all.

## Failure modes

- **Reporting model output as findings.** They enter a queue people trust and
  leave it as lost credibility.
- **Trusting the confidence.** Uncalibrated, unstable, and the first thing an
  eager pipeline gates on.
- **Sending the whole file.** The defect gets diluted and the answer degrades;
  the slice that makes it decidable is smaller than the file.
- **Dropping the signature from the slice.** The identical body is a critical
  defect in a handler and irrelevant in a migration script.
