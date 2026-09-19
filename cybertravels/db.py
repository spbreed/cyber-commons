"""Storage — SQLite, seeded on first use, with an append-only audit log.

Replaces the stub the corpus used to carry. The tree used to be unrunnable on
purpose; it runs now, because a reader who has never watched an agent take an
action cannot reason about what to stop it doing. The defects stayed where
they were — see LABELS.md — they simply have real rows underneath them now.

Standard library only. `sqlite3` ships with Python.
"""
import hashlib
import json
import sqlite3
import time
from pathlib import Path

from . import config

_CONN = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS bookings (
  id INTEGER PRIMARY KEY, reference TEXT, owner_id TEXT, route TEXT,
  depart TEXT, status TEXT, amount REAL, vendor TEXT);
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY, booking_id INTEGER, owner_id TEXT, amount REAL,
  method TEXT);
CREATE TABLE IF NOT EXISTS refunds (
  id INTEGER PRIMARY KEY AUTOINCREMENT, booking_id INTEGER, amount REAL,
  at REAL);
CREATE TABLE IF NOT EXISTS policies (
  id INTEGER PRIMARY KEY, title TEXT, body TEXT);
-- Append-only: no UPDATE and no DELETE is ever issued against this table.
-- A log the workload can edit is a log that proves nothing, which is A2.8.
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, at REAL, chain TEXT, tool TEXT,
  audience TEXT, scope TEXT, outcome TEXT, detail TEXT, trace_id TEXT
-- step:A2.8 add
  -- A2.8: each row carries the hash of the one before it, so an edit anywhere
  -- breaks every hash after it. Append-only was a convention until here; this
  -- makes it detectable.
  , prev_hash TEXT, row_hash TEXT
-- step:A2.8 end
  );
CREATE TABLE IF NOT EXISTS memory (
  id INTEGER PRIMARY KEY AUTOINCREMENT, at REAL, owner_id TEXT, kind TEXT,
  content TEXT, origin TEXT, trusted INTEGER);
"""

SEED_BOOKINGS = [
    (1, "CT-4417", "dana",  "LHR->SIN", "2026-10-02", "confirmed", 890.0, "skyline-air"),
    (2, "CT-4418", "priya", "SFO->NRT", "2026-10-09", "confirmed", 1240.0, "skyline-air"),
    (3, "CT-4419", "dana",  "LHR->AMS", "2026-11-14", "confirmed", 210.0, "northwind-rail"),
    (4, "CT-4420", "alex",  "BOS->LHR", "2026-10-21", "cancelled", 640.0, "skyline-air"),
]
SEED_PAYMENTS = [
    (1, 1, "dana", 890.0, "corporate-card"),
    (2, 2, "priya", 1240.0, "corporate-card"),
    (3, 3, "dana", 210.0, "corporate-card"),
]
SEED_POLICIES = [
    (1, "Refunds for cancelled flights",
     "A cancelled flight is refundable in full when the vendor cancelled it. "
     "A traveller-initiated cancellation inside 24 hours of departure is "
     "refundable less the vendor fee. Refunds above 500 require a finance "
     "approver."),
    (2, "Rail changes",
     "Rail bookings may be changed once at no cost up to 1 hour before "
     "departure. No refund is due after departure."),
    (3, "Duty of care",
     "Any itinerary change that leaves a traveller without onward "
     "accommodation must raise a duty-of-care ticket before it is applied."),
]


def conn():
    """One connection, seeded on first open."""
    global _CONN
    if _CONN is None:
        Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
        _CONN = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        _CONN.row_factory = sqlite3.Row
        _CONN.executescript(SCHEMA)
        if not _CONN.execute("SELECT 1 FROM bookings LIMIT 1").fetchone():
            _CONN.executemany(
                "INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?)", SEED_BOOKINGS)
            _CONN.executemany(
                "INSERT INTO payments VALUES (?,?,?,?,?)", SEED_PAYMENTS)
            _CONN.executemany(
                "INSERT INTO policies VALUES (?,?,?)", SEED_POLICIES)
            _CONN.commit()
    return _CONN


def cursor():
    return conn().cursor()


def rows(result):
    """sqlite3.Row -> plain dicts, so a tool's return value is JSON-able.

    Takes a cursor OR an already-materialised list, because the tools in
    `tools/` are inconsistent about which they return and that inconsistency is
    load-bearing — they are the corpus the AppSec lessons scan, and tidying
    their shape would edit the defects. Calling `.fetchall()` on a list that a
    tool had already fetched silently returned nothing, which made a live SQL
    injection look like a control working.
    """
    if result is None:
        return []
    if hasattr(result, "fetchall"):
        result = result.fetchall()
    return [dict(r) for r in result]


def audit(chain, tool, audience, scope, outcome, detail="", trace_id=""):
    """Write one row. Never updated, never deleted — only appended.

    Every call is recorded, and so is every refusal. A log that records only
    what succeeded cannot answer the question an investigation actually asks,
    which is what was attempted.
    """
    c = conn()
    row = (time.time(), chain, tool, audience, scope, outcome,
           detail if isinstance(detail, str) else json.dumps(detail), trace_id)
    # step:A2.8 was
    #~ # Append-only by convention: this module simply never issues an UPDATE
    #~ # or a DELETE. Nothing stops anything else from doing so, and an
    #~ # attacker holding the agent's credentials holds the log's.
    #~ c.execute(
    #~     "INSERT INTO audit (at, chain, tool, audience, scope, outcome,"
    #~     " detail, trace_id) VALUES (?,?,?,?,?,?,?,?)", row)
    # step:A2.8 now
    prev = c.execute("SELECT row_hash FROM audit ORDER BY id DESC "
                     "LIMIT 1").fetchone()
    prev_hash = (prev["row_hash"] if prev else GENESIS) or GENESIS
    c.execute(
        "INSERT INTO audit (at, chain, tool, audience, scope, outcome,"
        " detail, trace_id, prev_hash, row_hash) VALUES (?,?,?,?,?,?,?,?,?,?)",
        row + (prev_hash, _row_hash(prev_hash, row)))
    # step:A2.8 end
    c.commit()


# step:A2.8 add
GENESIS = "0" * 64


def _row_hash(prev_hash, row):
    """The hash of this row, chained to the one before it.

    Canonical and ordered: a hash over a dict would depend on insertion order
    and two honest machines would disagree about whether the log was intact.
    """
    payload = json.dumps([prev_hash, *[str(v) for v in row]],
                         separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_audit_chain():
    """Recompute every hash. Returns (ok, first_broken_id).

    This is the property `append-only` was standing in for. It does not stop a
    write — nothing in the same trust domain can — but an edit, a deletion or
    an insertion anywhere in the log breaks every hash after it, and that is
    visible in one pass. A3.8 is where the log moves somewhere the workload
    cannot reach at all; this is what you can do without that.
    """
    prev = GENESIS
    for r in conn().execute(
            "SELECT id, at, chain, tool, audience, scope, outcome, detail,"
            " trace_id, prev_hash, row_hash FROM audit ORDER BY id"):
        row = (r["at"], r["chain"], r["tool"], r["audience"], r["scope"],
               r["outcome"], r["detail"], r["trace_id"])
        if r["prev_hash"] != prev or r["row_hash"] != _row_hash(prev, row):
            return False, r["id"]
        prev = r["row_hash"]
    return True, None
# step:A2.8 end


def recent_audit(limit=60):
    return rows(conn().execute(
        "SELECT * FROM audit ORDER BY id DESC LIMIT ?", (limit,)))


def reset():
    """Drop the file and re-seed. Used by the smoke test."""
    global _CONN
    if _CONN is not None:
        _CONN.close()
        _CONN = None
    p = Path(config.DB_PATH)
    if p.exists():
        p.unlink()
    return conn()
