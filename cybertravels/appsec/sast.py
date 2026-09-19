# step:file C2.3
"""Stage 7 — deterministic rules first, then the pass a rule cannot express.

Two passes, and the split is not a preference. It follows from a property of
the defects themselves, which `cybertravels/LABELS.md` records in a column
before any scan is run: **is this defect expressible as a pattern?** Three
values, and the middle one is why mature codebases scan cleaner than they are.

    yes      a pattern matches it              search_bookings, _open_branch,
                                               render_template, download_invoice
    library  a pattern matches it *in a        sync_vendor — `verify=False` on
             library the rule knows*           CyberTravels' own HTTP wrapper,
                                               and every registry rule for this
                                               names `requests`
    no       the defect is the absence of      get_booking, cancel_booking,
             a call — no syntax to match       issue_refund

The deterministic pass below finds the `yes` rows and, with `WRAPPERS`
declared, the `library` row. It finds **none** of the `no` rows, and that is
not a gap to close by widening the rules. There is nothing to widen towards:
`get_booking` and `get_my_booking` are the same six lines, and the difference
is whether an ownership comparison happens between loading the record and
returning it. No pattern distinguishes them, at any width, ever. That is what
the model pass is for, and it is the only part of this file a model touches.

What a deterministic rule gives you that a model does not is worth naming,
because the fashion runs the other way: it is the same answer every run, it
costs milliseconds, it cites a line, and when it is wrong it is wrong the same
way every time, which is a thing you can fix once.

Nothing here imports the application. It parses it.
"""
import ast
from pathlib import Path

from .findings import Finding

# The corpus the pipeline scans. `appsec/` is deliberately included when the
# caller asks for the whole tree — see the package docstring on why a pipeline
# that exempts itself is the expensive kind.
CORPUS = ("tools", "agents", "knowledge")

# House wrappers around libraries a registry rule would name. This one line is
# the whole of the `library` row: without it, `sync_vendor` disables TLS
# verification in plain sight and every off-the-shelf rule for CWE-295 misses
# it, because they are written against `requests`.
WRAPPERS = {"HTTP": "requests"}


class Rule:
    """A deterministic rule, carrying what it can and cannot reach."""

    def __init__(self, rid, cwe, expressible, why):
        self.rid = rid
        self.cwe = cwe
        self.expressible = expressible
        self.why = why

    def __repr__(self):
        return f"<Rule {self.rid} {self.cwe} {self.expressible}>"


RULES = [
    Rule("sql-concat", "CWE-89", "yes",
         "a value is interpolated or concatenated into a SQL string"),
    Rule("shell-true", "CWE-78", "yes",
         "subprocess with shell=True"),
    Rule("eval-call", "CWE-95", "yes",
         "eval() on a value"),
    Rule("path-join", "CWE-22", "yes",
         "a filesystem root concatenated with a caller's value"),
    Rule("tls-off", "CWE-295", "library",
         "verify=False — matched here because WRAPPERS names the house client"),
]


# --------------------------------------------------------------------------- #
# A miniature taint question: does this expression derive from a parameter?
# --------------------------------------------------------------------------- #
# Small on purpose. It answers one question — is the interpolated value under
# the caller's control, or is it a local literal — and that question is the
# entire difference between `search_bookings` (a real injection) and
# `db.audit`'s column list (an f-string a scanner flags and a reviewer clears).
# A pipeline without it reports both and asks a human to tell them apart, which
# is stage 8 and 9's cost measured in somebody's afternoon.
def _names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _params_of(fn):
    a = fn.args
    return {p.arg for p in (*a.posonlyargs, *a.args, *a.kwonlyargs)
            } | ({a.vararg.arg} if a.vararg else set()) | (
                {a.kwarg.arg} if a.kwarg else set())


def _local_literals(fn):
    """Names bound in this function to something with no free variables —
    a literal, or a comprehension over literals."""
    out = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Name):
            if all(isinstance(c, (ast.Constant, ast.List, ast.Tuple, ast.Set))
                   for c in [node.value]):
                out.add(node.targets[0].id)
    return out


def tainted(expr, fn):
    """True when the expression reaches a parameter of the enclosing function."""
    return bool(_names_in(expr) & _params_of(fn))


# --------------------------------------------------------------------------- #
# The pass itself
# --------------------------------------------------------------------------- #
def _enclosing(tree):
    """node id -> the function that contains it. An AST has no parent
    pointers, so a finding could otherwise name a line and no unit."""
    owner = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(fn):
                owner.setdefault(id(node), fn)
    return owner


def _is_sql_string(node):
    """An f-string or a concatenation that looks like SQL."""
    if isinstance(node, ast.JoinedStr):
        text = "".join(v.value for v in node.values
                       if isinstance(v, ast.Constant) and
                       isinstance(v.value, str))
        return any(k in text.upper() for k in ("SELECT", "INSERT", "UPDATE",
                                               "DELETE"))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        text = " ".join(c.value for c in ast.walk(node)
                        if isinstance(c, ast.Constant) and
                        isinstance(c.value, str))
        return any(k in text.upper() for k in ("SELECT", "INSERT", "UPDATE",
                                               "DELETE"))
    return False


def scan_file(path, rel):
    """Every deterministic rule, over one file."""
    try:
        tree = ast.parse(path.read_text())
    except (OSError, SyntaxError):
        return []
    owner = _enclosing(tree)
    out = []

    def add(rid, node, detail):
        rule = next(r for r in RULES if r.rid == rid)
        fn = owner.get(id(node))
        out.append(Finding(rel, node.lineno, fn.name if fn else "<module>",
                           rule.cwe, basis=f"rule:{rid}", stage=7,
                           detail=detail))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = owner.get(id(node))
        func = node.func

        # CWE-89
        if isinstance(func, ast.Attribute) and func.attr == "execute":
            for arg in node.args[:1]:
                if _is_sql_string(arg):
                    add("sql-concat", node,
                        "caller value in the query" if fn and tainted(arg, fn)
                        else "interpolated SQL, operands are local literals")

        # CWE-78
        if any(isinstance(k.value, ast.Constant) and k.value.value is True
               for k in node.keywords if k.arg == "shell"):
            add("shell-true", node, "shell=True")

        # CWE-95
        if isinstance(func, ast.Name) and func.id == "eval":
            add("eval-call", node, "eval() on a value")

        # CWE-22 — a root constant concatenated with something else
        if isinstance(func, ast.Name) and func.id == "open" and node.args:
            a = node.args[0]
            if isinstance(a, ast.BinOp) and isinstance(a.op, ast.Add) and \
                    any(n.id.isupper() for n in ast.walk(a)
                        if isinstance(n, ast.Name)):
                add("path-join", node, "a root constant joined to a value")

        # CWE-295 — only reached because WRAPPERS names the house client
        if any(k.arg == "verify" and isinstance(k.value, ast.Constant)
               and k.value.value is False for k in node.keywords):
            recv = func.value.id if isinstance(func, ast.Attribute) and \
                isinstance(func.value, ast.Name) else ""
            if recv in WRAPPERS:
                add("tls-off", node,
                    f"verify=False on {recv}, a house wrapper around "
                    f"{WRAPPERS[recv]} — a rule naming the library misses this")
    return out


def scan(root, parts=CORPUS):
    """The deterministic pass over the tree. Same answer every run."""
    root = Path(root)
    out = []
    for part in parts:
        for path in sorted((root / part).rglob("*.py")):
            out.extend(scan_file(path, str(path.relative_to(root))))
    return sorted(out, key=lambda f: (f.file, f.line))


def unreachable_by_pattern():
    """What this pass structurally cannot find, stated rather than discovered.

    A pipeline that does not publish this is a pipeline whose clean run reads
    as an absence of defects. Every id here is a row of LABELS.md whose
    `pattern?` column is `no`.
    """
    return [
        ("tools/bookings_api.py", "get_booking", "CWE-639"),
        ("tools/bookings_api.py", "cancel_booking", "CWE-639"),
        ("tools/bookings_api.py", "search_bookings", "CWE-639"),
        ("tools/payments_api.py", "issue_refund", "CWE-639"),
        ("tools/payments_api.py", "download_invoice", "CWE-639"),
    ]


def model_pass_prompt(finding_sites):
    """What the model pass is asked, and what it is not asked.

    It is not asked "find the bugs". It is given the units that take an
    identifier and return a record, and asked one comparative question, because
    the defect is only visible in the comparison. The answer is a hypothesis
    and is recorded as basis `model:` so nothing downstream mistakes it for a
    pattern match.
    """
    return (
        "For each unit below, say whether an ownership comparison happens "
        "between loading the record and returning it. Answer per unit with "
        "yes, no, or cannot-tell. Do not report anything else.\n\n"
        + "\n".join(f"- {f}::{u}" for f, u in finding_sites))


# step:C2.17 add
# --------------------------------------------------------------------------- #
# C2.17 — stage 6: the smallest context that still supports a decision
# --------------------------------------------------------------------------- #
# The instinct is to give the model the repository and ask it to be thorough.
# What that produces is a window in which the relevant six lines are 2% of the
# input, and a model that reports the defects it can see rather than the ones
# that are there.
#
# Slicing on distance — "the function, plus fifty lines either side" — is the
# wrong axis. The right one is the path: the sink, the parameter that reaches
# it, and the units on the route from an entry point. For the IDOR class the
# slice has to include the *authorised twin*, because the defect is the
# difference between them and a slice containing only one of the pair cannot
# show it.
TWINS = {
    "get_booking": "get_my_booking",
    "cancel_booking": "get_my_booking",
    "issue_refund": "get_receipt",
    "download_invoice": "get_receipt",
}


def slice_for(root, finding, *, twin=True):
    """The source of the unit, its authorised twin, and nothing else."""
    path = Path(root) / finding.file
    try:
        tree = ast.parse(path.read_text())
    except (OSError, SyntaxError):
        return ""
    want = {finding.unit}
    if twin and finding.unit in TWINS:
        want.add(TWINS[finding.unit])
    src = path.read_text().splitlines()
    chunks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and \
                node.name in want:
            end = getattr(node, "end_lineno", node.lineno)
            chunks.append("\n".join(src[node.lineno - 1:end]))
    return "\n\n".join(chunks)


def slice_ratio(root, finding):
    """C2.17's Day 2: how much of the file the slice actually is.

    Report it per finding. A stage that claims to cut context and is handing
    over 90% of the file is a stage nobody has measured.
    """
    path = Path(root) / finding.file
    whole = len(path.read_text().splitlines()) or 1
    cut = len(slice_for(root, finding).splitlines())
    return round(cut / whole, 3)
# step:C2.17 end
