#!/usr/bin/env python3
"""Audit a coding agent's own configuration, tool list and MCP servers.

This is the executable half of the `coding-agent-hardening` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# The skill runtime comes from the shared library, not from a copy in this file.
# In a lesson notebook the cell above has already loaded it; standalone, find it
# the same way that cell does.
import glob as _glob, importlib.util as _ilu, os as _os, sys as _sys

if "cyber_commons_skill_runtime" not in _sys.modules:
    _where = (sorted(_glob.glob("/kaggle/input/**/cyber-commons-skill-runtime/__script__.py",
                                recursive=True))
              + [_os.path.join(p, "skills/_runtime/cyber_commons_skill_runtime.py")
                 for p in (".", "..", "../..",
                           _os.path.join(_os.path.dirname(__file__), "../../../_runtime"))])
    _found = next((p for p in _where if _os.path.isfile(p)), None)
    if _found is None:
        raise SystemExit("shared skill runtime not found; looked at " + repr(_where))
    _spec = _ilu.spec_from_file_location("cyber_commons_skill_runtime", _found)
    _mod = _ilu.module_from_spec(_spec)
    _sys.modules["cyber_commons_skill_runtime"] = _mod
    _spec.loader.exec_module(_mod)

from cyber_commons_skill_runtime import check, contract_of, parse_skill


def _skill_md():
    """The SKILL.md next to this script, or the one the notebook already parsed."""
    if "SKILL_MD" in globals():
        return globals()["SKILL_MD"]
    return (_pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()


import pathlib as _pathlib

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
