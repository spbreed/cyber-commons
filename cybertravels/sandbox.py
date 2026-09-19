# step:file A3.2
"""Sandboxed execution — what the agent's code can reach when it runs.

CyberTravels' Coding Agent writes code and runs it. Everything in `agents/` up
to here has run in the orchestrator's own process, which means it inherits the
orchestrator's filesystem, its environment and its network. The three defects
in `agents/coding_agent.py` and `agents/file_agent.py` are only as bad as they
are because of that inheritance — `_open_branch` reaches a shell that has
whatever the parent had.

A sandbox is a statement about **ambient authority**: what a process gets
without asking. The profile below says what an execution is allowed, and the
preflight says what the current process actually has. The gap between them is
the finding.

This models the decision rather than implementing containment — real isolation
is a container, a gVisor sandbox or a microVM, and none of that belongs in a
teaching repository that has to run on a laptop. What survives the
simplification is the part teams get wrong: **listing what you want denied
rather than what you want allowed**, and never checking that the list matches
the process you are actually in.
"""
import os
from pathlib import Path

from . import config


class Profile:
    """What one execution may reach. Allow-list, in all three dimensions."""

    __slots__ = ("name", "paths", "env_keys", "hosts", "may_spawn",
                 "wall_seconds")

    def __init__(self, name, paths=(), env_keys=(), hosts=(),
                 may_spawn=False, wall_seconds=30):
        self.name = name
        self.paths = [str(Path(p).resolve()) for p in paths]
        self.env_keys = set(env_keys)
        self.hosts = set(hosts)
        self.may_spawn = may_spawn
        self.wall_seconds = wall_seconds

    def as_dict(self):
        return {"name": self.name, "paths": self.paths,
                "env_keys": sorted(self.env_keys), "hosts": sorted(self.hosts),
                "may_spawn": self.may_spawn, "wall_seconds": self.wall_seconds}


# The Coding Agent's profile. No credentials in the environment is the single
# most valuable line here: an agent that cannot read a key cannot leak one,
# whatever it is persuaded to do.
CODING_AGENT = Profile(
    name="coding-agent",
    paths=[config.PROJECT_ROOT / "data" / "workspace"],
    env_keys=set(),                 # nothing. Not "no secrets" — nothing.
    hosts=set(),                    # egress is A3.3's allow-list, not here
    may_spawn=False,                # `_open_branch` reaches a shell. It should not.
    wall_seconds=30,
)

FILE_AGENT = Profile(
    name="file-agent",
    paths=[config.PROJECT_ROOT / "data" / "invoices"],
    env_keys=set(),
    hosts=set(),
    may_spawn=False,
    wall_seconds=15,
)


def reachable_now():
    """What the *current* process actually has, whatever the profile says.

    The point of measuring this is that a profile is a document until somebody
    compares it to reality. Teams write the profile, deploy without the
    isolation that enforces it, and the profile keeps describing a containment
    that was never applied.
    """
    interesting = [k for k in os.environ
                   if any(s in k.upper() for s in
                          ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL"))]
    return {
        "credential_env_keys": sorted(interesting),
        "cwd": str(Path.cwd()),
        "can_spawn": True,          # a plain Python process always can
    }


def violations(profile, observed=None):
    """Where the running process exceeds the profile. Empty is the goal and
    almost never the starting position."""
    obs = observed or reachable_now()
    out = []
    for key in obs["credential_env_keys"]:
        if key not in profile.env_keys:
            out.append({"kind": "ambient-credential", "detail": key,
                        "why": "a credential the profile does not grant is "
                               "reachable by anything this process runs"})
    if obs["can_spawn"] and not profile.may_spawn:
        out.append({"kind": "process-spawn", "detail": "subprocess available",
                    "why": "agents/coding_agent.py::_open_branch reaches a "
                           "shell, and the profile says it may not"})
    return out
