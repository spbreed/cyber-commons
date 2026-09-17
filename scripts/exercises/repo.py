"""Where this repository lives, in one place.

Every link a lesson renders — the skills tree, a `SKILL.md`, the sample repo,
the raw notebook Kaggle fetches — is pinned to a branch. That branch name was
written out longhand in nine files, and one of them had drifted to a branch
that does not exist on the remote at all: `track_a2.py` linked to
`.../tree/main/labs/tools/keycloak-obo`, and there has never been a `main`.

Nothing caught it. `check_docs.py` validates relative links in markdown; an
absolute GitHub URL inside a `.py` lesson source is outside both. So the name
lives here once, and `check_repo_links.py` checks that every branch-pinned URL
in the tree uses it.

Change `BRANCH` here and rebuild; do not spell it out anywhere else.
"""
from __future__ import annotations

OWNER = "spbreed"
NAME = "cyber-commons"

#: The branch every published link points at. `master` is the repository's
#: trunk: it is what a reader clones, what the site is built from, and what
#: `pages.yml` deploys.
BRANCH = "master"

REPO = f"https://github.com/{OWNER}/{NAME}"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{NAME}/{BRANCH}"
CLONE = f"{REPO}.git"


def tree(path: str = "") -> str:
    """A link to a directory in the repository, on the published branch."""
    return f"{REPO}/tree/{BRANCH}/{path}".rstrip("/")


def blob(path: str) -> str:
    """A link to a single file in the repository, on the published branch."""
    return f"{REPO}/blob/{BRANCH}/{path}"
