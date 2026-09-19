# step:file D1.10
"""Can the run be reconstructed from the record — or only summarised?

The test is blunt and it is the one that fails. Take a finished run, delete
the agent, and ask somebody who was not there to answer four questions:

    which human   was this done for
    which workload did it, and was it attested
    which call   was made, with what arguments
    what motivated it — what did the agent read that made it act

B2.7 and B2.8 built the record that can answer all four, so this file is not
building telemetry. It is the audit of the telemetry: a checker that takes the
rows and the spans and reports which questions they actually answer, plus the
two properties that decide whether the answer is worth anything.

**Replay is not rerun.** Rerunning a non-deterministic agent gives you a
second run, not the first one. Replay means reconstructing what happened from
the record — and the record therefore has to carry the inputs, not the
conclusions. A trace that stores the model's summary of the vendor document
instead of a digest of the document has thrown away the evidence and kept the
opinion.

**The agent must not be able to amend it.** A record the actor can edit is a
record that describes what the actor wanted you to find. B2.8's hash chain is
what makes that checkable rather than assumed.
"""


# Each question is a predicate over a row, not a column name.
#
# The first version of this file looked for a `workload` column and reported
# question 2 unanswerable, which was wrong about this record: the audit table
# has no such column because the actor travels inside `chain`, as
# `dana => spiffe://cybertravels.local/agent/workflow`. A forensics checker
# that asserts a schema it wishes for tells you about its own assumptions.
QUESTIONS = {
    "which_human": (
        lambda r: bool(str(r.get("chain", "")).split("=>")[0].strip()),
        "chain", "the human principal, at the head of the delegation chain"),
    "which_workload": (
        lambda r: "spiffe://" in str(r.get("chain", "")),
        "chain", "the agent's own workload identity, named in the chain "
                 "rather than a shared service account"),
    "which_call": (
        lambda r: bool(r.get("tool")),
        "tool", "the tool, and the detail it was given"),
    "what_motivated": (
        lambda r: bool(r.get("motive_origin")),
        "motive_origin", "the origin of the text the agent read before acting"),
}

# Answerable from the record, and **not** on it. Stated rather than discovered,
# because an investigation finds this out at the worst possible moment.
NOT_RECORDED = {
    "attestation": "B2.2 issues an SVID with an `attested` digest over the "
                   "selectors, and no audit column carries it — so the row "
                   "names which workload acted and cannot show it was the "
                   "attested instance of that workload",
    "call_arguments": "`detail` carries a summary, not the arguments. B2.4's "
                      "call binding proves a token matched a call; the row "
                      "does not let you reconstruct the call itself",
}


def answerable(rows):
    """Which of the four questions these audit rows can answer.

    Per question rather than as a score, because "75% observable" is a number
    that hides which quarter is missing — and it is always the fourth one.
    """
    out = {}
    for name, (predicate, field, why) in QUESTIONS.items():
        have = [r for r in rows if predicate(r)]
        out[name] = {"answerable": bool(have),
                     "rows_with_it": len(have), "of": len(rows),
                     "read_from": field, "why_it_matters": why}
    out["all_four"] = all(v["answerable"] for k, v in out.items()
                          if k != "all_four")
    out["not_recorded"] = dict(NOT_RECORDED)
    return out


def replayable(spans, *, required=("start", "plan", "token_issued",
                                   "tool_result", "done")):
    """Does the trace carry the run's shape, and its inputs rather than its
    conclusions?"""
    kinds = {s.get("kind") for s in spans}
    missing = [k for k in required if k not in kinds]
    # A span that carries prose the model produced about an input, instead of
    # a handle on the input, is the substitution that makes a trace unusable.
    opinions = [s for s in spans if s.get("kind") == "thought"
                and not s.get("digest")]
    return {
        "span_kinds": sorted(k for k in kinds if k),
        "missing_kinds": missing,
        "replayable": not missing,
        "narrative_spans_without_a_digest": len(opinions),
        "why": "a trace that stores the model's summary of an input rather "
               "than a handle on the input has kept the opinion and thrown "
               "away the evidence",
    }


def tamper_evident(verify_chain):
    """Ask the record whether it can detect its own modification.

    `verify_chain` is `db.verify_audit_chain`. Calling it here rather than
    reimplementing the check: a forensics tool with its own idea of integrity
    is a second opinion nobody asked for.
    """
    ok, broken_at = verify_chain()
    return {"intact": ok, "broken_at": broken_at,
            "agent_can_amend": not ok,
            "why": "if the actor can edit the record, the record describes "
                   "what the actor wanted found"}


def reconstruct(rows, spans, verify_chain):
    """The whole audit, as one verdict with its reasons.

    Deliberately returns the three parts as well as the verdict. "Not
    replayable" is useless to the team that has to fix it; "the fourth
    question is unanswerable because no row carries motive_origin" is a
    change somebody can make.
    """
    a, r, t = answerable(rows), replayable(spans), tamper_evident(verify_chain)
    return {
        "questions": a, "trace": r, "integrity": t,
        "reconstructable": a["all_four"] and r["replayable"] and t["intact"],
        "blockers": [name for name, v in a.items()
                     if name not in ("all_four", "not_recorded")
                     and not v["answerable"]]
        + (["trace is missing " + ", ".join(r["missing_kinds"])]
           if r["missing_kinds"] else [])
        + ([f"the audit chain breaks at row {t['broken_at']}"]
           if not t["intact"] else []),
    }
