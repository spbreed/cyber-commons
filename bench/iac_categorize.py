#!/usr/bin/env python3
"""Deterministic mapping of a Checkov check name to one security category.

Objective keyword rules (first match wins) so the TerraGoat ground truth is
reproducible and not hand-labeled. Categories are the controlled vocabulary the
models are scored against.
"""
CATEGORIES = [
    "SECRETS",           # hard-coded secrets/keys, secret expiry
    "VERSIONING",        # object versioning
    "PUBLIC_ACCESS",     # resource publicly/anonymously reachable, public IP/endpoint
    "NETWORK_CONTROLS",  # security groups, firewall/NSG rules, restricted SSH/RDP
    "TRANSIT_TLS",       # TLS/SSL/HTTPS in transit
    "ENCRYPTION",        # data-at-rest encryption, KMS/CMK, disk/HSM
    "LOGGING_MONITORING",# logging, audit, monitoring, tracing, threat detection
    "BACKUP_DR",         # backup, retention, deletion protection, snapshots, HA
    "IAM_ACCESS",        # IAM least-privilege, RBAC, auth, MFA, admin roles
    "HARDENING",         # catch-all (config hardening not covered above)
]

RULES = [
    ("SECRETS", ["hard coded", "hard-coded", "high entropy", "access key",
                 "no hard", "secrets have", "expiration date is set"]),
    ("VERSIONING", ["versioning"]),
    ("PUBLIC_ACCESS", ["publicly", "public access", "public network", "public ip",
                       "public endpoint", "anonymous", "to the world", "not public",
                       "not be public", "public ports", "restrict public", "disallow public",
                       "public clusters", "control plane is not public", "endpoint not accessible",
                       "endpoint disabled", "open to the world"]),
    ("NETWORK_CONTROLS", ["ingress", "egress", "security group", "0.0.0.0", "firewall",
                          "network security group", "nsg", "ssh access", "rdp access",
                          "restricted from the internet", "network policy", "port 22",
                          "port 80", "authorized ip", "private endpoint", "private cluster",
                          "private nodes", "private_ip", "api server authorized"]),
    ("TRANSIT_TLS", ["tls", "ssl", "https", "in transit", "enforce ssl", "http traffic",
                     "http version", "redirects all http", "connection requests over http",
                     "secure protocols", "requires all incoming connections to use ssl"]),
    ("ENCRYPTION", ["encrypt", "encryption", "cmk", "kms", "customer managed key",
                    "customer master key", "customer supplied encryption", "at rest",
                    "disk encryption", "backed by hsm", "secrets encryption", "csek"]),
    ("LOGGING_MONITORING", ["logging", "log ", "log_", "audit", "monitor", "tracing",
                            "flow log", "trail", "stackdriver", "threat detection",
                            "detailed monitoring", "enhanced monitoring", "access logging",
                            "logs", "log capture", "diagnostic", "activity log"]),
    ("BACKUP_DR", ["backup", "retention", "deletion protection", "snapshot", "soft-delete",
                   "geo-redundant", "multi-az", "replication", "recoverable", "purge protection",
                   "copy tags", "backtracking", "lifecycle", "cross-region", "high availability",
                   "dedicated master", "deletion"]),
    ("IAM_ACCESS", ["iam", "rbac", "authentication", "mfa", "least privilege", "privilege",
                    "credentials", "admin", "owner roles", "sso", "azure ad",
                    "active directory", "password authentication", "basic authentication",
                    "managed identity", "role is attached", "oslogin", "legacy authorization",
                    "binary authorization", "client certificate"]),
]


def categorize(check_name: str) -> str:
    n = (check_name or "").lower()
    for cat, kws in RULES:
        if any(k in n for k in kws):
            return cat
    return "HARDENING"


if __name__ == "__main__":
    import sqlite3, sys, json
    from collections import Counter, defaultdict
    from pathlib import Path
    db = Path(__file__).resolve().parent.parent / "data" / "vulnbench.db"
    con = sqlite3.connect(db)
    rows = con.execute("SELECT file_path, vuln_name FROM ground_truth WHERE source='terragoat' AND vuln_name IS NOT NULL").fetchall()
    per_file = defaultdict(set)
    cat_counts = Counter()
    for fp, name in rows:
        c = categorize(name)
        per_file[fp].add(c)
        cat_counts[c] += 1
    print("category distribution (per failed check):")
    for c in CATEGORIES:
        print(f"  {c:20s} {cat_counts[c]}")
    print(f"\nfiles: {len(per_file)}; mean categories/file: {sum(len(v) for v in per_file.values())/len(per_file):.1f}")
    if len(sys.argv) > 1 and sys.argv[1] == "--dump":
        Path("work_mantis/iac_truth.json").write_text(
            json.dumps({fp: sorted(cs) for fp, cs in sorted(per_file.items())}, indent=1))
        print("wrote work_mantis/iac_truth.json")
