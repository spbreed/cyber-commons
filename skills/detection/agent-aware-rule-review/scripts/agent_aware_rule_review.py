#!/usr/bin/env python3
"""Run classic detection rules against an agent doing its job, and measure behavioural drift against a signed-off baseline.

This is the executable half of the `agent-aware-rule-review` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

import statistics, time
from dataclasses import dataclass

@dataclass
class Event:
    ts: float; actor: str; action: str; target: str = ""

now = time.time()
AGENT = [Event(now + i*0.2, "patch-agent", "read_file", f"/work/{i}.py")
         for i in range(300)]
HUMAN = [Event(now + t, "dana@corp", "read_file", "/work/a.py")
         for t in (0, 12, 30, 95, 240, 600, 1500)]

CLASSIC = {
 "rate > 30 actions/min":
   lambda ev: (len(ev) / max((ev[-1].ts - ev[0].ts)/60, 1e-9)) > 30,
 "activity outside 09:00-18:00":
   lambda ev: True,                     # agents run continuously
 "same action > 100 times":
   lambda ev: max((sum(1 for e in ev if e.action == a) for a in {x.action for x in ev}),
                  default=0) > 100,
}
print(f"{'classic rule':34s}{'fires on agent':16s}fires on human")
print("-" * 66)
for name, rule in CLASSIC.items():
    print(f"{name:34s}{str(rule(AGENT)):16s}{rule(HUMAN)}")
print("\nAll three fire on an agent doing exactly its job. Deployed as-is, they")
print("produce continuous noise and are disabled within a week.")

@dataclass
class Baseline:
    """What normal looked like when the control was signed off."""
    tool_mix: dict
    actions_per_hour: float
    scopes_used: set

    def compare(self, events, scopes_used, hours=1.0):
        counts = {}
        for e in events:
            counts[e.action] = counts.get(e.action, 0) + 1
        total = sum(counts.values()) or 1
        now_mix = {k: v/total for k, v in counts.items()}
        keys = set(now_mix) | set(self.tool_mix)
        tvd = sum(abs(now_mix.get(k, 0) - self.tool_mix.get(k, 0)) for k in keys) / 2
        new_tools = sorted(set(now_mix) - set(self.tool_mix))
        new_scopes = sorted(scopes_used - self.scopes_used)
        return {"drift": round(tvd, 3), "new_tools": new_tools,
                "new_scopes": new_scopes,
                "rate_ratio": round((total/hours) / self.actions_per_hour, 2),
                "verdict": ("SIGNIFICANT — re-test the controls"
                            if tvd > 0.25 or new_tools or new_scopes
                            else "within tolerance")}

base = Baseline(tool_mix={"read_file": 0.85, "search": 0.15},
                actions_per_hour=1200, scopes_used={"repo:read"})

WEEKS = {
 "week 1 (baseline)":   ([("read_file", 850), ("search", 150)], {"repo:read"}),
 "week 4 (new prompt)": ([("read_file", 700), ("search", 200), ("write_file", 100)],
                          {"repo:read", "repo:write"}),
 "week 8 (upgrade)":    ([("read_file", 300), ("search", 100), ("write_file", 200),
                          ("run_shell", 400)], {"repo:read", "repo:write", "exec"}),
}
for label, (mix, scopes) in WEEKS.items():
    ev = [Event(now, "patch-agent", tool) for tool, n in mix for _ in range(n)]
    d = base.compare(ev, scopes)
    print(f"{label:22s} drift={d['drift']:.3f}  rate×{d['rate_ratio']}  {d['verdict']}")
    if d["new_tools"]:  print(f"{'':22s} new tools:  {d['new_tools']}")
    if d["new_scopes"]: print(f"{'':22s} new scopes: {d['new_scopes']}")

def alert_text(agent, d):
    if d["verdict"].startswith("within"): return None
    changes = []
    if d["new_tools"]:  changes.append(f"began using {d['new_tools']}")
    if d["new_scopes"]: changes.append(f"exercised new scopes {d['new_scopes']}")
    if d["drift"] > 0.25: changes.append(f"tool mix shifted (TVD {d['drift']})")
    return (f"[{agent}] behaviour changed from the signed-off baseline\n"
            f"   what changed : {'; '.join(changes)}\n"
            f"   why it matters: the controls in A3 were tested against the old\n"
            f"                   behaviour; a new tool may not be covered\n"
            f"   do this      : confirm a manifest change was reviewed (A1.1),\n"
            f"                   then re-run the containment suite (C1.2)")

ev = [Event(now, "patch-agent", tool) for tool, n in WEEKS["week 8 (upgrade)"][0]
      for _ in range(n)]
d = base.compare(ev, WEEKS["week 8 (upgrade)"][1])
print(alert_text("patch-agent", d))
assert d["new_tools"] and d["new_scopes"]
