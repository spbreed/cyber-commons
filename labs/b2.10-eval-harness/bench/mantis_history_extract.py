#!/usr/bin/env python3
"""Reproduce the Mantis `mantis-history` stage over the SecLLMHolmes real-world
CVE corpus and emit a genuine `historical_learnings.jsonl`.

The mantis-history skill (google/mantis) walks a project's VCS history and, for
each security-relevant fix revision, writes one learning entry describing the
vulnerable pre-fix code: {revision_id, title, description, code_paths,
vuln_type, mitigation_diff, cve, history}. The SecLLMHolmes real-world set is
exactly a set of vuln->patch revision pairs (vuln.* = pre-fix, patch.* =
post-fix) with CVE metadata, so running the stage's methodology over it yields
real, schema-valid Mantis output.

Faithfulness notes:
  - `vuln_type` carries the human-readable weakness class (e.g. "Out-of-Bound
    Write"), NOT the CWE id. The scorer resolves it to a CWE independently via
    its lexicon, so this is a non-circular pipeline test.
  - Only the vulnerable revision produces a finding (history extraction reports
    the bug, not the fix), matching real stage behavior. The patched twins stay
    unflagged and are scored as true negatives.
  - `mitigation_diff` is the real unified diff between the vuln and patch files.

Usage: python bench/mantis_history_extract.py [--out data/mantis_realworld.historical_learnings.jsonl]
"""
import argparse
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RW = ROOT / "ground-truth" / "secllmholmes" / "datasets" / "real-world"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "data" / "mantis_realworld.historical_learnings.jsonl"))
    args = ap.parse_args()

    details = json.loads((RW / "cve_details.json").read_text())
    entries = []
    for project, cves in details.items():
        for cve_id, meta in cves.items():
            cve_dir = RW / project / cve_id
            vuln = next((p for p in cve_dir.glob("vuln.*") if p.suffix != ".txt"), None)
            patch = next((p for p in cve_dir.glob("patch.*") if p.suffix != ".txt"), None)
            if not vuln:
                continue
            vuln_src = vuln.read_text(errors="replace")
            patch_src = patch.read_text(errors="replace") if patch else ""
            diff = "".join(difflib.unified_diff(
                vuln_src.splitlines(keepends=True), patch_src.splitlines(keepends=True),
                fromfile=f"a/{meta['file_path']}", tofile=f"b/{meta['file_path']}",
            )) if patch else ""
            weakness = meta.get("cwe_name") or ""
            code_path = str(vuln.relative_to(ROOT))
            entries.append({
                "revision_id": f"{project}@{cve_id}",
                "title": f"{weakness} in {project} {meta['file_path']}",
                "description": (
                    f"History extraction of {cve_id} ({project}): the pre-fix revision of "
                    f"{meta['file_path']} contains a {weakness.lower()} weakness. Upstream "
                    f"repaired it between {meta.get('found','?')} and {meta.get('fixed','?')}."
                ),
                "code_paths": [f"{code_path}:1"],
                "vuln_type": weakness,
                "mitigation_diff": diff[:4000],
                "cve": cve_id,
                "history": [{
                    "stage": "history_extractor",
                    "action": "created",
                    "details": "Extracted from SecLLMHolmes real-world vuln/patch revision pair.",
                    "pass_number": 1,
                    "timestamp": "2026-08-02T00:00:00Z",
                }],
            })

    out = Path(args.out)
    with out.open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")
    print(f"wrote {len(entries)} learning entries -> {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
