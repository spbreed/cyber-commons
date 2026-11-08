"""The programme does not fail at the functions. It fails at the seams.

Legal, compliance, privacy, cyber and model risk each hold part of the AI
control estate and none of them holds all of it. Every function is competent,
every function delivers what it owns, and the thing falls over between them —
because a handoff is nobody's deliverable and therefore nobody's deadline.

Three lessons, and they are one argument:

    F1.10  who holds which part, and where two of them both think the other
           has it
    F1.11  model risk management, whose playbook silently breaks once the
           model can act
    F1.12  the handoffs themselves, traced from producer to consumer
"""


# Who holds what. The interesting column is the last one: a part nobody holds
# is a gap, and a part two functions both believe the other holds is worse,
# because it is a gap that looks covered on both sides.
HOLDERS = {
    "legal position on autonomy": ["legal"],
    "privacy impact assessment": ["privacy"],
    "control design": ["cyber"],
    "model validation": ["model risk"],
    "regulatory obligation mapping": ["compliance"],
    "the system prompt's legal wording": ["legal", "cyber"],
    "agent entitlements review": ["cyber", "compliance"],
    "retention of agent telemetry": ["privacy", "cyber"],
    "evidence that a control works": [],
    "who may raise the autonomy of a deployment": [],
}


def seam_map():
    rows = []
    for part, held in sorted(HOLDERS.items()):
        rows.append({
            "part": part, "held_by": held,
            "state": ("unowned" if not held
                      else "shared" if len(held) > 1 else "owned"),
            "risk": ("nobody produces this" if not held
                     else "each may believe the other has it" if len(held) > 1
                     else ""),
        })
    return {"parts": rows,
            "unowned": [r["part"] for r in rows if r["state"] == "unowned"],
            "shared": [r["part"] for r in rows if r["state"] == "shared"],
            "why": "a shared part is not safer than an unowned one — it is an "
                   "unowned one that looks covered from both sides"}




