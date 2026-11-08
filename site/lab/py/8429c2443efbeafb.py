"""Ingress — where traveller text enters. Trust 0: unauthenticated until it is not.

Every injection risk in Function B begins on the edge out of this file.
"""
from .._stubs import route
from ..orchestrator.router import dispatch


@route("/chat")
def chat(request):
    """Free text from a traveller, plus whatever session they hold."""
    # Raw. By the time this reaches the model it is indistinguishable from
    # the operator's own instructions, which is B1.2.
    return dispatch(request.args["message"], session=request.session)


@route("/webhook/vendor")
def vendor_webhook(request):
    """A booking provider posts here. Nobody at CyberTravels wrote this text."""
    return dispatch(request.json["note"], session=None)
