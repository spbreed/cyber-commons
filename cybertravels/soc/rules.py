# step:file D2.2
"""Detections whose subject is a non-human principal.

Every rule in the estate has a subject, and it is a user. "A user downloaded
200 files." "A user logged in from two countries." The subject is doing a lot
of work in those sentences: it carries an assumption about tempo, about
session shape, about what a normal day looks like. Change the subject to an
agent and every one of those assumptions is wrong, while the rule keeps
firing exactly as written.

So the rules here name the agent as the subject, and each one is mapped to
ATT&CK and ATLAS — not for the compliance slide, but because a rule with no
technique attached cannot be reasoned about when somebody asks what the estate
does *not* cover.

The four that matter in this system are all about relationships rather than
volumes: a scope that widened, a tool sequence that has never happened, an
action with no human anywhere in its chain, and an approval that arrived faster
than anybody could have read it.
"""
from .. import config


class Rule:
    """One detection, with its subject, its technique and its cost."""

    __slots__ = ("name", "subject", "attack", "atlas", "over", "why",
                 "true_rate", "false_rate")

    def __init__(self, name, subject, attack, atlas, over, why,
                 *, true_rate=0.0, false_rate=0.0):
        if subject not in ("agent", "agent-platform", "human"):
            raise ValueError(f"{name}: a rule's subject has to be stated")
        self.name = name
        self.subject = subject
        self.attack = attack
        self.atlas = atlas
        self.over = over            # which source it reads
        self.why = why
        self.true_rate = true_rate
        self.false_rate = false_rate

    def as_dict(self):
        return {"rule": self.name, "subject": self.subject,
                "attack": self.attack, "atlas": self.atlas,
                "source": self.over, "why": self.why,
                "true_rate": self.true_rate, "false_rate": self.false_rate}


AGENT_RULES = [
    Rule("delegated scope widened between hops", "agent",
         "T1078 Valid Accounts", "AML.T0053 Agent Privilege Escalation",
         "audit_rows",
         "A2.3 makes a chain narrow; a widening one is either a bug or the "
         "thing A2.3 exists to stop",
         true_rate=0.0004, false_rate=0.0001),
    Rule("tool sequence never seen in the baseline", "agent",
         "T1059 Command and Scripting Interpreter", "AML.T0050 Tool Misuse",
         "mcp_calls",
         "lookup_vendor_doc immediately followed by issue_refund is the "
         "Northwind notice working",
         true_rate=0.0006, false_rate=0.004),
    Rule("action with no human in the delegation chain", "agent",
         "T1078.004 Cloud Accounts", "AML.T0053 Agent Privilege Escalation",
         "audit_rows",
         "every action should trace to a person; one that does not is either "
         "a scheduled job nobody registered or an agent acting for itself",
         true_rate=0.0003, false_rate=0.0008),
    Rule("approval granted faster than the content could be read", "agent",
         "T1204 User Execution", "AML.T0051 LLM Prompt Injection",
         "approvals",
         "A3.6's saturation, as a detection rather than a report — the gate "
         "is still 100% covered while nobody is reading",
         true_rate=0.0002, false_rate=0.0002),
]


def catalogue(subject=None):
    return [r.as_dict() for r in AGENT_RULES
            if subject is None or r.subject == subject]


def sequence_never_seen(calls, baseline):
    """The second rule, as a function. Pairs rather than whole trajectories:
    a whole-trajectory baseline never matches anything, which is how this rule
    gets written, produces nothing, and is reported as coverage."""
    pairs = set(zip(calls, calls[1:]))
    return sorted(p for p in pairs if p not in baseline)


def no_human_in_chain(rows):
    """Rows whose delegation chain never names a person from `config.USERS`."""
    return [r for r in rows
            if not any(u in str(r.get("chain", "")) for u in config.USERS)]


# step:D2.3 add
# --------------------------------------------------------------------------- #
# D2.3 — when the subject is the platform, not the workload
# --------------------------------------------------------------------------- #
# A workload-layer detection watches what the agent does. It is looking in the
# wrong place when the thing being attacked is the harness the agent runs in,
# because from inside the workload a sandbox escape, a poisoned cache entry and
# a silently expired exemption all look exactly like normal operation.
#
# These are named primitives rather than anomaly scores. An anomaly score over
# platform events is a number nobody can act on; "the coding agent's profile
# forbids spawning and a subprocess was created" is an incident.
PLATFORM_RULES = [
    Rule("process spawned under a profile that forbids it", "agent-platform",
         "T1611 Escape to Host", "AML.T0054 LLM Jailbreak", "edr",
         "A3.2's Profile.may_spawn is False for the coding agent, and "
         "nothing enforces it — so the detection is the enforcement",
         true_rate=0.0009, false_rate=0.0002),
    Rule("artefact cache entry differs from its manifest", "agent-platform",
         "T1195.002 Compromise Software Supply Chain",
         "AML.T0010 ML Supply Chain Compromise", "run_artefacts",
         "A3.8's shared surface, diffed rather than trusted",
         true_rate=0.0007, false_rate=0.0003),
    Rule("exemption expired and the control did not come back",
         "agent-platform", "T1562 Impair Defenses",
         "AML.T0055 Unsafe ML Artifacts", "audit_rows",
         "A3.9's Exemption has an expiry; nothing reconciles the register "
         "against the running configuration, so an expiry is a date that "
         "passes",
         true_rate=0.0005, false_rate=0.0001),
    Rule("secret in an artefact, and the credential still valid",
         "agent-platform", "T1552 Unsecured Credentials",
         "AML.T0024 Exfiltration", "run_artefacts",
         "finding the secret is the easy half; the detection is only closed "
         "when revocation happened",
         true_rate=0.0011, false_rate=0.0009),
]


def platform_catalogue():
    return [r.as_dict() for r in PLATFORM_RULES]


def exemption_reconciliation(register, live_controls, *, now):
    """D2.3's most useful rule, because it finds a control that is off and
    that everybody believes is on."""
    out = []
    for ex in register:
        if not ex.active(now) and not live_controls.get(ex.ref, True):
            out.append({"exemption": ex.ref, "expired_at": ex.expires_at,
                        "lifts": sorted(ex.lifts),
                        "state": "expired, and the control is still off"})
    return out
# step:D2.3 end


# step:D2.4 add
# --------------------------------------------------------------------------- #
# D2.4 — written by a loop, shipped by a human
# --------------------------------------------------------------------------- #
# A model writes a plausible detection quickly. Plausible is the problem: the
# rule reads well, maps to a technique, and has never been run against
# anything. So the loop's output is a *candidate*, and the gate between
# candidate and deployed is the one thing that cannot be automated away —
# a measured false-positive rate, and a human who accepts it.
def review(candidate, events_per_day, *, analysts=1):
    """Reuses C1.6's arithmetic rather than restating it. A detection team and
    a red team asking the same question should get the same answer."""
    from ..redteam.swarm import deployable
    v = deployable({"name": candidate.name,
                    "true_rate": candidate.true_rate,
                    "false_rate": candidate.false_rate},
                   events_per_day, analysts=analysts)
    v["subject"] = candidate.subject
    v["mapped"] = bool(candidate.attack and candidate.atlas)
    v["ship"] = v["deployable"] and v["mapped"]
    if not v["mapped"]:
        v["verdict"] = "unmapped: nobody can say what this does not cover"
    return v
# step:D2.4 end


# step:D2.5 add
# --------------------------------------------------------------------------- #
# D2.5 — a rule generated from one incident
# --------------------------------------------------------------------------- #
# It will match that incident. That is not evidence of anything: a rule
# generated from a trace and tested against that trace is a description of the
# trace. Two failure modes, opposite and equally common — overfitted to one
# session id, or so general it matches the baseline.
#
# The benign corpus is what separates them, and a rule with no measured
# false-positive rate is not a rule.
def generalise(trace, *, drop=("trace_id", "session", "timestamp", "booking_id",
                               "amount")):
    """Strip the fields that make a rule match exactly one run."""
    return {k: v for k, v in trace.items() if k not in drop}


def measure(rule_fn, incident_traces, benign_traces):
    """Against the incident it came from AND against ordinary traffic."""
    caught = sum(1 for t in incident_traces if rule_fn(t))
    noise = sum(1 for t in benign_traces if rule_fn(t))
    n_b = len(benign_traces) or 1
    return {
        "incidents_caught": caught, "of": len(incident_traces),
        "false_positives": noise, "benign_trials": len(benign_traces),
        "false_rate": round(noise / n_b, 5),
        "overfitted": caught == 1 and len(incident_traces) > 1,
        "too_general": noise / n_b > 0.05,
        "verdict": ("overfitted to one run" if caught < len(incident_traces)
                    else "matches the baseline" if noise / n_b > 0.05
                    else "generalises, and the noise is measured"),
    }
# step:D2.5 end
