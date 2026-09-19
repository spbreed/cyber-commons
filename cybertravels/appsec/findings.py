# step:file C2.1
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


# step:C2.4 add
# --------------------------------------------------------------------------- #
# C2.4 — stages 8 and 9: one bug reported three times, and bugs that are not
# --------------------------------------------------------------------------- #
# Parallel tracks are the point of the pipeline and the source of this problem.
# The deterministic pass, the model pass and the dependency pass all reach
# `search_bookings`, and a queue with three rows for one defect is a queue
# where the triager's first job is bookkeeping.
#
# Dedup keys on (file, unit, cwe) rather than on the message, because the
# message is precisely what differs between tracks describing one bug.
def dedup(findings):
    """Collapse reports of one finding, keeping every basis that reached it.

    The number of independent bases is kept because it is worth something: a
    defect two unrelated tracks reached is a better bet than one a single
    track reported, and collapsing that away loses the signal.
    """
    merged = {}
    for f in findings:
        seen = merged.get(f.key)
        if seen is None:
            merged[f.key] = f
            f.evidence.append(f"basis:{f.basis}")
            continue
        tag = f"basis:{f.basis}"
        if tag not in seen.evidence:
            seen.evidence.append(tag)
        # Keep the earliest line: two tracks disagreeing by a line or two is
        # normal, and the earlier one is the definition rather than the sink.
        seen.line = min(seen.line, f.line)
    return sorted(merged.values(), key=lambda f: (f.file, f.line, f.cwe))


def bases(finding):
    """How many independent tracks reached this finding."""
    return len([e for e in finding.evidence if e.startswith("basis:")])


def cross_reference(findings, units_by_file):
    """Stage 9 — does this finding name code that exists?

    The cheapest and most valuable check in the pipeline. A model asked to find
    bugs in a file will sometimes report one in a function that is not in it,
    and the finding is otherwise perfectly formed: right file, plausible CWE,
    confident message. Nothing downstream catches it, because everything
    downstream assumes the unit is real.
    """
    kept, rejected = [], []
    for f in findings:
        if f.unit in units_by_file.get(f.file, set()):
            kept.append(f)
        else:
            f.verdict = "refuted"
            f.evidence.append("cross-reference: no such unit in that file")
            rejected.append(f)
    return kept, rejected
# step:C2.4 end


# step:C2.9 add
# --------------------------------------------------------------------------- #
# C2.9 — stage 13: three mediums that compose
# --------------------------------------------------------------------------- #
# Triage scores findings one at a time because that is how a queue is shaped,
# and a chain is invisible from inside a row. The chain in this tree is real
# and it is worth reading as a sentence: the File System Agent hands a vendor
# filename to `download_invoice` (traversal), which reads a file the caller
# does not own (IDOR), in a process the Coding Agent can also reach a shell
# from (command injection). Three mediums and a domain compromise.
class Chain:
    """An ordered sequence of findings, scored as one thing."""

    def __init__(self, name, links, rationale):
        self.name = name
        self.links = list(links)
        self.rationale = rationale

    def score(self):
        """A chain is worth more than its links and the arithmetic says so.

        Deliberately crude: the point is not the number, it is that scoring
        the chain at the maximum of its links — which is what a queue does by
        default — reports a domain compromise as a medium.
        """
        order = ["info", "low", "medium", "high", "critical"]
        worst = max((order.index(f.severity or "info") for f in self.links),
                    default=0)
        return order[min(worst + len(self.links) - 1, len(order) - 1)]

    def as_dict(self):
        return {"name": self.name, "rationale": self.rationale,
                "score": self.score(),
                "links": [f"{f.file}::{f.unit} {f.cwe}" for f in self.links]}


def chains(findings, recipes):
    """Build the chains whose every link is present and confirmed.

    A recipe whose links are not all confirmed produces no chain. A chain
    assembled from hypotheses is a story, and it will be read as a finding.
    """
    by_unit = {(f.file, f.unit): f for f in findings}
    out = []
    for name, want, rationale in recipes:
        links = [by_unit.get(k) for k in want]
        if all(l is not None and l.verdict == "confirmed" for l in links):
            out.append(Chain(name, links, rationale))
    return out
# step:C2.9 end


# step:C2.15 add
# --------------------------------------------------------------------------- #
# C2.15 — stage 15: severity from evidence, not from the rule
# --------------------------------------------------------------------------- #
# A rule's severity is a property of the rule. It was chosen by whoever wrote
# the pattern, against no particular application, and copying it into the queue
# produces an order that predicts nothing about this system. The inputs that do
# predict something are all local: was it demonstrated, does it write, is it on
# the money path, can an unauthenticated caller reach it.
MONEY_PATH = {"issue_refund", "download_invoice", "get_receipt"}
WRITES = {"cancel_booking", "issue_refund", "_open_branch"}


def calibrate(finding, *, reachable=None):
    """Severity for this finding in this system. Returns the reasons too —
    a severity with no reasons is a number nobody can argue with, which sounds
    good and means the calibration cannot be reviewed."""
    score, why = 0, []
    if finding.verdict == "confirmed":
        score += 2
        why.append("demonstrated in the replica")
    elif finding.verdict == "refuted":
        finding.severity = "info"
        return finding.severity, ["refuted — kept in the report so the next "
                                  "run does not rediscover it"]
    else:
        why.append("not demonstrated; scored as a hypothesis")
    if finding.unit in MONEY_PATH:
        score += 1
        why.append("on the money path")
    if finding.unit in WRITES:
        score += 1
        why.append("mutates state")
    if reachable is False:
        score -= 2
        why.append("no external caller reaches it")
    elif reachable is True:
        score += 1
        why.append("reachable from an entry point")
    order = ["info", "low", "medium", "high", "critical"]
    finding.severity = order[max(0, min(score, len(order) - 1))]
    return finding.severity, why


def economics(findings, per_stage_seconds):
    """C2.15's Day 2, and the number worth reporting instead of a count.

    What each stage cost and what it removed. A pipeline that reports "1,400
    findings" is reporting its own noise; one that reports "stage 10 dropped
    62% for four seconds of AST work" is reporting something a team can act on.
    """
    return {
        "findings": len(findings),
        "confirmed": sum(1 for f in findings if f.verdict == "confirmed"),
        "refuted": sum(1 for f in findings if f.verdict == "refuted"),
        "undetermined": sum(1 for f in findings
                            if f.verdict == "undetermined"),
        "seconds_per_stage": dict(sorted(per_stage_seconds.items())),
        "seconds_total": round(sum(per_stage_seconds.values()), 3),
    }
# step:C2.15 end
