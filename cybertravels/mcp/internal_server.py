"""Internal MCP server — tool orchestration for the Workflow Agent."""

TOOLS = [
    {"name": "get_booking", "description": "Read a booking by id"},
    {"name": "cancel_booking", "description": "Cancel a booking by id"},
    {"name": "issue_refund", "description": "Refund a booking"},
    {"name": "search", "description": "Search bookings by reference"},
]


def plan_tools(message):
    """A stub planner. In the real system the model chooses these."""
    if "refund" in message.lower():
        return [{"tool": "issue_refund", "args": {"id": "B-1", "amount": 500}}]
    if "cancel" in message.lower():
        return [{"tool": "cancel_booking", "args": {"id": "B-1"}}]
    return [{"tool": "search", "args": {"q": message}}]
