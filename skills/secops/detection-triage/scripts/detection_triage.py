#!/usr/bin/env python3
"""Assemble the context a triage decision needs, and show what the same alert looks like without it.

This is the executable half of the `detection-triage` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# --- the skill's own contract, available both ways -------------------------
# This script is run two ways and both have to work: standalone from a
# terminal, and embedded in the lesson notebook underneath the cell that
# already parsed the SKILL.md. So take what is already defined and read the
# file only when it is not.
import pathlib as _pathlib


def _skill_md():
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


if "contract_of" not in globals():
    import json, re

    def parse_skill(md):
        """Split a SKILL.md into (frontmatter dict, body).

        Frontmatter is a small, fixed subset of YAML: `key: value`, plus folded
        scalars (`description: >-`) whose continuation lines are indented. That is
        all a skill needs, and parsing it directly means no dependency.
        """
        if not md.startswith("---"):
            raise ValueError("a SKILL.md must open with a frontmatter block")
        _, front, body = md.split("---", 2)
        meta, key = {}, None
        for line in front.strip().splitlines():
            if not line.strip():
                continue
            if not line[0].isspace() and ":" in line:
                key, val = line.split(":", 1)
                key, val = key.strip(), val.strip()
                # `>-` and `|` open a folded block; the value is on the next lines
                meta[key] = "" if val in (">-", ">", "|", "|-") else val
            elif key is not None:
                meta[key] = (meta[key] + " " + line.strip()).strip()
        if "allowed-tools" in meta:
            meta["allowed-tools"] = [t.strip() for t in meta["allowed-tools"].split(",")
                                     if t.strip()]
        for required in ("name", "description"):
            if not meta.get(required):
                raise ValueError(f"skill is missing a {required!r}")
        return meta, body.strip()

    _WORD = re.compile(r"[a-z][a-z-]{3,}")

    def route(task, skills):
        """Pick the skill whose description best matches a task. Deterministic.

        The description is not documentation — it is the routing key. An agent
        decides whether to load a skill by reading it, so a vague description means
        the skill never fires when it should, and two overlapping descriptions mean
        the wrong one fires.

        Returns (pick, scores, margin). A margin of 0 means the top two scored the
        same and the "winner" is just whichever sorted first — an arbitrary answer
        wearing a confident face. Callers should refuse to auto-route on margin 0
        rather than pretend the tiebreak meant something.
        """
        want = set(_WORD.findall(task.lower()))
        def score(meta):
            return len(want & set(_WORD.findall(meta["description"].lower())))
        scores = {n: score(skills[n]) for n in sorted(skills)}
        # sort names first, then by score: ties must break identically on every
        # machine or the same task routes differently on two runs
        ranked = sorted(sorted(skills), key=lambda n: -scores[n])
        top = scores[ranked[0]]
        margin = top - (scores[ranked[1]] if len(ranked) > 1 else 0)
        return ranked[0], scores, margin

    def contract_of(body):
        """The JSON block under '## Output contract' — the skill's machine promise."""
        # non-greedy across any prose between the heading and the fence
        m = re.search(r"## Output contract\b.*?```json\n(.*?)```", body, re.S)
        if not m:
            raise ValueError("skill declares no output contract")
        return json.loads(m.group(1))

    def check(instance, contract, path="$"):
        """Structural conformance of an instance against a contract template.

        Returns the list of problems. An empty list means the shape is right — and
        that is *all* it means. Conformance is not accuracy: an empty findings list
        conforms perfectly and tells you nothing.
        """
        problems = []
        if isinstance(contract, dict):
            if not isinstance(instance, dict):
                return [f"{path}: expected an object, got {type(instance).__name__}"]
            for k, v in sorted(contract.items()):
                if k not in instance:
                    problems.append(f"{path}.{k}: missing")
                else:
                    problems += check(instance[k], v, f"{path}.{k}")
        elif isinstance(contract, list):
            if not isinstance(instance, list):
                return [f"{path}: expected a list, got {type(instance).__name__}"]
            for i, item in enumerate(instance):          # every element, same template
                problems += check(item, contract[0], f"{path}[{i}]")
        elif isinstance(contract, str) and "|" in contract:
            if instance not in contract.split("|"):
                problems.append(f"{path}: {instance!r} is not one of {contract}")
        elif isinstance(contract, bool):                  # before the numeric case:
            if not isinstance(instance, bool):            # bool is a subclass of int
                problems.append(f"{path}: expected bool, got {type(instance).__name__}")
        elif isinstance(contract, (int, float)):
            # JSON has one number type. A contract written `0` must accept 0.4, or
            # every cost and rate in the pipeline has to be rounded to satisfy a
            # checker rather than to be correct.
            if isinstance(instance, bool) or not isinstance(instance, (int, float)):
                problems.append(f"{path}: expected a number, got {type(instance).__name__}")
        elif not isinstance(instance, type(contract)):
            problems.append(f"{path}: expected {type(contract).__name__}, "
                            f"got {type(instance).__name__}")
        return problems

SKILL_MD = _skill_md()
meta, body = parse_skill(SKILL_MD)

import time
from dataclasses import dataclass, field

@dataclass
class Token:
    sub: str; actor: str; scopes: set; act: dict = None
    def chain(self):
        out, node = [], self.act
        while node: out.append(node["actor"]); node = node.get("act")
        c = list(reversed(out)) + [self.actor]
        if c[0] != self.sub: c.insert(0, self.sub)
        return c

AGENTS = {
 "patch-agent":   Token("dana@corp", "patch-agent", {"repo:read", "repo:write"},
                        {"actor": "orchestrator", "act": None}),
 "rotator-agent": Token("ops@corp", "rotator-agent", {"secrets:read", "secrets:write"},
                        {"actor": "scheduler", "act": None}),
}
EVENT = {"action": "read_file", "target": "/vault/.env", "ts": time.time()}

print("BARE ALERT (what most SOCs receive):")
for actor in AGENTS:
    print(f"   {actor} read {EVENT['target']}")
print("   → identical. An analyst cannot tell these apart.\n")

print("ENRICHED ALERT:")
for actor, tok in AGENTS.items():
    expected = "secrets:read" in tok.scopes
    print(f"   actor        {tok.actor}")
    print(f"   on behalf of {tok.sub}")
    print(f"   chain        {' → '.join(tok.chain())}")
    print(f"   scopes held  {sorted(tok.scopes)}")
    print(f"   verdict      {'EXPECTED — this agent rotates secrets' if expected else 'ANOMALY — no secrets scope'}")
    print()

def triage_without_context(event):
    """All the analyst has is the action and the target."""
    return "escalate" if "/.env" in event["target"] or "secret" in event["target"] else "close"

def triage_with_context(event, token):
    needed = "secrets:read"
    if "/.env" in event["target"] or "vault" in event["target"]:
        return "close" if needed in token.scopes else "escalate"
    return "close"

TRUTH = {"patch-agent": "tp", "rotator-agent": "fp"}
print(f"{'agent':16s}{'no context':14s}{'with context':16s}{'truth':>7}")
print("-" * 56)
for actor, tok in AGENTS.items():
    a = triage_without_context(EVENT)
    b = triage_with_context(EVENT, tok)
    print(f"{actor:16s}{a:14s}{b:16s}{TRUTH[actor]:>7}")

print("\nWithout scopes, both escalate → the rotator generates a false positive")
print("every single night, and within a month the rule is tuned off.")

FIELDS = {
 "acting identity":  "which agent — not the human whose token it borrowed",
 "principal":        "who the action was for",
 "delegation chain": "who caused the task; where to look for the trigger",
 "scopes held":      "THE decisive field — is this action within its remit?",
 "tool + target":    "what it did",
 "session/trace id": "so the analyst can pull the whole run (D1.5)",
}
for k, v in FIELDS.items(): print(f"{k:20s}{v}")

def enrich(event, token, trace_id):
    return {"acting_identity": token.actor, "principal": token.sub,
            "chain": " → ".join(token.chain()), "scopes": sorted(token.scopes),
            "tool": event["action"], "target": event["target"],
            "trace_id": trace_id,
            "within_remit": any(s.startswith("secrets") for s in token.scopes)
                            if "vault" in event["target"] or "/.env" in event["target"]
                            else True}

print()
for actor, tok in AGENTS.items():
    e = enrich(EVENT, tok, trace_id=f"tr-{actor[:4]}-8812")
    verdict = "close (within remit)" if e["within_remit"] else "ESCALATE (outside remit)"
    print(f"{actor:16s}{verdict}")
    print(f"{'':16s}{e['chain']}  scopes={e['scopes']}")

assert enrich(EVENT, AGENTS["patch-agent"], "x")["within_remit"] is False
assert enrich(EVENT, AGENTS["rotator-agent"], "x")["within_remit"] is True

contract = contract_of(body)
import zlib

ALERTS = [("A-1", "patch-agent"), ("A-2", "rotator-agent"), ("A-3", "patch-agent"),
          ("A-4", "rotator-agent"), ("A-5", "patch-agent"), ("A-6", "rotator-agent")]
SAMPLE_RATE = 0.34

def sampled(alert_id):
    # crc32, never hash(): Python randomises string hashing per process, so a
    # hash()-seeded sampler is unauditable by construction
    return (zlib.crc32(alert_id.encode()) % 100) < SAMPLE_RATE * 100

triaged = []
for aid, agent in ALERTS:
    ctx = enrich(EVENT, AGENTS[agent], aid)
    within = ctx["within_remit"]
    triaged.append({
      "alert_id": aid,
      # reading /vault/.env is real either way; whether it is *fine* is decided
      # by the acting identity's remit, which is the context field that matters
      "verdict": "benign_true_positive" if within else "true_positive",
      "deciding_context": "identity",
      "reason": f"{ctx['acting_identity']} scopes {ctx['scopes']}",
      "confidence": 0.9 if within else 0.95,
      "auto_closed": within,
      "sampled_for_review": within and sampled(aid)})

reviewed = [t for t in triaged if t["sampled_for_review"]]
triage = {
 "triaged": triaged,
 "sampling": {"rate": SAMPLE_RATE, "seed_source": "zlib.crc32(alert_id)",
              "reviewed": len(reviewed), "disagreements": 0},
 "tuning": [{"rule": "vault-file-read", "fp_rate": 0.0,
             "volume": len(ALERTS), "priority": 0.0}],
}
problems = check(triage, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

for t in triaged:
    print(f"   {t['alert_id']}  {t['verdict']:20s} auto_closed={str(t['auto_closed']):5s} "
          f"sampled={t['sampled_for_review']}")
print(f"\nauto-closed {sum(t['auto_closed'] for t in triaged)}, "
      f"of which {len(reviewed)} sampled back for human review")
print()
print("`benign_true_positive` is its own verdict. Folding it into false-positive")
print("would teach the tuner to suppress a detection that is working exactly as")
print("designed - the read really happened, it was simply within remit.")
assert any(t["verdict"] == "benign_true_positive" for t in triaged)
assert any(t["verdict"] == "true_positive" for t in triaged)
assert reviewed, "auto-closing with no sample is a rule with no error bar"
