"""Workflow Agent — flights, hotels, payments and refunds, through MCP.

Holds scope booking.* and payments.refund. That is the authority every tool
call below inherits, which is what makes an unauthorised read on this path a
different severity from the same read on the advisor's.
"""
from ..mcp import internal_server
from ..tools import bookings_api, payments_api


def handle(message, session):
    plan = internal_server.plan_tools(message)
    out = []
    for step in plan:
        if step["tool"] == "get_booking":
            out.append(bookings_api.get_booking(session, step["args"]["id"]))
        elif step["tool"] == "cancel_booking":
            out.append(bookings_api.cancel_booking(session, step["args"]["id"]))
        elif step["tool"] == "issue_refund":
            out.append(payments_api.issue_refund(
                session, step["args"]["id"], step["args"]["amount"]))
        elif step["tool"] == "search":
            out.append(bookings_api.search_bookings(session, step["args"]["q"]))
    return out
