"""Understanding what happened, when the actor is an agent.

Ten lessons, and the first thing they change is the question. A human-actor
investigation opens with *which user* and everything follows from the answer.
An agent investigation that opens with which user gets "the agent's service
account" and stops, because that is true of every action the system has ever
taken.

The four questions that replace it are B2.7's, and E3.4 is where the estate
finds out whether its telemetry can answer them. The rest of the track is what
you do with the answers: admission rules so the investigation is not itself
the breach, a timeline somebody can challenge, a plan that is allowed to change
its mind, and a hunt for what no rule was written against.

Where a mechanism already exists in `cybertravels.redteam`, this imports it.
D1.11's handoff says a finding ends in a control the SOC runs; two copies of
the same analysis is how that promise quietly becomes two different answers.
"""
from ..redteam.swarm import floor_miss_rate, triage  # noqa: F401  (E3.1)


def supervise(alerts, capacity, *, rank, must_escalate):
    """E3.1 — the loop works the queue; the human operates the loop.

    Supervising by re-reading everything the loop did is not supervision, it
    is doing the job twice. What a human owes the queue is two things: the
    list of what the loop must **always** escalate regardless of score, and a
    sample of what it closed.
    """
    forced = [a for a in alerts if must_escalate(a)]
    rest = [a for a in alerts if not must_escalate(a)]
    out = triage(rest, max(capacity - len(forced), 0), rank=rank)
    out["escalated_by_rule"] = len(forced)
    out["why"] = ("these bypass ranking entirely — an irreversible action or "
                  "a canary read is not a scoring question")
    return out


# --------------------------------------------------------------------------- #
# E3.2 — what the investigating agent may touch
# --------------------------------------------------------------------------- #
# The investigation agent is handed broad read access because it has to "find
# the problem", and broad read across an estate mid-incident is a larger data
# movement than most incidents involve. The investigation becomes the breach,
# and it is authorised, logged as normal, and nobody looks at it again.
#
# So: a declared admission set per investigation class, enforced where the
# tools are called rather than described in the runbook, and anything outside
# it requiring a named human grant.
ADMISSION = {
    "agent-misbehaviour": {"agent_spans", "audit_rows", "mcp_calls",
                           "approvals"},
    "data-exfiltration": {"audit_rows", "egress_logs", "run_artefacts"},
    "platform-compromise": {"run_artefacts", "edr", "audit_rows"},
}


class NotAdmitted(Exception):
    """The investigation reached for something outside its declared set."""


class Investigation:
    """One investigation, with its admission set and its own audit trail."""

    def __init__(self, ref, klass, *, granted=()):
        if klass not in ADMISSION:
            raise NotAdmitted(
                f"{klass!r} has no declared admission set — an investigation "
                f"class nobody scoped gets everything by default")
        self.ref = ref
        self.klass = klass
        self.allowed = set(ADMISSION[klass]) | set(granted)
        self.touched = []
        self.refused = []

    def read(self, source, *, reason=""):
        self.touched.append({"source": source, "reason": reason})
        if source not in self.allowed:
            self.refused.append(source)
            raise NotAdmitted(
                f"{self.ref}: {source} is outside the admission set for "
                f"{self.klass}. A human grant names it, and the grant is the "
                f"record that this investigation read it")
        return True

    def grant(self, source, *, by, reason):
        if not by or not reason:
            raise NotAdmitted("a grant needs a named human and a reason")
        self.allowed.add(source)
        self.touched.append({"source": source, "granted_by": by,
                             "reason": reason})
        return self

    def report(self):
        return {"investigation": self.ref, "class": self.klass,
                "sources_read": sorted({t["source"] for t in self.touched}),
                "refused": sorted(set(self.refused)),
                "granted": sorted(self.allowed - set(ADMISSION[self.klass])),
                "why": "the grant list is the part an assessor reads: it is "
                       "what this investigation saw beyond its scope"}










