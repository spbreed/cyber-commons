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


# --------------------------------------------------------------------------- #
# C2.12 — black box: what you saw, and what you decided it meant
# --------------------------------------------------------------------------- #
# Given status codes and timings, a model will narrate an architecture. The
# narration is fluent, plausible, occasionally right, and formatted exactly
# like the observations it sits beside. The report is then fiction that reads
# like findings, and the giveaway — that nobody ever saw the thing — is the
# one detail the prose smooths over.
#
# So the type system does the work. An inference cannot carry a severity.
class Claim:
    """Something the engagement asserts, and how it came to."""

    __slots__ = ("what", "kind", "evidence", "severity")

    def __init__(self, what, kind, evidence):
        if kind not in ("observed", "inferred"):
            raise ValueError("a claim is observed or inferred; there is no "
                             "third kind and 'probably' is not evidence")
        if kind == "observed" and not evidence:
            raise ValueError("an observation with no evidence is an inference "
                             "that has been mislabelled")
        self.what = what
        self.kind = kind
        self.evidence = list(evidence)
        self.severity = None

    def rate(self, severity):
        """Only an observation can carry one."""
        if self.kind == "inferred":
            raise ValueError(
                f"cannot rate an inference: {self.what!r} was reasoned from "
                f"{self.evidence}, not seen. Go and observe it, or report it "
                f"as an inference with no severity")
        self.severity = severity
        return self

    def as_dict(self):
        return {"claim": self.what, "kind": self.kind,
                "evidence": self.evidence, "severity": self.severity}


def report_claims(claims):
    """Observations first, inferences after, and the ratio in the header.

    The ratio is the number worth reading. A black-box report that is 80%
    inference is a hypothesis document, and saying so is what makes the 20%
    worth acting on.
    """
    observed = [c for c in claims if c.kind == "observed"]
    inferred = [c for c in claims if c.kind == "inferred"]
    return {
        "observed": len(observed), "inferred": len(inferred),
        "inference_ratio": round(len(inferred) / max(len(claims), 1), 2),
        "claims": [c.as_dict() for c in observed + inferred],
    }






# --------------------------------------------------------------------------- #
# C2.11 — white box: presence is not the finding
# --------------------------------------------------------------------------- #
# Full source turns the loop into a list generator. Every sink in the tree is
# present, every one of them is reported, and the report is unusable because
# presence was never the question — reachability was, and so was whether an
# authorisation predicate sits on the path.
#
# The rule this encodes is the one that makes a white-box report actionable:
# a candidate carries the path that reaches it and the predicate on that path,
# and an unreachable sink is reported **as unreachable** rather than dropped.
# Dropping it is how a real defect disappears the day somebody adds a route.
AUTHORISATION_PREDICATES = ("require_owner", "verify_delegated", "decide",
                            "authorise")


def candidate(finding, graph, source):
    """One white-box candidate: the sink, its path, and the predicate on it."""
    live = graph.reachable()
    guards = [p for p in AUTHORISATION_PREDICATES
              if p in graph.calls.get(finding.unit, ())]
    return {
        "unit": finding.unit, "file": finding.file, "cwe": finding.cwe,
        "reachable": finding.unit in live,
        "entry_points": sorted(
            e for e in graph.entries
            if finding.unit in _walk(graph, e)),
        "authorisation_on_path": guards,
        "report_as": ("finding" if finding.unit in live and not guards
                      else "reachable, guarded" if guards
                      else "unreachable — reported, not dropped"),
        "source_lines": len(source.splitlines()),
    }


def _walk(graph, start):
    seen, stack = set(), [start]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(graph.calls.get(u, ()))
    return seen
