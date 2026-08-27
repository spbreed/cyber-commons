#!/usr/bin/env python3
"""Identify the AI security *control intent* of an agent or MCP server repository.

Control intent is a narrower and more honest claim than "is this secure". It
asks: **does this codebase contain evidence that its authors intended a given
control to exist?** A repository that imports a sandbox, validates an audience
claim, or routes every model call through one client has left intent behind in
the code. One that does none of those has not.

That distinction matters because intent is what static analysis can actually
establish. Whether the control *holds at runtime* needs a live deployment, and
the skills in `skills/attestation/` that require one say so rather than
guessing.

    python3 labs/attestation/control_intent.py <repo> [<repo> ...]
    python3 labs/attestation/control_intent.py --corpus /home/user/corpus --out results.json

Emits one in-toto-shaped, DSSE-framed attestation per repository, with an
OSCAL-flavoured predicate carrying a per-control verdict, the evidence that
produced it, and the confidence ceiling that applies.

Standard library only. Deterministic: the same commit produces the same
attestation, byte for byte, which is what makes drift detection meaningful.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# What we look for. Each signal is a regex plus the control it evidences.
# Signals are *intent*, not proof — the naming throughout keeps that honest.
# --------------------------------------------------------------------------

SOURCE_SUFFIXES = {".py", ".ts", ".js", ".go", ".rs", ".java", ".rb"}
CONFIG_SUFFIXES = {".json", ".yaml", ".yml", ".toml"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", "vendor", "__pycache__",
             ".venv", "venv", "target", ".next", "coverage", "testdata"}

# tool declaration sites — how an agent or MCP server says "this is a tool"
TOOL_DECL = [
    (r"@(?:mcp|server|app)\.tool\b",              "mcp decorator"),
    (r"@tool\b",                                   "framework decorator"),
    (r"\bTool\s*\(",                              "tool constructor"),
    (r"\bStructuredTool\b",                       "structured tool"),
    (r"\blist_tools\b|\bListToolsRequest",        "mcp list_tools"),
    (r"\bcall_tool\b|\bCallToolRequest",          "mcp call_tool"),
    (r"\bfunction_tool\b",                        "function tool"),
]

# dangerous sinks — what a tool can actually reach
SINKS = [
    (r"\bsubprocess\.(?:run|Popen|call|check_output)\b|\bos\.system\b|\bexec\.Command\b",
     "process", "process execution"),
    (r"\beval\s*\(|\bexec\s*\(",                 "process", "dynamic evaluation"),
    (r"open\s*\([^)]*['\"][wa]\+?['\"]|\bos\.remove\b|\bshutil\.rmtree\b|\bos\.WriteFile\b",
     "filesystem", "filesystem write or delete"),
    (r"\brequests\.(?:get|post)\b|\bhttpx\.|\burllib\.request\b|\bfetch\s*\(|\bhttp\.Client\b",
     "network", "outbound http"),
    (r"\bboto3\.client\b|\bos\.environ\[[^\]]*(?:KEY|TOKEN|SECRET|PASSWORD)",
     "credential", "credential access"),
    (r"\bDROP\s+TABLE\b|\bDELETE\s+FROM\b|\bTRUNCATE\b",
     "destructive", "destructive sql"),
]

# MCP tool annotations — hints, not guarantees, per the specification
ANNOTATIONS = ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]

# control-intent signals, keyed by control id
CONTROL_SIGNALS = {
 "C1_default_deny_least_privilege": [
    (r"\bdefault[_-]?deny\b",                       "explicit default-deny"),
    (r"\ballow[_-]?list\b|\ballowlist\b|\bwhitelist\b", "allowlist"),
    (r"\bpermission(?:s)?[_-]?check\b|\bauthorize\b|\brequire_permission\b", "authorisation check"),
    (r"\brego\b|\bopa\b|\bcedar\b|\bcasbin\b",      "policy engine"),
    (r"\bleast[_-]?privilege\b",                    "least privilege"),
    (r"\bIsAllowed\b|\bcheck_access\b|\bhas_scope\b", "access check"),
 ],
 "C2_sandbox_no_egress": [
    (r"\bfirecracker\b|\bgvisor\b|\brunsc\b|\bkata[_-]?container",  "isolation runtime"),
    (r"\bseccomp\b|\bapparmor\b|\bcgroup",          "kernel confinement"),
    (r"\be2b\b|\bpyodide\b|\bwasmtime\b|\bwasmer\b", "sandboxed interpreter"),
    (r"\bnetwork[_-]?mode\b|\bnetwork[_-]?disabled\b|\bno[_-]?network\b", "network mode control"),
    (r"\bdocker\b.*\b--network[= ]none\b|\bNetworkDisabled\b", "network disabled"),
    (r"\bRestrictedPython\b|\bsandbox\b",           "sandbox reference"),
 ],
 "C3_identity_chain_obo": [
    (r"\bspiffe\b|\bSVID\b|\bspire\b",              "workload identity"),
    (r"\bactor_token\b|\bmay_act\b|\bact\b\s*[:=]", "delegation claim"),
    (r"token[_-]?exchange|urn:ietf:params:oauth:grant-type:token-exchange", "rfc 8693 exchange"),
    (r"\baudience\b|\baud\b\s*[:=]|\ballowedAudience\b", "audience validation"),
    (r"\bon[_-]?behalf[_-]?of\b|\bOBO\b",            "on-behalf-of"),
    (r"\boauth2?\b.*\bPKCE\b|\bcode_challenge\b",   "oauth pkce"),
    (r"\bWWW-Authenticate\b|\bprotected[_-]?resource[_-]?metadata\b", "resource metadata"),
 ],
 "C4_gateway_guardrails": [
    (r"\bgateway\b",                                "gateway reference"),
    (r"\bguardrail",                                "guardrail"),
    (r"\bbase[_-]?url\b|\bendpoint[_-]?override\b|\bproxy\b", "endpoint indirection"),
    (r"\begress[_-]?(?:policy|allow)",              "egress policy"),
    (r"\bcontent[_-]?filter\b|\bmoderation\b",      "content filtering"),
 ],
 "C5_injection_screening": [
    (r"\bprompt[_-]?injection\b",                   "injection awareness"),
    (r"\bsanitiz|\bsanitis",                        "sanitisation"),
    (r"\bspotlight|\bdelimit",                      "spotlighting or delimiting"),
    (r"\bprompt[_-]?guard\b|\bllm[_-]?guard\b|\brebuff\b", "injection detector"),
    (r"\bprovenance\b|\buntrusted[_-]?(?:content|source|input)\b", "provenance tagging"),
    (r"\btrust(?:ed)?[_-]?(?:level|boundary|source)\b", "trust labelling"),
 ],
}

# Controls whose verdict may never exceed PARTIAL from static evidence, and why.
CEILINGS = {
 "C2_sandbox_no_egress":
   "absence of a covert channel is not provable from source; documented DNS and "
   "object-storage bypass paths exist even for approved sandboxes",
 "C5_injection_screening":
   "detector presence is verifiable; robustness is not - adaptive attacks drive "
   "published defences back above 95% success",
}

# Controls that cannot be judged at all without a live deployment.
RUNTIME_ONLY = {
 "C1_default_deny_least_privilege": "usage data and the effective role policy",
 "C4_gateway_guardrails": "reachability testing from the deployment's network position",
}

FRAMEWORKS = {
 "C1_default_deny_least_privilege": {"owasp_llm": ["LLM06"], "owasp_agentic": ["T2", "T3"]},
 "C2_sandbox_no_egress":            {"owasp_llm": ["LLM05"], "owasp_agentic": ["T11"]},
 "C3_identity_chain_obo":           {"owasp_llm": ["LLM06"], "owasp_agentic": ["T3", "T9"]},
 "C4_gateway_guardrails":           {"owasp_llm": ["LLM02"], "owasp_agentic": ["T2", "T6"]},
 "C5_injection_screening":          {"owasp_llm": ["LLM01"], "owasp_agentic": ["T6", "T12"]},
}


# --------------------------------------------------------------------------
def source_files(root: Path, cap: int = 4000) -> list[Path]:
    """Every source and config file, sorted, capped. Sorted keeps it deterministic."""
    out = []
    for p in sorted(root.rglob("*")):
        if len(out) >= cap:
            break
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix in SOURCE_SUFFIXES or p.suffix in CONFIG_SUFFIXES:
            try:
                if p.stat().st_size <= 512_000:
                    out.append(p)
            except OSError:
                pass
    return out


def scan(root: Path):
    """One pass over the tree, collecting every signal we care about."""
    files = source_files(root)
    tools, sinks, annotations = [], {}, {}
    control_hits = {cid: {} for cid in CONTROL_SIGNALS}
    scanned = 0

    for path in files:
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        scanned += 1
        rel = str(path.relative_to(root))

        for pattern, kind in TOOL_DECL:
            n = len(re.findall(pattern, text))
            if n:
                tools.append({"file": rel, "declaration": kind, "count": n})

        for pattern, cls, label in SINKS:
            if re.search(pattern, text):
                sinks.setdefault(cls, {"label": label, "files": []})
                if len(sinks[cls]["files"]) < 5:
                    sinks[cls]["files"].append(rel)

        for ann in ANNOTATIONS:
            if ann in text:
                annotations[ann] = annotations.get(ann, 0) + text.count(ann)

        for cid, signals in CONTROL_SIGNALS.items():
            for pattern, label in signals:
                if re.search(pattern, text, re.I):
                    hits = control_hits[cid].setdefault(label, [])
                    if len(hits) < 3:
                        hits.append(rel)

    return {"files_scanned": scanned, "tool_sites": tools, "sinks": sinks,
            "annotations": annotations, "control_hits": control_hits}


def verdict_for(cid: str, hits: dict) -> tuple[str, str, str]:
    """Turn signal hits into (verdict, confidence, why) — honestly.

    Static evidence can show intent. It cannot show enforcement, so nothing
    here returns PASS: the best available static verdict is INTENT_EVIDENCED,
    and controls that need a live deployment say exactly what is missing.
    """
    distinct = len(hits)
    if distinct == 0:
        return "NO_INTENT_FOUND", "STATIC", "no signal for this control in the source"
    if cid in CEILINGS:
        return "PARTIAL", "CAPPED", CEILINGS[cid]
    if cid in RUNTIME_ONLY:
        return ("INTENT_EVIDENCED", "STATIC",
                f"intent present in source; runtime verdict needs {RUNTIME_ONLY[cid]}")
    return ("INTENT_EVIDENCED", "STATIC",
            f"{distinct} distinct signals; enforcement not verifiable from source")


def git_commit(root: Path) -> str:
    try:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() or "unknown"
    except Exception:                                   # noqa: BLE001
        return "unknown"


def attest(root: Path, deployment_id: str | None = None) -> dict:
    """Produce one in-toto-shaped attestation for a repository."""
    root = root.resolve()
    did = deployment_id or root.name
    s = scan(root)

    controls = []
    for cid in sorted(CONTROL_SIGNALS):
        hits = s["control_hits"][cid]
        v, conf, why = verdict_for(cid, hits)
        controls.append({
            "id": cid, "verdict": v, "confidence": conf, "rationale": why,
            "signals": [{"signal": k, "evidence_files": v2} for k, v2 in sorted(hits.items())],
            "framework_mappings": FRAMEWORKS[cid],
        })

    # the rug-pull baseline: hash what the model reads, per the code-surface skill
    tool_files = sorted({t["file"] for t in s["tool_sites"]})
    surface = json.dumps({"tool_files": tool_files,
                          "sinks": sorted(s["sinks"]),
                          "annotations": sorted(s["annotations"])}, sort_keys=True)

    unannotated = not s["annotations"]
    predicate = {
        "deployment_id": did,
        "evaluator": "control_intent.py/1.0",
        "scope": "static source analysis only - no live deployment was inspected",
        "code_surface": {
            "files_scanned": s["files_scanned"],
            "tool_declaration_sites": len(s["tool_sites"]),
            "tool_files": tool_files[:10],
            "dangerous_sinks": [{"class": k, "what": v["label"], "examples": v["files"]}
                                for k, v in sorted(s["sinks"].items())],
            "mcp_annotations_found": s["annotations"],
            # the specification's pessimistic default, applied rather than assumed away
            "unannotated_default_applied": unannotated,
            "unannotated_default": ("destructiveHint=true, openWorldHint=true"
                                    if unannotated else None),
            "surface_hash": hashlib.sha256(surface.encode()).hexdigest()[:32],
        },
        "controls": controls,
        "drift": {"since": None, "changed": []},
    }
    return {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": did, "digest": {"gitCommit": git_commit(root)}}],
        "predicateType": "https://cyber-commons/attestations/ai-control-intent/v1",
        "predicate": predicate,
        # unsigned by design: signing is the attestation-signer skill's job, and
        # a fake signature here would be worse than none
        "signatures": [],
        "signing_note": "unsigned - see skills/attestation/attestation-signer-lifecycle",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repos", nargs="*", help="repository paths to analyse")
    ap.add_argument("--corpus", help="analyse every immediate subdirectory of this path")
    ap.add_argument("--out", help="write all attestations to this JSON file")
    a = ap.parse_args()

    targets = [Path(r) for r in a.repos]
    if a.corpus:
        targets += sorted(p for p in Path(a.corpus).iterdir() if p.is_dir())
    if not targets:
        ap.error("give at least one repository, or --corpus")

    results = []
    for t in targets:
        att = attest(t)
        results.append(att)
        p = att["predicate"]
        print(f"\n=== {p['deployment_id']} ===")
        print(f"  files scanned {p['code_surface']['files_scanned']:>5}   "
              f"tool sites {p['code_surface']['tool_declaration_sites']:>4}   "
              f"sinks {len(p['code_surface']['dangerous_sinks'])}")
        for c in p["controls"]:
            n = len(c["signals"])
            print(f"  {c['id']:34s}{c['verdict']:18s}{n} signal(s)")

    if a.out:
        Path(a.out).write_text(json.dumps(results, indent=1) + "\n")
        print(f"\nwrote {len(results)} attestations to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
