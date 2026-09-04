#!/usr/bin/env python3
"""Put the four investigation questions to one ledger entry, and try to amend the record as the agent.

This is the executable half of the `attribution-ledger-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

LEDGER = []          # append-only, and the agent holds no credential for it

def record(principal, workload, instance, chain, action, motivating):
    LEDGER.append({
        "principal": principal, "workload": workload, "instance": instance,
        "chain": list(chain), "action": action,
        "motivating_input": motivating["text"][:44],
        "input_origin": motivating["origin"],
    })

def agent_writes(entry):
    """The agent tries to amend the record."""
    raise PermissionError("ledger is append-only and out of the agent's trust domain")

record("dana@corp", "spiffe://corp/reports-agent", "run-8812",
       ["dana@corp", "orchestrator", "reports-agent"],
       "run_query DELETE FROM invoices WHERE id=8812",
       {"text": "wiki/473: retire invoice 8812 when the customer closes", "origin": "knowledge"})

QUESTIONS = {
 "which user caused the deletion?":         lambda e: e["principal"],
 "what performed it?":                      lambda e: f"{e['workload']} ({e['instance']})",
 "how did authority reach it?":             lambda e: " -> ".join(e["chain"]),
 "what made the agent decide?":             lambda e: f"{e['motivating_input']!r} from {e['input_origin']}",
}
e = LEDGER[0]
for q, answer in QUESTIONS.items():
    print(f"   {q:36s}{answer(e)}")

print(f"\nquestions answerable: {len(QUESTIONS)}/{len(QUESTIONS)}")
print()
print(f"input origin was {e['input_origin']!r} - a trust-0 component. That single")
print("field turns 'the agent deleted an invoice' into 'a wiki page told it to',")
print("which is a root cause rather than an observation.")

try:
    agent_writes({"action": "tidy up"})
except PermissionError as err:
    print(f"\nagent attempting to amend the ledger: refused ({err})")
assert len(LEDGER) == 1 and LEDGER[0]["input_origin"] == "knowledge"
