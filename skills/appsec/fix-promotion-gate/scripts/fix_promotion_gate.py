#!/usr/bin/env python3
"""Promote four candidate patches from the sandbox replica through QA to a merge request, and count how many CI alone would have merged.

This is the executable half of the `fix-promotion-gate` skill. The four
candidates are the ones from B2.11's confirmed SQL injection in CyberTravels'
booking service: one real fix, one that changes behaviour, one that only moves
the pattern, and one that closes the bug by deleting the feature.

Standard library only, and deterministic.
"""

# (id, patch, ci_green, exploit_blocked_in_replica, behaviour_preserved_in_qa,
#  new_findings, what it actually did)
CANDIDATES = [
    ("A", 'execute("... ref = ?", (ref,))',       True,  True,  True,  0,
     "parameterised and bound - the fix"),
    ("B", 'execute("... ref = ?", (ref[:8],))',   True,  True,  False, 0,
     "parameterised, and silently truncates the reference"),
    ("C", 'execute("... ref = " + escape(ref))',  True,  False, True,  0,
     "still concatenation; escape() moved the pattern past the rule"),
    ("D", 'return []',                            True,  True,  True,  0,
     "closes the finding by removing partial-reference search"),
]

# Step 2 — the control. Without it a probe that stopped asserting reports every
# patch as a success, and this is the run that proves the probe still works.
EXPLOIT_ON_UNPATCHED = True

print("the exploit, against the unpatched build in the replica")
print(f"   reproduces: {EXPLOIT_ON_UNPATCHED}   <- if this were False the probe is")
print("               broken and every result below would be meaningless")
print()

report = {"candidates": [], "evidence_attached": []}
print(f"   {'':<3}{'CI':<5}{'exploit':<9}{'behaviour':<11}{'new':<5}promoted to")
for cid, patch, ci, blocked, behaviour, new, what in CANDIDATES:
    if not blocked:
        promoted, died = "rejected", "sandbox: exploit still works"
    elif not behaviour:
        promoted, died = "rejected", "qa: behaviour changed"
    elif new:
        promoted, died = "rejected", "finding diff: introduced a new one"
    else:
        promoted, died = "merge-request", ""
    print(f"   {cid:<3}{'ok' if ci else '--':<5}{'blocked' if blocked else 'WORKS':<9}"
          f"{'same' if behaviour else 'CHANGED':<11}{new:<5}{promoted}"
          f"{'  <- ' + died if died else ''}")
    report["candidates"].append({"id": cid, "ci_green": ci,
                                 "exploit_blocked": blocked,
                                 "behaviour_preserved": behaviour,
                                 "new_findings": new, "promoted_to": promoted,
                                 "died_at": died})
print()

for cid, patch, *_rest, what in CANDIDATES:
    print(f"   {cid}  {what}")
print()

ci_alone = sum(1 for c in CANDIDATES if c[2])
opened = sum(1 for c in report["candidates"] if c["promoted_to"] == "merge-request")
report["would_merge_on_ci_alone"] = ci_alone
report["merge_requests_opened"] = opened

print(f"merge requests CI alone would have opened : {ci_alone}")
print(f"merge requests the gates opened           : {opened}")
print()
print("C is the one worth staring at. It is green, the rule no longer fires,")
print("and the exploit works unchanged - the patch moved the pattern rather than")
print("closing the injection. Only re-running the exploit catches that, and only")
print("in an environment built to be attacked.")
print()
print("D is the other kind. It passes every gate above and it is still wrong:")
print("it closes the finding by deleting partial-reference search, which is a")
print("feature travellers use. No automated gate rejects D, because 'is this the")
print("mechanism we want' is not a property of a test run - it is the question")
print("the merge request exists to ask a human.")
print()

# Step 5 — the evidence travels with the request, or the reviewer re-derives it.
report["evidence_attached"] = [
    "exploit run against the unpatched build: reproduces",
    "exploit run against the patched build: blocked",
    "QA regression: 4/4 booking behaviours unchanged",
    "finding diff: target finding gone, 0 introduced",
]
print("attached to the merge request for A:")
for e in report["evidence_attached"]:
    print(f"   - {e}")
print()
print("A reviewer opening that request does not have to establish whether the")
print("bug is closed. That is answered on the page, so the review can be about")
print("D's question instead - which is the only one they are needed for.")

assert EXPLOIT_ON_UNPATCHED, "the proof-of-fix control must reproduce"
assert ci_alone > opened, "if CI alone merges no more than the gates, a gate is not running"
# Two reach review, and one of those two is D. The gates are not a substitute
# for the review; they are what makes the review about something a human is
# needed for.
assert opened == 2, "the gates should stop the evasion and the behaviour change, and not D"
