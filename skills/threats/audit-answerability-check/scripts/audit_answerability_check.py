#!/usr/bin/env python3
"""Put the three questions an investigation asks to a complete-looking tool-call log.

This is the executable half of the `audit-answerability-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

LOG = [
 {"ts": "09:14:02", "actor": "agent-svc", "tool": "search",     "args": {"q": "invoice 8812"}},
 {"ts": "09:14:07", "actor": "agent-svc", "tool": "fetch_doc",  "args": {"id": "wiki/473"}},
 {"ts": "09:14:11", "actor": "agent-svc", "tool": "run_query",  "args": {"sql": "DELETE FROM invoices WHERE id=8812"}},
 {"ts": "09:14:12", "actor": "agent-svc", "tool": "send_email", "args": {"to": "ops@corp.example"}},
]

print("the log you have:")
for e in LOG:
    print(f"   {e['ts']}  {e['actor']:10s}{e['tool']:12s}{e['args']}")

QUESTIONS = {
 "which user caused the deletion?":            "principal",
 "what made the agent decide to delete?":      "motivating_input",
 "which agent in the chain originated it?":    "delegation_chain",
}
print()
print(f"{'question':44s}{'field needed':20s}present?")
answerable = 0
for q, field in QUESTIONS.items():
    present = any(field in e for e in LOG)
    answerable += present
    print(f"{q:44s}{field:20s}{'yes' if present else 'NO'}")

print(f"\nquestions answerable from this log: {answerable}/{len(QUESTIONS)}")
print()
print("The log is not broken. It is complete for debugging and empty for")
print("investigation, and the difference is three fields nobody was asked for.")
print()
print("One more: agent-svc holds db:admin. The log store is a database.")
print("A record the actor can edit is not evidence of anything.")
assert answerable == 0
