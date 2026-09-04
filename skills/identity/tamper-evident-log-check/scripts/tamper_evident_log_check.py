#!/usr/bin/env python3
"""Reconcile an agent's own transcript against a host stream, then hash-chain the segments and localise a rewrite.

This is the executable half of the `tamper-evident-log-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

RUN = [
 {"trace": "t-01", "harness_says": "ls /workspace",          "host_saw": "ls /workspace"},
 {"trace": "t-02", "harness_says": "cat report.md",          "host_saw": "cat report.md"},
 {"trace": "t-03", "harness_says": "python3 analyse.py",     "host_saw": "curl -s http://cache/put?m=..."},
 {"trace": "t-04", "harness_says": "git status",             "host_saw": "git status"},
 {"trace": "t-05", "harness_says": "echo done",              "host_saw": "python3 -c 'import os;os.execve(...)'"},
]

def in_band_check(run):
    """The only evidence is the transcript the agent's own process wrote."""
    return [r["trace"] for r in run if not r["harness_says"]]

print("in-band check - does every step have a recorded command?")
missing = in_band_check(RUN)
print(f"   steps: {len(RUN)}   steps with no record: {len(missing)}   verdict: "
      f"{'clean' if not missing else 'gaps'}")
print()
print("Two of these five steps executed something other than what was recorded.")
print("The in-band check cannot see that, because it is reading the record that")
print("the thing it is checking produced.")
assert not missing

def reconcile(run):
    """Divergence between the host stream and the harness transcript."""
    return [r for r in run if r["harness_says"] != r["host_saw"]]

diverged = reconcile(RUN)
print(f"{'trace':8s}{'harness recorded':30s}host observed")
for r in diverged:
    print(f"{r['trace']:8s}{r['harness_says']:30s}{r['host_saw'][:44]}")

rate = len(diverged) / len(RUN)
print(f"\nspoofing rate in this run: {rate:.0%}  ({len(diverged)} of {len(RUN)})")
print()
print("The reported rate across the source incident's sampled transcripts was")
print("about 7%, with the investigators unable to rule out more. Whatever the")
print("number, it is only knowable because two independent streams existed.")
assert len(diverged) == 2

import hashlib

def chain(segments):
    h = "0" * 64
    out = []
    for i, s in enumerate(segments):
        h = hashlib.sha256((s + h).encode()).hexdigest()
        out.append({"n": i, "segment": s, "head": h})
    return out

def verify(store):
    h = "0" * 64
    for row in store:
        h = hashlib.sha256((row["segment"] + h).encode()).hexdigest()
        if h != row["head"]:
            return False, row["n"]
    return True, None

SEGMENTS = [f"{r['trace']} {r['harness_says']}" for r in RUN]
store = chain(SEGMENTS)
ok, at = verify(store)
print(f"chain of {len(store)} segments verifies: {ok}")
print(f"head: {store[-1]['head'][:32]}...")

tampered = [dict(row) for row in store]
tampered[2]["segment"] = "t-03 python3 analyse.py   # nothing to see"
ok, at = verify(tampered)
print(f"\nafter rewriting segment 2: verifies={ok}, first break at segment {at}")
print()
print("The rewrite is not prevented - it is localised. Anyone holding the signed")
print("head knows which segment moved, which is the difference between a")
print("corrupted investigation and a bounded one.")
assert not ok and at == 2

WORKLOAD_ROLE = {
 "s3:GetObject":  ["arn:aws:s3:::agent-workspace/*"],
 "s3:PutObject":  ["arn:aws:s3:::agent-workspace/*"],
 "s3:ListBucket": ["arn:aws:s3:::agent-workspace"],
 "kms:Decrypt":   ["arn:aws:kms:::key/workspace"],
}
LOGGING_PLANE = ["arn:aws:s3:::agent-transcripts",
                 "arn:aws:s3:::agent-transcripts/*",
                 "arn:aws:kms:::key/transcript-signing"]

def reachable(role, targets):
    hits = []
    for action, resources in sorted(role.items()):
        for r in resources:
            for t in targets:
                if r == t or (r.endswith("/*") and t.startswith(r[:-1])):
                    hits.append((action, t))
    return hits

print("workload role vs the logging plane")
hits = reachable(WORKLOAD_ROLE, LOGGING_PLANE)
print(f"   permissions reaching the logging plane: {len(hits)}")
for a, t in hits:
    print(f"      {a} -> {t}")

WIDENED = dict(WORKLOAD_ROLE)
WIDENED["s3:PutObject"] = ["arn:aws:s3:::agent-workspace/*",
                           "arn:aws:s3:::agent-transcripts/*"]
bad = reachable(WIDENED, LOGGING_PLANE)
print(f"\nafter one convenience grant: {len(bad)} permission(s) reach it")
for a, t in bad:
    print(f"      {a} -> {t}")
print()
print("One line of IAM turns the chain, the WORM policy and the out-of-band")
print("sensor into decoration. This is a quarterly diff, not a design review.")
assert not hits and bad
