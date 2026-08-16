"""Incident response when the actor is an agent.

Three things change, and each has a primitive here:

  * **Scope is a graph, not a host.** The agent acted through delegation, so the
    blast radius follows the token chain (`scope_from_chain`).
  * **Containment must beat the loop.** A human approving a containment step is
    slower than the thing being contained (`containment_race`).
  * **Attribution is a design property.** If the agent impersonated a human,
    reconstruction is guesswork — `reconstruct` shows exactly how much you lose.

The regulatory clock starts at *awareness*, not at containment, and `clock`
computes that rather than letting anyone assume it.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LogLine:
    ts: float
    actor: str          # who the log says did it
    real_actor: str     # who actually did it (unknown to the responder at first)
    action: str
    target: str = ""


@dataclass
class Timeline:
    lines: list[LogLine] = field(default_factory=list)

    def add(self, *a, **kw) -> "Timeline":
        self.lines.append(LogLine(*a, **kw))
        return self

    def render(self, truth: bool = False) -> str:
        rows = [f"{'t+s':>6}  {'actor as logged':<18}{'action':<18}target"]
        base = self.lines[0].ts if self.lines else 0
        for ln in sorted(self.lines, key=lambda x: x.ts):
            who = ln.real_actor if truth else ln.actor
            rows.append(f"{ln.ts - base:>6.0f}  {who:<18}{ln.action:<18}{ln.target}")
        return "\n".join(rows)


def reconstruct(tl: Timeline) -> dict:
    """What the responder can and cannot establish from the logs alone.

    When an agent impersonates a principal, every line names the human. The
    incident is then reconstructed against the wrong actor, and the containment
    action taken — disable the human's account — does not stop the agent.
    """
    logged = {ln.actor for ln in tl.lines}
    actual = {ln.real_actor for ln in tl.lines}
    misattributed = [ln for ln in tl.lines if ln.actor != ln.real_actor]
    return {
        "actors_in_logs": sorted(logged),
        "actors_in_reality": sorted(actual),
        "misattributed_lines": len(misattributed),
        "hidden_actors": sorted(actual - logged),
        "attribution": "sound" if not misattributed else
                       "BROKEN — logs name the principal, not the agent that acted",
        "consequence": "none" if not misattributed else
                       f"containment aimed at {sorted(logged)} leaves "
                       f"{sorted(actual - logged)} running",
    }


def scope_from_chain(chain: list[str], reached: dict[str, list[str]]) -> dict:
    """Blast radius follows delegation, so scoping walks the actor chain.

    `reached` maps each actor to the resources it touched. Scoping only the last
    actor in the chain systematically under-counts the incident.
    """
    last_only = set(reached.get(chain[-1], []))
    full = {r for a in chain for r in reached.get(a, [])}
    return {"chain": " → ".join(chain),
            "scoped_last_actor_only": sorted(last_only),
            "scoped_whole_chain": sorted(full),
            "missed_by_naive_scoping": sorted(full - last_only),
            "undercount_factor": round(len(full) / len(last_only), 2) if last_only else None}


def containment_race(agent_actions_per_min: float, human_approval_minutes: float,
                     auto_containment_seconds: float = 5.0) -> dict:
    """How much more damage happens while containment waits for a human.

    This is the argument for pre-authorised, automated containment of non-human
    identities — expressed as a number rather than an opinion.
    """
    manual = agent_actions_per_min * human_approval_minutes
    auto = agent_actions_per_min * (auto_containment_seconds / 60)
    return {"actions_during_manual_approval": round(manual, 1),
            "actions_during_auto_containment": round(auto, 1),
            "ratio": round(manual / auto, 1) if auto else float("inf"),
            "conclusion": "pre-authorise revocation for non-human identities; "
                          "a human in the containment path is a control that "
                          "arrives after the damage"}


@dataclass
class Replay:
    """Deterministic replay: the difference between forensics and storytelling.

    An agent's run is replayable only if the inputs, the tool results and the
    model version were all recorded. Miss one and you can describe what happened
    but never demonstrate it.
    """
    prompts: list[str] = field(default_factory=list)
    tool_results: list[str] = field(default_factory=list)
    model_version: str = ""
    seed: int | None = None

    def replayable(self) -> tuple[bool, list[str]]:
        missing = []
        if not self.prompts:
            missing.append("prompts not recorded")
        if not self.tool_results:
            missing.append("tool results not recorded — the agent saw a world you cannot rebuild")
        if not self.model_version:
            missing.append("model version not pinned — a silent upgrade changes the output")
        if self.seed is None:
            missing.append("no seed — sampling makes the run unrepeatable")
        return (not missing), missing


def clock(awareness_ts: float, containment_ts: float, report_ts: float,
          deadline_hours: float = 72.0) -> dict:
    """Regulatory clocks start at awareness. Containment does not stop them."""
    to_contain = (containment_ts - awareness_ts) / 3600
    to_report = (report_ts - awareness_ts) / 3600
    return {"hours_to_containment": round(to_contain, 2),
            "hours_to_report": round(to_report, 2),
            "deadline_hours": deadline_hours,
            "met": to_report <= deadline_hours,
            "margin_hours": round(deadline_hours - to_report, 2),
            "note": "the clock runs from awareness, not from containment — "
                    "a fast fix does not buy reporting time"}


STOP_AUTHORITY = """\
Stop authority for autonomous systems — decide these before the incident:

  WHO can halt an agent fleet without seeking approval?
  WHAT is the mechanism, and is it tested? (revoke identity > kill process:
       a killed process restarts, a revoked identity cannot act)
  HOW LONG does it take end to end, measured, not estimated?
  WHAT BREAKS when it fires — and is that written down where the business
       has already agreed to it?
  WHO turns it back on, and against what evidence?

An untested stop button is a belief, not a control."""
