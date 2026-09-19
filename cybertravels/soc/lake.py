# step:file E2.1
"""Where agent telemetry lands, and what each tier costs to query.

The failure is not technical and it happens every time. Nobody prices the new
source, so it is indexed hot like everything else. The bill arrives, retention
is cut **across the board** because that is the lever the console offers, and
the traces go first — they are the newest source, the least defended in a
budget meeting, and the only one that answers E3.4.

The decision this file forces is per source, and it is driven by the queries
the SOC actually runs rather than by how important the source feels. A source
queried twice a quarter during postmortems does not belong in hot storage and
losing it entirely is not the alternative.
"""

# Per GB per month, and what each tier can do. The numbers are illustrative
# and their *ratios* are not — cold is roughly two orders of magnitude cheaper
# than hot, and that ratio decides every argument in this lesson.
#
# The capabilities **nest**, and getting that wrong is not a modelling detail.
# A hot index serves a postmortem query perfectly well; it is simply the most
# expensive way to do it. Written as three disjoint sets, no tier supports
# `audit_rows` — which needs alerting and audit — and the tiering function
# raises on the one source the SOC most needs to keep. Each tier adds to the
# one below it.
_COLD = {"investigation", "postmortem", "audit"}
_WARM = _COLD | {"interactive hunt"}
_HOT = _WARM | {"alerting", "dashboards"}

TIERS = {
    "hot":   {"cost_gb_month": 2.50, "latency": "seconds", "supports": _HOT},
    "warm":  {"cost_gb_month": 0.35, "latency": "minutes", "supports": _WARM},
    "cold":  {"cost_gb_month": 0.02, "latency": "hours, and a restore job",
              "supports": _COLD},
}

# The agent's own sources, with the volume they generate and — the column that
# decides the tier — what the SOC actually does with each one.
SOURCES = {
    "agent_spans": {"gb_month": 220, "queries": {"interactive hunt",
                                                 "investigation"}},
    "audit_rows": {"gb_month": 8, "queries": {"alerting", "investigation",
                                              "audit"}},
    "approvals": {"gb_month": 1, "queries": {"alerting", "audit"}},
    "model_io": {"gb_month": 900, "queries": {"postmortem"}},
    "mcp_calls": {"gb_month": 60, "queries": {"alerting", "interactive hunt"}},
}


def tier_for(source):
    """The cheapest tier that supports every query this source is used for.

    Cheapest-that-works, rather than a judgement about importance. Importance
    is how `model_io` — nine hundred gigabytes queried twice a quarter — ends
    up in hot storage and takes the budget that was paying for the audit rows.
    """
    need = SOURCES[source]["queries"]
    for name in ("cold", "warm", "hot"):
        if need <= TIERS[name]["supports"]:
            return name
    raise ValueError(f"{source}: no tier supports {sorted(need)}")


def plan(sources=None):
    """The tiering decision, with the bill and the counterfactual beside it."""
    sources = sources or list(SOURCES)
    rows = []
    for s in sources:
        tier = tier_for(s)
        gb = SOURCES[s]["gb_month"]
        rows.append({"source": s, "tier": tier, "gb_month": gb,
                     "cost_month": round(gb * TIERS[tier]["cost_gb_month"], 2),
                     "queries": sorted(SOURCES[s]["queries"]),
                     "latency": TIERS[tier]["latency"]})
    tiered = sum(r["cost_month"] for r in rows)
    all_hot = sum(SOURCES[s]["gb_month"] * TIERS["hot"]["cost_gb_month"]
                  for s in sources)
    return {
        "rows": sorted(rows, key=lambda r: -r["cost_month"]),
        "cost_month": round(tiered, 2),
        "cost_if_all_hot": round(all_hot, 2),
        "saved": round(all_hot - tiered, 2),
        # The sentence this lesson exists to prevent somebody saying.
        "note": "the alternative to tiering is not a bigger bill, it is a "
                "retention cut applied across every source at once — and the "
                "traces go first because they are the newest",
    }


def what_a_cut_costs(dropped):
    """Which clock stages stop working if this source is cut.

    Named against `soc.CLOCK`, so the trade is visible as an investigation
    that takes longer rather than as a line item that got smaller.
    """
    impact = {
        "agent_spans": ["triage", "attribute", "recover"],
        "audit_rows": ["detect", "attribute", "scope"],
        "approvals": ["detect", "scope"],
        "model_io": ["recover"],
        "mcp_calls": ["detect", "triage"],
    }
    return {"dropped": dropped,
            "stages_degraded": impact.get(dropped, []),
            "gb_month_saved": SOURCES.get(dropped, {}).get("gb_month", 0)}
