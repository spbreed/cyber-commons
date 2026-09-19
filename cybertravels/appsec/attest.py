# step:file C2.18
"""Stage 16 — bind the control claim to a deployment, or it is a spreadsheet.

Every control in Function A is real and running. What nobody can currently do
is answer the question an assessor actually asks: **which deployment was that
claim about?** "Sandbox egress is restricted" is true of something. Which
image, which role, which gateway, which guardrail configuration — and when any
of those change, is it still true?

An attestation is that binding. The shape borrowed here is in-toto's: a
statement about named subjects, carrying a predicate, signed. The parts that
matter for this lesson are not cryptographic:

* **one `deployment_id`**, so the claim has a referent;
* **per-control verdicts with evidence**, so a verdict can be re-checked
  rather than re-asserted;
* **framework mappings**, so the same evidence answers OWASP, ATLAS and the
  EU AI Act without three separate exercises;
* **drift**, so a claim that was true in March says so rather than pretending.

And one rule that is easy to write and hard to keep. **Two of these controls
cannot be proven by this pipeline, and are capped at PARTIAL.** Sandbox egress
is enforced outside the process, so nothing in here can observe its absence;
injection screening is a classifier whose failure mode is silence. Capping them
is not pessimism — it is the difference between an attestation and a document
that says PASS everywhere and is therefore evidence of nothing.
"""
import hashlib
import json
import time

VERDICTS = ("PASS", "PARTIAL", "FAIL", "NOT_APPLICABLE")

# Controls this pipeline cannot prove, and why. Kept as data rather than as a
# convention, so the cap survives somebody adding a check that looks like proof.
CAPPED_AT_PARTIAL = {
    "sandbox-egress":
        "enforced outside this process; nothing in the pipeline can observe "
        "the absence of a connection it never saw",
    "injection-screening":
        "a classifier whose failure mode is silence — a run with no detections "
        "and a run with no attacks are the same artefact",
}

# One control, many frameworks. The mapping lives with the control so the
# evidence is gathered once; maintaining three separate control sets is how
# the same system ends up with three different compliance answers.
FRAMEWORKS = {
    "delegated-authorisation": {
        "owasp": "LLM06 Excessive Agency",
        "atlas": "AML.T0053 Agent Privilege Escalation",
        "nist": "GOVERN 1.2 / MEASURE 2.7",
        "eu_ai_act": "Art. 14 Human oversight",
    },
    "default-deny-tools": {
        "owasp": "LLM06 Excessive Agency",
        "atlas": "AML.T0050 Tool Misuse",
        "nist": "MANAGE 2.2",
        "eu_ai_act": "Art. 9 Risk management",
    },
    "tamper-evident-audit": {
        "owasp": "LLM08 Vector and Embedding Weaknesses",
        "atlas": "AML.T0031 Erode Model Integrity",
        "nist": "MEASURE 2.8",
        "eu_ai_act": "Art. 12 Record-keeping",
    },
    "sandbox-egress": {
        "owasp": "LLM02 Sensitive Information Disclosure",
        "atlas": "AML.T0024 Exfiltration",
        "nist": "MANAGE 4.1",
        "eu_ai_act": "Art. 15 Accuracy, robustness and cybersecurity",
    },
    "injection-screening": {
        "owasp": "LLM01 Prompt Injection",
        "atlas": "AML.T0051 LLM Prompt Injection",
        "nist": "MEASURE 2.7",
        "eu_ai_act": "Art. 15 Accuracy, robustness and cybersecurity",
    },
}


class Control:
    """One control's verdict about one deployment."""

    __slots__ = ("control_id", "verdict", "evidence_uri", "detail", "at")

    def __init__(self, control_id, verdict, evidence_uri, detail=""):
        if verdict not in VERDICTS:
            raise ValueError(f"{verdict!r} is not one of {VERDICTS}")
        if verdict == "PASS" and not evidence_uri:
            raise ValueError(
                f"{control_id}: PASS with no evidence URI is an assertion. "
                f"The whole point of the predicate is that somebody else can "
                f"go and look")
        if control_id in CAPPED_AT_PARTIAL and verdict == "PASS":
            raise ValueError(
                f"{control_id} cannot be PASS: {CAPPED_AT_PARTIAL[control_id]}")
        self.control_id = control_id
        self.verdict = verdict
        self.evidence_uri = evidence_uri
        self.detail = detail
        self.at = time.time()

    def as_dict(self):
        return {"control": self.control_id, "verdict": self.verdict,
                "evidence": self.evidence_uri, "detail": self.detail,
                "frameworks": FRAMEWORKS.get(self.control_id, {}),
                "capped": self.control_id in CAPPED_AT_PARTIAL}


def subject(name, digest_of):
    """An in-toto subject: what the statement is about, by digest."""
    return {"name": name,
            "digest": {"sha256": hashlib.sha256(
                digest_of.encode() if isinstance(digest_of, str)
                else digest_of).hexdigest()}}


def statement(deployment_id, subjects, controls, *, previous=None):
    """The predicate, with drift against the last one if there is a last one."""
    body = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": list(subjects),
        "predicateType": "https://cybercommons.ai/AgenticControlIntent/v1",
        "predicate": {
            "deployment_id": deployment_id,
            "issued_at": time.time(),
            "controls": [c.as_dict() for c in controls],
            "summary": summarise(controls),
        },
    }
    if previous is not None:
        body["predicate"]["drift"] = drift(previous, body)
    return body


def summarise(controls):
    out = {v: 0 for v in VERDICTS}
    for c in controls:
        out[c.verdict] += 1
    out["provable"] = sum(1 for c in controls
                          if c.control_id not in CAPPED_AT_PARTIAL)
    out["capped_at_partial"] = sorted(
        c.control_id for c in controls if c.control_id in CAPPED_AT_PARTIAL)
    return out


def drift(previous, current):
    """What changed since the last attestation for this deployment.

    Both directions, and the subjects too: a verdict that stayed PASS while the
    image digest changed underneath it is the case this exists for, and it is
    invisible if you only diff the verdicts.
    """
    def verdicts(s):
        return {c["control"]: c["verdict"] for c in s["predicate"]["controls"]}

    def digests(s):
        return {x["name"]: x["digest"]["sha256"] for x in s["subject"]}

    was_v, now_v = verdicts(previous), verdicts(current)
    was_d, now_d = digests(previous), digests(current)
    changed_subjects = sorted(n for n in was_d.keys() & now_d.keys()
                              if was_d[n] != now_d[n])
    return {
        "verdicts_changed": {k: [was_v[k], now_v[k]] for k in
                             was_v.keys() & now_v.keys() if was_v[k] != now_v[k]},
        "controls_added": sorted(now_v.keys() - was_v.keys()),
        "controls_gone": sorted(was_v.keys() - now_v.keys()),
        "subjects_changed": changed_subjects,
        "unreviewed_pass": sorted(
            n for n in changed_subjects
            if all(v == "PASS" for k, v in now_v.items()
                   if now_v.get(k) == was_v.get(k))),
    }


def as_json(stmt):
    return json.dumps(stmt, indent=2, sort_keys=True, default=str)
