"""RAG Travel Advisor — itineraries from templates in a vector store."""
from ..knowledge import retriever


def handle(message, session):
    docs = retriever.search(message)
    return _render(message, docs)


def _render(message, docs):
    """The retrieved text is concatenated straight into the window.

    Trust 0 content reaching a component with authority, with nothing marking
    which spans a traveller wrote and which the corpus did.
    """
    return "\n".join([message] + [d["text"] for d in docs])
