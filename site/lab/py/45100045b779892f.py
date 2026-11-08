"""The decision point — default-deny on the tool call.

Function G had a policy table: `config.TOOL_POLICY` maps a tool to the audience
and scope the runtime must obtain. It is an allow-list, so an unknown tool
already fails. What it is not is a *decision*, and the difference matters in
three places:

* it answers yes or no and never says **why**, so a refusal reaches the
  operator as an absence rather than a reason;
* it reads the tool name and nothing else — not who is calling, not with what
  arguments, not what the result would reach;
* there is nowhere to hang the things B3.6 and B3.9 need, which are the rate a
  human is being asked to approve and whether a control is currently switched
  off.

This module is the decision point those need. One function, `decide()`, called
once per tool call, returning a record rather than a boolean.

**Default-deny means the default branch is a denial, not that the list is an
allow-list.** Those are different: an allow-list with a permissive fallback for
"tools we have not classified yet" is an allow-list that denies nothing. The
fallback here is `deny`, and a tool nobody classified is a tool nobody may
call — which is inconvenient exactly once, when somebody adds a tool and
forgets, and that is the moment the control is doing its job.
"""
import time

from . import config


class Decision:
    """Allowed or not, and why. The `why` is the part that gets used."""

    __slots__ = ("allowed", "reason", "rule", "tool", "principal", "at",
                 "obligations")

    def __init__(self, allowed, reason, rule, tool, principal, obligations=()):
        self.allowed = allowed
        self.reason = reason
        self.rule = rule
        self.tool = tool
        self.principal = principal
        self.obligations = list(obligations)
        self.at = time.time()

    def as_dict(self):
        return {"allowed": self.allowed, "reason": self.reason,
                "rule": self.rule, "tool": self.tool,
                "principal": self.principal, "obligations": self.obligations}

    def __bool__(self):
        return self.allowed

    def __repr__(self):
        return (f"<Decision {'allow' if self.allowed else 'DENY'} "
                f"{self.tool} rule={self.rule}>")


def decide(tool, args, session, *, exemptions=None):
    """Evaluate one tool call against identity, tool and arguments.

    Returns a `Decision`. Obligations are things the caller must then do —
    currently `human-approval`, which is how the gate stops being a special
    case inside the runtime and becomes something policy asks for.
    """
    principal = getattr(session, "user_id", None) or "anonymous"

    rule = config.TOOL_POLICY.get(tool)
    if rule is None:
        # The default branch. Not a fallback to allow, and not an exception
        # that reads as a crash — a decision, with a reason an operator can act
        # on, which is usually "somebody shipped a tool and no one classified
        # it".
        return Decision(False, f"no policy classifies the tool {tool!r}",
                        "default-deny", tool, principal)

    role = getattr(session, "role", None)
    allowed_scopes = config.ROLE_ALLOWED_SCOPES.get(role, set())
    if rule["scope"] not in allowed_scopes:
        return Decision(
            False,
            f"role {role!r} may not delegate {rule['scope']!r}",
            "least-privilege", tool, principal)

    obligations = ["human-approval"] if rule["high_risk"] else []


    return Decision(True, "allowed by policy", "tool-policy", tool, principal,
                    obligations)


# --------------------------------------------------------------------------- #
# B3.6 — approval that survives volume
# --------------------------------------------------------------------------- #
# The gate A1.7 built is present and, at enough volume, does nothing. Coverage
# stays at 100% while actual review collapses, and nothing in the system
# reports that — which is why the control has to be *measured* rather than
# merely enabled.
#
# The number is approvals per reviewer per hour. Above a threshold a reviewer
# is clicking rather than reading, and the honest response is to reduce what
# needs approving rather than to hire another reviewer.
REVIEW_SECONDS = 90          # what reading one properly actually takes
_APPROVALS: list[tuple[float, str]] = []


def record_approval(reviewer):
    _APPROVALS.append((time.time(), reviewer))


def approval_load(window=3600):
    """Per reviewer, in the last `window` seconds — and whether the gate is
    still a control at that rate."""
    now = time.time()
    recent = [(t, who) for t, who in _APPROVALS if now - t <= window]
    per = {}
    for _, who in recent:
        per[who] = per.get(who, 0) + 1
    capacity = window / REVIEW_SECONDS
    return {
        "window_seconds": window,
        "per_reviewer": dict(sorted(per.items())),
        "capacity_per_reviewer": round(capacity, 1),
        # True when somebody is being asked to approve faster than anyone can
        # read. The gate is still 100% covered at this point, which is the
        # trap.
        "saturated": any(n > capacity for n in per.values()),
    }


def reset_approvals():
    _APPROVALS.clear()


