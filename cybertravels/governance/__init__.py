# step:file F1.0
"""Governance that reads the code, rather than asserting about it.

Every other function in this commons built something. This one answers the
question the board actually asks — *who signed off, and can they still
evidence it* — and it answers it the only way that survives contact with an
auditor: by measuring the controls that are in the tree rather than by
restating the register.

That is the whole design decision here, and it is what makes this package
short. A governance module that models policies, workflows and sign-offs would
be a second system with its own drift. This one imports `cybertravels.policy`,
`cybertravels.registry`, `cybertravels.appsec`, `cybertravels.redteam` and
`cybertravels.soc`, asks each whether its control is present and functioning,
and reports what it found. When a control is removed, the number moves.

**A trustworthy-AI statement with no owner per property is a statement that
every property is somebody else's job.** So the first thing here is not a
principle; it is a table with a name in the second column.
"""

# The properties a trustworthy-AI statement claims, each with the function
# that owns it and the artefact that evidences it. The third column is what
# makes the first one checkable — a property with no artefact is a value, and
# values do not survive an audit.
PROPERTIES = [
    ("secure", "A", "cybertravels/policy.py, gateway.py, sandbox.py — the "
                    "decision point, the choke point and the profile"),
    ("correct", "B", "cybertravels/appsec/ — the pipeline that reviews it, "
                     "with recall measured against LABELS.md"),
    ("robust", "C", "cybertravels/redteam/campaign.py — a rate with an "
                    "interval, not an anecdote"),
    ("observable", "D", "cybertravels/soc/sensors.py — coverage per agent "
                        "action, and the uncovered ones named"),
    ("accountable", "E", "cybertravels/governance/ — this package, and the "
                         "attestation B3.7 and C2.18 produce"),
    ("private", "E", "soc/sensors.py FIELD_RETENTION, per field rather than "
                     "per record"),
]


def owners():
    return [{"property": p, "function": f, "evidence": e}
            for p, f, e in PROPERTIES]


def unowned(claimed):
    """Properties a statement claims that nothing in this system evidences.

    F1.0's Day 2 number, and the uncomfortable one: a statement is usually
    longer than the list of things anybody built.
    """
    have = {p for p, _f, _e in PROPERTIES}
    return sorted(set(claimed) - have)
