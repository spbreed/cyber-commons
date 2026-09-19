# step:file C1.0
"""The campaign — the arithmetic that makes an attack result a finding.

Everything in this file exists to stop one sentence being written: *"we got it
to issue a refund."* That sentence has no denominator. It does not say out of
how many, against which build, with what prompt, or whether the same thing
happens when you ask it politely.

Three pieces, and the third is the one almost nobody ships.

**A criterion.** Decided before the run, evaluated by something that is not the
model under test. `Case.succeeded` is a callable over the observed outcome, so
"it looked like it worked" cannot creep in.

**An interval.** Ten trials at 70% and ten at 90% are the same result. The
Wilson interval is used rather than the normal approximation because at the
ends — 0/20, 20/20 — the normal one produces intervals that include impossible
values, and 0/20 is exactly the case a defence gets evaluated on.

**An ablation.** Run the same cases with the harness stripped to nothing and
the model held constant. Whatever the bare model achieves is the model effect;
the difference is what your scaffolding contributed. Published jailbreak rates
are usually the second number reported as the first.

And the benign half. A technique with a 60% success rate that also fires on
40% of ordinary traffic has not found anything — it has found a coin. Every
campaign here carries benign cases and reports the false-alarm rate beside the
success rate, in the same table, because separating them is how one of them
gets quietly dropped.
"""
import math
import statistics
import time


class CampaignError(Exception):
    """The campaign was not set up in a way that could produce a number."""


class Case:
    """One attack, with the criterion that decides whether it worked."""

    __slots__ = ("name", "payload", "succeeded", "benign", "technique")

    def __init__(self, name, payload, succeeded, *, benign=False,
                 technique="unnamed"):
        if not callable(succeeded):
            raise CampaignError(
                f"{name}: the criterion must be a callable over the observed "
                f"outcome. A criterion applied by eye after the run is a "
                f"criterion chosen to fit it")
        self.name = name
        self.payload = payload
        self.succeeded = succeeded
        self.benign = benign
        self.technique = technique

    def __repr__(self):
        kind = "benign" if self.benign else "attack"
        return f"<Case {self.name} ({kind}) technique={self.technique}>"


class Trial:
    """One run of one case against one target."""

    __slots__ = ("case", "outcome", "worked", "at", "arm")

    def __init__(self, case, outcome, arm="full"):
        self.case = case
        self.outcome = outcome
        self.worked = bool(case.succeeded(outcome))
        self.arm = arm
        self.at = time.time()


def wilson(successes, n, z=1.96):
    """A 95% interval that behaves at the ends.

    The normal approximation gives 0/20 an interval of [0, 0], which reads as
    "this defence cannot be bypassed" and is a statement about the sample size.
    Wilson gives roughly [0, 0.16], which is the honest version: twenty clean
    trials rule out a high rate and say nothing about a low one.
    """
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4))


def trials_needed(p_expected, delta, z=1.96):
    """Roughly how many trials to distinguish p from p±delta.

    Printed in the campaign's preconditions so "we ran it ten times" is a
    decision somebody made rather than the number of times they got bored.
    """
    p = min(max(p_expected, 0.01), 0.99)
    return max(1, math.ceil((z * z * p * (1 - p)) / (delta * delta)))


class Campaign:
    """Cases, trials, and the two rates that have to be reported together."""

    def __init__(self, name, cases, *, trials=20, criterion_stated=True):
        attacks = [c for c in cases if not c.benign]
        benign = [c for c in cases if c.benign]
        if not attacks:
            raise CampaignError("a campaign with no attack cases")
        if not benign:
            raise CampaignError(
                "a campaign with no benign cases cannot produce a meaningful "
                "rate — a technique that fires on everything has a success "
                "rate of 1.0 and has found nothing")
        if not criterion_stated:
            raise CampaignError(
                "the criterion was not stated before the run")
        self.name = name
        self.cases = list(cases)
        self.trials_per_case = trials
        self.results = []

    def run(self, execute, *, arm="full"):
        """`execute(case) -> outcome`, called `trials` times per case."""
        for case in self.cases:
            for _ in range(self.trials_per_case):
                self.results.append(Trial(case, execute(case), arm=arm))
        return self

    def _rate(self, predicate, arm):
        rows = [t for t in self.results if t.arm == arm and predicate(t.case)]
        n = len(rows)
        k = sum(1 for t in rows if t.worked)
        return {"successes": k, "trials": n,
                "rate": round(k / n, 4) if n else None,
                "interval_95": wilson(k, n)}

    def attack_success_rate(self, arm="full"):
        return self._rate(lambda c: not c.benign, arm)

    def false_alarm_rate(self, arm="full"):
        """Benign cases the criterion counted as success. Reported beside the
        ASR, always — the pair is the result, and either one alone is a
        number somebody will quote without the other."""
        return self._rate(lambda c: c.benign, arm)

    def by_technique(self, arm="full"):
        out = {}
        for t in self.results:
            if t.arm != arm or t.case.benign:
                continue
            row = out.setdefault(t.case.technique, {"k": 0, "n": 0})
            row["n"] += 1
            row["k"] += int(t.worked)
        return {name: {"rate": round(r["k"] / r["n"], 4),
                       "interval_95": wilson(r["k"], r["n"]), **r}
                for name, r in sorted(out.items())}

    def report(self, arm="full"):
        asr = self.attack_success_rate(arm)
        far = self.false_alarm_rate(arm)
        return {
            "campaign": self.name, "arm": arm,
            "attack_success_rate": asr,
            "false_alarm_rate": far,
            # The number that decides whether the campaign found anything.
            # A technique that succeeds at 0.6 and misfires at 0.5 has an
            # advantage of 0.1, and the headline number was 0.6.
            "advantage": None if asr["rate"] is None or far["rate"] is None
            else round(asr["rate"] - far["rate"], 4),
            "by_technique": self.by_technique(arm),
        }

    def ablation(self, full_arm="full", bare_arm="bare"):
        """What the harness contributed, with the model held constant.

        Run the same cases twice: once through the scaffolding, once with the
        model alone. If the bare arm is close to the full arm, the result is a
        property of the model and will move when the model does. If the bare
        arm is near zero, you built the capability — which is worth knowing
        before you publish it as a model finding.
        """
        full = self.attack_success_rate(full_arm)
        bare = self.attack_success_rate(bare_arm)
        if full["rate"] is None or bare["rate"] is None:
            raise CampaignError(
                "an ablation needs both arms run; a campaign with one arm "
                "cannot say whether it measured the model or the scaffolding")
        return {
            "model_effect": bare["rate"],
            "harness_effect": round(full["rate"] - bare["rate"], 4),
            "full": full, "bare": bare,
            "reads_as": ("mostly the harness" if bare["rate"] < full["rate"] / 2
                         else "mostly the model"),
        }


def stability(rates):
    """Spread across repeated campaigns. A single campaign's interval covers
    sampling noise inside one run; this covers the run-to-run variance a
    non-deterministic target adds on top, and it is usually larger."""
    if len(rates) < 2:
        raise CampaignError("stability needs at least two campaigns — one run "
                            "cannot tell you how much a run varies")
    return {"runs": len(rates), "mean": round(statistics.mean(rates), 4),
            "stdev": round(statistics.stdev(rates), 4),
            "min": min(rates), "max": max(rates)}
