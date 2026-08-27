---
name: input-injection-screening-verifier
description: >-
  Verify that untrusted ingestion paths pass through an injection detection
  or sanitisation step before reaching model context. Use to attest
  injection screening, to inventory which untrusted sources are screened, or
  to check for the private-data plus untrusted-content plus egress
  combination.
allowed-tools: Read, Grep, Glob
---

# Input Injection Screening Verifier

**Controls:** Control 5 — indirect prompt-injection screening

## Confidence: PARTIAL — and this ceiling is not negotiable

You can verify that a detector **exists on the path** and record its class.
You cannot verify that it works. Published defences that reduce attack success
to a few percent under static attacks have been driven back above 95% by
adaptive, search-based attacks, and human red-teamers defeat them routinely.

**Record the detector class. Do not assert protection. Cap at PARTIAL.**

## Procedure

1. **Inventory untrusted ingestion paths.** Email, documents, web fetches,
   tickets, tool results, MCP tool descriptions, retrieved corpora, memory
   reads, inter-agent messages. Anything a party outside your trust boundary
   can write into.

2. **For each path, determine whether a screening step exists** between
   ingestion and model context, and record which one — a classifier, a
   prompt-attack filter, delimiting or spotlighting, a dual-model pattern, or
   nothing.

3. **Check provenance tagging.** Whether the origin survives into the context
   window is more durable than any detector, because it does not depend on
   recognising the payload.

4. **Flag the dangerous combination.** Private data reachable **and** untrusted
   content ingested **and** an egress path available is the combination that
   turns injection into exfiltration. Any deployment with all three is a
   finding on its own, whatever the detector says.

## Output contract

```json
{
  "deployment_id": "str",
  "ingestion_paths": [
    {"source": "str", "screened": true, "detector_class": "classifier|filter|spotlighting|dual_model|none",
     "provenance_tagged": true}
  ],
  "unscreened_sources": ["str"],
  "trifecta": {"private_data": true, "untrusted_content": true, "egress": true, "present": true},
  "verdict": "PARTIAL|FAIL",
  "verdict_ceiling_reason": "detector presence is verifiable; robustness under adaptive attack is not"
}
```

`PASS` is not a permitted value.

## Failure modes

- **Reporting a detector's benchmark score as this deployment's protection.**
  Those numbers are from static attacks.
- **Missing tool results as an ingestion path.** They are the most commonly
  forgotten one, because they arrive from a system you trust.
- **Ignoring the combination check** because each element looked acceptable
  alone.
