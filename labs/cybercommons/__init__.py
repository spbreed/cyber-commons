"""Cyber Commons — the shared lab library behind all 104 lesson notebooks.

Every module here is **standard library only**. That is a deliberate constraint,
not an accident of packaging: the notebooks have to run on a Kaggle kernel with
the internet switched off, on an air-gapped laptop, and in CI, without anyone
first negotiating a package mirror. If a lab needs a real external tool (Falco,
OPA, Keycloak, SPIRE) the notebook says so and models the *decision* the tool
makes, so the lesson still lands on a machine that cannot pull containers.

Layout
------
    planes      three planes, autonomy ladder, blast radius     M0, A1, A3, E1
    loop        plan-act-verify, verifiers, budgets, traces     M0, B2, D1
    injection   prompt-injection corpus and detector scoring    M0, A3, B1, C1
    identity    delegation chains, JIT authority, NHI registry  A2, C1
    sandbox     egress, path guards, tool permissions           A3, C1
    appsec      SAST triage, patch validation, SDLC metrics     B1
    evalkit     four-stage scoring, judges, conformance         B2, C1, C2, E1
    redteam     attack suites, success rate, finding reports    C1
    research    repro harness, supply chain, data provenance    C2
    soc         detections, triage quality, drift, attribution  D1
    ir          timelines, scoping, containment, replay         D2
    grc         inventory, risk tiering, control mapping        E1, E2, E3

Import in a notebook via the bootstrap cell, which puts the repository's `labs/`
directory on `sys.path` whether the notebook is running from a clone, from
Kaggle, or from the repository root.
"""

__version__ = "1.0.0"

__all__ = [
    "planes", "loop", "injection", "identity", "sandbox", "appsec",
    "evalkit", "redteam", "research", "soc", "ir", "grc",
]


def banner(session: str = "") -> str:
    """One line proving the library imported, printed at the top of every lab."""
    tag = f" · {session}" if session else ""
    return f"Cyber Commons lab library v{__version__}{tag} · stdlib only, no network"
