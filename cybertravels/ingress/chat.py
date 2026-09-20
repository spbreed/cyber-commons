"""Ingress — where traveller text enters. Trust 0: unauthenticated until it is not.

Every injection risk in Function B begins on the edge out of this file.
"""
from .._stubs import route
from ..orchestrator.router import dispatch
# step:B2.6 add
from ..provenance import mark
# step:B2.6 end


@route("/chat")
def chat(request):
    """Free text from a traveller, plus whatever session they hold."""
    # step:B2.6 was
    #~ # Raw. By the time this reaches the model it is indistinguishable from
    #~ # the operator's own instructions, which is B1.2.
    #~ return dispatch(request.args["message"], session=request.session)
    # step:B2.6 now
    # Marked at the boundary, which is the only place that honestly knows.
    # An authenticated traveller is still not authorised to redirect an agent.
    span = mark(request.args["message"], "traveller", source="/chat")
    return dispatch(span, session=request.session)
    # step:B2.6 end


@route("/webhook/vendor")
def vendor_webhook(request):
    """A booking provider posts here. Nobody at CyberTravels wrote this text."""
    # step:B2.6 was
    #~ return dispatch(request.json["note"], session=None)
    # step:B2.6 now
    span = mark(request.json["note"], "vendor-webhook", source="/webhook/vendor")
    return dispatch(span, session=None)
    # step:B2.6 end
