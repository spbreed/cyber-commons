"""Orchestrator — decides which agent handles what. Holds no authority itself."""
from ..agents import coding_agent, file_agent, rag_advisor, workflow_agent

AGENTS = {
    "book": workflow_agent.handle,
    "recommend": rag_advisor.handle,
    "patch": coding_agent.handle,
    "invoice": file_agent.handle,
}


def dispatch(message, session=None):
    # step:A2.6 add
    # `message` is a provenance.Span from A2.6 onward. Routing reads the text;
    # the label travels with it to the runtime, which renders it for the model.
    text = getattr(message, "text", message)
    intent = _classify(text)
    return AGENTS[intent](message, session)
    # step:A2.6 end
    # step:A2.6 was
    #~ intent = _classify(message)
    #~ return AGENTS[intent](message, session)
    # step:A2.6 end


def _classify(message):
    for word, intent in (("book", "book"), ("hotel", "recommend"),
                         ("patch", "patch"), ("invoice", "invoice")):
        if word in message.lower():
            return intent
    return "recommend"
