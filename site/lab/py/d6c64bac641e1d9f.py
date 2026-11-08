"""File System Agent — OCR on vendor PDFs, then updates backend APIs."""
from ..tools import payments_api


def handle(message, session):
    return payments_api.download_invoice(session, message.strip())


def render_template(template, booking):
    """eval on a customer-supplied itinerary template."""
    return eval(template, {"booking": booking})
