# step:file B2.5
"""Stage 10 — can an external caller actually get here?

A finding in dead code costs exactly what a finding on the money path costs:
somebody reads it, thinks about it, writes a ticket, and argues about the
severity. The only difference is that at the end of that the answer is no.
Ordering the queue by severity does not help, because severity was assigned
before anybody asked this question.

So ask it, mechanically, before anyone is paged. The walk is an AST call graph
from the entry points outward, which is cheap, runs in milliseconds, and is
wrong in a specific and honest direction: **it over-approximates.** Dynamic
dispatch, a name looked up in a dict, a handler resolved by string — this does
not follow any of them, so a unit it calls unreachable may be reachable by a
route it cannot see.

That direction matters and it decides how the result is used. Over-approximate
reachability is safe to *rank* with and unsafe to *drop* with. So nothing here
deletes a finding. `classify` marks it, the report says which, and a reviewer
decides — which is B2.11's rule stated as code: unreachable sinks are reported
as unreachable rather than dropped.
"""
import ast
from pathlib import Path


class Graph:
    """Who calls whom, by unqualified name.

    Names rather than qualified paths, because resolving an import graph to
    decide whether `handle` means the Coding Agent's or the File System Agent's
    is a bigger analysis than this stage is worth. Four functions are called
    `handle` in this tree and they collapse to one node.

    The collapse has to be a **union**, and this is the one place the direction
    is easy to get backwards. The first version assigned `calls[name]`, so the
    last `handle` parsed overwrote the other three and the walk reported
    `_open_branch` and `download_invoice` — both called from a `handle` — as
    unreachable. That is under-approximation, which is the dangerous side: it
    hides live defects behind a clean stage. Unioning makes the node reachable
    if *any* `handle` reaches it, which over-approximates, which is the side
    this stage is allowed to be wrong on.
    """

    def __init__(self):
        self.calls = {}          # unit -> every name any definition calls
        self.defined = {}        # unit -> the files it is defined in
        self.entries = set()     # units reachable from outside

    def add_file(self, path, rel):
        try:
            tree = ast.parse(path.read_text())
        except (OSError, SyntaxError):
            return
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            self.defined.setdefault(node.name, set()).add(rel)
            called = set()
            for c in ast.walk(node):
                if isinstance(c, ast.Call):
                    f = c.func
                    if isinstance(f, ast.Name):
                        called.add(f.id)
                    elif isinstance(f, ast.Attribute):
                        called.add(f.attr)
            self.calls.setdefault(node.name, set()).update(called)
            if self._is_entry(node, rel):
                self.entries.add(node.name)

    @staticmethod
    def _is_entry(node, rel):
        """Where the walk starts — B2.2's answer, not a second one.

        The threat model already had to decide what an entry point is. Asking
        the question again here would give two stages their own idea of where
        the system begins, and they would disagree the first time somebody
        added a decorator to one of the two lists.
        """
        from .threatmodel import is_entry_point
        return is_entry_point(node, rel)

    def reachable(self):
        """Everything the entry points can get to, transitively."""
        seen, stack = set(), list(self.entries)
        while stack:
            unit = stack.pop()
            if unit in seen:
                continue
            seen.add(unit)
            stack.extend(self.calls.get(unit, ()))
        return seen


def build(root, parts=("ingress", "agents", "tools", "knowledge", "mcp",
                       "orchestrator", "messaging")):
    g = Graph()
    root = Path(root)
    for part in parts:
        d = root / part
        if not d.exists():
            continue
        for path in sorted(d.rglob("*.py")):
            g.add_file(path, str(path.relative_to(root)))
    return g


def classify(findings, graph):
    """Mark each finding reachable or not. Marks; never drops."""
    live = graph.reachable()
    for f in findings:
        reachable = f.unit in live
        f.evidence.append(
            f"reachability: {'reachable from an entry point' if reachable else 'no entry point reaches it'}"
        )
    return {f.unit: (f.unit in live) for f in findings}


def report(findings, graph):
    """What stage 10 hands the next stage, and what it costs to say it.

    The two numbers worth printing are here rather than a single 'filtered'
    count: how many were set aside, and — the one that keeps this honest —
    that they were set aside by an analysis that over-approximates.
    """
    live = graph.reachable()
    unreachable = [f for f in findings if f.unit not in live]
    return {
        "findings": len(findings),
        "reachable": len(findings) - len(unreachable),
        "unreachable": len(unreachable),
        "unreachable_units": sorted({f.unit for f in unreachable}),
        "entry_points": sorted(graph.entries),
        "caveat": "this walk does not follow dynamic dispatch, so unreachable "
                  "means 'no static path was found', not 'cannot be called'. "
                  "Rank with it; do not delete with it.",
    }
