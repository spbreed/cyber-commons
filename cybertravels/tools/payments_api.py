"""Payments — charge, and refund. The tool that moves money."""
from .._stubs import DB
from .bookings_api import require_owner


def issue_refund(session, booking_id, amount):
    """IDOR on the money path: refunds against any booking id supplied."""
    DB.cursor().execute(
        "INSERT INTO refunds (booking_id, amount) VALUES (?, ?)",
        (booking_id, amount))
    return {"refunded": amount, "booking": booking_id}


def get_receipt(session, payment_id):
    """Authorised: the payment is loaded, then its owner is compared."""
    row = DB.cursor().execute(
        "SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
    require_owner(session, row["owner_id"] if row else None)
    return row


def download_invoice(session, path):
    """Path traversal: the vendor's filename is trusted."""
    return open("/var/invoices/" + path).read()
