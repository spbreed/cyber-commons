# step:file A3.11
"""Containment for the coding agent Alex runs in the IDE — not the one we ship.

Every control up to here guards an agent CyberTravels deploys: it has a
workload identity, a policy table, a budget and a gateway. The agent that
*wrote* all of that has none of them. It runs on a laptop, inside an editor,
with Alex's git credentials, Alex's cloud credentials and a shell, in an
environment nobody reviewed and no deployment pipeline touches.

That is the asymmetry this lesson is about. The production agent can reach the
booking rows. The development agent can reach the booking rows, the deployment
credentials, the signing key, the other twelve repositories checked out on that
machine, and the history of everything typed into that terminal.

**The constraint is friction, not strength.** A containment a developer notices
is a containment a developer turns off, and an agent configuration with every
guard disabled is worse than one with two guards that stayed on — because the
first one is also reported as compliant. So the order here is deliberate, and
it is not the order of a threat model:

    1. credential deny-list     the developer never notices; highest value
    2. workspace confinement    noticed once, at the first path outside
    3. command review           noticed constantly. Last, and often not at all

The first two are `DENY_READ` and `WORKSPACE_ROOTS` below. They cost nothing on
the happy path, which is the only reason they survive contact with a deadline.

Nothing here contains anything by itself — enforcement is the agent CLI's, and
this is the policy it should be given plus a way to check the configuration a
machine is actually running. A policy nobody compared against the live config
is A3.2's mistake in a different file.
"""
import fnmatch
import os
from pathlib import Path

from . import config

# Files an agent has no reason to read, ever, on any task. Expressed as the
# thing itself rather than as a directory, because the interesting copies are
# never where the documentation says they are — a service-account JSON ends up
# in Downloads, and a deny-list rooted at ~/.config misses it.
DENY_READ = [
    "**/.env",
    "**/.env.*",
    "**/.git-credentials",
    "**/.netrc",
    "**/.aws/credentials",
    "**/.ssh/id_*",
    "**/.config/gcloud/*.json",
    "**/.kube/config",
    "**/*.pem",
    "**/*service-account*.json",
    "**/.claude.json",              # holds the agent's own session material
]

# Environment variables the agent's process should not inherit. This is the
# line that costs a developer nothing: an agent editing Python does not need
# the deployment credentials that happen to be exported in that shell.
DENY_ENV = ("AWS_", "GITHUB_TOKEN", "GH_TOKEN", "ANTHROPIC_API_KEY",
            "NVIDIA_API_KEY", "NGC_API_KEY", "OPENAI_API_KEY",
            "GOOGLE_APPLICATION_CREDENTIALS", "CT_IDP_SECRET")

# Where the agent may work. One repository, resolved — so a symlink out of the
# tree is outside it, which is the case a prefix check on the unresolved path
# gets wrong.
WORKSPACE_ROOTS = [config.PROJECT_ROOT.parent]


class NotContained(Exception):
    """A read, a write or a spawn that the workspace policy refuses."""


def denied_read(path):
    """Is this path on the credential deny-list?

    Matched against the resolved path, because `../../.aws/credentials` and
    `~/.aws/credentials` are the same file and only one of them looks like one.
    """
    p = str(Path(path).expanduser().resolve())
    return any(fnmatch.fnmatch(p, pat) for pat in DENY_READ)


def confined(path):
    """Inside a workspace root, after resolving every link."""
    p = Path(path).expanduser().resolve()
    return any(p == root or root in p.parents
               for root in (r.resolve() for r in WORKSPACE_ROOTS))


def check_access(path, mode="read"):
    """The two guards, in the order that matters. Raises with the reason."""
    if mode == "read" and denied_read(path):
        raise NotContained(
            f"{path} is on the credential deny-list. A coding agent that can "
            f"read it can leak it in a summary without ever being attacked")
    if not confined(path):
        raise NotContained(
            f"{path} is outside the workspace. The other repositories on this "
            f"machine are not in scope for this task and never were")
    return True


def redact_env(env=None):
    """The environment the agent's subprocesses should actually get."""
    src = os.environ if env is None else env
    return {k: v for k, v in src.items()
            if not any(k.upper().startswith(d) or k.upper() == d
                       for d in DENY_ENV)}


def review(agent_config):
    """Compare one machine's agent configuration against this policy.

    `agent_config` is what the CLI is actually configured with — the shape any
    of them can export. Returns findings, worst first. The empty list is the
    goal and is not the usual answer on a machine nobody has looked at.
    """
    findings = []
    if not agent_config.get("deny_read"):
        findings.append({
            "control": "credential deny-list", "state": "absent",
            "friction": "none",
            "why": "the cheapest control here, and the one most often left "
                   "out because nothing fails without it"})
    if not agent_config.get("workspace_root"):
        findings.append({
            "control": "workspace confinement", "state": "absent",
            "friction": "one prompt, once",
            "why": "an agent with the home directory as its root has every "
                   "repository on the machine in scope"})
    if agent_config.get("inherit_env", True):
        findings.append({
            "control": "environment inheritance", "state": "inherited",
            "friction": "none",
            "why": "the deployment credentials exported in this shell are "
                   "readable by anything the agent runs"})
    if agent_config.get("auto_approve_commands"):
        findings.append({
            "control": "command review", "state": "auto-approved",
            "friction": "high",
            "why": "turned off first, for a reason — which is why it is last "
                   "here and why the two above have to hold without it"})
    return findings


def containment_score(agent_config):
    """A3.11's Day 2 number.

    Fraction of the containments that are on, weighted by nothing — a simple
    count, deliberately, because a weighted score invites arguing the weights
    instead of turning one on. Report it per machine; a fleet average hides
    the one laptop with everything off.
    """
    total = 4
    missing = len(review(agent_config))
    return {"controls": total, "in_place": total - missing,
            "missing": [f["control"] for f in review(agent_config)],
            "score": round((total - missing) / total, 2)}
