# Task: audit Terraform (IaC) for security misconfigurations

Authorized defensive security review. You are auditing Infrastructure-as-Code
(Terraform) files for **security misconfigurations** — the same job the Checkov
IaC scanner does. This is standard defensive cloud-security posture review of
configuration files; no exploit code is involved. For each file, report which
categories of misconfiguration are present.

## Rules

1. Analyze **file CONTENTS ONLY**. Filenames are opaque (`iac_01.tf`).
2. Do **NOT** read `work_mantis/*.secret.json`, `work_mantis/iac_truth.json`,
   any `verdicts*`/`iac_*` result files, or anything under `ground-truth/`.
   Only read the `.tf` files in the corpus directory given to you.
3. A single file usually has **several** categories. Report every category for
   which the file has at least one real misconfiguration (a missing or insecure
   setting on a resource). Judge by what the Terraform actually declares.

## Category vocabulary (use these labels exactly)

- `ENCRYPTION` — data-at-rest encryption missing/weak; no KMS/CMK/customer key.
- `TRANSIT_TLS` — no TLS/SSL/HTTPS enforcement in transit.
- `PUBLIC_ACCESS` — resource publicly/anonymously reachable; public IP/endpoint;
  publicly accessible DB/bucket.
- `NETWORK_CONTROLS` — permissive security groups / firewall / NSG rules; open
  SSH/RDP; missing network segmentation / private endpoints.
- `LOGGING_MONITORING` — logging, audit, monitoring, tracing, or threat
  detection disabled/missing.
- `BACKUP_DR` — no backup / retention / deletion protection / snapshots / HA /
  soft-delete / replication.
- `IAM_ACCESS` — over-broad IAM policy, missing RBAC/MFA/auth, admin/owner
  misuse, missing IAM authentication.
- `SECRETS` — hard-coded secrets/keys, missing secret expiry/rotation.
- `VERSIONING` — object versioning not enabled.
- `HARDENING` — other security hardening missing (deprecated runtime, immutable
  tags, instance metadata v1, healthchecks, EBS optimization, etc.).

## Output

Write ONE JSON file to the exact path given in your prompt, shape:

```json
{
  "model": "<your model>",
  "findings": {
    "iac_01.tf": ["ENCRYPTION", "PUBLIC_ACCESS", "LOGGING_MONITORING"],
    "iac_02.tf": ["IAM_ACCESS"]
  }
}
```

Include **every** file in the corpus exactly once, each mapped to a (possibly
empty) list of category labels from the vocabulary above. Output only the JSON.
