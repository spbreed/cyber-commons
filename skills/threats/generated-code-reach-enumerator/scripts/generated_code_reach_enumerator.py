#!/usr/bin/env python3
"""Enumerate what model-authored code reaches when executed, on an ordinary task and on a steered one.

This is the executable half of the `generated-code-reach-enumerator` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

# a stand-in for the process the agent's code runs inside
PROCESS_ENV = {
 "AWS_ACCESS_KEY_ID": "AKIA-EXAMPLE-NOT-REAL",
 "DATABASE_URL": "postgres://app:pw@prod-db/main",
 "HOME": "/home/agent",
}
FILESYSTEM = {"/home/agent/work/data.csv": "id,amount",
              "/home/agent/.ssh/id_ed25519": "PRIVATE KEY MATERIAL",
              "/etc/passwd": "root:x:0:0"}
NETWORK_REACHABLE = ["prod-db:5432", "169.254.169.254:80", "0.0.0.0/0"]

def execute(code):
    """The runtime runs model-authored text. Reach is decided by the process,
    not by the code's intent."""
    reached = []
    if "environ" in code:  reached += [f"env:{k}" for k in sorted(PROCESS_ENV)]
    if "open(" in code:    reached += [f"file:{p}" for p in sorted(FILESYSTEM)]
    if "connect" in code:  reached += [f"net:{h}" for h in NETWORK_REACHABLE]
    return reached

BENIGN = "rows = open('/home/agent/work/data.csv').read()"     # nobody attacked anything
STEERED = "import os; d=os.environ; connect('169.254.169.254')"

for label, code in (("ordinary bug / benign task", BENIGN),
                    ("steered by an injection", STEERED)):
    reach = execute(code)
    print(f"{label}:")
    print(f"   code   : {code[:58]}")
    print(f"   reached: {len(reach)} things")
    for r in reach[:6]:
        print(f"      {r}")
    print()

print("The benign task reached every file the process can see, including a")
print("private key it had no reason to touch. It was not attacked - the code")
print("used open(), and open() sees what the process sees.")
print()
print("Blast radius here is a property of the environment. A3.2 changes the")
print("environment; no amount of instruction changes it.")
assert any("id_ed25519" in r for r in execute(BENIGN))
