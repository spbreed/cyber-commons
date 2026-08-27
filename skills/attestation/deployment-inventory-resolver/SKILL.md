---
name: deployment-inventory-resolver
description: >-
  Resolve a deployment_id into the artifacts that make up one agentic
  deployment and build the evidence graph every other attestation skill
  consumes. Use first, before any control is evaluated, or when asked which
  repo, image, role, workload identity, gateway or guardrail a deployment
  actually consists of.
allowed-tools: Bash, Read, Grep, Glob
---

# Deployment Inventory Resolver

**Controls:** All — this skill produces the join key

## Why this runs first

`deployment_id` is the primary key for every other skill in this set. Without
it, an IAM finding, a SPIFFE entry and a gateway policy are three unrelated
facts about three things that may or may not be the same system.

This skill turns that ID into a manifest of content-addressed artifacts, so
every later finding resolves to one evaluable unit and cannot be silently
confused with a neighbouring deployment.

## Procedure

1. **Resolve the code.** Repository URL plus the exact commit SHA that was
   built. Not a branch — a branch moves.
2. **Resolve the image.** Registry digest (`sha256:…`), not a tag. Confirm the
   digest matches the revision actually deployed, not the newest build.
3. **Resolve the runtime identity.** The IAM role ARN, the SPIFFE ID, and —
   on platforms that auto-create one — the workload identity ARN exposed by the
   runtime/gateway description API.
4. **Resolve the traffic path.** Gateway or route ARN, and the guardrail ID
   attached to it.
5. **Resolve the downstreams.** Every service the deployment's tools call.
   These become the input to the risk-registry skill.
6. **Cross-link and check completeness.** Every artifact must reference the
   others. Report orphans rather than omitting them.

## Output contract

```json
{
  "deployment_id": "str",
  "resolved_at": "str",
  "artifacts": {
    "repo": {"url": "str", "commit": "str"},
    "image": {"registry": "str", "digest": "str", "matches_deployed": true},
    "identity": {"role_arn": "str", "spiffe_id": "str", "workload_identity_arn": "str"},
    "traffic": {"gateway_arn": "str", "guardrail_id": "str"},
    "downstreams": ["str"]
  },
  "missing": ["str"],
  "orphans": ["str"],
  "verdict": "PASS|PARTIAL|FAIL"
}
```

A manifest with entries in `missing` is `PARTIAL` at best. Every downstream
skill inherits that ceiling — you cannot attest a control on an artifact you
could not resolve.

## Failure modes

- **Resolving a tag instead of a digest.** Tags are mutable; the thing you
  attested is not necessarily the thing running.
- **Treating an unresolvable artifact as absent.** "No gateway configured" and
  "I could not read the gateway API" are different findings.
- **Reusing a manifest across runs.** Re-resolve. Drift is the point.
