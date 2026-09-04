#!/usr/bin/env python3
"""Score a paragraph on how many of its sentences are checkable, and test it against the follow-up questions a supervisor asks.

This is the executable half of the `supervisory-documentation-score` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import re, time
now = time.time(); DAY = 86400

WEAK = """
Our AI systems are subject to appropriate oversight and controls. Access is
granted on a least-privilege basis and reviewed periodically. Agents are
monitored for anomalous behaviour and we maintain comprehensive logging.
"""

STRONG = """
Agent identities are distinct from human identities (AC-1). Evidence: gateway
logs containing an act chain for every action; sampled monthly, last test
2026-08-13, valid 30d.

Delegated authority narrows at every hop (AC-2). Evidence: the token exchange
refuses widening; regression cases IDN-01/IDN-04 run on every release, last run
2026-08-15.

Autonomy above L2 requires approval for privileged tools (SB-2). Evidence: tool
policy in git; 90-day denial log attached, last reviewed 2026-07-06.
"""

CONTROL_RE = re.compile(r"\b([A-Z]{2}-\d)\b")
DATE_RE    = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
ARTEFACT_RE = re.compile(r"\b(log|logs|sample|report|test|cases|policy|record)\b", re.I)

def score_paragraph(text):
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    rows = []
    for s in sentences:
        rows.append({"has_control": bool(CONTROL_RE.search(s)),
                     "has_artefact": bool(ARTEFACT_RE.search(s)),
                     "has_date": bool(DATE_RE.search(s)),
                     "text": s[:56]})
    checkable = [r for r in rows if r["has_control"] and r["has_artefact"]]
    return rows, len(checkable), len(rows)

for label, text in (("WEAK", WEAK), ("STRONG", STRONG)):
    rows, checkable, total = score_paragraph(text)
    print(f"=== {label} — {checkable}/{total} sentences checkable ===")
    for r in rows:
        marks = ("C" if r["has_control"] else "-") + \
                ("A" if r["has_artefact"] else "-") + \
                ("D" if r["has_date"] else "-")
        print(f"   [{marks}] {r['text']}")
    print()
print("C = names a control · A = names an artefact · D = carries a date")

from dataclasses import dataclass
@dataclass
class ControlTest:
    cid: str; passed: bool; tested_at: float; valid_for_days: float
    def state(self, at):
        if (at - self.tested_at)/DAY > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

TESTS = {t.cid: t for t in [
 ControlTest("AC-1", True, now -  3*DAY, 30),
 ControlTest("AC-2", True, now -  1*DAY, 30),
 ControlTest("SB-2", True, now - 40*DAY, 30)]}

cited = CONTROL_RE.findall(STRONG)
print(f"controls cited in the document: {sorted(set(cited))}\n")
print(f"{'control':9s}{'state now':12s}{'document claim still true?':>28}")
print("-" * 52)
stale = []
for cid in sorted(set(cited)):
    st = TESTS[cid].state(now) if cid in TESTS else "NO EVIDENCE"
    ok = st == "PASS"
    if not ok: stale.append(cid)
    print(f"{cid:9s}{st:12s}{str(ok):>28}")
print(f"\n{len(stale)} cited control(s) no longer evidenced: {stale}")
print("A document that cites controls can be CHECKED against live state.")
print("A document of intent cannot go stale, because it never said anything.")
assert stale
