"""What CyberTravels ingests, from whom — and what happens when you write to it.

Two lessons in one file, because they are the same surface read twice. D1.1
inventories the paths by which text that somebody else wrote reaches the
agent's context. D1.2 writes to one of them and measures how far it gets.

The inventory is the part teams think they already have. They have a list of
*integrations* — the vendor API, the knowledge base, the ticket system. What
they do not have is the column that matters: **who can write into this, and
what does the agent do with what it finds there.** A vendor API nobody can
write to is an integration. A knowledge corpus any support agent can add a
row to is an ingestion path, and it is the one with no review on it.

CyberTravels has four, and they are not equally guarded:

    knowledge/retriever.py   CORPUS      anyone who can add a template
    mcp/vendor_server.py     VENDOR_DOCS the vendor, who is a third party
    memory.py                per person  whatever a previous run recorded
    ingress/chat.py          the request the traveller just typed

The third is the one people miss. Memory is an ingestion path with a delay:
text written in one run is read as context in the next, and the boundary
between "what the traveller said" and "what the system knows" is a row in a
table that a previous run wrote.
"""
import ast
import re
from pathlib import Path


class Path_:
    """One way text somebody else wrote reaches the agent."""

    __slots__ = ("name", "file", "writer", "reaches", "reviewed", "labelled")

    def __init__(self, name, file, writer, reaches, *, reviewed=False,
                 labelled=False):
        self.name = name
        self.file = file
        self.writer = writer          # who can put text here
        self.reaches = reaches        # which agent reads it
        self.reviewed = reviewed      # does a human see it before the agent
        self.labelled = labelled      # does it arrive marked as untrusted

    def as_dict(self):
        return {"path": self.name, "file": self.file, "writer": self.writer,
                "reaches": self.reaches, "human_reviewed": self.reviewed,
                "labelled_untrusted": self.labelled,
                # The row an assessor stops on: nobody reviews it and it is
                # not labelled, so it reaches the model looking like policy.
                "unreviewed_and_unlabelled": not self.reviewed
                and not self.labelled}


PATHS = [
    Path_("knowledge corpus", "knowledge/retriever.py",
          "anyone who can add a travel template", "RAG Advisor",
          reviewed=False, labelled=False),
    Path_("vendor documents", "mcp/vendor_server.py",
          "the vendor — a third party", "Workflow Agent",
          reviewed=False, labelled=True),
    Path_("agent memory", "memory.py",
          "a previous run, on behalf of whoever spoke to it", "every agent",
          reviewed=False, labelled=True),
    Path_("chat", "ingress/chat.py",
          "the traveller", "Workflow Agent",
          reviewed=False, labelled=True),
]


def inventory(root=None):
    """The paths, worst first. The ordering is the finding."""
    rows = [p.as_dict() for p in PATHS]
    if root:                     # confirm each named file is still there
        for row in rows:
            row["present"] = (Path(root) / row["file"]).is_file()
    return sorted(rows, key=lambda r: (not r["unreviewed_and_unlabelled"],
                                       r["path"]))


def unlabelled(root=None):
    """The paths whose text arrives with nothing marking it as data.

    D1.1's Day 2 number, and the one that predicts D1.2's result: text that
    arrives labelled can still be followed, but text that arrives unlabelled
    has no control between it and the model at all.
    """
    return [r["path"] for r in inventory(root) if not r["labelled_untrusted"]]


