#!/usr/bin/env python3
"""Exercise a tool at the widest scope it was ever granted, with the right identity and well-formed arguments.

This is the executable half of the `tool-scope-abuse-probe` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

DB = {"users":    [{"id": 1, "email": "alice@corp.example"}],
      "invoices": [{"id": 7, "amount": 120}],
      "secrets":  [{"id": 1, "value": "prod-signing-key"}]}

def run_query(sql):
    """One database tool. Scoped for the hardest job any caller ever has:
    the nightly reconciliation job needs to read everything."""
    table = sql.split("FROM ")[-1].split()[0]
    if sql.startswith("DELETE"):
        removed, DB[table] = len(DB[table]), []
        return {"deleted": removed, "table": table}
    return {"rows": DB.get(table, [])}

TOOLS = {"run_query": run_query}

def agent(request):
    """The runtime turns a request into a tool call. Nothing here is broken."""
    if "how many invoices" in request:
        return TOOLS["run_query"]("SELECT * FROM invoices")
    if "clean up" in request:
        return TOOLS["run_query"]("DELETE FROM " + request.split("clean up ")[1])
    if "signing key" in request:
        return TOOLS["run_query"]("SELECT * FROM secrets")
    return {"rows": []}

print("intended use:")
print(f"   how many invoices  -> {agent('how many invoices are open?')}")
print("\nsame tool, same identity, same well-formed arguments:")
print(f"   signing key        -> {agent('what is the prod signing key?')}")
print(f"   clean up secrets   -> {agent('clean up secrets')}")
print(f"\nsecrets table now: {DB['secrets']}")
print()
print("No exploit. The tool did exactly what it was built to do. It was scoped")
print("for the nightly reconciliation job, and every caller inherited that")
print("scope - including the one steered by a poisoned ticket in A1.3.")
assert DB["secrets"] == []
