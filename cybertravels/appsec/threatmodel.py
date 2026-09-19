# step:file C2.2
"""Stage 5 — a threat model derived from the tree, and re-derivable.

Threat models are not wrong because the people writing them are careless. They
are wrong because they are written once, by hand, in a document, against a
system that then changes for eighteen months while the document does not. The
model is accurate on the day of the workshop and decays from that afternoon.

So derive it. Assets from the schema, entry points from the call graph, trust
boundaries from the package layout — every one of them read out of the tree
rather than remembered. What a human then adds is the part a machine cannot
do: which assets matter, and what an attacker would want. That judgement is
worth a workshop. Enumerating the tables is not.

The second function here is the one that earns the stage. `drift()` compares a
model stored earlier against the tree as it stands now, so "the threat model is
out of date" stops being a feeling somebody has in a review and becomes a list
of the entry points that appeared since.
"""
import ast
import json
import re
from pathlib import Path

# Tables are found by reading the schema rather than by importing the module,
# so this works on a checkout whose dependencies are not installed.
_TABLE = re.compile(r"CREATE TABLE IF NOT EXISTS (\w+)")

# What an attacker wants, per asset. The one column a machine cannot fill in —
# it is a business judgement, and leaving it blank is how a derived model ends
# up technically complete and useless.
ASSET_VALUE = {
    "bookings": "somebody else's itinerary: where a named person will be, when",
    "payments": "card handles and the refund path",
    "refunds": "the money path — the only table where a write costs cash",
    "audit": "the record of what happened; valuable to change, not to read",
    "memory": "what the agent remembers about a traveller, across sessions",
    "run_artefacts": "what one run touched; the surface B3.8 is about",
}


def assets(root):
    """Every table the schema creates, with what an attacker would want."""
    text = (Path(root) / "db.py").read_text()
    return [{"asset": t, "kind": "table",
             "why_an_attacker_cares": ASSET_VALUE.get(
                 t, "UNCLASSIFIED — nobody has said what this is worth, which "
                    "is itself the finding")}
            for t in sorted(set(_TABLE.findall(text)))]


# Which shapes are entry points. Defined here because this is the stage that
# has to decide it, and inherited by C2.5's call graph — that stage starts its
# walk from this set rather than deciding the question a second time. Two
# stages with their own idea of where the system begins is two stages that
# disagree without either of them being wrong.
ENTRY_DECORATORS = ("route", "tool")


def is_entry_point(node, rel):
    """An entry point is something outside the process can start.

    Three shapes in this tree: a `@route` handler, an agent's `handle`, and an
    MCP tool. Named explicitly rather than inferred — an inferred entry-point
    set is one nobody can review, and getting it wrong silently makes the
    whole system look unreachable.
    """
    for d in node.decorator_list:
        name = d.func.id if isinstance(d, ast.Call) and \
            isinstance(d.func, ast.Name) else getattr(d, "id", "")
        if name in ENTRY_DECORATORS:
            return True
    if node.name == "handle" and rel.startswith("agents/"):
        return True
    return rel.startswith("mcp/") and not node.name.startswith("_")


def entry_points(root, parts=("ingress", "agents", "mcp")):
    """Where untrusted input enters, read out of the tree.

    A local property — this decorator, that filename — so it needs no call
    graph and arrives three lessons before one exists.
    """
    root = Path(root)
    out = []
    for part in parts:
        d = root / part
        if not d.exists():
            continue
        for path in sorted(d.rglob("*.py")):
            rel = str(path.relative_to(root))
            try:
                tree = ast.parse(path.read_text())
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and is_entry_point(node, rel):
                    out.append({"unit": node.name, "file": rel,
                                "channel": _channel(rel)})
    return sorted(out, key=lambda e: (e["file"], e["unit"]))


def _channel(rel):
    if rel.startswith("ingress/"):
        return "HTTP — a person or a vendor webhook"
    if rel.startswith("mcp/"):
        return "MCP — a tool call the model chose"
    if rel.startswith("agents/"):
        return "agent-to-agent — a peer's message"
    return "internal"


def boundaries(root):
    """Trust boundaries, as the packages actually draw them.

    Read from the layout because that is where they really are. A boundary in
    a diagram and no boundary in the import graph is a diagram.
    """
    out = []
    for d in sorted(p for p in Path(root).iterdir() if p.is_dir()):
        if d.name.startswith((".", "__")) or d.name in ("data", "static"):
            continue
        out.append({"package": d.name, "trust": _trust(d.name)})
    return out


def _trust(pkg):
    return {
        "ingress": "0 — whatever arrived",
        "agents": "1 — a model's output, which is data not instruction",
        "a2a": "1 — a peer, signed but not trusted",
        "mcp": "2 — a boundary that refuses its own caller",
        "orchestrator": "2 — holds the policy the model never sees",
        "tools": "3 — the only things that change anything",
        "appsec": "3 — reads the tree; ships with it, and is scanned by it",
    }.get(pkg, "3 — ours")


def build(root):
    return {"assets": assets(root), "entry_points": entry_points(root),
            "boundaries": boundaries(root)}


def drift(stored, root):
    """What changed since the model was written. The stage's Day 2 number.

    Reported in both directions. An entry point that appeared is the obvious
    one; an asset that vanished matters too, because a model still protecting
    it is a model somebody is reading.
    """
    now = build(root)
    was_entries = {(e["unit"], e["file"]) for e in stored.get("entry_points", [])}
    now_entries = {(e["unit"], e["file"]) for e in now["entry_points"]}
    was_assets = {a["asset"] for a in stored.get("assets", [])}
    now_assets = {a["asset"] for a in now["assets"]}
    return {
        "entry_points_added": sorted(now_entries - was_entries),
        "entry_points_gone": sorted(was_entries - now_entries),
        "assets_added": sorted(now_assets - was_assets),
        "assets_gone": sorted(was_assets - now_assets),
        "unclassified_assets": sorted(
            a["asset"] for a in now["assets"]
            if a["why_an_attacker_cares"].startswith("UNCLASSIFIED")),
        "stale": bool(now_entries ^ was_entries or now_assets ^ was_assets),
    }


def as_json(root):
    return json.dumps(build(root), indent=2, sort_keys=True)
