"""Ingress — where traveller text enters. Trust 0: unauthenticated until it is not.

Every injection risk in Function B begins on the edge out of this file.
"""
from .._stubs import route
from ..orchestrator.router import dispatch
from ..provenance import mark


@route("/chat")
def chat(request):
    """Free text from a traveller, plus whatever session they hold."""
    # Marked at the boundary, which is the only place that honestly knows.
    # An authenticated traveller is still not authorised to redirect an agent.
    span = mark(request.args["message"], "traveller", source="/chat")
    return dispatch(span, session=request.session)


@route("/webhook/vendor")
def vendor_webhook(request):
    """A booking provider posts here. Nobody at CyberTravels wrote this text."""
    span = mark(request.json["note"], "vendor-webhook", source="/webhook/vendor")
    return dispatch(span, session=None)
