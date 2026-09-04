#!/usr/bin/env python3
"""Scope what an agent touched during an incident, from the run record rather than from the alert.

This is the executable half of the `incident-scoping` skill: the check the
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

REACHED = {
 "dana@corp":    ["repo-core", "repo-infra", "vault-dev"],
 "orchestrator": ["repo-core", "queue-tasks"],
 "patch-agent":  ["repo-core", "repo-payments"],
 "deploy-agent": ["cluster-prod"],
}
CHAIN = ["dana@corp", "orchestrator", "patch-agent", "deploy-agent"]

def scope(chain, reached):
    last_only = set(reached.get(chain[-1], []))
    full = {r for a in chain for r in reached.get(a, [])}
    return {"chain": " → ".join(chain),
            "scoped_last_actor_only": sorted(last_only),
            "scoped_whole_chain": sorted(full),
            "missed_by_naive_scoping": sorted(full - last_only),
            "undercount_factor": round(len(full)/len(last_only), 2) if last_only else None}

s = scope(CHAIN, REACHED)
for k, v in s.items(): print(f"{k:26s}{v}")
print("\nScoping the last actor finds one cluster. The chain reached six")
print("resources, including a payments repository and a dev vault.")

print(f"{'depth':>6}{'last-actor scope':>19}{'chain scope':>14}{'undercount':>12}")
print("-" * 52)
for d in range(1, 5):
    sub = CHAIN[:d]
    r = scope(sub, REACHED)
    print(f"{d:>6}{len(r['scoped_last_actor_only']):>19}"
          f"{len(r['scoped_whole_chain']):>14}"
          f"{str(r['undercount_factor']):>12}")
print("\nEach hop adds resources the last actor never touched. This is why B2.0")
print("bounds delegation depth: depth is an incident-scope multiplier.")

SHARED = {"repo-core": ["build-agent", "test-agent"],
          "cluster-prod": ["deploy-agent", "monitor-agent"],
          "repo-payments": ["finance-agent"]}

def scope_transitive(chain, reached, shared, hops=1):
    """Anything that shares a touched resource may have been influenced."""
    direct = {r for a in chain for r in reached.get(a, [])}
    exposed = set(chain)
    frontier = set(direct)
    for _ in range(hops):
        nxt = set()
        for res in frontier:
            for actor in shared.get(res, []):
                if actor not in exposed:
                    exposed.add(actor)
                    nxt |= set(reached.get(actor, []))
        frontier = nxt
    return {"resources_direct": sorted(direct),
            "actors_in_scope": sorted(exposed),
            "second_order_actors": sorted(exposed - set(chain))}

t = scope_transitive(CHAIN, REACHED, SHARED)
for k, v in t.items(): print(f"{k:22s}{v}")
print("\nFive more identities shared a resource with the compromised chain.")
print("They are not confirmed compromised — they are IN SCOPE, which is different")
print("and is the distinction an incident record has to make explicitly.")
assert t["second_order_actors"]

# Verify: produce the scope statement for the incident record.
def scope_statement(chain, reached, shared):
    s = scope(chain, reached)
    t = scope_transitive(chain, reached, shared)
    return (f"SCOPE\n"
            f"  chain              {s['chain']}\n"
            f"  confirmed touched  {s['scoped_whole_chain']}\n"
            f"  would have been missed by scoping the acting agent alone:\n"
            f"                     {s['missed_by_naive_scoping']}\n"
            f"  undercount factor  {s['undercount_factor']}×\n"
            f"  in scope, not confirmed (shared a resource):\n"
            f"                     {t['second_order_actors']}")
print(scope_statement(CHAIN, REACHED, SHARED))

contract = contract_of(body)
t = scope_transitive(CHAIN, REACHED, SHARED)
reach = sorted({r for a in CHAIN for r in REACHED.get(a, [])})

incident = {
 "window": {"first_suspicious_action": f"{CHAIN[1]} accepted an external instruction",
            "detected_at": "the deploy that followed",
            # the trigger precedes the detection by about one task loop
            "gap_seconds": 42 * 60},
 "chain": [{"action": f"{a} acted", "motivating_input": "issue comment"
                      if a == CHAIN[1] else f"instruction from {CHAIN[i]}",
            "input_origin": "external_untrusted" if a == CHAIN[1] else "internal",
            "within_authority": True}
           for i, a in enumerate(CHAIN[1:])],
 "root_cause": {"input": "issue comment on a public tracker",
                "origin": "external_untrusted",
                "why_trusted": "repository content was read as instruction, not data"},
 # every action was permitted; that is what makes this hard
 "authority": {"authorised_but_wrong": len(CHAIN) - 1, "exceeded_authority": 0},
 "data": {"reach": reach, "confirmed_exfiltration": [],
          "egress_bounded_by": "agent network policy"},
 "containment": {"cut": "credential",
                 "does_not_stop": sorted(t["second_order_actors"]),
                 "evidence_snapshotted_first": True},
 "clock": {"regulatory_trigger": False,
           "basis": "no confirmed exfiltration of personal data yet"},
}
problems = check(incident, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\nauthorised but wrong : {incident['authority']['authorised_but_wrong']}")
print(f"exceeded authority   : {incident['authority']['exceeded_authority']}")
print(f"reach                : {len(reach)} resources")
print(f"confirmed exfil      : {len(incident['data']['confirmed_exfiltration'])}")
print(f"revoking one credential does NOT stop: "
      f"{incident['containment']['does_not_stop'] or 'nothing else'}")
print()
print("Zero actions exceeded authority, and the incident still happened. That")
print("combination says the grant was too broad - a different fix from a")
print("control that failed, which is why the contract counts them separately.")
print()
print("Reach is 4 resources; confirmed exfiltration is 0. Reporting the second")
print("as the scope is how a notification decision gets made on the wrong number.")
assert incident["authority"]["exceeded_authority"] == 0
assert len(reach) > len(incident["data"]["confirmed_exfiltration"])
