# step:file C1.9
"""The kill switch — and the paths it does not reach.

A2.5 built revocation and it works: `registry.revoke()` retires a workload,
and `identity.verify_delegated()` refuses anything it signed from that moment
rather than at token expiry. That is a real control and it is the reason this
lesson is not "build a kill switch".

The lesson is the second question, which nobody asks until the night they need
it: **what is still able to act after the switch is thrown?**

In this tree, three things are, and each is a different kind of gap:

1. **The direct API path.** `agents/file_agent.py::handle` calls
   `payments_api.download_invoice` in-process. No token is minted, so
   `verify_delegated` is never reached, so revocation is not on that path at
   all. A1.1's architecture map has a card for exactly this — *direct APIs, no
   MCP in the path, so no policy point either* — and this is what that card
   costs on the night.
2. **The in-flight call.** A run already past the exchange and inside the
   resource server completes. The window is short; it is not zero, and on the
   money path short is not the same as harmless.
3. **The evidence.** A stop that kills processes destroys the run state an
   investigation needs. Containment and forensics pull in opposite directions
   and the resolution has to be decided in advance, not at 3am.

So the measurement here is coverage, not capability: which of the paths an
agent can act through are actually behind the switch.
"""
import time


# Every route by which something in this system can have an effect, and
# whether revoking the workload identity stops it. Written by reading the
# tree, not by reading the design.
PATHS = [
    {"path": "MCP tool call", "via": "identity.verify_delegated",
     "stopped_by_revocation": True,
     "why": "the resource server checks registry.active on every call"},
    {"path": "token exchange", "via": "identity.token_exchange",
     "stopped_by_revocation": True,
     "why": "a revoked workload cannot obtain a new delegated token"},
    {"path": "direct API call", "via": "agents/file_agent.py::handle",
     "stopped_by_revocation": False,
     "why": "calls tools/payments_api.download_invoice in-process — no token "
            "is minted, so no check is reached. A1.1's 'direct APIs' card"},
    {"path": "shell", "via": "agents/coding_agent.py::_open_branch",
     "stopped_by_revocation": False,
     "why": "subprocess, in the orchestrator's own process. A3.2's sandbox "
            "profile forbids it; nothing enforces the profile"},
    {"path": "in-flight call", "via": "a run already past the exchange",
     "stopped_by_revocation": False,
     "why": "the delegated token was verified before the switch was thrown; "
            "the call completes"},
]


def coverage():
    """What fraction of the act-paths the kill switch is actually on.

    C1.9's Day 2 number, and it is not 1.0 in this tree. Report it that way:
    a kill switch described as covering the fleet, measured at 0.4, is a
    finding about the architecture rather than about the switch.
    """
    stopped = [p for p in PATHS if p["stopped_by_revocation"]]
    return {
        "paths": len(PATHS), "stopped": len(stopped),
        "coverage": round(len(stopped) / len(PATHS), 3),
        "still_live": [p["path"] for p in PATHS
                       if not p["stopped_by_revocation"]],
        "note": "coverage below 1.0 is an architecture finding: these paths "
                "were never behind a policy point, so there was nothing for "
                "the switch to switch",
    }


def revoke_fleet(registry, spiffe_ids, *, reason="fleet stop"):
    """Throw the switch, and return what it did and did not do."""
    started = time.time()
    stopped = []
    for sid in spiffe_ids:
        registry.revoke(sid, reason=reason)
        stopped.append(sid)
    return {
        "revoked": sorted(stopped),
        "seconds": round(time.time() - started, 4),
        "still_live": coverage()["still_live"],
        # The sentence that has to be in the runbook, because at 3am somebody
        # will report "the fleet is stopped" and mean "the tokens are dead".
        "do_not_report_as": "the fleet is stopped",
        "report_as": f"{len(stopped)} workload identities revoked; "
                     f"{len(coverage()['still_live'])} act-paths unaffected",
    }


def preserves_evidence(plan):
    """Does this stop plan keep what an investigation needs?

    The conflict is real and both sides are right. Containment wants the
    process gone; C1.10 wants the run state. Deciding it in advance is the
    control — deciding it during the incident means whoever types faster wins.
    """
    needs = {
        "audit_rows": "the chain A2.8 built; kill the database and it is gone",
        "trace_spans": "what the agent was doing, and why",
        "in_flight_args": "the arguments of the call that was running",
        "memory_rows": "what the agent had been told in earlier runs",
    }
    missing = {k: why for k, why in needs.items() if not plan.get(k)}
    return {"preserved": sorted(set(needs) - set(missing)),
            "lost": missing,
            "safe_to_run": not missing,
            "why": "a containment that destroys the record leaves you certain "
                   "it stopped and unable to say what it stopped"}


def time_to_stop(fleet_size, *, per_call_seconds=0.05, parallelism=1):
    """How long the switch actually takes at fleet scale.

    Worth computing before it is needed. A per-identity revocation loop that
    is instant at four workloads takes a quarter of an hour at twenty
    thousand, and the runbook says "revoke the fleet" as though it were one
    action.
    """
    seconds = fleet_size * per_call_seconds / max(parallelism, 1)
    return {"fleet": fleet_size, "seconds": round(seconds, 1),
            "minutes": round(seconds / 60, 2),
            "instant": seconds < 5,
            "note": "measure this before the incident; 'revoke the fleet' is "
                    "written in runbooks as though it were a single action"}
