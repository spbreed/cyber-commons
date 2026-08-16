"""The three planes, the autonomy ladder, and blast radius as a number.

This is the vocabulary Module 0 installs and every other track reuses. The point
of modelling it in code rather than prose is that it forces the distinction to
be decidable: given a tool manifest, a function has to *return* which plane each
tool sits in, and that answer can be wrong in a way a slide cannot.

    decision plane   the model proposes. Nothing here changes the world.
    control plane    policy decides whether a proposal becomes an action.
    action plane     the tool executes. State changes here, and only here.

"The model did it" is never a root cause, because the model only ever writes on
the decision plane. Something on the control plane let the proposal through.
"""
from __future__ import annotations

from dataclasses import dataclass, field

DECISION, CONTROL, ACTION = "decision", "control", "action"

# Autonomy ladder. The rung is not about how clever the model is — it is about
# what the model's output is allowed to trigger without a human in the path.
LADDER = {
    "L1": "Assist — model proposes, human performs every action.",
    "L2": "Act with approval — model calls tools, human approves each call.",
    "L2.5": "Act within a blast radius — pre-approved tool set, bounded scope, "
            "human reviews after the fact.",
    "L3": "Autonomous — model acts and self-verifies; humans see aggregates.",
}
RUNGS = ["L1", "L2", "L2.5", "L3"]


@dataclass(frozen=True)
class Tool:
    """One entry in an agent's tool manifest."""
    name: str
    writes: bool = False        # can it change state anywhere?
    external: bool = False      # does it reach outside the sandbox?
    reversible: bool = True     # can the change be undone cheaply?
    scope: str = "self"         # self | project | tenant | org | internet

    # A tool that cannot write is a read tool no matter what it is called. This
    # is the whole reason the manifest is the input: names lie, capabilities do not.
    @property
    def plane(self) -> str:
        return ACTION if self.writes else DECISION


# Scope ordering — how far a single bad call can reach.
SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20, "internet": 50}


@dataclass
class Manifest:
    """An agent's declared capabilities, plus the controls wrapped around them."""
    agent: str
    tools: list[Tool] = field(default_factory=list)
    approval_required: set[str] = field(default_factory=set)
    rung: str = "L2"

    def by_plane(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {DECISION: [], CONTROL: [], ACTION: []}
        for t in self.tools:
            out[t.plane].append(t.name)
        # every tool that needs approval puts a control-plane gate in the path
        out[CONTROL] = sorted(self.approval_required)
        return out

    def blast_radius(self) -> dict:
        """What one unreviewed action can cost, as a comparable number.

        The score is deliberately crude — scope weight, doubled when the change
        cannot be undone, zeroed when a human must approve the call. Crude and
        computed beats precise and never measured: the value of the metric is
        that adding a tool moves it, so a design review has something to argue
        about other than vibes.
        """
        per_tool, total = {}, 0
        for t in self.tools:
            if not t.writes:
                continue
            score = SCOPE_WEIGHT.get(t.scope, 1)
            if not t.reversible:
                score *= 2
            if t.name in self.approval_required:
                score = 0            # a gated call is not unreviewed
            per_tool[t.name] = score
            total += score
        return {"agent": self.agent, "rung": self.rung, "total": total,
                "per_tool": dict(sorted(per_tool.items(), key=lambda kv: -kv[1]))}

    def rung_check(self) -> list[str]:
        """Complaints where the claimed rung and the actual controls disagree."""
        problems = []
        writers = [t for t in self.tools if t.writes]
        ungated = [t.name for t in writers if t.name not in self.approval_required]
        if self.rung == "L1" and writers:
            problems.append(
                f"claims L1 but holds {len(writers)} state-changing tool(s): "
                f"{', '.join(t.name for t in writers)}")
        if self.rung == "L2" and ungated:
            problems.append(
                f"claims L2 (approve every call) but {len(ungated)} writer(s) are "
                f"ungated: {', '.join(ungated)}")
        if self.rung == "L2.5":
            wide = [t.name for t in writers
                    if SCOPE_WEIGHT.get(t.scope, 1) >= SCOPE_WEIGHT["org"]
                    and t.name not in self.approval_required]
            if wide:
                problems.append(
                    f"claims L2.5 (bounded blast radius) but these reach org-wide "
                    f"or further with no gate: {', '.join(wide)}")
        irreversible = [t.name for t in writers
                        if not t.reversible and t.name not in self.approval_required]
        if irreversible and self.rung != "L3":
            problems.append(
                f"irreversible and ungated: {', '.join(irreversible)} — "
                "there is no 'undo' step to review after the fact")
        return problems


def diff_manifests(before: Manifest, after: Manifest) -> dict:
    """What changed between two versions of an agent — the threat-model delta.

    A threat model goes stale the moment the tool list changes, so the useful
    artefact is not the model but this diff.
    """
    b = {t.name: t for t in before.tools}
    a = {t.name: t for t in after.tools}
    added, removed = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    return {
        "added": added,
        "removed": removed,
        "blast_before": before.blast_radius()["total"],
        "blast_after": after.blast_radius()["total"],
        "delta": after.blast_radius()["total"] - before.blast_radius()["total"],
        "new_problems": [p for p in after.rung_check() if p not in before.rung_check()],
    }


def describe_ladder() -> str:
    return "\n".join(f"  {r:5s} {LADDER[r]}" for r in RUNGS)
