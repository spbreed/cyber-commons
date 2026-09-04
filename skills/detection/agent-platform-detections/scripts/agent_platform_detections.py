#!/usr/bin/env python3
"""Write detections whose subject is the agent platform — sandbox escape, orphaned processes, cache tampering — and compare them with a generic anomaly score.

This is the executable half of the `agent-platform-detections` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

EVENTS = [
 {"t": 1,  "proc": "harness",   "syscall": "execve",  "arg": "python3 solve.py"},
 {"t": 2,  "proc": "solve.py",  "syscall": "openat",  "arg": "/workspace/in.json"},
 {"t": 3,  "proc": "solve.py",  "syscall": "ptrace",  "arg": "attach pid=1 (not a child)"},
 {"t": 4,  "proc": "solve.py",  "syscall": "execve",  "arg": "sh -c 'LD_PRELOAD=/tmp/x.so ...'"},
 {"t": 5,  "proc": "x.so",      "syscall": "openat",  "arg": "/run/harness.sock"},
 {"t": 6,  "proc": "solve.py",  "syscall": "openat",  "arg": "/workspace/out.json"},
 {"t": 7,  "proc": "sidecar",   "syscall": "execve",  "arg": "sleep 86400"},
]
BASELINE_TREE = {"harness", "solve.py"}

RULES = [
 ("ptrace attach to a non-child", lambda e: e["syscall"] == "ptrace" and "not a child" in e["arg"]),
 ("LD_PRELOAD on a spawned process", lambda e: "LD_PRELOAD" in e["arg"]),
 ("non-harness write to the RPC path", lambda e: "harness.sock" in e["arg"] and e["proc"] != "harness"),
 ("process outside the baseline tree", lambda e: e["proc"] not in BASELINE_TREE),
]

fired = []
for e in EVENTS:
    for name, rule in RULES:
        if rule(e):
            fired.append((e["t"], name, e["proc"]))
print(f"{'t':>3}  {'rule':36s}process")
for t, name, proc in fired:
    print(f"{t:>3}  {name:36s}{proc}")

# a generic score over the same events
volume = len(EVENTS)
score = volume / 100
print(f"\ngeneric anomaly score for this run: {score:.2f}  "
      f"(seven syscalls is unremarkable)")
print(f"named rules fired: {len(fired)}")
print()
print("The escape is four ordinary-looking events. Volume scoring cannot see it")
print("because nothing about the volume is unusual.")
assert len(fired) >= 5 and score < 0.1

TOOL_CALLS = [
 {"call": 1, "spawned": ["solve.py"],  "ended": ["solve.py"]},
 {"call": 2, "spawned": ["sidecar"],   "ended": []},
 {"call": 3, "spawned": ["fmt"],       "ended": ["fmt"]},
]
def orphans(calls):
    live = []
    for c in calls:
        for p in c["spawned"]:
            if p not in c["ended"]:
                live.append((c["call"], p))
    return live

live = orphans(TOOL_CALLS)
print("processes surviving the tool call that spawned them:")
for call, proc in live:
    print(f"   call {call}: {proc}")
print()
print("A background process that outlives its tool call is how a substituted")
print("command stays in place for the next one. This single rule is the cheapest")
print("detection in the set and it is specific enough to page on.")
assert live == [(2, "sidecar")]

import hashlib

def h(s): return hashlib.sha256(s.encode()).hexdigest()[:12]

MANIFEST = {"libtarget-1.4.jar": h("libtarget-1.4"),
            "runner-2.0.tar":    h("runner-2.0"),
            "fixtures-9.zip":    h("fixtures-9")}
REPOSITORY = {"libtarget-1.4.jar": h("libtarget-1.4-modified"),   # staged
              "runner-2.0.tar":    h("runner-2.0"),
              "extra-0.1.jar":     h("extra-0.1")}                # unexpected

def diff(manifest, repo):
    out = []
    for name in sorted(set(manifest) | set(repo)):
        if name not in repo:
            out.append((name, "MISSING - expected artifact removed"))
        elif name not in manifest:
            out.append((name, "UNEXPECTED - not in the manifest"))
        elif manifest[name] != repo[name]:
            out.append((name, "MODIFIED - hash mismatch"))
    return out

print("cache integrity diff (C5.4)")
for name, why in diff(MANIFEST, REPOSITORY):
    print(f"   {name:22s}{why}")

EXPOSURES = [("hf_liveToken", "public dataset card", 0)]
def revoke(exposures, human_in_loop):
    delay = 240 if human_in_loop else 2       # minutes
    return [(t, where, delay) for t, where, _ in exposures]

print("\ncredential exposure to revocation (C4.1)")
for mode, hitl in (("human in the loop", True), ("automated", False)):
    for token, where, delay in revoke(EXPOSURES, hitl):
        print(f"   {mode:20s}{token:16s}{where:22s}{delay:>4} min")
print("   reported interval from discovery to redistribution: minutes")

APPROVED = {"cyber-classifier": 30}
LIVE = {"cyber-classifier": "disabled", "egress-allowlist": "disabled"}
print("\nexemption-state reconciliation (C6.3), day 44")
for control, state in sorted(LIVE.items()):
    expires = APPROVED.get(control)
    if state == "enabled":
        verdict = "ok"
    elif expires is None:
        verdict = "P1 - disabled with no approved exemption"
    elif 44 > expires:
        verdict = f"P1 - exemption expired on day {expires}, auto re-enable"
    else:
        verdict = "ok - within an approved exemption"
    print(f"   {control:20s}{state:10s}{verdict}")
assert len(diff(MANIFEST, REPOSITORY)) == 3
