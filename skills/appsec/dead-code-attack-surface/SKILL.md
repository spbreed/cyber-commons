---
name: dead-code-attack-surface
description: >-
  Separate findings that are false positives about risk from findings that are
  false positives about code, and decide between suppressing a dead-code
  finding and deleting the code. Use when a queue is dominated by unreachable
  findings, when suppressions are being added in bulk, or when asked why a
  known-dead vulnerability came back live.
allowed-tools: Read, Grep, Glob
---

# Dead code is a true positive about the code and a false positive about the risk

Both halves of that sentence matter and teams usually act on only one.

The finding is **correct**: the concatenation is there, the sink is real, a
reviewer who opens the file will agree. What is wrong is the implied
consequence, because nothing untrusted can reach it. Triaging it costs exactly
as much as triaging one on the login path, and there are usually far more of
them — so a queue that does not separate the two is a queue engineers learn to
ignore, which costs you the reachable ones too.

The response almost everyone reaches for is a **suppression**. It empties the
queue and it is the wrong fix, for a reason that only shows up months later: a
suppression is keyed to a file, a line and a rule, and **none of those change
when somebody wires the function back up**. The code becomes reachable, the
finding does not come back, and the suppression is now hiding a live
vulnerability.

**Attack surface reduction (ASR) — deleting the code — resolves both halves at
once.** The finding goes because the code is gone, and the latent risk goes
with it. It is the only response to a dead-code finding that cannot rot.

## When to use this

When reachability analysis produces a large unreachable bucket, before any bulk
suppression, and during any dead-code or deprecation sweep — the security queue
is the cheapest available list of which dead code to delete first.

## Procedure

**1 — Partition by reachability, in three buckets, never two.** Reachable,
unreachable, and unknown. Collapsing unknown into unreachable is how real bugs
are dropped, and dynamic dispatch is exactly where framework-wired handlers
live.

**2 — For the unreachable bucket, ask why it is unreachable.** Dead code that
nothing calls, a test fixture, a feature flag that has been off for two years,
or an internal function with no external driver. Only the first is a deletion
candidate; the others are reachable under a condition you have not enumerated.

**3 — Rank deletion candidates by what they would cost if reachable.** The
dead-code queue is a to-delete list, and the security severity is the ordering
you already have. A dead `os.system` on a caller-supplied path is a better
first deletion than a dead string formatter.

**4 — Delete, and re-run the scan to prove the finding is gone.** The proof is
that the finding disappears without a suppression entry. If it needed one, the
code was not dead.

**5 — For anything you suppress instead, bind the suppression to reachability,
not to the line.** A suppression that does not expire, and does not re-open when
the call graph changes, is a permanent decision made on temporary evidence.

## Output contract

```json
{
  "buckets": {"reachable": 0, "unreachable": 0, "unknown": 0},
  "queue": {"before": 0, "after_reachability": 0},
  "responses": [{"finding": "str", "action": "suppress|wont-fix|delete",
                 "finding_cleared": true, "risk_cleared": true, "rots": true}],
  "asr": {"deleted": 0, "surface_removed": ["str"]},
  "resurrected": 0
}
```

`resurrected` counts findings whose code became reachable again while a
suppression was still in place. It should be zero, and the only way to keep it
zero is to have deleted the code or expired the suppression.

## Failure modes

- **Suppressing in bulk to clear the queue.** It works, and it converts a
  visible false positive into an invisible true one.
- **Collapsing `unknown` into `unreachable`.** The bucket that gets dropped is
  the one that contains the framework-wired handlers.
- **Deleting on the scanner's word alone.** Reachability from *untrusted* entry
  points is not reachability from anywhere; check the call graph before the
  delete, not after.
- **Treating ASR as a security project.** It is a deletion, it belongs in
  ordinary maintenance, and framing it as a programme is how it never happens.
