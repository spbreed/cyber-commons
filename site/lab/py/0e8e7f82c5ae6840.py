"""Agent-to-agent messaging. A peer's message is not a colleague's instruction."""

INBOX = {}


def send(to_agent, message, from_agent):
    INBOX.setdefault(to_agent, []).append({"from": from_agent, "text": message})


def receive(agent):
    """No provenance on the message: the reader cannot tell who wrote the text."""
    return INBOX.pop(agent, [])
