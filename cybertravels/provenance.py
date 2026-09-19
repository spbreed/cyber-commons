"""Provenance — marking text with where it came from, at the door.

# step:file B2.6

Function G built a system that labels two of the three untrusted channels.
Memory entries carry an origin (`memory.py`) and peer messages carry one
(`a2a/protocol.py`). The third — **text arriving at ingress** — did not, and
that is the channel B1.2 and B1.3 attack.

`ingress/chat.py` took a string and passed it to the orchestrator. By the time
it reached the model it was indistinguishable from the operator's own
instructions, because in a token stream there is nothing to distinguish. The
system prompt asked the model not to follow instructions found in content; that
is a request, and B1.2 measures how far a request gets.

## What this module does

Every string entering the system becomes a `Span` carrying its origin, and the
runtime renders spans with the label attached rather than concatenating raw
text. Three properties, and the third is the one people skip:

**The origin is assigned at the boundary, not inferred later.** The only place
that honestly knows where a string came from is the handler that received it.
A classifier guessing afterwards is guessing.

**The label survives every hop.** A span handed to a peer agent stays marked;
`a2a` already carries `origin`, so the two systems agree rather than each
having their own idea of trust.

**Marking is not filtering.** A marked injection is still an injection. The
label does not stop the model reading the text — it makes the operator able to
see, in the trace, that the instruction came from a hotel description. B3.1 is
what actually refuses the resulting tool call. Treating the label as the
control is the mistake B2.6 exists to prevent, so it is worth saying plainly:
**this closes nothing on its own.** It makes the rest closeable.
"""
import html

# Which origins the system will let influence a plan. Everything else is
# recorded, rendered and clearly marked — the same list `memory.py` uses, and
# deliberately the same so the two cannot drift into disagreeing about whether
# a vendor document is trustworthy.
TRUSTED = {"operator", "policy", "agent-conclusion"}

# Origins seen at ingress, and what each one is.
ORIGINS = {
    "operator": "CyberTravels' own instructions to the agent",
    "traveller": "a person typing into the chat box — authenticated, and still "
                 "not authorised to redirect the agent",
    "vendor-webhook": "a booking provider posting to us. Nobody here wrote it",
    "vendor-document": "text inside a document we fetched",
    "policy": "CyberTravels' travel policy, which we wrote",
    "agent-conclusion": "something an agent worked out",
}


class Span:
    """One piece of text, and where it came from."""

    __slots__ = ("text", "origin", "trusted", "source")

    def __init__(self, text, origin, source=""):
        if origin not in ORIGINS:
            raise ValueError(f"unknown origin: {origin!r} — add it to ORIGINS "
                             f"rather than passing a new string, or the label "
                             f"means whatever the caller felt like")
        self.text = text
        self.origin = origin
        self.trusted = origin in TRUSTED
        self.source = source          # the URL, file or handler it arrived at

    def as_dict(self):
        return {"origin": self.origin, "trusted": self.trusted,
                "source": self.source, "chars": len(self.text)}

    def __repr__(self):
        return f"<Span {self.origin} {len(self.text)}ch trusted={self.trusted}>"


def mark(text, origin, source=""):
    return Span(text, origin, source)


def render(spans):
    """Spans -> the block the model sees, with every label attached.

    The delimiters matter as much as the labels. Text that can close its own
    block can forge the next one's label, so the content is escaped: a span
    claiming to be `[operator]` arrives as `&lt;operator&gt;` and reads as what
    it is, which is a traveller trying to promote themselves.
    """
    out = []
    for s in spans:
        tag = "trusted" if s.trusted else "UNTRUSTED"
        where = f" from={s.source}" if s.source else ""
        out.append(f"<<<{tag} origin={s.origin}{where}>>>\n"
                   f"{html.escape(s.text)}\n"
                   f"<<<end origin={s.origin}>>>")
    return "\n".join(out)


def untrusted(spans):
    """The spans an operator should be shown first when a run goes wrong."""
    return [s for s in spans if not s.trusted]
