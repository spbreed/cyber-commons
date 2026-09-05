#!/usr/bin/env python3
"""Run the model over the one defect Semgrep structurally cannot reach, and record it as a hypothesis.

This is the executable half of the `sast-model-pass` skill, and the second of
the two audit skills in B2.3. The first scored real Semgrep output and ended on
three defects with no syntax to match. This one takes the first of them.

The two functions below are not written here. They are cut out of
`cybertravels/tools/bookings_api.py` — the same file Semgrep scanned at three
widths and missed — with `ast`, so the model reviews the bytes that are in the
repository rather than a paraphrase of them. `get_booking` returns the row a
caller names. `get_my_booking`, eleven lines further down, does the same read
and compares an owner. That is the whole difference, and no rule reaches it.

The model call goes through the shared adapter: offline it is a labelled
replay, and with an open-weight endpoint configured it is the same code against
a real model.

Standard library only, and deterministic.
"""

import ast
from pathlib import Path

from cyber_commons_skill_runtime import announce_backend, ask

# The tree, found from this file rather than from the working directory: on
# Kaggle `cwd` is /kaggle/working and the clone is beside it.
ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "cybertravels" / "tools" / "bookings_api.py"
TEXT = SOURCE.read_text()


def slice_of(unit, caller):
    """The slice, not the file: the function as committed, plus the authority
    its caller holds. Dropping that second line is what makes the answer wrong,
    and it is the line no file contains — it comes from A1.1's map."""
    tree = ast.parse(TEXT)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == unit:
            return f"# caller: {caller}\n{ast.get_source_segment(TEXT, node)}\n"
    raise SystemExit(f"{unit} is not in {SOURCE.name} — the corpus moved")


SLICE = slice_of("get_booking",
                 "Workflow Agent, holds scope booking.* and payments.refund")

# The safe twin from the same file, already authorised. It is here because a
# review pass that is never wrong has not been tested.
CONTROL = slice_of("get_my_booking",
                   "traveller, holds scope booking.read on their own bookings only")

# The format names its own tokens. An earlier version wrote the first field as
# "VERDICT", and a served Qwen2.5-7B returned the literal string VERDICT — it
# read the placeholder as the answer. The ask is the part you own, and that is
# B2.1's whole point arriving here as a bug.
QUESTION = ("Does this function verify that the caller is entitled to the rows "
            "it returns?\n"
            "Reply on ONE line, four fields separated by |:\n"
            "  field 1: exactly MISSING or PRESENT\n"
            "  field 2: a CWE id, e.g. CWE-862\n"
            "  field 3: your confidence, 0.00 to 1.00\n"
            "  field 4: one line copied exactly from the code above, or NONE\n"
            "Example of the shape: PRESENT|CWE-862|0.90|require_owner(x)")

# The replays are labelled and visible in the source, per the adapter's
# contract. They are what a correct answer looks like: the defect found on the
# function that has one, and no defect claimed on the function that does not.
# The fabrication that the verifier catches is demonstrated separately, below,
# so the rejection path is exercised on every run rather than only when a model
# happens to invent something.
REPLAY = {
    "get_booking":    "MISSING|CWE-639|0.82|def get_booking(session, booking_id):",
    "get_my_booking": "PRESENT|CWE-639|0.77|    require_owner(session, row[\"owner_id\"] if row else None)",
}

VERDICTS = {}

kind, model = announce_backend()
print()

report = {"backend": {"kind": kind, "model": model},
          "hypotheses": [], "rejected": [], "promoted": 0}

for unit, code in (("get_booking", SLICE), ("get_my_booking", CONTROL)):
    answer, kind, model = ask(f"{code}\n{QUESTION}", replay=REPLAY[unit],
                              system="You are a code reviewer. One line, no prose.")
    parts = [p.strip() for p in answer.strip().splitlines()[0].split("|")]
    verdict, cwe, conf, quote = (parts + ["", "", "0", "NONE"])[:4]
    verdict = verdict.strip().upper()
    VERDICTS[unit] = verdict
    try:
        conf = float(conf)
    except ValueError:
        conf = 0.0

    print(f"{unit}")
    print(f"   model says   : {verdict} {cwe} at confidence {conf:.2f}")
    print(f"   quoting      : {quote.strip()[:60]}")

    # Step 3 — the check that costs nothing. A quote that is not in the slice
    # is a fabrication, and this is where it dies.
    # NONE is not a fabrication. For an absence defect there is no line to
    # quote, and a served Qwen2.5-7B says so — it answered MISSING with NONE,
    # which is the correct reading of the question. Only a quote that was
    # *given* and is not in the slice is a fabrication.
    q = quote.strip()
    fabricated = q != "NONE" and q not in code
    verified = q != "NONE" and not fabricated
    if fabricated:
        print(f"   -> REJECTED  : that line is not in the file")
        report["rejected"].append({"unit": unit, "why": "quote-not-in-file"})
    elif verdict == "MISSING" and q == "NONE":
        print(f"   -> HYPOTHESIS: absence defect, nothing to quote - status hypothesis")
        report["hypotheses"].append({"unit": unit, "cwe": cwe, "confidence": conf,
                                     "quote_verified": False, "status": "hypothesis"})
    elif verdict != "MISSING":
        print(f"   -> NO CLAIM  : reviewed, nothing asserted, nothing to promote")
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
# The property is not the CWE id — several are defensible for "no entitlement
# check". It is whether the model can tell the unauthorised function from the
# authorised one, which is the claim this stage makes.
found = (VERDICTS.get("get_booking") == "MISSING"
         and VERDICTS.get("get_my_booking") == "PRESENT")
print("property checked : MISSING on get_booking and PRESENT on get_my_booking "
      "- telling the unauthorised function from its authorised twin")
print(f"held on {kind:12s} : {found}")
print()

# Step 3, as a check of the check. The rejection must be demonstrated on every
# run, and it cannot be demonstrated by *waiting for the model to be wrong*: a
# capable model gets the already-authorised control function right, which is
# the outcome you want and would leave the verifier untested. So the verifier
# is tested directly, against a quote known not to be in the file.
# A real fabrication, recorded from a run of this skill against a smaller model:
# a confident CWE-89 on a function whose query is already parameterised, quoting
# a concatenation that does not appear anywhere in the slice.
FABRICATED = 'cur.execute("SELECT * FROM bookings WHERE owner = \'" + user)'
print("the verifier, tested against a fabrication recorded from a smaller model")
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
