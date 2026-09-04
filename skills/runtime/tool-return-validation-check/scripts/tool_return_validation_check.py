#!/usr/bin/env python3
"""Check four tool returns against a schema and against an oracle, and propagate only what verified.

This is the executable half of the `tool-return-validation-check` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

SCHEMA = {"claim": str, "confidence": float, "verified_by": (str, type(None))}

def schema_ok(msg):
    return all(k in msg and isinstance(msg[k], t) for k, t in SCHEMA.items())

GROUND_TRUTH = {"libfoo has no known CVEs": False,      # it has one
                "test_login passes": True}

def verify(claim):
    """Independent: reads ground truth, not the sender's opinion."""
    if claim not in GROUND_TRUTH:
        return None, "no oracle for this claim"
    return GROUND_TRUTH[claim], "checked against the advisory database"

def propagate(msg, hops=3):
    """A claim may not travel without a verification result attached."""
    if not schema_ok(msg):
        return {"stopped": "malformed"}
    result, how = verify(msg["claim"])
    if result is None:
        return {"stopped": "unverifiable", "claim": msg["claim"], "why": how}
    if result is False:
        return {"stopped": "refuted", "claim": msg["claim"], "by": how}
    return {"propagated": msg["claim"], "verified_by": how, "hops": hops}

MESSAGES = [
 {"claim": "libfoo has no known CVEs", "confidence": 0.9, "verified_by": None},
 {"claim": "test_login passes",        "confidence": 0.5, "verified_by": None},
 {"claim": "the refund was approved",  "confidence": 0.99, "verified_by": None},
 {"claim": "libfoo is fine",           "confidence": "high", "verified_by": None},
]
for m in MESSAGES:
    print(f"   schema_ok={str(schema_ok(m)):5s} -> {propagate(m)}")

print()
print("The first message is schema-perfect and confident and false. Schema")
print("validation passed it; the oracle refuted it.")
print()
print("The third is unverifiable - no oracle exists. That is a legitimate")
print("outcome and it must not silently become 'true'. It stops here with a")
print("reason, which is what A1.12's cascade never had.")
assert propagate(MESSAGES[0])["stopped"] == "refuted"
assert propagate(MESSAGES[2])["stopped"] == "unverifiable"
assert "propagated" in propagate(MESSAGES[1])
