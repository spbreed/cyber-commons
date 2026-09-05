"""Stubs, so the tree parses and imports without a network or a database.

A corpus for scanners has to be readable by a scanner, which means it has to be
syntactically real. It does not have to work. Every external edge is a stub
here, so nothing in this repository can reach anything.
"""


class _Cursor:
    def execute(self, *a, **k):
        return self

    def fetchall(self):
        return []

    def fetchone(self):
        return None


class _DB:
    def cursor(self):
        return _Cursor()

    def execute(self, *a, **k):
        return _Cursor()


DB = _DB()


class _HTTP:
    def get(self, *a, **k):
        return {}

    def post(self, *a, **k):
        return {}


HTTP = _HTTP()


def route(path):
    """The framework's handler decorator. An entry point, in A1.1's language."""
    def wrap(fn):
        fn.__route__ = path
        return fn
    return wrap
