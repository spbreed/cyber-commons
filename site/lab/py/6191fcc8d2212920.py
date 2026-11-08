"""From a framework control to a number somebody can check this week.

An annual review certifies nothing about a system that changed the week after
it, and every system here changes weekly. So a control in this register is not
a paragraph with a date on it — it is a **key control indicator**: a named
measurement, a source in the tree, a threshold, and a cadence.

The rule that makes a KCI worth having is that it has to be computable without
asking anybody. If the measurement requires an engineer to go and look, it
will be taken once, at audit time, by somebody who knows what answer is
wanted.

Four lessons build this file:

    F1.1  the KCI itself — control -> measurement -> threshold
    F1.2  the inventory, derived from the tree rather than from a survey
    F1.3  tiering by what the thing can do, not by which model it uses
    F1.4  mapping outward to frameworks, never inward from them
"""
from .. import config


class KCI:
    """One control, as something measurable."""

    __slots__ = ("control_id", "name", "measure", "threshold", "direction",
                 "cadence_days", "source")

    def __init__(self, control_id, name, measure, threshold, direction,
                 cadence_days, source):
        if direction not in (">=", "<="):
            raise ValueError(f"{control_id}: a threshold needs a direction")
        if not callable(measure):
            raise ValueError(
                f"{control_id}: the measurement has to be computable. One that "
                f"needs an engineer to go and look is taken once, at audit "
                f"time, by somebody who knows what answer is wanted")
        self.control_id = control_id
        self.name = name
        self.measure = measure
        self.threshold = threshold
        self.direction = direction
        self.cadence_days = cadence_days
        self.source = source

    def evaluate(self):
        value = self.measure()
        passes = (value >= self.threshold if self.direction == ">="
                  else value <= self.threshold)
        return {"control": self.control_id, "name": self.name,
                "value": value, "threshold": self.threshold,
                "direction": self.direction, "passes": passes,
                "source": self.source, "cadence_days": self.cadence_days}






