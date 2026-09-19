# step:file C2.7
"""Supply chain — reconcile the manifest against the disk, then read the binary.

A dependency scan reads a manifest. That is the whole of what it does, and it
is worth saying plainly because the output does not look like it: a clean scan
is a statement that **nothing declared** has a known vulnerability. It is not a
statement about what is on disk, and on any estate of a certain age those are
different sets.

Two halves here, and the second is the one nobody runs.

**Reconcile.** Walk what is actually importable and compare it against the
manifest. Anything on disk and not in the manifest is invisible to every
scanner you own — not scanned clean, invisible. Anything in the manifest and
not on disk is a different problem: the scan is reporting on code that is not
running, which inflates the finding count and wastes triage.

**Read the artefact.** For the undeclared thing, there is no advisory to look
up, because nobody catalogued it. What is left is the artefact itself: the
strings, the imported names, and — the question that decides whether this is
an afternoon or an incident — whether it talks to the network.

The compiled artefact here is a `.pyc`, which is a real compiled artefact with
a real code object in it, readable with the standard library. A native `.so` is
the same exercise with harder tools and identical reasoning: you are recovering
intent from something nobody wrote down.
"""
import marshal
import importlib.util
import re
from pathlib import Path

# Names that mean this artefact reaches the network. Not a complete list and
# not meant to be: the point is that the question gets asked of the binary,
# by somebody, rather than answered from a manifest that does not mention it.
EGRESS_NAMES = {"socket", "urlopen", "urllib", "request", "requests", "http",
                "connect", "sendall", "httplib", "ssl", "curl"}


# A manifest names **distributions**; code imports **modules**, and they are
# not the same string. `PyJWT` is imported as `jwt`, `beautifulsoup4` as `bs4`,
# `Pillow` as `PIL`. Without this map the reconcile reports PyJWT as an unused
# dependency and `jwt` as an undeclared one — two findings, both false, from
# one correct manifest. It is the most common false positive this check
# produces, and a pipeline that ships it teaches its users to ignore the stage.
DISTRIBUTION_TO_IMPORT = {
    "pyjwt": "jwt",
    "beautifulsoup4": "bs4",
    "pillow": "pil",
    "python-dateutil": "dateutil",
    "pyyaml": "yaml",
    "protobuf": "google",
}


def declared(requirements_path):
    """What the manifest says, as the names the code would import."""
    out = set()
    for line in Path(requirements_path).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        dist = re.split(r"[<>=!\[ ]", line, 1)[0].lower()
        out.add(DISTRIBUTION_TO_IMPORT.get(dist, dist))
    return out


def first_party(root):
    """Top-level names this tree defines. Not dependencies — and the reason
    the reconcile has to know them is the interesting case below."""
    root = Path(root)
    out = {root.name.lower()}
    for p in root.iterdir():
        if p.is_dir() and (p / "__init__.py").exists():
            out.add(p.name.lower())
        elif p.suffix == ".py":
            out.add(p.stem.lower())
    return out


def imported(root):
    """Every top-level module the tree actually imports.

    This, rather than a listing of the directory, is what the manifest has to
    be reconciled against. A manifest describes what should be installed; the
    imports describe what the code will reach for at run time, and the gap
    between them is where an undeclared dependency lives.
    """
    import ast
    out = set()
    for path in sorted(Path(root).rglob("*.py")):
        try:
            tree = ast.parse(path.read_text())
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                out.update(a.name.split(".")[0].lower() for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                out.add(node.module.split(".")[0].lower())
    return out


def reconcile(requirements_path, root, stdlib=()):
    """The two directions, reported separately because they are different bugs.

    `shadowed` is the one worth stopping on. `mcp` is declared as a dependency
    **and** is the name of a first-party package in this tree. Nothing breaks
    today, because every import of the first-party one is relative and the
    third-party one is reached absolutely — but a resolution that depends on
    which form somebody used is a resolution that changes the day somebody
    tidies an import, and the scanner reports the manifest either way.
    """
    want = declared(requirements_path)
    mine = first_party(root)
    used = imported(root) - mine - set(stdlib)
    return {
        "declared": sorted(want),
        "imported_third_party": sorted(used),
        # The dangerous direction: the code reaches for it, no manifest entry
        # covers it, and therefore no scanner has ever looked at it.
        "undeclared_but_imported": sorted(used - want),
        # The wasteful direction: advisories about code nothing imports.
        "declared_but_unused": sorted(want - used),
        # A first-party name that is also a dependency name.
        "shadowed": sorted(want & mine),
        "coverage": 0.0 if not used else round(len(want & used) / len(used), 3),
    }


def strings_in(pyc_path, minimum=4):
    """Every string constant the compiled object carries, recursively."""
    data = Path(pyc_path).read_bytes()
    header = 16                      # magic, flags, mtime, size — CPython 3.7+
    try:
        code = marshal.loads(data[header:])
    except (ValueError, EOFError):
        return []
    out, stack = set(), [code]
    while stack:
        c = stack.pop()
        for const in getattr(c, "co_consts", ()):
            if isinstance(const, str) and len(const) >= minimum:
                out.add(const)
            elif hasattr(const, "co_consts"):
                stack.append(const)
        out.update(n for n in getattr(c, "co_names", ()) if len(n) >= minimum)
    return sorted(out)


def reads_the_network(pyc_path):
    """Does this artefact reach out? The question the manifest cannot answer."""
    found = {s for s in strings_in(pyc_path, minimum=3)
             if s.lower() in EGRESS_NAMES or s.lower().startswith("http")}
    return {"artefact": str(pyc_path), "egress_indicators": sorted(found),
            "reaches_network": bool(found),
            "note": "recovered from the compiled object, because no SBOM entry "
                    "covers this file and there is no advisory to look up"}


def compiled_artefacts(root):
    """Every compiled object in the tree, which is what the reconcile misses."""
    return sorted(Path(root).rglob("*.pyc")) + sorted(Path(root).rglob("*.so"))


def cache_tag():
    """Which interpreter wrote the artefacts, so a reader knows what they have."""
    return importlib.util.cache_from_source("x.py").split("/")[-1]
