#!/usr/bin/env python3
"""Execute this skill with the shared runtime, on itself.

The other 116 lessons load the runtime and run a skill. This one loads the
runtime and runs *this* skill, so the mechanism is visible rather than
described: where the runtime came from, what the frontmatter says, what the
contract requires, and what conformance does and does not prove.

Standard library only, and deterministic, so it runs on a Kaggle kernel with
the internet switched off.
"""

# The shared runtime, found the way every lesson finds it. In a notebook the
# cell above has already loaded it; standalone, look in the same two places.
# The runtime comes from the shared library. The lesson cell above put it
# on the path; standalone, PYTHONPATH does (see scripts/test_skills.py).
from cyber_commons_skill_runtime import check, contract_of, parse_skill

import pathlib

# Deliberately not the path. It is /kaggle/input/... on Kaggle and a repository
# path locally, and `kaggle_verify.py` compares this notebook's remote output
# against a local run line for line — so a lesson that prints where it is
# running can never be verified. Print the property instead of the location.
print("1 · the runtime")
print("   loaded  : one shared file — the kernel attached as a source on")
print("             Kaggle, skills/_runtime/ in a local checkout")
print("   copies  : none. 9,730 lines of it used to be in the notebooks")
print()

# ---------------------------------------------------------------- the skill
SKILL_MD = globals().get("SKILL_MD") or (
    pathlib.Path(__file__).resolve().parent.parent / "SKILL.md").read_text()

meta, body = parse_skill(SKILL_MD)
print("2 · the frontmatter — what an agent routes on")
print(f"   name        : {meta['name']}")
print(f"   description : {len(meta['description'].split())} words")
print(f"   allowed     : {', '.join(meta.get('allowed-tools', [])) or '-'}")
print(f"3 · the body — what it follows once it fires: {len(body.splitlines())} lines")
print()

# ------------------------------------------------------------- the contract
contract = contract_of(body)
print("4 · the output contract")
print(f"   keys        : {', '.join(sorted(contract))}")

INSTANCE = {
    "skill": {"name": meta["name"],
              "description_words": len(meta["description"].split()),
              "allowed_tools": meta.get("allowed-tools", []),
              "procedure_lines": len(body.splitlines())},
    "runtime": {"loaded_from": "kaggle", "path": "<attached kernel or checkout>",
                "shared": True},
    "contract": {"keys": sorted(contract), "conforms": True,
                 "conformance_proves_accuracy": False},
    "script": {"path": "skills/commons/how-a-lesson-runs/scripts/how_a_lesson_runs.py",
               "ran": True},
}
problems = check(INSTANCE, contract)
print(f"   conforms    : {not problems}"
      + (f"  ({len(problems)} problem(s))" if problems else ""))

# The ceiling, demonstrated rather than asserted. This instance is the right
# shape, satisfies every type and every enumeration, and says nothing.
VACUOUS = {"skill": {"name": "", "description_words": 0, "allowed_tools": [],
                     "procedure_lines": 0},
           "runtime": {"loaded_from": "repository", "path": "", "shared": False},
           "contract": {"keys": [], "conforms": False,
                        "conformance_proves_accuracy": False},
           "script": {"path": "", "ran": False}}
print(f"   a vacuous result conforms too : {not check(VACUOUS, contract)}")

# And the one thing the contract does catch: a value outside an enumeration.
NONSENSE = {**VACUOUS, "runtime": {**VACUOUS["runtime"], "loaded_from": ""}}
print(f"   a value outside an enum is caught : {bool(check(NONSENSE, contract))}")
print()
print("So a contract checks shape, types and enumerations, and nothing else.")
print("The vacuous instance above passes every one of those and is empty - which")
print("is why every skill here carries failure modes as well as a contract.")

assert not problems, problems
assert not check(VACUOUS, contract), "a vacuous instance must conform - that is the point"
assert check(NONSENSE, contract), "an out-of-enum value must be caught"
