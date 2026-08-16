"""Containment: egress policy, path guards, and tool permissions.

Sandboxing is the perimeter for an agent, because the agent's *intent* is not a
control you own. The three levers modelled here are the ones that hold when the
prompt is fully compromised:

    egress    what it can talk to        (exfiltration + C2)
    paths     what it can read or write  (secret theft + persistence)
    tools     what it can call at all    (everything else)

Each guard is deny-by-default and returns a *reason*, because a containment
decision you cannot explain is one you cannot tune.
"""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class Decision:
    allowed: bool
    reason: str
    subject: str = ""

    def __str__(self) -> str:
        return f"{'ALLOW' if self.allowed else 'DENY ':5s} {self.subject:44s} {self.reason}"


# ---------------------------------------------------------------- egress
@dataclass
class EgressPolicy:
    """Allowlist by host. Deny-by-default, because the interesting destination
    is always the one nobody thought to list."""
    allow_hosts: set[str] = field(default_factory=set)
    allow_suffixes: set[str] = field(default_factory=set)   # ".internal.example"
    block_private: bool = True

    PRIVATE = [re.compile(p) for p in (
        r"^127\.", r"^10\.", r"^192\.168\.", r"^169\.254\.",
        r"^172\.(1[6-9]|2\d|3[01])\.", r"^localhost$", r"^\[::1\]$")]

    def check(self, url: str) -> Decision:
        host = (urlparse(url).hostname or "").lower()
        if not host:
            return Decision(False, "unparseable destination", url)
        if self.block_private and any(p.match(host) for p in self.PRIVATE):
            # the cloud metadata endpoint is the one that ends careers
            extra = " (cloud metadata service)" if host.startswith("169.254") else ""
            return Decision(False, f"private/link-local address blocked{extra}", url)
        if host in self.allow_hosts:
            return Decision(True, "host on the allowlist", url)
        for suf in self.allow_suffixes:
            if host.endswith(suf):
                return Decision(True, f"matches allowed suffix {suf}", url)
        return Decision(False, "not on the egress allowlist", url)


# ---------------------------------------------------------------- filesystem
@dataclass
class PathGuard:
    """Confine reads and writes to a workspace, and never to secrets.

    Traversal is normalised *before* the check, which is the bug this class
    exists to not have: `workspace/../../.ssh/id_rsa` starts with `workspace/`.
    """
    workspace: str = "/work"
    deny_globs: tuple[str, ...] = (
        "*/.ssh/*", "*/.aws/*", "*.pem", "*.key", "*/.kaggle/*",
        "*/.git/config", "*/etc/shadow", "*/.env",
    )

    @staticmethod
    def _normalise(path: str) -> str:
        parts: list[str] = []
        for seg in path.split("/"):
            if seg in ("", "."):
                continue
            if seg == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(seg)
        return "/" + "/".join(parts)

    def check(self, path: str, write: bool = False) -> Decision:
        real = self._normalise(path)
        for g in self.deny_globs:
            if fnmatch.fnmatch(real, g):
                return Decision(False, f"matches deny rule {g}", path)
        ws = self._normalise(self.workspace)
        if real == ws or real.startswith(ws + "/"):
            return Decision(True, f"inside workspace ({real})", path)
        verb = "write" if write else "read"
        return Decision(False, f"{verb} outside workspace; resolves to {real}", path)


# ---------------------------------------------------------------- tools
@dataclass
class ToolPolicy:
    """Which tools an agent may call, and which need a human first.

    `require_approval` is the L2 gate. `deny` is the L2.5 boundary. An agent
    with an empty deny list is not sandboxed, it is merely polite.
    """
    allow: set[str] = field(default_factory=set)
    require_approval: set[str] = field(default_factory=set)
    deny: set[str] = field(default_factory=set)

    def check(self, tool: str, approved: bool = False) -> Decision:
        if tool in self.deny:
            return Decision(False, "tool explicitly denied", tool)
        if tool in self.require_approval and not approved:
            return Decision(False, "requires human approval, none presented", tool)
        if tool in self.allow or tool in self.require_approval:
            return Decision(True, "approved call" if approved else "on the allowlist", tool)
        return Decision(False, "not on the tool allowlist (deny by default)", tool)


# ---------------------------------------------------------------- the sandbox
@dataclass
class Sandbox:
    """All three levers together, with a log — the containment story end to end."""
    egress: EgressPolicy
    paths: PathGuard
    tools: ToolPolicy
    log: list[Decision] = field(default_factory=list)

    def _record(self, d: Decision) -> Decision:
        self.log.append(d)
        return d

    def call(self, tool: str, target: str = "", approved: bool = False) -> Decision:
        d = self.tools.check(tool, approved)
        if not d.allowed:
            return self._record(d)
        if target.startswith(("http://", "https://")):
            return self._record(self.egress.check(target))
        if target.startswith("/"):
            return self._record(self.paths.check(target, write="write" in tool))
        return self._record(d)

    def summary(self) -> dict:
        denied = [d for d in self.log if not d.allowed]
        return {"calls": len(self.log), "allowed": len(self.log) - len(denied),
                "denied": len(denied),
                "reasons": sorted({d.reason for d in denied})}


def default_sandbox() -> Sandbox:
    """A sane starting policy for the labs — narrow, and it says why."""
    return Sandbox(
        egress=EgressPolicy(allow_hosts={"api.github.com"},
                            allow_suffixes={".githubusercontent.com"}),
        paths=PathGuard(workspace="/work"),
        tools=ToolPolicy(allow={"read_file", "list_dir", "http_get"},
                         require_approval={"write_file", "run_shell"},
                         deny={"delete_repo", "rotate_secrets"}),
    )
