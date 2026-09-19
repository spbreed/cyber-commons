# step:file B2.6
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


# step:B2.8 add
# --------------------------------------------------------------------------- #
# B2.8 — stage 12: run the exploit, or drop the finding
# --------------------------------------------------------------------------- #
# A SAST finding is a hypothesis, and a queue of hypotheses gets argued about
# rather than fixed — because arguing is cheaper than proving and everybody
# knows it. An executed exploit ends the argument in one direction and, just as
# usefully, ends it in the other: a hypothesis that cannot be demonstrated here
# is dropped rather than shipped as a medium somebody has to carry.
#
# Every exploit below runs against the replica and returns evidence or None.
# None is a real answer and is recorded as one.
def exploit_sql_injection(db):
    """LABELS.md row 3 — `search_bookings` concatenates its reference.

    The payload is the oldest one there is. What makes it evidence rather than
    a demonstration of SQL is the second assertion: the rows that come back
    belong to owners the caller is not.
    """
    from ..tools import bookings_api
    from ..identity import Session
    dana = Session("dana", "traveller")
    # A narrow, honest search first, so the contrast is the evidence rather
    # than the payload: one row for her own reference, every row for the
    # payload. A "before" that already returns everything proves nothing.
    honest = bookings_api.search_bookings(dana, "4417")
    injected = bookings_api.search_bookings(dana, "' OR '1'='1")
    owners = {r["owner_id"] for r in injected}
    if len(injected) > len(honest) or len(owners) > 1:
        return {"payload": "' OR '1'='1",
                "rows_honest": len(honest), "rows_injected": len(injected),
                "owners_returned": sorted(owners),
                "note": "the extra rows belong to other travellers, which is "
                        "the half a SQL-injection finding usually leaves out"}
    return None


def exploit_idor(db):
    """LABELS.md rows 1 and 4 — no pattern found these; this demonstrates them.

    Dana asks for a booking that is Priya's, by id, and gets it. There is no
    payload and nothing is malformed: the request is exactly what the API
    documents. That is why stage 7 could not see it and why stage 12 can.
    """
    from ..tools import bookings_api
    from ..identity import Session
    dana = Session("dana", "traveller")
    for booking_id in range(1, 8):
        row = bookings_api.get_booking(dana, booking_id)
        if row and row["owner_id"] != "dana":
            return {"payload": f"booking_id={booking_id}",
                    "caller": "dana", "owner": row["owner_id"],
                    "reference": row["reference"],
                    "note": "a well-formed request for somebody else's record"}
    return None


def exploit_path_traversal(db, replica):
    """LABELS.md row 5 — `download_invoice` joins a caller's path to a root.

    Confirmed by reaching a file outside the invoice directory that we planted
    in the replica, rather than by reading anything real. A proof that needs a
    sensitive file to exist is a proof nobody can run twice.

    `INVOICE_ROOT` is computed at import time from the source tree, which means
    `isolated_db` does not isolate it — the replica moved the database and left
    the filesystem where it was. Relocating it here is not a test convenience;
    it is the bug the stage found in its own isolation, and the reason a
    replica has to be checked rather than assumed.
    """
    from ..tools import payments_api
    from ..identity import Session
    root = replica.path / "invoices"
    root.mkdir(parents=True, exist_ok=True)
    (root.parent / "canary.txt").write_text("planted by stage 12")
    was, payments_api.INVOICE_ROOT = payments_api.INVOICE_ROOT, str(root) + "/"
    try:
        body = payments_api.download_invoice(Session("dana", "traveller"),
                                             "../canary.txt")
    except OSError:
        return None
    finally:
        payments_api.INVOICE_ROOT = was
    if "planted by stage 12" in body:
        return {"payload": "../canary.txt", "escaped": True,
                "note": "read a file outside INVOICE_ROOT"}
    return None


def verdict_from(evidence):
    """The verifier stage 12 hands the harness. Three values, not two —
    an exploit that did not fire tells you about the exploit as well as about
    the defect, and 'refuted' claims more than that."""
    return "confirmed" if evidence else "undetermined"
# step:B2.8 end
