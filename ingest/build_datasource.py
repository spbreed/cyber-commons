#!/usr/bin/env python3
"""Build data/vulnbench.db from the OSS ground-truth sources in sources.yaml.

Shallow-clones each active repo into _repos/ and loads labeled rows into the
ground_truth table. Idempotent: rows for a source are replaced on re-run.

Usage:
    python ingest/build_datasource.py [--only secllmholmes terragoat] [--db data/vulnbench.db]
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPOS_DIR = ROOT / "_repos"
SCHEMA = ROOT / "bench" / "schema.sql"


def log(msg: str) -> None:
    print(msg, flush=True)


def ensure_clone(name: str, url: str) -> Path:
    dest = REPOS_DIR / name
    if (dest / ".git").exists():
        return dest
    REPOS_DIR.mkdir(exist_ok=True)
    log(f"[{name}] cloning {url} ...")
    subprocess.run(["git", "clone", "--quiet", "--depth", "1", url, str(dest)], check=True)
    return dest


def norm_cwe(raw: str) -> str:
    digits = "".join(ch for ch in raw if ch.isdigit())
    return f"CWE-{int(digits)}" if digits else raw.upper()


# --- parser: secllmholmes -------------------------------------------------

def parse_secllmholmes(repo: Path):
    """Yield (source, row) tuples for hand-crafted samples and real-world CVEs."""
    hc = repo / "datasets" / "hand-crafted"
    for cwe_dir in sorted((hc / "dataset").glob("CWE-*")):
        cwe = cwe_dir.name.upper()
        for f in sorted(cwe_dir.iterdir()):
            is_safe = f.name.startswith("p_")
            gt_txt = hc / "ground-truth" / cwe_dir.name / (f.stem + ".txt")
            rationale = gt_txt.read_text(errors="replace").strip() if gt_txt.exists() else None
            yield "secllmholmes-handcrafted", {
                "file_path": str(f.relative_to(repo)),
                "is_vulnerable": 0 if is_safe else 1,
                "cwe": cwe,
                "vuln_name": cwe,
                "rationale": rationale,
                "cve": None,
                "check_id": None,
                "line_start": None,
                "line_end": None,
            }

    rw = repo / "datasets" / "real-world"
    details = json.loads((rw / "cve_details.json").read_text())
    for project, cves in details.items():
        for cve_id, meta in cves.items():
            cve_dir = rw / project / cve_id
            if not cve_dir.is_dir():
                continue
            for kind, vulnerable in (("vuln", 1), ("patch", 0)):
                sources = [p for p in cve_dir.glob(kind + ".*") if p.suffix != ".txt"]
                if not sources:
                    continue
                src = sources[0]
                txt = cve_dir / (kind + ".txt")
                yield "secllmholmes-realworld", {
                    "file_path": str(src.relative_to(repo)),
                    "is_vulnerable": vulnerable,
                    "cwe": norm_cwe(meta.get("cwe", "")),
                    "vuln_name": meta.get("cwe_name"),
                    "rationale": txt.read_text(errors="replace").strip() if txt.exists() else None,
                    "cve": cve_id,
                    "check_id": None,
                    "line_start": None,
                    "line_end": None,
                }


# --- parser: checkov_oracle -----------------------------------------------

def find_checkov() -> str | None:
    env = os.environ.get("CHECKOV_BIN")
    if env and Path(env).exists():
        return env
    sibling = Path(sys.executable).parent / "checkov"
    if sibling.exists():
        return str(sibling)
    return shutil.which("checkov")


def parse_checkov_oracle(repo: Path, scan_dir: str, source_name: str):
    checkov = find_checkov()
    if not checkov:
        log(f"[{source_name}] checkov not found; skipping (install checkov to enable this oracle)")
        return
    target = repo / scan_dir
    log(f"[{source_name}] running checkov on {target} ...")
    proc = subprocess.run(
        [checkov, "-d", str(target), "-o", "json", "--compact", "--quiet"],
        capture_output=True, text=True,
    )
    out = proc.stdout.strip()
    if not out:
        log(f"[{source_name}] checkov produced no output (stderr: {proc.stderr[-300:]}); skipping")
        return
    data = json.loads(out)
    # checkov emits a LIST of per-framework result objects when multiple
    # frameworks match; a single dict otherwise.
    frameworks = data if isinstance(data, list) else [data]
    prefix = "" if scan_dir in (".", "") else scan_dir.rstrip("/")
    for fw in frameworks:
        results = fw.get("results", {}) if isinstance(fw, dict) else {}
        for check in results.get("failed_checks", []) or []:
            rel = check.get("file_path", "").lstrip("/")
            file_path = f"{prefix}/{rel}" if prefix else rel
            rng = check.get("file_line_range") or [None, None]
            yield source_name, {
                "file_path": file_path,
                "is_vulnerable": 1,
                "cwe": None,
                "vuln_name": check.get("check_name") or check.get("check_id"),
                "rationale": check.get("guideline"),
                "cve": None,
                "check_id": check.get("check_id"),
                "line_start": rng[0],
                "line_end": rng[1],
            }


# --- driver ---------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", nargs="*", help="source names to build (default: all active)")
    ap.add_argument("--db", default=str(ROOT / "data" / "vulnbench.db"))
    args = ap.parse_args()

    with open(ROOT / "ingest" / "sources.yaml") as fh:
        registry = yaml.safe_load(fh)["sources"]

    selected = []
    for src in registry:
        if args.only:
            if src["name"] in args.only:
                selected.append(src)
        elif src.get("active"):
            selected.append(src)
    if args.only:
        unknown = set(args.only) - {s["name"] for s in registry}
        if unknown:
            log(f"unknown sources: {sorted(unknown)}")
            return 2

    Path(args.db).parent.mkdir(exist_ok=True)
    con = sqlite3.connect(args.db)
    con.executescript(SCHEMA.read_text())

    counts: dict[str, int] = {}
    for src in selected:
        name, parser = src["name"], src["parser"]
        if parser == "stub" or (not src.get("active") and not args.only):
            log(f"[{name}] stub/inactive; skipping")
            continue
        if not src.get("active"):
            log(f"[{name}] registered but deploy-gated ({src.get('reason', 'inactive')}); skipping")
            continue
        repo = ensure_clone(name, src["repo"])
        if parser == "secllmholmes":
            rows = parse_secllmholmes(repo)
        elif parser == "checkov_oracle":
            rows = parse_checkov_oracle(repo, src.get("scan_dir", "."), name)
        else:
            log(f"[{name}] unknown parser {parser!r}; skipping")
            continue

        staged: dict[str, list[dict]] = {}
        for source_label, row in rows:
            staged.setdefault(source_label, []).append(row)
        for source_label, batch in staged.items():
            # scores and derived questions reference ground_truth rows; clear
            # them first so a source refresh stays idempotent (loader.py
            # re-derives the code_vuln questions afterwards)
            con.execute(
                "DELETE FROM scores WHERE gt_id IN (SELECT id FROM ground_truth WHERE source = ?)",
                (source_label,),
            )
            con.execute(
                "DELETE FROM questions WHERE ground_truth_ref IN "
                "(SELECT id FROM ground_truth WHERE source = ?)",
                (source_label,),
            )
            con.execute("DELETE FROM ground_truth WHERE source = ?", (source_label,))
            con.executemany(
                """INSERT INTO ground_truth
                   (source, file_path, is_vulnerable, cwe, vuln_name, check_id,
                    line_start, line_end, rationale, cve)
                   VALUES (:source, :file_path, :is_vulnerable, :cwe, :vuln_name,
                           :check_id, :line_start, :line_end, :rationale, :cve)""",
                [dict(r, source=source_label) for r in batch],
            )
            counts[source_label] = len(batch)
    con.commit()

    log("\nground_truth rows by source:")
    total = 0
    for source_label, n in con.execute(
        "SELECT source, COUNT(*) FROM ground_truth GROUP BY source ORDER BY source"
    ):
        log(f"  {source_label:28s} {n:5d}")
        total += n
    log(f"  {'TOTAL':28s} {total:5d}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
