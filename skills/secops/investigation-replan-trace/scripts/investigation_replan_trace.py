#!/usr/bin/env python3
"""Run an investigation that must abandon its first hypothesis, and show the replan in the trace.

This is the executable half of `investigation-replan-trace`. The failure it
exists for is not the agent being wrong at step one — everyone is wrong at step
one. It is the agent staying wrong: gathering evidence for a hypothesis the
evidence has already refuted, because nothing forced it to reconsider.

Standard library only, and deterministic.
"""

# Evidence arrives in order. Some of it refutes the working hypothesis.
EVIDENCE = [
    ("gateway", "refund issued for BK-772 at 03:14", {"agent-misuse", "credential-theft"}),
    ("traces",  "the refund came from the workflow agent's session", {"agent-misuse"}),
    ("iam",     "that session was opened by SPIFFE id, not a human login", {"agent-misuse"}),
    ("traces",  "the agent's plan for that run contains no refund step", set()),
    ("mcp",     "the vendor MCP server returned a tool description naming a refund",
     {"indirect-injection"}),
    ("corpus",  "that description changed 40 minutes before the run", {"indirect-injection"}),
]

HYPOTHESES = ["agent-misuse", "credential-theft", "indirect-injection"]
plan = "agent-misuse"          # where an analyst starts: the agent did it
alive = set(HYPOTHESES)

print(f"opening hypothesis: {plan}")
print()
report = {"steps": [], "replans": 0, "final": None}
for i, (source, fact, supports) in enumerate(EVIDENCE, 1):
    before = plan
    if supports:
        alive &= supports if plan in supports else alive
        alive = {h for h in alive if h in supports} or alive
    refuted = bool(supports) and plan not in supports
    note = ""
    if refuted:
        # Step 3 — the trigger. The plan changes, and the abandoned branch is named.
        plan = sorted(supports)[0]
        report["replans"] += 1
        note = f"  REPLAN {before} -> {plan}"
    elif not supports:
        note = "  (neutral — refutes nothing, so nothing changes)"
    print(f"{i}. {source:<9}{fact}")
    if note:
        print(f"   {note.strip()}")
    report["steps"].append({"n": i, "source": source, "fact": fact,
                            "hypothesis_before": before, "hypothesis_after": plan,
                            "replanned": refuted})
report["final"] = plan
print()
print(f"{report['replans']} replan(s) · final hypothesis: {report['final']}")
print()
print("Step 4 is the one that matters and the one an eager investigator skips.")
print("'the agent's plan contains no refund step' supports nothing - it is not")
print("evidence FOR another hypothesis, it is evidence AGAINST the current one.")
print("An agent scoring only support will read it as noise and carry on.")
print()
print("Step 5 is what actually moves the investigation, and it moves it away from")
print("the agent entirely: the instruction came from a vendor's tool description.")
print("The abandoned branch stays in the trace. A reviewer needs to see that")
print("agent-misuse was considered and dropped, not that it was never thought of.")

assert report["replans"] >= 1, "an investigation that never replans is not one"
assert report["final"] == "indirect-injection"
assert any(s["fact"].startswith("the agent's plan") for s in report["steps"])
