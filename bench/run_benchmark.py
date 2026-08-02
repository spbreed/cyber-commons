#!/usr/bin/env python3
"""Score a harness findings file (Mantis historical_learnings.jsonl schema)
against the ground-truth datasource using the Sola four-stage evaluation.

Usage:
    python bench/run_benchmark.py --findings data/mantis_findings.sample.jsonl \
        [--harness mantis] [--run-id nightly-2026-08-02] \
        [--gt-source secllmholmes-handcrafted] [--judges] [--min-acc 0.80]
"""
import argparse
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import JUDGE_METRICS, Matcher, expert_score, judge, resolve_cwe, split_path_line

ROOT = Path(__file__).resolve().parent.parent
MANTIS_SCHEMA = ROOT / "bench" / "mantis_schema.json"

# Mantis finding.status values that mean "not an active positive finding": the
# harness itself has retracted them, so they must not count as flags/FPs.
INACTIVE_STATUS = {"FALSE_POSITIVE", "DUPLICATE", "NON_VIABLE"}


def _load_validator(kind: str):
    """Return a callable(obj)->error|None validating against google/mantis
    schema.json (vendored at bench/mantis_schema.json). `kind` is a $defs key
    (learning_entry | finding). Returns None if jsonschema/schema unavailable."""
    if not MANTIS_SCHEMA.exists():
        return None
    try:
        import jsonschema
    except ImportError:
        return None
    root = json.loads(MANTIS_SCHEMA.read_text())
    sub = {**root, "$ref": f"#/$defs/{kind}"}
    validator = jsonschema.Draft202012Validator(sub)

    def _check(obj):
        errs = sorted(validator.iter_errors(obj), key=lambda e: e.path)
        return errs[0].message if errs else None
    return _check


def ingest_findings(con, path: Path, run_id: str, harness: str, validate: bool = True):
    """Ingest a Mantis findings file. Accepts both the history-inbox
    `learning_entry` shape (revision_id/vuln_type/mitigation_diff) and the
    richer `finding` object (id/cwe/status/mitigation/patch_diff)."""
    # scores reference findings, so clear them first to keep reruns idempotent
    con.execute("DELETE FROM scores WHERE run_id = ? AND harness = ?", (run_id, harness))
    con.execute("DELETE FROM findings WHERE run_id = ? AND harness = ?", (run_id, harness))
    findings = []
    stats = {"lines": 0, "ingested": 0, "skipped_status": 0, "schema_warnings": 0, "shape": set()}

    with open(path) as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            stats["lines"] += 1
            raw = json.loads(line)

            # trajectory_insight learning lines carry no finding to score
            if raw.get("type") == "trajectory_insight":
                continue

            is_finding_obj = "id" in raw and "status" in raw
            stats["shape"].add("finding" if is_finding_obj else "learning_entry")

            status = (raw.get("status") or "").upper()
            if status in INACTIVE_STATUS:
                stats["skipped_status"] += 1
                continue

            code_paths = raw.get("code_paths") or []
            file_path, line_no = split_path_line(code_paths[0]) if code_paths else (None, None)

            # explicit finding.cwe wins; else resolve free-text vuln_type/title/desc
            cwe = raw.get("cwe") or resolve_cwe(raw.get("vuln_type"), raw.get("title"), raw.get("description"))
            if cwe:
                m = __import__("re").search(r"CWE[-_ ]?(\d+)", cwe, __import__("re").IGNORECASE)
                cwe = f"CWE-{int(m.group(1))}" if m else cwe
            mitigation = raw.get("mitigation_diff") or raw.get("patch_diff") or raw.get("mitigation")

            cur = con.execute(
                """INSERT INTO findings (run_id, harness, revision_id, title, description,
                       file_path, line, code_paths, vuln_type, cwe, mitigation_diff, cve)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (run_id, harness, raw.get("revision_id") or raw.get("id"), raw.get("title"),
                 raw.get("description"), file_path, line_no, json.dumps(code_paths),
                 raw.get("vuln_type"), cwe, mitigation, raw.get("cve")),
            )
            findings.append({**raw, "id": cur.lastrowid, "file_path": file_path,
                             "line": line_no, "cwe": cwe, "mitigation_diff": mitigation})

    if validate:
        _run_schema_validation(path, stats)
    print(f"ingest: {len(findings)} scored, "
          f"{stats['skipped_status']} retracted (FALSE_POSITIVE/DUPLICATE), "
          f"shapes={sorted(stats['shape']) or ['(none)']}")
    return findings


def _run_schema_validation(path: Path, stats: dict) -> None:
    """Validate every line against the matching google/mantis $defs sub-schema
    and report conformance (non-fatal)."""
    learn_v = _load_validator("learning_entry")
    find_v = _load_validator("finding")
    if not learn_v or not find_v:
        print("schema: jsonschema or bench/mantis_schema.json unavailable; skipped validation")
        return
    ok = bad = 0
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        validator = find_v if ("id" in obj and "status" in obj) else learn_v
        err = validator(obj)
        if err:
            bad += 1
            if bad <= 3:
                print(f"schema: line invalid vs google/mantis contract: {err[:120]}")
        else:
            ok += 1
    print(f"schema: {ok}/{ok + bad} lines conform to google/mantis schema.json")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--findings", required=True)
    ap.add_argument("--harness", default="mantis")
    ap.add_argument("--run-id", default=dt.date.today().isoformat())
    ap.add_argument("--gt-source", default=None,
                    help="restrict scoring to one ground_truth source (e.g. secllmholmes-handcrafted)")
    ap.add_argument("--judges", action="store_true",
                    help="use real Anthropic judges (needs ANTHROPIC_API_KEY); offline heuristic otherwise")
    ap.add_argument("--min-acc", type=float, default=None,
                    help="exit non-zero if Expert Accuracy falls below this threshold")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip validation of findings against the vendored google/mantis schema.json")
    ap.add_argument("--db", default=str(ROOT / "data" / "vulnbench.db"))
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.row_factory = sqlite3.Row
    con.executescript((ROOT / "bench" / "schema.sql").read_text())

    findings = ingest_findings(con, Path(args.findings), args.run_id, args.harness,
                               validate=not args.no_validate)

    if args.gt_source:
        gt_rows = con.execute("SELECT * FROM ground_truth WHERE source = ?", (args.gt_source,)).fetchall()
    else:
        gt_rows = con.execute("SELECT * FROM ground_truth").fetchall()
    if not gt_rows:
        print(f"no ground truth rows{' for source ' + args.gt_source if args.gt_source else ''}; "
              "run ingest/build_datasource.py first")
        return 2

    matcher = Matcher(gt_rows)
    matched: dict[int, dict] = {}  # gt id -> finding
    for f in findings:
        if not f.get("file_path"):
            continue
        for gt in matcher.match(f["file_path"]):
            matched.setdefault(gt["id"], f)

    con.execute("DELETE FROM scores WHERE run_id = ? AND harness = ?", (args.run_id, args.harness))
    results = []
    for gt in gt_rows:
        f = matched.get(gt["id"])
        score, outcome = expert_score(gt, f)
        jscores, jmode = judge(gt, f, outcome, use_api=args.judges)
        results.append((gt, f, score, outcome, jscores))
        con.execute(
            """INSERT INTO scores (run_id, harness, gt_id, finding_id, outcome, expert_score,
                   faithfulness, hallucination_free, correctness, retrieval_use, example_adapt, judge_mode)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (args.run_id, args.harness, gt["id"], f["id"] if f else None, outcome, score,
             *[(jscores or {}).get(k) for k in JUDGE_METRICS],
             jmode if jscores else None),
        )
    con.commit()

    # ---- report ----------------------------------------------------------
    n = len(results)
    expert_acc = sum(r[2] for r in results) / n
    success = sum(1 for r in results if r[2] == 1.0) / n
    judged = [r[4] for r in results if r[4]]
    halluc_free = (sum(j["hallucination_free"] for j in judged) / len(judged)) if judged else None

    scope = args.gt_source or "ALL"
    print(f"\n=== vulnbench report  run={args.run_id}  harness={args.harness}  gt-source={scope} ===")
    print(f"ground-truth rows scored : {n}")
    print(f"findings ingested        : {len(findings)}")
    print(f"Expert Accuracy          : {expert_acc:.4f}")
    print(f"Success Rate (full credit): {success:.4f}")
    print(f"Hallucination-free (judged pairs): {halluc_free:.4f}" if halluc_free is not None
          else "Hallucination-free       : n/a (no judged pairs)")

    by_cwe: dict[str, list] = {}
    for gt, f, score, outcome, _ in results:
        by_cwe.setdefault(gt["cwe"] or "(no-CWE/IaC)", []).append((gt, f, score, outcome))
    print("\nby-CWE:")
    print(f"  {'CWE':14s} {'n':>3s} {'vuln_recall':>11s} {'expert_acc':>10s}  notes")
    for cwe in sorted(by_cwe):
        rows = by_cwe[cwe]
        vuln = [r for r in rows if r[0]["is_vulnerable"]]
        recall = (sum(1 for r in vuln if r[3] != "miss") / len(vuln)) if vuln else float("nan")
        acc = sum(r[2] for r in rows) / len(rows)
        notes = []
        for _, _, _, outcome in rows:
            if outcome in ("miss", "false_positive", "tp_wrong_cwe"):
                notes.append(outcome)
        note = ",".join(sorted(set(notes), key=notes.index)) if notes else ""
        rec = f"{recall:11.2f}" if vuln else f"{'—':>11s}"
        print(f"  {cwe:14s} {len(rows):3d} {rec} {acc:10.2f}  {note}")

    if judged:
        print("\nmean judge metrics (two judges, MIN-aggregated):")
        for k in JUDGE_METRICS:
            print(f"  {k:20s} {sum(j[k] for j in judged) / len(judged):.4f}")
        modes = {r[4] and 'judged' for r in results}
        _ = modes
        mode_row = con.execute(
            "SELECT DISTINCT judge_mode FROM scores WHERE run_id=? AND harness=? AND judge_mode IS NOT NULL",
            (args.run_id, args.harness)).fetchall()
        print(f"  judge mode: {', '.join(m[0] for m in mode_row)}")

    con.close()

    if args.min_acc is not None and expert_acc < args.min_acc:
        print(f"\nREGRESSION: Expert Accuracy {expert_acc:.4f} < threshold {args.min_acc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
