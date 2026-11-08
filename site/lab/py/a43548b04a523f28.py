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












