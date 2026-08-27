---
name: iam-least-privilege-verifier
description: >-
  Prove a deployment's role baseline is default-deny and quantify granted-
  but-unused permissions against observed usage. Use to evidence least
  privilege, to find excess permissions on an agent role, or when asked
  whether a deployment's IAM posture supports a default-deny claim.
allowed-tools: Bash, Read
---

# Iam Least Privilege Verifier

**Controls:** Control 1 — default-deny and least privilege

## Confidence: HIGH

This is one of the controls that is genuinely provable at runtime. Policy
documents are readable, and usage data turns "least privilege" from an
assertion into a measured delta.

## Procedure

1. **Establish the default-deny baseline.** Read every inline and attached
   policy. The baseline fails if any of these are present:
   - `Action: "*"` or `Resource: "*"` in an Allow statement
   - broad managed policies such as administrator or power-user equivalents
   - a wildcard principal on a trust policy

2. **Measure excess.** Compare granted permissions against observed usage from
   the access-analysis and last-accessed data. Count actions, roles, keys and
   passwords idle for at least the tracking period (configurable 1–180 days;
   default 90).

3. **Generate the least-privilege diff.** Policy generation derived from actual
   activity produces a candidate policy; the diff against what is granted is
   the excess-permission finding, expressed concretely rather than as a score.

4. **Check external access.** External-access findings must be zero, or each
   one must map to an approved exception.

## Output contract

```json
{
  "deployment_id": "str",
  "role_arn": "str",
  "default_deny_verified": true,
  "wildcard_findings": [{"policy": "str", "statement": "str"}],
  "excess_permission_count": 0,
  "unused": [{"type": "action|role|key|password", "name": "str", "idle_days": 0}],
  "generated_policy_diff": "str",
  "external_access_findings": 0,
  "tracking_period_days": 90,
  "verdict": "PASS|PARTIAL|FAIL"
}
```

## Failure modes

- **Incomplete audit-trail coverage.** If the trail is not intact, "unused" is
  unreliable and the verdict must be `PARTIAL`. Policy generation can miss
  legitimately-used-but-rare actions — an annual disaster-recovery permission
  looks identical to dead permission over a 90-day window.
- **Counting managed-policy names instead of effective actions.** Two policies
  can grant the same action; the union is what matters.
- **Treating a low excess count as a pass** while a wildcard is present. The
  baseline check is a gate, not a contributor to a score.
