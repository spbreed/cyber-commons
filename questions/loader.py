#!/usr/bin/env python3
"""Load benchmark question suites into the questions table.

Loads questions/sola_ispm.json (77 expected) and questions/sola_crossvendor.json
(50 expected) verbatim — it never fabricates question text; empty suite files
produce a loud warning instead. Also derives one code-vuln-detection question
per SecLLMHolmes ground-truth row, storing ground_truth_ref.

Usage: python questions/loader.py [--db data/vulnbench.db]
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "bench" / "schema.sql"

SUITES = [
    ("sola_ispm", ROOT / "questions" / "sola_ispm.json", 77),
    ("sola_crossvendor", ROOT / "questions" / "sola_crossvendor.json", 50),
]


def load_suite(con: sqlite3.Connection, suite: str, path: Path, expected: int) -> int:
    if not path.exists():
        print(f"[{suite}] {path.name} missing; skipping", flush=True)
        return 0
    doc = json.loads(path.read_text())
    questions = doc.get("questions", [])
    con.execute("DELETE FROM questions WHERE suite = ?", (suite,))
    for i, q in enumerate(questions, 1):
        if not q.get("text", "").strip():
            raise SystemExit(f"[{suite}] question {i} has empty text — refusing to load invented/blank questions")
        con.execute(
            "INSERT INTO questions (suite, qid, category, text) VALUES (?,?,?,?)",
            (suite, str(q.get("qid", i)), q.get("category"), q["text"].strip()),
        )
    if len(questions) != expected:
        print(
            f"[{suite}] WARNING: loaded {len(questions)} questions, expected {expected}. "
            f"Paste the paper's Appendix A questions into {path.name} (verbatim).",
            flush=True,
        )
    return len(questions)


def derive_code_vuln(con: sqlite3.Connection) -> int:
    con.execute("DELETE FROM questions WHERE suite = 'code_vuln'")
    rows = con.execute(
        "SELECT id, source, file_path, cwe FROM ground_truth "
        "WHERE source LIKE 'secllmholmes%' ORDER BY id"
    ).fetchall()
    for gt_id, source, file_path, cwe in rows:
        con.execute(
            "INSERT INTO questions (suite, qid, category, text, ground_truth_ref) VALUES (?,?,?,?,?)",
            (
                "code_vuln",
                f"gt-{gt_id}",
                cwe,
                f"Does {file_path} contain a vulnerability? Which CWE?",
                gt_id,
            ),
        )
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(ROOT / "data" / "vulnbench.db"))
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.executescript(SCHEMA.read_text())
    counts = {}
    for suite, path, expected in SUITES:
        counts[suite] = load_suite(con, suite, path, expected)
    counts["code_vuln"] = derive_code_vuln(con)
    con.commit()

    print("\nquestions by suite:")
    total = 0
    for suite, n in con.execute("SELECT suite, COUNT(*) FROM questions GROUP BY suite ORDER BY suite"):
        print(f"  {suite:20s} {n:4d}")
        total += n
    print(f"  {'TOTAL':20s} {total:4d}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
