"""Tools — the only components that change anything. Trust 3.

Four of the functions here take an identifier from the caller and return or
mutate the record it names. Which of them check that the caller owns that
record is the whole of the IDOR question, and it is not visible in any single
one of them: it is visible in the comparison between them.
"""
from .._stubs import DB


def require_owner(session, owner_id):
    """The ownership check. Present in this file; not called from everywhere."""
    if session is None or session.user_id != owner_id:
        raise PermissionError("not your record")


def get_booking(session, booking_id):
    """IDOR: the id comes from the caller and nothing compares it to the session."""
    cur = DB.cursor()
    cur.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    return cur.fetchone()


def get_my_booking(session, booking_id):
    """The same read, authorised. This is the shape the others should have."""
    row = DB.cursor().execute(
        "SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    require_owner(session, row["owner_id"] if row else None)
    return row


def cancel_booking(session, booking_id):
    """IDOR, and it writes: cancels whichever booking you name."""
    return DB.cursor().execute(
        "UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))


def search_bookings(session, reference):
    """SQL injection: the reference is concatenated to make partial search work."""
    cur = DB.cursor()
    cur.execute("SELECT * FROM bookings WHERE reference LIKE '%" + reference + "%'")
    return cur.fetchall()


def list_my_bookings(session):
    """Scoped by the session rather than by an argument. No id to tamper with."""
    return DB.cursor().execute(
        "SELECT * FROM bookings WHERE owner_id = ?", (session.user_id,)).fetchall()
