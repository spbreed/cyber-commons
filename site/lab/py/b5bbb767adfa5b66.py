"""Stage 11 — a disposable replica, and the refusal that makes it one.

Dynamic testing needs a running system. The path of least resistance is to
point it at staging, and staging is a shared environment with real integrations,
real queues and, often enough, a production database credential somebody left
in it. A destructive probe then becomes an incident, and the incident is
reported as a security team outage.

The replica is the answer, and it is not interesting technically: a fresh
SQLite file in a temporary directory, seeded, thrown away. What is interesting
is the **refusal**. `for_target()` will not build a replica pointed at anything
that looks like a shared environment, and it fails loudly rather than
defaulting to something safe-looking — because a stage that silently downgrades
is a stage whose output nobody can interpret.

Everything in the `after` half runs in here. That is what lets stage 12 say
"this was exploited" rather than "this is reachable".
"""
import os
import shutil
import tempfile
from pathlib import Path


class NotDisposable(Exception):
    """The target is not something we are allowed to attack."""


# Substrings that mean somebody else is using this. Deliberately a deny-list
# *and* an allow-list below: the deny-list catches the obvious, the allow-list
# is what actually decides, because a deny-list of environment names is a game
# of naming conventions that the next environment wins.
SHARED_MARKERS = ("staging", "stage", "prod", "production", "uat", "preprod",
                  "live", "shared")


class Replica:
    """A throwaway copy of the application's state."""

    def __init__(self, path, origin):
        self.path = path
        self.origin = origin
        self.closed = False

    def close(self):
        if not self.closed:
            shutil.rmtree(self.path, ignore_errors=True)
            self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def as_dict(self):
        return {"path": str(self.path), "origin": self.origin,
                "disposable": True, "network": "none"}


def assert_disposable(target):
    """Refuse anything that is not ours to break."""
    low = str(target).lower()
    for marker in SHARED_MARKERS:
        if marker in low:
            raise NotDisposable(
                f"{target!r} contains {marker!r} — this stage builds a replica "
                f"and attacks it, and a shared environment is not a replica. "
                f"Nothing about this is recoverable by being careful")
    return True


def for_target(target="local-replica"):
    """A fresh, empty, disposable root. Raises rather than degrading."""
    assert_disposable(target)
    return Replica(Path(tempfile.mkdtemp(prefix="ct-replica-")), target)


def isolated_db(replica):
    """Point the application's storage at the replica and seed it.

    This is the moment the `after` half starts importing the application it has
    so far only parsed, and it is worth noticing: from here the pipeline is
    running the defects rather than reading them.
    """
    from .. import config, db
    os.makedirs(replica.path / "data", exist_ok=True)
    config.DB_PATH = str(replica.path / "data" / "replica.db")
    db.reset()
    return db


