#!/usr/bin/env python3
"""Index every control an agentic platform needs — the ordinary ones and the agentic ones — and score coverage.

This is the executable half of the `control-baseline-index` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels estate so
two runs can be diffed and the result argued with.

The point the numbers make: an agent platform is mostly an ordinary platform.
Most of the controls below predate agents entirely, and a team that indexes only
the agentic rows will report good coverage of a small part of its exposure.

Standard library only, and deterministic, so it runs on a Kaggle kernel with the
internet switched off.
"""

from dataclasses import dataclass

FOUNDATION, AGENTIC = "foundation", "agentic"
IN_PLACE, PARTIAL, ABSENT = "in place", "partial", "absent"


@dataclass(frozen=True)
class Control:
    cid: str
    domain: str
    control: str
    era: str        # foundation = true before agents; agentic = new with them
    status: str     # what CyberTravels actually has today
    agent_note: str  # what the agents change about it, if anything
    owns: str       # the lesson that teaches it


# The index. Rows 1-12 are the controls a platform needed before any of this
# existed; the agentic rows are what the four agents added on top. Status is
# CyberTravels' own, measured in A1.1-A1.18 and in Function E.
INDEX = [
 # ---- foundation: the estate under the agents ----------------------------
 Control("F-01", "vulnerability management",
         "authenticated scanning of hosts, images and running workloads, with "
         "a fix clock per severity",
         FOUNDATION, PARTIAL,
         "The Coding Agent opens pull requests faster than the scan cadence, "
         "so the window between introduction and detection widened.",
         "B2.6"),
 Control("F-02", "supply chain",
         "SBOM per build, dependency and licence scanning, provenance on what "
         "ships",
         FOUNDATION, PARTIAL,
         "Two new supply chains: model weights, and a third-party MCP server "
         "CyberTravels does not operate and cannot read.",
         "B2.7"),
 Control("F-03", "environment segregation",
         "production separated from non-production by network, identity and "
         "data, with no shared credentials across the boundary",
         FOUNDATION, ABSENT,
         "The Coding Agent tests in lower environments and opens pull requests "
         "against production. It is the boundary, and it is one identity.",
         "A2.5"),
 Control("F-04", "encryption at rest",
         "storage, database and backup encryption with keys the platform team "
         "does not hold",
         FOUNDATION, IN_PLACE,
         "The vector store is a new data store holding ingested customer "
         "content, and it was not in the original scope.",
         "A3.7"),
 Control("F-05", "encryption in transit",
         "TLS on every hop including service-to-service, with certificate "
         "validation that is not disabled in any environment",
         FOUNDATION, PARTIAL,
         "Agent-to-agent messages and the local std-I/O path are hops nobody "
         "listed when the TLS inventory was taken.",
         "A3.5"),
 Control("F-06", "input validation",
         "schema and length validation on every externally reachable input, "
         "server side, before it reaches business logic",
         FOUNDATION, PARTIAL,
         "The new input is free text whose meaning is the payload. Schema "
         "validation passes it and the model acts on it.",
         "A2.6"),
 Control("F-07", "SDLC and change management",
         "peer review, signed commits, a tested release path and an approval "
         "record for every production change",
         FOUNDATION, PARTIAL,
         "The author of a change is now sometimes a model. Review is the "
         "control, and review capacity is what the volume broke.",
         "B2.0"),
 Control("F-08", "perimeter and DMZ",
         "externally initiated connections terminate in a DMZ; nothing from "
         "outside reaches an internal service directly",
         FOUNDATION, IN_PLACE,
         "Egress is the direction that matters now: an agent with tool access "
         "initiates outbound calls the perimeter was never shaped for.",
         "A3.3"),
 Control("F-09", "credential management",
         "no long-lived secrets in code or configuration, central storage, "
         "rotation on a clock and on departure",
         FOUNDATION, ABSENT,
         "Four agents share one service account, so a rotation breaks all four "
         "and an incident cannot be attributed to one.",
         "A2.1"),
 Control("F-10", "PKI",
         "an issuing hierarchy, certificate lifecycle, and revocation that "
         "actually propagates",
         FOUNDATION, PARTIAL,
         "Workload identity for agents is a PKI problem before it is an AI "
         "problem — attestation needs an issuer somebody trusts.",
         "A2.2"),
 Control("F-11", "key management lifecycle",
         "a KMS with separated duties, documented rotation, and destruction "
         "that is evidenced",
         FOUNDATION, PARTIAL,
         "Signing keys for attestation and for model artefacts join the "
         "lifecycle, and they have different custodians.",
         "B2.18"),
 Control("F-12", "logging and monitoring",
         "centralised, time-synchronised, tamper-evident logs with retention "
         "that outlives an investigation",
         FOUNDATION, PARTIAL,
         "No product in the estate records which prompt caused an action, so "
         "the log answers what happened and not why.",
         "D1.0"),
 # ---- agentic: what the four agents added --------------------------------
 Control("A-01", "workload identity for agents",
         "each agent holds an attested identity, separately revocable",
         AGENTIC, ABSENT,
         "Without it, attribution fails before the incident starts.",
         "A2.1"),
 Control("A-02", "delegated authority that narrows",
         "authority decreases at every hop and the act chain is recorded",
         AGENTIC, ABSENT,
         "An agent acting with more authority than its requester is the "
         "single most common finding.",
         "A2.3"),
 Control("A-03", "just-in-time authorisation",
         "task-scoped grants that expire with the task, never session-long "
         "wildcards",
         AGENTIC, ABSENT,
         "This is what stops an injected instruction reaching refunds.",
         "A2.4"),
 Control("A-04", "provenance at ingress",
         "every span carries its origin, and untrusted spans may not select a "
         "tool",
         AGENTIC, ABSENT,
         "The control that separates instructions from data.",
         "A2.6"),
 Control("A-05", "default-deny on the tool call",
         "adjudicated outside the agent, at the gateway",
         AGENTIC, ABSENT,
         "A model asked to enforce its own policy is subject and guard.",
         "A3.1"),
 Control("A-06", "sandboxed execution",
         "model-authored code runs with no ambient credential and no "
         "filesystem it was not given",
         AGENTIC, PARTIAL,
         "Generated code runs with the runtime's privileges by default.",
         "A3.2"),
 Control("A-07", "egress control",
         "deny-by-default outbound, with an allowlist per agent",
         AGENTIC, ABSENT,
         "Exfiltration by an agent looks like an ordinary API call.",
         "A3.3"),
 Control("A-08", "budgets and stop conditions",
         "a bounded spend, a bounded loop count, and a stop that works",
         AGENTIC, ABSENT,
         "A loop that concludes wrongly does so at machine speed.",
         "A3.4"),
 Control("A-09", "agent telemetry",
         "prompts, tool calls and decisions emitted as traces",
         AGENTIC, ABSENT,
         "Instrumentation you write. No product in the stack emits it.",
         "D1.3"),
 Control("A-10", "human oversight that survives volume",
         "an approval path whose queue does not become a rubber stamp",
         AGENTIC, PARTIAL,
         "Approval fatigue is a control failure, not a staffing problem.",
         "A3.6"),
]

WEIGHT = {IN_PLACE: 1.0, PARTIAL: 0.5, ABSENT: 0.0}


def bar(score: float, width: int = 20) -> str:
    filled = int(round(score * width))
    return "#" * filled + "." * (width - filled)


print("CyberTravels control index — every control the platform needs")
print("=" * 78)
print(f"{'id':6s}{'domain':32s}{'era':12s}{'status':10s}owns")
print("-" * 78)
for c in INDEX:
    print(f"{c.cid:6s}{c.domain[:31]:32s}{c.era:12s}{c.status:10s}{c.owns}")

print()
print("coverage by era")
print("-" * 78)
for era in (FOUNDATION, AGENTIC):
    rows = [c for c in INDEX if c.era == era]
    score = sum(WEIGHT[c.status] for c in rows) / len(rows)
    counts = {s: sum(1 for c in rows if c.status == s)
              for s in (IN_PLACE, PARTIAL, ABSENT)}
    print(f"{era:12s}{bar(score)}  {score:5.0%}  "
          f"{counts[IN_PLACE]} in place, {counts[PARTIAL]} partial, "
          f"{counts[ABSENT]} absent  (n={len(rows)})")

overall = sum(WEIGHT[c.status] for c in INDEX) / len(INDEX)
print(f"{'overall':12s}{bar(overall)}  {overall:5.0%}  (n={len(INDEX)})")

print()
print("the rows with nothing behind them")
print("-" * 78)
absent = [c for c in INDEX if c.status == ABSENT]
for c in absent:
    print(f"  {c.cid}  {c.domain}  ({c.era}, taught in {c.owns})")
    print(f"        needs: {c.control}")
    print(f"        agents change it: {c.agent_note}")

foundation_absent = [c for c in absent if c.era == FOUNDATION]
print()
print("what the index is for")
print("-" * 78)
print(f"{len(INDEX)} controls indexed: {sum(1 for c in INDEX if c.era == FOUNDATION)} "
      f"predate agents entirely, {sum(1 for c in INDEX if c.era == AGENTIC)} arrived "
      f"with them.")
print(f"{len(absent)} have nothing behind them, and {len(foundation_absent)} of those "
      f"are ordinary controls that were")
print("already required before CyberTravels shipped a single agent.")
if foundation_absent:
    print()
    print("An index of only the agentic rows would report "
          f"{sum(WEIGHT[c.status] for c in INDEX if c.era == AGENTIC) / sum(1 for c in INDEX if c.era == AGENTIC):.0%} "
          f"coverage of {sum(1 for c in INDEX if c.era == AGENTIC)} controls")
    print(f"and say nothing about {', '.join(c.cid for c in foundation_absent)} — "
          f"which is where an attacker starts.")
