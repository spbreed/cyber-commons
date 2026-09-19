# step:file A3.7
"""The agent gateway — one choke point, once there is more than one agent.

By A3.6 every control exists and each one lives where it was convenient to
write it: policy in `policy.py`, called from the runtime; budgets on the loop;
egress inside `egress.py`, invoked by whoever remembers; return validation in
`returns.py`, likewise. That works for one agent and stops working at four,
for a reason that has nothing to do with the controls themselves.

**A control enforced in N places is N chances to skip it.** The second agent is
written by somebody else on a deadline, and it calls the tool directly. Nothing
fails. The control is still in the repository, still tested, and no longer on
the path.

So the controls move behind one entry point, and the agents lose their direct
route. That is the whole idea, and the cost is real: a single choke point is a
single point of failure and a queue. It is worth it because the alternative is
a control surface nobody can enumerate.

Ordered deliberately. Identity before policy, because policy needs to know who
is asking. Budget before the human gate, because a run that is out of budget
should not consume a reviewer. Egress and return validation last, on the way
out and the way back.
"""
from . import egress, identity, policy, returns


class Refused(Exception):
    """The gateway declined. Carries the decision, so the caller can say why."""

    def __init__(self, decision):
        super().__init__(decision.reason)
        self.decision = decision


class Gateway:
    """One entry point. Agents hold this and nothing downstream of it."""

    def __init__(self, *, exemptions=(), budget=None, call=None):
        self.exemptions = list(exemptions)
        self.budget = budget
        self._call = call                 # how to actually reach the resource
        self.decisions = []               # every decision, for the audit trail

    def authorise(self, tool, args, session):
        """Identity -> policy -> budget. Returns a Decision or raises."""
        d = policy.decide(tool, args, session, exemptions=self.exemptions)
        self.decisions.append(d)
        if not d.allowed:
            raise Refused(d)
        if self.budget is not None and not self.budget.call():
            stop = policy.Decision(
                False, "tool-call budget exhausted", "budget", tool,
                getattr(session, "user_id", "?"))
            self.decisions.append(stop)
            raise Refused(stop)
        return d

    def egress(self, url, body=""):
        """Every outbound call, through here. An agent that can reach the
        network directly has an egress control that describes it rather than
        constrains it."""
        return egress.check(url, body)

    def returned(self, tool, raw, *, asked_for=None, session=None):
        return returns.guard(tool, raw, asked_for=asked_for, session=session)

    def coverage(self):
        """What fraction of calls this gateway actually adjudicated.

        A3.7's Day 2. Anything below 100% means an agent still has a direct
        route, and the number is the only way to find out — the controls all
        pass their own tests either way.
        """
        total = len(self.decisions)
        return {"decisions": total,
                "denied": sum(1 for d in self.decisions if not d.allowed),
                "rules": sorted({d.rule for d in self.decisions})}


def bound_call(gateway, tool, args, session, user_token, agent_token,
               audience, scope):
    """The whole path for one call, in the order the gateway enforces it."""
    gateway.authorise(tool, args, session)
    binding = identity.bind_call(tool, args)
    ex = identity.token_exchange(user_token, agent_token, audience, scope,
                                 call_binding=binding)
    return ex, binding
