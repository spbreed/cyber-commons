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
print("Read the two confidences again: 0.82 for the real defect, 0.71 for the")
print("invented one. That gap is not a threshold you can gate on - it is one")
print("sample of a number that moves between runs, and the honest use of it is")
print("as a sort order for a human, not as a cut-off for a pipeline.")
print()
print("The rejection cost nothing and required no judgement: the model quoted a")
print("line that is not in the file. Contextual verification (B2.4) is that")
print("check generalised, and it is the highest-yield filter in the pipeline.")
print()
print("Nothing here is promoted. This skill produces hypotheses; dedup,")
print("verification, reachability and dynamic validation decide which of them")
print("become findings. An audit stage that promotes its own output has removed")
print("the only independent step it had.")

assert report["hypotheses"], "the model pass found nothing at all"
assert report["rejected"], "a review pass that is never wrong has not been tested"
assert report["promoted"] == 0, "the audit stage must not promote its own output"
