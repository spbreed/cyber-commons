# step:file E4.1
"""From a conclusion to the actor actually stopped.

Five lessons, and they are all about the same thing: response automation is
decided per runbook by whoever wrote it, so the blast radius of the *response*
is unknown until it fires. The first wrong automated action is frequently
worse than the incident, and it is always more embarrassing.

So the tier is **derived**, not chosen. One policy, keyed on two properties
that can be read off an action rather than argued about — how much it touches,
and whether it can be undone — and every runbook's tier falls out of it. A
runbook whose author picked "fully automated" because that is the impressive
demo now has to change the policy in front of everybody, which is the point.
"""


# Blast radius x reversibility -> the tier. The grid is the policy; the
# runbooks are consequences of it.
#
# Reversible-and-wide is deliberately automated. That is where the value is:
# throttling a fleet is instantly undoable, and a response system that will
# not do the cheap reversible thing without a human is a response system that
# does nothing at 3am.
TIERS = {
    ("narrow", "reversible"): "automated",
    ("wide", "reversible"): "automated",
    ("narrow", "irreversible"): "human-in-the-loop",
    ("wide", "irreversible"): "manual",
}

ACTIONS = {
    "throttle the agent": ("narrow", "reversible"),
    "reduce scope on the next exchange": ("narrow", "reversible"),
    "reroute to a supervised queue": ("wide", "reversible"),
    "force human approval on every call": ("wide", "reversible"),
    "revoke one workload identity": ("narrow", "irreversible"),
    "revoke the fleet": ("wide", "irreversible"),
    "delete the run's artefacts": ("wide", "irreversible"),
    "roll back a booking": ("narrow", "irreversible"),
}


def tier_for(action):
    try:
        key = ACTIONS[action]
    except KeyError:
        raise KeyError(
            f"{action!r} has no blast radius or reversibility recorded — an "
            f"action nobody classified cannot be assigned a tier, and "
            f"defaulting it to automated is how this goes wrong")
    return TIERS[key]


def policy():
    return [{"action": a, "radius": r, "reversible": rev,
             "tier": TIERS[(r, rev)]}
            for a, (r, rev) in sorted(ACTIONS.items())]


# step:E4.2 add
# --------------------------------------------------------------------------- #
# E4.2 — the human-in-the-loop tier has to carry a real decision
# --------------------------------------------------------------------------- #
# A confirmation dialog is not a decision point. It arrives with one button
# that continues and one that abandons the incident, at a moment when the
# person is already committed, and it will be clicked. B3.6 measured what
# happens to a gate at volume; this is what happens to one at urgency.
#
# A real decision point has three properties, and a runbook that cannot
# produce them should be tiered manual instead.
def decision_point(runbook):
    needs = {
        "states_what_it_will_do": "in the specific — which identities, which "
                                  "bookings, not 'contain the agent'",
        "states_what_it_cannot_undo": "the part that decides the answer",
        "offers_a_narrower_option": "otherwise the choice is act or abandon, "
                                    "and act always wins",
    }
    missing = {k: why for k, why in needs.items() if not runbook.get(k)}
    return {"runbook": runbook.get("name"), "real_decision": not missing,
            "missing": missing,
            "verdict": "human-in-the-loop" if not missing else
            "this is a confirmation dialog; tier it manual or fix the prompt"}


def assign(runbook):
    """Derive the tier, and refuse a runbook that claims a tier it cannot hold."""
    derived = tier_for(runbook["action"])
    claimed = runbook.get("tier")
    out = {"runbook": runbook.get("name"), "action": runbook["action"],
           "derived_tier": derived, "claimed_tier": claimed}
    if claimed and claimed != derived:
        out["conflict"] = (
            f"claims {claimed} and the policy derives {derived} — change the "
            f"policy in front of everybody, or accept the derived tier")
    if derived == "human-in-the-loop":
        out["decision_point"] = decision_point(runbook)
    return out
# step:E4.2 end


# step:E4.3 add
# --------------------------------------------------------------------------- #
# E4.3 — containment in order, cheapest first
# --------------------------------------------------------------------------- #
# Mass revocation stops the incident and the business in the same instant, and
# the incident review is then about the outage. The ladder exists so that the
# response can start immediately with something reversible and escalate only
# as far as it has to.
#
# Each rung is strictly more disruptive than the one below, and each is
# reversible until the last two. Going straight to the bottom is a decision;
# arriving there because nobody built the rungs is not.
LADDER = [
    ("throttle", "rate-limit the loop", True,
     "buys minutes and costs latency"),
    ("scope-reduce", "narrow what the next token exchange may request", True,
     "B2.3's narrowing, applied deliberately"),
    ("reroute", "send the agent's work to a supervised queue", True,
     "the work continues, a human sees it"),
    ("force-HITL", "every call needs approval", True,
     "A1.7's gate, turned all the way up — and B3.6 says this does not scale"),
    ("revoke", "retire the workload identities", False,
     "B2.5; stops the token paths, and D1.9 measured which paths it misses"),
    ("hard-stop", "kill the processes", False,
     "and with them the run state E5.1 needs"),
]


def escalate(from_rung=None):
    """The next rung, and what it costs. Never skips."""
    names = [r[0] for r in LADDER]
    i = 0 if from_rung is None else names.index(from_rung) + 1
    if i >= len(LADDER):
        return None
    rung, what, reversible, why = LADDER[i]
    return {"rung": rung, "action": what, "reversible": reversible,
            "why": why, "remaining": names[i + 1:]}


def ladder_report(reached):
    names = [r[0] for r in LADDER]
    i = names.index(reached)
    return {"reached": reached, "rungs_used": i + 1,
            "still_reversible": all(r[2] for r in LADDER[:i + 1]),
            "skipped": [],
            "why": "starting at the bottom is a decision; arriving there "
                   "because the rungs were never built is not"}
# step:E4.3 end


# step:E4.4 add
# --------------------------------------------------------------------------- #
# E4.4 — who is allowed to stop it, and how long they take
# --------------------------------------------------------------------------- #
# The authority exists on paper, held by somebody who has never used it, for a
# system that did not exist when the policy was written. The readiness check
# is four questions and the last one is the only one with a number in it.
def readiness(state):
    checks = {
        "named_holder": "a person, not a role — a role is nobody at 3am",
        "deputy": "the holder is asleep, on a plane, or is the incident",
        "reachable_out_of_hours": "tested, by calling them",
        "rehearsed": "the switch has been thrown in anger or in a drill",
        "measured_time_to_stop": "in minutes, from a real attempt",
    }
    missing = {k: why for k, why in checks.items() if not state.get(k)}
    return {"ready": not missing, "missing": missing,
            "time_to_stop_minutes": state.get("measured_time_to_stop"),
            "why": "an unrehearsed stop authority is a paragraph; the first "
                   "time it is exercised will be the worst time to find out "
                   "how long it takes"}
# step:E4.4 end


# step:E4.5 add
# --------------------------------------------------------------------------- #
# E4.5 — the kill switch, from the defender's side
# --------------------------------------------------------------------------- #
# D1.9 measured this from the attacker's side and found coverage of 0.4 in
# this tree. The same measurement is the defender's readiness check, and it is
# imported rather than rewritten — two teams computing the same number
# separately is how they end up disagreeing about it during the incident.
#
# What this adds is the ordering that the red-team view did not need: snapshot
# before terminate, and revocation in the *same* action rather than after it.
# Terminating agents while their tokens stay valid leaves the persistence in
# place, and the incident ends when somebody revokes keys rather than when the
# processes stop.
from ..redteam.containment import coverage, preserves_evidence, time_to_stop  # noqa: E402,F401


KILL_ORDER = [
    ("snapshot", "run state, audit rows, in-flight arguments — E5.1 needs "
                 "them and terminate destroys them"),
    ("revoke", "in the same action as the stop, not after it"),
    ("terminate", "the processes"),
    ("verify", "re-run the coverage check: which act-paths are still live"),
]


def kill_path(plan):
    """Is this a tested kill path, in the right order, with evidence kept?

    The ordering check has to state what it requires rather than compare the
    plan against itself. The first version read
    `ordered == [s for s in KILL_ORDER if plan.get(s)]`, which is the same
    expression twice and is true of every plan — so a plan that terminated
    without revoking came back `order_correct`, which is precisely the
    failure this lesson is about.
    """
    ev = preserves_evidence(plan)
    cov = coverage()
    ordered = [step for step, _why in KILL_ORDER if plan.get(step)]

    missing = [s for s in ("snapshot", "revoke", "terminate")
               if not plan.get(s)]
    problems = [f"{s} is not in the plan" for s in missing]
    if not missing:
        if ordered.index("snapshot") > ordered.index("terminate"):
            problems.append("terminate runs before snapshot, which destroys "
                            "the run state E5.1 needs")
        if ordered.index("revoke") > ordered.index("terminate"):
            problems.append("terminate runs before revoke, so the processes "
                            "stop and the tokens stay valid — the persistence "
                            "survives the containment")
    return {
        "steps": ordered,
        "order_correct": not problems,
        "order_problems": problems,
        "verified_after": bool(plan.get("verify")),
        "evidence_preserved": ev["safe_to_run"],
        "evidence_lost": sorted(ev["lost"]),
        "act_path_coverage": cov["coverage"],
        "still_live_after": cov["still_live"],
        "independent_of_agent_path": bool(plan.get("independent_path")),
        "ready": (not problems and ev["safe_to_run"]
                  and bool(plan.get("independent_path"))),
        "why": "a kill path that runs through the agent's own execution path "
               "is one the incident can interfere with",
    }
# step:E4.5 end
