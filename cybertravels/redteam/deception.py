# step:file D1.8
"""Canaries — the only alert nobody has to triage.

Every detection in Function D has a false-positive rate, because every
detection is a guess about intent from behaviour. A canary is different in
kind: it is an object with **no legitimate reader**. Nothing in CyberTravels
reads it, no job touches it, no report includes it. So an access is not
evidence of something suspicious — it is the thing itself, and there is no
triage step because there is nothing to decide.

That property is fragile and it is the whole design problem. A canary that
something legitimately reads is a noisy detection with extra steps. So the
placement rule is severe: **if you cannot name why nothing reads it, it is not
a canary.**

Two things this file measures that canary write-ups usually skip:

* **decay.** A canary works because it is indistinguishable from the real
  thing. Agents that read the same environment repeatedly stop being fooled —
  and, more practically, a canary that has sat unread for a year starts
  looking like the one file nobody touches, which is itself a signal.
* **the threshold failure.** Deception is often deployed alongside a
  volume-based rule and the two are tuned together. The canary fires once;
  the volume rule needs five. The alert that cannot be a false positive is
  then suppressed by a threshold designed for alerts that can.
"""
import time


class Canary:
    """An object with no legitimate reader, and the reason written down."""

    __slots__ = ("name", "kind", "placed_at", "why_nothing_reads_it",
                 "reads", "decoy_of")

    def __init__(self, name, kind, why_nothing_reads_it, *, decoy_of=None):
        if not why_nothing_reads_it:
            raise ValueError(
                f"{name}: a canary needs the reason nothing legitimately reads "
                f"it, written down. Without it this is an ordinary detection "
                f"with an unexamined false-positive rate")
        self.name = name
        self.kind = kind                    # credential, record, file, tool
        self.why_nothing_reads_it = why_nothing_reads_it
        self.decoy_of = decoy_of            # what it is indistinguishable from
        self.placed_at = time.time()
        self.reads = []

    def read_by(self, who, *, at=None):
        """Every read is an incident. There is no benign branch here."""
        self.reads.append({"who": who, "at": at or time.time()})
        return {"canary": self.name, "actor": who, "verdict": "incident",
                "triage_required": False,
                "why": self.why_nothing_reads_it}

    def as_dict(self):
        return {"canary": self.name, "kind": self.kind,
                "decoy_of": self.decoy_of, "reads": len(self.reads),
                "why_nothing_reads_it": self.why_nothing_reads_it}


# Where a canary goes in this system, and why nothing reads each one. Every
# row had to earn its second column; a placement without one was dropped.
PLACEMENTS = [
    ("refund-canary-booking", "record",
     "a booking id outside the seeded range — no traveller owns it, so no "
     "legitimate lookup names it"),
    ("idp-canary-secret", "credential",
     "a second signing key that no component loads; config.py names only one"),
    ("invoice-canary.pdf", "file",
     "an invoice under data/invoices that no booking references"),
    ("export_all_travellers", "tool",
     "a tool in the policy table that no agent's prompt mentions and no "
     "workflow needs — it exists to be found"),
]


def place():
    return [Canary(name, kind, why) for name, kind, why in PLACEMENTS]


def decay(canary, *, now=None, half_life_days=180):
    """How much of the canary's value is left.

    Two decays at once. An agent exposed to the same environment repeatedly
    learns it, and an object untouched for long enough becomes conspicuous by
    its stillness. Neither is a reason not to place canaries; both are reasons
    to rotate them, and rotation is the thing that never gets scheduled.
    """
    age_days = ((now or time.time()) - canary.placed_at) / 86400
    return {"canary": canary.name, "age_days": round(age_days, 1),
            "value_remaining": round(0.5 ** (age_days / half_life_days), 3),
            "rotate": age_days > half_life_days,
            "why": "an unread object eventually reads as the one nobody "
                   "touches, which is a signal to the other side too"}


def suppressed_by_threshold(alerts, *, threshold):
    """The failure this lesson exists for.

    A canary alert has a count of one, by construction — you only read the
    decoy once. A volume rule tuned to fire at five suppresses it, and the
    suppression is invisible because the canary did fire, into a pipeline that
    dropped it. Returns the alerts that would be lost.
    """
    lost = [a for a in alerts
            if a.get("triage_required") is False and a.get("count", 1) < threshold]
    return {"threshold": threshold, "suppressed": len(lost),
            "alerts": [a["canary"] for a in lost],
            "why": "these need no triage and are individually conclusive; a "
                   "threshold built for alerts that need both is the wrong "
                   "pipeline for them"}
