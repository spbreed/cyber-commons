#!/usr/bin/env python3
"""Count the change surfaces that bypass change management and check which post-incident actions are still verifiable weeks later.

This is the executable half of the `post-incident-change-surface` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n, s, rev in tools if n not in gated)

BEFORE = [("read_file", "self", True), ("write_file", "project", True),
          ("http_post", "org", False)]
AFTER  = [("read_file", "self", True), ("write_file", "project", True),
          ("http_post", "org", False)]
gated_after = {"http_post"}

print(f"blast before {blast(BEFORE)}  after {blast(AFTER, gated_after)}")
print("the manifest diff records the change even though no PR was raised.\n")

def action_record(action, surface, control_type, owner, verify_by):
    is_control = control_type in ("preventive", "detective")
    return {"action": action, "surface": surface, "type": control_type,
            "owner": owner, "verify_by": verify_by,
            "acceptable": is_control and bool(owner) and bool(verify_by)}

RECORDS = [
 action_record("gate http_post behind approval", "tool manifest", "preventive",
               "platform-sec", "2026-09-30"),
 action_record("alert on credential-path reads", "detection", "detective",
               "soc", "2026-09-15"),
 action_record("update the prompt to warn the model", "prompt", "guidance",
               "", ""),
]
for r in RECORDS:
    print(f"{'OK  ' if r['acceptable'] else 'WEAK'} {r['action']:42s}"
          f"type={r['type']:11s} owner={r['owner'] or '—':14s} verify_by={r['verify_by'] or '—'}")
weak = [r for r in RECORDS if not r["acceptable"]]
print(f"\n{len(weak)} action(s) are guidance rather than controls: "
      f"{[r['action'] for r in weak]}")
assert weak
