"""GRC for systems that act: inventory, risk tiering, control mapping, evidence.

The governing insight for the whole E function: **point-in-time control testing
fails for AI**, because the thing you tested is not the thing running next week.
A model version changes, a tool is added, a prompt is edited — none of these are
code changes, and none of them trip a change-management process designed for
code.

So the artefacts here are continuous by construction: `ControlTest` carries a
freshness window and goes stale on its own, and `verify_continuously` reports how
much of your control set is currently *unevidenced* rather than how much passed
once.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


# ---------------------------------------------------------------- inventory
@dataclass
class AIAsset:
    """One entry in the AI/agent inventory — the artefact everything else needs.

    You cannot tier what you have not listed, and the honest finding of every
    first inventory is that most of it was already in production.
    """
    name: str
    kind: str                    # model | agent | copilot | embedded-feature
    owner: str = ""
    autonomy: str = "L1"         # the ladder from planes.py
    data: tuple[str, ...] = ()   # customer | employee | public | regulated
    external: bool = False       # can it act outside the org?
    shadow: bool = False         # discovered, not registered

    def gaps(self) -> list[str]:
        g = []
        if not self.owner:
            g.append("no named owner — nobody can accept the risk")
        if self.shadow:
            g.append("shadow: in use but never registered")
        if self.autonomy in ("L2.5", "L3") and not self.owner:
            g.append("acts semi-autonomously with no accountable owner")
        return g


# ---------------------------------------------------------------- risk tiering
TIER_THRESHOLDS = [(9, "critical"), (6, "high"), (3, "medium"), (0, "low")]


def risk_tier(asset: AIAsset) -> dict:
    """Tier by what it can *do*, not by which model it uses.

    Tiering on model capability is the common mistake: it makes every GPT-class
    system 'high' and every small model 'low', which tracks vendor marketing
    rather than exposure. Authority and data are what determine consequence.
    """
    score, why = 0, []
    autonomy_pts = {"L1": 0, "L2": 1, "L2.5": 3, "L3": 5}.get(asset.autonomy, 0)
    if autonomy_pts:
        score += autonomy_pts
        why.append(f"autonomy {asset.autonomy} (+{autonomy_pts})")
    if "regulated" in asset.data:
        score += 3
        why.append("regulated data (+3)")
    if "customer" in asset.data:
        score += 2
        why.append("customer data (+2)")
    if asset.external:
        score += 2
        why.append("can act externally (+2)")
    if asset.shadow:
        score += 1
        why.append("unregistered (+1)")
    tier = next(t for th, t in TIER_THRESHOLDS if score >= th)
    return {"asset": asset.name, "score": score, "tier": tier, "because": why}


# ---------------------------------------------------------------- controls
@dataclass
class Control:
    cid: str
    text: str
    kind: str                     # preventive | detective | corrective
    frameworks: tuple[str, ...] = ()


CATALOGUE = [
    Control("AC-1", "Agent identities are distinct from human identities and separately revocable",
            "preventive", ("NIST AI RMF: GOVERN-1.2", "ISO 42001: 6.1", "EU AI Act: Art.14")),
    Control("AC-2", "Delegated authority narrows at every hop and is recorded in an act chain",
            "preventive", ("NIST AI RMF: MANAGE-2.2", "ISO 42001: 8.1")),
    Control("SB-1", "Agent egress is deny-by-default with an allowlist",
            "preventive", ("NIST AI RMF: MANAGE-2.1", "ISO 27001: A.8.20")),
    Control("SB-2", "Privileged tools require approval below autonomy L3",
            "preventive", ("EU AI Act: Art.14 human oversight",)),
    Control("EV-1", "Every agent action is logged with the acting identity, not the principal",
            "detective", ("ISO 42001: 9.1", "EU AI Act: Art.12 record-keeping")),
    Control("EV-2", "Harness accuracy is evaluated against a held-out key on every release",
            "detective", ("NIST AI RMF: MEASURE-2.3",)),
    Control("DR-1", "Behavioural drift from the signed-off baseline raises an alert",
            "detective", ("NIST AI RMF: MEASURE-2.4", "ISO 42001: 9.1")),
    Control("ST-1", "A tested stop mechanism halts an agent fleet without vendor help",
            "corrective", ("EU AI Act: Art.14", "DORA: Art.11")),
]


def map_controls(asset: AIAsset, catalogue: list[Control] | None = None) -> dict:
    """Which controls this asset needs, and which frameworks that satisfies.

    Mapping runs one way only: control → framework. Starting from the framework
    produces a checklist that is complete and defends nothing.
    """
    catalogue = catalogue or CATALOGUE
    tier = risk_tier(asset)["tier"]
    required = []
    for c in catalogue:
        if tier in ("critical", "high"):
            required.append(c)
        elif c.kind == "preventive" or c.cid == "EV-1":
            required.append(c)
    frameworks = sorted({f for c in required for f in c.frameworks})
    return {"asset": asset.name, "tier": tier,
            "controls": [c.cid for c in required],
            "frameworks_satisfied": frameworks}


# ---------------------------------------------------- continuous verification
@dataclass
class ControlTest:
    """Evidence with an expiry date. That is the whole idea."""
    cid: str
    passed: bool
    evidence: str
    tested_at: float = field(default_factory=time.time)
    valid_for_days: float = 30.0

    def age_days(self, now: float | None = None) -> float:
        return ((now or time.time()) - self.tested_at) / 86400

    def fresh(self, now: float | None = None) -> bool:
        return self.age_days(now) <= self.valid_for_days

    def state(self, now: float | None = None) -> str:
        if not self.fresh(now):
            return "STALE"
        return "PASS" if self.passed else "FAIL"


def verify_continuously(tests: list[ControlTest], required: list[str],
                        now: float | None = None) -> dict:
    """The honest posture number: what fraction is *currently evidenced*.

    A control tested nine months ago is not passing. It is unevidenced, and an
    auditor who asks the right question will say so first.
    """
    by_id = {t.cid: t for t in tests}
    rows, evidenced = [], 0
    for cid in required:
        t = by_id.get(cid)
        if t is None:
            rows.append({"control": cid, "state": "NO EVIDENCE", "age_days": None})
            continue
        st = t.state(now)
        rows.append({"control": cid, "state": st, "age_days": round(t.age_days(now), 1)})
        if st == "PASS":
            evidenced += 1
    return {"required": len(required), "currently_evidenced": evidenced,
            "coverage": round(evidenced / len(required), 3) if required else 0.0,
            "rows": rows,
            "note": "point-in-time testing would report every non-STALE row as a "
                    "pass and overstate this number"}


# ---------------------------------------------------- guardrails & reporting
def guardrail_kind(rule: str, measurable_outcome: bool) -> dict:
    """Operating vs outcome guardrails — the distinction that decides enforceability.

    Operating: constrains how the system runs (testable now, cheap to verify).
    Outcome:   constrains what results are acceptable (matters more, needs a
               measurement you may not have yet).
    A programme of only operating guardrails passes audit and misses harm.
    """
    return {"rule": rule,
            "kind": "outcome" if measurable_outcome else "operating",
            "enforceable_today": not measurable_outcome,
            "risk": "may satisfy audit while missing real harm" if not measurable_outcome
                    else "needs an agreed measurement before it can be enforced"}


def board_translation(tier: str, blast_radius: int, asr: float, coverage: float) -> str:
    """E3.1 — the same facts, phrased so a board can decide something.

    The translation rule: no mechanism, no tool names. Exposure, likelihood,
    and the decision being asked for.
    """
    likelihood = "demonstrated" if asr > 0.3 else "reduced but unproven" if asr > 0 else "not demonstrated"
    return (f"Exposure: a {tier}-tier system can take {blast_radius} units of "
            f"unreviewed action.\n"
            f"Likelihood: red-team success rate {asr:.0%} — {likelihood}.\n"
            f"Assurance: {coverage:.0%} of required controls are currently evidenced; "
            f"the rest are untested or stale.\n"
            f"Decision requested: fund continuous verification, or accept the "
            f"unevidenced portion in writing with a named owner and a review date.")


SEQUENCING = """\
Sequencing an agentic security programme — the order that survives contact:

  1. Inventory        you cannot govern what you cannot list
  2. Identity         agents distinct from humans, separately revocable
  3. Containment      egress, paths, tools — deny by default
  4. Evidence         log the acting identity; retain enough to replay
  5. Evaluation       accuracy against a held-out key, per release
  6. Continuous       drift alerts and freshness windows on every control

Doing 5 before 2 produces a well-measured system nobody can switch off."""
