#!/usr/bin/env python3
"""Audit a coding agent's own configuration, tool list and MCP servers.

This is the executable half of the `coding-agent-hardening` skill: the check the
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

SCOPE_WEIGHT = {"self":1,"project":3,"tenant":8,"org":20}
DEV_TOOLS = [
 # (name, writes, scope, reversible, needed in the inner loop)
 ("read_file",  False,"self",   True,  True),
 ("write_file", True, "project",True,  True),
 ("run_tests",  True, "self",   True,  True),
 ("run_shell",  True, "tenant", False, True),
 ("git_commit", True, "project",True,  True),
 ("git_push",   True, "project",False, False),
 ("read_env",   False,"org",    True,  False),
 ("http_get",   False,"self",   True,  True),
]
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2)
               for n,w,s,rev,_ in tools if w and n not in gated)

print(f"{'tool':14s}{'writes':8s}{'scope':9s}{'reversible':12s}inner loop?")
print("-" * 58)
for n,w,s,rev,need in DEV_TOOLS:
    print(f"{n:14s}{str(w):8s}{s:9s}{str(rev):12s}{need}")
print(f"\ndefault blast radius: {blast(DEV_TOOLS)}")

import fnmatch
HOME = [
 "/home/dana/work/monorepo/src/app.py",
 "/home/dana/work/monorepo/.env",
 "/home/dana/work/other-team-repo/secrets.yaml",
 "/home/dana/.aws/credentials",
 "/home/dana/.ssh/id_ed25519",
 "/home/dana/.config/gcloud/application_default_credentials.json",
 "/home/dana/Downloads/customer-export-2026.csv",
]
def normalise(p):
    parts = []
    for seg in p.split("/"):
        if seg in ("", "."): continue
        if seg == "..":
            if parts: parts.pop()
            continue
        parts.append(seg)
    return "/" + "/".join(parts)

DENY = ("*/.ssh/*","*/.aws/*","*/.config/gcloud/*","*.pem","*/.env","*/Downloads/*")
def contained(p, workspace="/home/dana/work/monorepo"):
    real = normalise(p)
    if any(fnmatch.fnmatch(real, g) for g in DENY): return False
    return real.startswith(workspace + "/")

print(f"{'path':64s}{'default':9s}contained")
print("-" * 84)
for p in HOME:
    print(f"{p:64s}{'True':9s}{contained(p)}")
creds = [p for p in HOME if any(k in p for k in (".aws",".ssh","gcloud",".env"))]
print(f"\ncredential files reachable by default: {len(creds)}")
print(f"credential files reachable when contained: "
      f"{sum(1 for p in creds if contained(p))}")

gated = {"git_push"}
print(f"blast radius     {blast(DEV_TOOLS):>3} → {blast(DEV_TOOLS, gated):>3}")
print(f"reachable files  {len(HOME):>3} → {sum(1 for p in HOME if contained(p)):>3}")
print(f"credentials      {len(creds):>3} → {sum(1 for p in creds if contained(p)):>3}")
print(f"friction added   0.4 of 1.0 — one confirmation before a push")
assert not any(contained(p) for p in creds)
print("\nNo cloud or SSH credential is reachable, the inner loop is unchanged,")
print("and the only thing a developer notices is a prompt before pushing.")

contract = contract_of(body)

# What actually reaches a coding agent's context in a normal repository.
SURFACE = [
 ("AGENTS.md",             "operator", True),
 (".claude/settings.json", "operator", True),
 ("README.md",             "content",  True),
 ("docs/CONTRIBUTING.md",  "content",  True),
 ("package.json",          "content",  True),   # a hook may execute its scripts
 ("vendor/lib/README.md",  "content",  False),
]

worst = max(DEV_TOOLS, key=lambda t: SCOPE_WEIGHT[t[2]] * (1 if t[3] else 2))
audit = {
 "surface": [{"path": p, "control": c, "auto_loaded": a} for p, c, a in SURFACE],
 "findings": [
   {"kind": "prompt_injection", "path": "README.md", "grade": "directive",
    # severity is whatever the most powerful pre-approved tool can do
    "worst_case": f"content-controlled text triggers {worst[0]} at {worst[2]} scope",
    "severity": "critical" if not worst[3] else "high",
    "fix": "quote repository content as data; never as instruction"},
   {"kind": "unsafe_hook", "path": "package.json", "grade": "directive",
    "worst_case": "a hook runs a repo-supplied script the moment the repo opens",
    "severity": "critical",
    "fix": "pin the hook command; never take it from repository content"},
   {"kind": "overbroad_tool", "path": ".claude/settings.json", "grade": "advisory",
    "worst_case": f"{worst[0]} pre-approved with unrestricted arguments",
    "severity": "high", "fix": "split into narrow tools, or require approval"},
 ],
 "allowlist_review": [
   {"tool": name, "worst_single_call": f"{scope} scope, "
                                       f"{'reversible' if rev else 'IRREVERSIBLE'}",
    "bounded": scope in ("self", "project") and rev}
   for name, writes, scope, rev, _ in DEV_TOOLS if writes],
}
problems = check(audit, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\nauto-loaded, content-controlled inputs: "
      f"{[s['path'] for s in audit['surface'] if s['control']=='content' and s['auto_loaded']]}")
print(f"most powerful pre-approved tool      : {worst[0]} ({worst[2]} scope)")
print("\nallowlist:")
for r in audit["allowlist_review"]:
    print(f"   {r['tool']:12s}{r['worst_single_call']:34s}bounded={r['bounded']}")
unbounded = [r["tool"] for r in audit["allowlist_review"] if not r["bounded"]]
print(f"\nunbounded pre-approved tools: {unbounded}")
print()
print("The injection finding is Critical not because the README says anything")
print("clever, but because a directive path exists to a tool that cannot be")
print("undone. Rewrite the payload and the severity does not move.")
assert unbounded, "an unbounded pre-approved tool should be visible here"
