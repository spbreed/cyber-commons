"""Orchestrator — decides which agent handles what. Holds no authority itself."""
from ..agents import coding_agent, file_agent, rag_advisor, workflow_agent

AGENTS = {
    "book": workflow_agent.handle,
    "recommend": rag_advisor.handle,
    "patch": coding_agent.handle,
    "invoice": file_agent.handle,
}


def dispatch(message, session=None):
    intent = _classify(message)
    return AGENTS[intent](message, session)


def _classify(message):
    for word, intent in (("book", "book"), ("hotel", "recommend"),
                         ("patch", "patch"), ("invoice", "invoice")):
        if word in message.lower():
            return intent
    return "recommend"
