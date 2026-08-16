"""Security research as a repeatable process: reproduce, generalise, hand over.

Research that cannot be reproduced is an anecdote, and research that ends in a
finding rather than a control is a hobby. The primitives here follow that arc:

    Repro        a claim plus the exact conditions it holds under
    trial()      run it N times — flaky reproduction is the normal case
    Supply       dependency provenance and the typosquat check
    to_control() the step that turns a finding into something that ships

`trial` is deterministic via a seeded PRNG, so the notebooks give the same
numbers on every machine while still showing genuine flakiness.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from typing import Callable


# ------------------------------------------------------------------- repro
@dataclass
class Repro:
    """One reproducible claim. The fields are the ones a reviewer will ask for."""
    claim: str
    setup: str
    trigger: str
    observed: str
    conditions: dict = field(default_factory=dict)

    def card(self) -> str:
        cond = "\n".join(f"    {k:16s} {v}" for k, v in self.conditions.items())
        return (f"CLAIM     {self.claim}\n"
                f"SETUP     {self.setup}\n"
                f"TRIGGER   {self.trigger}\n"
                f"OBSERVED  {self.observed}\n"
                f"HOLDS WHEN\n{cond}")


def trial(effect: Callable[[random.Random], bool], n: int = 100, seed: int = 7) -> dict:
    """Run a stochastic effect n times and report the rate with a crude interval.

    A single successful jailbreak is not a result. The rate is the result, and
    the rate is what changes when a mitigation lands.
    """
    rng = random.Random(seed)
    hits = sum(effect(rng) for _ in range(n))
    rate = hits / n
    # normal approximation — good enough to stop anyone quoting 1/1 as 100%
    half = 1.96 * ((rate * (1 - rate) / n) ** 0.5) if n else 0.0
    return {"trials": n, "hits": hits, "rate": round(rate, 3),
            "ci95": (round(max(rate - half, 0), 3), round(min(rate + half, 1), 3)),
            "verdict": "reproducible" if rate > 0.5 else
                       "flaky" if rate > 0.05 else "not reproduced"}


# ------------------------------------------------------------- supply chain
@dataclass(frozen=True)
class Package:
    name: str
    version: str
    sha256: str = ""
    signed: bool = False
    downloads: int = 0
    age_days: int = 999


KNOWN_GOOD = {"requests", "urllib3", "numpy", "pandas", "cryptography",
              "pytest", "flask", "django", "scikit-learn", "colorama"}


def levenshtein(a: str, b: str) -> int:
    """Small, exact, stdlib. Typosquats live at distance 1–2 from a popular name."""
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def typosquat_check(pkg: Package, known: set[str] | None = None) -> dict:
    """Is this name suspiciously close to something popular?"""
    known = known or KNOWN_GOOD
    if pkg.name in known:
        return {"package": pkg.name, "suspicious": False, "reason": "exact known-good name"}
    near = sorted(((levenshtein(pkg.name, k), k) for k in known))[:1]
    if near and near[0][0] <= 2:
        return {"package": pkg.name, "suspicious": True,
                "reason": f"distance {near[0][0]} from popular package {near[0][1]!r}",
                "nearest": near[0][1]}
    return {"package": pkg.name, "suspicious": False, "reason": "no near neighbour"}


def provenance(pkg: Package) -> dict:
    """The signals that actually predict a bad dependency, and their verdict."""
    flags = []
    if not pkg.signed:
        flags.append("unsigned — no attestation linking artefact to source")
    if pkg.age_days < 30:
        flags.append(f"published {pkg.age_days}d ago — no soak time")
    if pkg.downloads < 1000:
        flags.append(f"only {pkg.downloads} downloads — no community scrutiny")
    sq = typosquat_check(pkg)
    if sq["suspicious"]:
        flags.append(sq["reason"])
    return {"package": f"{pkg.name}=={pkg.version}", "flags": flags,
            "verdict": "block" if len(flags) >= 3 else "review" if flags else "allow"}


# ------------------------------------------------------------- data layer
def poison_rate(dataset: list[str], poisoned: set[str]) -> dict:
    """How little poisoned data is needed to matter — usually a shocking amount less
    than people expect, which is why provenance beats volume."""
    n = len(dataset)
    bad = sum(1 for d in dataset if d in poisoned)
    return {"records": n, "poisoned": bad,
            "rate": round(bad / n, 5) if n else 0.0,
            "note": "published attacks land well under 1% of a corpus"}


def content_hash(text: str) -> str:
    """Provenance you can check later. A corpus without hashes cannot be audited."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


# ----------------------------------------------------- finding → control
def to_control(finding: str, surface: str) -> dict:
    """C2.8. A finding becomes institutional capital only when it ships as one of
    these: a control, a detection, an eval case, or a documented accepted risk."""
    return {
        "finding": finding,
        "control": f"preventive change on the {surface} surface",
        "detection": f"telemetry rule that fires when the {surface} precondition recurs",
        "eval_case": "a regression case added to the harness so it cannot silently return",
        "accepted_risk": "written down with an owner and a review date, if none of the above",
        "test": "the finding is closed when the eval case fails on the old build "
                "and passes on the new one",
    }
