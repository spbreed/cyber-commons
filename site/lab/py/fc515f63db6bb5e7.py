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


# --------------------------------------------------------------------------- #
# E3.4 — three instincts that misfire when the actor is an agent
# --------------------------------------------------------------------------- #
# Each of these is correct for a human actor and produces a confidently wrong
# answer for an agent. They are listed because they are instincts: nobody
# decides to do them, they are what an experienced responder does first.
INSTINCTS = [
    {"instinct": "ask which user",
     "for_a_human": "identifies the actor",
     "for_an_agent": "returns the service account, which is true of every "
                     "action the platform has ever taken",
     "ask_instead": "which human is at the head of the delegation chain, and "
                    "which workload identity acted for them"},
    {"instinct": "disable the account",
     "for_a_human": "stops them",
     "for_an_agent": "stops nothing already issued. B2.5's revocation is at "
                     "the workload, and D1.9 measured which paths it reaches",
     "ask_instead": "revoke the workload, and check the act-paths that "
                    "revocation is not on"},
    {"instinct": "read what they did",
     "for_a_human": "a session is a story",
     "for_an_agent": "a run is a thousand actions and the model's own "
                     "narration of them, which is not evidence",
     "ask_instead": "read the audit rows and the motive origin; the agent's "
                    "summary is a claim by the subject of the investigation"},
]


def attribute(row):
    """The four questions, answered from one audit row — or named as gaps."""
    chain = str(row.get("chain", ""))
    human = chain.split("=>")[0].strip() if "=>" in chain else None
    workload = next((p.strip() for p in chain.split("=>")
                     if "spiffe://" in p), None)
    return {
        "human": human,
        "workload": workload,
        "call": row.get("tool"),
        "motive": row.get("motive_origin"),
        "answered": sum(1 for v in (human, workload, row.get("tool"),
                                    row.get("motive_origin")) if v),
        "of": 4,
        "unanswered": [name for name, v in
                       (("human", human), ("workload", workload),
                        ("call", row.get("tool")),
                        ("motive", row.get("motive_origin"))) if not v],
    }




# --------------------------------------------------------------------------- #
# E3.6 — an investigation that is allowed to change its mind
# --------------------------------------------------------------------------- #
# An agent given an incident forms a hypothesis in its first turn and spends
# the rest of the investigation gathering support for it. That is not a model
# failure; it is what a plan does when nothing in the loop is allowed to
# abandon one. The fix is structural: a plan record, an explicit replan
# trigger, and abandoned branches that stay in the trace.
class Plan:
    """A hypothesis, its evidence, and every branch that was dropped."""

    def __init__(self, hypothesis):
        self.current = hypothesis
        self.history = []
        self.evidence = []

    def observe(self, fact, *, supports):
        self.evidence.append({"fact": fact, "supports": supports})
        return self

    def should_replan(self, *, threshold=2):
        """Contradicting evidence is a trigger, not a judgement call."""
        against = sum(1 for e in self.evidence if not e["supports"])
        return against >= threshold

    def replan(self, new_hypothesis, why):
        self.history.append({"abandoned": self.current, "why": why,
                             "evidence_at_the_time": list(self.evidence)})
        self.current = new_hypothesis
        self.evidence = []
        return self

    def trace(self):
        return {"current": self.current,
                "abandoned": [h["abandoned"] for h in self.history],
                "replans": len(self.history),
                "why": "an abandoned branch that is not in the trace looks "
                       "like a branch nobody considered"}




