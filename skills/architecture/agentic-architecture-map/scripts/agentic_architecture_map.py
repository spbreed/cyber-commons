#!/usr/bin/env python3
"""Draw CyberTravels as nine components, mark every edge where trust changes, and name the boxes that do not exist.

This is the executable half of the `agentic-architecture-map` skill. The
crossings are derived from the trust levels rather than listed: change a level
in COMPONENTS below and the count changes with it, which is the property that
makes the map arguable rather than decorative.

It also emits the map as Graphviz DOT, so the picture on the lesson page is
rendered from this data by the real `dot` binary rather than drawn by hand.

Standard library only, and deterministic.
"""

from cyber_commons_skill_runtime import dot_graph, emit_diagram

# Step 1 — all nine, present or not. An absent box is a decision, not a gap.
# (trust level, holds authority, present at CyberTravels)
COMPONENTS = {
    "ingress":       (0, False, True),   # traveller text, unauthenticated
    "orchestrator":  (2, False, True),
    "agent runtime": (2, True,  True),   # the loop that turns text into action
    "model":         (1, False, True),   # holds no credential, opens no socket
    "tools":         (3, True,  True),
    "mcp servers":   (1, True,  True),   # a third party's process, in your context
    "knowledge":     (0, False, True),   # retrieved text nobody on staff wrote
    "messaging":     (2, False, True),
    "egress":        (3, True,  False),  # CyberTravels has no gateway yet
}

# Step 2 — data flow, not call direction. Step 4 — what crosses.
EDGES = [
    ("ingress",       "orchestrator",  ["traveller text"]),
    ("orchestrator",  "agent runtime", ["task", "conversation"]),
    ("knowledge",     "agent runtime", ["retrieved documents"]),
    ("agent runtime", "model",         ["assembled context"]),
    ("model",         "agent runtime", ["proposed tool call"]),
    ("agent runtime", "tools",         ["arguments", "credentials"]),
    ("agent runtime", "mcp servers",   ["arguments", "credentials"]),
    ("mcp servers",   "agent runtime", ["tool results", "tool descriptions"]),
    ("tools",         "agent runtime", ["tool results"]),
    ("agent runtime", "messaging",     ["peer messages"]),
    ("messaging",     "agent runtime", ["peer messages"]),
]

present = {c for c, (_, _, p) in COMPONENTS.items() if p}
absent = sorted(c for c, (_, _, p) in COMPONENTS.items() if not p)

print(f"{len(COMPONENTS)} components, {len(present)} present at CyberTravels")
print(f"   {'component':<16}{'trust':>6}{'authority':>11}  present")
for name in sorted(COMPONENTS):
    trust, auth, is_present = COMPONENTS[name]
    print(f"   {name:<16}{trust:>6}{'yes' if auth else '-':>11}  "
          f"{'yes' if is_present else 'NO'}")
print()

# Step 3 — a crossing is an edge from a lower trust level to a higher one.
report = {"components": [], "edges": [], "absent": absent}
for name in sorted(COMPONENTS):
    trust, auth, is_present = COMPONENTS[name]
    report["components"].append({"name": name, "present": is_present,
                                 "trust": trust, "holds_authority": auth})

crossings = []
for src, dst, carries in EDGES:
    if src not in present or dst not in present:
        continue
    crossing = COMPONENTS[src][0] < COMPONENTS[dst][0]
    report["edges"].append({"from": src, "to": dst, "carries": carries,
                            "boundary_crossing": crossing})
    if crossing:
        crossings.append((src, dst, carries))
report["crossings"] = len(crossings)

print(f"{len(crossings)} trust-boundary crossing(s) — always more than expected")
for src, dst, carries in crossings:
    print(f"   {src:<16} -> {dst:<16}{COMPONENTS[src][0]}->{COMPONENTS[dst][0]}"
          f"   carries {', '.join(carries)}")
print()
print("Two of those carry content nobody on staff wrote — traveller text and")
print("retrieved documents — into a component that holds authority. Every")
print("injection risk in Function A is one of those two edges.")
print()

# Step 5 — name what is missing. A control for a component nobody has is a
# conversation nobody needs.
print(f"absent: {', '.join(absent)}")
print("CyberTravels has no egress gateway, so 'route it through the gateway' is")
print("not a control it can apply yet. Saying that here stops the argument")
print("later.")
print()

KIND = {}
for name, (trust, auth, is_present) in COMPONENTS.items():
    if not is_present:
        KIND[name] = "dead"
    elif trust == 0:
        KIND[name] = "entry"
    elif auth:
        KIND[name] = "sink"
    else:
        KIND[name] = "unit"

nodes = {n: {"label": f"{n}\\ntrust {COMPONENTS[n][0]}", "kind": KIND[n]}
         for n in COMPONENTS}
edges = [(s, d, "BOUNDARY" if COMPONENTS[s][0] < COMPONENTS[d][0] else "")
         for s, d, _ in EDGES]
emit_diagram("a-architecture-map",
             dot=dot_graph("architecture", nodes, edges,
                           legend_labels={"entry": "trust 0 — content from outside",
                                          "unit": "no authority",
                                          "sink": "holds authority",
                                          "dead": "not built yet"}))
print()
print("Red is trust 0 — content from outside. Orange holds authority. Dashed is")
print("a component CyberTravels does not have. Every BOUNDARY edge is a risk in")
print("Function A, and there are more of them than the picture suggests until")
print("the levels are written down.")

assert report["crossings"] >= 2, "a map with no crossings has the levels wrong"
assert absent, "name what is missing, or the map implies it exists"
assert any(e["boundary_crossing"] and "retrieved documents" in e["carries"]
           for e in report["edges"]), "the indirect-injection edge must cross"
