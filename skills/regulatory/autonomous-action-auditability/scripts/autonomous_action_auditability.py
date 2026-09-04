#!/usr/bin/env python3
"""Decide whether an audit record makes an autonomous action answerable, and show a complete, consistent, false record.

This is the executable half of the `autonomous-action-auditability` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import time
from dataclasses import dataclass, field

@dataclass
class Token:
    sub: str; actor: str; scopes: set; act: dict = None
    def chain(self):
        out, node = [], self.act
        while node: out.append(node["actor"]); node = node.get("act")
        c = list(reversed(out)) + [self.actor]
        if c[0] != self.sub: c.insert(0, self.sub)
        return c

@dataclass
class Replay:
    prompts: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)
    model_version: str = ""
    seed: object = None
    def replayable(self):
        missing = [n for n, v in (("prompts", self.prompts),
                                  ("tool results", self.tool_results),
                                  ("model version", self.model_version),
                                  ("seed", self.seed is not None)) if not v]
        return (not missing), missing

def audit_record(action, token, replay):
    ok, missing = replay.replayable()
    return {"action": action,
            "acting_identity": token.actor,
            "on_behalf_of": token.sub,
            "chain": " → ".join(token.chain()),
            "scopes_held": sorted(token.scopes),
            "replayable": ok,
            "replay_gaps": missing,
            "answerable": token.actor != token.sub and ok}

GOOD_TOKEN = Token("dana@corp", "patch-agent", {"repo:read", "repo:write"},
                   {"actor": "orchestrator", "act": None})
GOOD_REPLAY = Replay(["fix SEC-4471"], ["file contents…"], "glm-4.6@2026-07-14", 42)

r = audit_record("merge_pr #8812", GOOD_TOKEN, GOOD_REPLAY)
for k, v in r.items(): print(f"{k:18s}{v}")

IMPERSONATED = Token("dana@corp", "dana@corp", {"repo:write"}, None)
NO_REPLAY    = Replay(["fix SEC-4471"], ["file contents…"], "", None)

CASES = {
 "complete":                     (GOOD_TOKEN,  GOOD_REPLAY),
 "attribution broken":           (IMPERSONATED, GOOD_REPLAY),
 "replay incomplete":            (GOOD_TOKEN,  NO_REPLAY),
 "neither":                      (IMPERSONATED, NO_REPLAY),
}
print(f"{'case':22s}{'who acted':14s}{'replayable':12s}{'answerable':>12}")
print("-" * 62)
for name, (tok, rep) in CASES.items():
    r = audit_record("merge_pr #8812", tok, rep)
    print(f"{name:22s}{r['acting_identity']:14s}{str(r['replayable']):12s}"
          f"{str(r['answerable']):>12}")

r = audit_record("merge_pr #8812", IMPERSONATED, GOOD_REPLAY)
print(f"\nattribution-broken record: acting_identity={r['acting_identity']}")
print("The record is complete, internally consistent, and false. It says a human")
print("merged a pull request she never saw.")
assert not r["answerable"]

def auditability_drill(records, sample_size=3):
    """Pick actions at random and try to produce the full record for each."""
    results = []
    for i, (action, tok, rep) in enumerate(records[:sample_size], 1):
        r = audit_record(action, tok, rep)
        gaps = []
        if r["acting_identity"] == r["on_behalf_of"]:
            gaps.append("acting identity not distinguishable from the principal")
        gaps += [f"replay missing {m}" for m in r["replay_gaps"]]
        results.append({"n": i, "action": action, "complete": not gaps, "gaps": gaps})
    passed = sum(r["complete"] for r in results)
    return results, passed, len(results)

SAMPLE = [
 ("merge_pr #8812", GOOD_TOKEN, GOOD_REPLAY),
 ("deploy prod",    IMPERSONATED, GOOD_REPLAY),
 ("rotate secret",  GOOD_TOKEN, NO_REPLAY),
]
rows, passed, total = auditability_drill(SAMPLE)
for r in rows:
    print(f"{r['n']}. {r['action']:18s}{'COMPLETE' if r['complete'] else 'INCOMPLETE'}")
    for g in r["gaps"]: print(f"      ⚠ {g}")
print(f"\nauditability: {passed}/{total} sampled actions fully answerable "
      f"({passed/total:.0%})")
print("\nRun this as a drill, quarterly, on randomly chosen production actions.")
print("The percentage is the number that goes in the evidence pack — and it is")
print("far more persuasive than a statement that logging is comprehensive.")
assert passed < total
