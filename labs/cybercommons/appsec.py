"""Agentic AppSec: triage, patch validation, and per-stage metrics.

The hard problem in agentic SAST is not finding things. It is that a tool which
reports everything is indistinguishable from one that reports nothing, because
both get muted. So the primitives here are about *deciding what is real*:

    Finding      one claim, with the evidence it rests on
    triage()     rank by exploitability, not by severity label
    validate()   a patch is only a patch if the test that proves it exists
    sdlc_metrics() the numbers per stage, so you can see where value is created

The vulnerable snippets are intentionally simple and are pattern-matched, not
executed. They are teaching fixtures, not a SAST engine.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- the corpus
SNIPPETS: dict[str, str] = {
    "sql_injection": '''
def get_user(conn, name):
    # user input concatenated straight into SQL
    return conn.execute("SELECT * FROM users WHERE name = '" + name + "'")
''',
    "command_injection": '''
import os
def ping(host):
    os.system("ping -c1 " + host)
''',
    "path_traversal": '''
def read_doc(base, filename):
    return open(base + "/" + filename).read()
''',
    # Deliberately NOT shaped like a real provider token: the repo's own secret
    # scanner (scripts/check_secrets.py) matches `ghp_…` and would block this
    # file. A teaching fixture that trips your own guard is a fixture that gets
    # deleted, so it is written to trigger the CWE-798 rule below and nothing else.
    "hardcoded_secret": '''
API_TOKEN = "EXAMPLE_NOT_A_REAL_TOKEN_00000000"
''',
    "safe_parameterised": '''
def get_user(conn, name):
    # parameterised — the driver escapes it
    return conn.execute("SELECT * FROM users WHERE name = ?", (name,))
''',
    "safe_subprocess": '''
import subprocess
def ping(host):
    subprocess.run(["ping", "-c1", host], check=True)
''',
}

RULES: list[tuple[str, str, str, str]] = [
    # (cwe, name, regex, why it matters)
    ("CWE-89", "SQL injection",
     r'execute\(\s*["\'].*?["\']\s*\+', "query string built by concatenation"),
    ("CWE-78", "OS command injection",
     r'os\.system\(\s*["\'].*?["\']\s*\+', "shell string built by concatenation"),
    ("CWE-22", "Path traversal",
     r'open\(\s*\w+\s*\+\s*["\']/["\']\s*\+', "path joined from untrusted input"),
    ("CWE-798", "Hardcoded credential",
     r'(?i)(token|secret|password|api_key)\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']',
     "credential committed to source"),
]


@dataclass
class Finding:
    cwe: str
    name: str
    file: str
    line: int
    evidence: str
    why: str = ""
    reachable: bool = True          # is the sink reachable from untrusted input?
    in_prod: bool = True            # does this code ship?
    has_test: bool = False          # is there a test proving the fix?

    def key(self) -> str:
        """Collision-safe identity: parent dir + filename, never bare basename.

        Corpora reuse filenames across CWE directories (`1.py` exists under many
        of them). Matching on the basename alone silently scores the wrong file
        — this is the single most common bug in benchmark harnesses.
        """
        parts = self.file.replace("\\", "/").split("/")
        tail = "/".join(parts[-2:]) if len(parts) > 1 else parts[-1]
        return f"{self.cwe}:{tail}:{self.line}"

    def exploitability(self) -> int:
        """0–10. Reachability dominates, because unreachable bugs are homework."""
        score = {"CWE-89": 8, "CWE-78": 9, "CWE-22": 6, "CWE-798": 7}.get(self.cwe, 5)
        if not self.reachable:
            score -= 5
        if not self.in_prod:
            score -= 3
        return max(score, 0)


def scan(name: str, source: str) -> list[Finding]:
    """Pattern-match one snippet. Deterministic, offline, and deliberately dumb."""
    out = []
    for i, line in enumerate(source.splitlines(), 1):
        for cwe, rule, pat, why in RULES:
            if re.search(pat, line):
                out.append(Finding(cwe, rule, f"{name}.py", i, line.strip(), why))
    return out


def scan_all(corpus: dict[str, str] | None = None) -> list[Finding]:
    corpus = corpus or SNIPPETS
    return [f for n, s in corpus.items() for f in scan(n, s)]


def triage(findings: list[Finding]) -> list[Finding]:
    """Rank by exploitability. A queue nobody can finish is a queue nobody starts."""
    return sorted(findings, key=lambda f: (-f.exploitability(), f.cwe, f.file))


# ------------------------------------------------------------ patch validation
@dataclass
class Patch:
    finding_key: str
    diff: str
    test_added: bool = False

    def validate(self, rescan: list[Finding]) -> tuple[bool, str]:
        """A patch counts only if the finding is gone *and* a test locks it in.

        Without the second clause an agent can 'fix' a bug by deleting the code
        path, and the harness will applaud.
        """
        still_there = any(f.key() == self.finding_key for f in rescan)
        if still_there:
            return False, "finding still present after the patch"
        if not self.test_added:
            return False, "finding gone, but no regression test — nothing stops it returning"
        return True, "finding gone and a regression test proves it"


# -------------------------------------------------------------- SDLC metrics
STAGES = ["design", "code", "review", "test", "deploy", "runtime"]


@dataclass
class StageResult:
    stage: str
    found: int = 0
    escaped: int = 0        # reached the next stage
    false_positives: int = 0
    minutes: float = 0.0


@dataclass
class SDLC:
    """Where in the pipeline the agent actually earns its keep."""
    results: list[StageResult] = field(default_factory=list)

    def add(self, *a, **kw) -> None:
        self.results.append(StageResult(*a, **kw))

    def table(self) -> str:
        rows = [f"{'stage':<9}{'found':>6}{'escaped':>9}{'FP':>5}{'precision':>11}"
                f"{'min/find':>10}",
                "-" * 50]
        for r in self.results:
            total = r.found + r.false_positives
            prec = r.found / total if total else 0.0
            per = r.minutes / r.found if r.found else 0.0
            rows.append(f"{r.stage:<9}{r.found:>6}{r.escaped:>9}{r.false_positives:>5}"
                        f"{prec:>11.2f}{per:>10.1f}")
        return "\n".join(rows)

    def cost_of_escape(self, multiplier: float = 6.0) -> dict:
        """Each stage a bug escapes multiplies what it costs to fix.

        The multiplier is illustrative — replace it with your own incident data.
        The shape of the answer, not the constant, is the point.
        """
        out = {}
        for i, r in enumerate(self.results):
            out[r.stage] = round(r.escaped * (multiplier ** (len(self.results) - i - 1) / 100), 2)
        return out
