"""Detection engineering when the thing generating events is an agent.

Two directions run through this module and they are not the same job:

    detection *with* agents   the analyst's loop gets faster           (D1.1–D1.3)
    detection *for* agents    the agent is now the thing you watch     (D1.4–D1.7)

The second is the new work. An agent produces human-shaped telemetry at machine
speed, so the classic behavioural baselines invert: "logged in from two countries
in an hour" is an incident for a person and a Tuesday for a service. The
`agent_score` heuristic below makes that concrete and, importantly, gets some
cases wrong — which is the discussion the lesson wants.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field


@dataclass
class Event:
    """One telemetry record from the action plane."""
    ts: float
    actor: str
    action: str
    target: str = ""
    ok: bool = True
    session: str = ""


@dataclass
class Rule:
    """A detection: a name, a predicate, and — mandatory — what to do about it.

    A rule without a response is an alert nobody actions, which is worse than no
    rule because it consumes the attention budget that real ones need.
    """
    name: str
    severity: str
    predicate: object                    # Callable[[Event], bool]
    response: str

    def matches(self, e: Event) -> bool:
        return bool(self.predicate(e))    # type: ignore[operator]


@dataclass
class Alert:
    rule: str
    severity: str
    event: Event
    response: str


def run_rules(events: list[Event], rules: list[Rule]) -> list[Alert]:
    return [Alert(r.name, r.severity, e, r.response)
            for e in events for r in rules if r.matches(e)]


# --------------------------------------------------------- triage quality
def triage_quality(alerts: list[Alert], true_positives: set[str]) -> dict:
    """Precision, recall, and the number that actually decides adoption.

    Analysts do not abandon a detection because recall is low. They abandon it
    because precision is low — every false positive spends trust that recall
    never earns back.
    """
    flagged = {f"{a.event.actor}:{a.event.action}" for a in alerts}
    tp = len(flagged & true_positives)
    fp = len(flagged - true_positives)
    fn = len(true_positives - flagged)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {"alerts": len(alerts), "tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 3), "recall": round(rec, 3),
            "alerts_per_true_positive": round(len(alerts) / tp, 2) if tp else float("inf")}


# ------------------------------------------------- agent vs human attribution
def agent_score(events: list[Event], actor: str) -> dict:
    """Does this actor behave like software? 0.0 human … 1.0 machine.

    Three signals, none sufficient alone:
      * inter-arrival regularity  — humans are irregular, loops are not
      * rate                      — sustained high rate is not typing
      * off-hours continuity      — software has no evenings
    """
    ev = sorted((e for e in events if e.actor == actor), key=lambda e: e.ts)
    if len(ev) < 3:
        return {"actor": actor, "score": 0.0, "verdict": "insufficient data",
                "signals": {}}
    gaps = [b.ts - a.ts for a, b in zip(ev, ev[1:])]
    mean = statistics.fmean(gaps)
    # coefficient of variation: near 0 means metronomic
    cv = (statistics.pstdev(gaps) / mean) if mean else 0.0
    regularity = max(0.0, 1.0 - min(cv, 1.0))
    rate = len(ev) / max(ev[-1].ts - ev[0].ts, 1e-6)
    rate_signal = min(rate / 5.0, 1.0)              # ≥5 actions/sec is not a person
    span_hours = (ev[-1].ts - ev[0].ts) / 3600
    continuity = min(span_hours / 8.0, 1.0)         # 8h+ unbroken activity
    score = round(0.5 * regularity + 0.3 * rate_signal + 0.2 * continuity, 3)
    return {"actor": actor, "score": score,
            "verdict": "agent" if score > 0.6 else "human" if score < 0.3 else "unclear",
            "signals": {"regularity": round(regularity, 3),
                        "rate_per_sec": round(rate, 3),
                        "span_hours": round(span_hours, 2)}}


# ---------------------------------------------------------------- drift
@dataclass
class Baseline:
    """What normal looked like when the control was signed off.

    Drift monitoring exists because an agent's behaviour changes without a code
    change — new model version, new tool, new prompt. The control was tested
    against a behaviour that no longer exists.
    """
    tool_mix: dict[str, float]
    actions_per_hour: float

    def compare(self, events: list[Event], hours: float = 1.0) -> dict:
        if not events:
            return {"drift": 0.0, "verdict": "no data", "changes": {}}
        counts: dict[str, int] = {}
        for e in events:
            counts[e.action] = counts.get(e.action, 0) + 1
        total = sum(counts.values())
        now = {k: v / total for k, v in counts.items()}
        keys = set(now) | set(self.tool_mix)
        # total variation distance between the two tool mixes
        tvd = sum(abs(now.get(k, 0.0) - self.tool_mix.get(k, 0.0)) for k in keys) / 2
        rate_ratio = (total / hours) / self.actions_per_hour if self.actions_per_hour else 1.0
        changes = {k: round(now.get(k, 0.0) - self.tool_mix.get(k, 0.0), 3)
                   for k in sorted(keys)
                   if abs(now.get(k, 0.0) - self.tool_mix.get(k, 0.0)) > 0.05}
        return {"drift": round(tvd, 3), "rate_ratio": round(rate_ratio, 2),
                "verdict": "significant drift — re-test the controls" if tvd > 0.25
                           else "within tolerance",
                "changes": changes,
                "new_tools": sorted(set(now) - set(self.tool_mix))}


# ---------------------------------------------------------------- threat intel
@dataclass
class Indicator:
    value: str
    kind: str            # host | hash | technique
    source: str
    confidence: float

    def actionable(self) -> bool:
        """Intel you cannot turn into a rule is a newsletter."""
        return self.confidence >= 0.7 and self.kind in ("host", "hash")


def intel_to_rules(indicators: list[Indicator]) -> list[Rule]:
    """The only useful test of an intel feed: how many rules came out of it."""
    rules = []
    for i in indicators:
        if not i.actionable():
            continue
        rules.append(Rule(
            name=f"intel:{i.kind}:{i.value[:24]}",
            severity="high" if i.confidence > 0.9 else "medium",
            predicate=(lambda v: (lambda e: v in (e.target or "")))(i.value),
            response=f"isolate the actor and hunt back 30d ({i.source})"))
    return rules


def default_rules() -> list[Rule]:
    """A starter pack aimed at agent behaviour, not human behaviour."""
    return [
        Rule("agent reached metadata service", "critical",
             lambda e: "169.254.169.254" in (e.target or ""),
             "kill the session, rotate the instance role, hunt for use of the creds"),
        Rule("secret path accessed", "high",
             lambda e: any(p in (e.target or "") for p in (".ssh/", ".aws/", ".env")),
             "revoke the agent's token, diff what it read"),
        Rule("repeated tool failure", "medium",
             lambda e: not e.ok,
             "check for a loop stuck without a stop condition"),
        Rule("privileged tool without approval", "high",
             lambda e: e.action in ("delete_repo", "rotate_secrets"),
             "block, and check whether the approval gate is wired at all"),
    ]
