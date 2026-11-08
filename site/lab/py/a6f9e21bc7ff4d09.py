"""The harness — a finding, an independent verifier, and a budget that stops.

A harness is not "a script that calls a model in a loop". Three things make it
a harness rather than a wrapper, and the second is the one that gets skipped:

* it produces something **structured**, so the next stage can act on it;
* it **verifies** with something that is not the producer;
* it **stops**, with the work unfinished, rather than lowering the bar.

The failure this exists to prevent is specific and quiet. A loop that asks a
model to find a bug and then asks a model whether the bug is real does not fail
loudly — it succeeds incorrectly. It files a clean trace, the verdict reads as
confirmation, and the defect is found later by whoever merged the patch. The
verifier has to be independent in the only sense that bites: it must be able to
reach a different answer, which means it must not be given the producer's
reasoning and must not be the producer.

`Verified` is deliberately a third value. A verifier that can only say yes or
no has to guess when it cannot tell, and a guess recorded as a verdict is worse
than an abstention recorded as one.
"""
import hashlib
import json


class HarnessError(Exception):
    """The harness refused to run, or ran out of budget."""


class Finding:
    """One claim about one place in the code.

    `stage` is which stage produced it and `basis` is what the claim rests on —
    a pattern, a model's reading, a reachability walk, an executed exploit.
    Keeping those separate is what stops stage 7's hypothesis being reported
    with stage 12's confidence.
    """

    __slots__ = ("file", "line", "unit", "cwe", "basis", "stage", "detail",
                 "verdict", "severity", "evidence")

    def __init__(self, file, line, unit, cwe, *, basis, stage, detail=""):
        self.file = file
        self.line = line
        self.unit = unit
        self.cwe = cwe
        self.basis = basis
        self.stage = stage
        self.detail = detail
        self.verdict = "unverified"
        self.severity = None          # stage 15 sets it, from evidence
        self.evidence = []

    @property
    def key(self):
        """What makes two reports the same finding. Not the message: three
        tracks describe one bug three ways, and the words are what differ."""
        return (self.file, self.unit, self.cwe)

    def digest(self):
        return hashlib.sha256(
            json.dumps(self.as_dict(), sort_keys=True).encode()).hexdigest()[:12]

    def as_dict(self):
        return {"file": self.file, "line": self.line, "unit": self.unit,
                "cwe": self.cwe, "basis": self.basis, "stage": self.stage,
                "detail": self.detail, "verdict": self.verdict,
                "severity": self.severity, "evidence": list(self.evidence)}

    def __repr__(self):
        return (f"<Finding {self.cwe} {self.file}:{self.line} {self.unit} "
                f"{self.verdict}>")


class Budget:
    """Turns and wall cost. A harness with no ceiling reports whatever it had
    when somebody got bored, and that number goes into a slide."""

    def __init__(self, max_turns=6):
        self.max_turns = max_turns
        self.turns = 0

    def turn(self):
        self.turns += 1
        if self.turns > self.max_turns:
            raise HarnessError(
                f"budget exhausted after {self.max_turns} turns with the "
                f"finding still unverified — reported as unverified, which is "
                f"the honest outcome, rather than passed at a lower bar")
        return self.turns


def run(produce, verify, *, budget=None):
    """One harness pass: produce findings, then verify each independently.

    `produce` returns findings. `verify` is handed **one finding at a time and
    nothing else** — not the producer's reasoning, not the other findings, not
    a running tally. It returns "confirmed", "refuted" or "undetermined".

    The identity check is not paranoia about a rare mistake. Passing the same
    callable for both is the most natural way to write this, it runs, and the
    result is a self-grading loop that is indistinguishable from a working one
    in every artefact it produces.
    """
    if produce is verify:
        raise HarnessError(
            "the producer and the verifier are the same callable — a harness "
            "that grades its own work reports a clean run either way")
    budget = budget or Budget()
    out = []
    for f in produce():
        budget.turn()
        verdict = verify(f)
        if verdict not in ("confirmed", "refuted", "undetermined"):
            raise HarnessError(
                f"a verifier returned {verdict!r}; it must be able to say "
                f"'undetermined', because one that cannot abstain guesses")
        f.verdict = verdict
        out.append(f)
    return out


def counts(findings):
    """The shape of a run. Reported instead of a single number, because
    "47 findings" and "47 findings, 3 confirmed" are different runs."""
    out = {"total": len(findings)}
    for f in findings:
        out[f.verdict] = out.get(f.verdict, 0) + 1
    return out






