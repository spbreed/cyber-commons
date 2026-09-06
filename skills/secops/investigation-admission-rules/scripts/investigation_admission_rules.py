#!/usr/bin/env python3
"""Enforce an admission set on an investigating agent's queries, and record every refusal.

This is the executable half of `investigation-admission-rules`. An investigating
agent is granted broad read access to find a problem, and broad read access to
everything is what the incident was about. The admission set is decided per
investigation class, before the investigation starts.

Standard library only, and deterministic.
"""

# What this class of investigation may touch. Declared first, not inferred.
ADMISSION = {
    "agent-misuse": {
        "sources": {"agent.traces", "gateway.logs", "tool.audit"},
        "fields_denied": {"payment_card", "passport_no", "message_body"},
        "max_rows": 5000,
    }
}

QUERIES = [
    ("agent.traces",   ["agent", "tool", "ts"],                 400),
    ("gateway.logs",   ["src", "route", "ts"],                 1200),
    ("tool.audit",     ["tool", "arg", "ts"],                   300),
    ("bookings.db",    ["owner_id", "payment_card"],           8000),   # not admitted
    ("agent.traces",   ["agent", "message_body"],               900),   # denied field
    ("gateway.logs",   ["src", "route"],                      90000),   # over the cap
]

rule = ADMISSION["agent-misuse"]
print("investigation class: agent-misuse")
print(f"   sources admitted : {', '.join(sorted(rule['sources']))}")
print(f"   fields denied    : {', '.join(sorted(rule['fields_denied']))}")
print(f"   row cap          : {rule['max_rows']}")
print()

report = {"allowed": [], "refused": []}
print(f"{'source':<16}{'fields':<34}{'rows':>7}  outcome")
for source, fields, rows in QUERIES:
    why = None
    if source not in rule["sources"]:
        why = "source not admitted for this class"
    elif set(fields) & rule["fields_denied"]:
        bad = ", ".join(sorted(set(fields) & rule["fields_denied"]))
        why = f"denied field: {bad}"
    elif rows > rule["max_rows"]:
        why = f"{rows} rows exceeds the {rule['max_rows']} cap"
    out = "allow" if why is None else f"REFUSE — {why}"
    print(f"{source:<16}{','.join(fields):<34}{rows:>7}  {out}")
    (report["allowed"] if why is None else report["refused"]).append(
        {"source": source, "fields": fields, "rows": rows, "why": why})
print()
print(f"{len(report['allowed'])} allowed · {len(report['refused'])} refused")
print()
print("Every refusal is a record, not a silent drop. That matters twice: the")
print("investigator can ask a human for a grant with the exact query attached,")
print("and the refusals are themselves evidence that the investigation did not")
print("become the second incident.")
print()
print("Note the third refusal. Nothing about it is sensitive - it is the same")
print("source and the same fields as an allowed query. It is refused on volume,")
print("because 90,000 rows is not an investigation, it is a copy.")

assert len(report["refused"]) == 3
assert any("denied field" in (r["why"] or "") for r in report["refused"])
assert any("cap" in (r["why"] or "") for r in report["refused"])
