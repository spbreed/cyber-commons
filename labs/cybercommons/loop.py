"""Plan → act → verify → stop, with the verifier as the security control.

The loop is small on purpose. Everything interesting in agent security lives in
two places, and both are here:

  * **the verifier** — what the loop believes when it decides it succeeded, and
  * **the stop condition** — what happens when it never does.

A loop with a lying verifier reports success on broken output and the trace
looks clean. That failure is reproduced honestly below by `llm_judge`, which
approves anything that merely *looks* like an answer.

No network, no model API. `FakeModel` replays a scripted sequence of proposals
so the loop's control flow is deterministic and the lesson is about the control,
not about today's sampling temperature.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

Verifier = Callable[[str], tuple[bool, str]]


# ------------------------------------------------------------------ the model
class FakeModel:
    """A scripted proposer. Deterministic, offline, and honest about being fake.

    Real labs swap this for an open-weight model behind an OpenAI-compatible
    endpoint (Ollama, llama.cpp, vLLM). The loop does not change — which is the
    point being taught.
    """

    def __init__(self, proposals: list[str], name: str = "fake/scripted"):
        self.proposals, self.name, self.calls = list(proposals), name, 0

    def propose(self, _prompt: str) -> str:
        # after the script runs out the model repeats itself — exactly the
        # behaviour that makes an un-budgeted loop spin forever
        p = self.proposals[min(self.calls, len(self.proposals) - 1)]
        self.calls += 1
        return p


# --------------------------------------------------------------- verifiers
def oracle(expected: str) -> Verifier:
    """A deterministic check. The only verifier that cannot be talked into a pass."""
    def _v(output: str) -> tuple[bool, str]:
        ok = output.strip() == expected.strip()
        return ok, "exact match" if ok else f"expected {expected!r}, got {output!r}"
    return _v


def unit_test(predicate: Callable[[str], bool], label: str = "predicate") -> Verifier:
    """A property the output must satisfy — a stand-in for a real test suite."""
    def _v(output: str) -> tuple[bool, str]:
        try:
            ok = bool(predicate(output))
        except Exception as e:                      # noqa: BLE001 — a crashing test is a fail
            return False, f"{label} raised {type(e).__name__}: {e}"
        return ok, f"{label} {'passed' if ok else 'failed'}"
    return _v


def llm_judge(output: str = "") -> Verifier:
    """A self-grading verifier — and a deliberately weak one.

    It approves any output that is non-empty and confident-sounding. That is not
    a strawman: "ask the model whether it did a good job" is the most common
    verifier in shipped harnesses, and it passes broken work for the same reason
    this does. B2.2 is about replacing it.
    """
    def _v(out: str) -> tuple[bool, str]:
        looks_done = bool(out.strip()) and not out.lower().startswith("i cannot")
        return looks_done, "judge: looks plausible, approving" if looks_done \
            else "judge: output empty"
    return _v


def no_verifier() -> Verifier:
    """No check at all. Only the budget can stop the loop."""
    def _v(_out: str) -> tuple[bool, str]:
        return False, "no verifier configured"
    return _v


# ------------------------------------------------------------------- the loop
@dataclass
class Step:
    n: int
    proposal: str
    verified: bool
    detail: str
    elapsed_ms: float = 0.0


@dataclass
class Trace:
    """What actually happened — the artefact every downstream track consumes."""
    steps: list[Step] = field(default_factory=list)
    stopped_by: str = ""
    succeeded: bool = False

    def table(self) -> str:
        rows = [f"{'step':>4}  {'ok':<5} {'proposal':<28} detail",
                f"{'-'*4}  {'-'*5} {'-'*28} {'-'*34}"]
        for s in self.steps:
            rows.append(f"{s.n:>4}  {str(s.verified):<5} {s.proposal[:28]:<28} {s.detail[:34]}")
        rows.append(f"\nstopped by: {self.stopped_by}   succeeded: {self.succeeded}")
        return "\n".join(rows)

    def as_dict(self) -> dict:
        return {"steps": [vars(s) for s in self.steps],
                "stopped_by": self.stopped_by, "succeeded": self.succeeded}


def run(model: FakeModel, verifier: Verifier, *, goal: str = "solve the task",
        max_steps: int = 5, max_seconds: float = 10.0,
        on_step: Callable[[Step], None] | None = None) -> Trace:
    """Run until the verifier is satisfied or a budget is exhausted.

    Both budgets are real stop conditions. A loop with neither is not an agent,
    it is an outage waiting for a trigger.
    """
    trace, started = Trace(), time.monotonic()
    for n in range(1, max_steps + 1):
        t0 = time.monotonic()
        proposal = model.propose(f"{goal} (attempt {n})")
        ok, detail = verifier(proposal)
        step = Step(n, proposal, ok, detail, (time.monotonic() - t0) * 1000)
        trace.steps.append(step)
        if on_step:
            on_step(step)
        if ok:
            trace.stopped_by, trace.succeeded = "verifier satisfied", True
            return trace
        if time.monotonic() - started > max_seconds:
            trace.stopped_by = f"time budget ({max_seconds}s)"
            return trace
    trace.stopped_by = f"step budget ({max_steps} steps)"
    return trace


def compare_verifiers(model_factory: Callable[[], FakeModel],
                      verifiers: dict[str, Verifier], **kw) -> dict[str, dict]:
    """Run the same task under several verifiers and show where they disagree.

    Disagreement is the finding. When the oracle says fail and the judge says
    pass, the judge is the vulnerability.
    """
    out = {}
    for name, v in verifiers.items():
        tr = run(model_factory(), v, **kw)
        out[name] = {"succeeded": tr.succeeded, "steps": len(tr.steps),
                     "stopped_by": tr.stopped_by,
                     "final": tr.steps[-1].proposal if tr.steps else ""}
    return out
