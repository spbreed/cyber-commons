"""The offensive loop — scope it at the boundary, and label what you know.

An agentic pentest is the most capable and least supervised thing anybody runs
in an estate, and its traffic is indistinguishable from an attack because it is
one. Four lessons build it here and each contributes a refusal rather than a
capability, which is the right ratio for this tool:

    C2.10  scope, enforced where the agent cannot rewrite it
    C2.11  white box — reachability, not presence
    C2.12  black box — observed and inferred are different claims
    C2.13  grey box — the roles x objects x verbs matrix, and its blank cells
    C2.14  the preflight that refuses to start

**Scope is not a sentence in a prompt.** "Only test hosts in the list below" is
a request, addressed to the component an attacker is trying to influence, and
it is the first thing to go when the loop finds something interesting one hop
away. It belongs at the network layer, where the agent's own traffic is
filtered by something the agent does not run.
"""
import fnmatch
from urllib.parse import urlparse


class OutOfScope(Exception):
    """The loop tried to touch something it was not engaged to touch."""


class Scope:
    """What this engagement may reach. Checked on every request.

    Held outside the agent on purpose. The enforcement point in a real
    engagement is a proxy or an egress policy; this is the same decision, made
    where the code can still be read, with the placement stated rather than
    implied — B3.3 made the same argument about the application's own egress.
    """

    def __init__(self, hosts, *, exclude=()):
        self.hosts = list(hosts)
        self.exclude = list(exclude)
        self.allowed = 0
        self.refused = []

    def check(self, url):
        host = (urlparse(url).hostname or url).lower()
        for pattern in self.exclude:
            if fnmatch.fnmatch(host, pattern):
                self.refused.append(host)
                raise OutOfScope(
                    f"{host} matches the exclusion {pattern!r}. An exclusion "
                    f"is usually the one system whose owner did not consent")
        if not any(fnmatch.fnmatch(host, p) for p in self.hosts):
            self.refused.append(host)
            raise OutOfScope(
                f"{host} is not in scope. It was reached because the loop "
                f"found it, which is exactly when a prompt-level rule fails")
        self.allowed += 1
        return True

    def report(self):
        return {"in_scope_calls": self.allowed,
                "refused": sorted(set(self.refused)),
                "enforced_at": "the request boundary, not the prompt"}








