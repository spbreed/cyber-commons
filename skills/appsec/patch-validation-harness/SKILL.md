---
name: patch-validation-harness
description: >-
  Accept a proposed fix only when three things hold — behaviour unchanged, the
  exploit no longer works, and the fix proved against the build that was
  vulnerable. Use when an agent proposes a patch, or when a scanner going green
  is being read as a fix.
allowed-tools: Read, Grep, Glob, Bash
---

# A green scanner is not a fixed bug

Several candidate patches will make the scanner green. Some of them change
behaviour, some of them leave the bug exploitable, and one of them does neither.
Telling them apart needs three gates, and the third is the one that is usually
missing: proof against the **old** build, so "the exploit stops working" is a
statement about the patch rather than about the environment.

## When to use this

Every proposed remediation, whether authored by a person or an agent, and
especially when the evidence offered is that the scanner no longer fires.

## Procedure

**1 — Establish the baseline on the vulnerable build.** The behaviour cases must
pass and the exploit must work. If the exploit does not work here, you are about
to validate a patch against a bug you have not reproduced.

**2 — Gate one: behaviour unchanged.** Run every behaviour case against the
patched build. A patch that fixes the defect and changes an answer is a
regression with a security justification.

**3 — Gate two: the exploit no longer works.** Against the patched build,
directly. Not "the scanner is quiet" — the scanner was one of the tools that
missed the defect class in the first place.

**4 — Gate three: proof of fix.** Run the exploit against the old build again,
after the patch is written, in the same harness. It must still work. This is
what excludes the environment having changed underneath the test.

**5 — Report per candidate and per gate.** A candidate rejected at gate one and
one rejected at gate two need different conversations with whoever wrote them.

## Output contract

```json
{
  "baseline": {"behaviour_pass": true, "exploit_works": true},
  "candidates": [{"id": "str", "scanner_green": true,
                  "behaviour_unchanged": true, "exploit_blocked": true,
                  "proof_of_fix": true, "verdict": "accepted|rejected", "rejected_at": "str|null"}],
  "accepted": ["str"]
}
```

## Failure modes

- **Accepting a green scanner.** Several wrong patches produce one.
- **Skipping the behaviour cases.** The most reliable way to block an exploit is
  to break the feature.
- **Omitting proof of fix.** Without it you cannot distinguish a working patch
  from a broken exploit.
