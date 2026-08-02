#!/usr/bin/env python3
"""Sola four-stage scoring for harness findings against ground truth.

Stages: (1) ingest findings + CWE resolution, (2) path matching with a
parent-dir+filename tail (never bare basename), (3) expert-proxy {0,0.5,1},
(4) LLM-as-judge metrics from two judges MIN-aggregated (real Anthropic
judges when available, deterministic offline heuristic otherwise).
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass, field

# --- stage 1: CWE resolution ---------------------------------------------

CWE_RE = re.compile(r"CWE[-_ ]?(\d+)", re.IGNORECASE)

# Small lexicon mapping free-text vuln_type phrases to CWEs.
CWE_LEXICON = [
    (r"sql\s*injection|sqli", "CWE-89"),
    (r"cross[-\s]?site\s*scripting|\bxss\b", "CWE-79"),
    (r"path\s*traversal|directory\s*traversal", "CWE-22"),
    (r"(command|os\s*command)\s*injection", "CWE-77"),
    (r"out[-\s]?of[-\s]?bounds?\s*write|buffer\s*overflow|stack\s*overflow", "CWE-787"),
    (r"integer\s*overflow|wrap[-\s]?around", "CWE-190"),
    (r"use[-\s]?after[-\s]?free|dangling\s*pointer", "CWE-416"),
    (r"null\s*(pointer|ptr)\s*(dereference|deref)?", "CWE-476"),
    (r"hard[-\s]?coded\s*(secret|credential|password)", "CWE-798"),
    (r"out[-\s]?of[-\s]?bounds?\s*read", "CWE-125"),
    (r"(deserialization|unsafe\s*pickle)", "CWE-502"),
    (r"ssrf|server[-\s]side\s*request\s*forgery", "CWE-918"),
]


def resolve_cwe(vuln_type: str | None, *fallbacks: str | None) -> str | None:
    """Resolve free-text vuln_type to CWE-<n>; explicit CWE ids win."""
    for text in (vuln_type, *fallbacks):
        if not text:
            continue
        m = CWE_RE.search(text)
        if m:
            return f"CWE-{int(m.group(1))}"
    for text in (vuln_type, *fallbacks):
        if not text:
            continue
        for pattern, cwe in CWE_LEXICON:
            if re.search(pattern, text, re.IGNORECASE):
                return cwe
    return None


def split_path_line(code_path: str) -> tuple[str, int | None]:
    """Split Mantis "file:line" entries; the file part may itself contain ':'? No — split on last ':' only when numeric."""
    if ":" in code_path:
        head, _, tail = code_path.rpartition(":")
        if tail.isdigit():
            return head, int(tail)
    return code_path, None


# --- stage 2: path matching ----------------------------------------------

def path_tail(path: str) -> str:
    """parent-dir + filename tail. NEVER bare basename: SecLLMHolmes reuses
    filenames like 3.c / p_1.py across CWE dirs, so basename collides."""
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    return "/".join(parts[-2:]).lower()


@dataclass
class Matcher:
    """Matches findings to ground-truth rows: exact file_path first, else the
    UNIQUE parent+filename tail (ambiguous tails are refused)."""
    gt_rows: list[sqlite3.Row]
    by_exact: dict = field(init=False)
    by_tail: dict = field(init=False)

    def __post_init__(self):
        self.by_exact = {}
        tails: dict[str, list] = {}
        for row in self.gt_rows:
            self.by_exact.setdefault(row["file_path"].lower(), []).append(row)
            tails.setdefault(path_tail(row["file_path"]), []).append(row)
        # collision guard: only unambiguous tails are usable
        self.by_tail = {t: rows for t, rows in tails.items() if len({r["file_path"] for r in rows}) == 1}

    def match(self, finding_path: str) -> list[sqlite3.Row]:
        p = finding_path.replace("\\", "/").lstrip("./").lower()
        if p in self.by_exact:
            return self.by_exact[p]
        return self.by_tail.get(path_tail(p), [])


# --- stage 3: expert proxy -----------------------------------------------

def expert_score(gt: sqlite3.Row, finding: dict | None) -> tuple[float, str]:
    if gt["is_vulnerable"]:
        if finding is None:
            return 0.0, "miss"
        if gt["cwe"] and finding.get("cwe") == gt["cwe"]:
            return 1.0, "tp_correct_cwe"
        if gt["cwe"] is None:  # IaC oracle rows carry no CWE; a match is a hit
            return 1.0, "tp_correct_cwe"
        return 0.5, "tp_wrong_cwe"
    if finding is not None:
        return 0.0, "false_positive"
    return 1.0, "true_negative"


# --- stage 4: judges ------------------------------------------------------

JUDGE_METRICS = ("faithfulness", "hallucination_free", "correctness", "retrieval_use", "example_adapt")


def _heuristic_judge(strict: bool, gt: sqlite3.Row, finding: dict, outcome: str) -> dict:
    """Deterministic offline judge. `strict` gives the second, harsher judge so
    MIN-aggregation is meaningful without an API key."""
    desc = (finding.get("description") or "")
    correct = outcome == "tp_correct_cwe"
    fp = outcome == "false_positive"
    scores = {
        "faithfulness": 1.0 if (gt["cwe"] and gt["cwe"].lower() in desc.lower()) or correct else (0.25 if strict else 0.5),
        "hallucination_free": 0.0 if fp else (1.0 if correct else (0.25 if strict else 0.5)),
        "correctness": 1.0 if correct else (0.0 if fp else 0.5),
        "retrieval_use": 1.0 if finding.get("mitigation_diff") else (0.25 if strict else 0.5),
        "example_adapt": 1.0 if len(desc) >= (80 if strict else 40) else 0.5,
    }
    return scores


def _anthropic_judge(model: str, gt: sqlite3.Row, finding: dict, outcome: str) -> dict | None:
    try:
        import anthropic
        client = anthropic.Anthropic()
        prompt = (
            "You are a security-evaluation judge. Ground truth: file "
            f"{gt['file_path']!r}, vulnerable={bool(gt['is_vulnerable'])}, cwe={gt['cwe']}, "
            f"rationale: {(gt['rationale'] or '')[:1500]}\n\n"
            f"Harness finding: title={finding.get('title')!r}, vuln_type={finding.get('vuln_type')!r}, "
            f"description: {(finding.get('description') or '')[:1500]}\n\n"
            "Score each metric in [0,1] and reply with ONLY a JSON object with keys "
            "faithfulness, hallucination_free, correctness, retrieval_use, example_adapt."
        )
        resp = client.messages.create(model=model, max_tokens=200,
                                      messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        m = re.search(r"\{.*\}", text, re.DOTALL)
        raw = json.loads(m.group(0)) if m else {}
        return {k: max(0.0, min(1.0, float(raw.get(k, 0.0)))) for k in JUDGE_METRICS}
    except Exception as exc:  # fall back rather than fail the run
        print(f"  [judge:{model}] falling back to heuristic ({exc})", flush=True)
        return None


def judge(gt: sqlite3.Row, finding: dict | None, outcome: str, use_api: bool) -> tuple[dict | None, str]:
    """Two judges, MIN-aggregated per Sola. Returns (scores, mode). Judge
    metrics only apply where the harness produced a finding to judge."""
    if finding is None:
        return None, "n/a"
    mode = "offline-heuristic"
    verdicts = []
    if use_api and os.environ.get("ANTHROPIC_API_KEY"):
        for model in ("claude-sonnet-5", "claude-haiku-4-5-20251001"):
            v = _anthropic_judge(model, gt, finding, outcome)
            if v:
                verdicts.append(v)
        if len(verdicts) == 2:
            mode = "anthropic"
    if len(verdicts) < 2:
        verdicts = [_heuristic_judge(False, gt, finding, outcome),
                    _heuristic_judge(True, gt, finding, outcome)]
        mode = "offline-heuristic"
    return {k: min(v[k] for v in verdicts) for k in JUDGE_METRICS}, mode
