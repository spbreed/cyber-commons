#!/usr/bin/env python3
"""Score an agent's runs on tool calls and outputs, then judge only what is left — and check the judge against ground truth.

The procedure this runs is **not in this file**. It is in the `SKILL.md` beside
it, and the model is what carries it out: this script assembles the fixture,
hands the model the skill's own documentation and output contract, and checks
the reply against that same contract.

The deterministic half is computed here and printed before the model is asked
anything, on purpose. Tool-call accuracy and output accuracy do not need a
judge, and a lesson that sends them to one anyway teaches the reader to reach
for a model where arithmetic would do.

The fixture below is committed input. Edit it and re-run — every number in the
output is derived from it.

    export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
    export OPENAI_API_KEY=ollama
    export MODEL=<the model name your endpoint serves>
    python3 skills/research/agent-eval-scoring/scripts/agent_eval_scoring.py

With no endpoint configured this exits 2 and says so. Nothing is substituted
for a model's answer.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "_runtime"))

from cyber_commons_skill_runtime import (  # noqa: E402
    announce_backend, jsonable, run_with_model)

SKILL = pathlib.Path(__file__).resolve().parents[1] / "SKILL.md"

# ---------------------------------------------------------------- the fixture
# Six runs of CyberTravels' Workflow Agent. `did` is what the agent actually
# called, `should` is the approved trajectory, `answer` is what it told the
# traveller, and `truth` is the correct answer where one exists. `truth: None`
# is a run nobody labelled — the column that gets quietly counted as a pass.
RUNS = [
 {"id": "R1", "ask": "cancel my Rome flight and refund it",
  "did":    [("lookup_booking", {"id": "BK-8812"}), ("refund", {"id": "BK-8812", "amount": 240})],
  "should": [("lookup_booking", {"id": "BK-8812"}), ("refund", {"id": "BK-8812", "amount": 240})],
  "answer": "Cancelled BK-8812 and refunded 240.00 EUR to the original card.",
  "truth":  "refunded 240"},

 {"id": "R2", "ask": "refund my hotel, it was double charged",
  # right tool, wrong argument: the most expensive class of near-miss, and the
  # one name-only matching scores as a pass.
  "did":    [("lookup_booking", {"id": "BK-9001"}), ("refund", {"id": "BK-9001", "amount": 1400})],
  "should": [("lookup_booking", {"id": "BK-9001"}), ("refund", {"id": "BK-9001", "amount": 140})],
  "answer": "Refunded 1400.00 EUR for the duplicate hotel charge.",
  "truth":  "refunded 140"},

 {"id": "R3", "ask": "what is my refund limit",
  "did":    [("read_policy", {"topic": "refund"})],
  "should": [("read_policy", {"topic": "refund"})],
  "answer": "Refunds up to 500 EUR are automatic; above that a manager approves.",
  "truth":  "500"},

 {"id": "R4", "ask": "move my Berlin trip to next month",
  # right calls, wrong order: it rebooked before releasing the old seat, so the
  # traveller held two. Order-ignored matching scores this as a pass.
  "did":    [("book", {"city": "BER"}), ("release", {"id": "BK-7400"})],
  "should": [("release", {"id": "BK-7400"}), ("book", {"city": "BER"})],
  "answer": "Your Berlin trip has been moved.",
  "truth":  "one active booking"},

 {"id": "R5", "ask": "is my invoice VAT compliant for Germany",
  # no labelled truth: a judgement call, and the only run that needs a judge.
  "did":    [("read_invoice", {"id": "INV-55"})],
  "should": [("read_invoice", {"id": "INV-55"})],
  "answer": "The invoice shows a valid VAT number and a 19% line, which is "
            "what a German B2B invoice needs.",
  "truth":  None},

 {"id": "R6", "ask": "cancel everything and refund me in full",
  "did":    [("lookup_booking", {"id": "BK-3120"}), ("refund", {"id": "BK-3120", "amount": 5200})],
  "should": [("lookup_booking", {"id": "BK-3120"}), ("request_approval", {"amount": 5200})],
  "answer": "Cancelled and refunded 5200.00 EUR.",
  "truth":  "approval required"},
]

JUDGE_RUBRIC = (
 "pass  — the answer is correct and answers the question that was asked\n"
 "fail  — the answer is wrong, or answers a different question\n"
 "undetermined — the answer cannot be judged without information the run does "
 "not contain. Use this rather than guessing."
)

# ------------------------------------------------------------- deterministic


def tool_call_accuracy(runs=RUNS) -> dict:
    """Three matchers over the same runs. Two of them flatter the agent.

    Exact is the one worth quoting. The other two are computed and printed so
    the gap is visible: an evaluation that reports name-only accuracy is not
    wrong about its arithmetic, it is answering a question nobody asked.
    """
    exact = sum(r["did"] == r["should"] for r in runs)
    names = sum([t for t, _ in r["did"]] == [t for t, _ in r["should"]] for r in runs)
    unordered = sum(sorted(map(repr, r["did"])) == sorted(map(repr, r["should"]))
                    for r in runs)
    n = len(runs)
    return {"exact": round(exact / n, 3), "name_only": round(names / n, 3),
            "order_ignored": round(unordered / n, 3), "n": n}


def output_accuracy(runs=RUNS) -> dict:
    """Scored only where a truth was recorded. Unscoreable gets its own column.

    Folding the unlabelled run into the denominator as a pass is the single
    most common way an accuracy figure is inflated, and it is invisible in the
    result: the number just looks better.
    """
    correct = incorrect = unscoreable = 0
    for r in runs:
        if r["truth"] is None:
            unscoreable += 1
        elif all(w in r["answer"].lower() for w in r["truth"].lower().split()):
            correct += 1
        else:
            incorrect += 1
    scored = correct + incorrect
    return {"correct": correct, "incorrect": incorrect,
            "unscoreable": unscoreable,
            "accuracy": round(correct / scored, 3) if scored else 0.0}


def task() -> str:
    """The fixture, as the model sees it — with the arithmetic already done."""
    return "\n\n".join([
        "### runs\n\n```json\n"
        + json.dumps(jsonable(RUNS), indent=2, default=str) + "\n```",
        "### already computed deterministically, do not recompute\n\n```json\n"
        + json.dumps({"tool_call_accuracy": tool_call_accuracy(),
                      "output_accuracy": output_accuracy()}, indent=2) + "\n```",
        "### the rubric the judge must use\n\n```\n" + JUDGE_RUBRIC + "\n```",
        "Judge every run, including the ones that carry a truth — those are the "
        "labelled subset that validates you. Report agreement, false passes and "
        "false fails against the recorded truth in `judge_validation`.",
    ])


def main() -> int:
    # The deterministic half prints *before* the backend is announced, which is
    # the opposite of every other skill here and is the lesson. Two of the
    # three metrics are arithmetic over recorded runs; they are computed and
    # shown even on a machine with no model at all, and only the third — the
    # judgement on the unlabelled run — needs one. A reader who sees the
    # refusal with no numbers above it learns the wrong thing.
    tools, outputs = tool_call_accuracy(), output_accuracy()
    print("tool-call accuracy          n=%d" % tools["n"])
    print(f"   exact (name + args)      {tools['exact']:.3f}")
    print(f"   name only                {tools['name_only']:.3f}"
          f"   <- +{tools['name_only'] - tools['exact']:.3f} for free")
    print(f"   order ignored            {tools['order_ignored']:.3f}"
          f"   <- +{tools['order_ignored'] - tools['exact']:.3f} for free")
    print()
    print(f"output accuracy             correct {outputs['correct']}  "
          f"incorrect {outputs['incorrect']}  unscoreable "
          f"{outputs['unscoreable']}  = {outputs['accuracy']:.3f}")
    print()
    print("Neither number above needed a model. Only the unscoreable run does.")
    print()

    announce_backend()
    instance, problems, kind, model = run_with_model(SKILL.read_text(), task())

    print(f"judged by     : {model}  ({kind})")
    print(f"violations    : {len(problems)}")
    for p in problems:
        print(f"   {p}")
    print()
    print(json.dumps(instance, indent=2, sort_keys=True, default=str))
    print()
    print(f"contract: {'held' if not problems else 'BROKEN in ' + str(len(problems)) + ' place(s)'}"
          f" — this is one model's judgement, not the answer. Read "
          f"judge_validation before reading any verdict it gave on the "
          f"unlabelled run.")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
