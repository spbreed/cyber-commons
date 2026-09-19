"""Observability — the run record, as spans.

An agent run that emits only its final answer is unreviewable. What an
investigation needs is the shape of the run: which agent, which step, what it
decided, which tool it reached for, what the delegated token said, and what
came back. That is a trace, and it is the same idea OpenTelemetry formalises —
this is a small in-process version of it so the tree stays dependency-light and
a reader can see what a span *is* before meeting a collector.

Three rules the emitting code follows, and each one is a lesson in Function D:

* **Every span carries the trace id**, so the audit row and the agent step can
  be joined. An audit log that cannot be joined to the reasoning that caused
  the action tells you what happened and never why.
* **Nothing secret is ever put in a span.** Tokens are summarised to their
  claims — subject, actor, audience, scope, expiry — never carried whole.
* **Refusals are spans too.** A trace that records only successful tool calls
  hides exactly the events worth alerting on.
"""
# step:file A1.1
import json
import time
import uuid


def new_trace_id():
    return uuid.uuid4().hex[:16]


def redact_claims(claims: dict) -> dict:
    """What a span is allowed to say about a token. Never the token."""
    return {
        "sub": claims.get("sub"),
        "act": (claims.get("act") or {}).get("sub"),
        "aud": claims.get("aud"),
        "scope": claims.get("scope"),
        "exp": claims.get("exp"),
    }


class Trace:
    """One agent run. Append spans; read them back as JSON lines."""

    def __init__(self, user_id, agent, trace_id=None):
        self.trace_id = trace_id or new_trace_id()
        self.user_id = user_id
        self.agent = agent
        self.started = time.time()
        self.spans = []

    def span(self, kind, **fields):
        s = {
            "trace_id": self.trace_id,
            "seq": len(self.spans),
            "t": round(time.time() - self.started, 4),
            "kind": kind,
            "user": self.user_id,
            "agent": self.agent,
        }
        s.update(fields)
        self.spans.append(s)
        return s

    # --- the vocabulary. One method per thing worth alerting on. ---------
    def thought(self, text):
        return self.span("thought", text=text)

    def plan(self, tool, args, scope, high_risk):
        return self.span("plan", tool=tool, args=args, scope=scope,
                         high_risk=high_risk)

    def approval(self, tool, granted, approver=None):
        return self.span("approval", tool=tool, granted=granted,
                         approver=approver)

    def token(self, tool, claims):
        return self.span("token_issued", tool=tool,
                         claims=redact_claims(claims))

    def denied(self, tool, reason, at):
        """`at` says which boundary refused: policy, human, or resource."""
        return self.span("denied", tool=tool, reason=reason, at=at)

    def result(self, tool, summary):
        return self.span("tool_result", tool=tool, summary=summary)

    def final(self, text):
        return self.span("final", text=text)

    def budget(self, what, used, ceiling):
        return self.span("budget", what=what, used=used, ceiling=ceiling)

    def as_jsonl(self):
        return "\n".join(json.dumps(s, default=str) for s in self.spans)

    def counts(self):
        """A quick shape of the run, which is what a detection rule reads."""
        out = {}
        for s in self.spans:
            out[s["kind"]] = out.get(s["kind"], 0) + 1
        return out
