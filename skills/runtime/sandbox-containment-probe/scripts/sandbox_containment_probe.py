#!/usr/bin/env python3
"""Execute the same code against three environments and evaluate the network policies that separate them.

This is the executable half of the `sandbox-containment-probe` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

HOST = {"fs": ["/home/agent/work/data.csv", "/home/agent/.ssh/id_ed25519",
                "/etc/passwd"],
        "env": {"AWS_ACCESS_KEY_ID": "AKIA-EXAMPLE-NOT-REAL",
                "DATABASE_URL": "postgres://bookings-db.prod/main"},
        "net": ["bookings-db.prod:5432", "169.254.169.254:80", "0.0.0.0/0"]}

def sandbox(workdir="/sandbox/work", allow_net=(), keep_env=()):
    return {"fs": [p for p in HOST["fs"] if p.startswith(workdir)]
                  + [f"{workdir}/data.csv"],
            "env": {k: v for k, v in HOST["env"].items() if k in keep_env},
            "net": list(allow_net)}

def reach(env, code):
    out = []
    if "open("   in code: out += [f"file:{p}" for p in sorted(env["fs"])]
    if "environ" in code: out += [f"env:{k}"  for k in sorted(env["env"])]
    if "connect" in code: out += [f"net:{h}"  for h in sorted(env["net"])]
    return out

CODE = "import os; d=os.environ; open('/home/agent/.ssh/id_ed25519'); connect('x')"

configs = {
 "no sandbox":                    HOST,
 "sandbox, prod creds mounted":   sandbox(allow_net=["bookings-db.prod:5432"],
                                          keep_env=("AWS_ACCESS_KEY_ID",
                                                    "DATABASE_URL")),
 "sandbox, no ambient creds":     sandbox(),
}
for label, env in configs.items():
    r = reach(env, CODE)
    print(f"{label:32s}reached {len(r)}")
    for item in r:
        print(f"      {item}")
    print()

print("The middle configuration is the one that ships. The filesystem is")
print("isolated, the syscalls are filtered, and the environment holds a")
print("credential that reaches production over a network hop the sandbox allows.")
print()
print("Isolation of the wrong dimension is not a weaker control. It is the")
print("appearance of one.")
assert reach(configs["sandbox, no ambient creds"], CODE) and \
       not any("env:" in r for r in reach(configs["sandbox, no ambient creds"], CODE))

# The two NetworkPolicy objects above, as data. The point of modelling them
# rather than trusting them is the additive rule: a pod that NO policy selects
# is unrestricted, and policies never deny.
POLICIES = [
 {"name": "default-deny-all",      "selects": "*",              "egress": []},
 {"name": "workflow-agent-egress", "selects": "workflow-agent",
  "egress": [("bookings-db.prod", 5432), ("kube-dns", 53)]},
]

def permitted(policies, pod, dest, port):
    """Kubernetes semantics, exactly: restricted only if some policy selects
    this pod, and then permitted only if some selecting policy allows it."""
    selecting = [p for p in policies if p["selects"] in ("*", pod)]
    if not selecting:
        return True, "no policy selects this pod - unrestricted"
    for p in selecting:
        if (dest, port) in p["egress"]:
            return True, f"allowed by {p['name']}"
    return False, "no selecting policy permits it - denied"

ATTEMPTS = [
 ("workflow-agent", "bookings-db.prod", 5432, "the one it needs"),
 ("workflow-agent", "kube-dns",           53, "resolution, explicitly granted"),
 ("workflow-agent", "169.254.169.254",    80, "cloud metadata - node credentials"),
 ("workflow-agent", "archive.evil.example", 443, "A1.3's exfiltration target"),
 ("coding-agent",   "archive.evil.example", 443, "a pod nobody wrote a policy for"),
]

def run(policies, label):
    print(f"{label}:")
    out = 0
    for pod, dest, port, note in ATTEMPTS:
        ok, why = permitted(policies, pod, dest, port)
        out += ok
        print(f"   {pod:16s}{dest:22s}{port:<6d}"
              f"{'ALLOW' if ok else 'deny ':6s}{why}")
    print(f"   -> {out}/{len(ATTEMPTS)} connections permitted\n")
    return out

with_deny = run(POLICIES, "both objects applied")

# The usual breakage. Somebody removes default-deny-all because it broke a
# health check, and re-adds a targeted allow instead. Every test still passes.
without = run([p for p in POLICIES if p["name"] != "default-deny-all"],
              "default-deny-all deleted, the narrow policy kept")

print("Deleting the deny changed nothing about workflow-agent - its own policy")
print("still selects it. What it changed is every OTHER pod in the namespace,")
print("including coding-agent, which now reaches the internet because no")
print("object mentions it. Nothing failed, nothing alerted, and the namespace")
print("went from default-deny to default-allow in one commit.")
assert with_deny == 2
assert without == 3 and not permitted(POLICIES, "coding-agent",
                                      "archive.evil.example", 443)[0]
