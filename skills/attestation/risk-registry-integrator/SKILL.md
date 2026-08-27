---
name: risk-registry-integrator
description: >-
  Pull open risks and exceptions for the downstream services an agent or its
  MCP tools connect to, and map them to the deployment. Use to roll up
  inherited risk, to find expired exceptions on a dependency, or when asked
  what a deployment inherits from the systems it calls.
allowed-tools: Bash, Read
---

# Risk Registry Integrator

**Controls:** Cross-cutting — inherited risk

## What this adds

A deployment's own controls can be clean while every system it calls is
carrying an accepted risk. Inherited risk is invisible unless something joins
the downstream inventory to the register, and this skill is that join.

## Procedure

1. **Take the downstream inventory** from the inventory resolver. Do not build
   a second list — a divergence between the two is itself the finding.
2. **Query the register per downstream.** Open risks with severity and status,
   plus any accepted exceptions.
3. **Check exception expiry.** Expired and approaching-expiry exceptions are
   separate categories and are treated differently.
4. **Find unmapped downstreams.** A dependency with no register entry is not a
   dependency with no risk; it is one nobody has assessed.
5. **Roll up.** The deployment inherits the highest open severity among its
   dependencies, and that number belongs in the attestation.

## Output contract

```json
{
  "deployment_id": "str",
  "downstreams": [
    {"service": "str",
     "open_risks": [{"id": "str", "severity": "critical|high|medium|low", "status": "str"}],
     "exceptions": [{"id": "str", "expires": "str", "state": "active|expiring|expired"}],
     "in_register": true}
  ],
  "unmapped_downstreams": ["str"],
  "inherited_severity": "critical|high|medium|low|none",
  "verdict": "PASS|PARTIAL|FAIL"
}
```

## Failure modes

- **Treating an unmapped downstream as clean.** Absence of a record is absence
  of assessment.
- **Ignoring expired exceptions** because the risk is still recorded as
  accepted. An expired exception is an open risk with a date on it.
