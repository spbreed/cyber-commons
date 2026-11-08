"""The edges of the system: the database handle, an HTTP client, a route decorator.

This module used to stub all three, because the tree was a corpus for scanners
and nothing in it was meant to execute. It executes now — `DB` is a real SQLite
connection — and that changes what the defects in `tools/` mean. They were
descriptions of a vulnerability; they are the vulnerability.

`HTTP` is still a stub, deliberately. `sync_vendor` disables TLS verification,
and a corpus that actually made that request would be reaching a host on the
internet with verification off, from a machine belonging to somebody who cloned
a teaching repository. The defect stays readable and stays unexploitable, which
is the right trade for that one.
"""
from . import db as _db

# The real thing. `DB.cursor()` returns a live sqlite3 cursor, so the SQL
# injection in `search_bookings` is an injection rather than a picture of one.
DB = _db


class _HTTP:
    """Deliberately inert — see the module docstring."""

    def get(self, url, **kw):
        return {"url": url, "verify": kw.get("verify", True), "body": "{}"}

    def post(self, url, **kw):
        return {"url": url, "verify": kw.get("verify", True), "body": "{}"}


HTTP = _HTTP()


def route(path):
    """The framework's handler decorator. An entry point, in B1.1's language."""
    def wrap(fn):
        fn.__route__ = path
        return fn
    return wrap
