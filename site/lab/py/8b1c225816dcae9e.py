"""The sensor estate, measured against what the agent actually does.

Four products are bought — EDR, DLP, CSPM, CNAPP — the estate is declared
covered, and the coverage report is built the way coverage reports are always
built: per product, against that product's own feature list. Every row is
green and the agent's whole working day falls between them.

The fix is to change the denominator. Coverage is not "which sensors are
deployed"; it is **which of the actions this agent can take is any sensor in a
position to see.** That list is not a guess — it comes out of the tree.
`config.TOOL_POLICY` says which tools exist, and `redteam.containment.PATHS`
says which routes an action can take. Enumerate those, ask each sensor what it
observes, and the uncovered rows are named rather than counted.

The named rows are the deliverable. "83% covered" is a number that ends a
conversation; "nothing observes a delegated token being minted for
payments:refund" starts one.
"""
from .. import config


class Sensor:
    """One product, and what it is actually in a position to observe.

    `observes` is expressed as the *kind* of event, not the vendor's feature
    name. A feature list is a marketing document and mapping it to an agent's
    behaviour is the work this class exists to make somebody do.
    """

    __slots__ = ("name", "observes", "blind_to")

    def __init__(self, name, observes, blind_to=""):
        self.name = name
        self.observes = set(observes)
        self.blind_to = blind_to

    def sees(self, event_kind):
        return event_kind in self.observes


# The estate as CyberTravels buys it. Each `blind_to` is the sentence the
# vendor would agree with and the coverage report never contains.
ESTATE = [
    Sensor("EDR", {"process", "shell", "file-read", "file-write"},
           "anything that happens inside one process — a tool call is a "
           "function call, and a function call is not an event"),
    Sensor("DLP", {"egress-content", "file-write"},
           "a payload that leaves through an allowed vendor API, which is "
           "every payload this agent sends"),
    Sensor("CSPM", {"cloud-config"},
           "runtime behaviour entirely; it reads configuration"),
    Sensor("CNAPP", {"process", "cloud-config", "network-flow"},
           "the identity a flow was made under — it sees the connection, not "
           "the delegation chain behind it"),
    Sensor("agent telemetry", {"span", "token-mint", "tool-call", "approval",
                               "memory-write", "a2a-message"},
           "nothing, and it is the one nobody onboarded — E1.3"),
]


def actions():
    """Everything this agent can do, derived from the tree rather than listed.

    A hand-written action list is a list of the actions somebody remembered,
    and the ones that get forgotten are the ones with no sensor on them.
    """
    out = [{"action": f"tool:{tool}", "kind": "tool-call",
            "detail": f"{rule['scope']} via {rule['audience']}"}
           for tool, rule in sorted(config.TOOL_POLICY.items())]
    out += [
        {"action": "mint a delegated token", "kind": "token-mint",
         "detail": "RFC 8693 exchange — the moment authority is created"},
        {"action": "ask for human approval", "kind": "approval",
         "detail": "the gate A1.7 built"},
        {"action": "write to memory", "kind": "memory-write",
         "detail": "what the next run will read as context"},
        {"action": "message a peer agent", "kind": "a2a-message",
         "detail": "a hop that appears in no product's model"},
        {"action": "reach a shell", "kind": "shell",
         "detail": "agents/coding_agent.py::_open_branch"},
        {"action": "read an invoice", "kind": "file-read",
         "detail": "tools/payments_api.py::download_invoice"},
        {"action": "call a vendor API", "kind": "egress-content",
         "detail": "an allowed destination, per B3.3"},
    ]
    return out


def matrix(estate=None, without=()):
    """Per action, which sensors can see it. Uncovered rows come back named.

    `without` drops sensors, which is how the lesson is demonstrated: run it
    with the agent telemetry source excluded and most of the agent's day
    becomes invisible, which is the estate as most teams actually have it.
    """
    estate = [s for s in (estate or ESTATE) if s.name not in without]
    rows = []
    for act in actions():
        seen_by = [s.name for s in estate if s.sees(act["kind"])]
        rows.append({**act, "seen_by": seen_by, "covered": bool(seen_by)})
    uncovered = [r for r in rows if not r["covered"]]
    return {
        "actions": len(rows),
        "covered": len(rows) - len(uncovered),
        "coverage": round((len(rows) - len(uncovered)) / len(rows), 3),
        # The deliverable. Not a percentage — the sentences.
        "uncovered_actions": [r["action"] for r in uncovered],
        "rows": rows,
    }


def blind_spots(estate=None):
    """What each product cannot see, in its own row, stated plainly."""
    return [{"sensor": s.name, "blind_to": s.blind_to}
            for s in (estate or ESTATE)]


# --------------------------------------------------------------------------- #
# E1.2 — behaviour that changes with no code change
# --------------------------------------------------------------------------- #
# The detection that worked last month degraded and nothing in the change log
# explains it, because none of the things that changed go through change
# management. A model version, a system prompt, a retrieval index, an MCP tool
# description: every one of them alters what the agent does, and not one is a
# commit against this repository.
#
# So baseline the surfaces themselves and diff them. The finding is not "the
# rule got worse" — it is "these four surfaces moved and three of them have no
# approver".
DRIFT_SURFACES = {
    "model_version": ("the vendor's, changed on their schedule", False),
    "system_prompt": ("cybertravels/runtime.py::_system_prompt", True),
    "tool_policy": ("cybertravels/config.py::TOOL_POLICY", True),
    "retrieval_index": ("knowledge/retriever.py::CORPUS — anyone who can add "
                        "a template", False),
    "mcp_tool_descriptions": ("the vendor server's, rewritable after you "
                              "approved them — B1.9", False),
    "memory": ("what previous runs wrote", False),
}


def baseline(state):
    """Snapshot the surfaces that change behaviour. `state` is a dict of
    surface -> a digestible value."""
    return {k: state.get(k) for k in DRIFT_SURFACES}


def drift(was, now):
    """What moved, and — the column that makes this a finding — whether
    anything approved it."""
    moved = []
    for surface, (where, managed) in DRIFT_SURFACES.items():
        if was.get(surface) != now.get(surface):
            moved.append({"surface": surface, "where": where,
                          "change_managed": managed,
                          "was": was.get(surface), "now": now.get(surface)})
    unmanaged = [m["surface"] for m in moved if not m["change_managed"]]
    return {"moved": moved, "count": len(moved),
            "outside_change_management": unmanaged,
            "why": "a detection degrades when any of these move; only the "
                   "managed ones leave a record somebody reviews"}


