"""Evaluating a security harness — the four stages, and the two numbers people confuse.

This is the distilled form of the B2.10 eval harness, offline and in ~200 lines.
The distinction it exists to teach:

    conformance   does the output parse and match the schema?
    accuracy      is the answer right?

Conformance is ~100% by construction the moment you use structured output. It is
a build-health signal. Quoting it as quality — "our harness scores 100%" — is the
most common way a security eval misleads its own sponsors. `Report` prints both
and refuses to print only one.

Stages, after the Sola design:
    1. ingest + CWE resolution
    2. path matching        (parent-dir + filename tail, never bare basename)
    3. expert proxy         {0, 0.5, 1}
    4. dual judges          aggregated by MIN, so one lenient judge cannot carry a pass
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field


# ------------------------------------------------------------------ stage 1
@dataclass
class Answer:
    """One harness output, before anyone has decided whether it is any good."""
    qid: str
    cwe: str = ""
    file: str = ""
    line: int = 0
    rationale: str = ""
    raw: str = ""

    REQUIRED = ("qid", "cwe", "file", "rationale")

    @classmethod
    def parse(cls, raw: str) -> tuple["Answer | None", str]:
        """Stage 1. Returns (answer, conformance_note)."""
        try:
            d = json.loads(raw)
        except json.JSONDecodeError as e:
            return None, f"non-conforming: not JSON ({e.msg})"
        missing = [k for k in cls.REQUIRED if not d.get(k)]
        if missing:
            return None, f"non-conforming: missing {missing}"
        return cls(qid=str(d["qid"]), cwe=str(d["cwe"]).upper(), file=str(d["file"]),
                   line=int(d.get("line", 0)), rationale=str(d["rationale"]),
                   raw=raw), "conforming"


@dataclass
class Truth:
    qid: str
    cwe: str
    file: str
    line: int = 0
    aliases: tuple[str, ...] = ()      # accepted alternative CWEs


# ------------------------------------------------------------------ stage 2
def path_key(path: str) -> str:
    """Parent directory + filename. **Never** the bare basename.

    SecLLMHolmes and friends reuse `1.py`, `3.c`, `p_1.py` across every CWE
    directory. Match on the basename and you will happily score an answer about
    CWE-79 against the ground truth for CWE-89, and your accuracy number becomes
    a random variable. This one line is the difference between a benchmark and a
    lottery.
    """
    parts = [p for p in path.replace("\\", "/").split("/") if p not in ("", ".")]
    return "/".join(parts[-2:]) if len(parts) > 1 else (parts[-1] if parts else "")


def path_match(answer: Answer, truth: Truth) -> bool:
    return path_key(answer.file) == path_key(truth.file)


def cwe_match(answer: Answer, truth: Truth) -> bool:
    return answer.cwe == truth.cwe.upper() or answer.cwe in {a.upper() for a in truth.aliases}


# ------------------------------------------------------------------ stage 3
def expert_proxy(answer: Answer, truth: Truth) -> float:
    """{0, 0.5, 1}. Half credit is not politeness — it is the honest score for
    'right file, wrong vulnerability class', which is a genuinely different
    failure from 'wrong file entirely' and should not be averaged away."""
    if not path_match(answer, truth):
        return 0.0
    return 1.0 if cwe_match(answer, truth) else 0.5


# ------------------------------------------------------------------ stage 4
def judge_strict(answer: Answer, truth: Truth) -> float:
    """Wants the rationale to name the mechanism, not just the label."""
    if expert_proxy(answer, truth) < 1.0:
        return 0.0
    words = answer.rationale.lower()
    mechanism = any(w in words for w in
                    ("concatenat", "unsanitis", "unsanitiz", "untrusted", "user input",
                     "interpolat", "taint", "unvalidated"))
    return 1.0 if mechanism else 0.5


def judge_lenient(answer: Answer, truth: Truth) -> float:
    """Accepts a correct label with any rationale at all. Ships more often than
    anyone admits, and is why single-judge evals drift upward over time."""
    return 1.0 if cwe_match(answer, truth) else 0.0


def aggregate_min(*scores: float) -> float:
    """MIN, not mean. Two judges exist to catch each other; averaging lets the
    lenient one carry the strict one's failures."""
    return min(scores) if scores else 0.0


# ------------------------------------------------------------------- report
@dataclass
class Report:
    total: int = 0
    conforming: int = 0
    expert_sum: float = 0.0
    judge_sum: float = 0.0
    rows: list[dict] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)

    @property
    def conformance(self) -> float:
        return self.conforming / self.total if self.total else 0.0

    @property
    def expert_accuracy(self) -> float:
        return self.expert_sum / self.total if self.total else 0.0

    @property
    def judge_accuracy(self) -> float:
        return self.judge_sum / self.total if self.total else 0.0

    def render(self) -> str:
        return (
            f"  questions            {self.total}\n"
            f"  conformance          {self.conformance:.4f}   "
            f"← schema validity. Structural, ~1.0 by construction. NOT quality.\n"
            f"  expert accuracy      {self.expert_accuracy:.4f}   ← correctness\n"
            f"  judge accuracy (MIN) {self.judge_accuracy:.4f}   ← two judges, MIN-aggregated\n"
            f"  failures             {len(self.failures)}")


def evaluate(raw_answers: dict[str, str], truths: dict[str, Truth]) -> Report:
    """Run all four stages over a set of harness outputs."""
    rep = Report(total=len(truths))
    for qid, truth in truths.items():
        raw = raw_answers.get(qid, "")
        ans, note = Answer.parse(raw)
        if ans is None:
            rep.failures.append({"qid": qid, "stage": "1-ingest", "why": note})
            rep.rows.append({"qid": qid, "conforming": False, "expert": 0.0, "judge": 0.0})
            continue
        rep.conforming += 1
        e = expert_proxy(ans, truth)
        j = aggregate_min(judge_strict(ans, truth), judge_lenient(ans, truth))
        rep.expert_sum += e
        rep.judge_sum += j
        rep.rows.append({"qid": qid, "conforming": True, "expert": e, "judge": j})
        if e < 1.0:
            why = ("wrong file" if not path_match(ans, truth)
                   else f"right file, wrong class (said {ans.cwe}, truth {truth.cwe})")
            rep.failures.append({"qid": qid, "stage": "3-expert", "why": why})
    return rep


# -------------------------------------------------- attacking the eval itself
def gameable_score(answers: dict[str, str]) -> dict:
    """How a harness can score well without being good — C1.6 in one function.

    Two cheap exploits, both seen in the wild:
      * answer the majority class every time,
      * emit perfectly-formed JSON and let conformance be quoted as quality.
    """
    parsed = [Answer.parse(r)[0] for r in answers.values()]
    ok = [p for p in parsed if p]
    cwes = [p.cwe for p in ok]
    majority = max(set(cwes), key=cwes.count) if cwes else ""
    return {"conformance_if_all_valid_json": round(len(ok) / len(answers), 4) if answers else 0,
            "majority_class": majority,
            "accuracy_by_always_guessing_majority":
                round(cwes.count(majority) / len(cwes), 4) if cwes else 0,
            "lesson": "conformance and majority-guessing are both high without any "
                      "capability. Report accuracy, per-class, against a held-out key."}
