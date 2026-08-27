---
name: entitlement-overprivilege-analyzer
description: >-
  Analyse entitlement and identity registries to find over-privileged access
  held by a deployment's identities. Use to check granted entitlements
  against what the declared tools actually need, to find over-broad OAuth
  scopes on credential providers, or to find standing privilege.
allowed-tools: Bash, Read
---

# Entitlement Overprivilege Analyzer

**Controls:** Controls 1 and 3 — over-privileged access

## What this adds beyond the IAM verifier

The IAM verifier measures cloud permissions against cloud usage. This skill
measures **application-level entitlements** — relationship-graph authorisation,
OAuth scopes on stored credential providers, and identity-registry
relationships — against what the declared tool surface actually requires.

An agent can hold a minimal cloud role and an OAuth token with full mailbox
access.

## Procedure

1. **Take the required capability set** from the code-surface analyzer. This is
   the denominator: what the declared tools genuinely need.
2. **Enumerate granted entitlements** from the authorisation graph for every
   identity in the deployment manifest.
3. **Enumerate credential-provider scopes.** Stored OAuth scopes are frequently
   far wider than the tool needs, because the consent screen offered a bundle.
4. **Diff.** Every grant with no corresponding requirement is an over-privilege
   finding, and each needs a justification gap recorded — the grant, the
   requirement it was presumably for, and the absence.
5. **Flag standing privilege.** Any grant that is permanent rather than issued
   per task.

## Output contract

```json
{
  "deployment_id": "str",
  "identities": [
    {"id": "str",
     "granted": ["str"],
     "required_by_tools": ["str"],
     "excess": [{"grant": "str", "justification_gap": "str"}]}
  ],
  "oauth_scope_excess": [{"provider": "str", "granted_scope": "str", "needed_scope": "str"}],
  "standing_privilege": ["str"],
  "verdict": "PASS|PARTIAL|FAIL"
}
```

## Failure modes

- **Comparing grants against other grants.** The denominator is the tool
  surface, not a peer deployment.
- **Accepting a bundled OAuth scope** because it was what the provider offered.
- **Missing standing privilege** because the scope itself looked narrow.
