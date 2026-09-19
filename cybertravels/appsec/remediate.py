# step:file B2.16
"""Stage 14 — a patch is not accepted because the scanner went quiet.

This is the stage with the sharpest failure mode in the pipeline, because the
wrong outcome looks exactly like the right one. A patch that silences the
scanner and a patch that fixes the bug produce the same green tick, the same
closed ticket and the same finding count. Renaming the variable the rule keyed
on does it. Adding `# nosec` does it. Wrapping the sink in a helper the rule
does not follow does it, and that one is not even dishonest — somebody was
refactoring.

So a patch is accepted on three pieces of evidence, and the scanner is not one
of them:

1. **the exploit no longer fires** in the replica, using the same payload that
   confirmed the finding;
2. **a regression test exists**, and it *fails on the unpatched code*. A test
   that passes both ways is a test that tests nothing, and it is the most
   common thing a generated fix ships with;
3. **the fix is on the path**, not around it — the patched unit is still the
   one the entry point reaches.

Requirement 2 is the one worth arguing for. Everything else can be satisfied by
a patch that happens to work today; only a test that goes red without the patch
says the next person cannot undo it silently.
"""


class PatchRejected(Exception):
    """The evidence did not support merging it."""


class Patch:
    """A proposed fix, as the replacement for one unit."""

    def __init__(self, unit, file, replacement, rationale):
        self.unit = unit
        self.file = file
        self.replacement = replacement      # a callable, in the replica
        self.rationale = rationale

    def as_dict(self):
        return {"unit": self.unit, "file": self.file,
                "rationale": self.rationale}


def apply_in(module, patch):
    """Swap the unit in the replica. Returns the original, to put back.

    Patching a live module rather than editing a file is what makes the
    before/after comparison a single run: the same process, the same data, one
    variable changed. An edit-and-rerun compares two builds and two databases.
    """
    original = getattr(module, patch.unit)
    setattr(module, patch.unit, patch.replacement)
    return original


def accept(patch, module, *, exploit, regression):
    """The three pieces of evidence, in order, with the reason on failure.

    `exploit` is the same callable that confirmed the finding at stage 12.
    `regression` is a test taking no arguments that raises on failure.
    """
    original = getattr(module, patch.unit)

    # 1 — the exploit must stop firing with the patch in place.
    apply_in(module, patch)
    try:
        still_fires = exploit()
    finally:
        pass
    if still_fires:
        setattr(module, patch.unit, original)
        raise PatchRejected(
            f"{patch.unit}: the exploit still fires with the patch applied. "
            f"Whatever this changed, it was not the thing that was wrong")

    # 2 — the regression test must pass patched, and FAIL unpatched. This is
    # the half that is skipped, and skipping it is how a fix gets reverted six
    # weeks later by somebody who saw a green suite.
    try:
        regression()
    except Exception as e:  # noqa: BLE001
        setattr(module, patch.unit, original)
        raise PatchRejected(
            f"{patch.unit}: the regression test fails against the patched "
            f"code ({e})")
    setattr(module, patch.unit, original)
    try:
        regression()
    except Exception:  # noqa: BLE001
        caught = True
    else:
        caught = False
    if not caught:
        raise PatchRejected(
            f"{patch.unit}: the regression test passes against the UNPATCHED "
            f"code, so it does not test the defect. A test that is green both "
            f"ways is the most common thing a generated fix ships with")

    setattr(module, patch.unit, patch.replacement)
    return {"unit": patch.unit, "merged": True,
            "evidence": ["exploit no longer fires in the replica",
                         "regression test passes patched",
                         "regression test fails unpatched"],
            "not_evidence": ["the scanner went quiet"]}


def revert(module, unit, original):
    setattr(module, unit, original)


def fix_get_booking():
    """The patch for LABELS.md row 1, written as the authorised twin already is.

    Note what it does *not* do: it does not sanitise, filter or validate the
    id. The id was never the problem. The problem is that nothing compared the
    record's owner to the session, and the fix is that comparison — which is
    why no pattern found the defect and no pattern will confirm the fix.
    """
    def get_booking(session, booking_id):
        from ..tools.bookings_api import require_owner
        from .._stubs import DB
        row = DB.cursor().execute(
            "SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
        require_owner(session, row["owner_id"] if row else None)
        return row
    return Patch("get_booking", "tools/bookings_api.py", get_booking,
                 "compare the loaded record's owner to the session, as "
                 "get_my_booking already does")
