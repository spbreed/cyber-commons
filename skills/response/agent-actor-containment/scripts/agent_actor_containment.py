#!/usr/bin/env python3
"""Establish what a human's account being disabled does not stop, and separate a task the user authorised from the actions taken under it.

This is the executable half of the `agent-actor-containment` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
from dataclasses import dataclass, field

@dataclass
class Session:
    actor: str; token_issued: float; token_ttl: float; account_enabled: bool = True
    identity_revoked: bool = False
    def can_act(self, at):
        if self.identity_revoked: return False, "identity revoked"
        if at - self.token_issued > self.token_ttl: return False, "token expired"
        if not self.account_enabled:
            return True, "account disabled, but the issued token is still valid"
        return True, "active"

now = time.time()
SESSIONS = {
 "dana@corp (human)":  Session("dana@corp", now-60, 3600),
 "patch-agent":        Session("patch-agent", now-60, 3600),
 "deploy-agent":       Session("deploy-agent", now-60, 3600),
}
print("INSTINCT 1 — disable dana@corp's account")
for s in SESSIONS.values(): s.account_enabled = (s.actor != "dana@corp")
for name, s in SESSIONS.items():
    ok, why = s.can_act(now)
    print(f"   {name:22s} can act: {str(ok):5s}  {why}")
print("   → the agents were never using her account interactively; they hold")
print("     their own issued tokens, and one of them is acting AS her.")

print("\nINSTINCT 2 — interview the user")
INTERVIEW = {
 "did you read the AWS credentials?":       "No. I opened a ticket and went to lunch.",
 "what did you ask the agent to do?":       "Fix the finding in billing.py.",
 "did you approve the external POST?":      "I didn't know it made external calls.",
}
for q, a in INTERVIEW.items():
    print(f"   Q: {q}\n   A: {a}")
print("   → she authorised a TASK. The actions were chosen by a model. She is")
print("     not withholding information; she does not have it.")

print("\nINSTINCT 3 — assume one actor")
CHAIN = ["dana@corp", "orchestrator", "patch-agent"]
print(f"   actual chain: {' → '.join(CHAIN)}")
print(f"   actors involved: {len(CHAIN)}; actors in the logs: 1")

class Registry:
    def __init__(self):
        self.revoked = set()
    def revoke(self, actor):
        self.revoked.add(actor); return actor
    def valid(self, session):
        return session.actor not in self.revoked

reg = Registry()
for s in SESSIONS.values(): s.account_enabled = True   # undo instinct 1

print("correct first action — revoke patch-agent's identity:")
reg.revoke("patch-agent")
SESSIONS["patch-agent"].identity_revoked = True
for name, s in SESSIONS.items():
    ok, why = s.can_act(now)
    print(f"   {name:22s} can act: {str(ok):5s}  {why}")
print("\n   dana keeps working. deploy-agent keeps working. The actor stopped.")

print("\nTIME TO EFFECT, measured:")
LEVERS = {"disable the human's account": (5,  "agent unaffected"),
          "kill the agent process":      (2,  "supervisor restarts it; token still valid"),
          "revoke the agent identity":   (12, "agent cannot act, even after restart"),
          "rotate the shared credential":(420,"works, and breaks every other consumer")}
for lever, (secs, note) in LEVERS.items():
    print(f"   {lever:32s}{secs:>5}s  {note}")
assert not SESSIONS["patch-agent"].can_act(now)[0]
assert SESSIONS["deploy-agent"].can_act(now)[0]
