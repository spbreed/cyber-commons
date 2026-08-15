# Ground-truth repositories

This folder holds local clones of the OSS "deliberately vulnerable" projects
that vulnbench uses as labeled ground truth. The clones themselves are
**gitignored** (only this README is tracked) — `ingest/build_datasource.py`
shallow-clones any missing repo on demand, so a fresh checkout self-heals.

The registry of sources (URL, parser, active/deploy-gated flag) is
[`ingest/sources.yaml`](../ingest/sources.yaml).

## Active sources (rows in `data/vulnbench.db` today)

| Folder | Upstream | What it is | How vulnerabilities are labeled | Rows |
|---|---|---|---|---|
| `secllmholmes/` | [ai4cloudops/SecLLMHolmes](https://github.com/ai4cloudops/SecLLMHolmes) | Curated dataset for evaluating LLM vulnerability detection | Hand-crafted: per-CWE folders where `N.ext` is vulnerable and `p_N.ext` is its patched twin, with expert rationale text under `ground-truth/`. Real-world: `vuln.*`/`patch.*` file pairs for 15 CVEs plus `cve_details.json` metadata | 48 + 30 |
| `terragoat/` | [bridgecrewio/terragoat](https://github.com/bridgecrewio/terragoat) | Deliberately insecure Terraform (AWS/Azure/GCP) | Scanned with **Checkov**; every failed policy check becomes one vulnerable row (check id, file, line range) | 474 |

## Deploy-gated sources (cloned here, not yet ingested)

These are registered in `sources.yaml` with `active: false`: their ground
truth only becomes meaningful once the environment is deployed/rendered, so
ingestion is gated until then.

| Folder | Upstream | What it is | Gate |
|---|---|---|---|
| `cloudgoat/` | [RhinoSecurityLabs/cloudgoat](https://github.com/RhinoSecurityLabs/cloudgoat) | "Vulnerable by design" AWS scenarios | Scenarios are templated; scan after `cloudgoat create` renders real Terraform |
| `awsgoat/` | [ine-labs/AWSGoat](https://github.com/ine-labs/AWSGoat) | Vulnerable AWS infrastructure + app modules | IaC scan possible, full truth needs deployment |
| `iam-vulnerable/` | [BishopFox/iam-vulnerable](https://github.com/BishopFox/iam-vulnerable) | IAM privilege-escalation playground (Terraform) | Privesc paths exist only in a deployed account |
| `goad/` | [Orange-Cyberdefense/GOAD](https://github.com/Orange-Cyberdefense/GOAD) | Game of Active Directory — vulnerable AD lab | Ground truth requires a running AD range |
| `nyu-ctf/` | [NYU-LLM-CTF/NYU_CTF_Bench](https://github.com/NYU-LLM-CTF/NYU_CTF_Bench) | CTF challenge benchmark for LLM agents | Each challenge needs its runtime container |
| `cybench/` | [andyzorigin/cybench](https://github.com/andyzorigin/cybench) | Professional CTF task benchmark | Each task needs its runtime environment |

## Refreshing / re-cloning

```bash
python ingest/build_datasource.py --only secllmholmes terragoat   # active sources
```

To pre-clone everything (including gated sources) without ingesting:

```bash
cd ground-truth
while read -r name url; do
  [ -d "$name" ] || git clone --depth 1 "$url" "$name"
done <<'EOF'
secllmholmes   https://github.com/ai4cloudops/SecLLMHolmes
terragoat      https://github.com/bridgecrewio/terragoat
cloudgoat      https://github.com/RhinoSecurityLabs/cloudgoat
awsgoat        https://github.com/ine-labs/AWSGoat
iam-vulnerable https://github.com/BishopFox/iam-vulnerable
goad           https://github.com/Orange-Cyberdefense/GOAD
nyu-ctf        https://github.com/NYU-LLM-CTF/NYU_CTF_Bench
cybench        https://github.com/andyzorigin/cybench
EOF
```

(Folder names match the `name` field in `sources.yaml`, which is what the
builder expects.)

Note: cybench and NYU_CTF_Bench are large (~3 GB each with challenge
artifacts); the active sources are small.
