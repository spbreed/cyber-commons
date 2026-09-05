#!/usr/bin/env python3
"""Run the model over the one defect Semgrep structurally cannot reach, and record it as a hypothesis.

This is the executable half of the `sast-model-pass` skill, and the second of
the two audit skills in B2.3. The first scored real Semgrep output and ended on
a defect with no syntax to match: `find_booking` returns a booking to whoever
asks, in a service whose Workflow Agent holds payments scope. No rule reaches
the absence of a call.

The model call goes through the shared adapter: offline it is a labelled
replay, and with an open-weight endpoint configured it is the same code against
a real model.

Standard library only, and deterministic.
"""

from cyber_commons_skill_runtime import announce_backend, ask

# The slice, not the file: the function, its signature, and the authority its
# caller holds. Dropping that last line is what makes the answer wrong.
SLICE = '''\
# caller: Workflow Agent, holds scope booking.* and payments.refund
def find_booking(reference):
    cur = DB.cursor()
    cur.execute("SELECT * FROM bookings WHERE reference LIKE ?", (f"%{reference}%",))
    return cur.fetchall()
'''

# A second function from the same file, already parameterised and already
# authorised. It is here because a review pass that is never wrong has not
# been tested.
CONTROL = '''\
# caller: traveller, holds scope booking.read on their own bookings only
def my_bookings(session):
    require_owner(session.user_id)
    cur = DB.cursor()
    cur.execute("SELECT * FROM bookings WHERE owner = ?", (session.user_id,))
    return cur.fetchall()
'''

QUESTION = ("Does this function verify that the caller is entitled to the rows "
            "it returns? Answer on one line as VERDICT|CWE|confidence|quoted "
            "line, where the quoted line is copied exactly from the code above "
            "or is the word NONE.")

# The replays are labelled and visible in the source, per the adapter's
# contract. The second is a real failure mode, not a strawman: a confident
# claim about a line that is not in the file.
REPLAY = {
    "find_booking": "MISSING|CWE-862|0.82|def find_booking(reference):",
    "my_bookings":  "MISSING|CWE-89|0.71|cur.execute(\"SELECT * FROM bookings WHERE owner = '\" + user)",
}

kind, model = announce_backend()
print()

report = {"backend": {"kind": kind, "model": model},
          "hypotheses": [], "rejected": [], "promoted": 0}

for unit, code in (("find_booking", SLICE), ("my_bookings", CONTROL)):
    answer, kind, model = ask(f"{code}\n{QUESTION}", replay=REPLAY[unit],
                              system="You are a code reviewer. One line, no prose.")
    parts = [p.strip() for p in answer.strip().splitlines()[0].split("|")]
    verdict, cwe, conf, quote = (parts + ["", "", "0", "NONE"])[:4]
    try:
        conf = float(conf)
    except ValueError:
        conf = 0.0

    print(f"{unit}")
    print(f"   model says   : {verdict} {cwe} at confidence {conf:.2f}")
    print(f"   quoting      : {quote[:60]}")

    # Step 3 — the check that costs nothing. A quote that is not in the slice
    # is a fabrication, and this is where it dies.
    verified = quote != "NONE" and quote in code
    if not verified:
        print(f"   -> REJECTED  : that line is not in the file")
        report["rejected"].append({"unit": unit, "why": "quote-not-in-file"})
    else:
        print(f"   -> HYPOTHESIS: quote verified, status hypothesis (not a finding)")
        report["hypotheses"].append({"unit": unit, "cwe": cwe, "confidence": conf,
                                     "quote_verified": True, "status": "hypothesis"})
    print()

print(f"{len(report['hypotheses'])} hypothesis · {len(report['rejected'])} rejected "
      f"· {report['promoted']} promoted")
print()
# Reported rather than asserted, in the shape every model-facing skill uses.
# The pipeline property (below) must hold on any backend; this one is about
# the model, and a small model missing it is a finding about the model.
found = any(h["unit"] == "find_booking" and h["cwe"].upper() == "CWE-862"
            for h in report["hypotheses"])
print("property checked : the model finds the missing authorisation check "
      "that no rule can express")
print(f"held on {kind:12s} : {found}")
print()

# Step 3, as a check of the check. The rejection must be demonstrated on every
# run, and it cannot be demonstrated by *waiting for the model to be wrong*: a
# capable model gets the already-authorised control function right, which is
# the outcome you want and would leave the verifier untested. So the verifier
# is tested directly, against a quote known not to be in the file.
FABRICATED = 'cur.execute("SELECT * FROM bookings WHERE owner = \'" + user)'
print("the verifier, tested against a known fabrication")
print(f"   claim quotes : {FABRICATED[:58]}")
print(f"   in the file? : {FABRICATED in CONTROL}")
print(f"   -> REJECTED  : the quote is not in the slice, so the claim dies here")
verifier_works = FABRICATED not in CONTROL
print()

print("That check costs nothing and requires no judgement, and it is the single")
print("highest-yield filter available: a claim about a line that does not exist")
print("is provably wrong without a second opinion. B2.4 is the same check")
print("generalised into a stage.")
print()
print("What the confidence number is worth: it is uncalibrated - 0.82 does not")
print("mean the claim is right 82% of the time - and it is unstable across runs.")
print("Sort a human's queue with it if you like. Do not let it decide anything")
print("on its own, and note that this run is one sample of it.")
print()
print("Nothing here is promoted. This skill produces hypotheses; dedup,")
print("verification, reachability and dynamic validation decide which of them")
print("become findings. An audit stage that promotes its own output has removed")
print("the only independent step it had.")

assert report["hypotheses"], "the model pass found nothing at all"
assert verifier_works, "the quote check did not reject a fabricated quote"
assert report["promoted"] == 0, "the audit stage must not promote its own output"
